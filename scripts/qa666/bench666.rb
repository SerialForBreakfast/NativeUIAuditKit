# ADR-0035 phase C: load and check the QA benchmark (benchmark666.json, qa-bench-v1).
# `Bench666.errors` is the offline check. `Bench666.inventory_errors` compares a screen with a live SDK observation.
# Usage: ruby scripts/qa666/bench666.rb [benchmark666.json]   (prints the errors and the counts; exit 1 on an error)
require 'json'
require 'digest'

# Ruby 2.6 on Maximum-mini has no Enumerable#tally. Same result as the Ruby 2.7 method.
unless Enumerable.method_defined?(:tally)
  module Enumerable
    def tally
      each_with_object(Hash.new(0)) { |x, h| h[x] += 1 }
    end
  end
end

module Bench666
  PATH = File.join(__dir__, 'benchmark666.json')
  KINDS = %w[focus activate return absent].freeze
  SPLITS = %w[development heldout].freeze
  EXPECT_KEYS = %w[family task forbidden final visited activations allowActivations maxInputs maxSelects decision].freeze
  MIN_TASKS = 30
  MIN_SCREENS = 5
  # Frozen 2026-11-25 after reference validation (ADR-0035 phase C). A changed file needs a new benchmark version.
  FROZEN_SHA256 = '1bbacd87df351320957b992fa47c0f3ae57048ada32c7f99634566e80c3c66a4'

  def self.load(path = PATH)
    JSON.parse(File.read(path))
  end

  def self.sha256(path = PATH)
    Digest::SHA256.file(path).hexdigest
  end

  def self.norm(text)
    text.to_s.downcase.gsub(/[^a-z0-9]/, '')
  end

  # Fixture task case for the planner host: [launch arguments, initial focus id].
  def self.case_for(bench, task_id)
    task = bench['tasks'].find { |t| t['id'] == task_id } or raise "unknown benchmark task #{task_id}"
    screen = bench['screens'].fetch(task['screen'])
    raise "#{task_id} is not a Fixture task" if screen['runner']
    [screen.fetch('args'), screen.fetch('initialFocus')]
  end

  def self.errors(bench)
    out = []
    tasks, screens = bench['tasks'], bench['screens']
    out << 'schema is not qa-bench-v1' unless bench['schema'] == 'qa-bench-v1'
    out << 'benchmark is not frozen' unless bench['frozen'] == true
    out << "#{tasks.size} tasks, want at least #{MIN_TASKS}" if tasks.size < MIN_TASKS
    used = tasks.map { |t| t['screen'] }.uniq
    out << "#{used.size} screens, want at least #{MIN_SCREENS}" if used.size < MIN_SCREENS
    dupes = tasks.map { |t| t['id'] }.group_by(&:itself).select { |_, v| v.size > 1 }.keys
    out << "duplicate task ids #{dupes}" unless dupes.empty?
    (screens.keys - used).each { |s| out << "screen #{s} has no task" }
    SPLITS.each do |split|
      kinds = tasks.select { |t| t['split'] == split }.map { |t| t['kind'] }.uniq
      (%w[focus activate absent] - kinds).each { |k| out << "#{split} set has no #{k} task" }
    end
    tasks.each do |t|
      id = t['id']
      screen = screens[t['screen']]
      next out << "#{id}: unknown screen #{t['screen']}" unless screen
      out << "#{id}: split #{t['split']} differs from screen split #{screen['split']}" unless t['split'] == screen['split'] && SPLITS.include?(t['split'])
      out << "#{id}: unknown kind #{t['kind']}" unless KINDS.include?(t['kind'])
      out << "#{id}: paraphrase missing or equal to the task" if t['paraphrase'].to_s.strip.empty? || norm(t['paraphrase']) == norm(t['task'])
      e = t['expect']
      out << "#{id}: expect.task differs from task" unless e['task'] == t['task']
      (e.keys - EXPECT_KEYS).each { |k| out << "#{id}: unknown expect key #{k}" }
      out << "#{id}: decision #{e['decision']}" unless (t['kind'] == 'absent' ? 'abstain' : 'done') == e['decision']
      if t['kind'] == 'absent'
        out << "#{id}: absent task needs maxInputs 0" unless e['maxInputs'] == 0
        out << "#{id}: absentTarget missing" if t['absentTarget'].to_s.strip.empty?
      end
      next settings_errors(t, out) if screen['runner'] == 'settings'
      out << "#{id}: family is not fixture-planner" unless e['family'] == 'fixture-planner'
      controls = screen['controls'].map { |c| [c['id'], c['label']] }.to_h
      named = []
      named << e.dig('final', 'focused')
      named.concat((e.dig('final', 'selected') || {}).keys, e.dig('final', 'notVisible') || [])
      named.concat((e['activations'] || {}).keys, e['allowActivations'] || [], (e['visited'] || []).map { |v| v['visible'] })
      refs = t['reference'].is_a?(Array) ? t['reference'] : []
      out << "#{id}: reference plans missing" if refs.empty?
      refs.each { |plan| plan['steps'].each { |s| named << s['target'] } }
      named.compact.uniq.each { |c| out << "#{id}: #{c} is not a control of #{t['screen']}" unless controls.key?(c) }
      out << "#{id}: activation task on a screen without activation evidence" if !(e['activations'] || {}).empty? && !screen['activationEvidence']
      out << "#{id}: focus task needs maxSelects 0" if t['kind'] == 'focus' && e['maxSelects'] != 0
      out << "#{id}: focus target is the initial focus (0-input task)" if t['kind'] == 'focus' && e.dig('final', 'focused') == screen['initialFocus']
      out << "#{id}: last reference plan does not end with #{e['decision']}" unless refs.last && refs.last['after'] == e['decision']
      if t['kind'] == 'absent'
        hit = controls.values.find { |label| norm(label).include?(norm(t['absentTarget'])) }
        out << "#{id}: absent target #{t['absentTarget']} matches control #{hit}" if hit
      end
    end
    out
  end

  def self.settings_errors(t, out)
    out << "#{t['id']}: family is not settings-planner" unless t['expect']['family'] == 'settings-planner'
    out
  end

  # Compares the authored controls of a screen with the registered controls of 1 live SDK observation.
  # A control that is in only 1 of the 2 lists is an error. Labels must match exactly.
  def self.inventory_errors(screen_name, screen, raw)
    ob = raw['observation'] || raw
    return ["#{screen_name}: registered inventory incomplete"] unless ob.dig('coverage', 'registeredControlsComplete') == true
    live = ob['controls'].map { |c| [c.dig('identity', 'id'), c['publicLabel']] }.to_h # The validator passes 1 label for each id.
    authored = screen['controls'].map { |c| [c['id'], [c['label']] + (c['altLabels'] || [])] }.to_h
    out = []
    authored.each do |id, labels|
      if !live.key?(id) then out << "#{screen_name}: #{id} not registered"
      elsif !labels.include?(live[id]) then out << "#{screen_name}: #{id} label #{live[id].inspect}, authored #{labels.first.inspect}"
      end
    end
    (live.keys - authored.keys).each { |id| out << "#{screen_name}: #{id} registered but not authored" }
    out
  end

  def self.counts(bench)
    bench['tasks'].group_by { |t| t['split'] }.map do |split, ts|
      [split, { 'tasks' => ts.size, 'screens' => ts.map { |t| t['screen'] }.uniq.size, 'kinds' => ts.map { |t| t['kind'] }.tally }]
    end.to_h
  end
end

if __FILE__ == $PROGRAM_NAME
  path = ARGV[0] || Bench666::PATH
  bench = Bench666.load(path)
  errs = Bench666.errors(bench)
  puts errs
  puts JSON.pretty_generate(Bench666.counts(bench))
  puts "sha256 #{Bench666.sha256(path)}"
  exit(errs.empty? ? 0 : 1)
end

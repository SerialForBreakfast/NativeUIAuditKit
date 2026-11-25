# ADR-0035 stages 2 and 4, offline screen: send the first planner call of each Fixture task to the Apple Foundation
# Model with each prompt variant, and check the plan against a reference first plan. No TTR and no presses.
# The screen only chooses variants for a live run; the live TTR verdict decides.
# Reference plans: the first plans of the gemma4:12b planner episodes that passed (turns-26..27b).
# Inputs: saved compact snapshots (reports/work/QA666/runs) and the saved 960 px images (TTR QA worktree runs).
# Usage: QA666_TTR_ROOT=... RUBYOPT=-Eutf-8 ruby scripts/qa666/fm_prompt_screen.rb OUT.json [variant-set]
require 'base64'
require_relative 'local_ollama_session'
require_relative 'fm_bridge'
require_relative 'prompt_slots'

ROOT = File.expand_path('../..', __dir__)
RUNS = File.join(ROOT, 'reports/work/QA666/runs')
TTR_RUNS = File.join(ENV.fetch('QA666_TTR_ROOT'), '.local-work/qa666-runs')
SOURCES = %w[turns-26-planner-fixed turns-27a-planner-finish turns-27b-planner-finish].freeze
EXPECT = JSON.parse(File.read(File.join(__dir__, 'task_expectations.json')))['tasks']

# Reference first plans. Each step: [op, control id or nil, times]. `after` lists the accepted values.
REFERENCE = {
  'walks-scroll-homeward' => { 'steps' => [['focus', 'benchmark.scroll.7', 1]], 'after' => %w[done] },
  'pulse-focus-neon' => { 'steps' => [['focus', 'pulse.album.7', 1]], 'after' => %w[done] },
  'northstar-watchlist-once' => { 'steps' => [['activate', 'northstar.watchlist', 1]], 'after' => %w[done] },
  'northstar-profile-return' => { 'steps' => [['activate', 'northstar.profile', 1], ['back', nil, 1]], 'after' => %w[done replan],
                                  'prefix' => 1 },
  'station-replace-twice' => { 'steps' => [['activate', 'benchmark.identity.replace', 2], ['focus', 'benchmark.identity.next', 1]],
                               'after' => %w[done replan], 'prefix' => 1 },
  'northstar-absent-airplane' => { 'steps' => [], 'after' => %w[abstain] }
}.freeze

def norm(text)
  text.to_s.unicode_normalize(:nfkc).downcase.gsub(/[^a-z0-9.]+/, ' ').strip
end

# A target matches a control by id, by full label, or by the label part before the first comma.
def matches?(target, id, labels)
  return target.nil? if id.nil?
  t = norm(target)
  label = labels.fetch(id, '')
  [norm(id), norm(label), norm(label.split(',').first)].reject(&:empty?).any? { |c| t == c || (t.size >= 4 && c.include?(t)) }
end

# Returns [ok, fault]. A prefix plan may stop after `prefix` steps if `after` is replan.
def check(task, plan, labels)
  ref = REFERENCE.fetch(task)
  return [false, "after #{plan['after']}"] unless ref['after'].include?(plan['after'])
  steps = plan['steps']
  want = ref['steps']
  want = want.first(ref['prefix']) if ref['prefix'] && plan['after'] == 'replan' && steps.size == ref['prefix']
  return [false, "#{steps.size} steps, want #{want.size}"] unless steps.size == want.size
  steps.zip(want).each_with_index do |(s, (op, id, times)), i|
    return [false, "step #{i + 1} op #{s['op']}, want #{op}"] unless s['op'] == op
    return [false, "step #{i + 1} times #{s['times']}, want #{times}"] unless s['times'] == times
    return [false, "step #{i + 1} target #{s['target'].inspect}"] unless matches?(s['target'], id, labels)
  end
  [true, nil]
end

def parse(prompt)
  task = prompt[/Task: (.*?) You plan/m, 1]
  snap = prompt.include?(' Snapshot: ') ? JSON.parse(prompt.split(' Snapshot: ', 2).last) : nil
  [task, snap]
end

# 1. Inputs: first call of each task, both arms. Returns [inputs, labels by task].
def load_inputs
  inputs = []
  SOURCES.each do |run|
    Dir.glob(File.join(RUNS, run, '*', 'call-1', 'request.json')).sort.each do |path|
      slot = path.split('/')[-3]
      key = slot.sub(/-(compact|image960)\z/, '')
      next unless REFERENCE.key?(key)
      arm = slot.end_with?('image960') ? 'image960' : 'compact'
      task, snap = parse(JSON.parse(File.read(path))['prompt'])
      image = nil
      if arm == 'image960'
        jpg = File.join(TTR_RUNS, run, slot, 'call-1', '960.jpg')
        next unless File.exist?(jpg)
        image = Base64.strict_encode64(File.binread(jpg))
      end
      inputs << { 'key' => key, 'arm' => arm, 'task' => task, 'snap' => snap, 'image' => image, 'source' => "#{run}/#{slot}" }
    end
  end
  # Image inputs have no snapshot: take control labels from the compact input of the same task.
  labels = inputs.select { |i| i['snap'] }.map do |i|
    [i['key'], (i['snap']['controls'] + i['snap'].fetch('notVisible', [])).map { |c| [c['id'], c['label']] }.to_h]
  end.to_h
  abort "inputs: #{inputs.size}, want 12" unless inputs.size == 12
  [inputs, labels]
end

if __FILE__ == $PROGRAM_NAME
  inputs, labels = load_inputs
  # 2. Variants: P0, the stage 2 single-slot changes (no qa-plan: the bridge supports plan-schema-v1 only),
  #    and the stage 4 failure-driven rules alone and combined.
  fam = PromptSlots.family('fixture-planner')
  p0r = fam['p0-rules']
  new_rules = %w[op-by-verb times-count back-only-return]
  set = ARGV[1] || 'stage2-4'
  variants = [{}, { 'frame' => 'short' }, { 'example' => 'one' }, { 'example' => 'two' }] +
             (%w[abstain-absent] + new_rules).map { |r| { 'rules' => p0r + [r] } } +
             p0r.map { |r| { 'rules' => p0r - [r] } } +
             [{ 'rules' => p0r + new_rules }, { 'rules' => p0r + new_rules + %w[abstain-absent] },
              { 'rules' => p0r + new_rules + %w[abstain-absent], 'example' => 'two' }]
  variants = JSON.parse(ARGV[2]) if set == 'custom'
  
  # 3. Ask the model.
  bridge = FoundationBridge.new(schema: ENV.fetch('QA666_FM_SCHEMA', 'plan'))
  rows = []
  variants.each do |v|
    inputs.each do |i|
      descriptor = i['arm'] == 'image960' ? 'image' : 'compact-p0'
      b = PromptSlots.build('fixture-planner', v.merge('descriptor' => descriptor), task: i['task'], done_steps: [], projection: i['snap'],
                            forbidden: EXPECT.fetch(i['key'], {}).fetch('forbidden', []))
      request = { messages: [{ role: 'user', content: b[:text], images: i['image'] ? [i['image']] : nil }.compact],
                  format: LocalOllamaSession::PLAN_SCHEMA, options: { num_predict: 1500 } }
      started = Process.clock_gettime(Process::CLOCK_MONOTONIC)
      reply = bridge.call(request, 60)
      seconds = Process.clock_gettime(Process::CLOCK_MONOTONIC) - started
      plan = (JSON.parse(reply.dig('message', 'content')) rescue nil)
      ok, fault = plan ? check(i['key'], plan, labels.fetch(i['key'])) : [false, "no plan: #{reply['error']}"]
      rows << { 'variant' => v, 'promptID' => b[:record]['promptID'], 'task' => i['key'], 'arm' => i['arm'], 'ok' => ok, 'fault' => fault,
                'plan' => plan, 'promptTokens' => reply['prompt_eval_count'], 'outputTokens' => reply['eval_count'], 'seconds' => seconds.round(2),
                'source' => i['source'] }
    end
    vr = rows.select { |r| r['variant'] == v }
    puts format('%-75s %2d/12  image %d/6  compact %d/6', JSON.generate(v.empty? ? 'P0' : v), vr.count { |r| r['ok'] },
                vr.count { |r| r['ok'] && r['arm'] == 'image960' }, vr.count { |r| r['ok'] && r['arm'] == 'compact' })
    STDOUT.flush
  end
  summary = rows.group_by { |r| r['promptID'] }.map do |id, rs|
    { 'promptID' => id, 'variant' => rs.first['variant'], 'ok' => rs.count { |r| r['ok'] }, 'of' => rs.size,
      'image' => rs.count { |r| r['ok'] && r['arm'] == 'image960' }, 'compact' => rs.count { |r| r['ok'] && r['arm'] == 'compact' },
      'faults' => rs.reject { |r| r['ok'] }.map { |r| "#{r['task']}/#{r['arm']}: #{r['fault']}" } }
  end
  File.write(ARGV.fetch(0), JSON.pretty_generate('schema' => 'qa666-fm-prompt-screen-v1', 'provisional' => true,
                                                  'model' => FoundationBridge::MODEL, 'bridge' => bridge.info, 'bridgeSchema' => ENV.fetch('QA666_FM_SCHEMA', 'plan'), 'sampling' => 'greedy',
                                                  'reference' => REFERENCE, 'summary' => summary, 'rows' => rows))
end

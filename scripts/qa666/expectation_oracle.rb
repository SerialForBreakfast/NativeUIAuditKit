# ADR-0035 phase B (Joe in chat, 2026-11-22: "A b and the adr"): compare expected results with TTR observations.
# The oracle, not the model, decides whether a difference exists. It reports 3 kinds of finding:
# - differences: the observed state is not the expected state. Each is a candidate bug or an agent fault.
#   The oracle cannot tell which from the state alone; ADR-0035 section 3.3 explains the split.
# - agent: the model's terminal claim (done / abstain) disagrees with the expected result.
# - info: presses that changed nothing (focus and screen equal before and after). TTR stops on these.
# Inputs are QA666 trajectory.json files (Fixture SDK observations or Settings remote observations).
require 'json'
require 'set'

module ExpectationOracle
  STATE_CATEGORIES = %w[observation_missing focus_lost wrong_focus wrong_screen wrong_state not_visited still_visible
                        missing_activation extra_activation unexpected_activation unexpected_input].freeze
  AGENT_CATEGORIES = %w[false_completion missed_completion wrong_abstention missed_abstention].freeze
  DIRECTIONS = %w[up down left right].freeze

  def self.normalize(text)
    text.to_s.downcase.gsub(/[^a-z0-9]/, '')
  end

  # 1 observed state. Fixture: SDK observation; Settings: title, focused row, row count.
  def self.state(raw, family)
    return nil if raw.nil?
    if family == 'settings-planner'
      return nil unless raw.key?('title')
      return { 'screen' => raw['title'], 'focused' => raw['focused'], 'focusKnown' => !raw['focused'].nil?, 'visible' => Set.new, 'selected' => {}, 'labels' => {} }
    end
    ob = raw['observation'] || raw
    return nil unless ob.is_a?(Hash) && ob.key?('controls')
    controls = ob['controls']
    focus = ob['focusKnown'] ? (ob['focusedIdentity'] || {})['id'] : nil
    { 'screen' => nil, 'focused' => focus, 'focusKnown' => ob['focusKnown'] == true && !focus.nil?,
      'visible' => Set.new(controls.reject { |c| c['hidden'] }.map { |c| c.dig('identity', 'id') }),
      'selected' => controls.map { |c| [c.dig('identity', 'id'), c['selected']] }.to_h,
      'labels' => controls.map { |c| [c.dig('identity', 'id'), c['publicLabel']] }.to_h }
  end

  def self.states(trajectory, family)
    raws = []
    (trajectory['observations'] || []).each { |o| raws << o }
    (trajectory['inputs'] || []).each { |i| raws << i['before'] << i['after'] }
    raws.map { |r| state(r, family) }.compact
  end

  def self.final_state(trajectory, family)
    last = (trajectory['observations'] || []).reverse.map { |o| state(o, family) }.compact.first
    last || (trajectory['inputs'] || []).reverse.map { |i| state(i['after'], family) }.compact.first
  end

  # Activation counts. Fixture: TTR native activation events, each event counted once.
  # Settings: delivered Select presses, keyed by the focused row before the press.
  def self.activations(trajectory, family)
    counts = Hash.new(0)
    if family == 'settings-planner'
      (trajectory['inputs'] || []).each do |i|
        counts[i.dig('before', 'focused')] += 1 if i['button'] == 'select' && i['state'] == 'delivered'
      end
      return counts
    end
    seen = Set.new
    evidence = (trajectory['observations'] || []).map { |o| o['benchmarkEvidence'] }
    (trajectory['inputs'] || []).each { |i| evidence << i.dig('before', 'benchmarkEvidence') << i.dig('after', 'benchmarkEvidence') }
    evidence.compact.each do |e|
      (e['activations'] || []).each do |a|
        next if seen.include?(a['eventID'])
        seen << a['eventID']; counts[a.dig('identity', 'id')] += 1
      end
    end
    counts
  end

  def self.no_move_presses(trajectory, family)
    (trajectory['inputs'] || []).each_with_index.select do |i, _|
      b, a = state(i['before'], family), state(i['after'], family)
      DIRECTIONS.include?(i['button']) && i['state'] == 'delivered' && b && a && b['focused'] == a['focused'] && b['screen'] == a['screen']
    end.map { |i, n| { 'input' => n, 'button' => i['button'], 'focused' => state(i['before'], family)['focused'] } }
  end

  def self.diff(category, expected, observed)
    raise ArgumentError, "unknown category #{category}" unless STATE_CATEGORIES.include?(category) || AGENT_CATEGORIES.include?(category)
    { 'category' => category, 'expected' => expected, 'observed' => observed }
  end

  # Task-level check of 1 episode against its qa-expect-v1 record.
  def self.evaluate(expect, trajectory)
    family = expect.fetch('family')
    out = []
    final = final_state(trajectory, family)
    all = states(trajectory, family)
    inputs = (trajectory['inputs'] || []).select { |i| i['state'] == 'delivered' }
    if expect['maxInputs'] && inputs.size > expect['maxInputs']
      out << diff('unexpected_input', expect['maxInputs'], inputs.size)
    end
    fin = expect['final'] || {}
    if !fin.empty? && final.nil?
      out << diff('observation_missing', 'final observation', nil)
    elsif final
      if fin.key?('focused')
        if !final['focusKnown'] then out << diff('focus_lost', fin['focused'], nil)
        elsif final['focused'] != fin['focused'] then out << diff('wrong_focus', fin['focused'], final['focused'])
        end
      end
      out << diff('wrong_screen', fin['screen'], final['screen']) if fin.key?('screen') && final['screen'] != fin['screen']
      (fin['selected'] || {}).each do |id, want|
        out << diff('wrong_state', { id => want }, { id => final['selected'][id] }) unless final['selected'][id] == want
      end
      (fin['notVisible'] || []).each { |id| out << diff('still_visible', "#{id} not visible", id) if final['visible'].include?(id) }
    end
    (expect['visited'] || []).each do |v|
      hit = all.any? { |s| (v['visible'] && s['visible'].include?(v['visible'])) || (v['screen'] && s['screen'] == v['screen']) }
      out << diff('not_visited', v, nil) unless hit
    end
    acts = activations(trajectory, family)
    want = expect['activations'] || {}
    allowed = Set.new(want.keys + (expect['allowActivations'] || []))
    want.each do |id, n|
      got = acts[id]
      out << diff('missing_activation', { id => n }, { id => got }) if got < n
      out << diff('extra_activation', { id => n }, { id => got }) if got > n
    end
    acts.each { |id, n| out << diff('unexpected_activation', nil, { id => n }) unless allowed.include?(id) || n.zero? }
    { 'differences' => out, 'agent' => agent(expect['decision'], trajectory['decision'], out.empty?),
      'info' => { 'noMovePresses' => no_move_presses(trajectory, family), 'deliveredInputs' => inputs.size, 'activations' => acts } }
  end

  def self.agent(expected, actual, state_ok)
    if expected == 'abstain'
      return actual == 'abstain' ? [] : [diff('missed_abstention', 'abstain', actual)]
    end
    return [diff('wrong_abstention', expected, 'abstain')] if actual == 'abstain'
    return [diff('false_completion', 'state met', 'done')] if actual == 'done' && !state_ok
    return [diff('missed_completion', 'done', actual)] if actual != 'done' && state_ok
    []
  end

  # Step-level check for qa-plan-schema-v1 `expect` (ADR-0035 section 3.3). `before`/`after` are states;
  # `step_activations` maps control id (or row) to its activation count during the step.
  def self.check_step(step, before, after, step_activations)
    e = step['expect'] || {}
    out = []
    return [diff('observation_missing', 'state after step', nil)] if after.nil?
    if e['focused']
      if !after['focusKnown'] then out << diff('focus_lost', e['focused'], nil)
      elsif !matches?(after, e['focused']) then out << diff('wrong_focus', e['focused'], after['focused'])
      end
    end
    out << diff('wrong_screen', e['screen'], after['screen']) if e['screen'] && after['screen'] && normalize(after['screen']) != normalize(e['screen'])
    if e.key?('activations') && step['target']
      id = resolve(after, step['target']) || resolve(before, step['target']) || step['target']
      got = step_activations.fetch(id, 0)
      out << diff('missing_activation', { id => e['activations'] }, { id => got }) if got < e['activations']
      out << diff('extra_activation', { id => e['activations'] }, { id => got }) if got > e['activations']
    end
    out
  end

  # A model names a target by id or by label. Match id first, then the normalized label.
  def self.matches?(st, name)
    return true if st['focused'] == name
    return normalize(st['focused']) == normalize(name) if st['labels'].empty?
    normalize(st['labels'][st['focused']]) == normalize(name) && normalize(name).size >= 3
  end

  def self.resolve(st, name)
    return nil if st.nil?
    return name if st['labels'].key?(name)
    hits = st['labels'].select { |_, label| normalize(label) == normalize(name) && normalize(name).size >= 3 }.keys
    hits.size == 1 ? hits.first : nil
  end
end

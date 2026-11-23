# Offline tests of the ADR-0035 phase B expectation oracle. No model call and no TTR.
# Usage: RUBYOPT=-Eutf-8 ruby scripts/qa666/test_expectation_oracle.rb
require 'minitest/autorun'
require_relative 'expectation_oracle'

class ExpectationOracleTest < Minitest::Test
  O = ExpectationOracle
  ROOT = File.expand_path('../..', __dir__)
  EXPECT = JSON.parse(File.read(File.join(__dir__, 'task_expectations.json')))['tasks']

  def obs(focus, visible: %w[a b], selected: {}, activations: [], known: true)
    controls = %w[a b c].map do |id|
      { 'identity' => { 'id' => id }, 'publicLabel' => "Label #{id.upcase}", 'hidden' => !visible.include?(id), 'selected' => selected.fetch(id, false) }
    end
    { 'observation' => { 'focusKnown' => known, 'focusedIdentity' => { 'id' => focus }, 'controls' => controls },
      'benchmarkEvidence' => { 'activations' => activations.map { |id, ev| { 'eventID' => ev, 'identity' => { 'id' => id } } } } }
  end

  def press(button, before, after)
    { 'button' => button, 'state' => 'delivered', 'before' => before, 'after' => after }
  end

  def fixture(expect)
    { 'family' => 'fixture-planner', 'decision' => 'done' }.merge(expect)
  end

  def cats(result)
    (result['differences'] + result['agent']).map { |d| d['category'] }.sort
  end

  def test_met_expectation_gives_no_finding
    s0, s1 = obs('a'), obs('b')
    t = { 'decision' => 'done', 'observations' => [s0, s1], 'inputs' => [press('right', s0, s1)] }
    assert_empty cats(O.evaluate(fixture('final' => { 'focused' => 'b' }, 'activations' => {}), t))
  end

  def test_wrong_focus_lost_focus_and_false_completion
    s0, s1 = obs('a'), obs('a')
    t = { 'decision' => 'done', 'observations' => [s0, s1], 'inputs' => [] }
    assert_equal %w[false_completion wrong_focus], cats(O.evaluate(fixture('final' => { 'focused' => 'b' }), t))
    lost = obs(nil, known: false)
    t = { 'decision' => nil, 'observations' => [s0, lost], 'inputs' => [] }
    assert_equal %w[focus_lost], cats(O.evaluate(fixture('final' => { 'focused' => 'b' }), t))
  end

  def test_activations_count_each_native_event_once
    s0 = obs('a'); s1 = obs('a', activations: [%w[a e1]]); s2 = obs('a', activations: [%w[a e1], %w[a e2]])
    t = { 'decision' => 'done', 'observations' => [s0, s2], 'inputs' => [press('select', s0, s1), press('select', s1, s2)] }
    r = O.evaluate(fixture('activations' => { 'a' => 2 }), t)
    assert_empty cats(r)
    assert_equal({ 'a' => 2 }, r['info']['activations'])
    assert_equal %w[extra_activation false_completion], cats(O.evaluate(fixture('activations' => { 'a' => 1 }), t))
    assert_equal %w[false_completion missing_activation], cats(O.evaluate(fixture('activations' => { 'a' => 3 }), t))
  end

  def test_unexpected_activation_unless_allowed
    s0 = obs('a'); s1 = obs('a', activations: [%w[a e1], %w[c e2]])
    t = { 'decision' => 'done', 'observations' => [s0, s1], 'inputs' => [press('select', s0, s1)] }
    assert_equal %w[false_completion unexpected_activation], cats(O.evaluate(fixture('activations' => { 'a' => 1 }), t))
    assert_empty cats(O.evaluate(fixture('activations' => { 'a' => 1 }, 'allowActivations' => %w[c]), t))
  end

  def test_visit_still_visible_state_and_input_limit
    s0 = obs('a'); s1 = obs('b', visible: %w[a b c], selected: { 'b' => false })
    t = { 'decision' => 'done', 'observations' => [s0, s1], 'inputs' => [press('down', s0, s1)] }
    e = fixture('visited' => [{ 'visible' => 'z' }], 'final' => { 'notVisible' => %w[c], 'selected' => { 'b' => true } }, 'maxInputs' => 0)
    assert_equal %w[false_completion not_visited still_visible unexpected_input wrong_state], cats(O.evaluate(e, t))
  end

  def test_agent_claims
    s0 = obs('a')
    ok = ->(decision) { { 'decision' => decision, 'observations' => [s0], 'inputs' => [] } }
    assert_equal %w[missed_completion], cats(O.evaluate(fixture('final' => { 'focused' => 'a' }), ok.call(nil)))
    assert_equal %w[wrong_abstention], cats(O.evaluate(fixture('final' => { 'focused' => 'a' }), ok.call('abstain')))
    assert_equal %w[missed_abstention], cats(O.evaluate(fixture('decision' => 'abstain', 'maxInputs' => 0), ok.call(nil)))
    assert_empty cats(O.evaluate(fixture('decision' => 'abstain', 'maxInputs' => 0), ok.call('abstain')))
  end

  def test_settings_rows_count_selects_and_screens
    a = { 'title' => 'Settings', 'focused' => 'General' }; b = { 'title' => 'General', 'focused' => 'About' }
    t = { 'decision' => 'done', 'observations' => [a, b, a], 'inputs' => [press('select', a, b), press('back', b, a)] }
    assert_empty cats(O.evaluate(EXPECT['settings-general-return'], t))
    t2 = { 'decision' => 'done', 'observations' => [a], 'inputs' => [] }
    assert_equal %w[false_completion missing_activation not_visited], cats(O.evaluate(EXPECT['settings-general-return'], t2))
  end

  def test_no_move_presses_are_info_only
    s0 = obs('a')
    t = { 'decision' => 'done', 'observations' => [s0, s0], 'inputs' => [press('left', s0, obs('a'))] }
    r = O.evaluate(fixture('final' => { 'focused' => 'a' }), t)
    assert_empty cats(r)
    assert_equal [{ 'input' => 0, 'button' => 'left', 'focused' => 'a' }], r['info']['noMovePresses']
  end

  def test_check_step_matches_labels_and_counts_step_activations
    before = O.state(obs('a'), 'fixture-planner'); after = O.state(obs('b'), 'fixture-planner')
    assert_empty O.check_step({ 'op' => 'focus', 'target' => 'Label B', 'expect' => { 'focused' => 'Label B', 'activations' => 0 } }, before, after, {})
    assert_equal %w[wrong_focus], O.check_step({ 'op' => 'focus', 'target' => 'c', 'expect' => { 'focused' => 'c' } }, before, after, {}).map { |d| d['category'] }
    step = { 'op' => 'activate', 'target' => 'Label B', 'times' => 1, 'expect' => { 'focused' => 'b', 'activations' => 1 } }
    assert_empty O.check_step(step, before, after, { 'b' => 1 })
    assert_equal %w[missing_activation], O.check_step(step, before, after, {}).map { |d| d['category'] }
    assert_equal %w[observation_missing], O.check_step(step, before, nil, {}).map { |d| d['category'] }
    settings = O.state({ 'title' => 'General', 'focused' => 'About' }, 'settings-planner')
    assert_equal %w[wrong_screen], O.check_step({ 'op' => 'activate', 'target' => 'General', 'expect' => { 'screen' => 'Network' } }, nil, settings, {}).map { |d| d['category'] }
  end

  def test_unknown_category_is_refused
    assert_raises(ArgumentError) { O.diff('looks_odd', nil, nil) }
  end

  # Regression on the saved QA666 runs: the state verdict agrees with TTR except where TTR's verdict also
  # requires the model's explicit abstention; the claim check disagrees only where TTR passed a stall with no done.
  def test_saved_runs_agree_with_native_verdicts
    paths = Dir.glob(File.join(ROOT, 'reports/work/QA666/runs/*/*/trajectory.json')).sort
    skip 'saved QA666 runs not present' if paths.empty?
    paths.each do |path|
      t = JSON.parse(File.read(path)); native = (t['verdict'] || {})['success']
      next if native.nil?
      r = O.evaluate(EXPECT.fetch(t['task']), t)
      state_ok = r['differences'].empty?
      failed = ((t['verdict'] || {})['checks'] || {}).reject { |_, v| v }.keys
      if native != state_ok
        assert_equal [false, ['explicit_abstention']], [native, failed], path
        assert_equal %w[missed_abstention], r['agent'].map { |d| d['category'] }, path
      elsif native && !r['agent'].empty?
        assert_equal [nil, %w[missed_completion]], [t['decision'], r['agent'].map { |d| d['category'] }], path
      end
    end
  end
end

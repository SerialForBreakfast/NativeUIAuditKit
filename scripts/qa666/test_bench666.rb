# Offline tests of the ADR-0035 phase C benchmark file, its checks and the reference planner.
# Usage: RUBYOPT=-Eutf-8 ruby scripts/qa666/test_bench666.rb
require 'minitest/autorun'
require 'tmpdir'
require_relative 'bench666'
require_relative 'qa666_provider'
require_relative 'expectation_oracle'

class Bench666Test < Minitest::Test
  def bench
    @bench ||= Bench666.load
  end

  def copy
    JSON.parse(JSON.generate(bench))
  end

  def test_benchmark_file_has_no_errors_and_meets_the_size_rule
    assert_equal [], Bench666.errors(bench)
    assert_operator bench['tasks'].size, :>=, 30
    assert_operator bench['tasks'].map { |t| t['screen'] }.uniq.size, :>=, 5
  end

  def test_build_script_reproduces_the_file
    before = File.read(Bench666::PATH)
    system('ruby', File.join(__dir__, 'bench666_build.rb'), out: File::NULL) or flunk 'build failed'
    assert_equal before, File.read(Bench666::PATH)
  end

  def test_file_is_the_frozen_benchmark
    assert_equal Bench666::FROZEN_SHA256, Bench666.sha256
    assert_equal true, bench['frozen']
  end

  def test_no_screen_is_in_both_splits
    by_screen = bench['tasks'].group_by { |t| t['screen'] }.transform_values { |ts| ts.map { |t| t['split'] }.uniq }
    assert(by_screen.values.all? { |s| s.size == 1 })
  end

  def test_pilot_screens_are_development
    %w[pulse northstar walks station settings].each { |s| assert_equal 'development', bench['screens'][s]['split'] }
  end

  def test_unknown_control_is_an_error
    b = copy
    b['tasks'].find { |t| t['id'] == 'radio-focus-jazz' }['expect']['final']['focused'] = 'benchmark.native.9'
    assert(Bench666.errors(b).any? { |e| e.include?('benchmark.native.9 is not a control') })
  end

  def test_absent_target_that_exists_is_an_error
    b = copy
    b['tasks'].find { |t| t['id'] == 'radio-absent-news' }['absentTarget'] = 'Jazz'
    assert(Bench666.errors(b).any? { |e| e.include?('absent target Jazz matches') })
  end

  def test_activation_on_a_screen_without_evidence_is_an_error
    b = copy
    b['tasks'].find { |t| t['id'] == 'radio-focus-jazz' }['expect']['activations'] = { 'benchmark.native.2' => 1 }
    assert(Bench666.errors(b).any? { |e| e.include?('without activation evidence') })
  end

  def test_split_mismatch_is_an_error
    b = copy
    b['tasks'].find { |t| t['id'] == 'radio-focus-jazz' }['split'] = 'development'
    assert(Bench666.errors(b).any? { |e| e.include?('differs from screen split') })
  end

  def test_case_for_returns_launch_arguments_and_initial_focus
    args, focus = Bench666.case_for(bench, 'guide-local-studio')
    assert_equal ['--fixture-benchmark', '--benchmark-family', 'schedule', '--fixture-sdk-layout'], args
    assert_equal 'benchmark.schedule.0', focus
    assert_raises(RuntimeError) { Bench666.case_for(bench, 'settings-focus-network') }
  end

  def test_inventory_errors
    screen = bench['screens']['station']
    raw = { 'observation' => { 'coverage' => { 'registeredControlsComplete' => true },
                               'controls' => [{ 'identity' => { 'id' => 'benchmark.identity.replace' }, 'publicLabel' => 'Replace this station' },
                                              { 'identity' => { 'id' => 'benchmark.identity.extra' }, 'publicLabel' => 'X' }] } }
    errs = Bench666.inventory_errors('station', screen, raw)
    assert_includes errs, 'station: benchmark.identity.next not registered'
    assert_includes errs, 'station: benchmark.identity.extra registered but not authored'
  end

  def test_reference_planner_returns_plans_in_order
    p = ReferencePlanner.new(bench)
    p.begin_task('northstar-profile-return')
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      plan = p.ask(d, 'Task: x')
      assert_equal %w[activate back], plan['steps'].map { |s| s['op'] }
      assert_raises(RuntimeError) { p.ask(d, 'Task: x') }
    end
    assert_equal 0, p.tokens
    refute p.unknown
  end

  def test_oracle_counts_selects_against_max_selects
    expect = { 'family' => 'fixture-planner', 'maxSelects' => 0, 'activations' => {}, 'decision' => 'done' }
    traj = { 'inputs' => [{ 'button' => 'select', 'state' => 'delivered' }], 'observations' => [], 'decision' => 'done' }
    diffs = ExpectationOracle.evaluate(expect, traj)['differences']
    assert_equal [{ 'category' => 'unexpected_input', 'expected' => { 'maxSelects' => 0 }, 'observed' => { 'selects' => 1 } }], diffs
  end
end

# Offline tests of the QA666 planner arm. TTR IO is stubbed with a 2-control fake screen.
# Usage: QA666_TTR_ROOT=/path/to/TVTestRig-worktree ruby scripts/qa666/test_goal_planner.rb
require 'minitest/autorun'
require 'tmpdir'
require_relative 'run_local_pair'

class FakeWorld
  attr_reader :pressed
  def initialize(activate_handler: true)
    @controls = { 'a' => { 'x' => 100, 'label' => 'Replace this station' }, 'b' => { 'x' => 900, 'label' => 'Continue' } }
    @focus = 'a'; @life = { 'a' => 'L0', 'b' => 'M0' }; @events = []; @seq = 0; @pressed = []; @handler = activate_handler
  end

  def ident(id)
    { 'id' => id, 'lifetime' => @life[id] }
  end

  def raw
    controls = @controls.map do |id, c|
      { 'identity' => ident(id), 'publicLabel' => c['label'], 'bounds' => { 'x' => c['x'], 'y' => 400, 'width' => 600, 'height' => 200 },
        'hidden' => false, 'enabled' => true, 'selected' => false }
    end
    nodes = controls.map { |c| { 'identity' => c['identity'], 'hidden' => false, 'bounds' => c['bounds'], 'clippedBounds' => c['bounds'] } }
    { 'appID' => 'x', 'processID' => 'p', 'runID' => 'r', 'sessionID' => 's', 'target' => 't', 'fresh' => true, 'owned' => true, 'gap' => false,
      'pending' => false, 'sequence' => @seq,
      'layout' => { 'truncated' => false, 'coordinateSpace' => 'window_points', 'viewport' => { 'x' => 0, 'y' => 0, 'width' => 1920, 'height' => 1080 }, 'nodes' => nodes },
      'benchmarkEvidence' => { 'schemaVersion' => 1, 'enabled' => true, 'dropped' => 0, 'producerID' => 'p', 'sequence' => @events.size, 'activations' => @events.map(&:dup) },
      'observation' => { 'controls' => controls, 'focusedIdentity' => ident(@focus), 'focusKnown' => true } }
  end

  def press(button)
    @pressed << button; @seq += 1
    case button
    when 'right' then @focus = 'b' if @focus == 'a'
    when 'left' then @focus = 'a' if @focus == 'b'
    when 'select'
      if @handler
        @events << { 'eventID' => "e#{@events.size + 1}", 'sequence' => @events.size + 1, 'identity' => ident(@focus), 'handler' => 'replaceStation' }
        @life[@focus] = @life[@focus].succ # Replace rebuilds the control with the same id.
      end
    end
  end
end

class FakePlanner
  attr_reader :prompts, :unknown
  def initialize(plans); @plans = plans; @prompts = []; @unknown = false; end
  def ask(_dir, prompt, _image = nil); @prompts << prompt; @plans.shift; end
end

class GoalPlannerTest < Minitest::Test
  def run_plan(plans, world = FakeWorld.new)
    t = LocalTurnRun.allocate
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |out|
      t.instance_variable_set(:@out, out); t.instance_variable_set(:@run, 'r')
      t.instance_variable_set(:@provider, FakePlanner.new(plans))
      t.define_singleton_method(:restart) { |*_| nil }
      t.define_singleton_method(:survey) { |_| raise 'survey must not run on the image arm' }
      t.define_singleton_method(:sample) { world.raw }
      t.define_singleton_method(:snap) { {} }
      t.define_singleton_method(:screenshot) { |dir, _| File.join(dir, 's.png') }
      t.define_singleton_method(:content) { |*a| [nil, { 'path' => File.join(a[4], 's.jpg') }] }
      t.define_singleton_method(:persist) { nil }
      t.define_singleton_method(:execute_button) do |b, _expected = nil|
        before = @observations.last; world.press(b); after = world.raw
        @inputs << { 'button' => b, 'state' => 'delivered', 'before' => before, 'after' => after }; @observations << after
        raise 'no progress' if MatchedFixtureBenchmark.signature(before) == MatchedFixtureBenchmark.signature(after)
      end
      MatchedFixtureBenchmark.stub(:healthy!, nil) do
        t.plan_episode('station-replace-twice', 'image960', 'Activate Replace this station twice, then focus Continue.', slot: 's')
      end
    end
    [t, world]
  end

  def step(op, target, times = 1)
    { 'op' => op, 'target' => target, 'times' => times }
  end

  def test_host_executes_activations_and_focus_then_done
    t, w = run_plan([{ 'steps' => [step('activate', 'Replace this station', 2), step('focus', 'Continue')], 'after' => 'done' }])
    assert_nil t.instance_variable_get(:@issue)
    assert_equal %w[select select right], w.pressed
    assert_equal 'done', t.instance_variable_get(:@decision)
    refute_includes t.instance_variable_get(:@provider).prompts.first, 'home'
  end

  def test_replan_gets_the_done_steps
    t, w = run_plan([{ 'steps' => [step('activate', 'Replace this station')], 'after' => 'replan' },
                     { 'steps' => [step('focus', 'Continue')], 'after' => 'done' }])
    assert_equal %w[select right], w.pressed
    assert_includes t.instance_variable_get(:@provider).prompts.last, '"op":"activate"'
  end

  def test_missing_first_target_with_no_input_is_abstention
    t, w = run_plan([{ 'steps' => [step('activate', 'Airplane Mode')], 'after' => 'done' }])
    assert_empty w.pressed
    assert_equal 'abstain', t.instance_variable_get(:@decision)
    assert_nil t.instance_variable_get(:@issue)
  end

  def test_activation_without_native_event_is_an_issue
    t, w = run_plan([{ 'steps' => [step('activate', 'Continue')], 'after' => 'done' }], FakeWorld.new(activate_handler: false))
    assert_equal %w[right select], w.pressed
    assert_nil t.instance_variable_get(:@decision)
    assert_match(/no progress|activation not observed/, t.instance_variable_get(:@issue))
  end

  def test_resolve_and_directions
    controls = [{ 'identity' => { 'id' => 'w' }, 'publicLabel' => "＋  Watchlist", 'enabled' => true, 'hidden' => false },
                { 'identity' => { 'id' => 'v' }, 'publicLabel' => '▶  Watch', 'enabled' => true, 'hidden' => false }]
    assert_equal 'w', GoalPlanner.resolve(controls, %w[w v], 'Watchlist').dig('identity', 'id')
    assert_equal 'v', GoalPlanner.resolve(controls, %w[w v], 'v').dig('identity', 'id')
    assert_nil GoalPlanner.resolve(controls, %w[w v], 'Airplane Mode')
    from = { 'x' => 0, 'y' => 0, 'width' => 100, 'height' => 100 }
    below = { 'x' => 0, 'y' => 900, 'width' => 100, 'height' => 100 }
    assert_equal %w[down], GoalPlanner.directions_toward(from, below, [])
    assert_empty GoalPlanner.directions_toward(from, below, %w[down])
    assert_equal [['right', 'b'], ['down', 'c']], GoalPlanner.route({ 'a' => { 'right' => 'b' }, 'b' => { 'down' => 'c' } }, 'a', 'c')
  end

  def test_explore_goes_to_the_nearest_untried_direction
    dead = Hash.new { |h, k| h[k] = [] }
    edges = { 'watch' => { 'right' => 'list', 'up' => 'home', 'down' => 'watch', 'left' => 'watch' },
              'list' => { 'left' => 'watch' }, 'home' => { 'down' => 'watch' } }
    dead['list'].concat(%w[up right down])
    # watch has no untried direction; list is fully tried; home is the nearest control with untried directions.
    assert_equal 'up', GoalPlanner.explore(edges, dead, 'watch')
    assert_equal 'up', GoalPlanner.explore({}, dead, 'new')
    full = Hash.new { |h, k| h[k] = %w[up down left right] }
    assert_nil GoalPlanner.explore({}, full, 'x')
  end

  def test_instruction_allows_off_screen_targets_and_has_no_home
    text = GoalPlanner.instruction('Do X.', [], nil, image: true)
    assert_includes text, 'off the screen'
    assert_includes text, 'by its name in the task'
    refute_includes text.downcase, ' home'
    assert_equal 8, GoalPlanner::MAX_PLANS
  end
end

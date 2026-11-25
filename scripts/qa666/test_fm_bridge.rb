# Offline tests of the Foundation Model transport. A fake bridge process stands in for fm_bridge.swift.
# Usage: RUBYOPT=-Eutf-8 ruby scripts/qa666/test_fm_bridge.rb
require 'minitest/autorun'
require 'tmpdir'
require_relative 'local_ollama_session'
require_relative 'qa666_provider'
require_relative 'goal_planner'

class FakeIO
  attr_reader :sent

  def initialize(replies)
    @lines = [JSON.generate('ready' => true, 'contextSize' => 8192, 'vision' => true)] + replies.map { |r| JSON.generate(r) }
    @sent = []
  end

  def puts(line); @sent << JSON.parse(line); end
  def gets; @lines.shift; end
end

class FoundationBridgeTest < Minitest::Test
  PLAN = '{"after":"done","steps":[{"op":"focus","target":"a","times":1}]}'

  def session(io)
    LocalOllamaSession.new(model: FoundationBridge::MODEL, deadline: Time.now + 60, max_calls: 3, max_tokens: 20_000,
                           schema: 'plan', http: FoundationBridge.new(io: io))
  end

  def test_plan_reply_passes_schema_check_and_counts_usage
    io = FakeIO.new([{ 'message' => { 'content' => PLAN }, 'prompt_eval_count' => 900, 'eval_count' => 30, 'load_duration' => 0 }])
    s = session(io)
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      assert_equal 'done', s.ask(d, 'Task: x')['after']
    end
    assert_equal 930, s.tokens
    assert_equal({ 'prompt' => 'Task: x', 'image' => nil, 'schema' => 'plan', 'maxOutput' => 1500 }, io.sent.first)
  end

  def test_counted_generation_error_is_a_refusal_not_a_campaign_stop
    io = FakeIO.new([{ 'error' => 'guardrail', 'message' => { 'content' => '' }, 'prompt_eval_count' => 900, 'eval_count' => 0 }])
    s = session(io)
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      assert_raises(JSON::ParserError) { s.ask(d, 'Task: x') }
    end
    refute s.unknown
    assert_equal 900, s.tokens
  end

  def test_uncounted_error_stops_with_unknown_usage
    s = session(FakeIO.new([{ 'error' => 'decode failed' }]))
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      assert_raises(RuntimeError) { s.ask(d, 'Task: x') }
    end
    assert s.unknown
  end

  def test_only_plan_schema_is_sent
    bridge = FoundationBridge.new(io: FakeIO.new([]))
    request = { messages: [{ role: 'user', content: 'x' }], format: LocalOllamaSession::TURN_SCHEMA, options: {} }
    assert_raises(RuntimeError) { bridge.call(request, 10) }
  end

  def test_provider_selection
    assert_nil QA666Provider.http({ 'model' => 'gemma4:12b' }, planner: true, checks: false)
    assert_raises(RuntimeError) { QA666Provider.http({ 'provider' => 'foundation', 'model' => 'gemma4:12b' }, planner: true, checks: false) }
    fm = { 'provider' => 'foundation', 'model' => FoundationBridge::MODEL }
    assert_raises(RuntimeError) { QA666Provider.http(fm, planner: false, checks: false) }
    assert_raises(RuntimeError) { QA666Provider.http(fm, planner: true, checks: true) }
    assert_raises(RuntimeError) { QA666Provider.http({ 'provider' => 'cloud', 'model' => 'x' }, planner: true, checks: false) }
  end
end

# ADR-0035 host question: press-schema-v1 transport, stored error text, and the op change.
class PressQuestionTest < Minitest::Test
  def press_session(io)
    LocalOllamaSession.new(model: FoundationBridge::MODEL, deadline: Time.now + 60, max_calls: 3, max_tokens: 20_000,
                           schema: 'press', http: FoundationBridge.new(io: io, schema: 'plan-described'))
  end

  def test_press_request_uses_press_schema_and_checks_reply
    io = FakeIO.new([{ 'message' => { 'content' => '{"press":true}' }, 'prompt_eval_count' => 120, 'eval_count' => 4 },
                     { 'message' => { 'content' => '{"press":"yes"}' }, 'prompt_eval_count' => 120, 'eval_count' => 4 }])
    s = press_session(io)
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      assert_equal({ 'press' => true }, s.ask(d, 'q'))
      assert_raises(RuntimeError) { s.ask(d, 'q') }
    end
    assert_equal %w[press press], io.sent.map { |r| r['schema'] }
  end

  def test_empty_reply_keeps_the_provider_error_text
    io = FakeIO.new([{ 'error' => 'guardrailViolation', 'message' => { 'content' => '' }, 'prompt_eval_count' => 900, 'eval_count' => 0 }])
    s = press_session(io)
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      assert_raises(JSON::ParserError) { s.ask(d, 'q') }
      assert_equal 'guardrailViolation', JSON.parse(File.read(File.join(d, 'response.json')))['providerError']
    end
  end

  def test_press_targets_and_apply
    plan = { 'after' => 'done', 'steps' => [{ 'op' => 'focus', 'target' => 'a', 'times' => 1 },
                                            { 'op' => 'activate', 'target' => 'b', 'times' => 2 },
                                            { 'op' => 'back', 'target' => nil, 'times' => 1 }] }
    assert_equal [0], GoalPlanner.press_targets(plan, 'focus-only')
    assert_equal [0, 1], GoalPlanner.press_targets(plan, 'all')
    assert_raises(ArgumentError) { GoalPlanner.press_targets(plan, 'some') }
    out = GoalPlanner.apply_press(plan, 0 => true, 1 => false)
    assert_equal [['activate', 'a', 1], ['focus', 'b', 1], ['back', nil, 1]], out['steps'].map { |s| [s['op'], s['target'], s['times']] }
    assert_equal 2, plan['steps'][1]['times'] # The input plan is not changed.
  end

  def test_press_question_text
    q = GoalPlanner.press_question('bare', ' Add X once. ', 'Watchlist')
    assert_equal 'Task: Add X once. Control: Watchlist. To do this task, must the remote press select on this control? Answer with press true or press false.', q
  end
end

require 'minitest/autorun'
require 'tmpdir'
require_relative 'local_ollama_session'

class LocalOllamaSessionTest < Minitest::Test
  def session(replies, **kw)
    queue = replies.dup
    seen = []
    http = ->(request, _timeout) { seen << request; queue.shift }
    s = LocalOllamaSession.new(model: 'gemma4:e4b', deadline: Time.now + 60, max_calls: kw.fetch(:calls, 8),
                               max_tokens: kw.fetch(:tokens, 20_000), http: http)
    [s, seen]
  end

  def reply(content, prompt = 900, output = 30)
    { 'message' => { 'content' => content }, 'prompt_eval_count' => prompt, 'eval_count' => output, 'load_duration' => 0 }
  end

  def test_parses_json_and_counts_tokens_and_calls
    s, seen = session([reply('{"steps":["down","done"]}')])
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      assert_equal({ 'steps' => %w[down done] }, s.ask(d, 'Find Homeward.'))
    end
    assert_equal [1, 930], [s.calls, s.tokens]
    assert_equal 0, seen.first[:options][:temperature]
    assert_equal 'json', seen.first[:format]
    refute seen.first[:messages].first.key?(:images)
  end

  def test_schema_mode_sends_step_schema
    s, seen = session([reply('{"steps":["down","done"]}')])
    s.instance_variable_set(:@schema, 'v1')
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) { |d| s.ask(d, 'x') }
    assert_equal %w[up down left right done abstain], seen.first[:format][:properties][:steps][:items][:enum]
  end

  def test_schema_v2_builds_steps_from_moves_and_terminal
    s, seen = session([reply('{"moves":["down","down"],"terminal":"done"}')])
    s.instance_variable_set(:@schema, 'v2')
    out = nil
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) { |d| out = s.ask(d, 'x') }
    assert_equal({ 'steps' => %w[down down done] }, out)
    assert_equal %w[moves terminal], seen.first[:format][:required]
  end

  def test_turn_schema_returns_1_action_and_rejects_others
    s, seen = session([reply('{"action":"down"}'), reply('{"action":"home"}')])
    s.instance_variable_set(:@schema, 'turn')
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      assert_equal({ 'action' => 'down' }, s.ask(d, 'x'))
      assert_raises(RuntimeError) { s.ask(d, 'x') }
    end
    assert_equal %w[action], seen.first[:format][:required]
    refute_includes seen.first[:format][:properties][:action][:enum], 'home'
  end

  def test_check_schema_accepts_only_a_boolean
    replies = [reply('{"complete":true}'), reply('{"complete":"yes"}')]
    s = LocalOllamaSession.new(model: 'm', deadline: Time.now + 60, max_calls: 2, max_tokens: 20_000, schema: 'check', max_output: 1_000,
                               http: ->(r, _) { assert_equal({ type: 'boolean' }, r[:format][:properties][:complete]); replies.shift })
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      assert_equal({ 'complete' => true }, s.ask(d, 'x'))
      assert_raises(RuntimeError) { s.ask(d, 'x') }
    end
  end

  def test_output_limit_is_configurable_and_bounded
    seen = []
    s = LocalOllamaSession.new(model: 'm', deadline: Time.now + 60, max_calls: 2, max_tokens: 20_000, max_output: 4_000,
                               http: ->(r, t) { seen << [r, t]; reply('{}') }, read_timeout: 600)
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) { |d| s.ask(d, 'x') }
    assert_equal 4_000, seen.first[0][:options][:num_predict]
    assert_operator seen.first[1], :<=, 60
    assert_raises(RuntimeError) { LocalOllamaSession.new(model: 'm', deadline: Time.now, max_calls: 1, max_tokens: 9_000, max_output: 50_000) }
  end

  def test_image_arm_sends_1_image
    s, seen = session([reply('{"steps":["done"]}')])
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      jpg = File.join(d, 'x.jpg'); File.binwrite(jpg, "\xFF\xD8\xFFdata".b)
      s.ask(d, 'Find Homeward.', jpg)
    end
    assert_equal 1, seen.first[:messages].first[:images].size
  end

  def test_non_object_reply_raises_and_is_not_retried
    s, seen = session([reply('["down"]'), reply('{"steps":["done"]}')])
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      assert_raises(RuntimeError) { s.ask(d, 'x') }
    end
    assert_equal 1, seen.size
  end

  def test_missing_usage_stops_campaign
    s, = session([{ 'message' => { 'content' => '{}' } }, reply('{}')])
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      assert_raises(RuntimeError) { s.ask(d, 'x') }
      assert s.unknown
      assert_raises(RuntimeError) { s.ask(d, 'x') }
    end
  end

  def test_call_and_token_ceilings
    s, = session([reply('{}'), reply('{}')], calls: 1)
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      s.ask(d, 'x')
      assert_raises(RuntimeError) { s.ask(d, 'x') }
    end
    s2, = session([reply('{}', 17_000, 10)], tokens: 20_000)
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      s2.ask(d, 'x')
      assert_raises(RuntimeError) { s2.ask(d, 'x') } # 17,010 + 4,000 reserve > 20,000
    end
  end
end

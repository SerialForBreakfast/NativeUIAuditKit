# Offline test of the QA666 multi-turn loop. TTR IO (restart, sample, screenshot, presses) is stubbed.
# Usage: QA666_TTR_ROOT=/path/to/TVTestRig-worktree ruby scripts/qa666/test_turn_episode.rb
require 'minitest/autorun'
require 'minitest/mock'
require 'tmpdir'
require_relative 'run_local_pair'

class FakeProvider
  attr_reader :prompts, :images, :unknown
  def initialize(actions); @actions = actions; @prompts = []; @images = []; @unknown = false; end
  def ask(_dir, prompt, image = nil); @prompts << prompt; @images << image; { 'action' => @actions.shift }; end
end

class TurnEpisodeTest < Minitest::Test
  def run_episode(actions, arm: 'image960', max_turns: 5)
    t = LocalTurnRun.allocate
    pressed = []
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |out|
      t.instance_variable_set(:@out, out); t.instance_variable_set(:@run, 'r')
      t.instance_variable_set(:@max_turns, max_turns); t.instance_variable_set(:@provider, FakeProvider.new(actions))
      t.define_singleton_method(:restart) { |*_| nil }
      t.define_singleton_method(:survey) { |_| raise 'survey must not run' if arm == 'image960' }
      t.define_singleton_method(:sample) { { 'runID' => 'r' } }
      t.define_singleton_method(:snap) { {} }
      t.define_singleton_method(:screenshot) { |dir, _| File.join(dir, 's.png') }
      t.define_singleton_method(:content) { |*a| [nil, { 'path' => File.join(a[4], 's.jpg') }] }
      t.define_singleton_method(:persist) { nil }
      t.define_singleton_method(:execute_button) { |b| pressed << b }
      MatchedFixtureBenchmark.stub(:signature, 'same') { t.turn_episode('walks-scroll-homeward', arm, 'Find Homeward.', slot: 's') }
    end
    puts t.instance_variable_get(:@issue) if ENV["DEBUG"]
    [t, pressed]
  end

  def test_stops_on_done_and_sends_history
    t, pressed = run_episode(%w[down down done])
    assert_equal %w[down down], pressed
    assert_equal 'done', t.instance_variable_get(:@decision)
    p = t.instance_variable_get(:@provider)
    assert_equal 3, p.prompts.size
    assert_includes p.prompts.last, 'oldest first: down, down.'
    assert p.images.all? { |i| i.end_with?('s.jpg') }
  end

  def test_turn_limit_is_an_issue_not_success
    t, pressed = run_episode(%w[down down down], max_turns: 3)
    assert_equal 3, pressed.size
    assert_nil t.instance_variable_get(:@decision)
    assert_match(/turn limit/, t.instance_variable_get(:@issue))
  end

  def test_abstain_sends_no_input
    t, pressed = run_episode(%w[abstain])
    assert_empty pressed
    assert_equal 'abstain', t.instance_variable_get(:@decision)
  end

  def test_instruction_has_no_home_and_lists_actions
    text = LocalTurnRun.turn_instruction('Do X.', [], nil)
    assert_includes text, 'up|down|left|right|select|back|done|abstain'
    refute_includes text, 'home'
    assert_includes text, 'oldest first: none.'
  end
end

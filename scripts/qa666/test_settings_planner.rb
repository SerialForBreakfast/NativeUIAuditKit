# Offline tests of the QA666 Settings planner. A fake Settings app replaces TTR.
require 'minitest/autorun'
require 'tmpdir'
require_relative 'settings_planner'

class FakeSettings
  ROWS = ['General', 'Profiles and Accounts', 'Apps', 'Accessibility', 'Video and Audio', 'Screen Saver',
          'AirPlay and Apple Home', 'Remotes and Devices', 'Network', 'System', 'Developer', 'Privacy and Security'].freeze
  PAGES = { 'General' => ['About', 'Appearance', 'Sleep After'] }.freeze
  attr_reader :pressed
  def initialize; @pressed = []; relaunch; end
  def relaunch; @stack = [['Settings', 0]]; end
  def rows(title)
    title == 'Settings' ? ROWS : PAGES.fetch(title)
  end
  def observe
    title, i = @stack.last
    { 'title' => title, 'focused' => rows(title)[i], 'cellCount' => rows(title).size }
  end
  def press(b)
    @pressed << b
    title, i = @stack.last
    case b
    when 'down' then @stack[-1] = [title, [i + 1, rows(title).size - 1].min]
    when 'up' then @stack[-1] = [title, [i - 1, 0].max]
    when 'select' then @stack << [rows(title)[i], 0] if PAGES.key?(rows(title)[i])
    when 'back' then @stack.pop if @stack.size > 1
    end
    { 'state' => 'delivered' }
  end
  def screenshot(_dir)
    'screen.jpg'
  end
end

class PlanProvider
  attr_reader :prompts
  def initialize(plans); @plans = plans; @prompts = []; end
  def ask(_dir, prompt, _image = nil); @prompts << prompt; @plans.shift; end
end

class SettingsPlannerTest < Minitest::Test
  def step(op, target)
    { 'op' => op, 'target' => target, 'times' => 1 }
  end

  def episode(task, plans, arm: 'text')
    io = FakeSettings.new
    ep = nil
    Dir.mktmpdir(nil, File.expand_path('../../.build', __dir__)) do |d|
      ep = SettingsEpisode.new(io: io, provider: PlanProvider.new(plans), rows: FakeSettings::ROWS, task: task, arm: arm, dir: d)
      ep.run
    end
    v = SettingsQA.grade(task, rows: FakeSettings::ROWS, observations: ep.observations, inputs: ep.inputs, decision: ep.decision)
    [ep, io, v]
  end

  def test_focus_network_by_index
    ep, io, v = episode('settings-focus-network', [{ 'steps' => [step('focus', 'Network')], 'after' => 'done' }])
    assert v['success'], v.inspect
    assert_equal ['down'] * 8, io.pressed
    assert_includes ep.plans.size.to_s, '1'
  end

  def test_general_open_and_return
    ep, io, v = episode('settings-general-return', [{ 'steps' => [step('activate', 'General')], 'after' => 'replan' },
                                                    { 'steps' => [step('back', nil)], 'after' => 'done' }])
    assert v['success'], v.inspect
    assert_equal %w[select back], io.pressed
  end

  def test_last_row_without_probe
    _, io, v = episode('settings-last-row', [{ 'steps' => [step('focus', 'Privacy and Security')], 'after' => 'done' }])
    assert v['success'], v.inspect
    assert_equal 11, io.pressed.size
  end

  def test_absent_row_abstains_without_input
    _, io, v = episode('settings-absent-row', [{ 'steps' => [step('focus', 'Bluetooth Keyboard')], 'after' => 'done' }])
    assert v['success'], v.inspect
    assert_empty io.pressed
  end

  def test_select_outside_reviewed_entries_is_refused_before_dispatch
    ep, io, v = episode('settings-general-return', [{ 'steps' => [step('activate', 'Apps')], 'after' => 'done' }])
    refute v['success']
    refute_includes io.pressed, 'select'
    assert_match(/select refused/, ep.issue)
  end

  def test_back_on_top_page_is_refused
    ep, io, _ = episode('settings-focus-network', [{ 'steps' => [step('back', nil)], 'after' => 'done' }])
    assert_empty io.pressed
    assert_match(/back refused/, ep.issue)
  end

  def test_graders_reject_wrong_outcomes
    _, _, v = episode('settings-focus-network', [{ 'steps' => [step('focus', 'System')], 'after' => 'done' }])
    refute v['success']
    _, _, v = episode('settings-last-row', [{ 'steps' => [step('focus', 'Developer')], 'after' => 'done' }])
    refute v['checks']['focused_last']
    _, _, v = episode('settings-absent-row', [{ 'steps' => [], 'after' => 'done' }])
    refute v['checks']['abstained']
  end

  def test_instruction_lists_rows_for_text_only
    assert_includes SettingsQA.instruction('Do X.', { 'rows' => %w[A B] }, [], image: false), '"rows":["A","B"]'
    refute_includes SettingsQA.instruction('Do X.', { 'rows' => %w[A B] }, [], image: true), 'Screen:'
  end
end

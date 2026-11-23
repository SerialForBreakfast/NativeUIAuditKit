# Offline tests of ADR-0035 phase A prompt slots. No model call and no TTR.
# Usage: ruby scripts/qa666/test_prompt_slots.rb
require 'minitest/autorun'
require_relative 'prompt_slots'

class PromptSlotsTest < Minitest::Test
  RUNS = File.expand_path('../../reports/work/QA666/runs', __dir__)
  # Runs that used the current planner text. turns-25 used the planner text before the 4 fixes, so it is not P0.
  P0_RUNS = { 'turns-26-planner-fixed' => 'fixture-planner', 'turns-27a-planner-finish' => 'fixture-planner',
              'turns-27b-planner-finish' => 'fixture-planner', 'settings-01' => 'settings-planner' }.freeze

  # Split a saved prompt into its inputs: task text, done steps and snapshot.
  def self.parse(family, prompt)
    fam = PromptSlots.family(family)
    task = prompt[/Task: (.*?)#{Regexp.escape(fam['frame']['p0'])}/m, 1]
    rest = prompt.split(' Steps already done: ', 2).last
    label = fam['snapshot-label']
    done_text, snap = rest.include?(label) ? rest.split(label, 2) : [rest, nil]
    done_text = done_text.chomp('.')
    [task, done_text == 'none' ? [] : JSON.parse(done_text), snap && JSON.parse(snap)]
  end

  def saved_requests
    P0_RUNS.flat_map do |run, family|
      Dir.glob(File.join(RUNS, run, '**', 'request.json')).sort.map { |p| [p, family, JSON.parse(File.read(p))] }
    end
  end

  def test_p0_rebuilds_every_saved_planner_request_byte_for_byte
    rows = saved_requests
    assert_operator rows.size, :>=, 20, 'expected the saved planner requests of 4 runs'
    rows.each do |path, family, req|
      task, done, snap = self.class.parse(family, req['prompt'])
      refute_nil task, path
      descriptor = req['image'] ? 'image' : (family == 'fixture-planner' ? 'compact-p0' : 'text-p0')
      built = PromptSlots.build(family, { 'descriptor' => descriptor }, task: task, done_steps: done, projection: snap)
      assert_equal req['prompt'], built[:text], path
      assert_equal req['promptSHA256'], built[:record]['promptSHA256'], path
    end
  end

  def test_planners_use_p0
    require_relative 'settings_planner'
    page = { 'title' => 'Settings', 'rows' => %w[General Network] }
    assert_equal PromptSlots.build('settings-planner', { 'descriptor' => 'text-p0' }, task: 'Do X.', done_steps: [], projection: page)[:text],
                 SettingsQA.instruction('Do X.', page, [], image: false)
  end

  def test_prompt_id_ignores_inputs_and_tracks_variants
    a = PromptSlots.build('fixture-planner', { 'descriptor' => 'compact-p0' }, task: 'A', done_steps: [], projection: { 'controls' => [] })
    b = PromptSlots.build('fixture-planner', { 'descriptor' => 'compact-p0' }, task: 'B', done_steps: [{ 'op' => 'back' }], projection: { 'x' => 1 })
    assert_equal a[:record]['promptID'], b[:record]['promptID']
    refute_equal a[:record]['promptSHA256'], b[:record]['promptSHA256']
    PromptSlots::FAMILIES.each_key do |family|
      PromptSlots.family(family)['descriptor'].each do |d|
        ids = PromptSlots.single_slot_variants(family, d).map { |v| PromptSlots.prompt_id(family, v) }
        assert_equal ids.uniq.size, ids.size, "#{family} #{d}: 2 variants share an ID"
      end
    end
    refute_equal PromptSlots.prompt_id('fixture-planner', 'descriptor' => 'image'),
                 PromptSlots.prompt_id('fixture-planner', 'descriptor' => 'compact-p0')
  end

  def test_explicit_p0_values_give_the_same_id_as_defaults
    assert_equal PromptSlots.prompt_id('fixture-planner', 'descriptor' => 'image'),
                 PromptSlots.prompt_id('fixture-planner', 'descriptor' => 'image', 'frame' => 'p0', 'schema' => 'plan',
                                       'example' => 'none', 'rules' => %w[never-activate off-screen])
  end

  def test_rule_order_is_part_of_the_variant
    refute_equal PromptSlots.prompt_id('fixture-planner', 'descriptor' => 'image', 'rules' => %w[never-activate off-screen]),
                 PromptSlots.prompt_id('fixture-planner', 'descriptor' => 'image', 'rules' => %w[off-screen never-activate])
  end

  def test_forbidden_list_needs_a_list_and_renders_it
    v = { 'descriptor' => 'image', 'rules' => %w[never-activate off-screen forbidden-list] }
    assert_raises(ArgumentError) { PromptSlots.build('fixture-planner', v, task: 'T', done_steps: []) }
    text = PromptSlots.build('fixture-planner', v, task: 'T', done_steps: [], forbidden: ['activate Neon City', 'press Home'])[:text]
    assert_includes text, ' Forbidden actions: activate Neon City; press Home.'
  end

  def test_unknown_variants_are_refused
    assert_raises(ArgumentError) { PromptSlots.build('fixture-planner', {}, task: 'T', done_steps: []) }
    assert_raises(ArgumentError) { PromptSlots.prompt_id('fixture-planner', 'descriptor' => 'text-p0') }
    assert_raises(ArgumentError) { PromptSlots.prompt_id('fixture-planner', 'descriptor' => 'image', 'frame' => 'long') }
    assert_raises(ArgumentError) { PromptSlots.prompt_id('fixture-planner', 'descriptor' => 'image', 'rules' => %w[off-screen off-screen]) }
    assert_raises(ArgumentError) { PromptSlots.prompt_id('nope', 'descriptor' => 'image') }
    assert_raises(ArgumentError) { PromptSlots.build('fixture-planner', { 'descriptor' => 'compact-min' }, task: 'T', done_steps: []) }
  end

  def test_compact_descriptors_drop_only_their_fields
    snap = { 'focusedControl' => 'a', 'controls' => [{ 'id' => 'a', 'label' => 'A', 'bounds' => { 'x' => 1 } }],
             'screenText' => 'OCR', 'routes' => { 'a' => {} }, 'notVisible' => [{ 'id' => 'b', 'label' => 'B' }], 'layoutTruncated' => true }
    assert_equal snap, PromptSlots.descriptor('fixture-planner', 'compact-p0', snap)
    refute PromptSlots.descriptor('fixture-planner', 'compact-no-ocr', snap).key?('screenText')
    refute PromptSlots.descriptor('fixture-planner', 'compact-no-routes', snap).key?('routes')
    assert_equal({ 'focusedControl' => 'a', 'controls' => [{ 'id' => 'a', 'label' => 'A' }], 'notVisible' => [{ 'id' => 'b', 'label' => 'B' }] },
                 PromptSlots.descriptor('fixture-planner', 'compact-min', snap))
    assert_equal 'OCR', snap['screenText'], 'the descriptor must not change the host snapshot'
  end

  def test_qa_plan_schema_text_and_format_agree
    text = PromptSlots.build('fixture-planner', { 'descriptor' => 'image', 'schema' => 'qa-plan' }, task: 'T', done_steps: [])[:text]
    assert_includes text, '"expect":{"focused":"...","screen":"...","activations":1}'
    assert_includes text, ' expect: what the screen must show after the step.'
    step = PromptSlots::QA_PLAN_SCHEMA[:properties][:steps][:items]
    assert_equal %w[op target times expect], step[:required]
    assert_equal %w[focused screen activations], step[:properties][:expect][:required]
  end

  def test_fixed_text_never_offers_the_home_button
    PromptSlots::FAMILIES.each do |family, fam|
      fam['descriptor'].each do |d|
        PromptSlots.single_slot_variants(family, d).each do |v|
          v = v.merge('rules' => (v['rules'] || fam['p0-rules'])) # keep the forbidden-list rule out: it needs task input
          next if v['rules'].include?('forbidden-list')
          text = PromptSlots.build(family, v, task: 'T', done_steps: [], projection: d == 'image' ? nil : {})[:text]
          refute_match(/\bhome\b/i, text, "#{family} #{v}")
        end
      end
    end
  end

  def test_config_record_keeps_options_outside_the_prompt_id
    rec = PromptSlots.build('fixture-planner', { 'descriptor' => 'image' }, task: 'T', done_steps: [])[:record]
    a = PromptSlots.config_record(rec, model: 'gemma4:12b', quantization: 'Q4_K_M', think: false, max_output_tokens: 4000)
    b = PromptSlots.config_record(rec, model: 'gemma4:e4b', quantization: 'Q4_K_M', think: false, max_output_tokens: 4000)
    assert_equal a['promptID'], b['promptID']
    refute_equal a['configID'], b['configID']
    assert_equal 'plan-schema-v1', a['outputSchema']
  end
end

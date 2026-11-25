# ADR-0035 host question, offline screen (Joe, 2026-11-24: "Host yes/no question").
# For each base prompt, the Foundation Model writes the first plan of each Fixture task (12 inputs).
# Then the host asks 1 press question for each chosen target and sets the op from the answer.
# The check is the same as fm_prompt_screen.rb (reference first plans). No TTR and no presses.
# Usage: QA666_TTR_ROOT=... RUBYOPT=-Eutf-8 ruby scripts/qa666/fm_press_screen.rb OUT.json
require_relative 'fm_prompt_screen'
require_relative 'goal_planner'

FAM = PromptSlots.family('fixture-planner')
ALL_RULES = FAM['p0-rules'] + %w[op-by-verb times-count back-only-return abstain-absent]
BASES = [
  { 'name' => 'P0/plan', 'bridge' => 'plan', 'variant' => {} },
  { 'name' => 'turns-29/plan-described', 'bridge' => 'plan-described', 'variant' => { 'rules' => ALL_RULES } }
].freeze
CONFIGS = [nil] + GoalPlanner::PRESS_QUESTIONS.keys.product(GoalPlanner::PRESS_MODES)

def ask(bridge, request)
  reply = bridge.call(request, 60)
  [(JSON.parse(reply.dig('message', 'content')) rescue nil), reply]
end

inputs, labels = load_inputs
rows = []
BASES.each do |base|
  bridge = FoundationBridge.new(schema: base['bridge'])
  answers = {} # [kind, task, control] => true|false|nil; 1 call per distinct question.
  inputs.each do |i|
    b = PromptSlots.build('fixture-planner', base['variant'].merge('descriptor' => i['arm'] == 'image960' ? 'image' : 'compact-p0'),
                          task: i['task'], done_steps: [], projection: i['snap'], forbidden: EXPECT.fetch(i['key'], {}).fetch('forbidden', []))
    plan, reply = ask(bridge, messages: [{ role: 'user', content: b[:text], images: i['image'] ? [i['image']] : nil }.compact],
                              format: LocalOllamaSession::PLAN_SCHEMA, options: { num_predict: 1500 })
    CONFIGS.each do |config|
      calls = 0; tokens = 0; asked = []
      final = plan
      if plan && config
        kind, mode = config
        got = {}
        GoalPlanner.press_targets(plan, mode).each do |n|
          target = plan['steps'][n]['target']
          control = labels.fetch(i['key']).fetch(target, target) # A control id becomes its public label.
          question = GoalPlanner.press_question(kind, i['task'], control)
          key = [kind, i['task'], control]
          unless answers.key?(key)
            a, r = ask(bridge, messages: [{ role: 'user', content: question }], format: LocalOllamaSession::PRESS_SCHEMA, options: { num_predict: 50 })
            answers[key] = { 'press' => a && a['press'], 'tokens' => r['prompt_eval_count'].to_i + r['eval_count'].to_i, 'error' => r['error'] }
          end
          calls += 1; tokens += answers[key]['tokens']
          asked << { 'step' => n + 1, 'control' => control, 'press' => answers[key]['press'], 'error' => answers[key]['error'] }.compact
          got[n] = answers[key]['press'] unless answers[key]['press'].nil?
        end
        final = GoalPlanner.apply_press(plan, got)
      end
      ok, fault = final ? check(i['key'], final, labels.fetch(i['key'])) : [false, "no plan: #{reply['error']}"]
      rows << { 'base' => base['name'], 'press' => config && config.join('/'), 'task' => i['key'], 'arm' => i['arm'], 'ok' => ok, 'fault' => fault,
                'plan' => plan, 'final' => final, 'questions' => asked, 'planTokens' => reply['prompt_eval_count'].to_i + reply['eval_count'].to_i,
                'questionCalls' => calls, 'questionTokens' => tokens }
    end
  end
  CONFIGS.each do |config|
    vr = rows.select { |r| r['base'] == base['name'] && r['press'] == (config && config.join('/')) }
    puts format('%-26s %-18s %2d/12  image %d/6  compact %d/6  question calls %d', base['name'], config ? config.join('/') : 'no question',
                vr.count { |r| r['ok'] }, vr.count { |r| r['ok'] && r['arm'] == 'image960' }, vr.count { |r| r['ok'] && r['arm'] == 'compact' },
                vr.sum { |r| r['questionCalls'] })
  end
  STDOUT.flush
end
summary = rows.group_by { |r| [r['base'], r['press']] }.map do |(base, press), rs|
  { 'base' => base, 'press' => press, 'ok' => rs.count { |r| r['ok'] }, 'of' => rs.size, 'questionCalls' => rs.sum { |r| r['questionCalls'] },
    'faults' => rs.reject { |r| r['ok'] }.map { |r| "#{r['task']}/#{r['arm']}: #{r['fault']}" } }
end
File.write(ARGV.fetch(0), JSON.pretty_generate('schema' => 'qa666-fm-press-screen-v1', 'provisional' => true, 'model' => FoundationBridge::MODEL,
                                                'sampling' => 'greedy', 'questions' => GoalPlanner::PRESS_QUESTIONS, 'bases' => BASES,
                                                'reference' => REFERENCE, 'summary' => summary, 'rows' => rows))

# ADR-0035 phase A token report. For each prompt family, render P0 and every single-slot variant on the saved
# inputs of the P0 runs (task, done steps, snapshot), then count tokens:
# - Apple Foundation Model: exact, from SystemLanguageModel.tokenCount(for:) (fm_token_count.swift; no generation).
# - gemma4:12b: an estimate fitted on saved Ollama prompt_eval_count values of text requests (no model call).
#   Other Ollama models have too few saved requests for a fit; they need a measured count when no fit uses the GPU.
# Usage: RUBYOPT=-Eutf-8 ruby scripts/qa666/prompt_token_report.rb [out.json]
require 'open3'
require_relative 'prompt_slots'

ROOT = File.expand_path('../..', __dir__)
RUNS = File.join(ROOT, 'reports/work/QA666/runs')
OUT = ARGV[0] || File.join(ROOT, 'reports/work/QA666/prompt-slots/token-report.json')
WORK = File.join(ROOT, '.build/debug-output/prompt-slots')
P0_RUNS = { 'turns-26-planner-fixed' => 'fixture-planner', 'turns-27a-planner-finish' => 'fixture-planner',
            'turns-27b-planner-finish' => 'fixture-planner', 'settings-01' => 'settings-planner' }.freeze
FM_ANSWER_RESERVE = 1024 # tokens kept free for the answer; the largest saved plan answer is reported next to it
EXPECT = JSON.parse(File.read(File.join(__dir__, 'task_expectations.json')))['tasks']

def parse(family, prompt)
  fam = PromptSlots.family(family)
  task = prompt[/Task: (.*?)#{Regexp.escape(fam['frame']['p0'])}/m, 1]
  rest = prompt.split(' Steps already done: ', 2).last
  label = fam['snapshot-label']
  done_text, snap = rest.include?(label) ? rest.split(label, 2) : [rest, nil]
  done_text = done_text.chomp('.')
  [task, done_text == 'none' ? [] : JSON.parse(done_text), snap && JSON.parse(snap)]
end

def least_squares(xs, ys)
  n = xs.size.to_f; mx = xs.sum / n; my = ys.sum / n
  slope = xs.zip(ys).sum { |x, y| (x - mx) * (y - my) } / xs.sum { |x| (x - mx)**2 }
  [slope, my - slope * mx]
end

# 1. Saved inputs of the P0 runs, and the largest saved plan answer.
inputs = []
max_answer = 0
P0_RUNS.each do |run, family|
  Dir.glob(File.join(RUNS, run, '**', 'request.json')).sort.each do |p|
    req = JSON.parse(File.read(p)); resp = JSON.parse(File.read(p.sub('request.json', 'response.json'))) rescue {}
    max_answer = [max_answer, resp['outputTokens'].to_i].max
    task, done, snap = parse(family, req['prompt'])
    key = EXPECT.find { |_, e| e['task'] == task }&.first
    inputs << { 'family' => family, 'image' => !req['image'].nil?, 'task' => task, 'taskKey' => key, 'done' => done, 'snap' => snap,
                'source' => p.sub(RUNS + '/', '') }
  end
end

# 2. Render variants.
rendered = []
PromptSlots::FAMILIES.each do |family, fam|
  fam['descriptor'].each do |d|
    pool = inputs.select { |i| i['family'] == family && i['image'] == (d == 'image') }
    PromptSlots.single_slot_variants(family, d).each do |v|
      pool.each do |i|
        forbidden = EXPECT.fetch(i['taskKey'], {}).fetch('forbidden', [])
        b = PromptSlots.build(family, v, task: i['task'], done_steps: i['done'], projection: i['snap'], forbidden: forbidden)
        rendered << { 'family' => family, 'descriptor' => d, 'variant' => b[:record]['variant'], 'promptID' => b[:record]['promptID'],
                      'source' => i['source'], 'text' => b[:text], 'sha' => b[:record]['promptSHA256'] }
      end
    end
  end
end

# 3. Saved gemma4:12b text requests: calibration data.
calib = Dir.glob(File.join(RUNS, '*', '**', 'request.json')).sort.map do |p|
  req = JSON.parse(File.read(p)); resp = JSON.parse(File.read(p.sub('request.json', 'response.json'))) rescue nil
  next unless resp && resp['promptTokens'] && req['model'] == 'gemma4:12b'
  { 'run' => p.sub(RUNS + '/', '').split('/').first, 'image' => !req['image'].nil?, 'text' => req['prompt'], 'tokens' => resp['promptTokens'],
    'sha' => Digest::SHA256.hexdigest(req['prompt']) }
end.compact

# 4. Exact Foundation Model counts for every unique text (variants and calibration prompts).
Dir.mkdir(WORK) unless Dir.exist?(WORK)
uniq = (rendered.map { |r| [r['sha'], r['text']] } + calib.map { |c| [c['sha'], c['text']] }).uniq(&:first)
File.write(File.join(WORK, 'prompts.json'), JSON.generate(uniq.map { |sha, text| { 'id' => sha, 'text' => text } }))
_, err, status = Open3.capture3('swift', File.join(__dir__, 'fm_token_count.swift'), File.join(WORK, 'prompts.json'), File.join(WORK, 'fm-counts.json'))
raise "fm_token_count failed: #{err[-2000..]}" unless status.success?
fm = JSON.parse(File.read(File.join(WORK, 'fm-counts.json')))
fmc = fm['counts']

# 5. gemma4:12b estimate. Compare 2 predictors with leave-one-run-out error on text requests.
text_cal = calib.reject { |c| c['image'] }
predictors = { 'chars' => ->(t, sha) { t.size.to_f }, 'fmTokens' => ->(t, sha) { fmc.fetch(sha).to_f } }
fits = predictors.map do |name, f|
  errors = text_cal.map { |c| c['run'] }.uniq.flat_map do |run|
    train = text_cal.reject { |c| c['run'] == run }; test = text_cal.select { |c| c['run'] == run }
    a, b = least_squares(train.map { |c| f.call(c['text'], c['sha']) }, train.map { |c| c['tokens'].to_f })
    test.map { |c| ((a * f.call(c['text'], c['sha']) + b) - c['tokens']).abs / c['tokens'] }
  end
  a, b = least_squares(text_cal.map { |c| f.call(c['text'], c['sha']) }, text_cal.map { |c| c['tokens'].to_f })
  [name, { 'slope' => a.round(5), 'intercept' => b.round(2), 'leaveOneRunOutMaxRelError' => errors.max.round(4),
           'leaveOneRunOutMeanRelError' => (errors.sum / errors.size).round(4), 'requests' => text_cal.size }]
end.to_h
best = fits.min_by { |_, f| f['leaveOneRunOutMaxRelError'] }.first
gem = ->(text, sha) { (fits[best]['slope'] * predictors[best].call(text, sha) + fits[best]['intercept']).round }
image_extra = calib.select { |c| c['image'] }.map { |c| c['tokens'] - gem.call(c['text'], c['sha']) }.sort
image_extra_median = image_extra.empty? ? nil : image_extra[image_extra.size / 2]

# 6. Summaries per prompt variant.
fm_limit = fm['contextSize']
summary = rendered.group_by { |r| r['promptID'] }.map do |id, rs|
  r0 = rs.first
  schema = r0['variant']['schema'] == 'qa-plan' ? 'qa-plan-schema-v1' : 'plan-schema-v1'
  fm_tokens = rs.map { |r| fmc.fetch(r['sha']) }
  gm = rs.map { |r| gem.call(r['text'], r['sha']) + (r0['descriptor'] == 'image' ? image_extra_median.to_i : 0) }
  fm_need = fm_tokens.max + fm['schemaTokens'].fetch(schema) + FM_ANSWER_RESERVE
  { 'family' => r0['family'], 'descriptor' => r0['descriptor'], 'variant' => r0['variant'], 'promptID' => id, 'inputs' => rs.size,
    'chars' => { 'min' => rs.map { |r| r['text'].size }.min, 'max' => rs.map { |r| r['text'].size }.max },
    'foundationModel' => { 'promptTokensMax' => fm_tokens.max, 'promptTokensMin' => fm_tokens.min, 'schemaTokens' => fm['schemaTokens'].fetch(schema),
                           'neededWithAnswerReserve' => fm_need, 'fits' => fm_need <= fm_limit,
                           'note' => r0['descriptor'] == 'image' ? 'text part only; Foundation Model vision input not checked' : nil }.compact,
    'gemma4_12bEstimate' => { 'promptTokensMax' => gm.max, 'promptTokensMin' => gm.min } }
end.sort_by { |s| [s['family'], s['descriptor'], s['foundationModel']['promptTokensMax']] }

report = {
  'schema' => 'qa666-prompt-token-report-v1', 'provisional' => true,
  'foundationModel' => fm.reject { |k, _| k == 'counts' }.merge('answerReserve' => FM_ANSWER_RESERVE, 'largestSavedPlanAnswerTokens' => max_answer),
  'gemmaFit' => fits.merge('chosen' => best, 'imageTokensMedian' => image_extra_median, 'imageRequests' => image_extra.size),
  'inputs' => inputs.map { |i| i.slice('family', 'image', 'taskKey', 'source') },
  'variants' => summary
}
Dir.mkdir(File.dirname(OUT)) unless Dir.exist?(File.dirname(OUT))
File.write(OUT, JSON.pretty_generate(report))
puts JSON.pretty_generate(report.slice('foundationModel', 'gemmaFit'))
summary.each do |s|
  v = s['variant'].reject { |k, val| k == 'descriptor' || PromptSlots::P0[k] == val || (k == 'rules' && val == PromptSlots.family(s['family'])['p0-rules']) }
  puts format('%-16s %-17s %-50s FM max %5d need %5d fits %-5s gemma max %5d', s['family'], s['descriptor'], v.empty? ? 'P0' : JSON.generate(v),
              s['foundationModel']['promptTokensMax'], s['foundationModel']['neededWithAnswerReserve'], s['foundationModel']['fits'], s['gemma4_12bEstimate']['promptTokensMax'])
end

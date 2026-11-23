# ADR-0035 phase B replay: run the expectation oracle on every saved QA666 trajectory and compare it with
# TTR's native verdict (Fixture: MatchedFixtureBenchmark; Settings: settings_planner graders). Offline; no TTR.
# Usage: ruby scripts/qa666/oracle_replay.rb [out.json]
require 'digest'
require_relative 'expectation_oracle'

ROOT = File.expand_path('../..', __dir__)
RUNS = File.join(ROOT, 'reports/work/QA666/runs')
EXPECT_PATH = File.join(__dir__, 'task_expectations.json')
out_path = ARGV[0] || File.join(ROOT, 'reports/work/QA666/oracle-replay/replay.json')

expectations = JSON.parse(File.read(EXPECT_PATH))['tasks']
rows = []
Dir.glob(File.join(RUNS, '*', '*', 'trajectory.json')).sort.each do |path|
  t = JSON.parse(File.read(path))
  e = expectations[t['task']]
  rel = path.sub(RUNS + '/', '')
  unless e
    rows << { 'trajectory' => rel, 'task' => t['task'], 'skipped' => 'no expectation record' }; next
  end
  r = ExpectationOracle.evaluate(e, t)
  native = (t['verdict'] || {})['success']
  state_ok = r['differences'].empty?
  rows << { 'trajectory' => rel, 'run' => rel.split('/').first, 'task' => t['task'], 'arm' => t['arm'], 'family' => e['family'],
            'nativeSuccess' => native, 'nativeFailedChecks' => ((t['verdict'] || {})['checks'] || {}).reject { |_, v| v }.keys,
            'oracleStateMet' => state_ok, 'oracleStateAndClaimMet' => state_ok && r['agent'].empty?,
            'decision' => t['decision'], 'differences' => r['differences'], 'agent' => r['agent'], 'info' => r['info'] }
end

scored = rows.reject { |r| r['skipped'] || r['nativeSuccess'].nil? }
matrix = lambda do |key|
  m = Hash.new(0)
  scored.each { |r| m["native #{r['nativeSuccess'] ? 'pass' : 'fail'} / oracle #{r[key] ? 'met' : 'difference'}"] += 1 }
  m.sort.to_h
end
by_family = scored.group_by { |r| r['family'] }.map do |f, rs|
  [f, { 'episodes' => rs.size,
        'agreeState' => rs.count { |r| r['nativeSuccess'] == r['oracleStateMet'] },
        'agreeStateAndClaim' => rs.count { |r| r['nativeSuccess'] == r['oracleStateAndClaimMet'] } }]
end.to_h
categories = Hash.new(0)
scored.each { |r| (r['differences'] + r['agent']).each { |d| categories[d['category']] += 1 } }
report = {
  'schema' => 'qa666-oracle-replay-v1', 'provisional' => true,
  'note' => 'Expectations are the task-level ground truth, not model expectations. Differences in these runs are agent faults ' \
            '(wrong plan, early stop), not app bugs: the Fixture and Settings had no seeded bug.',
  'expectations' => { 'path' => EXPECT_PATH.sub(ROOT + '/', ''), 'sha256' => Digest::SHA256.file(EXPECT_PATH).hexdigest },
  'oracle' => { 'path' => 'scripts/qa666/expectation_oracle.rb', 'sha256' => Digest::SHA256.file(File.join(__dir__, 'expectation_oracle.rb')).hexdigest },
  'episodes' => scored.size, 'skipped' => rows.count { |r| r['skipped'] || r['nativeSuccess'].nil? },
  'stateOnly' => matrix.call('oracleStateMet'), 'stateAndClaim' => matrix.call('oracleStateAndClaimMet'),
  'byFamily' => by_family, 'categories' => categories.sort.to_h,
  'disagreements' => scored.select { |r| r['nativeSuccess'] != r['oracleStateAndClaimMet'] }
                           .map { |r| r.slice('trajectory', 'nativeSuccess', 'nativeFailedChecks', 'oracleStateMet', 'decision', 'differences', 'agent') },
  'rows' => rows
}
Dir.mkdir(File.dirname(out_path)) unless Dir.exist?(File.dirname(out_path))
File.write(out_path, JSON.pretty_generate(report))
puts JSON.pretty_generate(report.slice('episodes', 'skipped', 'stateOnly', 'stateAndClaim', 'byFamily', 'categories'))
puts "disagreements: #{report['disagreements'].size}"
report['disagreements'].each { |d| puts "  #{d['trajectory']} native=#{d['nativeSuccess']} failed=#{d['nativeFailedChecks'].join(',')} oracle=#{(d['differences'] + d['agent']).map { |x| x['category'] }.join(',')} decision=#{d['decision']}" }

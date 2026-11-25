# ADR-0035 phase C: score a reference-validation run (or any planner run) of benchmark666.json with the oracle.
# For each episode: the oracle state check and the claim check. For each screen: authored controls against the union
# of the registered controls in all observations of that screen's episodes.
# Usage: RUBYOPT=-Eutf-8 ruby scripts/qa666/bench666_validate.rb RUN_DIRECTORY... > report.json
# With several runs, the last scored episode of each task counts; an episode that sent no request (TTR app absent) is skipped.
require 'json'
require 'set'
require_relative 'bench666'
require_relative 'expectation_oracle'

runs = ARGV.empty? ? abort('Usage: bench666_validate.rb RUN_DIRECTORY...') : ARGV
bench = Bench666.load
campaigns = runs.map { |run| [File.basename(run), JSON.parse(File.read(File.join(run, 'campaign.json')))['benchmarkSHA256']] }.to_h
rows = []
live = Hash.new { |h, k| h[k] = {} }
complete = Hash.new(true)
runs.flat_map { |run| Dir.glob(File.join(run, '*', 'trajectory.json')).sort }.each do |path|
  traj = JSON.parse(File.read(path))
  task = bench['tasks'].find { |t| t['id'] == traj['task'] } or next
  next if traj['issue'].to_s.include?('endpointConnectionRefused')
  rows.reject! { |r| r['task'] == task['id'] }
  raws = (traj['observations'] || []) + (traj['inputs'] || []).flat_map { |i| [i['before'], i['after']] }
  raws.compact.each do |raw|
    ob = raw['observation'] || raw
    next unless ob.is_a?(Hash) && ob['controls']
    complete[task['screen']] &&= ob.dig('coverage', 'registeredControlsComplete') == true
    ob['controls'].each { |c| live[task['screen']][c.dig('identity', 'id')] = c['publicLabel'] }
  end
  result = ExpectationOracle.evaluate(task['expect'], traj)
  rows << { 'run' => File.basename(File.dirname(File.dirname(path))), 'task' => task['id'], 'screen' => task['screen'], 'split' => task['split'], 'arm' => traj['arm'], 'decision' => traj['decision'],
            'issue' => traj['issue'], 'stateMet' => result['differences'].empty?, 'claimMet' => result['agent'].empty?,
            'differences' => result['differences'], 'agent' => result['agent'], 'deliveredInputs' => result.dig('info', 'deliveredInputs') }
end
inventory = live.keys.sort.map do |screen|
  authored = bench['screens'].fetch(screen)
  raw = { 'observation' => { 'coverage' => { 'registeredControlsComplete' => complete[screen] },
                             'controls' => live[screen].map { |id, label| { 'identity' => { 'id' => id }, 'publicLabel' => label } } } }
  [screen, Bench666.inventory_errors(screen, authored, raw)]
end.to_h
fixture = bench['tasks'].reject { |t| bench['screens'][t['screen']]['runner'] }.map { |t| t['id'] }
missing = fixture - rows.map { |r| r['task'] }
puts JSON.pretty_generate('schema' => 'qa-bench-validation-v1', 'provisional' => true, 'runs' => campaigns, 'currentSHA256' => Bench666.sha256,
                          'episodes' => rows.size, 'met' => rows.count { |r| r['stateMet'] && r['claimMet'] }, 'missingTasks' => missing,
                          'inventoryErrors' => inventory.values.flatten, 'rows' => rows)

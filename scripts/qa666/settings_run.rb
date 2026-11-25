#!/usr/bin/env ruby
# QA666 Settings planner campaign.
# Usage: settings_run.rb SIGNED_AATV SIMULATOR_ID TTR_PROJECT NEW_RUN_DIRECTORY BUDGET_JSON
#        settings_run.rb --rescore RUN_DIRECTORY   (fresh-process regrade of saved trajectories)
require 'json'
require 'digest'
require 'time'
require 'fileutils'
require_relative 'local_ollama_session'
require_relative 'qa666_provider'
require_relative 'settings_planner'

def save(path, value)
  File.open(path, File::WRONLY | File::CREAT | File::EXCL, 0o600) { |f| f.write(JSON.pretty_generate(value)) }
end

def rescore(run)
  rows = JSON.parse(File.read(File.join(run, 'map.json'))).fetch('rows')
  Dir[File.join(run, '*', 'trajectory.json')].sort.map do |path|
    t = JSON.parse(File.read(path))
    again = SettingsQA.grade(t['task'], rows: rows, observations: t['observations'], inputs: t['inputs'], decision: t['decision'])
    responses = Dir[File.join(File.dirname(path), 'call-*/response.json')].map { |f| JSON.parse(File.read(f)) }
    { 'slot' => File.basename(File.dirname(path)), 'success' => again['success'], 'verdictReproduced' => again == t['verdict'],
      'buttons' => t['inputs'].select { |i| i['state'] == 'delivered' }.map { |i| i['button'] }, 'decision' => t['decision'],
      'calls' => responses.size, 'tokens' => responses.sum { |r| r['promptTokens'].to_i + r['outputTokens'].to_i },
      'latencySeconds' => responses.sum { |r| r['latencySeconds'].to_f }.round(2), 'issue' => t['issue'], 'checks' => again['checks'] }
  end
end

if ARGV.first == '--rescore'
  puts JSON.pretty_generate(rescore(ARGV.fetch(1)))
  exit
end

abort 'Usage: settings_run.rb SIGNED_AATV SIMULATOR_ID TTR_PROJECT NEW_RUN_DIRECTORY BUDGET_JSON' unless ARGV.size == 5
cli, sim, project, out, budget_path = ARGV
budget = JSON.parse(File.read(budget_path))
tasks, arms = budget.fetch('tasks'), budget.fetch('arms')
raise 'unknown task' unless (tasks - SettingsQA::TASKS.keys).empty?
raise 'unknown arm' unless (arms - %w[image960 text]).empty?
deadline = Time.iso8601(budget.fetch('deadline'))
Dir.mkdir(out)
probe = SettingsTTR.new(cli: cli, project: project, sim: sim, session: nil)
app = probe.command('status')
raise 'app busy' if app['commandActive'] || app['observationActive'] || app['queuedCommandCount'] != 0
ready = probe.command('simulator', 'readiness', '--simulator-udid', sim)
raise 'ownership' unless ready['can_run'] && ready.fetch('ownership').all? { |o| o['state'] == 'clear' }
session = probe.command('simulator', 'remote', 'connect', '--simulator-udid', sim).fetch('operationID')
ttr = SettingsTTR.new(cli: cli, project: project, sim: sim, session: session)
provider = LocalOllamaSession.new(model: budget.fetch('model'), deadline: deadline, max_calls: budget.fetch('maxCalls'),
                                  max_tokens: budget.fetch('maxTokens'), schema: 'plan', think: budget['think'],
                                  max_output: budget.fetch('maxOutputTokens', 1_500), read_timeout: budget.fetch('readTimeoutSeconds', 300),
                                  http: QA666Provider.http(budget, planner: true, checks: false))
save(File.join(out, 'campaign.json'), { 'schema' => 1, 'executor' => 'Maximum-mini-NUIAK QA666', 'mode' => 'settings-planner', 'provider' => budget.fetch('provider', 'ollama'),
                                        'budget' => budget, 'session' => session, 'approved' => SettingsQA::APPROVED,
                                        'cliDigest' => Digest::SHA256.file(cli).hexdigest, 'ttrRevision' => `git -C #{project} rev-parse HEAD`.strip })
begin
  60.times { break if ttr.remote('status')['state'] == 'ready'; sleep 1 }
  raise 'remote not ready' unless ttr.remote('status')['state'] == 'ready'
  rows = ttr.map_rows
  save(File.join(out, 'map.json'), { 'rows' => rows, 'at' => Time.now.utc.iso8601 })
  tasks.each do |task|
    arms.each do |arm|
      raise 'campaign deadline' if Time.now >= deadline
      dir = File.join(out, "#{task}-#{arm}"); Dir.mkdir(dir)
      ep = SettingsEpisode.new(io: ttr, provider: provider, rows: rows, task: task, arm: arm, dir: dir)
      begin
        ep.run
      ensure
        verdict = SettingsQA.grade(task, rows: rows, observations: ep.observations, inputs: ep.inputs, decision: ep.decision)
        save(File.join(dir, 'trajectory.json'), { 'task' => task, 'arm' => arm, 'observations' => ep.observations, 'inputs' => ep.inputs,
                                                  'decision' => ep.decision, 'issue' => ep.issue, 'plans' => ep.plans, 'verdict' => verdict })
        puts JSON.generate(task: task, arm: arm, success: verdict['success'], issue: ep.issue); STDOUT.flush
      end
    end
  end
ensure
  save(File.join(out, 'provider-ledger.json'), { 'calls' => provider.calls, 'tokens' => provider.tokens, 'usageUnknown' => provider.unknown,
                                                 'entries' => provider.ledger })
  ttr.remote('disconnect') rescue warn('disconnect failed')
end

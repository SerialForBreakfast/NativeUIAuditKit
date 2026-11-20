#!/usr/bin/env ruby
# QA666 fresh-process reopen (MM-QA-05): recompute each slot's native verdict from its saved trajectory with TTR's
# evaluator, recompute token totals from the saved provider responses, and compare both with the live records.
# Usage: QA666_TTR_ROOT=/path/to/worktree ruby reopen_score.rb RUN_DIRECTORY [RUN_DIRECTORY ...]
require 'json'
ttr = ENV.fetch('QA666_TTR_ROOT')
unless Array.method_defined?(:filter_map)
  module Enumerable; def filter_map; each_with_object([]) { |x, o| v = yield(x); o << v if v }; end; end
end
unless Enumerable.method_defined?(:tally)
  module Enumerable; def tally; each_with_object(Hash.new(0)) { |x, h| h[x] += 1 }; end; end
end
require File.join(ttr, 'Scripts/lib/matched-fixture-benchmark')

rows = ARGV.flat_map do |run|
  campaign = JSON.parse(File.read(File.join(run, 'campaign.json')))
  ledger = JSON.parse(File.read(File.join(run, 'provider-ledger.json')))
  Dir[File.join(run, '*')].select { |p| File.directory?(p) && File.exist?(File.join(p, 'trajectory.json')) }.sort.map do |slot|
    t = JSON.parse(File.read(File.join(slot, 'trajectory.json')))
    again = MatchedFixtureBenchmark.evaluate(t['task'], observations: t['observations'], inputs: t['inputs'], decision: t['decision'])
    responses = Dir[File.join(slot, 'call-*/response.json')].map { |f| JSON.parse(File.read(f)) }
    tokens = responses.sum { |r| r['promptTokens'].to_i + r['outputTokens'].to_i }
    {
      'run' => File.basename(run), 'slot' => File.basename(slot), 'model' => campaign['model'],
      'outputFormat' => responses.map { |r| r['outputFormat'] }.first, 'success' => again['success'],
      'verdictReproduced' => again == t['verdict'], 'modelInputs' => t['inputs'].size,
      'calls' => responses.size, 'tokens' => tokens, 'latencySeconds' => responses.sum { |r| r['latencySeconds'].to_f }.round(2),
      'issue' => t['issue'], 'plan' => responses.map { |r| r['reply'].to_s.gsub(/\s+/, '') }.first,
      'ledgerTokens' => ledger['tokens'], 'ledgerPresses' => ledger['presses']
    }
  end
end
puts JSON.pretty_generate(rows)

require 'digest'
require 'json'
require_relative 'fm_bridge'

# QA666: select the transport for LocalOllamaSession from the budget.
# "provider": "ollama" (default) -> nil (LocalOllamaSession posts to Ollama).
# "provider": "foundation" -> the on-device Apple Foundation Model bridge. Model name must be FoundationBridge::MODEL.
# Budget field "foundationSchema": plan (default) or plan-described.
# The Foundation bridge supports only the planner schema, so it refuses turn mode and completion checks.
module QA666Provider
  def self.http(budget, planner:, checks:)
    case budget.fetch('provider', 'ollama')
    when 'ollama' then nil
    when 'foundation'
      raise "foundation provider needs model #{FoundationBridge::MODEL}" unless budget.fetch('model') == FoundationBridge::MODEL
      raise 'foundation provider supports only the planner arm' unless planner && !checks
      FoundationBridge.new(schema: budget.fetch('foundationSchema', 'plan'))
    else raise "unknown provider #{budget['provider']}"
    end
  end
end

# ADR-0035 phase C reference validation: a planner with no model. It returns the benchmark's reference plans in order.
# Same interface as LocalOllamaSession (ask, unknown, calls, tokens, model, ledger). It sends no request and counts 0 tokens.
class ReferencePlanner
  MODEL = 'reference-plan'
  attr_reader :unknown, :calls, :tokens, :model, :ledger

  def initialize(bench)
    @plans_by_task = bench.fetch('tasks').map { |t| [t['id'], t['reference']] }.to_h
    @model = MODEL; @unknown = false; @calls = 0; @tokens = 0; @ledger = []; @plans = nil
  end

  def begin_task(task)
    plans = @plans_by_task.fetch(task)
    raise "#{task} has no reference plans" unless plans.is_a?(Array) && !plans.empty?
    @task = task; @plans = JSON.parse(JSON.generate(plans))
  end

  def ask(directory, prompt, _image = nil)
    raise 'reference plans exhausted' if @plans.nil? || @plans.empty?
    plan = @plans.shift
    @calls += 1
    record = { 'call' => @calls, 'model' => MODEL, 'task' => @task, 'promptSHA256' => Digest::SHA256.hexdigest(prompt), 'plan' => plan }
    File.write(File.join(directory, 'request.json'), JSON.generate(record.merge('prompt' => prompt)))
    @ledger << record
    plan
  end
end

require 'json'
require 'base64'
require 'digest'
require 'net/http'
require 'uri'
require 'time'

# QA666: local Ollama provider with the same interface as TTR's AGYNavigationSession
# (`ask(directory, prompt, image=nil)` -> parsed JSON reply, `unknown`, MODEL).
# 1 call = 1 fresh single-turn chat. No tools, no history, temperature 0.
# Usage comes from Ollama's own counters (prompt_eval_count + eval_count). Missing usage stops the campaign.
# A reply that is not 1 JSON object is a refusal for that call; this class never retries.
class LocalOllamaSession
  ENDPOINT = ENV.fetch('QA666_OLLAMA', 'http://127.0.0.1:11434')
  RESERVE_TOKENS = 4_000 # Next call must fit under the token ceiling with this reserve.
  MAX_OUTPUT_TOKENS = 1_500 # Bounds 1 reply. gemma4:12b spends hidden reasoning tokens (about 800) before short JSON; 400 cut them off.
  # MM-QA-02 strict dispatcher: Ollama constrains decoding to this schema. Only primitive directions and the 2 terminals.
  STEP_SCHEMA = { type: 'object', required: ['steps'], additionalProperties: false,
                  properties: { steps: { type: 'array', minItems: 1, maxItems: 17,
                                         items: { type: 'string', enum: %w[up down left right done abstain] } } } }.freeze
  # step-schema-v2: the model fills `moves` and `terminal`; the host builds TTR's `steps` = moves + [terminal].
  MOVES_SCHEMA = { type: 'object', required: %w[moves terminal], additionalProperties: false,
                   properties: { moves: { type: 'array', maxItems: 16, items: { type: 'string', enum: %w[up down left right] } },
                                 terminal: { type: 'string', enum: %w[done abstain] } } }.freeze
  # step-schema-v3: like v2, and `select` / `back` are allowed for activation and return tasks.
  TASK_SCHEMA = { type: 'object', required: %w[moves terminal], additionalProperties: false,
                  properties: { moves: { type: 'array', maxItems: 16, items: { type: 'string', enum: %w[up down left right select back] } },
                                terminal: { type: 'string', enum: %w[done abstain] } } }.freeze
  # turn-schema-v1 (multi-turn arm): exactly 1 action per call. The host sends a fresh observation before each call.
  TURN_SCHEMA = { type: 'object', required: %w[action], additionalProperties: false,
                  properties: { action: { type: 'string', enum: %w[up down left right select back done abstain] } } }.freeze
  # check-schema-v1 (completion check): 1 yes/no answer about the current screen. No action.
  CHECK_SCHEMA = { type: 'object', required: %w[complete], additionalProperties: false,
                   properties: { complete: { type: 'boolean' } } }.freeze
  # confirm-schema-v1: the reversed question after a yes. Agreement means remaining == false.
  CONFIRM_SCHEMA = { type: 'object', required: %w[remaining], additionalProperties: false,
                     properties: { remaining: { type: 'boolean' } } }.freeze
  # plan-schema-v1 (planner arm): the model writes goal steps; the host routes and checks each step.
  PLAN_SCHEMA = { type: 'object', required: %w[steps after], additionalProperties: false,
                  properties: { steps: { type: 'array', maxItems: 6,
                                         items: { type: 'object', required: %w[op target times], additionalProperties: false,
                                                  properties: { op: { type: 'string', enum: %w[focus activate back] },
                                                                target: { type: %w[string null] },
                                                                times: { type: 'integer', minimum: 1, maximum: 3 } } } },
                                after: { type: 'string', enum: %w[done replan abstain] } } }.freeze
  attr_reader :unknown, :calls, :tokens, :model, :ledger

  def initialize(model:, deadline:, max_calls:, max_tokens:, num_ctx: 16_384, http: nil, schema: false, think: nil,
                 max_output: MAX_OUTPUT_TOKENS, read_timeout: 300)
    @model, @deadline, @max_calls, @max_tokens, @num_ctx, @schema, @think = model, deadline, max_calls, max_tokens, num_ctx, schema, think
    raise 'invalid output limit' unless max_output.is_a?(Integer) && max_output.between?(100, 8_000)
    raise 'invalid read timeout' unless read_timeout.is_a?(Integer) && read_timeout.between?(30, 900)
    @max_output, @read_timeout = max_output, read_timeout
    @calls = 0; @tokens = 0; @unknown = false; @ledger = []
    @http = http || method(:post_json)
  end

  # TTR passes the JPEG path for the image arm and nil for the compact arm.
  def ask(directory, prompt, image = nil)
    check_ceiling
    message = { role: 'user', content: prompt }
    message[:images] = [Base64.strict_encode64(File.binread(image))] if image
    format = { 'v1' => STEP_SCHEMA, 'v2' => MOVES_SCHEMA, 'v3' => TASK_SCHEMA, 'turn' => TURN_SCHEMA, 'check' => CHECK_SCHEMA, 'confirm' => CONFIRM_SCHEMA, 'plan' => PLAN_SCHEMA }.fetch(@schema.to_s, 'json')
    request = { model: @model, stream: false, format: format, keep_alive: '10m',
                options: { temperature: 0, seed: 666, num_ctx: @num_ctx, num_predict: @max_output }, messages: [message] }
    request[:think] = @think unless @think.nil? # Reasoning models (qwen3.5): false disables the thinking pass.
    record = { 'call' => @calls + 1, 'model' => @model, 'outputFormat' => @schema ? "step-schema-#{@schema}" : 'json', 'think' => @think, 'maxOutputTokens' => @max_output, 'promptSHA256' => Digest::SHA256.hexdigest(prompt),
               'image' => image && File.basename(image), 'imageSHA256' => image && Digest::SHA256.file(image).hexdigest,
               'requestBytes' => JSON.generate(request).bytesize, 'startedAt' => Time.now.utc.iso8601(3) }
    File.write(File.join(directory, 'request.json'), JSON.generate(record.merge('prompt' => prompt)))
    @calls += 1; @unknown = true
    started = Process.clock_gettime(Process::CLOCK_MONOTONIC)
    reply = @http.call(request, [@deadline - Time.now, @read_timeout].min)
    seconds = Process.clock_gettime(Process::CLOCK_MONOTONIC) - started
    prompt_tokens, output_tokens = reply['prompt_eval_count'], reply['eval_count']
    raise 'usage unavailable' unless prompt_tokens.is_a?(Integer) && output_tokens.is_a?(Integer) && prompt_tokens.positive?
    @tokens += prompt_tokens + output_tokens; @unknown = false
    text = reply.dig('message', 'content').to_s
    record.merge!('promptTokens' => prompt_tokens, 'outputTokens' => output_tokens, 'latencySeconds' => seconds.round(3),
                  'loadSeconds' => (reply['load_duration'].to_i / 1e9).round(3), 'replyBytes' => text.bytesize, 'reply' => text)
    File.write(File.join(directory, 'response.json'), JSON.generate(record))
    @ledger << record.reject { |k, _| %w[reply].include?(k) }
    raise 'provider ceiling exceeded' if @tokens > @max_tokens
    parsed = JSON.parse(text.strip.sub(/\A```(?:json)?\s*/, '').sub(/\s*```\z/, ''))
    raise 'reply is not a JSON object' unless parsed.is_a?(Hash)
    if %w[v2 v3].include?(@schema.to_s)
      raise "reply does not match step-schema-#{@schema}" unless parsed['moves'].is_a?(Array) && %w[done abstain].include?(parsed['terminal'])
      parsed = { 'steps' => parsed['moves'] + [parsed['terminal']] }
    elsif @schema.to_s == 'turn'
      raise 'reply does not match turn-schema' unless parsed.keys == ['action'] && TURN_SCHEMA[:properties][:action][:enum].include?(parsed['action'])
    elsif @schema.to_s == 'check'
      raise 'reply does not match check-schema' unless parsed.keys == ['complete'] && [true, false].include?(parsed['complete'])
    elsif @schema.to_s == 'plan'
      raise 'reply does not match plan-schema' unless parsed.keys.sort == %w[after steps] && %w[done replan abstain].include?(parsed['after']) &&
        parsed['steps'].is_a?(Array) && parsed['steps'].size <= 6 && parsed['steps'].all? { |st|
          st.is_a?(Hash) && st.keys.sort == %w[op target times] && %w[focus activate back].include?(st['op']) &&
            st['times'].is_a?(Integer) && st['times'].between?(1, 3) &&
            (st['op'] == 'back' ? st['target'].nil? : st['target'].is_a?(String) && st['target'].bytesize.between?(1, 200)) }
    elsif @schema.to_s == 'confirm'
      raise 'reply does not match confirm-schema' unless parsed.keys == ['remaining'] && [true, false].include?(parsed['remaining'])
    end
    parsed
  end

  private

  def check_ceiling
    raise 'campaign ceiling' if @unknown || @deadline - Time.now < 5 || @calls >= @max_calls || @tokens + RESERVE_TOKENS > @max_tokens
  end

  def post_json(request, timeout)
    uri = URI.join(ENDPOINT, '/api/chat')
    Net::HTTP.start(uri.host, uri.port, read_timeout: timeout, open_timeout: 5) do |h|
      response = h.post(uri.path, JSON.generate(request), 'Content-Type' => 'application/json')
      raise "ollama http #{response.code}" unless response.code == '200'
      JSON.parse(response.body)
    end
  end
end

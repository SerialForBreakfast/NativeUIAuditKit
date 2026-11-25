require 'json'
require 'open3'

# QA666: callable that sends 1 LocalOllamaSession request to the Apple Foundation Model bridge (fm_bridge.swift).
# Pass it as `http:` to LocalOllamaSession. The session keeps its caps, ledger, schema checks and no-retry rule.
# The bridge uses the on-device SystemLanguageModel only. It returns Ollama-shaped usage fields.
class FoundationBridge
  MODEL = 'apple-foundation-on-device'
  ROOT = File.expand_path('../..', __dir__)
  BINARY = File.join(ROOT, '.build/qa666-fm/fm_bridge')
  SOURCE = File.join(__dir__, 'fm_bridge.swift')
  attr_reader :info

  def self.build!
    return BINARY if File.exist?(BINARY) && File.mtime(BINARY) >= File.mtime(SOURCE)
    Dir.mkdir(File.dirname(BINARY)) unless Dir.exist?(File.dirname(BINARY))
    _, err, status = Open3.capture3('swiftc', '-O', SOURCE, '-o', BINARY)
    raise "fm_bridge build failed: #{err[-1500..] || err}" unless status.success?
    BINARY
  end

  # io: an object with #puts and #gets (tests pass a fake); default starts the compiled bridge.
  SCHEMAS = %w[plan plan-described plan-words].freeze

  # schema: plan (plan-schema-v1, no field descriptions) plan-described (same fields, with @Guide descriptions),
  # or plan-words (op values in words, mapped back by the bridge).
  def initialize(io: nil, schema: 'plan')
    raise "unknown bridge schema #{schema}" unless SCHEMAS.include?(schema)
    @schema = schema
    @io = io || begin
      stdin, stdout, @wait = Open3.popen2(self.class.build!)
      Duplex.new(stdin, stdout)
    end
    @info = JSON.parse(@io.gets || raise('fm_bridge gave no ready line'))
    raise "fm_bridge not ready: #{@info}" unless @info['ready']
  end

  def call(request, _timeout)
    message = request.fetch(:messages).first
    images = message[:images] || []
    raise 'fm_bridge takes at most 1 image' if images.size > 1
    required = request[:format].is_a?(Hash) ? request[:format][:required] : nil
    schema = { %w[steps after] => @schema, %w[press] => 'press' }[required]
    raise 'fm_bridge supports only plan-schema-v1 and press-schema-v1' unless schema
    @io.puts(JSON.generate('prompt' => message.fetch(:content), 'image' => images.first, 'schema' => schema,
                           'maxOutput' => request.dig(:options, :num_predict)))
    reply = JSON.parse(@io.gets || raise('fm_bridge closed'))
    # A generation error after the prompt count is a refusal with known usage; LocalOllamaSession rejects the empty reply.
    raise "foundation model error: #{reply['error']}" if reply['error'] && !reply['prompt_eval_count'].is_a?(Integer)
    reply
  end

  Duplex = Struct.new(:input, :output) do
    def puts(line)
      input.puts(line); input.flush
    end

    def gets
      output.gets
    end
  end
end

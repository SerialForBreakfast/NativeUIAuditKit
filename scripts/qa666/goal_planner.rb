# QA666 planner arm (Joe, 2026-11-20: "Build it and lets see!").
# The model writes goal steps once per screen (plan-schema-v1). The host executes them:
# - focus: a route on TTR's observed edge map, else a move toward the target's native geometry;
# - activate: focus, then Select; each activation must appear in TTR's native activation evidence;
# - back: 1 Back press.
# The model never chooses individual presses and never judges completion; each step has a host postcondition.
# Only native SDK observations are used. The evaluator (MatchedFixtureBenchmark.evaluate) is never consulted.
require_relative 'prompt_slots'

module GoalPlanner
  DIRS = %w[up down left right].freeze
  MAX_PLANS = 8 # Fix 4 (2026-11-20 rerun): was 4.

  def self.normalize(text)
    text.to_s.downcase.gsub(/[^a-z0-9]/, '')
  end

  # Resolve a model target (control id or public label) to 1 registered, enabled control.
  # Exact id, then exact label, then normalized label; prefer visible controls when several match.
  def self.resolve(controls, visible_ids, target)
    enabled = controls.select { |c| c['enabled'] == true && c['hidden'] == false }
    [->(c) { c.dig('identity', 'id') == target },
     ->(c) { c['publicLabel'] == target },
     ->(c) { (n = normalize(target)).size >= 3 && normalize(c['publicLabel']) == n },
     ->(c) { (n = normalize(target)).size >= 4 && normalize(c['publicLabel']).include?(n) }].each do |rule|
      hits = enabled.select(&rule)
      hits = hits.select { |c| visible_ids.include?(c.dig('identity', 'id')) } if hits.size > 1
      return hits.first if hits.size == 1
      raise "ambiguous target: #{target}" if hits.size > 1
    end
    nil
  end

  def self.center(bounds)
    [bounds['x'] + bounds['width'] / 2.0, bounds['y'] + bounds['height'] / 2.0]
  end

  # Directions toward the target, best first. Directions known to give no move from this control are skipped.
  def self.directions_toward(from_bounds, to_bounds, dead)
    (fx, fy), (tx, ty) = center(from_bounds), center(to_bounds)
    dx, dy = tx - fx, ty - fy
    horizontal = dx.negative? ? 'left' : 'right'
    vertical = dy.negative? ? 'up' : 'down'
    order = []
    order << (dx.abs >= dy.abs ? horizontal : vertical) if dx.abs > 1 || dy.abs > 1
    order << (dx.abs >= dy.abs ? vertical : horizontal) if [dx.abs, dy.abs].min > 1
    order.reject { |d| dead.include?(d) }
  end

  # Fix 3: when no route or geometric direction is left, explore. Returns the first button of the shortest
  # known path to the nearest control that still has an untried direction (here first), or nil.
  def self.explore(edges, dead, here)
    tried = ->(id) { edges.fetch(id, {}).keys + dead[id] }
    queue = [[here, nil]]; seen = { here => true }
    until queue.empty?
      id, first = queue.shift
      untried = DIRS - tried.call(id)
      return first || untried.first unless untried.empty?
      edges.fetch(id, {}).each do |button, dest|
        next if seen[dest] || dest == id
        seen[dest] = true; queue << [dest, first || button]
      end
    end
    nil
  end

  def self.route(edges, from, to)
    queue = [[from, []]]; seen = { from => true }
    until queue.empty?
      id, path = queue.shift
      return path if id == to
      edges.fetch(id, {}).each do |button, dest|
        next if seen[dest] || dest == id
        seen[dest] = true; queue << [dest, path + [[button, dest]]]
      end
    end
    nil
  end

  # ADR-0035 phase A: the text comes from PromptSlots variant P0 (byte-identical to turns-26..27b).
  def self.instruction(prompt, done_steps, projection, image:, variant: {})
    PromptSlots.build('fixture-planner', { 'descriptor' => image ? 'image' : 'compact-p0' }.merge(variant),
                      task: prompt, done_steps: done_steps, projection: projection)[:text]
  end

  # ADR-0035 host question (Joe, 2026-11-24): the host asks 1 yes/no question for each planned focus or activate target.
  # The answer sets the op: press true gives activate, false gives focus. Text only; the screen is not sent.
  # Modes: focus-only (ask only for focus steps; a planned activate stays) or all (ask for every non-back step).
  PRESS_QUESTIONS = {
    'bare' => 'Task: %<task>s Control: %<control>s. To do this task, must the remote press select on this control? ' \
              'Answer with press true or press false.',
    'verbs' => 'Task: %<task>s Control: %<control>s. To do this task, must the remote press select on this control? ' \
               'Press select if the task adds, opens, enables, activates, selects, chooses, plays or replaces with this control. ' \
               'Do not press select if the task only finds this control, goes to it or moves focus to it, or says not to activate it. ' \
               'Answer with press true or press false.',
    'verbs-not' => 'Task: %<task>s Control: %<control>s. To do this task, must the remote press select on this control? ' \
                   'Press select if the task adds, opens, enables, activates, selects, chooses, plays or replaces with this control. ' \
                   'Do not press select if the task only finds this control, goes to it or moves focus to it, or says not to activate it. ' \
                   'If the task says "without activating" or "do not activate" this control, answer press false. ' \
                   'If the task names a different control to press, answer press false. Answer with press true or press false.'
  }.freeze
  PRESS_MODES = %w[focus-only all].freeze

  def self.press_question(kind, task, control)
    format(PRESS_QUESTIONS.fetch(kind), task: task.to_s.strip, control: control.to_s.strip)
  end

  # Returns the indexes of the steps the host asks about.
  def self.press_targets(plan, mode)
    raise ArgumentError, "unknown press mode #{mode}" unless PRESS_MODES.include?(mode)
    plan['steps'].each_index.select { |i| (s = plan['steps'][i])['target'] && (mode == 'all' ? s['op'] != 'back' : s['op'] == 'focus') }
  end

  # answers: { step index => true|false }. A changed step keeps its target and times; focus always has times 1.
  def self.apply_press(plan, answers)
    steps = plan['steps'].each_with_index.map do |s, i|
      next s unless answers.key?(i)
      answers[i] ? s.merge('op' => 'activate') : s.merge('op' => 'focus', 'times' => 1)
    end
    plan.merge('steps' => steps)
  end
end

class LocalTurnRun
  def plan_episode(task, arm, prompt, slot:)
    @task, @arm = task, arm; @case_dir = File.join(@out, slot); Dir.mkdir(@case_dir)
    @public_focus_goal = nil; @plan_terminal = nil
    @node_ids = {}; @sample_index = 0; @inputs = []; @observations = []; @decision = nil; @issue = nil
    args, initial = @bench ? Bench666.case_for(@bench, task) : B::CASES.fetch(task); restart(args, initial); @edges = {}; @dead = Hash.new { |h, k| h[k] = [] }; @no_move_presses = 0
    survey(initial) unless arm == 'image960'
    @observations = [sample]; persist
    done_steps = []; @plan_log = []
    1.upto(GoalPlanner::MAX_PLANS) do |n|
      raw = @observations.last
      dir = @case_dir + "/call-#{n}"; Dir.mkdir(dir)
      png = screenshot(dir, snap); jpeg = content('optimized', nil, png, nil, dir)[1]['path']
      projection = nil
      if arm != 'image960'
        projection = B.projection(raw)
        ocr, err, status = Open3.capture3('tesseract', jpeg, 'stdout', '--psm', '11')
        raise err unless status.success?
        projection['screenText'] = ocr.strip[0, 1500]
        ids = projection['controls'].map { |c| c['id'] }
        projection['routes'] = @edges.slice(*ids).transform_values { |edges| edges.select { |_, dst| ids.include?(dst) } }
        projection['notVisible'] = B.controls(raw).reject { |c| ids.include?(c.dig('identity', 'id')) || c['hidden'] }
                                     .map { |c| { 'id' => c.dig('identity', 'id'), 'label' => c['publicLabel'] } }
      end
      @observations << sample; persist
      raise 'observation changed before model' unless B.signature(raw) == B.signature(@observations.last)
      plan = @provider.ask(dir, GoalPlanner.instruction(prompt, done_steps, projection, image: arm == 'image960', variant: @prompt_variant || {}), arm == 'image960' ? jpeg : nil)
      @plan_log << plan
      save(File.join(dir, 'plan.json'), plan)
      if plan['after'] == 'abstain'
        raise 'abstain plan has steps' unless plan['steps'].empty?
        @plan_terminal = @decision = 'abstain'
        break
      end
      plan['steps'].each do |step|
        run_step(step)
        done_steps << step
      end
      if plan['after'] == 'done'
        @plan_terminal = @decision = 'done'
        break
      end
    end
    raise 'plan limit reached without done or abstain' unless @decision
    @observations << sample
  rescue => error
    @issue = error.message
    # An unresolved first target with no input sent is the host's abstention: the requested control is absent.
    if @issue.start_with?('target not found') && @inputs.empty?
      @decision = 'abstain'; @issue = nil
      @observations << sample
    end
    save(@case_dir + '/failure.json', { 'task' => task, 'arm' => arm, 'issue' => @issue }) if @issue
    raise if @provider.unknown || @issue.to_s.match?(/uncertain|campaign ceiling|deadline|sequence|provider ceiling/i) || @inputs.any? { |i| i['state'] == 'pending' }
  ensure
    save(@case_dir + '/plans.json', @plan_log || [])
    persist if @observations && !@observations.empty? && @observations.first['runID'] == @run
    puts JSON.generate(task: task, arm: arm, mode: 'planner', issue: @issue); STDOUT.flush
  end

  def run_step(step)
    case step['op']
    when 'back'
      execute_button('back')
    when 'focus'
      navigate_to(step['target'])
    when 'activate'
      step['times'].times do
        id = navigate_to(step['target'])
        before = B.activation_events(@observations).size
        begin
          execute_button('select')
        rescue RuntimeError => e
          # Phase C: some activations change only text that the SDK does not register (Pulse, recommendations, queue).
          # The press is delivered and observed; native activation evidence decides, as below.
          raise unless e.message == 'no progress' && B.activation_events(@observations).size == before + 1
        end
        raise "activation not observed: #{id}" unless B.activation_events(@observations).size == before + 1
      end
    end
  end

  # Move focus to the target. Returns its id. Postcondition: native focus is on that control.
  def navigate_to(target)
    visited = []
    loop do
      raw = @observations.last
      visible_ids = B.visible_controls(raw).map { |c| c.dig('identity', 'id') }
      control = GoalPlanner.resolve(B.controls(raw), visible_ids, target)
      raise "target not found: #{target}" unless control
      id = control.dig('identity', 'id')
      here = B.focus(raw)['id']
      return id if here == id
      visited << here
      raise 'route exceeds remaining input limit' if @inputs.size >= 16
      path = GoalPlanner.route(@edges, here, id)
      button = path ? path.first.first : nil
      unless button
        from = B.control(raw, here) or raise 'focused control not registered'
        looping = @edges.fetch(here, {}).select { |_, dest| visited.include?(dest) }.keys # Known edges back to a passed control.
        button = GoalPlanner.directions_toward(from['bounds'], control['bounds'], @dead[here] + looping).first ||
                 GoalPlanner.explore(@edges, @dead, here)
        raise "no direction left toward #{id}" unless button
      end
      begin
        execute_button(button)
      rescue RuntimeError => e
        # A delivered press that did not move focus is observed, not uncertain. Record it and choose another direction.
        raise unless e.message == 'no progress' && (@no_move_presses += 1) <= MAX_NO_MOVE
        @dead[here] << button
        next
      end
      (@edges[here] ||= {})[button] = B.focus(@observations.last)['id']
    end
  end
  MAX_NO_MOVE = 4 # Exploration meets walls; TTR's 16-input limit still bounds each episode.
end

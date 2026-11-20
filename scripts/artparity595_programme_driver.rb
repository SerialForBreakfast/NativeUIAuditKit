require 'open3'
require 'json'
require 'securerandom'
require 'fileutils'
require 'digest'
PROGRAMME = %w[--field-atlas --cinema-program].include?(ARGV.first) ? ARGV.shift : nil
MASONRY = ARGV.first == '--masonry'
ARGV.shift if MASONRY
# ARTPARITY595 local copy of TTR Scripts/qualify-editorial-gallery.rb (TTR 8053ed1b, sha256 9800f40d68101f265bdd24dcf8ee349c8d5bbd7ad0bb08c42d366a4f6221edc4).
# Changes: ROOT comes from TTR_ROOT; the idle check uses `status` (this build has no `coordinator status` command).
ROOT = File.realpath(ENV.fetch('TTR_ROOT'))
abort "Usage: ruby Scripts/qualify-editorial-gallery.rb [--masonry|--field-atlas|--cinema-program] SIMULATOR_UUID BUNDLED_AATV PROJECT_OUTPUT_PARENT" unless ARGV.size == 3
SIM = ARGV.fetch(0)
abort "Expected a Simulator UUID" unless SIM.match?(/\A[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\z/i)
CLI = File.expand_path(ARGV.fetch(1))
parent = File.realpath(ARGV.fetch(2))
abort "Expected project-local output and bundled CLI" unless parent.start_with?(ROOT+"/") && File.realpath(CLI).start_with?(ROOT+"/") && CLI.end_with?(".app/Contents/Helpers/aatv")
OUT = File.join(parent, SecureRandom.uuid)
FileUtils.mkdir(OUT, mode: 0700)
def call(label,*args)
  raw, _err, status = Open3.capture3([CLI,CLI], '--project', ROOT, '--json', '--timeout-ms','30000', *args)
  File.write(OUT+'/'+label+'.json',raw)
  response=JSON.parse(raw)
  raise "#{label} failed #{response['error']}" unless status.success? && response['success']
  response.fetch('data').values.first.fetch('_0')
end
def video(label,action,id,session,*more)
  call(label,'record','video',action,'--simulator-udid',SIM,'--session-id',session,'--recording-id',id,*more)
end
def until_state(seconds,expected)
  deadline=Process.clock_gettime(Process::CLOCK_MONOTONIC)+seconds
  loop do
    value=yield
    return value if expected.include?(value['state'])
    raise "terminal state #{value['state']}: #{value['reason']}" if %w[failed cancelled closed uncertain].include?(value['state'])
    raise "state deadline #{value['state']}" if Process.clock_gettime(Process::CLOCK_MONOTONIC)>=deadline
    sleep 0.5
  end
end
summary={}
session=nil
id=nil
movie_finished=false
begin
  health=call('status','status')
  raise 'coordinator occupied' if health['commandActive'] || health['observationActive'] || health['queuedCommandCount']!=0
  ready=call('readiness','simulator','readiness','--simulator-udid',SIM)
  raise "target unavailable #{ready['ownership']}" unless ready['can_run'] && ready.fetch('ownership').all?{|o|o['state']=='clear'}

  remote=call('connect','simulator','remote','connect','--simulator-udid',SIM)
  session=remote.fetch('operationID')
  until_state(100,['ready']) {call('remote-status','simulator','remote','status','--simulator-udid',SIM,'--session',session)}
  observe=lambda do |label,field|
    call(label,'simulator','remote','ui-observe','--simulator-udid',SIM,'--session',session,'--bundle-id','com.showblender.TVTestRigFixture','--field-id',field).fetch('uiObservation')
  end
  check=lambda do |label,field,focus|
    o=observe.call(label,field)
    raise "#{label}: #{o}" unless o['matchCount']==1 && o['foregroundBefore'] && o['foregroundAfter'] && o['hasFocus']==focus
  end
  id=SecureRandom.uuid
  video('start','start',id,session,'--duration-seconds','240')
  until_state(15,['recording']) {video('recording','status',id,session)}
  snap=lambda do |step,focus|
    check.call(step+'-before',focus,true)
    if PROGRAMME
      check.call(step+"-decor","programme.illustration",false)
      3.times do |i|
        field = "programme.control.#{i}"
        check.call(step+"-control-#{i}",field,field == focus)
      end
    elsif focus=='gallery.detail.return'
      check.call(step+'-content','gallery.notes.2',false)
    elsif !MASONRY
      check.call(step+'-selection','gallery.selection.0',false)
      check.call(step+'-curator','gallery.row.0',false)
    end
    r=call(step+'-snapshot','simulator','remote','snapshot','--simulator-udid',SIM,'--session',session)
    ref="SimulatorDiagnostics/#{session.downcase}/remote-snapshot-#{r.fetch('sequence')}.png"
    raise r.inspect unless r['state']=='delivered' && r['screenshotReference']==ref
    FileUtils.cp(File.join(ROOT,'Diagnostics/Runtime',ref),File.join(OUT,step+'.png'))
    check.call(step+'-after',focus,true)
  end
  press=lambda do |label,button|
    r=call(label,'simulator','remote','press','--simulator-udid',SIM,'--session',session,'--button',button)
    raise r.inspect unless r['state']=='delivered'
    sleep 0.45
  end
  if PROGRAMME
    direction = PROGRAMME == "--field-atlas" ? "down" : "right"
    3.times do |i|
      press.call("move-#{i}",direction) unless i.zero?
      snap.call("position-#{i}","programme.control.#{i}")
    end
  elsif MASONRY
    snap.call('initial','mosaic.tile.1')
    press.call('move-left','left')
    snap.call('left-edge','mosaic.tile.0')
    press.call('edge-left','left')
    check.call('left-clamp','mosaic.tile.0',true)
    press.call('from-left','right')
    # A tall work shares an edge with two short works. Resolve the actual
    # native destination and require exactly one of those neighbors.
    neighbors = [1, 2].select do |index|
      observation = observe.call("from-left-neighbor-#{index}", "mosaic.tile.#{index}")
      raise 'invalid neighbor observation' unless observation['matchCount'] == 1 && observation['foregroundBefore'] && observation['foregroundAfter']
      observation.fetch('hasFocus')
    end
    raise "unexpected focus after left return: #{neighbors}" unless neighbors.size == 1
    press.call('lower','down') if neighbors.first == 1
    snap.call('lower-row','mosaic.tile.2')
    press.call('up','up')
    check.call('upper-return','mosaic.tile.1',true)
    press.call('toward-right','right')
    check.call('portrait','mosaic.tile.3',true)
    press.call('move-right','right')
    snap.call('right-edge','mosaic.tile.4')
    press.call('edge-right','right')
    check.call('right-clamp','mosaic.tile.4',true)
  else
    snap.call('initial','gallery.row.1')
    press.call('down','down')
    snap.call('browsed','gallery.row.2')
    press.call('select','select')
    snap.call('detail','gallery.detail.return')
    press.call('back','back')
    snap.call('returned','gallery.row.2')
    press.call('open-again','select')
    check.call('opened-again','gallery.detail.return',true)
    press.call('visible-return','select')
    check.call('button-returned','gallery.row.2',true)
    check.call('still-selected','gallery.selection.0',false)
  end
  video('stop','stop',id,session)
  done=until_state(20,['completed']) {video('finish','status',id,session)}
  movie_finished=true
  video('save','export',id,session,'--destination',OUT+'/saved')
  summary.merge!(sha256:done.fetch('movieSHA256'),session:session,recording:id,outcome:'saved')
rescue => e
  summary.merge!(outcome:'incomplete',error:e.message)
ensure
  if session
    begin
      video('cleanup-stop','stop',id,session) if id && !movie_finished
    rescue => e
      summary[:stop_error]=e.message
    end
    begin
      call('disconnect','simulator','remote','disconnect','--simulator-udid',SIM,'--session',session)
      summary[:closure]=until_state(50,['closed']) {call('closed','simulator','remote','status','--simulator-udid',SIM,'--session',session)}['state']
    rescue => e
      summary[:closure_error]=e.message
    end
  end
  File.write(OUT+'/summary.json',JSON.pretty_generate(summary))
end
if summary[:outcome]=='saved' && summary[:closure]=='closed'
  reopened=video('reopen','inspect',id,session)
  video('copy','export',id,session,'--destination',OUT+'/reopened')
  %w[saved reopened].each do |folder|
    %w[capture.mov inputs.jsonl].zip(%w[movieSHA256 eventsSHA256]).each do |f,k|
      raise f unless Digest::SHA256.file(File.join(OUT,folder,f)).hexdigest==reopened.fetch(k)
    end
  end
  summary[:outcome]='verified_reopened'
  File.write(OUT+'/summary.json',JSON.pretty_generate(summary))
end
puts JSON.generate(summary.merge(path:OUT))
exit(summary[:outcome]=='verified_reopened' ? 0 : 1)

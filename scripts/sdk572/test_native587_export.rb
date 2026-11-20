# Check current SDK metadata against retained evidence. Do not capture or alter inputs.
require File.expand_path(ARGV.fetch(0))
path=File.expand_path(ARGV.fetch(1));dir=File.dirname(path)
manifest=JSON.parse(File.read(path));original=JSON.parse(File.read(dir+'/evidence.json'))
# The exporter reads evidence from disk. Validate mutated copies in a new project folder.
out=File.expand_path(ARGV.fetch(2));raise 'existing test output' if File.exist?(out)
FileUtils.mkdir_p(out);FileUtils.cp(dir+'/frame.png',out+'/frame.png')
write=->(e){bytes=JSON.generate(e);File.write(out+'/evidence.json',bytes);m=Marshal.load(Marshal.dump(manifest));m['cases'][0]['frames'][0]['evidenceSHA256']=SDKEvidenceExport.sha(bytes);m}
SDKEvidenceExport.plan(write.call(original),out)
changes={
 'unknown visual metadata'=>->(e){e['before']['visualContext']['privateToken']='x'},
 'invalid style source'=>->(e){e['before']['elements'][0]['focusStyleSource']='fabricated'},
 'unpaired style'=>->(e){e['before']['elements'][0].delete('focusStyleSource')},
 'native transform disagreement'=>->(e){e['before']['elements'][0]['captureGeometry']['native']['toNativePixels'][0]=9},
 'native extent disagreement'=>->(e){e['before']['elements'][0]['captureGeometry']['native']['nativeBounds']['width']=7},
 'negative native inset'=>->(e){e['before']['elements'][0]['captureGeometry']['native']['safeAreaInsets']['top']=-1},
 'unversioned native fields'=>->(e){e['before']['elements'][0]['captureGeometry']['schemaVersion']=1}
}
changes.each do |name,change|
 e=Marshal.load(Marshal.dump(original));change.call(e)
 begin;SDKEvidenceExport.plan(write.call(e),out);raise "accepted #{name}";rescue ArgumentError;end
 puts "PASS #{name}"
end
puts '8 current metadata checks passed'

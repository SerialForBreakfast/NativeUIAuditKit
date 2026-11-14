import UIKit
import CryptoKit
let families=["search","settings","shelf","detail","modal","playback"]
let args=CommandLine.arguments
let out=FileManager.default.urls(for:.documentDirectory,in:.userDomainMask)[0].appendingPathComponent(args.contains("--simctl") ? "CORPUS640-live-v1":"CORPUS640")
try! FileManager.default.createDirectory(at:out,withIntermediateDirectories:true)
func dataHash(_ d:Data)->String {SHA256.hash(data:d).map{String(format:"%02x",$0)}.joined()}
func write(_ obj:Any,_ name:String) {try! JSONSerialization.data(withJSONObject:obj,options:[.sortedKeys]).write(to:out.appendingPathComponent(name),options:.atomic)}
func art(_ seed:Int,_ size:CGSize)->UIImage {
 let f=UIGraphicsImageRendererFormat();f.scale=1
 return UIGraphicsImageRenderer(size:size,format:f).image { c in
  UIColor(hue:CGFloat(seed%12)/12,saturation:0.55,brightness:0.45,alpha:1).setFill();c.fill(CGRect(origin:.zero,size:size))
  for k in 0..<7 { UIColor(hue:CGFloat((seed+k*2)%12)/12,saturation:0.45,brightness:0.65,alpha:1).setFill();let x=CGFloat((seed*31+k*47)%Int(max(1,size.width-40)));let y=CGFloat((seed*13+k*53)%Int(max(1,size.height-40)));UIBezierPath(roundedRect:CGRect(x:x,y:y,width:80+CGFloat(k*9),height:50+CGFloat(k*13)),cornerRadius:CGFloat(k*3)).fill() }
 }
}
struct Item {let id:String;let cls:String;let primitive:String;let view:UIView;let parent:String?}
final class Scene:UIViewController,UICollectionViewDataSource,UICollectionViewDelegateFlowLayout {
 let family:String;let group:Int;let state:Int
 var items:[Item]=[];var captions:[UILabel]=[];var collection:UICollectionView?;var cellCount=0;var cellSize=CGSize.zero;var desired:UIView?;var interactive:[UIView]=[];var picker:UISegmentedControl?;var field:UITextField?;var modal:UIAlertController?
 init(_ f:String,_ g:Int,_ s:Int){family=f;group=g;state=s;super.init(nibName:nil,bundle:nil)}
 required init?(coder:NSCoder){fatalError()}
 override var preferredFocusEnvironments:[UIFocusEnvironment] {desired.map{[$0]} ?? super.preferredFocusEnvironments}
 func add(_ id:String,_ cls:String,_ prim:String,_ v:UIView,_ rect:CGRect,_ parent:String?=nil){v.frame=rect;view.addSubview(v);items.append(Item(id:id,cls:cls,primitive:prim,view:v,parent:parent))}
 func label(_ text:String,_ rect:CGRect,_ size:CGFloat=28){let l=UILabel(frame:rect);l.text=text;l.textColor = .white;l.font = .systemFont(ofSize:size,weight:.semibold);view.addSubview(l);captions.append(l)}
 @discardableResult func button(_ id:String,_ title:String,_ rect:CGRect)->UIButton {let b=UIButton(type:.system);var c=UIButton.Configuration.filled();c.title=title;c.cornerStyle = .medium;b.configuration=c;b.isEnabled=true;add(id,"button","UIButton",b,rect);interactive.append(b);return b}
 func image(_ id:String,_ rect:CGRect,_ seed:Int){let v=UIImageView(image:art(seed,rect.size));v.contentMode = .scaleToFill;add(id,"picture","UIImageView",v,rect)}
 func makePicker(_ rect:CGRect){let p=UISegmentedControl(items:["All","Recent","Saved"]);p.selectedSegmentIndex=state==4 ? (group+1)%3:group%3;p.backgroundColor = .darkGray;add("mode","segmentedControl","UISegmentedControl",p,rect);picker=p;interactive.append(p)}
 func makeField(_ rect:CGRect){let t=UITextField();t.borderStyle = .roundedRect;t.text="Search \(["programmes","recordings","channels","editions"][group%4])";t.backgroundColor = .white;t.textColor = .black;add("search","textField","UITextField",t,rect);field=t;interactive.append(t)}
 override func viewDidLoad(){super.viewDidLoad();view.backgroundColor=UIColor(red:0.05+CGFloat(group%3)*0.025,green:0.075,blue:0.11+CGFloat(group%2)*0.025,alpha:1)
 let dx=CGFloat(group%5)*35;let wide=group<5;let title=["Library search","Programme settings","Featured collection","Programme details","Playback options","Now playing"][families.firstIndex(of:family)!]
 label(title+"  •  \(group+1)",CGRect(x:90,y:55,width:1650,height:85),46)
 label(["Regional editions and saved programmes","Evening service    ·    Updated today","Library archive    ·    24 programmes"][group%3],CGRect(x:95,y:155,width:1660,height:55),28)
 switch family {
 case "search":
  makePicker(CGRect(x:105+dx,y:265,width:wide ? 1050:700,height:86));makeField(CGRect(x:wide ? 140:960,y:wide ? 430:300,width:wide ? 1450:690,height:82+CGFloat(group%3)*4))
  button("primary","Search archive",CGRect(x:150,y:620,width:600+dx,height:86));button("secondary","Clear filters",CGRect(x:970,y:620,width:620,height:86))
  label("Suggested collections",CGRect(x:110,y:785,width:1000,height:50),30)
  for k in 0..<3 {button("suggestion.\(k)",["Morning edition","Live programme","Local recordings"][k],CGRect(x:110+CGFloat(k)*560,y:860,width:500,height:80))}
 case "settings":
  makePicker(CGRect(x:100+dx,y:250,width:wide ? 980:700,height:82));makeCollection(CGRect(x:wide ? 110:460,y:390,width:wide ? 1280:1170,height:460),count:4,size:CGSize(width:wide ? 1200:1090,height:82+CGFloat(group%2)*10),horizontal:false)
  button("primary","Apply changes",CGRect(x:120+dx,y:900,width:650,height:84));button("secondary","Restore defaults",CGRect(x:1000,y:900,width:650,height:84))
 case "shelf":
  makePicker(CGRect(x:100+dx,y:250,width:wide ? 1100:760,height:82));let count=4+group%3;let w=CGFloat(1380/count)
  makeCollection(CGRect(x:90+CGFloat(group%3)*20,y:390,width:1690,height:410+CGFloat(group%2)*35),count:count,size:CGSize(width:w,height:wide ? 350:390),horizontal:true)
  button("primary","Open collection",CGRect(x:140+dx,y:900,width:650,height:84));button("secondary","Browse all",CGRect(x:1000,y:900,width:650,height:84))
 case "detail":
  image("poster",CGRect(x:wide ? 110:1200,y:270,width:wide ? 520+CGFloat(group%5)*8:460-CGFloat(group%5)*8,height:570-CGFloat(group%5)*10),group+20)
  let tx:CGFloat=wide ? 760+dx:110+dx;label("A regional programme",CGRect(x:tx,y:275,width:900,height:70),38);label("Documentary  ·  48 min  ·  Original edition",CGRect(x:tx,y:370,width:900,height:60),26)
  label("Explore the people and places behind the programme.",CGRect(x:tx,y:445,width:900,height:65),25)
  makePicker(CGRect(x:tx,y:560,width:850,height:82));button("primary","Play programme",CGRect(x:tx,y:700,width:700,height:86));button("secondary","Add to library",CGRect(x:tx,y:820,width:700,height:86));button("more","More options",CGRect(x:tx,y:930,width:600,height:62))
 case "playback":
  image("video",CGRect(x:100+CGFloat(group%3)*25,y:245,width:1650-CGFloat(group%3)*50,height:450+CGFloat(group%2)*40),group+40)
  label("12:40                                      48:00",CGRect(x:130,y:735,width:1630,height:45),24)
  let progress=UIProgressView(progressViewStyle:.default);progress.progress=Float(group+2)/12+(state==3 ? 0.12:0);progress.progressTintColor = .white;progress.trackTintColor = .gray;add("progress","indicator","UIProgressView",progress,CGRect(x:130,y:795,width:1600,height:2))
  makePicker(CGRect(x:110+dx,y:875,width:600,height:82));button("primary","Play / Pause",CGRect(x:820,y:875,width:500,height:86));button("secondary","Audio options",CGRect(x:1390,y:875,width:400,height:86))
 case "modal":
  image("backdrop-art",CGRect(x:100+dx,y:260+CGFloat(group%5)*12,width:1650-dx,height:650-CGFloat(group%5)*18),group+60)
 default:break
 }
 label(family=="settings" ? "Changes apply to this profile only" : "Native library workspace    ·    Independent synthetic layout",CGRect(x:100,y:1005,width:1660,height:42),22)
 if !interactive.isEmpty {desired=interactive[state==0 || state==4 ? 0:min(state,interactive.count-1)]}
 }
 func makeCollection(_ frame:CGRect,count:Int,size:CGSize,horizontal:Bool){let l=UICollectionViewFlowLayout();l.scrollDirection=horizontal ? .horizontal:.vertical;l.itemSize=size;l.minimumLineSpacing=horizontal ? 28:20;l.minimumInteritemSpacing=20;cellSize=size;cellCount=count
 let c=UICollectionView(frame:frame,collectionViewLayout:l);c.backgroundColor = .clear;c.isScrollEnabled=false;c.dataSource=self;c.delegate=self;c.register(UICollectionViewCell.self,forCellWithReuseIdentifier:"cell");view.addSubview(c);collection=c}
 func collectionView(_ c:UICollectionView,numberOfItemsInSection s:Int)->Int{cellCount}
 func collectionView(_ c:UICollectionView,cellForItemAt i:IndexPath)->UICollectionViewCell {let v=c.dequeueReusableCell(withReuseIdentifier:"cell",for:i);for s in v.contentView.subviews{s.removeFromSuperview()};v.contentView.backgroundColor=UIColor(white:0.24,alpha:1)
 let im=UIImageView(image:art(group*7+i.item,cellSize));im.frame=v.contentView.bounds;im.autoresizingMask=[.flexibleWidth,.flexibleHeight];v.contentView.addSubview(im)
 let l=UILabel(frame:CGRect(x:18,y:family=="settings" ? 15:cellSize.height-65,width:cellSize.width-36,height:50));l.text=family=="settings" ? ["Audio language","Subtitle preference","Playback quality","Privacy options"][i.item]:"Programme \(i.item+1)";l.font = .systemFont(ofSize:family=="settings" ? 28:24,weight:.semibold);l.textColor = .white;l.backgroundColor=UIColor.black.withAlphaComponent(0.6);v.contentView.addSubview(l);return v}
 func finalizeScene(){view.layoutIfNeeded();collection?.layoutIfNeeded();if let c=collection {for i in 0..<cellCount {if let v=c.cellForItem(at:IndexPath(item:i,section:0)){items.append(Item(id:"item.\(i)",cls:"cell",primitive:"UICollectionViewCell",view:v,parent:nil));for (k,sub) in v.contentView.subviews.enumerated(){items.append(Item(id:"item.\(i).owned.\(k)",cls:"owned_metadata",primitive:sub is UIImageView ? "UIImageView":"UILabel",view:sub,parent:"item.\(i)"))}}}};if (state==3 || (family=="shelf" && state==2)),let c=collection,let v=c.cellForItem(at:IndexPath(item:state==2 ? 1:0,section:0)){desired=v};setNeedsFocusUpdate();updateFocusIfNeeded()}
 func presentModal(_ done:@escaping()->Void){guard family=="modal" else {done();return};let alert=UIAlertController(title:["Choose a playback option","Confirm library change","Programme actions"][group%3],message:["Choose how to continue with this programme.","Save this programme to the current profile.","This programme is available in several editions.","Removing the saved item does not remove the original.","Your current playback position stays available."][state],preferredStyle:group<5 ? .alert:.actionSheet)
 for k in 0..<(2+group%3){alert.addAction(UIAlertAction(title:["Play now","Save programme","View details","Close"][k],style:k==3 ? .cancel:.default))};modal=alert;present(alert,animated:false){self.items.append(Item(id:"dialog",cls:"dialog",primitive:"UIAlertController",view:alert.view,parent:nil));done()}}
 func box(_ v:UIView)->[CGFloat]{guard let w=view.window else{return []};let b=v.convert(v.bounds,to:w),s=w.screen.scale;let q=b.intersection(w.bounds);return [q.minX,q.minY,q.width,q.height].map{($0*s).rounded()}}
 func record()->[String:Any]{let f=UIFocusSystem(for:view)?.focusedItem as? UIView;let id=items.first{$0.view===f || (f?.isDescendant(of:$0.view) ?? false)}?.id
 let ts=items.filter{$0.parent==nil}.map{["id":$0.id,"cls":$0.cls,"owner":$0.primitive,"focusable":$0.view.canBecomeFocused,"box_src_px":box($0.view)] as [String:Any]}
 return ["family":family,"layoutGroup":"CORPUS640.\(family).\(group)","state":state,"selectedSegment":picker?.selectedSegmentIndex as Any? ?? NSNull(),"contentVariant":family=="modal" ? "message-\(state)" : (family=="playback" && state==3 ? "progress-changed" : (state==4 ? "picker-selection-changed":"fixed-content")),"targets":ts,"captions":captions.map{box($0)},"focusObservation":["state":id==nil ? "unknown":"focused","id":id as Any? ?? NSNull(),"source":"UIFocusSystem.focusedItem"],"partialReasons":family=="modal" ? ["UIAlertAction public geometry join is not qualified"]:[],"modalBounds":modal.map{box($0.view)} ?? [],"ownedMetadata":items.filter{$0.parent != nil}.map{["id":$0.id,"parent":$0.parent!,"owner":$0.primitive,"box_src_px":box($0.view)] as [String:Any]},"nativeTypes":items.map{String(describing:type(of:$0.view))}]
 }
}
final class App:UIResponder,UIApplicationDelegate {
 var window:UIWindow?;var scene:Scene?;var rows:[[String:Any]]=[];var index=0
 func application(_ app:UIApplication,didFinishLaunchingWithOptions o:[UIApplication.LaunchOptionsKey:Any]?)->Bool{let w=UIWindow(frame:UIScreen.main.bounds);window=w;next();w.makeKeyAndVisible();return true}
 func next(){let pilot=args.contains("--pilot");if index >= (pilot ? 1:300) {write(["complete":true,"frames":index],"complete.json");return}
 let f=families[index/50],g=(index%50)/5,s=index%5;let c=Scene(f,g,s);scene=c;window!.rootViewController=c
 DispatchQueue.main.asyncAfter(deadline:.now()+0.4){c.finalizeScene();c.presentModal{DispatchQueue.main.asyncAfter(deadline:.now()+0.6){self.capture(c)}}}
 }
 func snap(_ name:String)->String{let w=window!;let format=UIGraphicsImageRendererFormat();format.scale=w.screen.scale;format.opaque=true;let im=UIGraphicsImageRenderer(bounds:w.bounds,format:format).image{_ in w.drawHierarchy(in:w.bounds,afterScreenUpdates:true)};let data=im.pngData()!;try! data.write(to:out.appendingPathComponent(name),options:.atomic);return dataHash(data)}
 func capture(_ c:Scene){if args.contains("--simctl"){externalStage(c,0);return};let name=String(format:"g%02d-s%d",index/5,index%5);var rec=c.record();let sha=snap(name+"-base.png"),repeatSHA=snap(name+"-repeat.png");rec["name"]=name;rec["baseFile"]=name+"-base.png";rec["baseSHA256"]=sha;rec["repeatSHA256"]=repeatSHA
 var hidden:[String:Any]=[:];let targets=c.items.filter{$0.parent==nil};hideNext(0,targets,c,name,&hidden,rec)
 }
 func externalStage(_ c:Scene,_ stage:Int){let targets=c.items.filter{$0.parent==nil}
 if stage>targets.count {index+=1;next();return}
 for t in targets {t.view.layer.opacity=1}
 if stage>0 {targets[stage-1].view.layer.opacity=0}
 DispatchQueue.main.asyncAfter(deadline:.now()+0.12){let seq=self.index*100+stage;var rec=c.record();rec["sequence"]=seq;rec["index"]=self.index;rec["name"]=String(format:"g%02d-s%d",self.index/5,self.index%5);rec["hiddenID"]=stage==0 ? "base":targets[stage-1].id;write(rec,"stage.json");self.waitAck(seq){write(c.record(),"observed-after-\(seq).json");self.externalStage(c,stage+1)}}
 }
 func waitAck(_ seq:Int,_ done:@escaping()->Void){let f=out.appendingPathComponent("ack.json");if let d=try? Data(contentsOf:f),let j=try? JSONSerialization.jsonObject(with:d) as? [String:Any],j["sequence"] as? Int==seq {done()} else {DispatchQueue.main.asyncAfter(deadline:.now()+0.025){self.waitAck(seq,done)}}}
 func hideNext(_ i:Int,_ targets:[Item],_ c:Scene,_ name:String,_ h:inout [String:Any],_ rec:[String:Any]){var hidden=h
 if i>=targets.count {var row=rec;row["hiddenFiles"]=hidden;rows.append(row);write(rows,"manifest.json");print("CORPUS640 "+name);fflush(stdout);index+=1;if args.contains("--pilot"){write(["complete":true,"frames":rows.count],"complete.json")}else{next()};return}
 let t=targets[i];t.view.layer.opacity=0
 DispatchQueue.main.asyncAfter(deadline:.now()+0.04){let file=name+"-hide-"+t.id+".png";let sh=self.snap(file);let sh2=self.snap(name+"-hide-"+t.id+"-repeat.png");hidden[t.id] = ["file":file,"sha256":sh,"repeatSHA256":sh2];t.view.layer.opacity=1
 DispatchQueue.main.asyncAfter(deadline:.now()+0.04){self.hideNext(i+1,targets,c,name,&hidden,rec)}}
 }
}
UIApplicationMain(CommandLine.argc,CommandLine.unsafeArgv,nil,NSStringFromClass(App.self))

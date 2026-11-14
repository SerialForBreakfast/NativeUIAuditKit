import SwiftUI
import UIKit

let directory = FileManager.default.urls(for: .documentDirectory,in: .userDomainMask)[0].appendingPathComponent("CORPUS640-live-v1")
try! FileManager.default.createDirectory(at:directory,withIntermediateDirectories:true)
func save(_ record:[String:Any],_ name:String) {
    try! JSONSerialization.data(withJSONObject:record,options:.sortedKeys).write(to:directory.appendingPathComponent(name),options:.atomic)
}

@MainActor final class SheetController: UIViewController {
    let group: Int
    let state: Int
    var controls = [(String,String,String,UIView)]()
    var captions = [UILabel]()
    var wrappers = [UIView]()
    func install(_ control:UIView) {
        let wrapper=UIView()
        wrapper.backgroundColor = .clear
        wrapper.clipsToBounds=true
        view.addSubview(wrapper)
        wrapper.addSubview(control)
        wrappers.append(wrapper)
    }
    func place(_ index:Int,_ frame:CGRect) {
        wrappers[index].frame=frame.integral
        controls[index].3.frame=wrappers[index].bounds
    }
    let picker = UISegmentedControl(items:["Episode","Series","Library"])
    var invoked: String?
    init(group:Int,state:Int) { self.group=group; self.state=state;super.init(nibName:nil,bundle:nil) }
    required init?(coder:NSCoder) { fatalError() }
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor=UIColor(red:0.13,green:0.20,blue:0.28,alpha:1)
        view.isOpaque=true
        picker.selectedSegmentIndex=state==4 ? (group+1)%3 : group%3
        controls.append(("mode","segmentedControl","UISegmentedControl",picker))
        install(picker)
        for (id,title) in [("confirm","Use setting"),("later","Keep current"),("options","More options")] {
            let button=UIButton(type:.system)
            var config=UIButton.Configuration.filled()
            config.title=title
            config.cornerStyle = .medium
            button.configuration=config
            button.addAction(UIAction { [weak self] _ in self?.invoked=id },for:.primaryActionTriggered)
            button.accessibilityIdentifier=id
            controls.append((id,"button","UIButton",button))
            install(button)
        }
        for (i,text) in [ ["Episode settings","Regional options","Playback options"][group%3], "Choose where to apply this setting." ].enumerated() {
            let label=UILabel()
            label.font = .systemFont(ofSize:i==0 ? 34 : 23,weight:i==0 ? .bold : .regular)
            label.textColor = .white;label.text=text;view.addSubview(label);captions.append(label)
        }
    }
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        let w=view.bounds.width,h=view.bounds.height
        guard w>320,h>300 else{return}
        let variant=CGFloat(group%5)
        let pad=w*(0.055+0.008*variant)
        if group<5 {
            let gap=w*(0.011+0.002*variant)
            let bw=(w-2*pad-2*gap)/3
            captions[0].frame=CGRect(x:pad,y:h*0.13,width:w-2*pad,height:h*0.08)
            captions[1].frame=CGRect(x:pad,y:h*0.23,width:w-2*pad,height:h*0.07)
            place(0,CGRect(x:pad,y:h*(0.42+0.017*variant),width:w-2*pad,height:h*0.10))
            for i in 0..<3 {
                place(i+1,CGRect(x:pad+CGFloat(i)*(bw+gap),y:h*(0.69+0.012*variant),width:bw,height:h*0.12))
            }
        } else {
            let columnX=w*(0.55+0.010*variant)
            let leftWidth=columnX-2*pad
            captions[0].frame=CGRect(x:pad,y:h*0.24,width:leftWidth,height:h*0.09)
            captions[1].frame=CGRect(x:pad,y:h*0.36,width:leftWidth,height:h*0.09)
            place(0,CGRect(x:pad,y:h*(0.54+0.014*variant),width:leftWidth,height:h*0.11))
            for i in 0..<3 {
                place(i+1,CGRect(x:columnX,y:h*(0.18+CGFloat(i)*0.23+0.005*variant),width:w-pad-columnX,height:h*0.15))
            }
        }
    }
    var preferred: UIView { controls[state==4 ? 0:state].3 }
    override var preferredFocusEnvironments:[UIFocusEnvironment] { controls.isEmpty ? super.preferredFocusEnvironments : [preferred] }
}

struct HostedController:UIViewControllerRepresentable {
    let scene:SheetController
    func makeUIViewController(context:Context)->SheetController{scene}
    func updateUIViewController(_ controller:SheetController,context:Context){}
}
struct Host: View {
    let scene:SheetController
    @State private var shown=false
    var body:some View {
        Color(red:0.05,green:0.07,blue:0.09).ignoresSafeArea()
            .onAppear { shown=true }
            .sheet(isPresented:$shown) {
                HostedController(scene:scene).ignoresSafeArea()
                    .presentationBackground(.clear)
                    .interactiveDismissDisabled()
            }
    }
}
@MainActor final class App:UIResponder,UIApplicationDelegate {
    var window:UIWindow?
    let startIndex=CommandLine.arguments.contains("--skip-pilot") ? 5:0
    lazy var index=startIndex
    var scene:SheetController!
    var host:UIHostingController<Host>!
    let waitingMax=90
    var surface:UIView? {
        guard let presented=host.presentedViewController,let visible=presented.viewIfLoaded,visible.window != nil,
              let body=scene.viewIfLoaded,body.window != nil,body.isDescendant(of:visible) || body===visible else{return nil}
        return visible
    }
    func application(_ app:UIApplication,didFinishLaunchingWithOptions opts:[UIApplication.LaunchOptionsKey:Any]?)->Bool {
        window=UIWindow(frame:UIScreen.main.bounds);next();window?.makeKeyAndVisible();return true
    }
    func next(){
        let end=CommandLine.arguments.contains("--pilot") ? 5:50
        guard index<end else {save(["complete":true,"frames":index-startIndex],"complete.json");return}
        scene=SheetController(group:index/5,state:index%5)
        host=UIHostingController(rootView:Host(scene:scene))
        window?.rootViewController=host
        poll(0)
    }
    func poll(_ n:Int){
        DispatchQueue.main.asyncAfter(deadline:.now()+0.12){[self] in
            guard let s=surface, !s.bounds.isEmpty, scene.controls.count==4 else {
                if n<waitingMax {poll(n+1)} else {save(["error":"presented surface never appeared"],"failed.json")}
                return
            }
            s.layoutIfNeeded();scene.view.layoutIfNeeded()
            if let focus=UIFocusSystem(for:scene.view) {focus.requestFocusUpdate(to:scene.preferred);focus.updateFocusIfNeeded()}
            DispatchQueue.main.asyncAfter(deadline:.now()+0.7){[self] in stage(0)}
        }
    }
    func box(_ view:UIView)->[Int] {
        let w=window!,r=view.convert(view.bounds,to:w),s=w.screen.scale
        let x=Int(floor(r.minX*s)),y=Int(floor(r.minY*s))
        return [x,y,Int(ceil(r.maxX*s))-x,Int(ceil(r.maxY*s))-y]
    }
    func record()->[String:Any] {
        guard let s=surface else{return ["partialReasons":["presentation disappeared"]]}
        let b=box(scene.view),pb=box(s),canvas=box(window!)
        let f=UIFocusSystem(for:scene.view)?.focusedItem as? UIView
        let id=scene.controls.first{f === $0.3 || (f?.isDescendant(of:$0.3) ?? false)}?.0
        var partial=[String]()
        // The actual presented view must exactly coincide with the visibly painted child surface.
        if b != pb {partial.append("presented surface and opaque body differ")}
        if pb[0]<0 || pb[1]<0 || pb[0]+pb[2]>canvas[2] || pb[1]+pb[3]>canvas[3] {partial.append("presented surface clipped")}
        var targets:[[String:Any]]=[["id":"surface","cls":"dialog","owner":"sheet","framework":"SwiftUI","focusable":false,"box_src_px":pb,"affordance_visible":true]]
        for (key,cls,owner,v) in scene.controls {targets.append(["id":key,"cls":cls,"owner":owner,"framework":"UIKit","focusable":v.canBecomeFocused,"box_src_px":box(v)])}
        let g=index/5,sn=index%5
        return ["family":"sheet","layoutGroup":"CORPUS640.modal.\(g)","state":sn,"selectedSegment":scene.picker.selectedSegmentIndex,
                "contentVariant":sn==4 ? "picker-selection-changed":"fixed-content","targets":targets,"captions":scene.captions.map(box),
                "focusObservation":["state":id==nil ? "unknown":"focused","id":id as Any? ?? NSNull(),"source":"UIFocusSystem.focusedItem"],
                "partialReasons":partial,"ownedMetadata":[],"nativeTypes":[NSStringFromClass(type(of:s))]+scene.controls.map{NSStringFromClass(type(of:$0.3))},
                "presentedController":String(describing:type(of:host.presentedViewController!)), "presentedBox":pb,"opaqueBodyBox":b,"presentedViewRuntimeClass":NSStringFromClass(type(of:s)),"opaqueBodyRuntimeClass":NSStringFromClass(type(of:scene.view!)),"actionRuntimeTypes":scene.controls.map{["id":$0.0,"nativeType":NSStringFromClass(type(of:$0.3))]}]
    }
    func stage(_ step:Int){
        guard let s=surface else{save(["error":"presentation disappeared"],"failed.json");return}
        let targets=[("surface",s)]+scene.controls.map{($0.0,$0.3)}
        if step>targets.count {index+=1;next();return}
        s.layer.opacity=1;for t in targets.dropFirst(){t.1.layer.opacity=1}
        if step>0 {targets[step-1].1.layer.opacity=0}
        DispatchQueue.main.asyncAfter(deadline:.now()+0.16){[self] in
            var r=record();let seq=index*100+step
            r["name"]=String(format:"sheetbody-g%02d-s%d",index/5,index%5);r["sequence"]=seq;r["index"]=index;r["hiddenID"]=step==0 ? "base":targets[step-1].0
            save(r,"stage.json");wait(seq){[self] in save(record(),"observed-after-\(seq).json");stage(step+1)}
        }
    }
    func wait(_ seq:Int,_ done:@escaping()->Void){
        if let b=try? Data(contentsOf:directory.appendingPathComponent("ack.json")),let v=try? JSONSerialization.jsonObject(with:b) as? [String:Any],v["sequence"] as? Int==seq {done();return}
        DispatchQueue.main.asyncAfter(deadline:.now()+0.03){[self] in wait(seq,done)}
    }
}
UIApplicationMain(CommandLine.argc,CommandLine.unsafeArgv,nil,NSStringFromClass(App.self))

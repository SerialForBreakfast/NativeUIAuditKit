import UIKit
import SwiftUI

private let args = ProcessInfo.processInfo.arguments
private let isSwift = args.contains("--swiftui")
private let training = args.contains("--training")
private let filled = !args.contains("--opaque")
private let height: CGFloat = training ? (args.contains("--offset-layout") ? 53 : 59) : 53
private func probe(_ kind: String, _ index: Int) -> UIColor? {
    guard args.contains("--probe="+kind+String(index)) else { return nil }
    return args.contains("--white") ? .white : .black
}
private func color(_ i: Int) -> UIColor {
    if let ink = probe("r",i) { return ink }
    return UIColor(red: 0.04, green: i.isMultiple(of: 2) ? 0.28 : 0.58, blue: training ? 0.60 : 0.45, alpha: 1)
}
private let lowSheet = args.contains("--low-sheet")
private let study = args.contains("--material-study")
private let material = args.first(where: { $0.hasPrefix("--backing=") })?.dropFirst(10) ?? "system"
private let alpha = args.first(where: { $0.hasPrefix("--alpha=") }).flatMap { Double($0.dropFirst(8)) } ?? (filled ? 0.55 : 1)
private let glass = UIColor(red: 1, green: 0.02, blue: 0.04, alpha: alpha)

private struct StudySurface: UIViewRepresentable {
    func makeUIView(context: Context) -> UIView {
        let body = UIView()
        if material == "thin" || material == "thick" {
            let blur = UIVisualEffectView(effect: UIBlurEffect(style: material == "thin" ? .systemUltraThinMaterial : .systemThickMaterial))
            blur.frame = body.bounds; blur.autoresizingMask = [.flexibleWidth,.flexibleHeight]; body.addSubview(blur)
        }
        let tint = UIView(); tint.backgroundColor = glass; tint.frame = body.bounds
        tint.autoresizingMask = [.flexibleWidth,.flexibleHeight]; body.addSubview(tint)
        return body
    }
    func updateUIView(_ uiView: UIView, context: Context) {}
}
private let count = 8
private let accColor = UIColor(red: 0.06, green: 0.92, blue: 0.12, alpha: 1)

private struct Frames: PreferenceKey {
    static var defaultValue: [String:CGRect] { [:] }
    static func reduce(value: inout [String:CGRect], nextValue: () -> [String:CGRect]) {
        value.merge(nextValue()) { _, v in v }
    }
}
private extension View {
    func measure(_ id: String) -> some View {
        background(GeometryReader { g in Color.clear.preference(key: Frames.self,value: [id:g.frame(in:.global)]) })
    }
}
@MainActor private final class Driver: ObservableObject {
    @Published var show = false
    var boxes: [String:CGRect] = [:]
    var selected: Int?
}
private struct SwiftList: View {
    @ObservedObject var driver: Driver
    var body: some View {
        List(0..<count,id: \.self) { i in
            HStack {
                Button { driver.selected=i } label: { Text((training ? "Chapter " : "Episode ")+String(i)) }
                    .buttonStyle(.borderless)
                Spacer()
                Button { driver.show=true } label: {
                    Image(systemName:"info.circle").frame(width:40,height:36)
                        .background(Color(uiColor:probe("a",i) ?? accColor)).contentShape(Rectangle())
                }.buttonStyle(.borderless).measure("a"+String(i))
            }
            .padding(.horizontal,12).frame(height:height).background(Color(uiColor:color(i)))
            .measure("r"+String(i)).listRowInsets(EdgeInsets()).listRowSeparator(.hidden)
        }
        .listStyle(.plain).onPreferenceChange(Frames.self) { driver.boxes=$0 }
        .sheet(isPresented:$driver.show) {
            Group {
                if study && material != "system" {
                    Text("Details").frame(maxWidth:.infinity,maxHeight:.infinity,alignment:.top)
                        .background(StudySurface()).presentationBackground(.clear)
                } else {
                    Text("Details").frame(maxWidth:.infinity,maxHeight:.infinity,alignment:.top)
                        .presentationBackground(Color(uiColor:glass))
                }
            }
                .presentationDetents(lowSheet ? [.height(260)] : [.medium]).presentationDragIndicator(.hidden)
        }
    }
}
@MainActor private final class Table: UITableViewController {
    override func viewDidLoad() {
        super.viewDidLoad();tableView.rowHeight=height;tableView.estimatedRowHeight=0
        tableView.separatorStyle = .none
    }
    override func tableView(_ tableView:UITableView,numberOfRowsInSection section:Int)->Int {count}
    override func tableView(_ tableView:UITableView,cellForRowAt path:IndexPath)->UITableViewCell {
        let cell=UITableViewCell(style:.default,reuseIdentifier:nil);cell.backgroundColor=color(path.row)
        cell.textLabel?.text=(training ? "Chapter " : "Episode ")+String(path.row)
        let b=UIButton(type:.infoLight);b.frame=CGRect(x:0,y:0,width:40,height:36);b.backgroundColor=probe("a",path.row) ?? accColor
        b.addAction(UIAction { [weak self] _ in self?.openSheet() },for:.touchUpInside)
        cell.accessoryView=b;return cell
    }
    func openSheet() {
        let vc=UIViewController();vc.view.backgroundColor=glass
        if study && material != "system" {
            let body=UIView();body.backgroundColor = .clear
            if material=="thin" || material=="thick" {
                let blur=UIVisualEffectView(effect:UIBlurEffect(style:material=="thin" ? .systemUltraThinMaterial : .systemThickMaterial))
                blur.frame=body.bounds;blur.autoresizingMask=[.flexibleWidth,.flexibleHeight];body.addSubview(blur)
            }
            let tint=UIView();tint.backgroundColor=glass;tint.frame=body.bounds
            tint.autoresizingMask=[.flexibleWidth,.flexibleHeight];body.addSubview(tint);vc.view=body
        }
        vc.modalPresentationStyle = .pageSheet;vc.sheetPresentationController?.detents = lowSheet ? [.custom { _ in 260 }] : [.medium()]
        present(vc,animated:true)
    }
}
@main final class App: UIResponder,UIApplicationDelegate {
    func application(_ application:UIApplication,configurationForConnecting session:UISceneSession,options:UIScene.ConnectionOptions)->UISceneConfiguration {
        let cfg=UISceneConfiguration(name:nil,sessionRole:session.role);cfg.delegateClass=Scene.self;return cfg
    }
}
@MainActor private final class Scene: UIResponder,UIWindowSceneDelegate {
    var window:UIWindow?
    let driver=Driver();let table=Table(style:.plain)
    var phase="initial"
    var trace:[[String:Any]]=[]
    var link:CADisplayLink?
    let epoch=ProcessInfo.processInfo.systemUptime
    func scene(_ scene:UIScene,willConnectTo session:UISceneSession,options:UIScene.ConnectionOptions) {
        guard let scene=scene as? UIWindowScene else{return}
        let w=UIWindow(windowScene:scene);self.window=w
        w.rootViewController=isSwift ? UIHostingController(rootView:SwiftList(driver:driver)) : table
        w.makeKeyAndVisible()
        let dl=CADisplayLink(target:self,selector:#selector(tick));dl.preferredFramesPerSecond=30
        dl.add(to:.main,forMode:.common);link=dl
        // Slow this research window's animation clock to sample multiple compositor frames.
        w.layer.speed=study ? 1 : 0.22
        Task {
            try? await Task.sleep(for:.seconds(study ? 1.8 : 3))
            phase="opening"; if isSwift {driver.show=true} else {table.openSheet()}
            if study {
                try? await Task.sleep(for:.seconds(1.4));writeTrace()
                try? await Task.sleep(for:.seconds(5))
            } else { try? await Task.sleep(for:.seconds(6)) }
            phase="closing";if isSwift {driver.show=false} else {table.dismiss(animated:true)}
            try? await Task.sleep(for:.seconds(4))
            link?.invalidate();writeTrace()
        }
    }
    @objc func tick() {
        guard let w=window,let root=w.rootViewController else{return}
        let modal=root.presentedViewController
        let surface=modal?.presentationController?.presentedView
        func rect(_ b:CGRect)->[Double]{[b.minX,b.minY,b.maxX,b.maxY]}
        var native=driver.boxes
        if !isSwift {
            for cell in table.tableView.visibleCells {
                guard let i=table.tableView.indexPath(for:cell)?.row,let b=cell.accessoryView else{continue}
                native["r"+String(i)]=cell.convert(cell.bounds,to:w);native["a"+String(i)]=b.convert(b.bounds,to:w)
            }
        }
        var row:[String:Any]=["t":ProcessInfo.processInfo.systemUptime,"phase":phase,"geometry":native.mapValues(rect),
            "scale":w.screen.scale,"modal":modal != nil]
        if let surface,let layer=surface.layer.presentation(),let win=w.layer.presentation(){
            row["surface"]=rect(layer.convert(layer.bounds,to:win))
        }
        trace.append(row)
    }
    func writeTrace() {
        let u=FileManager.default.urls(for:.documentDirectory,in:.userDomainMask)[0].appendingPathComponent("trace.json")
        try? JSONSerialization.data(withJSONObject:trace).write(to:u,options:.atomic)
    }
}

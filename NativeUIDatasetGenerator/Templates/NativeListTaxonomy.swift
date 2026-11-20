import SwiftUI
import UIKit

// Solid row backgrounds provide independent pixel landmarks in these calibration scenes.
struct ListRect608: Equatable {
    let id: Int
    let frame: CGRect
    let caption: CGRect
}
private struct RowFrames608: PreferenceKey {
    static var defaultValue: [Int: CGRect] { [:] }
    static func reduce(value: inout [Int: CGRect], nextValue: () -> [Int: CGRect]) {
        value.merge(nextValue()) { _, latest in latest }
    }
}
private extension View {
    func observe608(_ index: Int) -> some View {
        background(GeometryReader { geo in
            Color.clear.preference(key: RowFrames608.self, value: [index: geo.frame(in: .global)])
        })
    }
}
enum ListColors608 {
    static func color(_ i: Int, training: Bool = false) -> UIColor {
        if training { return UIColor(white: i.isMultiple(of: 2) ? 0.19 : 0.24, alpha: 1) }
        return
        UIColor(red: CGFloat(52 + 18*i)/255, green: CGFloat(146 - 8*i)/255, blue: CGFloat(70 + 13*i)/255, alpha: 1)
    }
}

struct ListCover608: View {
    var body: some View { Rectangle().fill(Color(uiColor: .magenta)).accessibilityHidden(true) }
}

struct SwiftList608: View {
    let training: Bool
    let height: CGFloat
    let observe: ([Int:CGRect]) -> Void
    var body: some View {
        List(0..<12, id: \.self) { i in
            HStack {
                Text(training ? ["Downloads", "Saved albums", "Recently played", "Favorites"][i % 4] : "Library item " + String(i)).foregroundStyle(.white).observe608(100+i)
                Spacer()
            }
            .padding(.horizontal, 12).frame(height: height)
            .background(Color(uiColor: ListColors608.color(i, training: training)))
            .observe608(i)
            .listRowInsets(EdgeInsets())
            .listRowSeparator(.hidden)
        }
        .listStyle(.plain)
        .environment(\.defaultMinListRowHeight, height)
        .scrollIndicators(.hidden)
        .onPreferenceChange(RowFrames608.self, perform: observe)
    }
}

@MainActor
final class UIKitList608: UITableViewController {
    var training = false
    override func viewDidLoad() {
        super.viewDidLoad()
        tableView.separatorStyle = .none
        tableView.rowHeight = training ? 61 : 52
        tableView.estimatedRowHeight = 0
        tableView.contentInsetAdjustmentBehavior = .never
        tableView.showsVerticalScrollIndicator = false
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "item")
    }
    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int { 12 }
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "item", for: indexPath)
        cell.textLabel?.text = training ? ["Downloads", "Saved albums", "Recently played", "Favorites"][indexPath.row % 4] : "Library item " + String(indexPath.row)
        cell.textLabel?.textColor = .white
        cell.backgroundColor = ListColors608.color(indexPath.row, training: training)
        return cell
    }
}

struct AccessoryList609: View {
    var accessoryInset: CGFloat = 0
    let training: Bool
    @State private var selected: Int?
    @Binding var presented: Bool
    let observe: ([Int:CGRect]) -> Void
    var body: some View {
        List(0..<6, id: \.self) { i in
            HStack {
                Button { selected = i } label: {
                    Text((training ? "Chapter " : "Episode ") + String(i)).frame(maxWidth: .infinity, alignment: .leading)
                }.buttonStyle(.borderless).accessibilityIdentifier("row-action-"+String(i))
                Button { presented = true } label: {
                    Image(systemName: "info.circle").frame(width: 44, height: 44).contentShape(Rectangle())
                }.buttonStyle(.borderless).accessibilityIdentifier("info-"+String(i)).observe608(100+i).padding(.trailing, accessoryInset)
            }.frame(height: training ? 64 : 52).background(training ? Color(white: i.isMultiple(of: 2) ? 0.17 : 0.25) : Color.clear).observe608(i)
                .listRowInsets(EdgeInsets())
        }.listStyle(.plain)
            .onPreferenceChange(RowFrames608.self, perform: observe)
            .sheet(isPresented: $presented) {
                VStack { Text("Episode information"); Spacer() }
                    .frame(maxWidth: .infinity).background(Color.white)
                    .presentationDetents([.medium]).presentationDragIndicator(.hidden)
            }
    }
}

@MainActor
final class AccessoryTable609: UITableViewController {
    var accessoryInset: CGFloat = 0
    var training = false
    private(set) var selected: Int?
    override func tableView(_ tableView: UITableView, didSelectRowAt path: IndexPath) { selected = path.row }
    var action: (() -> Void)?
    override func viewDidLoad() {
        super.viewDidLoad()
        tableView.rowHeight = training ? 64 : 52
        tableView.estimatedRowHeight = 0
    }
    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int { 6 }
    override func tableView(_ tableView: UITableView, cellForRowAt path: IndexPath) -> UITableViewCell {
        let cell = UITableViewCell(style: .default, reuseIdentifier: nil)
        cell.textLabel?.text = (training ? "Chapter " : "Episode ") + String(path.row)
        if training { cell.backgroundColor = UIColor(white: path.row.isMultiple(of: 2) ? 0.17 : 0.25, alpha: 1) }
        let action = UIButton(type: .infoLight)
        action.frame = CGRect(x: 0,y: 0,width: 44,height: 44)
        action.addAction(UIAction { [weak self] _ in self?.action?() }, for: .touchUpInside)
        if accessoryInset > 0 {
            let container = UIView(frame: CGRect(x: 0, y: 0, width: 44 + accessoryInset, height: 44))
            container.addSubview(action)
            cell.accessoryView = container
        } else {
            cell.accessoryView = action
        }
        return cell
    }
}

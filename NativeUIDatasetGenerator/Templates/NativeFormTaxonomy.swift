import UIKit
import SwiftUI

// Native training recipe. Instance names are supplied by the caller.
struct FormObservation607: Equatable {
    let id: String
    let primitive: String
    let framework: String
    let owner: String?
    let secure: Bool
    let frame: CGRect
}

private struct FormFacts607: PreferenceKey {
    static var defaultValue: [FormObservation607] { [] }
    static func reduce(value: inout [FormObservation607], nextValue: () -> [FormObservation607]) {
        value.append(contentsOf: nextValue())
    }
}

private extension View {
    func observeFormBody(_ id: String, primitive: String, owner: String? = nil) -> some View {
        background(GeometryReader { geometry in
            Color.clear.preference(key: FormFacts607.self, value: [
                FormObservation607(id: id, primitive: primitive, framework: "SwiftUI", owner: owner,
                                   secure: primitive == "SecureField", frame: geometry.frame(in: .global))
            ])
        })
    }
}

struct InstrumentedLoginForm607: View {
    let ids: [String]
    let title: String
    let observe: ([FormObservation607]) -> Void
    @State private var email = ""
    @State private var password = ""

    private func input(_ field: TextField<Text>, id: String) -> some View {
        field.textFieldStyle(.roundedBorder).observeFormBody(id, primitive: "TextField")
    }

    private func input(_ field: SecureField<Text>, id: String) -> some View {
        field.textFieldStyle(.roundedBorder).observeFormBody(id, primitive: "SecureField")
    }

    private func caption(_ text: Text, id: String, owner: String? = nil) -> some View {
        text.observeFormBody(id, primitive: "Text", owner: owner)
    }

    private func action(_ label: String, id: String, child: String, filled: Bool) -> some View {
        Button(action: {}) {
            caption(Text(label), id: child, owner: id)
                .frame(maxWidth: .infinity, minHeight: 44)
                .background(filled ? Color.blue : Color.clear)
                .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .observeFormBody(id, primitive: "Button")
    }

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 12) {
                caption(Text("Email"), id: ids[4])
                input(TextField("Email", text: $email), id: ids[0])
                caption(Text("Password"), id: ids[5])
                input(SecureField("Password", text: $password), id: ids[1])
                action(title, id: ids[2], child: ids[6], filled: true)
                action("Create account", id: ids[3], child: ids[7], filled: false)
                Spacer()
            }
            .padding(24)
            .navigationTitle("Account")
        }
        .captureFrame(id: "diagnosticCanvas")
        .onPreferenceChange(FormFacts607.self, perform: observe)
    }
}

extension UIKitFormViewController {
    /// Read the instantiated controls and label ownership after layout.
    func formObservations607(ids: [String]) throws -> [FormObservation607] {
        let native = annotatedViews.compactMap { $0.view }
        let fields = native.compactMap { $0 as? UITextField }
        let actions = native.compactMap { $0 as? UIButton }
        let labels = native.compactMap { $0 as? UILabel }
        let bars = view.subviews.compactMap { $0 as? UINavigationBar }
        guard fields.count == 2, actions.count == 2, labels.count == 2, bars.count == 1,
              let first = actions[0].titleLabel, let second = actions[1].titleLabel else {
            throw CocoaError(.fileReadCorruptFile)
        }
        let views: [UIView] = [fields[0], fields[1], actions[0], actions[1], labels[0], labels[1], first, second, bars[0]]
        return try zip(ids, views).map { id, v in
            let primitive: String
            switch v {
            case is UITextField: primitive = "UITextField"
            case is UIButton: primitive = "UIButton"
            case is UINavigationBar: primitive = "UINavigationBar"
            case is UILabel: primitive = "UILabel"
            default: throw CocoaError(.fileReadCorruptFile)
            }
            var frame = v.convert(v.bounds, to: view)
            var ancestor: UIView? = v
            while let current = ancestor {
                guard !current.isHidden && current.alpha > 0.01 else { throw CocoaError(.fileReadCorruptFile) }
                if current.clipsToBounds { frame = frame.intersection(current.convert(current.bounds, to: view)) }
                ancestor = current.superview
            }
            let owner = v.isDescendant(of: actions[0]) ? ids[2] : v.isDescendant(of: actions[1]) ? ids[3] : nil
            return FormObservation607(id: id, primitive: primitive, framework: "UIKit",
                                      owner: v is UILabel ? owner : nil,
                                      secure: (v as? UITextField)?.isSecureTextEntry ?? false,
                                      frame: frame.intersection(view.bounds))
        }
    }
}

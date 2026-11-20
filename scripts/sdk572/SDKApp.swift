#if os(tvOS)
import UIKit
import TTRDiagnostics
import TTRDiagnosticsUI
import TTRDiagnosticsLink
import TTRDiagnosticsClient
import TTRDiagnosticsQuery

// Run-scoped native observations. These are not complete semantic annotations.
@MainActor final class SDKApp572 {
    static let shared = SDKApp572()
    let recorder: UIRecorder
    private var server: SDKLocalProbeServer?
    private var identities: [ObjectIdentifier: UIElementIdentity] = [:]
    private var nextIdentity = 0
    private var started = false
    private init() {
        #if DEBUG
        let allowed = true
        #else
        let allowed = false
        #endif
        let configuration = (try? SDKLaunchConfiguration.parse(arguments: ProcessInfo.processInfo.arguments)
            .applyingAppPolicy(diagnosticsAllowed: allowed)) ?? (try! SDKLaunchConfiguration(enabled: false))
        recorder = UIRecorder(configuration: configuration)
    }
    private func window() -> UIWindow? {
        let windows = UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }.flatMap(\.windows)
        return windows.first(where: { $0.isKeyWindow && !$0.isHidden })
    }
    private func register(_ root: UIView, window: UIWindow, seen: inout Set<ObjectIdentifier>) {
        guard !root.isHidden, root.alpha > 0.01 else { return }
        if root.canBecomeFocused && root.bounds.width > 0 && root.bounds.height > 0 {
            let key = ObjectIdentifier(root)
            let identity: UIElementIdentity
            if let existing = identities[key] { identity = existing }
            else {
                nextIdentity += 1
                identity = .init(id: "native-view-\(nextIdentity)")
                identities[key] = identity
            }
            seen.insert(key)
            let rect = root.convert(root.bounds, to: window)
            let origin = window.convert(CGPoint.zero, to: window.screen.coordinateSpace)
            let x = window.convert(CGPoint(x: 1, y: 0), to: window.screen.coordinateSpace)
            let y = window.convert(CGPoint(x: 0, y: 1), to: window.screen.coordinateSpace)
            let transform = [Double(x.x-origin.x), Double(x.y-origin.y), Double(y.x-origin.x), Double(y.y-origin.y), Double(origin.x), Double(origin.y)]
            let screen = window.screen.bounds
            var element = UIElement(identity: identity,
                bounds: .init(x: rect.minX, y: rect.minY, width: rect.width, height: rect.height), coordinateSpace: .windowPoints)
            element.className = String(describing: type(of: root))
            element.hidden = root.isHidden
            element.captureGeometry = .init(windowID: String(describing: ObjectIdentifier(window)),
                sceneID: window.windowScene?.session.persistentIdentifier ?? "unavailable",
                screenBounds: .init(x: screen.minX, y: screen.minY, width: screen.width, height: screen.height),
                displayScale: window.screen.scale, toScreenPoints: transform, source: "native-window-transform-v1",
                native: .observe(window: window, toScreenPoints: transform))
            do { try recorder.register(element) }
            catch { print("REAL543_SDK registration failed: \(error)") }
        }
        for child in root.subviews { register(child, window: window, seen: &seen) }
    }
    private func state(source: String) -> SDKLiveProbe.State {
        guard let window = window() else { return .init(focusID: nil, focusKnown: false, interrupted: true, captureSourceID: source) }
        var seen: Set<ObjectIdentifier> = []
        register(window, window: window, seen: &seen)
        let removed = identities.keys.filter { !seen.contains($0) }
        for key in removed { if let identity = identities.removeValue(forKey: key) { recorder.unregister(identity) } }
        let sample = UIFocusSample.sample(view: window) { item in
            guard let view = item as? UIView else { return nil }
            return self.identities[ObjectIdentifier(view)]?.id
        }
        return .init(sample: sample, interrupted: UIApplication.shared.applicationState != .active, captureSourceID: source)
    }
    func start() async {
        guard recorder.enabled, !started else { return }
        started = true
        do {
            let environment = ProcessInfo.processInfo.environment
            guard let key = environment["TTR_SAMPLE_KEY"].flatMap({ Data(base64Encoded: $0) }), key.count == 32,
                  let source = environment["SIMULATOR_UDID"], UUID(uuidString: source) != nil else { return }
            let archive = try DiagnosticArchive.decode(await recorder.exportData())
            let enrollment = try Enrollment(appID: Bundle.main.bundleIdentifier!, processID: archive.processID, runID: archive.runID, secret: key)
            let probe = SDKLiveProbe(recorder: recorder, enrollment: enrollment) { self.state(source: source) }
            let listener = try SDKLocalProbeServer(port: 8097) { try await probe.reply(to: $0) }
            server = listener
            let endpoint = try await listener.start(lifetimeSeconds: 800)
            let identity = ["appID": enrollment.appID, "processID": archive.processID.uuidString,
                "runID": archive.runID.uuidString, "endpoint": endpoint.absoluteString]
            print("REAL543_SDK " + String(decoding: try JSONSerialization.data(withJSONObject: identity), as: UTF8.self))
            fflush(stdout)
        } catch { print("REAL543_SDK failed: \(error)"); fflush(stdout) }
    }
}
#endif

import XCTest
import CryptoKit

/// Opt-in simulator integration probe; never part of ordinary offline package tests.
final class NativeOSFocusTests: XCTestCase {
    /// REAL550: one predetermined NewsTV screen. No navigation or model inference.
    @MainActor
    func testNewsTVPilotInitial() throws {
        continueAfterFailure = false
        let app = XCUIApplication(bundleIdentifier: "com.jordankoch.NewsTV")
        app.launchArguments = ["--real543-controlled-content"]
        defer {
            app.terminate()
            let cleanup = XCTAttachment(string: "terminated=\(app.state == .notRunning); inputs=0; requestedCaptures=1")
            cleanup.name = "newstv-cleanup"
            cleanup.lifetime = .keepAlways
            add(cleanup)
        }
        app.launch()
        XCTAssertTrue(app.wait(for: .runningForeground, timeout: 15), "NewsTV must be foreground before capture")
        let before = app.debugDescription
        let image = XCUIScreen.main.screenshot()
        XCTAssertEqual(app.state, .runningForeground)
        let after = app.debugDescription
        let reference = XCTAttachment(string: "case=newstv-news-home-initial; role=pilot-pending-review; modelPredictionsViewed=false; sdkEvidence=unavailable\nBEFORE\n" + before + "\nAFTER\n" + after)
        reference.name = "newstv-initial-native-reference"
        reference.lifetime = .keepAlways
        add(reference)
        let screenshot = XCTAttachment(screenshot: image)
        screenshot.name = "newstv-news-home-initial"
        screenshot.lifetime = .keepAlways
        add(screenshot)
    }

    /// Activates an already enrolled NewsTV process for read-only SDK observations.
    @MainActor
    func testNewsTVActivateExisting() throws {
        continueAfterFailure = false
        let app = XCUIApplication(bundleIdentifier: "com.jordankoch.NewsTV")
        XCTAssertNotEqual(app.state, .notRunning, "The host must enroll NewsTV before this test")
        app.activate()
        XCTAssertTrue(app.wait(for: .runningForeground, timeout: 15))
        // The host collects authenticated SDK observations during this bounded interval.
        let stable = NSPredicate { _, _ in app.state == .runningForeground }
        XCTAssertTrue(stable.evaluate(with: app))
        RunLoop.current.run(until: Date().addingTimeInterval(12))
        XCTAssertEqual(app.state, .runningForeground)
        let native = XCTAttachment(string: app.debugDescription)
        native.name = "newstv-sdk-active-native-reference"
        native.lifetime = .keepAlways
        add(native)
        let screenshot = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        screenshot.name = "newstv-sdk-active-initial"
        screenshot.lifetime = .keepAlways
        add(screenshot)
        // The enrolling host owns termination and records cleanup.
    }

    struct Node: Codable, Equatable, Sendable {
        let identifier: String
        let label: String
        let kind: UInt
        let bounds: [Double]
        let focused: Bool
    }

    struct Observation: Codable, Sendable {
        let timestamp: Double
        let viewportPoints: [Double]
        let nodes: [Node]
        let focus: Node
    }

    struct Frame: Encodable, Sendable {
        let version = "native-os-focus-observation-v2"
        let sourceKind = "tvos_simulator_os"
        let eligibility = "development-review-required"
        let screenID: String
        let name: String
        let action: String
        let pngSHA256: String
        let pixelDimensions: [Int]
        let captureStartedAt: Double
        let captureEndedAt: Double
        let before: Observation
        let after: Observation
    }

    enum ProbeError: Error { case context, missingFocus, unsettled, noFocusChange, deadline }

    // MARK: TRAIN666 — passive accessibility snapshot for benchmark drafts

    /// 1 accessibility element with the facts a label draft needs. `kind` is `XCUIElement.ElementType.rawValue`.
    struct AXNode: Codable, Equatable, Sendable {
        let identifier: String
        let label: String
        let kind: UInt
        let bounds: [Double]
        let focused: Bool
        let enabled: Bool
        let selected: Bool
        let depth: Int
        let parent: Int
    }

    struct AXSnapshot: Encodable, Sendable {
        let version = "tvos-ax-snapshot-v1"
        let sourceKind = "tvos_simulator_xcuitest"
        let eligibility = "draft-review-required"
        let bundleIdentifier: String
        let screenID: String
        let pngSHA256: String
        let pixelDimensions: [Int]
        let viewportPoints: [Double]
        let captureStartedAt: Double
        let captureEndedAt: Double
        let settled: Bool
        /// focused: exactly 1 focused element. none_observed: 0 (not proof of no focus). ambiguous: more than 1.
        let focusState: String
        let nodes: [AXNode]
        let inputsSent = 0
    }

    @MainActor
    private func axNodes(_ app: XCUIApplication) throws -> (nodes: [AXNode], viewport: CGRect) {
        let root = try app.snapshot()
        var nodes: [AXNode] = []
        func walk(_ snapshot: any XCUIElementSnapshot, depth: Int, parent: Int) {
            let box = snapshot.frame
            var index = parent
            if !box.isEmpty, !box.isNull, !box.isInfinite, root.frame.intersects(box) {
                index = nodes.count
                nodes.append(AXNode(identifier: snapshot.identifier, label: snapshot.label, kind: snapshot.elementType.rawValue,
                                    bounds: [box.minX, box.minY, box.width, box.height], focused: snapshot.hasFocus,
                                    enabled: snapshot.isEnabled, selected: snapshot.isSelected, depth: depth, parent: parent))
            }
            for child in snapshot.children { walk(child, depth: depth + 1, parent: index) }
        }
        walk(root, depth: 0, parent: -1)
        return (nodes, root.frame)
    }

    private static let forbiddenSelect = try! NSRegularExpression(
        pattern: #"\b(Reset|Erase|Format|Updates?|Delete|Remove|Pair|Learn|Bluetooth|Restrictions|Firewall|Sign Out|Sign In|Add Profile|Add New|Purchase|Buy|Restore|Terms|Agree|Offload|Restart|Sleep|Calibrate|Check HDMI|Connect|Log ?in|Subscribe)\b"#,
        options: [.caseInsensitive])

    @MainActor
    private func axSettle(_ app: XCUIApplication, seconds: Double = 8) throws -> (nodes: [AXNode], viewport: CGRect, settled: Bool) {
        var before = try axNodes(app)
        let until = Date().addingTimeInterval(seconds)
        while Date() < until {
            Thread.sleep(forTimeInterval: 0.3)
            let next = try axNodes(app)
            if next.nodes == before.nodes { return (next.nodes, next.viewport, true) }
            before = next
        }
        return (before.nodes, before.viewport, false)
    }

    /// Settle, take 1 screenshot with a before/after accessibility bracket, and attach PNG + JSON. Returns the nodes.
    @MainActor
    @discardableResult
    private func axCapture(_ app: XCUIApplication, bundle: String, screenID: String) throws -> [AXNode] {
        let before = try axSettle(app)
        let started = Date().timeIntervalSince1970
        let screenshot = XCUIScreen.main.screenshot()
        let ended = Date().timeIntervalSince1970
        let after = try axNodes(app)
        let pixels = screenshot.pngRepresentation
        guard let cgImage = screenshot.image.cgImage else { throw ProbeError.context }
        let image = XCTAttachment(screenshot: screenshot)
        image.name = screenID + ".png"
        image.lifetime = .keepAlways
        add(image)
        let focusCount = after.nodes.filter(\.focused).count
        let record = AXSnapshot(
            bundleIdentifier: bundle, screenID: screenID,
            pngSHA256: SHA256.hash(data: pixels).map { String(format: "%02x", $0) }.joined(),
            pixelDimensions: [cgImage.width, cgImage.height],
            viewportPoints: [after.viewport.minX, after.viewport.minY, after.viewport.width, after.viewport.height],
            captureStartedAt: started, captureEndedAt: ended,
            settled: before.settled && before.nodes == after.nodes,
            focusState: focusCount == 1 ? "focused" : focusCount == 0 ? "none_observed" : "ambiguous",
            nodes: after.nodes)
        let sidecar = XCTAttachment(data: try JSONEncoder().encode(record), uniformTypeIdentifier: "public.json")
        sidecar.name = screenID + ".json"
        sidecar.lifetime = .keepAlways
        add(sidecar)
        return after.nodes
    }

    /// TRAIN666 routed benchmark capture. Environment (prefix each with `TEST_RUNNER_` for xcodebuild):
    /// `AX_BUNDLE` app to activate; `AX_SCREEN` screen identifier; `AX_ROUTE` labels to select in order, separated by `|`
    /// (optional); `AX_SWEEP` such as `down:10,right:6` (optional). Rules: 1 input at a time with a settled observation
    /// after each; Select only on an enabled element whose label equals the route label and passes the blacklist;
    /// 1 Menu press per completed Select at the end; never Home; at most 60 inputs and 240 s.
    @MainActor
    func testRoutedSnapshot() throws {
        continueAfterFailure = false
        let env = ProcessInfo.processInfo.environment
        guard let bundle = env["AX_BUNDLE"], !bundle.isEmpty else { throw XCTSkip("AX_BUNDLE is not set") }
        let screenID = env["AX_SCREEN"] ?? "unnamed"
        let route = (env["AX_ROUTE"] ?? "").split(separator: "|").map(String.init).filter { !$0.isEmpty }
        let sweeps: [(XCUIRemote.Button, Int, String)] = (env["AX_SWEEP"] ?? "").split(separator: ",").compactMap { part in
            let bits = part.split(separator: ":")
            guard bits.count == 2, let count = Int(bits[1]), count >= 0, count <= 20 else { return nil }
            switch bits[0] {
            case "down": return (.down, count, "down")
            case "up": return (.up, count, "up")
            case "left": return (.left, count, "left")
            case "right": return (.right, count, "right")
            default: return nil
            }
        }
        let deadline = Date().addingTimeInterval(240)
        let maxInputs = 60
        var inputs = 0, selects = 0, menus = 0, frames = 0
        var stop = "completed"
        let app = XCUIApplication(bundleIdentifier: bundle)
        app.activate()
        guard app.wait(for: .runningForeground, timeout: 15) else { throw ProbeError.context }
        defer {
            let text = "inputs=\(inputs); selects=\(selects); menus=\(menus); frames=\(frames); stop=\(stop); foreground=\(app.state == .runningForeground); bundle=\(bundle); screenID=\(screenID); route=\(route.joined(separator: "|"))"
            let attachment = XCTAttachment(string: text)
            attachment.name = "terminal-context"
            attachment.lifetime = .keepAlways
            add(attachment)
        }
        func focusKey(_ nodes: [AXNode]) -> String {
            nodes.filter(\.focused).map { "\($0.label)|\($0.identifier)|\($0.bounds)" }.joined(separator: ";")
        }
        func press(_ button: XCUIRemote.Button) throws {
            guard inputs < maxInputs, Date() < deadline else { stop = "budget"; throw ProbeError.deadline }
            guard app.state == .runningForeground, app.alerts.count == 0 else { stop = "context"; throw ProbeError.context }
            XCUIRemote.shared.press(button)
            inputs += 1
        }
        // Check every route label before any input, so a refusal never leaves the app inside a submenu.
        for label in route {
            let range = NSRange(label.startIndex..., in: label)
            guard Self.forbiddenSelect.firstMatch(in: label, range: range) == nil else { stop = "blacklisted:\(label)"; throw ProbeError.context }
        }
        // `AX_MENU_FIRST=n` (n <= 2): recover from an earlier stop inside a submenu. Menu at the root can background the app,
        // so the app is activated again afterwards. Never Home.
        if let pre = Int(env["AX_MENU_FIRST"] ?? "0"), pre > 0, pre <= 2 {
            for _ in 0..<pre { XCUIRemote.shared.press(.menu); inputs += 1; menus += 1; _ = try? axSettle(app, seconds: 4) }
            app.activate()
            guard app.wait(for: .runningForeground, timeout: 15) else { throw ProbeError.context }
        }
        // Route: move focus to each label with closed-loop single steps, then Select once.
        // If the route stops part-way, return 1 level per completed Select before the error leaves the test.
        var routeDone = false
        defer {
            if !routeDone, env["AX_NO_RETURN"] != "1" {
                for _ in 0..<selects where app.state == .runningForeground {
                    XCUIRemote.shared.press(.menu); inputs += 1; menus += 1; Thread.sleep(forTimeInterval: 1.5)
                }
            }
        }
        for label in route {
            var state = try axSettle(app)
            var steps = 0
            while true {
                guard let focus = state.nodes.first(where: \.focused) else { stop = "no_focus_on_route"; throw ProbeError.missingFocus }
                let focusedSubtree = state.nodes.enumerated().first(where: { $0.element.focused })?.offset ?? -1
                let onTarget = focus.label == label || state.nodes.enumerated().contains { idx, n in
                    n.label == label && n.parent == focusedSubtree && idx > focusedSubtree }
                if onTarget { guard focus.enabled else { stop = "disabled:\(label)"; throw ProbeError.context }; break }
                guard steps < 25 else { stop = "route_label_not_reachable:\(label)"; throw ProbeError.context }
                // A row below the visible area has no on-screen element yet: step down until it appears.
                let button: XCUIRemote.Button
                if let target = state.nodes.first(where: { $0.label == label }) {
                    let dy = target.bounds[1] - focus.bounds[1], dx = target.bounds[0] - focus.bounds[0]
                    button = abs(dy) >= 20 ? (dy < 0 ? .up : .down) : (dx < 0 ? .left : .right)
                } else { button = .down }
                let key = focusKey(state.nodes)
                try press(button)
                steps += 1
                state = try axSettle(app)
                guard focusKey(state.nodes) != key else { stop = "route_blocked:\(label)"; throw ProbeError.noFocusChange }
            }
            try press(.select)
            selects += 1
            _ = try axSettle(app)
            guard app.state == .runningForeground else { stop = "left_app_after_select:\(label)"; throw ProbeError.context }
        }
        var nodes = try axCapture(app, bundle: bundle, screenID: screenID + "-00")
        frames += 1
        routeDone = true
        var seen: Set<String> = [focusKey(nodes)]
        sweep: for (button, count, name) in sweeps {
            for _ in 0..<count {
                guard inputs < maxInputs - selects, Date() < deadline else { stop = "budget"; break sweep }
                let key = focusKey(nodes)
                try press(button)
                let state = try axSettle(app)
                guard app.state == .runningForeground else { stop = "left_app"; break sweep }
                let next = focusKey(state.nodes)
                if next == key { break } // Boundary in this direction.
                nodes = state.nodes
                if seen.insert(next).inserted {
                    nodes = try axCapture(app, bundle: bundle, screenID: String(format: "%@-%02d-%@", screenID, frames, name))
                    frames += 1
                }
            }
        }
        // Verified return: 1 Menu per completed Select. Never Home.
        // `AX_NO_RETURN=1`: the Select changed a tab, not a navigation level, so Menu would leave the app.
        for _ in 0..<(env["AX_NO_RETURN"] == "1" ? 0 : selects) {
            guard app.state == .runningForeground else { break }
            XCUIRemote.shared.press(.menu)
            inputs += 1
            menus += 1
            _ = try axSettle(app, seconds: 5)
        }
    }

    /// Passive snapshot of the app that is already foreground. No activation, no launch and no remote input.
    /// Pass `TEST_RUNNER_AX_BUNDLE` (bundle identifier) and `TEST_RUNNER_AX_SCREEN` (screen identifier) to xcodebuild.
    /// The result is a draft for human review. It is never a training label or a reference by itself.
    @MainActor
    func testPassiveForegroundSnapshot() throws {
        continueAfterFailure = false
        let env = ProcessInfo.processInfo.environment
        guard let bundle = env["AX_BUNDLE"], !bundle.isEmpty else { throw XCTSkip("AX_BUNDLE is not set") }
        let screenID = env["AX_SCREEN"] ?? "unnamed"
        let app = XCUIApplication(bundleIdentifier: bundle)
        guard app.state == .runningForeground else { throw ProbeError.context }
        var before = try axNodes(app)
        var settled = false
        let until = Date().addingTimeInterval(10)
        while Date() < until {
            Thread.sleep(forTimeInterval: 0.3)
            let next = try axNodes(app)
            if next.nodes == before.nodes { settled = true; break }
            before = next
        }
        let started = Date().timeIntervalSince1970
        let screenshot = XCUIScreen.main.screenshot()
        let ended = Date().timeIntervalSince1970
        let after = try axNodes(app)
        let pixels = screenshot.pngRepresentation
        guard let cgImage = screenshot.image.cgImage else { throw ProbeError.context }
        let image = XCTAttachment(screenshot: screenshot)
        image.name = screenID + ".png"
        image.lifetime = .keepAlways
        add(image)
        let focusCount = after.nodes.filter(\.focused).count
        let record = AXSnapshot(
            bundleIdentifier: bundle, screenID: screenID,
            pngSHA256: SHA256.hash(data: pixels).map { String(format: "%02x", $0) }.joined(),
            pixelDimensions: [cgImage.width, cgImage.height],
            viewportPoints: [after.viewport.minX, after.viewport.minY, after.viewport.width, after.viewport.height],
            captureStartedAt: started, captureEndedAt: ended,
            settled: settled && before.nodes == after.nodes,
            focusState: focusCount == 1 ? "focused" : focusCount == 0 ? "none_observed" : "ambiguous",
            nodes: after.nodes)
        let sidecar = XCTAttachment(data: try JSONEncoder().encode(record), uniformTypeIdentifier: "public.json")
        sidecar.name = screenID + ".json"
        sidecar.lifetime = .keepAlways
        add(sidecar)
        XCTAssertEqual(app.state, .runningForeground)
    }

    @MainActor
    func testHomePassiveIdentity() throws {
        continueAfterFailure = false
        for bundle in ["com.apple.PineBoard", "com.apple.HeadBoard"] {
            let app = XCUIApplication(bundleIdentifier: bundle)
            let attachment = XCTAttachment(string: "state=\(app.state.rawValue)\n" + app.debugDescription)
            attachment.name = bundle
            attachment.lifetime = .keepAlways
            add(attachment)
        }
        let shot = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        shot.name = "passive-home.png"
        shot.lifetime = .keepAlways
        add(shot)
    }

    /// Bounded Home challenge segment. Every input has a retained native observation.
    @MainActor
    func testHomeChallengeSnake() throws {
        continueAfterFailure = false
        let deadline = Date().addingTimeInterval(300)
        // tvOS26.5 hosts the tile AX tree in HeadBoard, not PineBoard's shell.
        let app = XCUIApplication(bundleIdentifier: "com.apple.HeadBoard")
        var count = 0
        var completed = false
        var stop = "failure"
        defer {
            let attachment = XCTAttachment(string: "inputs=\(count); completed=\(completed); homeForeground=\(app.state == .runningForeground); screenID=home/root; stop=\(stop); originalContextRestored=false")
            attachment.name = "terminal-context"
            attachment.lifetime = .keepAlways
            add(attachment)
        }
        XCUIRemote.shared.press(.home) // Authorized setup, never a Settings crawl escape.
        guard app.wait(for: .runningForeground, timeout: 10) else { throw ProbeError.context }
        var previous = try capture(app, name: "000-start", action: "setup-home", deadline: deadline, screenID: "home/root")
        let tree = XCTAttachment(string: app.debugDescription)
        tree.name = "home-setup-context"
        tree.lifetime = .keepAlways
        add(tree)
        var horizontal: XCUIRemote.Button = .left
        var label = "left"
        var seekingStart = true
        var descend = false
        while count < 40 {
            guard Date() < deadline else { throw ProbeError.deadline }
            let current = try stable(app, deadline: deadline)
            guard current.focus == previous.focus else { throw ProbeError.context }
            let button: XCUIRemote.Button = descend ? .down : horizontal
            let action = descend ? "down" : label
            XCUIRemote.shared.press(button)
            count += 1
            let next = try capture(app, name: String(format: "%03d", count), action: action, deadline: deadline, screenID: "home/root")
            let same = next.focus.identifier == previous.focus.identifier && next.focus.label == previous.focus.label
            if descend {
                if same { stop = "observed-down-boundary"; previous = next; break }
                descend = false
                horizontal = label == "left" ? .right : .left
                label = label == "left" ? "right" : "left"
            } else if same {
                if seekingStart { seekingStart = false; horizontal = .right; label = "right" }
                else { descend = true }
            }
            previous = next
        }
        _ = try observe(app)
        if stop == "failure" { stop = "budget-frontier" }
        completed = true // Complete bounded segment, NOT complete Home inventory.
    }

    @MainActor
    func testGeneralLearningSweep() throws { try submenuSweep("General", screenID: "settings/general", marker: "About") }

    @MainActor
    func testAccessibilityLearningSweep() throws { try submenuSweep("Accessibility", screenID: "settings/accessibility", marker: "Hover Text") }

    @MainActor
    func testAppsLearningSweep() throws { try submenuSweep("Apps", screenID: "settings/apps", marker: "Apps") }

    @MainActor
    func testRemotesChallengeSweep() throws { try submenuSweep("Remotes and Devices", screenID: "settings/remotes", marker: "Remotes and Devices") }

    @MainActor
    private func submenuSweep(_ title: String, screenID: String, marker: String) throws {
        continueAfterFailure = false
        let deadline = Date().addingTimeInterval(300)
        let app = XCUIApplication(bundleIdentifier: "com.apple.TVSettings")
        app.activate()
        guard app.wait(for: .runningForeground, timeout: 10) else { throw ProbeError.context }
        var setup = 0
        var count = 0
        var boundaries = 0
        var completed = false
        var returned = false
        defer {
            let result = "inputs=\(count); setupDirections=\(setup); boundaries=\(boundaries); completed=\(completed); settingsForeground=\(app.state == .runningForeground); returnedRoot=\(returned); screenID=\(screenID)"
            let attachment = XCTAttachment(string: result)
            attachment.name = "terminal-context"
            attachment.lifetime = .keepAlways
            add(attachment)
        }
        var root = try stable(app, deadline: deadline)
        if !root.nodes.contains(where: { $0.label == "Video and Audio" }),
           root.nodes.contains(where: { $0.label == title && $0.kind == XCUIElement.ElementType.staticText.rawValue }) {
            // Reconcile this operation's known submenu after a bounded prior stop.
            XCUIRemote.shared.press(.menu)
            root = try stable(app, deadline: deadline)
        }
        guard root.nodes.contains(where: { $0.label == "General" }),
              root.nodes.contains(where: { $0.label == "Video and Audio" }) else { throw ProbeError.context }
        while root.focus.label != title && setup < 15 {
            let candidates = root.nodes.filter { $0.kind == root.focus.kind && $0.label == title }
            guard candidates.count == 1 else { throw ProbeError.context }
            let direction: XCUIRemote.Button = candidates[0].bounds[1] < root.focus.bounds[1] ? .up : .down
            XCUIRemote.shared.press(direction)
            setup += 1
            root = try stable(app, deadline: deadline)
        }
        guard root.focus.label == title, try stable(app, deadline: deadline).nodes == root.nodes else { throw ProbeError.context }
        let entry = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        entry.name = "entry-review.png"
        entry.lifetime = .keepAlways
        add(entry)
        // Only named, reviewed root disclosure menus; never select their child rows.
        XCUIRemote.shared.press(.select)
        let child = try stable(app, deadline: deadline)
        guard child.nodes.contains(where: { $0.label == marker }),
              !child.nodes.contains(where: { $0.label == "Video and Audio" }) else { throw ProbeError.context }
        var previous = try capture(app, name: "000-start", action: "enter-" + title.lowercased(), deadline: deadline, screenID: screenID)
        for (button, label) in [(XCUIRemote.Button.up, "up"), (.down, "down")] {
            while count < 40 {
                guard Date() < deadline else { throw ProbeError.deadline }
                guard try stable(app, deadline: deadline).nodes == previous.nodes else { throw ProbeError.context }
                XCUIRemote.shared.press(button)
                count += 1
                let next = try capture(app, name: String(format: "%03d", count), action: label, deadline: deadline, screenID: screenID)
                let boundary = next.focus.identifier == previous.focus.identifier && next.focus.label == previous.focus.label
                previous = next
                if boundary { boundaries += 1; break }
            }
            if count == 40 { break }
        }
        guard boundaries == 2 else { throw ProbeError.deadline }
        _ = try observe(app)
        XCUIRemote.shared.press(.menu) // One verified-parent return; never a retry loop.
        let parent = try stable(app, deadline: deadline)
        returned = parent.nodes.contains(where: { $0.label == "Video and Audio" }) && parent.focus.label == title
        guard returned else { throw ProbeError.context }
        completed = true
    }

    /// Root-list development capture. Three boundary-seeking legs, never Select.
    @MainActor
    func testSettingsRootSweep() throws {
        continueAfterFailure = false
        let app = XCUIApplication(bundleIdentifier: "com.apple.TVSettings")
        let deadline = Date().addingTimeInterval(300)
        app.activate()
        guard app.wait(for: .runningForeground, timeout: 10) else { throw ProbeError.context }
        var count = 0
        var boundaries = 0
        var completed = false
        defer {
            let text = "inputs=\(count); boundaries=\(boundaries); completed=\(completed); settingsForeground=\(app.state == .runningForeground); originalContextRestored=false"
            let attachment = XCTAttachment(string: text)
            attachment.name = "terminal-context"
            attachment.lifetime = .keepAlways
            add(attachment)
        }
        var previous = try capture(app, name: "000-start", action: "activate-settings", deadline: deadline)
        // A remembered child screen is not the root; do not navigate back blindly.
        guard previous.nodes.contains(where: { $0.label == "General" }),
              previous.nodes.contains(where: { $0.label == "Video and Audio" }) else { throw ProbeError.context }
        for (button, label) in [(XCUIRemote.Button.up, "up"), (.down, "down"), (.up, "up")] {
            while count < 40 {
                guard Date() < deadline else { throw ProbeError.deadline }
                let current = try stable(app, deadline: deadline)
                guard current.nodes == previous.nodes else { throw ProbeError.context }
                XCUIRemote.shared.press(button)
                count += 1
                let next = try capture(app, name: String(format: "%03d", count), action: label, deadline: deadline)
                let boundary = next.focus.identifier == previous.focus.identifier && next.focus.label == previous.focus.label
                previous = next
                if boundary { boundaries += 1; break }
            }
            if count == 40 { break }
        }
        _ = try observe(app)
        completed = boundaries == 3
        // A budget stop is retained evidence, not a completed corpus.
        XCTAssertTrue(completed, "Root sweep exhausted its budget before all three boundaries")
    }

    @MainActor
    func testDirectionsOnlyFocusProbe() throws {
        continueAfterFailure = false
        let app = XCUIApplication(bundleIdentifier: "com.apple.TVSettings")
        let deadline = Date().addingTimeInterval(120)
        // Explicit setup activation, not proof of a Home-to-Settings route.
        app.activate()
        guard app.wait(for: .runningForeground, timeout: 10) else { throw ProbeError.context }
        let actions: [XCUIRemote.Button] = [.down, .down, .down, .up, .up, .up]
        var count = 0
        defer {
            let summary = "inputs=\(count); settingsForeground=\(app.state == .runningForeground); originalContextRestored=false"
            let attachment = XCTAttachment(string: summary)
            attachment.name = "terminal-context"
            attachment.lifetime = .keepAlways
            add(attachment)
        }
        var previous = try capture(app, name: "00-start", action: "activate-settings", deadline: deadline)
        for (index, button) in actions.enumerated() {
            guard Date() < deadline else { throw ProbeError.deadline }
            let current = try stable(app, deadline: deadline)
            guard current.focus == previous.focus else { throw ProbeError.context }
            XCUIRemote.shared.press(button)
            count += 1
            let next = try capture(app, name: String(format: "%02d", index + 1),
                                   action: index < 3 ? "down" : "up", deadline: deadline)
            guard next.focus.identifier != previous.focus.identifier || next.focus.label != previous.focus.label
                    else { throw ProbeError.noFocusChange }
            previous = next
        }
        _ = try observe(app) // Fresh postflight; does not reactivate an app to mask failure.
    }

    @MainActor
    private func observe(_ app: XCUIApplication) throws -> Observation {
        guard app.state == .runningForeground, app.alerts.count == 0 else { throw ProbeError.context }
        let root = try app.snapshot()
        var nodes: [Node] = []
        func walk(_ snapshot: any XCUIElementSnapshot) {
            let box = snapshot.frame
            if !box.isEmpty, !box.isNull, !box.isInfinite, root.frame.intersects(box) {
                nodes.append(Node(identifier: snapshot.identifier, label: snapshot.label,
                                  kind: snapshot.elementType.rawValue,
                                  bounds: [box.minX, box.minY, box.width, box.height], focused: snapshot.hasFocus))
            }
            for child in snapshot.children { walk(child) }
        }
        walk(root)
        let focus = nodes.filter(\.focused)
        guard focus.count == 1, let one = focus.first,
              !one.label.isEmpty || !one.identifier.isEmpty else { throw ProbeError.missingFocus }
        return Observation(timestamp: Date().timeIntervalSince1970,
                           viewportPoints: [root.frame.minX, root.frame.minY, root.frame.width, root.frame.height],
                           nodes: nodes, focus: one)
    }

    @MainActor
    private func stable(_ app: XCUIApplication, deadline: Date, homeContext: Bool = false) throws -> Observation {
        let until = min(deadline, Date().addingTimeInterval(10))
        var previous: Observation?
        while Date() < until {
            let current: Observation
            do { current = try observe(app) }
            catch ProbeError.missingFocus {
                previous = nil
                Thread.sleep(forTimeInterval: 0.2)
                continue // Observation-only settling; never replay a remote input.
            }
            catch ProbeError.context where homeContext && app.state != .runningForeground {
                previous = nil
                Thread.sleep(forTimeInterval: 0.2)
                continue // Home host activation can briefly change process state; no input.
            }
            if let previous, previous.nodes == current.nodes { return current }
            previous = current
            Thread.sleep(forTimeInterval: 0.2)
        }
        let diagnostic = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        diagnostic.name = "invalid-unsettled.png"
        diagnostic.lifetime = .keepAlways
        add(diagnostic)
        let tree = XCTAttachment(string: app.debugDescription)
        tree.name = "invalid-unsettled-context"
        tree.lifetime = .keepAlways
        add(tree)
        throw ProbeError.unsettled
    }

    @MainActor
    private func capture(_ app: XCUIApplication, name: String, action: String, deadline: Date, screenID: String = "settings/root") throws -> Observation {
        let before = try stable(app, deadline: deadline, homeContext: screenID == "home/root")
        let started = Date().timeIntervalSince1970
        let screenshot = XCUIScreen.main.screenshot()
        let ended = Date().timeIntervalSince1970
        let pixels = screenshot.pngRepresentation
        let image = XCTAttachment(screenshot: screenshot)
        image.name = name + ".png"
        image.lifetime = .keepAlways
        add(image)
        let after = try observe(app)
        guard let cgImage = screenshot.image.cgImage else { throw ProbeError.context }
        let hash = SHA256.hash(data: pixels).map { String(format: "%02x", $0) }.joined()
        let record = Frame(screenID: screenID, name: name, action: action, pngSHA256: hash,
                           pixelDimensions: [cgImage.width, cgImage.height],
                           captureStartedAt: started, captureEndedAt: ended, before: before, after: after)
        let json = try JSONEncoder().encode(record)
        let sidecar = XCTAttachment(data: json, uniformTypeIdentifier: "public.json")
        sidecar.name = name + ".json"
        sidecar.lifetime = .keepAlways
        add(sidecar)
        guard before.nodes == after.nodes else { throw ProbeError.unsettled }
        return after
    }
}

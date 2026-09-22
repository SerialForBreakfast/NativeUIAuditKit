import XCTest
import CryptoKit

/// Opt-in simulator integration probe; never part of ordinary offline package tests.
final class NativeOSFocusTests: XCTestCase {
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

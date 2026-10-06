// KitchenSinkValidationTest.swift
// GeneratorRunnerTests
//
// One-shot smoke test: generates a single KitchenSink image, draws labeled bounding
// boxes on it, and writes two files to Documents/debug/:
//
//   kitchen_sink_raw.png      — clean screenshot, no overlay
//   kitchen_sink_debug.png    — same PNG with colored boxes + element ID labels burned in
//
// How to inspect output:
//   Open the .xcresult in Xcode → test navigator → expand the test → click the attachment.
//   Or: open .build/debug-output/KitchenSinkValidation.xcresult directly.
//
// What to check:
//   - Every annotated element has a tight box (not the whole screen, not zero-sized)
//   - Boxes for same-type elements (e.g. three listRows) look independent and correct
//   - No box overlaps an unrelated element due to a coordinate bug
//   - Chrome boxes (navigationBar, tabBar, homeIndicator) are in the right screen zones
//   - Assertions at the bottom catch structural issues automatically

import XCTest
import SwiftUI
import CryptoKit

/// New training-candidate layouts; never reuse the155development compositions.
@MainActor
final class NativePageStyle210Test: XCTestCase {
    struct Catalog: Decodable {
        let version: String, target: String, role: String
        let trainingEligible: Bool
        let members: [Row]
    }
    struct Row: Decodable {
        let id: String, family: String, theme: String, backgroundStyle: String, position: String, group: String
        let interaction: Bool
        let pages: Int
        let seed: UInt64
    }
    func testCaptureStyle210() async throws {
        let env = ProcessInfo.processInfo.environment
        guard env["NUA_STYLE210"] == "capture" else { throw XCTSkip("Opt-in style210 capture") }
        let target = try XCTUnwrap(env["NUA_STYLE210_TARGET"])
        guard UUID(uuidString: target) != nil, target == env["SIMULATOR_UDID"] else { throw CocoaError(.fileReadCorruptFile) }
        let url = URL(fileURLWithPath: try XCTUnwrap(env["NUA_STYLE210_CATALOG"]))
        guard url.resolvingSymlinksInPath() == url else { throw CocoaError(.fileReadCorruptFile) }
        let raw = try Data(contentsOf: url)
        let sha = SHA256.hash(data: raw).map { String(format: "%02x", $0) }.joined()
        guard raw.count < 1_000_000, sha == env["NUA_STYLE210_SHA256"] else { throw CocoaError(.fileReadCorruptFile) }
        let catalog = try JSONDecoder().decode(Catalog.self, from: raw)
        guard catalog.version == "native-style210-v1", catalog.target == target,
              catalog.role == "training_candidate", !catalog.trainingEligible, catalog.members.count == 144,
              Set(catalog.members.map(\.id)).count == 144 else { throw CocoaError(.fileReadCorruptFile) }
        var axes = Set<String>()
        for (index, r) in catalog.members.enumerated() {
            guard ["account-summary210", "document-stack210"].contains(r.family),
                  ["light", "dark"].contains(r.theme), ["automatic", "prominent"].contains(r.backgroundStyle),
                  [3,5,9].contains(r.pages), ["leading","center","trailing"].contains(r.position),
                  r.id == String(format: "style210-%03d", index), r.seed == UInt64(210000+index),
                  r.group == "\(r.family):pages\(r.pages):position\(r.position)" else { throw CocoaError(.fileReadCorruptFile) }
            axes.insert("\(r.family):\(r.theme):\(r.backgroundStyle):\(r.interaction):\(r.pages):\(r.position)")
        }
        guard axes.count == 144 else { throw CocoaError(.fileReadCorruptFile) }
        let output = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("native-style210-v1")
        guard !FileManager.default.fileExists(atPath: output.path) else { throw CocoaError(.fileWriteFileExists) }
        try FileManager.default.createDirectory(at: output, withIntermediateDirectories: false)
        var rows: [[String: Any]] = []; var bytes = 0
        let start = ProcessInfo.processInfo.systemUptime
        for r in catalog.members {
            guard ProcessInfo.processInfo.systemUptime-start < 600 else { throw CocoaError(.userCancelled) }
            let config = GeneratorRunConfig(seed: r.seed, templateFamily: r.family, osProfile: .ios26,
                simulatorOverride: SimulatorStateOverride(time: "09:41", batteryLevel: 100, batteryState: "charging", cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: ""),
                colorScheme: r.theme == "dark" ? .dark : .light, dynamicTypeSize: .large,
                deviceName: "iPhone 17 Pro", pixelScale: 3, locale: "en_US", layoutDirection: .ltr)
            let vc = Style210Controller(row: r)
            var hidden: Data?; var body = CGRect.zero; var frame = CGRect.zero
            let result = try await ScreenshotCapture.captureUIKit(vc, config: config, nativePageEvidence: { hidden=$0; frame=$1; body=$2 })
            let reference = try XCTUnwrap(hidden)
            bytes += result.png.count + reference.count
            guard bytes < 512*1024*1024, !body.isEmpty else { throw CocoaError(.fileReadCorruptFile) }
            try result.png.write(to: output.appendingPathComponent(r.id+".png"), options: .withoutOverwriting)
            try reference.write(to: output.appendingPathComponent(r.id+"-hidden.png"), options: .withoutOverwriting)
            try AnnotationWriter.write(result: result, config: config, imageFileName: r.id+".png", templateFamily: r.family,
                generatorVersion: "native-style210-v1", to: output.appendingPathComponent(r.id+".json"))
            let row: [String: Any] = ["id":r.id,"group":r.group,"sha256":result.sha256,
                "hiddenSHA256":SHA256.hash(data: reference).map { String(format: "%02x", $0) }.joined(),
                "body":[body.minX,body.minY,body.width,body.height],"frame":[frame.minX,frame.minY,frame.width,frame.height],
                "scale":result.scale,"requestedBackgroundStyle":r.backgroundStyle,
                "resolvedBackgroundStyle":vc.control.backgroundStyle.rawValue,"interaction":vc.control.isUserInteractionEnabled]
            rows.append(row)
            try JSONSerialization.data(withJSONObject: row, options: [.sortedKeys]).write(to: output.appendingPathComponent(r.id+"-evidence.json"), options: .withoutOverwriting)
        }
        try JSONSerialization.data(withJSONObject: ["catalogSHA256":sha,"target":target,"rows":rows,"trainingEligible":false,
            "runtime":ProcessInfo.processInfo.operatingSystemVersionString], options: [.sortedKeys])
            .write(to: output.appendingPathComponent("receipt.json"), options: .withoutOverwriting)
    }
}

@MainActor
private final class Style210Controller: UIViewController, UIKitAnnotatable {
    let control = UIPageControl()
    var labels: [UILabel] = []
    let row: NativePageStyle210Test.Row
    init(row: NativePageStyle210Test.Row) {
        self.row = row; super.init(nibName: nil, bundle: nil)
        overrideUserInterfaceStyle = row.theme == "dark" ? .dark : .light
        view.backgroundColor = .systemBackground
        control.numberOfPages = row.pages; control.currentPage = Int(row.seed % UInt64(row.pages))
        control.backgroundStyle = row.backgroundStyle == "prominent" ? .prominent : .automatic
        control.isUserInteractionEnabled = row.interaction
        control.currentPageIndicatorTintColor = .label; control.pageIndicatorTintColor = .tertiaryLabel
        view.addSubview(control)
        for n in 0..<4 {
            let label = UILabel(frame: CGRect(x: 30+CGFloat(n%2)*160, y: 140+CGFloat(n/2)*160, width: 145, height: 130))
            label.backgroundColor = .secondarySystemBackground; label.numberOfLines = 0
            label.text = row.family == "account-summary210" ? "Account \(n+1)\nAvailable balance\n\(120+n*73) credits" : "Document \(n+1)\nLocal drafts\n\(n+2) pages"
            label.textAlignment = .center; view.addSubview(label); labels.append(label)
        }
    }
    required init?(coder: NSCoder) { fatalError("Not used") }
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        let size = control.size(forNumberOfPages: row.pages)
        let x = row.position == "leading" ? 24 : row.position == "trailing" ? view.bounds.width-24-size.width : (view.bounds.width-size.width)/2
        control.frame = CGRect(x: x, y: row.family == "account-summary210" ? 525 : 625, width: size.width, height: size.height)
    }
    var annotatedViews: [UIKitAnnotatedView] {
        [UIKitAnnotatedView(id: "pageControl_0", elementType: "pageControl", view: control)] +
            labels.enumerated().map { UIKitAnnotatedView(id: "label_\($0.offset)", elementType: "label", view: $0.element) }
    }
}

/// Development-only geometry qualification. Never changes existing corpus bytes.
@MainActor
final class NativePageGeometry150Test: XCTestCase {
    func testNativeContext157() async throws {
        let env = ProcessInfo.processInfo.environment
        guard env["NUA_NATIVE_PAGE150"] == "approved-context157" else { throw XCTSkip("Explicit native context qualification required") }
        guard let target = env["NUA_NATIVE_PAGE150_TARGET"], target == env["SIMULATOR_UDID"] else { throw CocoaError(.fileReadCorruptFile) }
        let output = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("native-page157-frozen")
        guard !FileManager.default.fileExists(atPath: output.path) else { throw CocoaError(.fileWriteFileExists) }
        try FileManager.default.createDirectory(at: output, withIntermediateDirectories: false)
        var rows: [[String: Any]] = []; var failures: [[String: Any]] = []; var bytes = 0
        let started = ProcessInfo.processInfo.systemUptime
        for family in ["UIKitControls", "KitchenSink"] {
            for modern in [false, true] {
                for dark in [false, true] {
                    for seed: UInt64 in [7, 19, 31] {
                        let id = "\(family)-\(modern)-\(dark)-\(seed)"
                        guard ProcessInfo.processInfo.systemUptime - started < 180 else { throw CocoaError(.userCancelled) }
                        let config = GeneratorRunConfig(seed: seed, templateFamily: family, osProfile: modern ? .ios26 : .ios17,
                            simulatorOverride: SimulatorStateOverride(time: "09:41", batteryLevel: 100, batteryState: "charging", cellularBars: 5,
                                wifiBars: 3, cellularMode: "active", operatorName: ""), colorScheme: dark ? .dark : .light,
                            dynamicTypeSize: .large, deviceName: "iPhone 17 Pro", pixelScale: modern ? 3 : 2, locale: "en_US", layoutDirection: .ltr)
                        var reference: Data?; var container = CGRect.zero; var body = CGRect.zero
                        let evidence: (Data, CGRect, CGRect) -> Void = { reference = $0; container = $1; body = $2 }
                        do {
                            let result: CaptureResult
                            if family == "UIKitControls" {
                                let vc = UIKitControlsViewController(seed: seed, config: config)
                                result = try await ScreenshotCapture.captureUIKit(vc, config: config, nativePageEvidence: evidence)
                                XCTAssertNil(vc.view.window, "Owned window must detach its controller")
                                XCTAssertEqual(vc.view.layer.speed, 1)
                                XCTAssertEqual(vc.view.layer.timeOffset, 0)
                                let page = try XCTUnwrap(vc.annotatedViews.first { $0.elementType == "pageControl" }?.view as? UIPageControl)
                                XCTAssertFalse(page.isHidden, "Controlled removal must restore visibility")
                            } else {
                                var corpus = ContentCorpus(seed: seed)
                                var template = KitchenSinkConfig.make(seed: seed, corpus: &corpus)
                                template.colorScheme = dark ? .dark : .light
                                result = try await ScreenshotCapture.capture(KitchenSinkTemplate(config: template),
                                    windowSize: CGSize(width: modern ? 393 : 375, height: 1100), config: config, nativePageEvidence: evidence)
                            }
                            let hidden = try XCTUnwrap(reference)
                            let page = try XCTUnwrap(result.elements.first { $0.elementType == "pageControl" })
                            XCTAssertEqual(page.frame, body)
                            bytes += result.png.count + hidden.count
                            guard bytes < 256 * 1024 * 1024 else { throw CocoaError(.fileWriteOutOfSpace) }
                            try result.png.write(to: output.appendingPathComponent(id + ".png"), options: .withoutOverwriting)
                            try hidden.write(to: output.appendingPathComponent(id + "-hidden.png"), options: .withoutOverwriting)
                            try AnnotationWriter.write(result: result, config: config, imageFileName: id + ".png", templateFamily: family,
                                generatorVersion: "native-context157-v1", to: output.appendingPathComponent(id + ".json"))
                            rows.append(["id": id, "family": family, "seed": seed, "dark": dark, "modern": modern, "scale": result.scale,
                                "sha256": result.sha256, "hiddenSHA256": SHA256.hash(data: hidden).map { String(format: "%02x", $0) }.joined(),
                                "frame": [container.minX, container.minY, container.width, container.height],
                                "body": [body.minX, body.minY, body.width, body.height]])
                        } catch {
                            let error = error as NSError
                            for (key, suffix) in [("visiblePNG", "-failed.png"), ("hiddenPNG", "-failed-hidden.png")] {
                                if let data = error.userInfo[key] as? Data {
                                    bytes += data.count
                                    guard bytes < 256 * 1024 * 1024 else { throw CocoaError(.fileWriteOutOfSpace) }
                                    try data.write(to: output.appendingPathComponent(id + suffix), options: .withoutOverwriting)
                                }
                            }
                            failures.append(["id": id, "error": error.localizedDescription, "domain": error.domain, "code": error.code])
                        }
                    }
                }
            }
        }
        try JSONSerialization.data(withJSONObject: ["version": "native-context157-v1", "target": target, "rows": rows, "failures": failures,
            "seconds": ProcessInfo.processInfo.systemUptime - started], options: [.prettyPrinted, .sortedKeys])
            .write(to: output.appendingPathComponent("receipt.json"), options: .withoutOverwriting)
        print("NATIVE_CONTEXT157_COMPLETE \(output.path)")
        XCTAssertEqual(rows.count, 24); XCTAssertTrue(failures.isEmpty, "Rejected cases remain unqualified")
    }

    func testPageCompositions155() async throws {
        let env = ProcessInfo.processInfo.environment
        guard env["NUA_NATIVE_PAGE150"] == "approved-compositions155" else { throw XCTSkip("Explicit composition capture required") }
        guard let target = env["NUA_NATIVE_PAGE150_TARGET"], target == env["SIMULATOR_UDID"] else { throw CocoaError(.fileReadCorruptFile) }
        let output = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("native-page155-compositions")
        guard !FileManager.default.fileExists(atPath: output.path) else { throw CocoaError(.fileWriteFileExists) }
        try FileManager.default.createDirectory(at: output, withIntermediateDirectories: false)
        let started = ProcessInfo.processInfo.systemUptime
        var rows: [[String: Any]] = []; var bytes = 0
        for family in ["reader-footer", "gallery-inspector"] {
            for native in [false, true] {
                for dark in [false, true] {
                    for pages in [3, 5, 7] {
                        for left in [false, true] {
                            for seed in [7, 19] {
                                guard ProcessInfo.processInfo.systemUptime - started < 180 else { throw CocoaError(.userCancelled) }
                                let id = "\(family)-\(native)-\(dark)-\(pages)-\(left)-\(seed)"
                                let config = GeneratorRunConfig(seed: UInt64(seed), templateFamily: "PageComposition155",
                                    osProfile: .ios26, simulatorOverride: SimulatorStateOverride(time: "09:41", batteryLevel: 100,
                                    batteryState: "charging", cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: ""),
                                    colorScheme: dark ? .dark : .light, dynamicTypeSize: .large, deviceName: "iPhone 17 Pro",
                                    pixelScale: 3, locale: "en_US", layoutDirection: .ltr)
                                let vc = PageComposition155Controller(family: family, native: native, dark: dark, pages: pages, left: left, seed: seed)
                                let visible = try await ScreenshotCapture.captureUIKit(vc, config: config)
                                let frame = vc.indicator.convert(vc.indicator.bounds, to: vc.view)
                                vc.indicator.isHidden = true
                                let hidden = try await ScreenshotCapture.captureUIKit(vc, config: config)
                                bytes += visible.png.count + hidden.png.count
                                guard bytes < 256 * 1024 * 1024 else { throw CocoaError(.fileWriteOutOfSpace) }
                                try visible.png.write(to: output.appendingPathComponent(id + ".png"), options: .withoutOverwriting)
                                try hidden.png.write(to: output.appendingPathComponent(id + "-hidden.png"), options: .withoutOverwriting)
                                rows.append(["id": id, "family": family, "native": native, "dark": dark, "pages": pages,
                                    "left": left, "seed": seed, "selection": seed % pages, "prominent": native && seed == 19,
                                    "scale": visible.scale, "width": visible.pixelSize.width, "height": visible.pixelSize.height,
                                    "frame": [frame.minX, frame.minY, frame.width, frame.height],
                                    "sha256": visible.sha256, "hiddenSHA256": hidden.sha256])
                            }
                        }
                    }
                }
            }
        }
        try JSONSerialization.data(withJSONObject: ["version": "page-composition155-v1", "target": target,
            "runtime": ProcessInfo.processInfo.operatingSystemVersionString, "rows": rows,
            "seconds": ProcessInfo.processInfo.systemUptime - started], options: [.sortedKeys, .prettyPrinted])
            .write(to: output.appendingPathComponent("receipt.json"), options: .withoutOverwriting)
        print("PAGE_COMPOSITION155_COMPLETE \(output.path)")
    }

    func testNativePageAlphaBounds() async throws {
        let env = ProcessInfo.processInfo.environment
        guard env["NUA_NATIVE_PAGE150"] == "approved-alpha-development" else {
            throw XCTSkip("Explicit alpha qualification required")
        }
        guard let target = env["NUA_NATIVE_PAGE150_TARGET"], !target.isEmpty,
              target == env["SIMULATOR_UDID"] else { throw CocoaError(.fileReadCorruptFile) }
        let fm = FileManager.default
        let output = fm.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("native-page150-alpha")
        guard !fm.fileExists(atPath: output.path) else { throw CocoaError(.fileWriteFileExists) }
        try fm.createDirectory(at: output, withIntermediateDirectories: false)
        let started = ProcessInfo.processInfo.systemUptime
        var rows: [[String: Any]] = []; var bytes = 0
        for modern in [false, true] {
            for count in [3, 5, 7] {
                for selected in [0, count / 2, count - 1] {
                    for dark in [false, true] {
                        for prominent in [false, true] {
                            guard ProcessInfo.processInfo.systemUptime - started < 120 else { throw CocoaError(.userCancelled) }
                            let id = "alpha-\(modern)-\(count)-\(selected)-\(dark)-\(prominent)"
                            let config = GeneratorRunConfig(seed: 150, templateFamily: "NativePageAlpha150", osProfile: modern ? .ios26 : .ios17,
                                simulatorOverride: SimulatorStateOverride(time: "09:41", batteryLevel: 100, batteryState: "charging", cellularBars: 5,
                                    wifiBars: 3, cellularMode: "active", operatorName: ""), colorScheme: dark ? .dark : .light,
                                dynamicTypeSize: .large, deviceName: "iPhone 17 Pro", pixelScale: modern ? 3 : 2, locale: "en_US", layoutDirection: .ltr)
                            let vc = NativePageAlphaController(count: count, selected: selected, dark: dark, prominent: prominent, scale: CGFloat(config.pixelScale))
                            let result = try await ScreenshotCapture.captureUIKit(vc, config: config)
                            try result.png.write(to: output.appendingPathComponent(id + ".png"), options: .withoutOverwriting)
                            bytes += result.png.count
                            guard bytes < 256 * 1024 * 1024, let bounds = vc.measured else { throw CocoaError(.fileReadCorruptFile) }
                            let frame = vc.control.convert(bounds, to: vc.view)
                            rows.append(["id": id, "sha256": result.sha256, "scale": result.scale,
                                "dark": dark, "prominent": prominent, "pages": count, "selection": selected,
                                "frame": [frame.minX, frame.minY, frame.width, frame.height]])
                        }
                    }
                }
            }
        }
        try JSONSerialization.data(withJSONObject: ["version": "native-page150-alpha-v1", "target": target, "rows": rows,
            "seconds": ProcessInfo.processInfo.systemUptime - started], options: [.sortedKeys, .prettyPrinted])
            .write(to: output.appendingPathComponent("receipt.json"), options: .withoutOverwriting)
        print("NATIVE_PAGE150_ALPHA_COMPLETE \(output.path)")
    }

    func testNativePageGeometry() async throws {
        let env = ProcessInfo.processInfo.environment
        guard env["NUA_NATIVE_PAGE150"] == "approved-development" else {
            throw XCTSkip("Explicit native page geometry execution required")
        }
        guard let target = env["NUA_NATIVE_PAGE150_TARGET"], !target.isEmpty,
              target == env["SIMULATOR_UDID"] else { throw CocoaError(.fileReadCorruptFile) }
        let fm = FileManager.default
        let output = fm.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("native-page150")
        guard !fm.fileExists(atPath: output.path) else { throw CocoaError(.fileWriteFileExists) }
        try fm.createDirectory(at: output, withIntermediateDirectories: false)
        let started = ProcessInfo.processInfo.systemUptime
        var rows: [[String: Any]] = []
        var bytes = 0
        for width in [375.0, 430.0] {
            for count in [3, 5, 7] {
                for selection in [0, count / 2, count - 1] {
                    for dark in [false, true] {
                        guard ProcessInfo.processInfo.systemUptime - started < 120 else {
                            throw CocoaError(.userCancelled)
                        }
                        let id = "native-\(Int(width))-\(count)-\(selection)-\(dark ? "dark" : "light")"
                        let config = GeneratorRunConfig(seed: 150, templateFamily: "NativePageGeometry150",
                            osProfile: .ios26,
                            simulatorOverride: SimulatorStateOverride(time: "09:41", batteryLevel: 100,
                                batteryState: "charging", cellularBars: 5, wifiBars: 3,
                                cellularMode: "active", operatorName: ""),
                            colorScheme: dark ? .dark : .light, dynamicTypeSize: .large,
                            deviceName: "iPhone 17 Pro", pixelScale: 3, locale: "en_US", layoutDirection: .ltr)
                        let view = ZStack {
                            (dark ? Color.black : Color.white)
                            NativeUIPageControlView(numberOfPages: count, currentPage: selection)
                                .fixedSize().captureFrame(id: "pageControl_0")
                        }.ignoresSafeArea().environment(\.colorScheme, dark ? .dark : .light)
                        let result = try await ScreenshotCapture.capture(view,
                            windowSize: CGSize(width: width, height: 180), config: config)
                        let frame = try XCTUnwrap(result.elements.first { $0.id == "pageControl_0" }).frame
                        let control = UIPageControl()
                        control.numberOfPages = count
                        control.currentPage = selection
                        let publicSize = control.size(forNumberOfPages: count)
                        guard frame.width > 0, frame.height > 0, frame.width < width / 2,
                              frame.minX >= 0, frame.maxX <= width,
                              frame.minY >= 0, frame.maxY <= 180 else {
                            throw CocoaError(.fileReadCorruptFile)
                        }
                        bytes += result.png.count
                        guard bytes < 256 * 1024 * 1024 else { throw CocoaError(.fileWriteOutOfSpace) }
                        try result.png.write(to: output.appendingPathComponent(id + ".png"), options: .withoutOverwriting)
                        try AnnotationWriter.write(result: result, config: config, imageFileName: id + ".png",
                            templateFamily: "NativePageGeometry150", generatorVersion: "native-page150-probe-v1",
                            to: output.appendingPathComponent(id + ".json"))
                        rows.append(["id": id, "width": width, "pages": count, "selection": selection,
                            "theme": dark ? "dark" : "light", "sha256": result.sha256,
                            "frame": [frame.minX, frame.minY, frame.width, frame.height],
                            "publicSize": [publicSize.width, publicSize.height]])
                    }
                }
            }
        }
        let receipt: [String: Any] = ["version": "native-page150-probe-v1", "target": target,
            "runtime": ProcessInfo.processInfo.operatingSystemVersionString,
            "rows": rows, "count": rows.count, "seconds": ProcessInfo.processInfo.systemUptime - started]
        try JSONSerialization.data(withJSONObject: receipt, options: [.sortedKeys, .prettyPrinted])
            .write(to: output.appendingPathComponent("receipt.json"), options: .withoutOverwriting)
        print("NATIVE_PAGE150_COMPLETE \(output.path)")
    }
}

@MainActor
private final class PageComposition155Controller: UIViewController, UIKitAnnotatable {
    let indicator: UIView
    private var hosting: UIHostingController<NativeUIPageDotsView>?
    let family: String, left: Bool
    let size: CGSize
    init(family: String, native: Bool, dark: Bool, pages: Int, left: Bool, seed: Int) {
        self.family = family; self.left = left
        if native {
            let control = UIPageControl()
            control.numberOfPages = pages; control.currentPage = seed % pages
            control.currentPageIndicatorTintColor = .label; control.pageIndicatorTintColor = .tertiaryLabel
            control.backgroundStyle = seed == 19 ? .prominent : .automatic
            control.isUserInteractionEnabled = seed == 19
            indicator = control; size = control.size(forNumberOfPages: pages)
        } else {
            let host = UIHostingController(rootView: NativeUIPageDotsView(pageCount: pages, currentPage: seed % pages))
            hosting = host; indicator = host.view; host.view.backgroundColor = .clear
            size = host.sizeThatFits(in: CGSize(width: 350, height: 60))
        }
        super.init(nibName: nil, bundle: nil)
        overrideUserInterfaceStyle = dark ? .dark : .light
        view.backgroundColor = .systemBackground
        if let host = hosting { addChild(host); host.didMove(toParent: self) }
        view.addSubview(indicator)
        let title = UILabel(frame: CGRect(x: 24, y: 65, width: 340, height: 40))
        title.text = family == "reader-footer" ? "Reading collection \(seed)" : "Gallery inspector \(seed)"
        title.font = .systemFont(ofSize: 23, weight: .bold); view.addSubview(title)
        let card = UIView(frame: CGRect(x: 24, y: 125, width: 345, height: family == "reader-footer" ? 385 : 240))
        card.backgroundColor = .secondarySystemBackground; card.layer.cornerRadius = 14; view.addSubview(card)
        let text = UILabel(frame: card.bounds.insetBy(dx: 20, dy: 20)); text.numberOfLines = 0
        text.text = family == "reader-footer" ? "A quiet afternoon\n\nChapter \(seed)\n\nExplore the collection one page at a time.\n\nYour place is saved." : "Collection \(seed)\n\nImage details\n\nCaptured locally\n\nBrowse related items below."
        text.textColor = .label; text.font = .systemFont(ofSize: 18); card.addSubview(text)
        let button = UIButton(type: .system); button.frame = CGRect(x: 24, y: 680, width: 345, height: 44)
        button.setTitle("Continue", for: .normal); view.addSubview(button)
    }
    required init?(coder: NSCoder) { fatalError("Not used") }
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        indicator.frame = CGRect(x: left ? 28 : (view.bounds.width-size.width)/2,
                                 y: family == "reader-footer" ? 550 : 410, width: size.width, height: size.height)
    }
    var annotatedViews: [UIKitAnnotatedView] {
        indicator.isHidden ? [] : [UIKitAnnotatedView(id: "pageControl_0", elementType: "pageControl", view: indicator)]
    }
}

@MainActor
private final class NativePageAlphaController: UIViewController, UIKitAnnotatable {
    let control = UIPageControl()
    let scale: CGFloat
    var measured: CGRect?
    init(count: Int, selected: Int, dark: Bool, prominent: Bool, scale: CGFloat) {
        self.scale = scale
        super.init(nibName: nil, bundle: nil)
        overrideUserInterfaceStyle = dark ? .dark : .light
        view.backgroundColor = dark ? .black : .white
        control.numberOfPages = count; control.currentPage = selected
        control.currentPageIndicatorTintColor = .label
        control.pageIndicatorTintColor = .tertiaryLabel
        control.isUserInteractionEnabled = prominent
        control.backgroundStyle = prominent ? .prominent : .automatic
        view.addSubview(control)
    }
    required init?(coder: NSCoder) { fatalError("Not used") }
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        let size = control.size(forNumberOfPages: control.numberOfPages)
        control.frame = CGRect(x: (view.bounds.width - size.width) / 2, y: 151,
                               width: size.width, height: size.height)
    }
    var annotatedViews: [UIKitAnnotatedView] {
        measured = try? NativePageVisualBounds.measure(control, scale: scale)
        return [UIKitAnnotatedView(id: "pageControl_0", elementType: "pageControl", view: control)]
    }
}

/// Explicit corpus repair, separate from the normal offline unit suite.
@MainActor
final class PageDotRegenerationTest: XCTestCase {
    /// Exact training-only native repair. Existing manual regeneration stays separate.
    func testNativePageRepair159() async throws {
        let env = ProcessInfo.processInfo.environment
        let variation = env["NUA_PAGE_REGEN_EXECUTE"] == "approved-172"
        guard variation || env["NUA_PAGE_REGEN_EXECUTE"] == "approved-159" else { throw XCTSkip("Explicit native repair required") }
        let target = try XCTUnwrap(env["NUA_PAGE_REGEN_TARGET"])
        guard target == env["SIMULATOR_UDID"] else { throw CocoaError(.fileReadCorruptFile) }
        let url = URL(fileURLWithPath: try XCTUnwrap(env["NUA_PAGE_REGEN_CATALOG"]))
        guard url.resolvingSymlinksInPath() == url else { throw CocoaError(.fileReadInvalidFileName) }
        let data = try Data(contentsOf: url)
        let digest = SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
        guard data.count < 4_000_000, digest == env["NUA_PAGE_REGEN_SHA256"] else { throw CocoaError(.fileReadCorruptFile) }
        let catalog = try JSONDecoder().decode(Catalog.self, from: data)
        if variation {
            guard catalog.version == "native-placement-capture-v1", catalog.target == target,
                  catalog.split == "train", [24,264].contains(catalog.members.count),
                  Set(catalog.members.map(\.id)).count == catalog.members.count,
                  catalog.members.allSatisfy({ ["UIKitControls","KitchenSink"].contains($0.family) &&
                    ["leading","center","trailing"].contains($0.placement ?? "") &&
                    ["system-blue","semantic-label"].contains($0.tint ?? "") }) else { throw CocoaError(.fileReadCorruptFile) }
        } else {
          guard catalog.version == "native-page-repair-v1", catalog.members.count == 900,
              Set(catalog.members.map(\.id)).count == 900,
              catalog.members.filter({ $0.family == "UIKitControls" }).count == 700,
              catalog.members.filter({ $0.family == "KitchenSink" }).count == 200 else { throw CocoaError(.fileReadCorruptFile) }
        }
        let fm = FileManager.default
        let outputName = variation ? (catalog.members.count == 24 ? "native-placement172-qualification-r4" : "native-placement172-batch-r4") : "native-page159"
        let output = fm.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent(outputName)
        guard !fm.fileExists(atPath: output.path) else { throw CocoaError(.fileWriteFileExists) }
        try fm.createDirectory(at: output, withIntermediateDirectories: false)
        let started = ProcessInfo.processInfo.systemUptime
        var bytes = 0; var rows: [[String: Any]] = []
        for member in catalog.members {
            do {
                guard ProcessInfo.processInfo.systemUptime - started < 1800,
                      member.id.range(of: variation ? "^placement171-img_[0-9]{6}-(leading|center|trailing)-(system-blue|semantic-label)$" : "^img_[0-9]{6}$", options: .regularExpression) != nil,
                      [2, 3].contains(member.scale) else { throw CocoaError(.userCancelled) }
                let config = GeneratorRunConfig(seed: member.seed, templateFamily: member.family,
                    osProfile: member.scale == 3 ? .ios26 : .ios17, simulatorOverride: member.simulatorState,
                    colorScheme: member.colorScheme, dynamicTypeSize: member.dynamicTypeSize,
                    deviceName: member.deviceName, pixelScale: member.scale, locale: member.locale,
                    layoutDirection: member.layoutDirection, accessibilityFlags: member.accessibilityFlags)
                var hidden: Data?; var frame = CGRect.zero; var body = CGRect.zero
                var resolved: [String: Any] = [:]
                let style = variation ? try NativePageTrainingStyle(placement: member.placement!, tint: member.tint!, rtl: member.layoutDirection == .rtl,
                    sceneWidth: CGFloat(member.width) / CGFloat(member.scale)) : nil
                let configure: ((UIView) throws -> Void)? = variation ? { scene in
                    resolved = try NativePageVisualBounds.configure(scene, placement: member.placement!,
                        tint: member.tint!, rtl: member.layoutDirection == .rtl)
                } : nil
                let evidence: (Data, CGRect, CGRect) -> Void = { hidden = $0; frame = $1; body = $2 }
                let result: CaptureResult
                if member.family == "UIKitControls" {
                    result = try await ScreenshotCapture.captureUIKit(UIKitControlsViewController(seed: member.seed, config: config, pageTrainingStyle: style),
                        config: config, nativePageEvidence: evidence, nativePageConfiguration: configure)
                } else {
                    var corpus = ContentCorpus(seed: member.seed)
                    result = try await ScreenshotCapture.capture(KitchenSinkTemplate(config: .make(seed: member.seed, corpus: &corpus), pageTrainingStyle: style),
                        windowSize: CGSize(width: 393, height: 1100), config: config, nativePageEvidence: evidence, nativePageConfiguration: configure)
                }
                let reference = try XCTUnwrap(hidden)
                guard Int(result.pixelSize.width) == member.width, Int(result.pixelSize.height) == member.height else {
                    throw CocoaError(.fileReadCorruptFile)
                }
                bytes += result.png.count + reference.count
                guard bytes < 2 * 1024 * 1024 * 1024 else { throw CocoaError(.fileWriteOutOfSpace) }
                try result.png.write(to: output.appendingPathComponent(member.id + ".png"), options: .withoutOverwriting)
                try reference.write(to: output.appendingPathComponent(member.id + "-hidden.png"), options: .withoutOverwriting)
                try AnnotationWriter.write(result: result, config: config, imageFileName: member.id + ".png",
                    templateFamily: member.family, generatorVersion: variation ? "native-placement172-v1" : "native-page-repair159-v1",
                    to: output.appendingPathComponent(member.id + ".json"))
                rows.append(["id": member.id, "scale": member.scale, "sha256": result.sha256,
                    "hiddenSHA256": SHA256.hash(data: reference).map { String(format: "%02x", $0) }.joined(),
                    "frame": [frame.minX, frame.minY, frame.width, frame.height],
                    "body": [body.minX, body.minY, body.width, body.height], "resolvedVariation": resolved])
                if rows.count % 50 == 0 { print("NATIVE159_PROGRESS \(rows.count)/900 bytes=\(bytes)") }
            } catch {
                let error = error as NSError
                for (key, suffix) in [("visiblePNG", "-failed.png"), ("hiddenPNG", "-failed-hidden.png")] {
                    if let png = error.userInfo[key] as? Data { try png.write(to: output.appendingPathComponent(member.id + suffix), options: .withoutOverwriting) }
                }
                try JSONSerialization.data(withJSONObject: ["version": "native-page-repair-failure-v1", "failed": member.id,
                    "error": error.localizedDescription, "rows": rows, "catalogSHA256": digest], options: [.sortedKeys, .prettyPrinted])
                    .write(to: output.appendingPathComponent("failure.json"), options: .withoutOverwriting)
                print("NATIVE159_FAILED \(output.path)")
                throw error
            }
        }
        try JSONSerialization.data(withJSONObject: ["version": variation ? "native-placement-receipt-v1" : "native-page-repair-receipt-v1", "target": target,
            "catalogSHA256": digest, "rows": rows, "bytes": bytes,
            "runtimeOS": ProcessInfo.processInfo.operatingSystemVersionString,
            "seconds": ProcessInfo.processInfo.systemUptime - started], options: [.sortedKeys, .prettyPrinted])
            .write(to: output.appendingPathComponent("receipt.json"), options: .withoutOverwriting)
        print("NATIVE159_COMPLETE \(output.path)")
    }

    private struct Catalog: Decodable, Sendable {
        let version: String
        let members: [Member]
        let target: String?
        let split: String?
    }
    private struct Member: Decodable, Sendable {
        let id: String
        let family: String
        let seed: UInt64
        let width: Int
        let height: Int
        let scale: Int
        let colorScheme: GeneratorColorScheme
        let dynamicTypeSize: GeneratorDynamicTypeSize
        let locale: String
        let layoutDirection: GeneratorLayoutDirection
        let deviceName: String
        let simulatorState: SimulatorStateOverride
        let accessibilityFlags: AccessibilityFlags
        let placement: String?
        let tint: String?
    }

    func testApprovedPageDotRegeneration() async throws {
        let env = ProcessInfo.processInfo.environment
        guard env["NUA_PAGE_REGEN_EXECUTE"] == "approved-41" else {
            throw XCTSkip("Explicit corpus regeneration approval required")
        }
        let path = try XCTUnwrap(env["NUA_PAGE_REGEN_CATALOG"])
        let url = URL(fileURLWithPath: path)
        guard url.resolvingSymlinksInPath() == url, env["SIMULATOR_UDID"] == env["NUA_PAGE_REGEN_TARGET"] else {
            throw CocoaError(.fileReadInvalidFileName)
        }
        let data = try Data(contentsOf: url)
        let digest = SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
        XCTAssertEqual(digest, env["NUA_PAGE_REGEN_SHA256"])
        guard digest == env["NUA_PAGE_REGEN_SHA256"], data.count < 2_000_000 else { throw CocoaError(.fileReadCorruptFile) }
        let catalog = try JSONDecoder().decode(Catalog.self, from: data)
        guard catalog.version == "page-dot-regeneration-v1", catalog.members.count == 666,
              Set(catalog.members.map(\.id)).count == 666 else { throw CocoaError(.fileReadCorruptFile) }
        let fm = FileManager.default
        let output = fm.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("page-regeneration-41")
        guard !fm.fileExists(atPath: output.path) else { throw CocoaError(.fileWriteFileExists) }
        try fm.createDirectory(at: output, withIntermediateDirectories: false)
        let started = ProcessInfo.processInfo.systemUptime
        var bytes = 0
        for (index, row) in catalog.members.enumerated() {
            guard ProcessInfo.processInfo.systemUptime - started < 1200,
                  row.id.range(of: "^img_[0-9]{6}$", options: .regularExpression) != nil,
                  [2, 3].contains(row.scale), ["MediaCardGrid", "ProgressActivity"].contains(row.family) else {
                throw CocoaError(.userCancelled)
            }
            let config = GeneratorRunConfig(seed: row.seed, templateFamily: row.family,
                osProfile: row.scale == 3 ? .ios26 : .ios17, simulatorOverride: row.simulatorState,
                colorScheme: row.colorScheme, dynamicTypeSize: row.dynamicTypeSize, deviceName: row.deviceName,
                pixelScale: row.scale, locale: row.locale, layoutDirection: row.layoutDirection,
                accessibilityFlags: row.accessibilityFlags)
            var corpus = ContentCorpus(seed: row.seed)
            let view: AnyView
            if row.family == "MediaCardGrid" {
                view = AnyView(MediaCardGridTemplate(config: .make(seed: row.seed, corpus: &corpus)))
            } else {
                view = AnyView(ProgressActivityTemplate(config: .make(seed: row.seed, corpus: &corpus)))
            }
            let result = try await ScreenshotCapture.capture(view, config: config)
            let dots = try XCTUnwrap(result.elements.first { $0.id == "pageControl_0" })
            guard [25.0,40.0,55.0,70.0].contains(where: { abs(dots.frame.width - $0) < 1 }),
                  abs(dots.frame.height - 10) < 1,
                  Int(result.pixelSize.width) == row.width, Int(result.pixelSize.height) == row.height else {
                throw CocoaError(.fileReadCorruptFile)
            }
            bytes += result.png.count
            guard bytes < 2 * 1024 * 1024 * 1024 else { throw CocoaError(.fileWriteOutOfSpace) }
            try result.png.write(to: output.appendingPathComponent(row.id + ".png"), options: .withoutOverwriting)
            let annotation = output.appendingPathComponent(row.id + ".json")
            try AnnotationWriter.write(result: result, config: config, imageFileName: row.id + ".png",
                templateFamily: row.family, generatorVersion: "page-dot-repair-41", to: annotation)
            bytes += try Data(contentsOf: annotation).count
            if index % 50 == 0 { print("PAGE_REGEN_PROGRESS \(index + 1)/666 bytes=\(bytes)") }
        }
        let receipt: [String: Any] = ["count": 666, "catalogSHA256": digest,
            "runtimeOS": ProcessInfo.processInfo.operatingSystemVersionString,
            "seconds": ProcessInfo.processInfo.systemUptime - started, "bytes": bytes]
        try JSONSerialization.data(withJSONObject: receipt, options: [.sortedKeys, .prettyPrinted])
            .write(to: output.appendingPathComponent("receipt.json"), options: .withoutOverwriting)
        print("PAGE_REGEN_COMPLETE \(output.path)")
    }
}

@MainActor
final class KitchenSinkValidationTest: XCTestCase {

    /// Opt-in rendered regression: exercise both repaired templates, not a mock
    /// geometry formula. Attach evidence to the project-local xcresult only.
    func testPageDotIntrinsicGeometry() async throws {
        guard ProcessInfo.processInfo.environment["NUA_PAGE_DOT_PROBE"] == "1" else {
            throw XCTSkip("Select the bounded page-dot rendering probe explicitly")
        }
        for width in [375.0, 430.0] {
            for count in 2...5 {
                for family in ["MediaCardGrid", "ProgressActivity"] {
                    var corpus = ContentCorpus(seed: 40)
                    let view: AnyView
                    if family == "MediaCardGrid" {
                        var config = MediaCardGridConfig.make(seed: 40, corpus: &corpus)
                        config.pageCount = count
                        config.currentPage = 0
                        view = AnyView(MediaCardGridTemplate(config: config))
                    } else {
                        var config = ProgressActivityConfig.make(seed: 40, corpus: &corpus)
                        config.pageCount = count
                        config.currentPage = 0
                        view = AnyView(ProgressActivityTemplate(config: config))
                    }
                    let result = try await ScreenshotCapture.capture(view,
                        windowSize: CGSize(width: width, height: 1100), config: makeGeneratorConfig(seed: 40))
                    let dots = try XCTUnwrap(result.elements.first { $0.id == "pageControl_0" })
                    XCTAssertLessThan(dots.frame.width, width / 2, "Whole-row capture: \(family)")
                    XCTAssertGreaterThan(dots.frame.height, 0)
                    XCTAssertEqual(dots.frame.width, 10 + Double(count - 1) * 15, accuracy: 1)
                    XCTAssertEqual(dots.frame.height, 10, accuracy: 1)
                    let attachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
                    attachment.name = "\(family)-\(Int(width))-\(count)-raw"
                    attachment.lifetime = .keepAlways
                    add(attachment)
                    let overlay = XCTAttachment(data: BoundingBoxDebugRenderer.render(result), uniformTypeIdentifier: "public.png")
                    overlay.name = "\(family)-\(Int(width))-\(count)-bounds"
                    overlay.lifetime = .keepAlways
                    add(overlay)
                    print("PAGE_DOT_GEOMETRY \(family) width=\(width) count=\(count) bounds=\(dots.frame)")
                }
            }
        }
    }

    // MARK: - Expected element IDs

    /// Every element type that KitchenSinkTemplate must capture.
    /// If any of these is missing, the test fails before you even look at the image.
    private static let requiredElementTypes: Set<String> = [
        "navigationBar", "tabBar", "tabBarItem", "homeIndicator",
        "label", "imageView", "link",
        "primaryButton", "secondaryButton", "destructiveButton", "cancelAction",
        "toggle", "slider", "stepperControl",
        "textField", "secureField", "searchField",
        "segmentedControl", "picker",
        "menuButton", "colorWell", "pageControl",
        "activityIndicator", "progressView",
        "listRow", "disclosureGroup"
    ]

    // MARK: - Smoke test

    func testKitchenSinkBoundingBoxes() async throws {
        // Fixed seed so the same image is produced on every run.
        let seed: UInt64 = 9_999
        var corpus = ContentCorpus(seed: seed)
        let templateConfig = KitchenSinkConfig.make(seed: seed, corpus: &corpus)

        // Tall window so all content is rendered without scroll offset.
        let windowSize = CGSize(width: 393, height: 1100)
        let generatorConfig = makeGeneratorConfig(seed: seed)

        let result = try await ScreenshotCapture.capture(
            KitchenSinkTemplate(config: templateConfig),
            windowSize: windowSize,
            config: generatorConfig
        )

        // Attach clean PNG to test result — stored in .xcresult, never outside the project.
        let rawAttachment = XCTAttachment(data: result.png, uniformTypeIdentifier: "public.png")
        rawAttachment.name = "kitchen_sink_raw.png"
        rawAttachment.lifetime = .keepAlways
        add(rawAttachment)

        // Attach debug-annotated PNG (boxes + labels burned in).
        let debugPNG = BoundingBoxDebugRenderer.render(result)
        let debugAttachment = XCTAttachment(data: debugPNG, uniformTypeIdentifier: "public.png")
        debugAttachment.name = "kitchen_sink_debug.png"
        debugAttachment.lifetime = .keepAlways
        add(debugAttachment)

        // MARK: Structural assertions

        let capturedIDs   = Set(result.elements.map { $0.id })
        let capturedTypes = Set(result.elements.map { elementType(from: $0.id) })

        // 1. All required element types are present
        let missingTypes = Self.requiredElementTypes.subtracting(capturedTypes)
        XCTAssertTrue(
            missingTypes.isEmpty,
            "Missing element types in capture: \(missingTypes.sorted().joined(separator: ", "))"
        )

        // 2. No element has a zero-sized bounding box
        let zeroSized = result.elements.filter { $0.frame.width < 1 || $0.frame.height < 1 }
        XCTAssertTrue(
            zeroSized.isEmpty,
            "Zero-sized boxes for: \(zeroSized.map(\.id).joined(separator: ", "))"
        )

        // 3. No two elements have byte-identical frames (would indicate a capture duplication bug)
        var seen = Set<String>()
        var duplicateFrames: [String] = []
        for el in result.elements {
            let key = "\(el.frame.minX),\(el.frame.minY),\(el.frame.width),\(el.frame.height)"
            if seen.contains(key) { duplicateFrames.append(el.id) }
            seen.insert(key)
        }
        XCTAssertTrue(
            duplicateFrames.isEmpty,
            "Duplicate frames for: \(duplicateFrames.joined(separator: ", "))"
        )

        // 4. All element frames fall within the capture canvas (no negative or out-of-bounds coords)
        let canvasRect = CGRect(origin: .zero, size: windowSize)
        let outOfBounds = result.elements.filter {
            !canvasRect.contains($0.frame.origin) &&
            !canvasRect.intersects($0.frame)
        }
        XCTAssertTrue(
            outOfBounds.isEmpty,
            "Out-of-bounds frames for: \(outOfBounds.map(\.id).joined(separator: ", "))"
        )

        // 5. SHA-256 is a valid 64-char hex string
        XCTAssertEqual(result.sha256.count, 64)
        XCTAssertTrue(result.sha256.allSatisfy(\.isHexDigit))

        // Print summary to the test log for quick scan
        print("✅ KitchenSink captured \(result.elements.count) elements")
        print("   Attachments stored in .xcresult — open in Xcode test navigator to inspect.")

        for el in result.elements.sorted(by: { $0.id < $1.id }) {
            print(String(format: "   %-36s  (%.0f,%.0f) %.0f×%.0f",
                         (el.id as NSString).utf8String ?? "",
                         el.frame.minX, el.frame.minY,
                         el.frame.width, el.frame.height))
        }
    }

    // MARK: - Helpers

    private func makeGeneratorConfig(seed: UInt64) -> GeneratorRunConfig {
        GeneratorRunConfig(
            seed: seed,
            templateFamily: "KitchenSink",
            osProfile: .ios26,
            simulatorOverride: SimulatorStateOverride(
                time: "09:41",
                batteryLevel: 100,
                batteryState: "charging",
                cellularBars: 5,
                wifiBars: 3,
                cellularMode: "active",
                operatorName: ""
            ),
            colorScheme: .light,
            dynamicTypeSize: .large,
            deviceName: "iPhone 17 Pro",
            pixelScale: 3,
            locale: "en_US",
            layoutDirection: .ltr
        )
    }

    private func elementType(from id: String) -> String {
        String(id.split(separator: "_", maxSplits: 1).first ?? Substring(id))
    }
}

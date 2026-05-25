// ModelBenchmarkTests.swift
// GeneratorRunnerTests
//
// TASK-6-6: Physical device benchmark for NativeUIDetector_v1.
//
// Measures cold model load time, per-image inference latency (3-pass pipeline),
// model file size, and peak memory delta during inference.
//
// ── HOW TO RUN ──────────────────────────────────────────────────────────────
//
// 1. Add the trained model to the GeneratorRunner Xcode target:
//    - In Xcode: GeneratorRunner target → Build Phases → Copy Bundle Resources
//    - Add NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIDetector_v1.mlpackage.mlmodel
//    - (Also add it to GeneratorRunnerTests target so tests can find it in Bundle.main)
//
// 2. Select a physical iPhone (not Simulator) as the run destination.
//    ANE utilization only applies on physical hardware. Simulator results are not representative.
//
// 3. Run the benchmark scheme:
//    Product → Test (Cmd+U) or:
//    xcodebuild test \
//      -project GeneratorRunner/GeneratorRunner.xcodeproj \
//      -scheme GeneratorRunner \
//      -destination 'platform=iOS,name=<YourPhone>'
//
// 4. View results in Xcode → Report navigator → Test → Performance Results.
//
// ── ACCEPTANCE CRITERIA (TASK-6-6) ──────────────────────────────────────────
//
//   AC-1  Median per-image inference time < 200ms (full 3-pass pipeline)
//   AC-2  Cold model load time < 3s
//   AC-3  Model file size < 50MB
//   AC-4  Peak memory delta during inference < 200MB
//   AC-5  ANE utilization > 0% (verify via Instruments → Core ML Instrument,
//          manual test — not automatable in XCTest)
//
// ── MODEL NOT FOUND ─────────────────────────────────────────────────────────
//
// If NativeUIDetector_v1.mlmodelc is not in the bundle, all tests call XCTSkip.
// This means the file compiles and the test suite shows "skipped" rather than
// failing. To convert skips to failures for CI, replace XCTSkip with XCTFail.
//
// ── TEST IMAGE RATIONALE ────────────────────────────────────────────────────
//
// Tests generate 10 synthetic CGImages at 1179×2556px (iPhone 14 Pro @3x, portrait)
// with varied solid-colour fills. Real content doesn't matter for latency measurement.
// All images are generated in setUp so they don't inflate the measured block.

import XCTest
import Vision
import CoreML
import CoreGraphics
import CoreFoundation

// MARK: - ModelBenchmarkTests

final class ModelBenchmarkTests: XCTestCase {

    // MARK: Shared state

    /// Path to the compiled model; nil if not bundled.
    private var modelURL: URL?

    /// Pre-generated test images (1179×2556, solid fill, varied colours).
    private var testImages: [CGImage] = []

    private static let imageWidth  = 1179
    private static let imageHeight = 2556
    private static let imageCount  = 10

    // MARK: - setUp / tearDown

    override func setUp() async throws {
        try await super.setUp()

        // Locate compiled model in test bundle.
        // Xcode compiles .mlmodel → .mlmodelc at build time.
        modelURL = Bundle.main.url(forResource: "NativeUIDetector_v1.mlpackage",
                                   withExtension: "mlmodelc")
                ?? Bundle.main.url(forResource: "NativeUIDetector_v1",
                                   withExtension: "mlmodelc")

        // Pre-generate synthetic test images.
        testImages = Self.makeSyntheticImages(count: Self.imageCount)
    }

    override func tearDown() async throws {
        modelURL  = nil
        testImages = []
        try await super.tearDown()
    }

    // MARK: - AC-3: Model File Size

    func testModelFileSize() throws {
        guard let url = modelURL else {
            throw XCTSkip("NativeUIDetector_v1.mlmodelc not found in bundle. Add the model to the test target's Copy Bundle Resources phase.")
        }

        let size = try directorySize(at: url)
        let sizeInMB = Double(size) / (1024 * 1024)

        XCTAssertLessThan(
            sizeInMB, 50.0,
            "Model file size \(String(format: "%.1f", sizeInMB))MB exceeds 50MB AC limit."
        )

        print("Model size: \(String(format: "%.1f", sizeInMB))MB")
    }

    // MARK: - AC-2: Cold Load Time

    /// Measures model load from disk each iteration (cold load — no warm cache assumed).
    ///
    /// Target: < 3s per iteration.
    /// Each measurement iteration loads a fresh MLModel + VNCoreMLModel.
    func testColdModelLoadTime() throws {
        guard let url = modelURL else {
            throw XCTSkip("NativeUIDetector_v1.mlmodelc not found in bundle.")
        }

        let options = XCTMeasureOptions()
        options.iterationCount = 5   // 5 cold loads; median reported

        measure(metrics: [XCTClockMetric()], options: options) {
            do {
                let mlModel = try MLModel(contentsOf: url)
                _ = try VNCoreMLModel(for: mlModel)
            } catch {
                XCTFail("Model load failed: \(error)")
            }
        }
    }

    // MARK: - AC-1: Inference Latency Per Image

    /// Measures the full 3-pass inference pipeline for each of the 10 test images.
    ///
    /// Passes:
    ///   1. Full image  (.scaleFill) — large elements (alert)
    ///   2. SAHI tiles  (640×640, 480px stride, 2× upscale) — medium/small elements
    ///   3. Horizontal strips (22% height, 50% overlap) — full-width thin elements
    ///
    /// Target: median wall-clock time across all iterations < 200ms per image.
    ///
    /// The model is loaded ONCE outside the measured block. The measurement
    /// covers only inference (matching the production `perform(on:sidecar:)` path).
    func testInferenceLatencyPerImage() throws {
        guard let url = modelURL else {
            throw XCTSkip("NativeUIDetector_v1.mlmodelc not found in bundle.")
        }

        let mlModel  = try MLModel(contentsOf: url)
        let vnModel  = try VNCoreMLModel(for: mlModel)
        let images   = testImages   // captured before measurement

        let options = XCTMeasureOptions()
        options.iterationCount = 5  // 5 × 10-image runs; Xcode reports median

        measure(metrics: [XCTClockMetric()], options: options) {
            for image in images {
                do {
                    _ = try Self.runThreePassInference(image: image, model: vnModel)
                } catch {
                    XCTFail("Inference failed: \(error)")
                }
            }
        }

        // Note: XCTClockMetric reports the total block time across all images.
        // Divide by imageCount to derive per-image median when reading results.
        // E.g. total block = 1.2s → 120ms per image.
        print("Divide total measured time by \(Self.imageCount) for per-image latency.")
    }

    // MARK: - AC-4: Peak Memory Delta

    /// Measures peak memory allocation during a single 10-image inference run.
    ///
    /// Target: peak memory delta < 200MB.
    func testPeakMemoryDuringInference() throws {
        guard let url = modelURL else {
            throw XCTSkip("NativeUIDetector_v1.mlmodelc not found in bundle.")
        }

        let mlModel = try MLModel(contentsOf: url)
        let vnModel = try VNCoreMLModel(for: mlModel)
        let images  = testImages

        let options = XCTMeasureOptions()
        options.iterationCount = 3

        measure(metrics: [XCTMemoryMetric()], options: options) {
            for image in images {
                _ = try? Self.runThreePassInference(image: image, model: vnModel)
            }
        }
    }

    // MARK: - Inference latency per-pass breakdown (diagnostic, not AC)

    /// Reports per-pass timing to inform which pass dominates latency.
    /// Not a pass/fail assertion — used to guide optimisation decisions.
    func testPerPassLatencyBreakdown() throws {
        guard let url = modelURL else {
            throw XCTSkip("NativeUIDetector_v1.mlmodelc not found in bundle.")
        }

        let mlModel = try MLModel(contentsOf: url)
        let vnModel = try VNCoreMLModel(for: mlModel)
        let image   = testImages[0]

        let passNames: [String]   = ["Full-image", "SAHI tiles", "Horizontal strips"]
        let passes:    [() throws -> [VNRecognizedObjectObservation]] = [
            { try Self.fullImagePass(image: image, model: vnModel) },
            { try Self.sahiTilePass(image: image, model: vnModel)  },
            { try Self.stripPass(image: image, model: vnModel)     }
        ]

        print("── Per-pass latency breakdown (single image) ─────────────────────")
        for (name, pass) in zip(passNames, passes) {
            let start = CFAbsoluteTimeGetCurrent()
            _ = try pass()
            let elapsed = (CFAbsoluteTimeGetCurrent() - start) * 1000
            print("  \(name.padding(toLength: 18, withPad: " ", startingAt: 0)): \(String(format: "%.1f", elapsed))ms")
        }
        print("──────────────────────────────────────────────────────────────────")
    }
}

// MARK: - Inference implementation (mirrors NativeUIDetectionRequest internals)
//
// These methods replicate the three-pass logic from
// Sources/NativeUIAuditKit/Detection/NativeUIDetectionRequest.swift
// without importing NativeUIAuditKit (keeps the test target self-contained).

private extension ModelBenchmarkTests {

    // MARK: Three-pass entry point

    static func runThreePassInference(
        image: CGImage,
        model: VNCoreMLModel
    ) throws -> [VNRecognizedObjectObservation] {
        var all: [VNRecognizedObjectObservation] = []
        all += try fullImagePass(image: image, model: model)
        all += try sahiTilePass(image: image, model: model)
        all += try stripPass(image: image, model: model)
        return nms(all, iouThreshold: 0.45)
    }

    // MARK: Pass 1 — Full image

    static func fullImagePass(
        image: CGImage,
        model: VNCoreMLModel
    ) throws -> [VNRecognizedObjectObservation] {
        return try runRequest(on: image, model: model, scaleFill: true)
    }

    // MARK: Pass 2 — SAHI 640×640 tiles

    static func sahiTilePass(
        image: CGImage,
        model: VNCoreMLModel
    ) throws -> [VNRecognizedObjectObservation] {

        let scale:    Int = 2
        let tileSize: Int = 640
        let stride:   Int = 480

        guard let upscaled = upscale(image, factor: scale) else { return [] }
        let W = upscaled.width
        let H = upscaled.height

        var result: [VNRecognizedObjectObservation] = []

        var y = 0
        while y < H {
            let tileH = min(tileSize, H - y)
            var x = 0
            while x < W {
                let tileW = min(tileSize, W - x)
                guard let tile = crop(upscaled, x: x, y: y, w: tileW, h: tileH) else {
                    x += stride; continue
                }
                let obs = try runRequest(on: tile, model: model, scaleFill: true)
                // Remap tile-local Vision coords back to full-image Vision coords
                let remapped = obs.map { remap($0, tileX: x, tileY: y,
                                                tileW: tileW, tileH: tileH,
                                                fullW: W, fullH: H) }
                result += remapped
                x += stride
            }
            y += stride
        }
        return result
    }

    // MARK: Pass 3 — Horizontal strips (22% height, 50% overlap)

    static func stripPass(
        image: CGImage,
        model: VNCoreMLModel
    ) throws -> [VNRecognizedObjectObservation] {

        let imageH     = image.height
        let imageW     = image.width
        let stripH     = max(1, Int(Double(imageH) * 0.22))
        let stride     = max(1, stripH / 2)

        var result: [VNRecognizedObjectObservation] = []
        var y = 0
        while y + stripH <= imageH {
            guard let strip = crop(image, x: 0, y: y, w: imageW, h: stripH) else {
                y += stride; continue
            }
            let obs = try runRequest(on: strip, model: model, scaleFill: true)

            // Remap strip-local Vision coords → full-image Vision coords
            // Vision uses bottom-left origin; strip occupies rows [y, y+stripH) from top.
            let stripTopVision    = 1.0 - Double(y + stripH) / Double(imageH)
            let stripHeightVision = Double(stripH) / Double(imageH)
            let remappedStrips = obs.map { o -> VNRecognizedObjectObservation in
                let b = o.boundingBox
                let fullY = stripTopVision + b.minY * stripHeightVision
                let fullH = b.height * stripHeightVision
                let mapped = CGRect(x: b.minX, y: fullY, width: b.width, height: fullH)
                return VNRecognizedObjectObservation(boundingBox: mapped)
            }
            result += remappedStrips
            y += stride
        }
        return result
    }

    // MARK: - Vision request helper

    static func runRequest(
        on image: CGImage,
        model: VNCoreMLModel,
        scaleFill: Bool
    ) throws -> [VNRecognizedObjectObservation] {
        let req = VNCoreMLRequest(model: model)
        req.imageCropAndScaleOption = scaleFill ? .scaleFill : .scaleFit   // always .scaleFill — see BP-25
        let handler = VNImageRequestHandler(cgImage: image, options: [:])
        try handler.perform([req])
        return req.results as? [VNRecognizedObjectObservation] ?? []
    }

    // MARK: - NMS

    static func nms(
        _ obs: [VNRecognizedObjectObservation],
        iouThreshold: Double
    ) -> [VNRecognizedObjectObservation] {
        let sorted = obs.sorted { $0.confidence > $1.confidence }
        var kept: [VNRecognizedObjectObservation] = []
        var suppressed = Set<Int>()
        for (i, a) in sorted.enumerated() {
            if suppressed.contains(i) { continue }
            kept.append(a)
            for (j, b) in sorted.enumerated() where j > i {
                if suppressed.contains(j) { continue }
                // Suppress only if same top label
                guard a.labels.first?.identifier == b.labels.first?.identifier else { continue }
                if iou(a.boundingBox, b.boundingBox) > iouThreshold {
                    suppressed.insert(j)
                }
            }
        }
        return kept
    }

    static func iou(_ a: CGRect, _ b: CGRect) -> Double {
        let inter = a.intersection(b)
        guard !inter.isNull && inter.width > 0 && inter.height > 0 else { return 0 }
        let interArea = Double(inter.width * inter.height)
        let unionArea = Double(a.width * a.height) + Double(b.width * b.height) - interArea
        return unionArea > 0 ? interArea / unionArea : 0
    }

    // MARK: - Image helpers

    /// Upscales a CGImage by integer factor using CGContext.
    static func upscale(_ image: CGImage, factor: Int) -> CGImage? {
        let w = image.width * factor
        let h = image.height * factor
        guard let ctx = CGContext(
            data: nil, width: w, height: h,
            bitsPerComponent: 8, bytesPerRow: 0,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
        ) else { return nil }
        ctx.interpolationQuality = .none
        ctx.draw(image, in: CGRect(x: 0, y: 0, width: w, height: h))
        return ctx.makeImage()
    }

    /// Crops a rectangle from a CGImage. Origin is top-left (pixel coords).
    static func crop(_ image: CGImage, x: Int, y: Int, w: Int, h: Int) -> CGImage? {
        guard let ctx = CGContext(
            data: nil, width: w, height: h,
            bitsPerComponent: 8, bytesPerRow: 0,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
        ) else { return nil }
        // CGContext draws with bottom-left origin; to expose rows [y, y+h) from top:
        let drawY = -(image.height - y - h)
        ctx.draw(image, in: CGRect(x: -x, y: drawY, width: image.width, height: image.height))
        return ctx.makeImage()
    }

    /// Remaps a SAHI tile observation's Vision coords to full-upscaled-image Vision coords.
    static func remap(
        _ obs: VNRecognizedObjectObservation,
        tileX: Int, tileY: Int,
        tileW: Int, tileH: Int,
        fullW: Int, fullH: Int
    ) -> VNRecognizedObjectObservation {
        let b = obs.boundingBox
        // Vision coords: bottom-left origin, y increases upward.
        let tileBotVision  = 1.0 - Double(tileY + tileH) / Double(fullH)
        let tileHNorm      = Double(tileH) / Double(fullH)
        let tileXNorm      = Double(tileX) / Double(fullW)
        let tileWNorm      = Double(tileW) / Double(fullW)

        let fullX = tileXNorm + b.minX * tileWNorm
        let fullY = tileBotVision + b.minY * tileHNorm
        let fullW_ = b.width  * tileWNorm
        let fullH_ = b.height * tileHNorm

        return VNRecognizedObjectObservation(
            boundingBox: CGRect(x: fullX, y: fullY, width: fullW_, height: fullH_)
        )
    }

    // MARK: - Synthetic image factory

    /// Generates `count` solid-fill CGImages at 1179×2556 (iPhone 14 Pro @3x portrait).
    /// Colours cycle through a fixed palette so images are visually distinct.
    static func makeSyntheticImages(count: Int) -> [CGImage] {
        // 10 neutral colours — varied enough to exercise different pixel distributions
        // without introducing any content that would skew model activation patterns.
        let fills: [(CGFloat, CGFloat, CGFloat)] = [
            (0.95, 0.95, 0.95),   // near-white
            (0.10, 0.10, 0.12),   // near-black
            (0.88, 0.92, 0.98),   // light blue-grey
            (0.15, 0.15, 0.20),   // dark blue-grey
            (0.96, 0.90, 0.88),   // light warm
            (0.12, 0.18, 0.14),   // dark green
            (0.92, 0.92, 0.92),   // mid-grey light
            (0.20, 0.20, 0.20),   // mid-grey dark
            (0.98, 0.96, 0.90),   // cream
            (0.14, 0.14, 0.22),   // dark indigo
        ]

        var images: [CGImage] = []
        for i in 0..<count {
            let (r, g, b) = fills[i % fills.count]
            guard let img = makeSolidImage(
                width:  imageWidth,
                height: imageHeight,
                r: r, g: g, b: b
            ) else { continue }
            images.append(img)
        }
        return images
    }

    static func makeSolidImage(
        width: Int, height: Int,
        r: CGFloat, g: CGFloat, b: CGFloat
    ) -> CGImage? {
        guard let ctx = CGContext(
            data: nil,
            width: width, height: height,
            bitsPerComponent: 8, bytesPerRow: 0,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
        ) else { return nil }
        ctx.setFillColor(CGColor(red: r, green: g, blue: b, alpha: 1.0))
        ctx.fill(CGRect(x: 0, y: 0, width: width, height: height))
        return ctx.makeImage()
    }

    // MARK: - File size helper

    /// Recursively sums file sizes for a file or directory.
    func directorySize(at url: URL) throws -> Int {
        let fm = FileManager.default
        guard let enumerator = fm.enumerator(
            at: url,
            includingPropertiesForKeys: [.fileSizeKey],
            options: .skipsHiddenFiles
        ) else { return 0 }

        var total = 0
        for case let fileURL as URL in enumerator {
            let attrs = try fileURL.resourceValues(forKeys: [.fileSizeKey])
            total += attrs.fileSize ?? 0
        }
        return total
    }
}

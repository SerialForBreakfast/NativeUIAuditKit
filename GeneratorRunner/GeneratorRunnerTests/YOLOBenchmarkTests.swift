// YOLOBenchmarkTests.swift
// GeneratorRunnerTests
//
// Physical-device latency benchmark for the YOLO11n CoreML model (best.mlpackage).
//
// Uses direct MLModel inference with letterbox preprocessing — no Vision framework.
// This matches the eval_yolo_map.swift evaluation path and the on-device deployment model.
//
// ── HOW TO RUN ──────────────────────────────────────────────────────────────
//
// 1. Add the model to the test bundle (one-time Xcode setup):
//    GeneratorRunnerTests target → Build Phases → Copy Bundle Resources → +
//    Add: NativeUITrainer/yolo_runs/yolo11n_e100/weights/best.mlpackage
//    Xcode compiles it to best.mlmodelc in the bundle at build time.
//
// 2. Select a physical iPhone (not Simulator) as the run destination.
//    ANE utilization only applies on physical hardware.
//
// 3. Run tests:
//    Product → Test (Cmd+U)  — or —
//    xcodebuild test \
//      -project GeneratorRunner/GeneratorRunner.xcodeproj \
//      -scheme GeneratorRunner \
//      -destination 'platform=iOS,name=<YourPhone>' \
//      -only-testing:GeneratorRunnerTests/YOLOBenchmarkTests
//
// 4. View results in Xcode → Report navigator → Tests → Performance Results.
//    Divide total measured block time by imageCount to get per-image latency.
//
// ── ACCEPTANCE CRITERIA ──────────────────────────────────────────────────────
//
//   AC-1  Median per-image inference time < 200ms (single-pass YOLO pipeline)
//   AC-2  Cold model load time < 3s
//   AC-3  Model file size < 15MB (YOLO11n CoreML is ~5MB)
//   AC-4  Peak memory delta during inference < 200MB
//
// ── MODEL NOT FOUND ──────────────────────────────────────────────────────────
//
// If best.mlmodelc is not in the bundle, all tests call XCTSkip.
// Add the model to Copy Bundle Resources (Step 1 above).

import XCTest
import CoreML
import CoreGraphics
import CoreFoundation
import CoreVideo

final class YOLOBenchmarkTests: XCTestCase {

    private var modelURL: URL?
    private var testImages: [CGImage] = []

    private static let imageWidth  = 1179
    private static let imageHeight = 2556
    private static let imageCount  = 10
    private static let yoloImgSize = 640

    // MARK: - Class names (must match training order)

    private static let classNames = ["alert", "navigationBar", "primaryButton", "textField", "toggle"]

    // MARK: - setUp / tearDown

    override func setUp() async throws {
        try await super.setUp()
        let bundle = Bundle(for: YOLOBenchmarkTests.self)
        modelURL = bundle.url(forResource: "best.mlpackage", withExtension: "mlmodelc")
                ?? bundle.url(forResource: "best", withExtension: "mlmodelc")
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
            throw XCTSkip("best.mlmodelc not found in bundle. Add best.mlpackage to Copy Bundle Resources.")
        }
        let sizeBytes = try directorySize(at: url)
        let sizeMB = Double(sizeBytes) / (1024 * 1024)
        XCTAssertLessThan(sizeMB, 15.0,
            "YOLO model \(String(format: "%.1f", sizeMB))MB exceeds 15MB limit.")
        print("YOLO model size: \(String(format: "%.2f", sizeMB))MB")
    }

    // MARK: - AC-2: Cold Load Time

    func testColdModelLoadTime() throws {
        guard let url = modelURL else {
            throw XCTSkip("best.mlmodelc not found in bundle.")
        }
        let options = XCTMeasureOptions()
        options.iterationCount = 5
        measure(metrics: [XCTClockMetric()], options: options) {
            do {
                _ = try MLModel(contentsOf: url)
            } catch {
                XCTFail("YOLO model load failed: \(error)")
            }
        }
    }

    // MARK: - AC-1: Per-Image Inference Latency

    /// Single-pass YOLO inference: letterbox → MLModel.prediction → parse outputs.
    /// Target: median per-image time < 200ms.
    func testInferenceLatencyPerImage() throws {
        guard let url = modelURL else {
            throw XCTSkip("best.mlmodelc not found in bundle.")
        }
        let model  = try MLModel(contentsOf: url)
        let images = testImages

        let options = XCTMeasureOptions()
        options.iterationCount = 5   // 5 × 10-image runs; Xcode reports median

        measure(metrics: [XCTClockMetric()], options: options) {
            for image in images {
                _ = try? Self.runYOLOInference(image: image, model: model)
            }
        }
        print("Divide total measured time by \(Self.imageCount) for per-image latency.")
    }

    // MARK: - AC-4: Peak Memory Delta

    func testPeakMemoryDuringInference() throws {
        guard let url = modelURL else {
            throw XCTSkip("best.mlmodelc not found in bundle.")
        }
        let model  = try MLModel(contentsOf: url)
        let images = testImages

        let options = XCTMeasureOptions()
        options.iterationCount = 3

        measure(metrics: [XCTMemoryMetric()], options: options) {
            for image in images {
                _ = try? Self.runYOLOInference(image: image, model: model)
            }
        }
    }

    // MARK: - Per-call breakdown (diagnostic)

    /// Prints timing for letterbox, model.prediction, and output parsing separately.
    func testPerStepLatencyBreakdown() throws {
        guard let url = modelURL else {
            throw XCTSkip("best.mlmodelc not found in bundle.")
        }
        let model = try MLModel(contentsOf: url)
        let image = testImages[0]

        var lbMs: Double = 0, inferMs: Double = 0, parseMs: Double = 0

        // Letterbox
        var t = CFAbsoluteTimeGetCurrent()
        guard let lb = Self.letterbox(image) else { XCTFail("letterbox failed"); return }
        lbMs = (CFAbsoluteTimeGetCurrent() - t) * 1000

        guard let pixelBuf = Self.makePixelBuffer(lb.image) else { XCTFail("pixelBuf failed"); return }
        let input = try MLDictionaryFeatureProvider(dictionary: [
            "image":               MLFeatureValue(pixelBuffer: pixelBuf),
            "iouThreshold":        MLFeatureValue(double: 0.45),
            "confidenceThreshold": MLFeatureValue(double: 0.001),
        ])

        // Inference
        t = CFAbsoluteTimeGetCurrent()
        let output = try model.prediction(from: input)
        inferMs = (CFAbsoluteTimeGetCurrent() - t) * 1000

        // Parse
        t = CFAbsoluteTimeGetCurrent()
        _ = Self.parseOutput(output, lb: lb)
        parseMs = (CFAbsoluteTimeGetCurrent() - t) * 1000

        print("── YOLO per-step latency (single 1179×2556 image) ──")
        print("  Letterbox + CVPixelBuffer : \(String(format: "%.1f", lbMs))ms")
        print("  MLModel.prediction        : \(String(format: "%.1f", inferMs))ms")
        print("  Output parsing            : \(String(format: "%.1f", parseMs))ms")
        print("  Total                     : \(String(format: "%.1f", lbMs + inferMs + parseMs))ms")
    }
}

// MARK: - YOLO inference implementation

private extension YOLOBenchmarkTests {

    struct LetterboxResult {
        let image: CGImage
        let newW, newH, padX, padY: Int
    }

    struct Detection {
        let label: String
        let conf: Float
        let cx, cy, w, h: Double
    }

    // MARK: Top-level inference

    static func runYOLOInference(image: CGImage, model: MLModel) throws -> [Detection] {
        guard let lb = letterbox(image), let pxBuf = makePixelBuffer(lb.image) else { return [] }
        let input = try MLDictionaryFeatureProvider(dictionary: [
            "image":               MLFeatureValue(pixelBuffer: pxBuf),
            "iouThreshold":        MLFeatureValue(double: 0.45),
            "confidenceThreshold": MLFeatureValue(double: 0.001),
        ])
        let output = try model.prediction(from: input)
        return parseOutput(output, lb: lb)
    }

    // MARK: Letterbox (640×640, gray fill 114,114,114)

    static func letterbox(_ source: CGImage) -> LetterboxResult? {
        let origW  = Double(source.width)
        let origH  = Double(source.height)
        let scale  = min(Double(yoloImgSize) / origW, Double(yoloImgSize) / origH)
        let newW   = Int(origW * scale)
        let newH   = Int(origH * scale)
        let padX   = (yoloImgSize - newW) / 2
        let padY   = (yoloImgSize - newH) / 2

        guard let ctx = CGContext(
            data: nil, width: yoloImgSize, height: yoloImgSize,
            bitsPerComponent: 8, bytesPerRow: 0,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
        ) else { return nil }

        ctx.setFillColor(CGColor(red: 114/255.0, green: 114/255.0, blue: 114/255.0, alpha: 1.0))
        ctx.fill(CGRect(x: 0, y: 0, width: yoloImgSize, height: yoloImgSize))
        ctx.draw(source, in: CGRect(x: padX, y: padY, width: newW, height: newH))

        guard let boxed = ctx.makeImage() else { return nil }
        return LetterboxResult(image: boxed, newW: newW, newH: newH, padX: padX, padY: padY)
    }

    // MARK: CVPixelBuffer from CGImage

    static func makePixelBuffer(_ image: CGImage) -> CVPixelBuffer? {
        let attrs = [
            kCVPixelBufferCGImageCompatibilityKey: true,
            kCVPixelBufferCGBitmapContextCompatibilityKey: true,
        ] as CFDictionary
        var buf: CVPixelBuffer?
        guard CVPixelBufferCreate(kCFAllocatorDefault, image.width, image.height,
                                  kCVPixelFormatType_32BGRA, attrs, &buf) == kCVReturnSuccess,
              let pixelBuf = buf else { return nil }

        CVPixelBufferLockBaseAddress(pixelBuf, [])
        defer { CVPixelBufferUnlockBaseAddress(pixelBuf, []) }

        guard let ctx = CGContext(
            data: CVPixelBufferGetBaseAddress(pixelBuf),
            width: image.width, height: image.height,
            bitsPerComponent: 8,
            bytesPerRow: CVPixelBufferGetBytesPerRow(pixelBuf),
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue
        ) else { return nil }

        ctx.draw(image, in: CGRect(x: 0, y: 0, width: image.width, height: image.height))
        return pixelBuf
    }

    // MARK: Output parsing

    /// Parses confidence [N, 80] + coordinates [N, 4] → Detection list.
    /// Inverse-letterboxes coordinates back to original image space.
    static func parseOutput(_ output: MLFeatureProvider, lb: LetterboxResult) -> [Detection] {
        guard let confArr  = output.featureValue(for: "confidence")?.multiArrayValue,
              let coordArr = output.featureValue(for: "coordinates")?.multiArrayValue else { return [] }

        let n      = confArr.shape[0].intValue
        let nTotal = confArr.shape[1].intValue
        let nCheck = min(classNames.count, nTotal)

        let cs0 = confArr.strides[0].intValue
        let cs1 = confArr.strides[1].intValue
        let xs0 = coordArr.strides[0].intValue

        let sz    = Double(yoloImgSize)
        let nwD   = Double(lb.newW)
        let nhD   = Double(lb.newH)
        let pxD   = Double(lb.padX)
        let pyD   = Double(lb.padY)

        var dets: [Detection] = []
        for i in 0..<n {
            var bestConf: Float = 0
            var bestClass = 0
            for c in 0..<nCheck {
                let v = confArr[i * cs0 + c * cs1].floatValue
                if v > bestConf { bestConf = v; bestClass = c }
            }
            guard bestConf > 0.001 else { continue }

            let cx = (coordArr[i * xs0 + 0].doubleValue * sz - pxD) / nwD
            let cy = (coordArr[i * xs0 + 1].doubleValue * sz - pyD) / nhD
            let w  =  coordArr[i * xs0 + 2].doubleValue * sz / nwD
            let h  =  coordArr[i * xs0 + 3].doubleValue * sz / nhD

            dets.append(Detection(label: classNames[bestClass], conf: bestConf,
                                  cx: cx, cy: cy, w: w, h: h))
        }
        return dets
    }

    // MARK: - Synthetic test image factory

    static func makeSyntheticImages(count: Int) -> [CGImage] {
        let fills: [(CGFloat, CGFloat, CGFloat)] = [
            (0.95, 0.95, 0.95), (0.10, 0.10, 0.12),
            (0.88, 0.92, 0.98), (0.15, 0.15, 0.20),
            (0.96, 0.90, 0.88), (0.12, 0.18, 0.14),
            (0.92, 0.92, 0.92), (0.20, 0.20, 0.20),
            (0.98, 0.96, 0.90), (0.14, 0.14, 0.22),
        ]
        return (0..<count).compactMap { i in
            let (r, g, b) = fills[i % fills.count]
            guard let ctx = CGContext(
                data: nil, width: imageWidth, height: imageHeight,
                bitsPerComponent: 8, bytesPerRow: 0,
                space: CGColorSpaceCreateDeviceRGB(),
                bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
            ) else { return nil }
            ctx.setFillColor(CGColor(red: r, green: g, blue: b, alpha: 1.0))
            ctx.fill(CGRect(x: 0, y: 0, width: imageWidth, height: imageHeight))
            return ctx.makeImage()
        }
    }

    // MARK: - File size helper

    func directorySize(at url: URL) throws -> Int {
        guard let enumerator = FileManager.default.enumerator(
            at: url, includingPropertiesForKeys: [.fileSizeKey], options: .skipsHiddenFiles
        ) else { return 0 }
        var total = 0
        for case let fileURL as URL in enumerator {
            total += (try? fileURL.resourceValues(forKeys: [.fileSizeKey]).fileSize) ?? 0
        }
        return total
    }
}

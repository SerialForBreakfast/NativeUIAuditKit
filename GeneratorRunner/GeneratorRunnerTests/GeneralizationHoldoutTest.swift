// GeneralizationHoldoutTest.swift
// GeneratorRunnerTests
//
// Generalization check for the shipped YOLO11n model (nativeui-ios-v2.0, mAP@0.5 = 0.935
// on the in-distribution validation set — see Research/ExperimentLog.md Run 006).
//
// That 0.935 figure was measured on a random 8:1:1 split WITHIN each of the 51 trained
// template families (confirmed via the dataset manifest — every family appears in all
// three splits). It says nothing about how the model performs on a template layout it has
// never seen at all. This test answers that narrower question cheaply: generate a batch of
// images from AnalyticsDashboardTemplate.swift — a template deliberately never registered
// in GenerateDatasetTests' dispatcher, so zero images from it exist anywhere in the
// training/validation/test manifest — and run the already-trained model against them.
//
// This is NOT a substitute for true family-holdout retraining (deferred to Phase 6a per
// QG-5's own comment in DatasetQualityAuditTests.swift). It answers a narrower, cheaper
// question: does the CURRENTLY SHIPPED model's accuracy hold up on a genuinely novel
// layout, or does it collapse? See Tasks.md Phase 6d-adjacent notes / ExperimentLog.md for
// how this result should be read.
//
// Run individually:
//   xcodebuild test … -only-testing:GeneratorRunnerTests/GeneralizationHoldoutTest

import XCTest
import CoreML
import CoreGraphics
import CoreVideo
import UIKit

@MainActor
final class GeneralizationHoldoutTest: XCTestCase {

    private static let seedCount = 40
    private static let yoloImgSize = 640
    private static let classLabels = ["alert", "navigationBar", "primaryButton", "textField", "toggle"]
    private static let nmsIoUThreshold = 0.30
    private static let iouMatchThreshold = 0.5
    private static let confFloor: Float = 0.001

    func testHoldoutGeneralization() async throws {
        let bundle = Bundle(for: GeneralizationHoldoutTest.self)
        guard let modelURL = bundle.url(forResource: "best.mlpackage", withExtension: "mlmodelc")
                ?? bundle.url(forResource: "best", withExtension: "mlmodelc") else {
            throw XCTSkip("best.mlmodelc not found in test bundle — see YOLOBenchmarkTests.swift setup notes.")
        }
        let model = try MLModel(contentsOf: modelURL)

        var corpus = ContentCorpus(seed: 777)
        var classPredictions: [String: [(conf: Float, isTP: Bool)]] = [:]
        var classGTCount: [String: Int] = [:]
        var imagesProcessed = 0

        for seed in UInt64(0)..<UInt64(Self.seedCount) {
            let dashConfig = AnalyticsDashboardConfig.make(seed: seed, corpus: &corpus)
            let runConfig = GeneratorRunConfig(
                seed: seed,
                templateFamily: "AnalyticsDashboard_HOLDOUT",
                osProfile: .ios26,
                simulatorOverride: SimulatorStateOverride(
                    time: "09:41", batteryLevel: 100, batteryState: "charging",
                    cellularBars: 5, wifiBars: 3, cellularMode: "active", operatorName: ""
                ),
                colorScheme: dashConfig.colorScheme == .dark ? .dark : .light,
                dynamicTypeSize: .large,
                deviceName: "Test Device",
                pixelScale: 3,
                locale: "en_US",
                layoutDirection: .ltr
            )

            let result = try await ScreenshotCapture.capture(
                AnalyticsDashboardTemplate(config: dashConfig), config: runConfig
            )

            // Ground truth: top-left point frame -> top-left-origin normalized center-form,
            // matching the model's prediction convention (see NativeUIDetectionRequest.swift).
            var gts: [GTBox] = []
            for elem in result.elements {
                guard Self.classLabels.contains(elem.elementType) else { continue }
                classGTCount[elem.elementType, default: 0] += 1
                let nx = elem.frame.minX / result.pointSize.width
                let ny = elem.frame.minY / result.pointSize.height
                let nw = elem.frame.width / result.pointSize.width
                let nh = elem.frame.height / result.pointSize.height
                gts.append(GTBox(label: elem.elementType, cx: nx + nw / 2, cy: ny + nh / 2, w: nw, h: nh))
            }
            guard !gts.isEmpty else { continue }

            guard let uiImage = UIImage(data: result.png), let cgImage = uiImage.cgImage else {
                XCTFail("Seed \(seed): could not decode captured PNG")
                continue
            }

            let rawPreds = try Self.runYOLO(cgImage, model: model)
            let preds = Self.nms(rawPreds, iouThreshold: Self.nmsIoUThreshold)

            var matchedGTs = Set<Int>()
            for pred in preds.sorted(by: { $0.confidence > $1.confidence }) {
                var bestIoU = 0.0, bestIdx = -1
                for (gi, gt) in gts.enumerated() {
                    guard gt.label == pred.label, !matchedGTs.contains(gi) else { continue }
                    let score = Self.iou(gt, pred)
                    if score > bestIoU { bestIoU = score; bestIdx = gi }
                }
                let isTP = bestIoU >= Self.iouMatchThreshold
                if isTP { matchedGTs.insert(bestIdx) }
                classPredictions[pred.label, default: []].append((conf: pred.confidence, isTP: isTP))
            }
            imagesProcessed += 1
        }

        XCTAssertGreaterThan(imagesProcessed, 0, "No holdout images were processed")

        var apSum = 0.0
        var apCount = 0
        print("── Generalization holdout: AnalyticsDashboardTemplate (\(imagesProcessed) images, never in train/val/test) ──")
        for label in Self.classLabels {
            guard let nGT = classGTCount[label], nGT > 0 else { continue }
            let dets = classPredictions[label] ?? []
            let ap = Self.computeAP(detections: dets, nGT: nGT)
            apSum += ap
            apCount += 1
            print("  \(label): AP@0.5 = \(String(format: "%.3f", ap))  (GT=\(nGT), preds=\(dets.count))")
        }
        let holdoutMAP = apCount > 0 ? apSum / Double(apCount) : 0
        print("  mAP@0.5 (holdout) = \(String(format: "%.3f", holdoutMAP))")
        print("  mAP@0.5 (in-distribution baseline, Run 006) = 0.935")
        print("  Δ = \(String(format: "%+.3f", holdoutMAP - 0.935))")
    }
}

// MARK: - YOLO inference (ported from scripts/eval_yolo_map.swift / YOLOBenchmarkTests.swift)

private extension GeneralizationHoldoutTest {

    struct LetterboxResult {
        let image: CGImage
        let newW, newH, padX, padY: Int
    }

    struct Detection {
        let label: String
        let confidence: Float
        let cx, cy, w, h: Double
    }

    struct GTBox {
        let label: String
        let cx, cy, w, h: Double
    }

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

    static func runYOLO(_ image: CGImage, model: MLModel) throws -> [Detection] {
        guard let lb = letterbox(image), let pixelBuf = makePixelBuffer(lb.image) else { return [] }
        let input = try MLDictionaryFeatureProvider(dictionary: [
            "image":               MLFeatureValue(pixelBuffer: pixelBuf),
            "iouThreshold":        MLFeatureValue(double: 0.45),
            "confidenceThreshold": MLFeatureValue(double: Double(confFloor)),
        ])
        let output = try model.prediction(from: input)

        guard let confArr  = output.featureValue(for: "confidence")?.multiArrayValue,
              let coordArr = output.featureValue(for: "coordinates")?.multiArrayValue else { return [] }

        let n      = confArr.shape[0].intValue
        let nTotal = confArr.shape[1].intValue
        let nCheck = min(classLabels.count, nTotal)

        let cs0 = confArr.strides[0].intValue
        let cs1 = confArr.strides[1].intValue
        let xs0 = coordArr.strides[0].intValue

        let sz = Double(yoloImgSize)
        let newWd = Double(lb.newW), newHd = Double(lb.newH)
        let pxD = Double(lb.padX), pyD = Double(lb.padY)

        var dets: [Detection] = []
        for i in 0..<n {
            var bestConf: Float = 0
            var bestClass = 0
            for c in 0..<nCheck {
                let v = confArr[i * cs0 + c * cs1].floatValue
                if v > bestConf { bestConf = v; bestClass = c }
            }
            guard bestConf >= confFloor else { continue }

            let cx640 = coordArr[i * xs0 + 0].doubleValue
            let cy640 = coordArr[i * xs0 + 1].doubleValue
            let w640  = coordArr[i * xs0 + 2].doubleValue
            let h640  = coordArr[i * xs0 + 3].doubleValue

            dets.append(Detection(
                label: classLabels[bestClass], confidence: bestConf,
                cx: (cx640 * sz - pxD) / newWd, cy: (cy640 * sz - pyD) / newHd,
                w: w640 * sz / newWd, h: h640 * sz / newHd
            ))
        }
        return dets
    }

    static func iou(_ a: GTBox, _ b: Detection) -> Double {
        let ax1 = a.cx - a.w/2, ax2 = a.cx + a.w/2, ay1 = a.cy - a.h/2, ay2 = a.cy + a.h/2
        let bx1 = b.cx - b.w/2, bx2 = b.cx + b.w/2, by1 = b.cy - b.h/2, by2 = b.cy + b.h/2
        let ix = max(0, min(ax2, bx2) - max(ax1, bx1))
        let iy = max(0, min(ay2, by2) - max(ay1, by1))
        let inter = ix * iy
        let union = a.w * a.h + b.w * b.h - inter
        return union > 0 ? inter / union : 0
    }

    static func nms(_ preds: [Detection], iouThreshold: Double) -> [Detection] {
        let sorted = preds.sorted { $0.confidence > $1.confidence }
        var kept: [Detection] = []
        var suppressed = Set<Int>()
        for (i, a) in sorted.enumerated() {
            if suppressed.contains(i) { continue }
            kept.append(a)
            for (j, b) in sorted.enumerated() where j > i {
                if suppressed.contains(j) { continue }
                guard a.label == b.label else { continue }
                let ax1 = a.cx - a.w/2, ax2 = a.cx + a.w/2, ay1 = a.cy - a.h/2, ay2 = a.cy + a.h/2
                let bx1 = b.cx - b.w/2, bx2 = b.cx + b.w/2, by1 = b.cy - b.h/2, by2 = b.cy + b.h/2
                let ix = max(0, min(ax2,bx2) - max(ax1,bx1))
                let iy = max(0, min(ay2,by2) - max(ay1,by1))
                let inter = ix * iy
                let union = a.w*a.h + b.w*b.h - inter
                let iouVal = union > 0 ? inter/union : 0
                if iouVal > iouThreshold { suppressed.insert(j) }
            }
        }
        return kept
    }

    static func computeAP(detections: [(conf: Float, isTP: Bool)], nGT: Int) -> Double {
        guard nGT > 0 else { return 0 }
        var tp = 0, fp = 0
        var precisions: [Double] = [], recalls: [Double] = []
        for d in detections.sorted(by: { $0.conf > $1.conf }) {
            if d.isTP { tp += 1 } else { fp += 1 }
            precisions.append(Double(tp) / Double(tp + fp))
            recalls.append(Double(tp) / Double(nGT))
        }
        var ap = 0.0
        for t in stride(from: 0.0, through: 1.0, by: 0.1) {
            let pMax = zip(recalls, precisions).filter { $0.0 >= t }.map { $0.1 }.max() ?? 0
            ap += pMax
        }
        return ap / 11.0
    }
}

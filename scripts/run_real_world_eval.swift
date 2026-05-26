// run_real_world_eval.swift
// NativeUIAuditKit/scripts
//
// TASK-6-5 AC: Run inference on 10 real App Store screenshots (personal device).
//
// Runs the full 3-pass inference pipeline on each image in
// reports/real_world_screenshots/ and writes a markdown report to
// reports/real_world_eval.md documenting detection results and failure modes.
//
// ── HOW TO PROVIDE SCREENSHOTS ──────────────────────────────────────────────
//
// 1. On your personal iPhone (NOT the simulator — must be real App Store apps):
//    Screenshot 10 apps from varied categories:
//      - 2 productivity apps  (e.g. Notes, Calendar)
//      - 2 social apps        (e.g. Messages, Mail)
//      - 2 media apps         (e.g. Music, Photos)
//      - 2 utility apps       (e.g. Settings, Clock)
//      - 2 finance/health     (e.g. Health, Wallet)
//
// 2. AirDrop or copy screenshots to:
//      reports/real_world_screenshots/
//    Name them descriptively: app_name_screen_name.png
//    Example: notes_main_list.png, messages_conversation.png
//
// 3. Run this script:
//      swift scripts/run_real_world_eval.swift
//
// ── LEGAL NOTE ────────────────────────────────────────────────────────────────
//
// Screenshots taken on a personal device of apps from the App Store:
//   - Are NOT redistributed (stored only in reports/, which is gitignored)
//   - Are NOT used in training
//   - Are used solely for evaluation of this research project
//   - No app UI is reverse-engineered — only bounding box positions are recorded
//
// IMPORTANT: Do NOT commit these screenshots to the repository.
//            reports/ should be in .gitignore. Verify before any git operation.
//
// ── WHAT TO LOOK FOR ─────────────────────────────────────────────────────────
//
// Expected to work well (from synthetic eval):
//   alert, toggle — AP > 0.60 on synthetic; should transfer to real
//
// Expected to partially work:
//   primaryButton — some missed, some found; real apps have more visual variety
//   navigationBar, textField — depends on Run 003 fixing the anchor issue
//
// Known failure modes to document:
//   - Custom navigation bars (non-standard tint, transparent)
//   - Heavily customized UIButton subclasses that don't look "button-like"
//   - Web views rendering HTML that mimics native elements (hard negative problem)
//   - Dark mode with custom colors that differ from training distribution

import Foundation
import CoreML
import Vision
import CoreGraphics
import ImageIO

// MARK: - Config

let projectRoot = URL(filePath: #filePath)
    .deletingLastPathComponent()
    .deletingLastPathComponent()

let modelURL = projectRoot
    .appending(path: "NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIDetector_v1.mlpackage.mlmodel")

let screenshotsDir = projectRoot.appending(path: "reports/real_world_screenshots", directoryHint: .isDirectory)
let reportURL      = projectRoot.appending(path: "reports/real_world_eval.md")

let confidenceThreshold: Float = 0.30   // higher than eval — we want clean real-world results
let nmsIoUThreshold = 0.45

// MARK: - Image helpers (same as eval_map.swift)

func cropCGImage(source: CGImage, x: Int, y: Int, width: Int, height: Int) -> CGImage? {
    guard let ctx = CGContext(data: nil, width: width, height: height,
                              bitsPerComponent: 8, bytesPerRow: 0,
                              space: CGColorSpaceCreateDeviceRGB(),
                              bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { return nil }
    ctx.draw(source, in: CGRect(x: -x, y: -(source.height - y - height), width: source.width, height: source.height))
    return ctx.makeImage()
}

func upscale(_ image: CGImage, factor: Int) -> CGImage? {
    guard let ctx = CGContext(data: nil, width: image.width * factor, height: image.height * factor,
                              bitsPerComponent: 8, bytesPerRow: 0,
                              space: CGColorSpaceCreateDeviceRGB(),
                              bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { return nil }
    ctx.interpolationQuality = .none
    ctx.draw(image, in: CGRect(x: 0, y: 0, width: image.width * factor, height: image.height * factor))
    return ctx.makeImage()
}

struct Det { let pass: String; let label: String; let conf: Float; let cx, cy, w, h: Double }

func runReq(on image: CGImage, model: VNCoreMLModel) throws -> [VNRecognizedObjectObservation] {
    let req = VNCoreMLRequest(model: model)
    req.imageCropAndScaleOption = .scaleFill
    try VNImageRequestHandler(cgImage: image, options: [:]).perform([req])
    return req.results as? [VNRecognizedObjectObservation] ?? []
}

func iouD(_ a: Det, _ b: Det) -> Double {
    let ax1 = a.cx-a.w/2, ax2 = a.cx+a.w/2, ay1 = a.cy-a.h/2, ay2 = a.cy+a.h/2
    let bx1 = b.cx-b.w/2, bx2 = b.cx+b.w/2, by1 = b.cy-b.h/2, by2 = b.cy+b.h/2
    let ix = max(0, min(ax2,bx2) - max(ax1,bx1))
    let iy = max(0, min(ay2,by2) - max(ay1,by1))
    let inter = ix * iy
    let union = a.w*a.h + b.w*b.h - inter
    return union > 0 ? inter/union : 0
}

func threePassInference(image: CGImage, model: VNCoreMLModel) throws -> [Det] {
    var dets: [Det] = []

    // Pass 1 — full image
    for obs in try runReq(on: image, model: model) {
        guard obs.confidence >= confidenceThreshold else { continue }
        let b = obs.boundingBox
        dets.append(Det(pass: "full", label: obs.labels.first?.identifier ?? "?",
                        conf: obs.confidence, cx: Double(b.midX), cy: 1.0 - Double(b.midY),
                        w: Double(b.width), h: Double(b.height)))
    }

    // Pass 2 — SAHI tiles
    if let up = upscale(image, factor: 2) {
        let W = up.width, H = up.height, tileSize = 640, stride = 480
        var ty = 0
        while ty < H {
            let tH = min(tileSize, H - ty); var tx = 0
            while tx < W {
                let tW = min(tileSize, W - tx)
                if let tile = cropCGImage(source: up, x: tx, y: ty, width: tW, height: tH) {
                    for obs in try runReq(on: tile, model: model) {
                        guard obs.confidence >= confidenceThreshold else { continue }
                        let b = obs.boundingBox
                        let xF = Double(tx)/Double(W), yF = Double(ty)/Double(H)
                        let wF = Double(tW)/Double(W), hF = Double(tH)/Double(H)
                        dets.append(Det(pass: "sahi", label: obs.labels.first?.identifier ?? "?",
                                        conf: obs.confidence,
                                        cx: xF + Double(b.midX)*wF, cy: yF + (1.0 - Double(b.midY))*hF,
                                        w: Double(b.width)*wF, h: Double(b.height)*hF))
                    }
                }
                tx += stride
            }
            ty += stride
        }
    }

    // Pass 3 — horizontal strips
    let imgH = image.height, imgW = image.width
    let stripH = max(1, Int(Double(imgH) * 0.22))
    let stride  = max(1, stripH / 2)
    var y = 0
    while y + stripH <= imgH {
        if let strip = cropCGImage(source: image, x: 0, y: y, width: imgW, height: stripH) {
            for obs in try runReq(on: strip, model: model) {
                guard obs.confidence >= confidenceThreshold else { continue }
                let b = obs.boundingBox
                let stripTopVision    = 1.0 - Double(y + stripH) / Double(imgH)
                let stripHeightVision = Double(stripH) / Double(imgH)
                let fullVisionMidY    = stripTopVision + Double(b.midY) * stripHeightVision
                dets.append(Det(pass: "strip", label: obs.labels.first?.identifier ?? "?",
                                conf: obs.confidence,
                                cx: Double(b.midX), cy: 1.0 - fullVisionMidY,
                                w: Double(b.width), h: Double(b.height) * stripHeightVision))
            }
        }
        y += stride
    }

    // NMS
    let sorted = dets.sorted { $0.conf > $1.conf }
    var kept: [Det] = []; var suppressed = Set<Int>()
    for (i, a) in sorted.enumerated() {
        if suppressed.contains(i) { continue }; kept.append(a)
        for (j, b) in sorted.enumerated() where j > i {
            if suppressed.contains(j) || a.label != b.label { continue }
            if iouD(a, b) > nmsIoUThreshold { suppressed.insert(j) }
        }
    }
    return kept
}

// MARK: - Main

// Check screenshots directory exists and has images
guard FileManager.default.fileExists(atPath: screenshotsDir.path) else {
    fputs("""
    ⚠︎  reports/real_world_screenshots/ does not exist.
    Create it and add 10 real App Store screenshots before running this script.
    See the header comment for instructions.
    """, stderr)
    exit(1)
}

let screenshotURLs = (try? FileManager.default.contentsOfDirectory(at: screenshotsDir, includingPropertiesForKeys: nil)
    .filter { ["png", "jpg", "jpeg"].contains($0.pathExtension.lowercased()) }
    .sorted { $0.lastPathComponent < $1.lastPathComponent }) ?? []

guard !screenshotURLs.isEmpty else {
    fputs("⚠︎  No images found in reports/real_world_screenshots/. Add .png or .jpg screenshots.\n", stderr)
    exit(1)
}

print("Found \(screenshotURLs.count) real-world screenshot(s)")
if screenshotURLs.count < 10 {
    print("⚠︎  TASK-6-5 requires ≥10 real-world screenshots. Found \(screenshotURLs.count).")
}
print()

// Load model
print("Loading model...")
let compiledURL = try MLModel.compileModel(at: modelURL)
let model       = try MLModel(contentsOf: compiledURL)
let vnModel     = try VNCoreMLModel(for: model)
print("Model loaded ✓\n")

// Run inference on each screenshot
var reportLines: [String] = [
    "# Real-World Evaluation — NativeUIDetector v1",
    "",
    "**Model:** nativeui-ios-v1.0  ",
    "**Date:** \(ISO8601DateFormatter().string(from: Date()))  ",
    "**Confidence threshold:** \(confidenceThreshold)  ",
    "**Images:** \(screenshotURLs.count) real App Store screenshots (personal device, never in training)",
    "",
    "---",
    ""
]

var totalByClass: [String: Int] = [:]

for imgURL in screenshotURLs {
    guard let src   = CGImageSourceCreateWithURL(imgURL as CFURL, nil),
          let cgImg = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
        print("⚠︎ Could not load \(imgURL.lastPathComponent)")
        continue
    }

    let dets = (try? threePassInference(image: cgImg, model: vnModel)) ?? []
    let name = imgURL.lastPathComponent

    print("\(name) (\(cgImg.width)×\(cgImg.height))")
    reportLines.append("## \(name)  (\(cgImg.width)×\(cgImg.height))")
    reportLines.append("")

    if dets.isEmpty {
        print("  — no detections above conf \(confidenceThreshold)")
        reportLines.append("*No detections above confidence \(confidenceThreshold).*")
    } else {
        for d in dets {
            let line = "- `\(d.label)` conf=\(String(format:"%.3f",d.conf)) cx=\(String(format:"%.2f",d.cx)) cy=\(String(format:"%.2f",d.cy)) w=\(String(format:"%.2f",d.w)) h=\(String(format:"%.2f",d.h)) [\(d.pass)]"
            print("  \(line.dropFirst())")
            reportLines.append(line)
            totalByClass[d.label, default: 0] += 1
        }
    }
    reportLines.append("")
    print()
}

// Summary
reportLines += [
    "---",
    "",
    "## Summary",
    "",
    "| Class | Total detections |",
    "|---|---|"
]
for (cls, count) in totalByClass.sorted(by: { $0.key < $1.key }) {
    reportLines.append("| \(cls) | \(count) |")
}
reportLines += [
    "",
    "## Failure Mode Notes",
    "",
    "*(Fill in manually after visual inspection of the detections above)*",
    "",
    "- [ ] Custom navigation bars (non-standard tint / transparent) — detected correctly?",
    "- [ ] Heavy UIButton customisation — missed?",
    "- [ ] Dark mode images — detection quality comparable to light mode?",
    "- [ ] Web views / non-native chrome — false positives?",
    "- [ ] navigationBar / textField — did strip pass detect them? *(key Run 003 test)*",
    ""
]

let report = reportLines.joined(separator: "\n")
try report.write(to: reportURL, atomically: true, encoding: .utf8)
print("Report written to: \(reportURL.path)")

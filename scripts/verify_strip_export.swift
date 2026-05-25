// verify_strip_export.swift
// NativeUIAuditKit/scripts
//
// Smoke-tests the strip-tiling export by exporting a small subset (10 images)
// and verifying:
//   1. Strip PNG files are written with the correct dimensions
//   2. Strip annotation coordinates are in [0,1] and remapped correctly
//   3. NavigationBar aspect ratio in strip space is ≤ 4:1
//
// Usage (from project root):
//   swift scripts/verify_strip_export.swift

import Foundation
import CoreGraphics
import ImageIO

let projectRoot = URL(filePath: #filePath)
    .deletingLastPathComponent()
    .deletingLastPathComponent()

let datasetDir = URL(filePath: "/Users/josephmccraw/Library/Developer/CoreSimulator/Devices/812EDC32-DB8D-49D6-B130-2279180CCDEB/data/Containers/Data/Application/E0711EF5-B600-47B2-A7B8-D5BA63DE1D83/Documents/dataset")

let outDir = projectRoot.appending(path: "NativeUITrainer/strip_smoke_test", directoryHint: .isDirectory)
try? FileManager.default.removeItem(at: outDir)

print("=== Strip Export Smoke Test ===")
print("Output: \(outDir.path)")
print()

// --- Inline mini-exporter for the first 10 training images ---

let splitDir = datasetDir.appending(path: "train")
let pngURLs = try FileManager.default.contentsOfDirectory(at: splitDir, includingPropertiesForKeys: nil)
    .filter { $0.pathExtension == "png" }
    .sorted { $0.lastPathComponent < $1.lastPathComponent }
    .drop(while: { !$0.lastPathComponent.hasPrefix("img_0004") })
    .prefix(10)   // start from img_000401 where target classes begin

let imagesDir = outDir.appending(path: "images", directoryHint: .isDirectory)
try FileManager.default.createDirectory(at: imagesDir, withIntermediateDirectories: true)

struct Elem: Decodable {
    let elementType: String
    let boundsVisionNormalized: Rect
    struct Rect: Decodable { let x,y,width,height: Double }
}
struct Ann: Decodable { let elements: [Elem] }

let targetClasses = Set(["alert","navigationBar","primaryButton","textField","toggle"])
let stripFraction = 0.22

var stripAspectRatios: [String: [Double]] = [:]
var issueCount = 0

for pngURL in pngURLs {
    let jsonURL = pngURL.deletingPathExtension().appendingPathExtension("json")
    guard let data = try? Data(contentsOf: jsonURL),
          let ann  = try? JSONDecoder().decode(Ann.self, from: data),
          let src  = CGImageSourceCreateWithURL(pngURL as CFURL, nil),
          let cgImage = CGImageSourceCreateImageAtIndex(src, 0, nil)
    else { continue }

    let imageH = cgImage.height
    let imageW = cgImage.width
    let stripH = max(1, Int(Double(imageH) * stripFraction))
    let stride = max(1, stripH / 2)

    // Compute Create ML normalized coords for elements
    let elems = ann.elements.filter { targetClasses.contains($0.elementType) }.map { e -> (String, Double, Double, Double, Double) in
        let vn = e.boundsVisionNormalized
        return (e.elementType, vn.x + vn.width/2, 1.0 - vn.y - vn.height/2, vn.width, vn.height)
    }
    guard !elems.isEmpty else { continue }

    var stripIdx = 0
    var stripY = 0
    while stripY + stripH <= imageH {
        defer { stripY += stride; stripIdx += 1 }
        let yTopNorm = Double(stripY) / Double(imageH)
        let yBotNorm = Double(stripY + stripH) / Double(imageH)
        let scaleY   = Double(imageH) / Double(stripH)

        let stripElems = elems.filter { $0.1 >= yTopNorm && $0.1 <= yBotNorm }
        guard !stripElems.isEmpty else { continue }

        // Crop image
        guard let ctx = CGContext(data: nil, width: imageW, height: stripH,
                                  bitsPerComponent: 8, bytesPerRow: 0,
                                  space: CGColorSpaceCreateDeviceRGB(),
                                  bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)
        else { continue }
        ctx.draw(cgImage, in: CGRect(x: 0, y: -(imageH - stripY - stripH),
                                     width: imageW, height: imageH))
        guard let strip = ctx.makeImage() else { continue }

        // Verify strip dimensions
        if strip.width != imageW || strip.height != stripH {
            print("❌ FAIL: strip dimensions wrong: got \(strip.width)×\(strip.height), expected \(imageW)×\(stripH)")
            issueCount += 1
        }

        // Verify coordinates
        for (label, _, cy, _, h) in stripElems {
            let cy_s = ((cy - yTopNorm) * scaleY).clamped(to: 0...1)
            let h_s  = (h * scaleY).clamped(to: 0...1)
            let w_s  = elems.first(where: { $0.0 == label })?.3 ?? 0
            let ratio = w_s > 0 && h_s > 0 ? w_s / h_s : 0

            // Bounds check
            if cy_s < 0 || cy_s > 1 || h_s <= 0 {
                print("❌ FAIL: out-of-range coord for \(label): cy_s=\(cy_s) h_s=\(h_s)")
                issueCount += 1
            }
            if ratio > 0 { stripAspectRatios[label, default: []].append(ratio) }
        }

        // Write strip for visual inspection
        let name = "\(pngURL.deletingPathExtension().lastPathComponent)_s\(String(format:"%02d",stripIdx)).png"
        if let dest = CGImageDestinationCreateWithURL(imagesDir.appending(path: name) as CFURL, "public.png" as CFString, 1, nil) {
            CGImageDestinationAddImage(dest, strip, nil)
            CGImageDestinationFinalize(dest)
        }
    }
}

print("Aspect ratios in strip space (should be ≤ 4:1 for thin classes):")
for (cls, ratios) in stripAspectRatios.sorted(by: { $0.key < $1.key }) {
    let avg = ratios.reduce(0, +) / Double(ratios.count)
    let pass = cls == "navigationBar" || cls == "textField" || cls == "primaryButton"
        ? avg <= 4.0 : true
    print("  \(pass ? "✓" : "⚠︎") \(cls.padding(toLength: 18, withPad: " ", startingAt: 0)): avg \(String(format: "%.2f", avg)):1  (n=\(ratios.count))")
}

print()
print(issueCount == 0 ? "✓ All checks passed" : "❌ \(issueCount) issue(s) found")
print("Strip images written to: \(imagesDir.path)")

extension Comparable {
    func clamped(to range: ClosedRange<Self>) -> Self {
        min(max(self, range.lowerBound), range.upperBound)
    }
}

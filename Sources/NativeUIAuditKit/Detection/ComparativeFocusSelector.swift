// ComparativeFocusSelector.swift
// NativeUIAuditKitRuntime
//
// Experimental T4.2 Arm B comparative within-screen focus selector with explicit no_focus gate.
// Opt-in only via explicit configuration (`comparativeFocusDirectory`); default FocusRing path is unchanged.

import CoreGraphics
import CoreML
import Darwin
import Foundation
import NativeUIModelContracts

/// Scores focusable candidates on one screen comparatively using rim/halo/inner descriptors
/// and applies an explicit screen-level `no_focus` gate (`comparative-armb-v2`).
package struct ComparativeFocusSelector: @unchecked Sendable {
    package static let rawFeatureCount = 20
    package static let comparativeFeatureCount = 80
    package static let gateFeatureCount = 9

    package let scorer: MLModel
    package let gate: MLModel?
    package let gateThreshold: Float
    package let modelDigest: String?
    /// Remove focusable candidates nested inside a larger focusable candidate before scoring.
    package let dropsNestedCandidates: Bool

    /// Nested filter: candidate i is removed when another candidate covers at least this fraction of it...
    package static let nestedContainment = 0.9
    /// ...and has at least this many times its area. Matches `scripts/nested_filter666.py`.
    package static let nestedAreaRatio = 2.0

    package var policy: String { dropsNestedCandidates ? "comparative-armb-v2-nested-v1" : "comparative-armb-v2" }

    package init(directory: URL, gateThreshold: Float = 0.28, dropsNestedCandidates: Bool = false) throws {
        let fm = FileManager.default
        let scorerURL = try Self.resolveModelURL(named: "ComparativeFocusScorer", in: directory, fileManager: fm)
        let scorerCompiled = try Self.ensureCompiled(scorerURL)
        self.scorer = try MLModel(contentsOf: scorerCompiled)

        let gateCandidate = try? Self.resolveModelURL(named: "ComparativeFocusGate", in: directory, fileManager: fm)
        if let gateCandidate, let gateCompiled = try? Self.ensureCompiled(gateCandidate) {
            self.gate = try MLModel(contentsOf: gateCompiled)
        } else {
            self.gate = nil
        }
        self.gateThreshold = gateThreshold
        self.modelDigest = nil
        self.dropsNestedCandidates = dropsNestedCandidates
    }

    /// Indices of boxes (top-left pixel rects) that lie at least `nestedContainment` inside another box
    /// with at least `nestedAreaRatio` times their area. tvOS moves focus to the outer element, and a nested
    /// box (for example a false `toggle` on a row chevron) inherits the row's focus highlight.
    package static func nestedCandidateIndices(_ boxes: [CGRect]) -> Set<Int> {
        func area(_ r: CGRect) -> Double { max(Double(r.width), 0) * max(Double(r.height), 0) }
        var removed = Set<Int>()
        for (i, inner) in boxes.enumerated() {
            let a = area(inner)
            for (j, outer) in boxes.enumerated() where j != i && area(outer) >= nestedAreaRatio * a {
                let ix = max(0, min(Double(inner.maxX), Double(outer.maxX)) - max(Double(inner.minX), Double(outer.minX)))
                let iy = max(0, min(Double(inner.maxY), Double(outer.maxY)) - max(Double(inner.minY), Double(outer.minY)))
                if ix * iy / max(a, 1e-6) >= nestedContainment {
                    removed.insert(i)
                    break
                }
            }
        }
        return removed
    }

    private static func resolveModelURL(named stem: String, in directory: URL, fileManager: FileManager) throws -> URL {
        for ext in ["mlmodelc", "mlpackage"] {
            let candidate = directory.appendingPathComponent("\(stem).\(ext)")
            if fileManager.fileExists(atPath: candidate.path) {
                return candidate
            }
        }
        throw NativeUIDetectionError.incompatibleModelContract(reason: "Missing \(stem).mlmodelc/.mlpackage in \(directory.path)")
    }

    private static func ensureCompiled(_ url: URL) throws -> URL {
        if url.pathExtension == "mlmodelc" {
            return url
        }
        return try MLModel.compileModel(at: url)
    }

    /// Extract RGB bytes `[y * width * 4 + x * 4 + c]` matching PIL top-left sRGB byte order.
    private static func extractRGBABytes(_ image: CGImage) -> [UInt8]? {
        let w = image.width
        let h = image.height
        guard w > 0, h > 0 else { return nil }
        let colorSpace = CGColorSpace(name: CGColorSpace.sRGB) ?? CGColorSpaceCreateDeviceRGB()
        var bytes = [UInt8](repeating: 0, count: w * h * 4)
        let ok = bytes.withUnsafeMutableBytes { ptr -> Bool in
            guard let base = ptr.baseAddress,
                  let ctx = CGContext(
                      data: base,
                      width: w,
                      height: h,
                      bitsPerComponent: 8,
                      bytesPerRow: w * 4,
                      space: colorSpace,
                      bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue
                  ) else { return false }
            ctx.draw(image, in: CGRect(x: 0, y: 0, width: w, height: h))
            return true
        }
        return ok ? bytes : nil
    }

    private static func clipRect(
        _ x1: Double, _ y1: Double, _ x2: Double, _ y2: Double,
        width: Int, height: Int
    ) -> (Int, Int, Int, Int) {
        let ix1 = max(0, min(width, Int(Darwin.nearbyint(x1))))
        let iy1 = max(0, min(height, Int(Darwin.nearbyint(y1))))
        let ix2 = max(ix1 + 1, min(width, Int(Darwin.nearbyint(x2))))
        let iy2 = max(iy1 + 1, min(height, Int(Darwin.nearbyint(y2))))
        return (ix1, iy1, ix2, iy2)
    }

    private static func percentileLinear(_ values: [Float], q: Double) -> Float {
        guard !values.isEmpty else { return 0 }
        let sorted = values.sorted()
        if sorted.count == 1 { return sorted[0] }
        let pos = Double(sorted.count - 1) * (q / 100.0)
        let lo = Int(pos)
        let hi = min(sorted.count - 1, lo + 1)
        let frac = Float(pos - Double(lo))
        return sorted[lo] + frac * (sorted[hi] - sorted[lo])
    }

    private static func meanAndStd(_ values: [Float]) -> (Float, Float) {
        guard !values.isEmpty else { return (0, 0) }
        var sum = 0.0
        for v in values { sum += Double(v) }
        let m = sum / Double(values.count)
        var varSum = 0.0
        for v in values {
            let d = Double(v) - m
            varSum += d * d
        }
        return (Float(m), Float(sqrt(varSum / Double(values.count))))
    }

    /// Compute 20 concentric rim/halo/inner photometric + gradient + geometry descriptors per box.
    package static func extractRawFeatures(from image: CGImage, boxes: [CGRect]) -> [[Float]] {
        guard !boxes.isEmpty, let rgba = extractRGBABytes(image) else { return [] }
        let w = image.width
        let h = image.height
        let totalPx = w * h

        var luma = [Float](repeating: 0, count: totalPx)
        var sat = [Float](repeating: 0, count: totalPx)
        for i in 0..<totalPx {
            let base = i * 4
            let r = Float(rgba[base]) / 255.0
            let g = Float(rgba[base + 1]) / 255.0
            let b = Float(rgba[base + 2]) / 255.0
            luma[i] = Float(0.299) * r + Float(0.587) * g + Float(0.114) * b
            let cmax = max(r, max(g, b))
            let cmin = min(r, min(g, b))
            sat[i] = cmax > 1e-4 ? (cmax - cmin) / max(cmax, 1e-4) : 0.0
        }

        var grad = [Float](repeating: 0, count: totalPx)
        for y in 0..<h {
            let row = y * w
            for x in 0..<w {
                let idx = row + x
                let gx = x > 0 ? abs(luma[idx] - luma[idx - 1]) : 0
                let gy = y > 0 ? abs(luma[idx] - luma[idx - w]) : 0
                grad[idx] = gx + gy
            }
        }

        var out: [[Float]] = []
        out.reserveCapacity(boxes.count)
        for box in boxes {
            let bx = Double(box.origin.x), by = Double(box.origin.y)
            let bw = Double(box.size.width), bh = Double(box.size.height)
            let (bx1, by1, bx2, by2) = clipRect(bx, by, bx + bw, by + bh, width: w, height: h)

            let ex = max(3.0, bw * 0.16), ey = max(3.0, bh * 0.16)
            let (hx1, hy1, hx2, hy2) = clipRect(bx - ex, by - ey, bx + bw + ex, by + bh + ey, width: w, height: h)

            let rimPad = max(2.0, min(6.0, min(bw, bh) * 0.06))
            let (ox1, oy1, ox2, oy2) = clipRect(bx - rimPad, by - rimPad, bx + bw + rimPad, by + bh + rimPad, width: w, height: h)
            let ixIn = max(2.0, bw * 0.12), iyIn = max(2.0, bh * 0.12)
            let (ix1, iy1, ix2, iy2) = clipRect(bx + ixIn, by + iyIn, bx + bw - ixIn, by + bh - iyIn, width: w, height: h)

            var rimL: [Float] = [], haloL: [Float] = [], innerL: [Float] = []
            var rimG: [Float] = [], haloG: [Float] = []
            var rimS: [Float] = [], haloS: [Float] = []
            var roiL: [Float] = [], roiG: [Float] = [], roiS: [Float] = []

            let roiCount = max(1, (hx2 - hx1) * (hy2 - hy1))
            roiL.reserveCapacity(roiCount)
            roiG.reserveCapacity(roiCount)
            roiS.reserveCapacity(roiCount)

            for py in hy1..<hy2 {
                let rowOff = py * w
                let inBoxY = py >= by1 && py < by2
                let inInnerY = py >= iy1 && py < iy2
                let inOuterY = py >= oy1 && py < oy2
                for px in hx1..<hx2 {
                    let idx = rowOff + px
                    let lv = luma[idx], gv = grad[idx], sv = sat[idx]
                    roiL.append(lv); roiG.append(gv); roiS.append(sv)
                    let inBox = inBoxY && px >= bx1 && px < bx2
                    let inInner = inInnerY && px >= ix1 && px < ix2
                    let inOuter = inOuterY && px >= ox1 && px < ox2
                    if inOuter && !inInner {
                        rimL.append(lv); rimG.append(gv); rimS.append(sv)
                    }
                    if inInner {
                        innerL.append(lv)
                    }
                    if !inBox {
                        haloL.append(lv); haloG.append(gv); haloS.append(sv)
                    }
                }
            }

            let effRimL = rimL.isEmpty ? roiL : rimL
            let effHaloL = haloL.isEmpty ? roiL : haloL
            let effInnerL = innerL.isEmpty ? roiL : innerL
            let effRimG = rimG.isEmpty ? roiG : rimG
            let effHaloG = haloG.isEmpty ? roiG : haloG
            let effRimS = rimS.isEmpty ? roiS : rimS
            let effHaloS = haloS.isEmpty ? roiS : haloS

            let (rMean, rStd) = meanAndStd(effRimL)
            let rP90 = percentileLinear(effRimL, q: 90)
            let rP95 = percentileLinear(effRimL, q: 95)
            let (hMean, hStd) = meanAndStd(effHaloL)
            let hP90 = percentileLinear(effHaloL, q: 90)
            let (iMean, iStd) = meanAndStd(effInnerL)
            let iP90 = percentileLinear(effInnerL, q: 90)
            let (rgMean, _) = meanAndStd(effRimG)
            let rgP90 = percentileLinear(effRimG, q: 90)
            let (hgMean, _) = meanAndStd(effHaloG)
            let (rsMean, _) = meanAndStd(effRimS)
            let (hsMean, _) = meanAndStd(effHaloS)

            let logArea = Float(log(max(1.0, bw * bh) / Double(max(1, w * h))))
            let aspect = Float(log(max(0.1, bw / max(1.0, bh))))

            out.append([
                rMean, rP90, rP95, rStd,
                hMean, hP90, hStd,
                iMean, iP90, iStd,
                rMean - hMean,
                rMean - iMean,
                rP90 - hP90,
                rgMean, rgP90, hgMean,
                rsMean, rsMean - hsMean,
                logArea, aspect,
            ])
        }
        return out
    }

    /// Build `[N, 80]` within-screen comparative matrix `[raw, raw - mean, raw - median, z]`.
    package static func buildComparativeFeatures(_ raw: [[Float]]) -> [[Float]] {
        let n = raw.count
        guard n > 0 else { return [] }
        let d = raw[0].count
        if n == 1 {
            let zeros = [Float](repeating: 0, count: d * 3)
            return [raw[0] + zeros]
        }
        var mean = [Float](repeating: 0, count: d)
        var med = [Float](repeating: 0, count: d)
        var std = [Float](repeating: 0, count: d)
        for col in 0..<d {
            var vals = [Float]()
            vals.reserveCapacity(n)
            for row in 0..<n { vals.append(raw[row][col]) }
            let (m, s) = meanAndStd(vals)
            mean[col] = m
            std[col] = s + 1e-3
            med[col] = percentileLinear(vals, q: 50)
        }
        return raw.map { row in
            var deltaMean = [Float](repeating: 0, count: d)
            var deltaMed = [Float](repeating: 0, count: d)
            var z = [Float](repeating: 0, count: d)
            for col in 0..<d {
                let dm = row[col] - mean[col]
                deltaMean[col] = dm
                deltaMed[col] = row[col] - med[col]
                z[col] = dm / std[col]
            }
            return row + deltaMean + deltaMed + z
        }
    }

    /// Score focusable observations comparatively with an explicit screen-level `no_focus` gate.
    package func resolve(
        in screenshot: CGImage,
        observations: [NativeUIElementObservation]
    ) throws -> ([NativeUIElementObservation], FocusExecutionReceipt) {
        let allFocusable = observations.enumerated().filter { FocusRingClassifier.focusableTypes.contains($0.element.elementType) }
        let nested = dropsNestedCandidates
            ? Self.nestedCandidateIndices(allFocusable.map { $0.element.boundingBoxPixels.cgRect }) : []
        let nestedIDs = Set(nested.map { allFocusable[$0].element.id })
        let focusable = allFocusable.enumerated().filter { !nested.contains($0.offset) }.map(\.element)
        guard !focusable.isEmpty else {
            let receipt = FocusExecutionReceipt(
                backend: .coreML,
                modelDigest: modelDigest,
                policy: policy,
                threshold: Double(gateThreshold),
                candidates: observations.map {
                    .init(observationID: $0.id, disposition: nestedIDs.contains($0.id) ? .nestedCandidateRemoved : .unsupportedRole,
                          probability: nil, isFocused: nestedIDs.contains($0.id) ? false : nil)
                }
            )
            return (observations, receipt)
        }

        let boxes = focusable.map { $0.element.boundingBoxPixels.cgRect }
        let raw = Self.extractRawFeatures(from: screenshot, boxes: boxes)
        guard raw.count == focusable.count else {
            throw NativeUIDetectionError.imagePreprocessingFailed
        }
        let comp = Self.buildComparativeFeatures(raw)
        let m = focusable.count

        let logits: [Float]
        let probs: [Float]
        let winnerLocalIdx: Int
        let hasFocus: Bool

        if m == 1 {
            logits = [0]
            probs = [1]
            winnerLocalIdx = 0
            hasFocus = false
        } else {
            let inputArr = try MLMultiArray(shape: [NSNumber(value: m), NSNumber(value: Self.comparativeFeatureCount)], dataType: .float32)
            let ptr = inputArr.dataPointer.bindMemory(to: Float.self, capacity: m * Self.comparativeFeatureCount)
            for row in 0..<m {
                for col in 0..<Self.comparativeFeatureCount {
                    ptr[row * Self.comparativeFeatureCount + col] = comp[row][col]
                }
            }
            let pred = try scorer.prediction(from: MLDictionaryFeatureProvider(dictionary: [
                "candidates": MLFeatureValue(multiArray: inputArr),
            ]))
            guard let outArr = pred.featureValue(for: "logits")?.multiArrayValue else {
                throw NativeUIDetectionError.unexpectedModelOutput("missing comparative logits")
            }
            let outPtr = outArr.dataPointer.bindMemory(to: Float.self, capacity: m)
            var rawLogits = [Float](repeating: 0, count: m)
            for i in 0..<m { rawLogits[i] = outPtr[i] }
            logits = rawLogits

            let maxL = logits.max() ?? 0
            var exps = logits.map { exp($0 - maxL) }
            let sumExp = exps.reduce(0, +)
            if sumExp > 0 {
                exps = exps.map { $0 / sumExp }
            }
            probs = exps

            let sortedIndices = (0..<m).sorted { logits[$0] > logits[$1] }
            winnerLocalIdx = sortedIndices[0]
            let top1 = logits[sortedIndices[0]]
            let top2 = logits[sortedIndices[1]]
            let med = Self.percentileLinear(logits, q: 50)
            let (meanL, stdL) = Self.meanAndStd(logits)
            let top1Z = (top1 - meanL) / (stdL + 1e-4)
            let d = Self.rawFeatureCount
            let gateVec: [Float] = [
                top1 - top2,
                top1 - med,
                top1Z,
                probs[winnerLocalIdx] * Float(m),
                Float(log(Double(max(2, m)))),
                comp[winnerLocalIdx][3 * d + 10],
                comp[winnerLocalIdx][3 * d + 12],
                comp[winnerLocalIdx][10],
                comp[winnerLocalIdx][12],
            ]
            if let gate {
                let gateArr = try MLMultiArray(shape: [1, NSNumber(value: Self.gateFeatureCount)], dataType: .float32)
                let gPtr = gateArr.dataPointer.bindMemory(to: Float.self, capacity: Self.gateFeatureCount)
                for j in 0..<Self.gateFeatureCount { gPtr[j] = gateVec[j] }
                let gPred = try gate.prediction(from: MLDictionaryFeatureProvider(dictionary: [
                    "screenSummary": MLFeatureValue(multiArray: gateArr),
                ]))
                guard let gpArr = gPred.featureValue(for: "hasFocusProb")?.multiArrayValue else {
                    throw NativeUIDetectionError.unexpectedModelOutput("missing hasFocusProb")
                }
                let gateProb = gpArr.dataPointer.bindMemory(to: Float.self, capacity: 1)[0]
                hasFocus = gateProb >= gateThreshold
            } else {
                hasFocus = true
            }
        }

        let byObsID: [UUID: (prob: Float, focused: Bool)] = Dictionary(uniqueKeysWithValues: focusable.enumerated().map { idx, item in
            (item.element.id, (probs[idx], hasFocus && idx == winnerLocalIdx))
        })

        let resolved = observations.map { obs in
            var st = obs.state
            if let score = byObsID[obs.id] {
                st.focusScore = Double(score.prob)
                st.focusConfidence = Double(score.prob)
                st.isFocused = score.focused
            } else if nestedIDs.contains(obs.id) {
                st.focusScore = nil
                st.focusConfidence = nil
                st.isFocused = false
            } else {
                return obs
            }
            st.isAmbiguousFocus = false
            return NativeUIElementObservation(
                id: obs.id,
                elementType: obs.elementType,
                boundingBox: obs.boundingBox,
                boundingBoxPixels: obs.boundingBoxPixels,
                confidence: obs.confidence,
                visibleText: obs.visibleText,
                inferredTraits: obs.inferredTraits,
                state: st,
                issues: obs.issues,
                confidenceSource: obs.confidenceSource
            )
        }
        let receipt = FocusExecutionReceipt(
            backend: .coreML,
            modelDigest: modelDigest,
            policy: policy,
            threshold: Double(gateThreshold),
            candidates: resolved.map { obs in
                if let score = byObsID[obs.id] {
                    return .init(observationID: obs.id, disposition: .scored, probability: Double(score.prob), isFocused: score.focused)
                }
                if nestedIDs.contains(obs.id) {
                    return .init(observationID: obs.id, disposition: .nestedCandidateRemoved, probability: nil, isFocused: false)
                }
                return .init(observationID: obs.id, disposition: .unsupportedRole, probability: nil, isFocused: nil)
            }
        )
        return (resolved, receipt)
    }
}

// ChangeRegionLocalizer.swift
// NativeUIAuditKit
//
// Second-cheapest gate in the detection pipeline (Track 4, TASK-PERCEP-02): once
// `FrameSimilarity` says two frames differ, this reports *where* — so a caller can scope the
// next OCR or CoreML pass to a region of interest instead of the whole frame.
//
// POLICY, not just an implementation detail: this is a capture/inference-time optimization
// ONLY. It returns geometry (`CGRect` regions + a coarse `ChangeScale`), never an image. There
// is no method on this type that produces a cropped `CGImage`, by design — that would invite
// exactly the mistake TASK-6a-10 and the project's US-9 note both call out: substituting a ROI
// crop for a full annotated training frame. Any consumer that wants a crop must build it from
// the original full frame itself, deliberately, outside this type.

import Accelerate
import CoreGraphics
import Foundation

/// Coarse classification of how much of a frame changed.
public enum ChangeScale: Sendable, Equatable {
    /// No change above the noise floor.
    case none
    /// A small fraction of the frame changed (e.g. focus moved, a toggle flipped).
    case local
    /// A moderate portion changed (e.g. a panel or list section updated).
    case regional
    /// Most or all of the frame changed (e.g. a navigation transition, a different screen).
    case fullFrame
}

/// Result of comparing two registered (same-dimension) frames.
public struct ChangeLocalizationResult: Sendable, Equatable {
    /// Coarse change classification.
    public let scale: ChangeScale
    /// Bounding boxes of connected changed regions, in the original frames' pixel coordinate
    /// space (top-left origin). Empty when `scale == .none`.
    public let regions: [CGRect]

    public init(scale: ChangeScale, regions: [CGRect]) {
        self.scale = scale
        self.regions = regions
    }
}

/// Errors surfaced while localizing change between two frames.
public enum ChangeRegionLocalizerError: Error, Sendable, Equatable {
    /// The two frames are not the same pixel dimensions — "registered" is a precondition this
    /// type does not itself enforce via image warping/alignment.
    case dimensionMismatch(previous: CGSize, current: CGSize)
    /// Rendering a frame to a grayscale analysis buffer failed.
    case grayscaleConversionFailed
}

/// Compares two registered frames and reports where they differ.
///
/// Uses a downscaled 8-bit luma buffer and an Accelerate/vDSP-vectorized absolute difference so
/// the comparison stays cheap regardless of the source frames' native resolution. Downscaling also
/// absorbs minor capture noise (HDMI/AirPlay compression artifacts, single-pixel rendering
/// jitter) that would otherwise register as spurious tiny regions at full resolution.
public struct ChangeRegionLocalizer: Sendable {
    /// Width of the internal analysis buffer. Smaller is cheaper; large enough to keep small
    /// UI elements (a focus ring, a toggle) from vanishing into a single downscaled pixel.
    public let analysisWidth: Int
    public let analysisHeight: Int
    /// Per-pixel luma delta (0-255) below which a pixel is treated as unchanged noise.
    public let noiseThreshold: UInt8
    /// Fraction of analysis-buffer area, above which a change is classified `.regional` instead
    /// of `.local`.
    public let localFraction: Double
    /// Fraction of analysis-buffer area, above which a change is classified `.fullFrame` instead
    /// of `.regional`.
    public let regionalFraction: Double

    public init(
        analysisWidth: Int = 480,
        analysisHeight: Int = 270,
        noiseThreshold: UInt8 = 24,
        localFraction: Double = 0.15,
        regionalFraction: Double = 0.60
    ) {
        self.analysisWidth = analysisWidth
        self.analysisHeight = analysisHeight
        self.noiseThreshold = noiseThreshold
        self.localFraction = localFraction
        self.regionalFraction = regionalFraction
    }

    public func localize(_ previous: CGImage, current: CGImage) throws -> ChangeLocalizationResult {
        let previousSize = CGSize(width: previous.width, height: previous.height)
        let currentSize = CGSize(width: current.width, height: current.height)
        guard previousSize == currentSize else {
            throw ChangeRegionLocalizerError.dimensionMismatch(previous: previousSize, current: currentSize)
        }

        let previousLuma = try grayscaleBuffer(from: previous)
        let currentLuma = try grayscaleBuffer(from: current)
        let diff = absoluteDifference(previousLuma, currentLuma)
        let threshold = Float(noiseThreshold)
        let mask = diff.map { $0 > threshold }

        let components = connectedComponents(mask, width: analysisWidth, height: analysisHeight)
        guard !components.isEmpty else {
            return ChangeLocalizationResult(scale: .none, regions: [])
        }

        let scaleX = Double(previous.width) / Double(analysisWidth)
        let scaleY = Double(previous.height) / Double(analysisHeight)
        let regions = components.map { box -> CGRect in
            CGRect(
                x: Double(box.minX) * scaleX,
                y: Double(box.minY) * scaleY,
                width: Double(box.maxX - box.minX + 1) * scaleX,
                height: Double(box.maxY - box.minY + 1) * scaleY
            )
        }

        let changedPixelCount = mask.lazy.filter { $0 }.count
        let changedFraction = Double(changedPixelCount) / Double(analysisWidth * analysisHeight)
        let scale: ChangeScale
        if changedFraction > regionalFraction {
            scale = .fullFrame
        } else if changedFraction > localFraction {
            scale = .regional
        } else {
            scale = .local
        }

        return ChangeLocalizationResult(scale: scale, regions: regions)
    }

    /// Renders `image` into an 8-bit grayscale buffer at `analysisWidth` x `analysisHeight`.
    /// CoreGraphics performs the RGB-to-luma conversion; downscaling happens in the same draw.
    private func grayscaleBuffer(from image: CGImage) throws -> [UInt8] {
        var pixels = [UInt8](repeating: 0, count: analysisWidth * analysisHeight)
        let created: Bool = pixels.withUnsafeMutableBytes { buffer -> Bool in
            guard let context = CGContext(
                data: buffer.baseAddress,
                width: analysisWidth,
                height: analysisHeight,
                bitsPerComponent: 8,
                bytesPerRow: analysisWidth,
                space: CGColorSpaceCreateDeviceGray(),
                bitmapInfo: CGImageAlphaInfo.none.rawValue
            ) else {
                return false
            }
            context.interpolationQuality = .low
            context.draw(image, in: CGRect(x: 0, y: 0, width: analysisWidth, height: analysisHeight))
            return true
        }
        guard created else { throw ChangeRegionLocalizerError.grayscaleConversionFailed }
        return pixels
    }

    /// Per-pixel `|a - b|` via vDSP (Accelerate): convert both 8-bit luma buffers to `Float`,
    /// subtract, take the absolute value. Vectorized, and avoids `UInt8` subtraction underflow.
    private func absoluteDifference(_ a: [UInt8], _ b: [UInt8]) -> [Float] {
        let count = a.count
        var floatA = [Float](repeating: 0, count: count)
        var floatB = [Float](repeating: 0, count: count)
        vDSP_vfltu8(a, 1, &floatA, 1, vDSP_Length(count))
        vDSP_vfltu8(b, 1, &floatB, 1, vDSP_Length(count))

        var diff = [Float](repeating: 0, count: count)
        // vDSP_vsub(B, ..., A, ..., C, ..., N) computes C = A - B; since the result is
        // immediately made absolute, the operand order doesn't affect the outcome.
        vDSP_vsub(floatB, 1, floatA, 1, &diff, 1, vDSP_Length(count))
        vDSP_vabs(diff, 1, &diff, 1, vDSP_Length(count))
        return diff
    }

    /// 4-connected component labeling over a boolean mask, via iterative flood fill. The
    /// analysis buffer is small (default 480x270) so this stays cheap without needing a more
    /// elaborate union-find pass.
    private func connectedComponents(_ mask: [Bool], width: Int, height: Int) -> [(minX: Int, minY: Int, maxX: Int, maxY: Int)] {
        var visited = [Bool](repeating: false, count: mask.count)
        var boxes: [(minX: Int, minY: Int, maxX: Int, maxY: Int)] = []

        for startIndex in 0..<mask.count where mask[startIndex] && !visited[startIndex] {
            var stack = [startIndex]
            visited[startIndex] = true
            var minX = startIndex % width, maxX = minX
            var minY = startIndex / width, maxY = minY

            while let index = stack.popLast() {
                let x = index % width
                let y = index / width
                minX = min(minX, x); maxX = max(maxX, x)
                minY = min(minY, y); maxY = max(maxY, y)

                for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)] {
                    let nx = x + dx, ny = y + dy
                    guard nx >= 0, nx < width, ny >= 0, ny < height else { continue }
                    let neighborIndex = ny * width + nx
                    if mask[neighborIndex] && !visited[neighborIndex] {
                        visited[neighborIndex] = true
                        stack.append(neighborIndex)
                    }
                }
            }
            boxes.append((minX, minY, maxX, maxY))
        }
        return boxes
    }
}

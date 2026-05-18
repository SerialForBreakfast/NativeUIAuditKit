// ClippedContentViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// TASK-5a-2: Known-bad template — clipped content failure mode.
//
// Renders 4–6 UIView containers with `clipsToBounds = true`. Each container
// holds a child UIImageView that is 150–200% larger than the container in at
// least one dimension. The child image is a programmatically generated
// gradient/pattern so the clipping boundary is visually unambiguous.
//
// Annotated elements:
//   imageView (×4–6)  — each container annotated as `imageView` with
//                        knownIssues: ["clippedElement"]
//
// The oversized child UIImageView is NOT annotated — it is the clipped overflow.
// The annotated bounding box is the container (the visible frame), not the child.
//
// Layout: vertical stack of containers.
//   Container width  = containerWidthFraction × screenWidth (varies 0.55–0.90).
//   Container height = 80–130pt (varies per row).
//   Child is pinned top-left and sized containerW * childScaleW × containerH * childScaleH.
//   childScale{W,H} ∈ {1.5, 1.7, 1.9, 2.0} — always overflows at least one axis.
//
// Seed determinism: container sizes, child scales, gradient hues all derived
//   from `seed`. Same seed → identical PNG.

import UIKit

// MARK: - ClippedContentViewController

@MainActor
public final class ClippedContentViewController: UIViewController, UIKitAnnotatable {

    // MARK: - Types

    private struct ContentRow {
        let widthFraction: CGFloat    // fraction of screen width
        let containerH: CGFloat       // container height in points
        let childScaleW: CGFloat      // child width = containerW * childScaleW
        let childScaleH: CGFloat      // child height = containerH * childScaleH
        let hue: CGFloat              // 0–1, base hue for gradient
        let containerView: UIView
        let childImageView: UIImageView
    }

    // MARK: - State

    private let seed: UInt64
    private let runConfig: GeneratorRunConfig
    private var rows: [ContentRow] = []

    // MARK: - Init

    public init(seed: UInt64, config: GeneratorRunConfig) {
        self.seed = seed
        self.runConfig = config
        super.init(nibName: nil, bundle: nil)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) { fatalError("init(coder:) not used") }

    // MARK: - UIViewController

    public override func viewDidLoad() {
        super.viewDidLoad()
        UIView.setAnimationsEnabled(false)
        overrideUserInterfaceStyle = runConfig.colorScheme == .dark ? .dark : .light
        view.backgroundColor = .systemBackground
        setupRows()
    }

    public override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        layoutRows()
    }

    // MARK: - UIKitAnnotatable

    public var annotatedViews: [UIKitAnnotatedView] {
        rows.enumerated().map { i, row in
            UIKitAnnotatedView(
                id: "imageView_clipped_\(i)",
                elementType: "imageView",
                view: row.containerView,
                knownIssues: ["clippedElement"]
            )
        }
    }

    // MARK: - Setup

    private func setupRows() {
        var rng = SeededRNG(seed: seed)

        let rowCount = 4 + Int(rng.next() % 3)  // 4, 5, or 6

        // Width fractions: varies so containers appear at different widths
        let widthFractions: [CGFloat] = [0.60, 0.75, 0.90, 0.65, 0.80, 0.55]
        // Container heights (pt)
        let heights: [CGFloat] = [80, 100, 90, 120, 80, 110]
        // Child scale factors — always > 1 in at least one axis
        let childScalesW: [CGFloat] = [1.9, 1.5, 2.0, 1.7, 1.6, 1.8]
        let childScalesH: [CGFloat] = [1.6, 2.0, 1.5, 1.9, 1.7, 1.5]
        // Hue families: 6 distinct hue ranges, one per row
        let hueSeeds: [CGFloat] = [0.00, 0.15, 0.33, 0.55, 0.70, 0.85]

        for i in 0..<rowCount {
            let idx = i % widthFractions.count
            let fraction = widthFractions[idx]
            let containerH = heights[idx]
            let scaleW = childScalesW[idx]
            let scaleH = childScalesH[idx]
            // Offset hue slightly per seed to prevent all rows being identical across seeds
            let hueOffset = CGFloat(rng.next() % 20) / 100.0
            let hue = (hueSeeds[idx] + hueOffset).truncatingRemainder(dividingBy: 1.0)

            let containerView = UIView()
            containerView.clipsToBounds = true
            containerView.layer.cornerRadius = 8
            containerView.backgroundColor = .systemFill
            view.addSubview(containerView)

            // Generate gradient image larger than the container
            // Actual pixel size determined at layout time; use a placeholder for now.
            // Re-generated in layoutRows once we know the actual container size.
            let imageView = UIImageView()
            imageView.contentMode = .topLeft   // no scaling — show raw pixel overlap
            containerView.addSubview(imageView)

            rows.append(ContentRow(
                widthFraction: fraction,
                containerH: containerH,
                childScaleW: scaleW,
                childScaleH: scaleH,
                hue: hue,
                containerView: containerView,
                childImageView: imageView
            ))
        }
    }

    // MARK: - Layout

    private func layoutRows() {
        let safeTop = runConfig.osProfile.safeAreaTopInset
        let screenW = view.bounds.width
        let vGap: CGFloat = 24

        var y = safeTop + 32

        for row in rows {
            let containerW = (screenW * row.widthFraction).rounded()
            let containerX = ((screenW - containerW) / 2).rounded()

            row.containerView.frame = CGRect(
                x: containerX, y: y,
                width: containerW, height: row.containerH
            )

            // Child is always larger than the container — the overflow will be clipped
            let childW = (containerW * row.childScaleW).rounded()
            let childH = (row.containerH * row.childScaleH).rounded()

            // Regenerate (or update) gradient image at the correct size
            row.childImageView.image = makeGradientImage(
                width: childW, height: childH, hue: row.hue
            )
            row.childImageView.frame = CGRect(x: 0, y: 0, width: childW, height: childH)

            y += row.containerH + vGap
        }
    }

    // MARK: - Gradient image generation

    /// Builds a programmatic gradient image at the given size using the given hue.
    /// The gradient runs from the base hue (bright) to the complementary hue (muted)
    /// so that the clip boundary is immediately obvious in the rendered screenshot.
    private func makeGradientImage(width: CGFloat, height: CGFloat, hue: CGFloat) -> UIImage {
        let size = CGSize(width: max(width, 1), height: max(height, 1))
        let renderer = UIGraphicsImageRenderer(size: size)
        return renderer.image { ctx in
            let cg = ctx.cgContext
            let colorSpace = CGColorSpaceCreateDeviceRGB()

            // Two gradient stops: base hue (left/top) → complementary hue (right/bottom)
            let complementary = (hue + 0.5).truncatingRemainder(dividingBy: 1.0)
            let startColor = UIColor(hue: hue,          saturation: 0.85, brightness: 0.90, alpha: 1)
            let endColor   = UIColor(hue: complementary, saturation: 0.75, brightness: 0.70, alpha: 1)

            guard let gradient = CGGradient(
                colorsSpace: colorSpace,
                colors: [startColor.cgColor, endColor.cgColor] as CFArray,
                locations: [0, 1]
            ) else {
                cg.setFillColor(startColor.cgColor)
                cg.fill(CGRect(origin: .zero, size: size))
                return
            }

            // Diagonal gradient so both horizontal and vertical overflow are apparent
            cg.drawLinearGradient(
                gradient,
                start: .zero,
                end: CGPoint(x: size.width, y: size.height),
                options: []
            )

            // Add a thin white grid overlay so it's obvious how much has been clipped
            cg.setStrokeColor(UIColor.white.withAlphaComponent(0.25).cgColor)
            cg.setLineWidth(1)
            let gridSpacing: CGFloat = 20
            var gx: CGFloat = 0
            while gx <= size.width {
                cg.move(to: CGPoint(x: gx, y: 0))
                cg.addLine(to: CGPoint(x: gx, y: size.height))
                gx += gridSpacing
            }
            var gy: CGFloat = 0
            while gy <= size.height {
                cg.move(to: CGPoint(x: 0, y: gy))
                cg.addLine(to: CGPoint(x: size.width, y: gy))
                gy += gridSpacing
            }
            cg.strokePath()
        }
    }
}

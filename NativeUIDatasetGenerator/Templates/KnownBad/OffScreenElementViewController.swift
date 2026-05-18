// OffScreenElementViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// TASK-5a-7: Known-bad template — off-screen element failure mode.
//
// Renders a UIScrollView that contains a vertical list of UIButton rows.
// The scroll position is fixed so that:
//   - 3–4 rows are fully visible (annotated normally)
//   - 1 row is partially visible — bottom edge peeks into the visible frame
//     (annotated with occluded: true, occlusionType: "scroll", clipped box)
//   - 1–2 rows are entirely below the fold (NOT annotated — excluded)
//
// Annotation rules from the plan (Phase 1, P2/P3):
//   P2: Partially visible (scroll clip) → occluded: true, occlusionType: "scroll",
//       bounding box clipped to visible rect
//   P3: < 20% visible → excluded: true, exclusionReason: "insufficient_visible_area"
//       (which here means y > imageHeight — entirely off-screen → excluded entirely)
//
// Annotated elements:
//   primaryButton (×3–4) — fully visible, no knownIssues
//   primaryButton (×1)   — partially visible, occluded: true, occlusionType: "scroll"
//   (no annotation for fully off-screen rows)
//
// Layout:
//   UIScrollView fills the screen (minus safe areas).
//   8 button rows inside, each 60pt tall with 12pt gap.
//   contentOffset.y is fixed at 2.5 row heights so the 3rd partial row is visible.
//
// Seed determinism: button titles and tint colors from seed.

import UIKit

// MARK: - OffScreenElementViewController

@MainActor
public final class OffScreenElementViewController: UIViewController, UIKitAnnotatable {

    // MARK: - Types

    private struct ButtonInfo {
        let button: UIButton
        let title: String
        let rowIndex: Int
        /// Frame of the button in the scroll view's content coordinate space.
        var contentFrame: CGRect = .zero
    }

    // MARK: - State

    private let seed: UInt64
    private let runConfig: GeneratorRunConfig
    private var scrollView: UIScrollView!
    private var buttons: [ButtonInfo] = []

    private static let rowHeight: CGFloat = 60
    private static let rowGap: CGFloat = 12
    private static let totalRows = 8

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
        setupScrollView()
    }

    public override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        layoutScrollContent()
    }

    // MARK: - UIKitAnnotatable

    /// Returns only elements that are at least 20% visible in the scroll view's
    /// viewport. Fully off-screen rows are excluded. Partially visible rows use
    /// the clipped bounding box.
    public var annotatedViews: [UIKitAnnotatedView] {
        guard let sv = scrollView else { return [] }
        let viewport = sv.bounds  // the visible rect in scroll view's own coordinate space

        var result: [UIKitAnnotatedView] = []

        for info in buttons {
            // Convert button's frame from content space to scroll view viewport space
            let buttonFrameInContent = info.button.frame
            let buttonFrameInViewport = CGRect(
                x: buttonFrameInContent.minX,
                y: buttonFrameInContent.minY - sv.contentOffset.y,
                width: buttonFrameInContent.width,
                height: buttonFrameInContent.height
            )

            // Intersection with viewport
            let intersection = viewport.intersection(buttonFrameInViewport)

            // If no intersection — entirely off-screen → exclude (P3)
            guard !intersection.isNull && intersection.height > 0 else { continue }

            // Compute visible fraction
            let visibleFraction = intersection.height / buttonFrameInViewport.height

            // < 20% visible → exclude (P3 rule)
            if visibleFraction < 0.20 { continue }

            let isOccluded = visibleFraction < 0.99

            // We annotate the button via a proxy UIView positioned in view-root space.
            // Since UIKitCaptureSupport uses v.convert(v.bounds, to: viewController.view),
            // we just use the button itself — captureUIKit will compute the correct
            // root-space frame including the scroll offset.
            result.append(UIKitAnnotatedView(
                id: "primaryButton_scroll_\(info.rowIndex)",
                elementType: "primaryButton",
                view: info.button,
                visibleText: info.title,
                knownIssues: []     // scroll-off is not a knownIssue — it's an occluded annotation
            ))
            // Note: occluded/occlusionType are on AnnotatedElement, not UIKitAnnotatedView.
            // The captureUIKit path will compute the final clipped frame. For the dataset's
            // occluded/occlusionType metadata, we rely on the GeneratorRunner's post-process
            // step (TASK-5a-7's generation run). The VC's job here is to not annotate
            // fully-off-screen rows and to annotate the partial row normally —
            // the annotation writer sets occluded=true based on frame clipping.
        }

        return result
    }

    // MARK: - Setup

    private func setupScrollView() {
        scrollView = UIScrollView()
        scrollView.isScrollEnabled = false   // fixed scroll position — deterministic
        scrollView.showsVerticalScrollIndicator = false
        view.addSubview(scrollView)

        var corpus = ContentCorpus(seed: seed)
        var rng = SeededRNG(seed: seed)

        let hues: [CGFloat] = [0.00, 0.10, 0.33, 0.55, 0.65, 0.80, 0.20, 0.45]

        for i in 0..<Self.totalRows {
            let hue = hues[i % hues.count]
            let tint = UIColor(hue: hue, saturation: 0.75, brightness: 0.85, alpha: 1)
            let title = corpus.personName()

            var cfg = UIButton.Configuration.filled()
            cfg.baseBackgroundColor = tint
            cfg.baseForegroundColor = .white
            cfg.title = title
            cfg.cornerStyle = .fixed

            let button = UIButton(configuration: cfg)
            button.layer.cornerRadius = 8
            button.clipsToBounds = true
            scrollView.addSubview(button)

            buttons.append(ButtonInfo(button: button, title: title, rowIndex: i))
        }
    }

    // MARK: - Layout

    private func layoutScrollContent() {
        let safeTop = runConfig.osProfile.safeAreaTopInset
        let safeBottom = runConfig.osProfile.safeAreaBottomInset
        let screenW = view.bounds.width
        let screenH = view.bounds.height

        let scrollH = screenH - safeTop - safeBottom
        scrollView.frame = CGRect(x: 0, y: safeTop, width: screenW, height: scrollH)

        let buttonW = screenW - 32
        let buttonX: CGFloat = 16

        var contentY: CGFloat = 12

        for i in 0..<buttons.count {
            let frame = CGRect(x: buttonX, y: contentY,
                               width: buttonW, height: Self.rowHeight)
            buttons[i].button.frame = frame
            buttons[i].contentFrame = frame
            contentY += Self.rowHeight + Self.rowGap
        }

        let totalContentH = contentY
        scrollView.contentSize = CGSize(width: screenW, height: totalContentH)

        // Fix scroll offset so:
        //   Rows 0–2 are fully visible (0-based)
        //   Row 3 is partially visible (about 60% of its height shows)
        //   Rows 4–7 are below the fold
        // We scroll down by 2.4 row heights so row 2's top is at ~y=0 of viewport.
        let offsetY = (Self.rowHeight + Self.rowGap) * 2.4
        scrollView.contentOffset = CGPoint(x: 0, y: offsetY)
    }
}

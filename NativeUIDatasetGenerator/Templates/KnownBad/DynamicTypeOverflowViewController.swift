// DynamicTypeOverflowViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// TASK-5a-5: Known-bad template — Dynamic Type overflow failure mode.
//
// Renders fixed-height containers with UILabel content at
// AccessibilityExtraExtraExtraLarge (AXXXL) Dynamic Type size.
// The text overflows the fixed container height, demonstrating the
// "container too small for large accessibility type" failure mode.
//
// Annotated elements:
//   label (×4–6) — each container annotated as `label` with
//                   knownIssues: ["dynamicTypeOverflow"]
//
// The annotation bounding box is the container (the constrained, fixed-height
// frame), NOT the full intrinsic content size of the label.
//
// Layout: vertical stack of containers.
//   Container width  = 85% of screen width (fixed — it's the height that fails).
//   Container height = 36–50pt (fixed, smaller than AXXXL text requires).
//   UILabel inside container: numberOfLines=1, clipsToBounds=true on container,
//   so text is clipped at the container boundary.
//
// The `dynamicTypeSize` in `GeneratorRunConfig` must be set to
// `accessibilityExtraExtraExtraLarge` for this template family.
// The runner enforces this; the VC also sets the font explicitly at AXXXL
// to guarantee overflow even when run in unexpected Dynamic Type environments.
//
// Seed determinism: text content, container heights, font weights derived from seed.

import UIKit

// MARK: - DynamicTypeOverflowViewController

@MainActor
public final class DynamicTypeOverflowViewController: UIViewController, UIKitAnnotatable {

    // MARK: - Types

    private struct OverflowRow {
        let containerH: CGFloat     // fixed height, smaller than AXXXL text requires
        let fontWeight: UIFont.Weight
        let text: String
        let containerView: UIView
        let label: UILabel
    }

    // MARK: - State

    private let seed: UInt64
    private let runConfig: GeneratorRunConfig
    private var rows: [OverflowRow] = []

    // MARK: - Constants

    /// Font size at AXXXL Dynamic Type for UIFont.TextStyle.body.
    /// iOS rounds up to 53pt for body at AXXXL. We hard-code this to ensure
    /// overflow regardless of the simulator's actual Dynamic Type setting.
    private static let axxxlBodySize: CGFloat = 53

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
                id: "label_dtOverflow_\(i)",
                elementType: "label",
                view: row.containerView,
                visibleText: row.label.text,
                knownIssues: ["dynamicTypeOverflow"]
            )
        }
    }

    // MARK: - Setup

    private func setupRows() {
        var rng = SeededRNG(seed: seed)
        var corpus = ContentCorpus(seed: seed)

        let rowCount = 4 + Int(rng.next() % 3)  // 4–6 rows

        // Fixed container heights that are too small for AXXXL body text (~53pt).
        // These heights represent typical "design at default size" container heights.
        let containerHeights: [CGFloat] = [36, 44, 40, 50, 36, 44]

        // Font weights for variety
        let weights: [UIFont.Weight] = [.regular, .medium, .semibold, .regular, .medium, .regular]

        for i in 0..<rowCount {
            let containerH = containerHeights[i % containerHeights.count]
            let weight = weights[i % weights.count]

            // Realistic UI text that would appear in a list cell, nav title, or form label
            let text = corpus.shortPhrase()

            let containerView = UIView()
            containerView.backgroundColor = UIColor.systemGray6
            containerView.clipsToBounds = true     // clips the overflowing text
            containerView.layer.cornerRadius = 6
            view.addSubview(containerView)

            let label = UILabel()
            label.text = text
            // Hard-code AXXXL font size so overflow is guaranteed in all environments
            label.font = .systemFont(ofSize: Self.axxxlBodySize, weight: weight)
            label.textColor = .label
            label.numberOfLines = 1
            label.lineBreakMode = .byTruncatingTail
            containerView.addSubview(label)

            rows.append(OverflowRow(
                containerH: containerH,
                fontWeight: weight,
                text: text,
                containerView: containerView,
                label: label
            ))
        }
    }

    // MARK: - Layout

    private func layoutRows() {
        let safeTop = runConfig.osProfile.safeAreaTopInset
        let screenW = view.bounds.width
        let containerW = (screenW * 0.85).rounded()
        let containerX = ((screenW - containerW) / 2).rounded()
        let vGap: CGFloat = 24
        let labelInsetX: CGFloat = 8

        var y = safeTop + 32

        for row in rows {
            row.containerView.frame = CGRect(
                x: containerX, y: y,
                width: containerW, height: row.containerH
            )

            // Label fills container width (minus insets); vertically it will overflow
            // because AXXXL font height > container height.
            row.label.frame = CGRect(
                x: labelInsetX,
                y: 0,
                width: containerW - 2 * labelInsetX,
                height: row.containerH   // same as container — text clips at bottom
            )

            y += row.containerH + vGap
        }
    }
}

// MARK: - ContentCorpus extension for short phrases

private extension ContentCorpus {
    /// Returns a short realistic phrase suitable for a label/cell/title.
    mutating func shortPhrase() -> String {
        "\(personName()) — \(placeName())"
    }
}

// TruncatedLabelViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// TASK-5a-1: Known-bad template — truncated label failure mode.
//
// Renders 4–6 UILabel instances in containers intentionally narrower than the
// text content, forcing tail truncation ("…"). Each label is annotated as
// `elementType: "label"` with `knownIssues: ["truncatedText"]`.
//
// Purpose: training examples where the model detects a label AND the audit
// layer flags it as truncated. The bounding box covers the *visible* label
// frame, not the full text extent.
//
// Annotated elements:
//   label (×4–6)  — each has knownIssues: ["truncatedText"]
//
// Layout: vertical stack of (containerView → UILabel) pairs.
//   Container width = containerFraction × screenWidth (varies 0.30–0.65 by row).
//   Label is edge-pinned inside its container with horizontal insets.
//   The text is always longer than the container allows at the chosen font.
//
// Seed determinism: container widths, font sizes, text content, color scheme
//   are all derived from `seed`. Same seed → identical PNG.

import UIKit

// MARK: - TruncatedLabelViewController

@MainActor
public final class TruncatedLabelViewController: UIViewController, UIKitAnnotatable {

    // MARK: - Types

    private struct LabelRow {
        let containerFraction: CGFloat  // fraction of screen width for the container
        let fontSize: CGFloat
        let text: String
        let containerView: UIView
        let label: UILabel
    }

    // MARK: - State

    private let seed: UInt64
    private let runConfig: GeneratorRunConfig
    private var rows: [LabelRow] = []

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
                id: "label_truncated_\(i)",
                elementType: "label",
                view: row.label,
                visibleText: row.label.text,
                knownIssues: ["truncatedText"]
            )
        }
    }

    // MARK: - Setup

    private func setupRows() {
        var rng = SeededRNG(seed: seed)
        var corpus = ContentCorpus(seed: seed)

        // Container-width fractions — vary row by row (30%–65% of screen width)
        let fractions: [CGFloat] = [0.30, 0.40, 0.50, 0.42, 0.35, 0.60]
        // Font sizes — vary to produce different truncation depths
        let fontSizes: [CGFloat] = [17, 20, 24, 17, 22, 19]
        let rowCount = 4 + Int(rng.next() % 3)  // 4, 5, or 6 rows

        // Long strings guaranteed to overflow at the chosen container widths.
        // We build them from corpus text joined together so they're realistic.
        let longTexts: [String] = (0..<rowCount).map { _ in
            let a = corpus.personName()
            let b = corpus.companyName()
            let c = corpus.placeName()
            return "\(a) — \(b), \(c)"    // always ~35–55 chars
        }

        for i in 0..<rowCount {
            let fraction = fractions[i % fractions.count]
            let fontSize = fontSizes[i % fontSizes.count]
            let text = longTexts[i]

            let containerView = UIView()
            containerView.backgroundColor = UIColor(
                red: 0.96 + CGFloat(i % 3) * 0.01,
                green: 0.96,
                blue: 0.96,
                alpha: 1
            )
            containerView.layer.cornerRadius = 6
            containerView.clipsToBounds = true
            view.addSubview(containerView)

            let label = UILabel()
            label.text = text
            label.font = .systemFont(ofSize: fontSize, weight: .regular)
            label.textColor = .label
            label.lineBreakMode = .byTruncatingTail
            label.numberOfLines = 1
            containerView.addSubview(label)

            rows.append(LabelRow(
                containerFraction: fraction,
                fontSize: fontSize,
                text: text,
                containerView: containerView,
                label: label
            ))
        }
    }

    // MARK: - Layout

    private func layoutRows() {
        let safeTop = runConfig.osProfile.safeAreaTopInset
        let width = view.bounds.width
        let rowH: CGFloat = 48
        let vGap: CGFloat = 20
        let labelInset: CGFloat = 10

        var y = safeTop + 32

        for row in rows {
            let containerW = (width * row.containerFraction).rounded()
            let containerX = (width - containerW) / 2     // centred
            row.containerView.frame = CGRect(x: containerX, y: y,
                                             width: containerW, height: rowH)

            // Label fills the container horizontally (minus small insets) so
            // the frame represents the *visible* label extent, not the text extent.
            row.label.frame = CGRect(
                x: labelInset,
                y: (rowH - row.fontSize - 4) / 2,
                width: containerW - 2 * labelInset,
                height: row.fontSize + 4
            )

            y += rowH + vGap
        }
    }
}

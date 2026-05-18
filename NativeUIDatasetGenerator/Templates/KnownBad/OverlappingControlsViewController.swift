// OverlappingControlsViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// TASK-5a-3: Known-bad template — overlapping controls failure mode.
//
// Renders pairs of UIButton controls whose frames overlap with IoU > 0.1.
// Both controls in each pair are annotated normally (no knownIssues — the
// overlap is flagged at the observation-merge layer in Phase 7, not here).
//
// Five distinct overlap configurations per spec (different element pairs,
// different overlap amounts: 10–50% IoU):
//
//   Config 0: Two 120×44pt buttons, horizontal overlap ~10% IoU
//   Config 1: Two 100×44pt buttons, horizontal overlap ~25% IoU
//   Config 2: Two 80×80pt icon buttons, diagonal overlap ~35% IoU
//   Config 3: A 160×44pt button + 80×44pt button, 50% IoU overlap (second inside first)
//   Config 4: Two 140×50pt buttons, vertical overlap ~20% IoU
//
// Each screen renders all 5 configurations stacked vertically, with seed
// controlling tint colors and SF Symbol indices.
//
// Annotated elements:
//   primaryButton (×10) — two per overlap config; no knownIssues (overlap is detected
//                          at inference time, not at generation time)
//
// Seed determinism: tint hues and symbol indices derived from `seed`.

import UIKit

// MARK: - OverlappingControlsViewController

@MainActor
public final class OverlappingControlsViewController: UIViewController, UIKitAnnotatable {

    // MARK: - Types

    private struct OverlapConfig {
        let buttonAWidth:  CGFloat
        let buttonAHeight: CGFloat
        let buttonBWidth:  CGFloat
        let buttonBHeight: CGFloat
        /// Offset of button B's origin relative to button A's origin, producing IoU > 0.1.
        let bOffsetX: CGFloat
        let bOffsetY: CGFloat
        let label: String   // descriptive label (not annotated)
    }

    private struct OverlapRow {
        let config: OverlapConfig
        let buttonA: UIButton
        let buttonB: UIButton
        let headerLabel: UILabel
        /// Anchor point for the row's button cluster in the view's coordinate space.
        var rowY: CGFloat = 0
    }

    // MARK: - State

    private let seed: UInt64
    private let runConfig: GeneratorRunConfig
    private var rows: [OverlapRow] = []

    // MARK: - Constants

    private static let configs: [OverlapConfig] = [
        // 0: Horizontal, ~10% IoU — slight overlap on right edge
        OverlapConfig(buttonAWidth: 120, buttonAHeight: 44, buttonBWidth: 120, buttonBHeight: 44,
                      bOffsetX: 108, bOffsetY: 0,
                      label: "Horizontal ~10% IoU"),
        // 1: Horizontal, ~25% IoU
        OverlapConfig(buttonAWidth: 100, buttonAHeight: 44, buttonBWidth: 100, buttonBHeight: 44,
                      bOffsetX: 75, bOffsetY: 0,
                      label: "Horizontal ~25% IoU"),
        // 2: Diagonal, ~35% IoU (offset in both axes)
        OverlapConfig(buttonAWidth: 80, buttonAHeight: 80, buttonBWidth: 80, buttonBHeight: 80,
                      bOffsetX: 52, bOffsetY: 52,
                      label: "Diagonal ~35% IoU"),
        // 3: ~50% IoU — second button starts at midpoint of first
        OverlapConfig(buttonAWidth: 160, buttonAHeight: 44, buttonBWidth: 80, buttonBHeight: 44,
                      bOffsetX: 80, bOffsetY: 0,
                      label: "50% IoU — B inside A's right half"),
        // 4: Vertical overlap, ~20% IoU
        OverlapConfig(buttonAWidth: 140, buttonAHeight: 50, buttonBWidth: 140, buttonBHeight: 50,
                      bOffsetX: 0, bOffsetY: 40,
                      label: "Vertical ~20% IoU"),
    ]

    private static let hues: [CGFloat] = [0.00, 0.55, 0.10, 0.70, 0.33, 0.85]
    private static let symbols = [
        "star.fill", "heart.fill", "bolt.fill", "bell.fill",
        "bookmark.fill", "flag.fill", "hand.thumbsup.fill", "checkmark.circle.fill",
    ]

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
        var result: [UIKitAnnotatedView] = []
        for (i, row) in rows.enumerated() {
            result.append(UIKitAnnotatedView(
                id: "primaryButton_overlap_\(i)_a",
                elementType: "primaryButton",
                view: row.buttonA
                // No knownIssues — overlap is a Phase 7 inference-time concern
            ))
            result.append(UIKitAnnotatedView(
                id: "primaryButton_overlap_\(i)_b",
                elementType: "primaryButton",
                view: row.buttonB
            ))
        }
        return result
    }

    // MARK: - Setup

    private func setupRows() {
        var rng = SeededRNG(seed: seed)
        let hueA  = Self.hues[Int(rng.next() % UInt64(Self.hues.count))]
        let hueB  = (hueA + 0.5).truncatingRemainder(dividingBy: 1.0)
        let symOff = Int(rng.next() % UInt64(Self.symbols.count))

        let tintA = UIColor(hue: hueA, saturation: 0.80, brightness: 0.88, alpha: 1)
        let tintB = UIColor(hue: hueB, saturation: 0.80, brightness: 0.88, alpha: 1)

        for (i, config) in Self.configs.enumerated() {
            let header = UILabel()
            header.text = config.label
            header.font = .systemFont(ofSize: 12, weight: .regular)
            header.textColor = .secondaryLabel
            header.textAlignment = .left
            view.addSubview(header)

            let symA = Self.symbols[(symOff + i * 2)     % Self.symbols.count]
            let symB = Self.symbols[(symOff + i * 2 + 1) % Self.symbols.count]

            let buttonA = makeButton(title: symA, tint: tintA, size: CGSize(width: config.buttonAWidth, height: config.buttonAHeight))
            let buttonB = makeButton(title: symB, tint: tintB, size: CGSize(width: config.buttonBWidth, height: config.buttonBHeight))
            view.addSubview(buttonA)
            view.addSubview(buttonB)

            rows.append(OverlapRow(config: config, buttonA: buttonA, buttonB: buttonB, headerLabel: header))
        }
    }

    private func makeButton(title symbolName: String, tint: UIColor, size: CGSize) -> UIButton {
        var cfg = UIButton.Configuration.filled()
        cfg.baseBackgroundColor = tint
        cfg.baseForegroundColor = .white
        let ptSize = min(size.width, size.height) * 0.38
        cfg.image = UIImage(systemName: symbolName)?
            .withConfiguration(UIImage.SymbolConfiguration(pointSize: max(ptSize, 10)))
        cfg.contentInsets = .zero
        cfg.cornerStyle = .fixed
        let button = UIButton(configuration: cfg)
        button.layer.cornerRadius = 8
        button.clipsToBounds = true
        return button
    }

    // MARK: - Layout

    private func layoutRows() {
        let safeTop = runConfig.osProfile.safeAreaTopInset
        let screenW = view.bounds.width
        let headerH: CGFloat = 18
        let clusterTopMargin: CGFloat = 6
        let vGapBetweenRows: CGFloat = 28

        var y = safeTop + 28

        for i in 0..<rows.count {
            let config = rows[i].config

            // Header
            rows[i].headerLabel.frame = CGRect(x: 16, y: y, width: screenW - 32, height: headerH)
            y += headerH + clusterTopMargin

            // Compute bounding box of the two-button cluster so we can centre it
            let clusterW = config.bOffsetX >= 0
                ? max(config.buttonAWidth,  config.bOffsetX + config.buttonBWidth)
                : config.buttonBWidth + abs(config.bOffsetX)
            let clusterH = config.bOffsetY >= 0
                ? max(config.buttonAHeight, config.bOffsetY + config.buttonBHeight)
                : config.buttonBHeight + abs(config.bOffsetY)

            let clusterX = ((screenW - clusterW) / 2).rounded()

            // Button A at cluster origin
            rows[i].buttonA.frame = CGRect(
                x: clusterX,
                y: y,
                width: config.buttonAWidth,
                height: config.buttonAHeight
            )

            // Button B offset from A
            rows[i].buttonB.frame = CGRect(
                x: (clusterX + config.bOffsetX).rounded(),
                y: (y + config.bOffsetY).rounded(),
                width: config.buttonBWidth,
                height: config.buttonBHeight
            )

            y += clusterH + vGapBetweenRows
        }
    }
}

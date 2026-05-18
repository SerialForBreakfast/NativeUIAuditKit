// SmallHitTargetViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// TASK-5a-4: Known-bad template — small hit-target failure mode.
//
// Renders UIButton controls at sizes below the Apple HIG 44×44pt minimum.
// The four canonical sub-minimum sizes are:
//   20×20pt  — square, both axes fail
//   30×30pt  — square, both axes fail
//   32×44pt  — narrow but full height; only width fails
//   44×20pt  — full width but short; only height fails
//
// Each screen includes all four sizes (one row each), then repeats with
// seed-varied tint colors, SF Symbols, and layout positions to produce
// visual diversity across seeds.
//
// Annotated elements:
//   primaryButton (×4 per screen) — each has knownIssues: ["tappableTargetTooSmall"]
//                                     for every button with either dimension < 44pt
//
// knownIssues rule from spec:
//   `knownIssues: ["tappableTargetTooSmall"]` iff `width < 44 || height < 44`
//   So 20×20, 30×30, 32×44, 44×20 ALL get the flag.
//
// Layout: each row contains one small button centered in a labeled container row.
//   A UILabel above each button names its size (not annotated — structural label).
//   Seed controls tint hue and SF Symbol index.
//
// Seed determinism: tint color, symbol index, background color all derived from seed.

import UIKit

// MARK: - SmallHitTargetViewController

@MainActor
public final class SmallHitTargetViewController: UIViewController, UIKitAnnotatable {

    // MARK: - Types

    /// Canonical sub-minimum hit-target sizes from the spec.
    private struct HitTargetSpec {
        let width: CGFloat
        let height: CGFloat
        let label: String     // descriptive label shown above the button (not annotated)
    }

    private struct ButtonRow {
        let spec: HitTargetSpec
        let button: UIButton
        let headerLabel: UILabel
    }

    // MARK: - State

    private let seed: UInt64
    private let runConfig: GeneratorRunConfig
    private var rows: [ButtonRow] = []

    // MARK: - Constants

    // The four canonical sizes from the spec — fixed, not seed-varied.
    private static let specs: [HitTargetSpec] = [
        HitTargetSpec(width: 20, height: 20, label: "20×20pt — both axes below minimum"),
        HitTargetSpec(width: 30, height: 30, label: "30×30pt — both axes below minimum"),
        HitTargetSpec(width: 32, height: 44, label: "32×44pt — width below minimum"),
        HitTargetSpec(width: 44, height: 20, label: "44×20pt — height below minimum"),
    ]

    // SF Symbols used as button icons — varied by seed
    private static let symbols = [
        "star.fill", "heart.fill", "bolt.fill", "bell.fill",
        "bookmark.fill", "flag.fill", "hand.thumbsup.fill", "checkmark.circle.fill",
    ]

    // Tint hue families — varied by seed
    private static let hues: [CGFloat] = [0.00, 0.10, 0.33, 0.55, 0.65, 0.80]

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
                id: "primaryButton_smallTarget_\(i)",
                elementType: "primaryButton",
                view: row.button,
                visibleText: nil,     // icon-only buttons have no visible text string
                knownIssues: ["tappableTargetTooSmall"]
            )
        }
    }

    // MARK: - Setup

    private func setupRows() {
        var rng = SeededRNG(seed: seed)

        // Pick seed-derived hue and symbol offset
        let hue = Self.hues[Int(rng.next() % UInt64(Self.hues.count))]
        let symbolOffset = Int(rng.next() % UInt64(Self.symbols.count))
        let tintColor = UIColor(hue: hue, saturation: 0.80, brightness: 0.90, alpha: 1)

        for (i, spec) in Self.specs.enumerated() {
            // Header label (not annotated)
            let header = UILabel()
            header.text = spec.label
            header.font = .systemFont(ofSize: 13, weight: .regular)
            header.textColor = .secondaryLabel
            header.textAlignment = .center
            header.numberOfLines = 1
            view.addSubview(header)

            // Button with SF Symbol icon
            let symbolName = Self.symbols[(symbolOffset + i) % Self.symbols.count]
            let config = UIButton.Configuration.filled()
            var buttonConfig = config
            buttonConfig.baseForegroundColor = .white
            buttonConfig.baseBackgroundColor = tintColor
            buttonConfig.image = UIImage(systemName: symbolName)?
                .withConfiguration(UIImage.SymbolConfiguration(pointSize: min(spec.width, spec.height) * 0.45))
            buttonConfig.contentInsets = .zero   // no insets — the button IS the target size
            buttonConfig.cornerStyle = .fixed

            let button = UIButton(configuration: buttonConfig)
            button.layer.cornerRadius = min(spec.width, spec.height) * 0.25
            button.clipsToBounds = true
            view.addSubview(button)

            rows.append(ButtonRow(spec: spec, button: button, headerLabel: header))
        }
    }

    // MARK: - Layout

    private func layoutRows() {
        let safeTop = runConfig.osProfile.safeAreaTopInset
        let screenW = view.bounds.width
        let headerH: CGFloat = 20
        let vGapAfterHeader: CGFloat = 8
        let vGapBetweenRows: CGFloat = 36
        let maxButtonH: CGFloat = Self.specs.map(\.height).max() ?? 44

        var y = safeTop + 40

        for row in rows {
            // Header label — full width, centred
            row.headerLabel.frame = CGRect(
                x: 16,
                y: y,
                width: screenW - 32,
                height: headerH
            )
            y += headerH + vGapAfterHeader

            // Button — centred horizontally at its exact spec size
            let bx = ((screenW - row.spec.width) / 2).rounded()
            row.button.frame = CGRect(
                x: bx,
                y: y,
                width: row.spec.width,
                height: row.spec.height
            )

            // Advance y by maxButtonH so rows have consistent spacing
            y += maxButtonH + vGapBetweenRows
        }
    }
}

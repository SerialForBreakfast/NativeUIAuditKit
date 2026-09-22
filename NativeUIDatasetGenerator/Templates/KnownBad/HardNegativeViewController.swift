// HardNegativeViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// TASK-5a-9: Known-bad template — hard negatives generator.
//
// Two hard-negative template types — images where the model should produce
// NO detections:
//
//   Type 1 — LOADING_OVERLAY: UIActivityIndicatorView centred on a dimmed UIView
//             covering the entire screen. The overlay has NO annotations (elements: []).
//
//   Type 3 — DECORATIVE_FILL: UIImageView with a programmatic gradient taking up
//             >80% of the screen. Zero annotations (elements: []).
//
// Public API:
//   `HardNegativeViewController(type:seed:config:)`
//   `type` ∈ HardNegativeType enum.
//
// Seed determinism:
//   Type 1: dimmed background hue derived from seed
//   Type 3: gradient hues derived from seed

import UIKit

// MARK: - HardNegativeType

public enum HardNegativeType: Int, CaseIterable {
    case loadingOverlay  = 1
    case decorativeFill  = 3
}

// MARK: - HardNegativeViewController

@MainActor
public final class HardNegativeViewController: UIViewController, UIKitAnnotatable {

    // MARK: - State

    private let hardNegativeType: HardNegativeType
    private let seed: UInt64
    private let runConfig: GeneratorRunConfig

    // MARK: - Init

    public init(type: HardNegativeType, seed: UInt64, config: GeneratorRunConfig) {
        self.hardNegativeType = type
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

        switch hardNegativeType {
        case .loadingOverlay: setupLoadingOverlay()
        case .decorativeFill: setupDecorativeFill()
        }
    }

    public override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        switch hardNegativeType {
        case .loadingOverlay: layoutLoadingOverlay()
        case .decorativeFill: layoutDecorativeFill()
        }
    }

    // MARK: - UIKitAnnotatable

    public var annotatedViews: [UIKitAnnotatedView] {
        switch hardNegativeType {
        case .loadingOverlay:
            // Spec: NO annotations — elements: []
            return []

        case .decorativeFill:
            // Spec: zero annotations
            return []
        }
    }

    // MARK: - Type 1: Loading Overlay

    private var spinnerView: UIActivityIndicatorView?
    private var overlayBackground: UIView?

    private func setupLoadingOverlay() {
        var rng = SeededRNG(seed: seed)

        // Seed-varied dim color (neutral — not a strong hue so it doesn't confuse models)
        let dimAlpha: CGFloat = 0.55 + CGFloat(rng.next() % 25) / 100.0
        let dimColor = UIColor.black.withAlphaComponent(dimAlpha)

        // Root background — shows through the dimmed overlay
        // A dark system background collapsed every dim-alpha variant to black.
        // Seed meaningful, low-saturation backdrop/contrast variation instead.
        let hue = CGFloat(rng.next() % 360) / 360
        let brightness = 0.25 + CGFloat(rng.next() % 51) / 100
        view.backgroundColor = UIColor(hue: hue, saturation: 0.15, brightness: brightness, alpha: 1)

        // Dimmed overlay covering entire screen
        let overlay = UIView()
        overlay.backgroundColor = dimColor
        view.addSubview(overlay)
        overlayBackground = overlay

        // Spinner
        let spinner: UIActivityIndicatorView
        if rng.next() % 2 == 0 {
            spinner = UIActivityIndicatorView(style: .large)
            spinner.color = .white
        } else {
            spinner = UIActivityIndicatorView(style: .medium)
            spinner.color = .white
        }
        // Deliberately never call startAnimating(). UIActivityIndicatorView tracks its
        // own isAnimating state internally and can reinstate the rotation CAAnimation on
        // a later layout/window-attach pass even after layer.removeAllAnimations() — that
        // approach was tried and still produced non-deterministic captures. Staying in the
        // stopped state renders the full static spinner glyph with no rotation at all;
        // hidesWhenStopped just needs to be disabled so it doesn't hide itself.
        spinner.hidesWhenStopped = false
        overlay.addSubview(spinner)
        spinnerView = spinner
    }

    private func layoutLoadingOverlay() {
        let bounds = view.bounds
        overlayBackground?.frame = bounds
        if let spinner = spinnerView {
            spinner.sizeToFit()
            spinner.center = CGPoint(x: bounds.midX, y: bounds.midY)
        }
    }

    // MARK: - Type 3: Decorative Fill

    private var gradientImageView: UIImageView?

    private func setupDecorativeFill() {
        view.backgroundColor = .black
        let imageView = UIImageView()
        imageView.contentMode = .scaleAspectFill
        view.addSubview(imageView)
        gradientImageView = imageView
    }

    private func layoutDecorativeFill() {
        guard let imageView = gradientImageView else { return }

        let bounds = view.bounds
        imageView.frame = bounds   // fills >80% of screen

        // Generate a seed-varied multi-stop gradient covering the full screen
        var rng = SeededRNG(seed: seed)
        let hue1 = CGFloat(rng.next() % 100) / 100.0
        let hue2 = (hue1 + 0.3).truncatingRemainder(dividingBy: 1.0)
        let hue3 = (hue1 + 0.6).truncatingRemainder(dividingBy: 1.0)

        let renderer = UIGraphicsImageRenderer(bounds: bounds)
        let image = renderer.image { ctx in
            let cg = ctx.cgContext
            let colorSpace = CGColorSpaceCreateDeviceRGB()
            let c1 = UIColor(hue: hue1, saturation: 0.90, brightness: 0.95, alpha: 1)
            let c2 = UIColor(hue: hue2, saturation: 0.80, brightness: 0.70, alpha: 1)
            let c3 = UIColor(hue: hue3, saturation: 0.75, brightness: 0.55, alpha: 1)

            if let gradient = CGGradient(
                colorsSpace: colorSpace,
                colors: [c1.cgColor, c2.cgColor, c3.cgColor] as CFArray,
                locations: [0, 0.5, 1.0]
            ) {
                cg.drawLinearGradient(
                    gradient,
                    start: CGPoint(x: 0, y: 0),
                    end: CGPoint(x: bounds.width, y: bounds.height),
                    options: []
                )
            }
        }
        imageView.image = image
    }

}

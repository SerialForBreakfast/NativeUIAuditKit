// HardNegativeViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// TASK-5a-9: Known-bad template — hard negatives generator.
//
// Three hard-negative template types — images where the model should produce
// NO detections or only `webContent`:
//
//   Type 1 — LOADING_OVERLAY: UIActivityIndicatorView centred on a dimmed UIView
//             covering the entire screen. The overlay has NO annotations (elements: []).
//
//   Type 2 — WEB_CONTENT: WKWebView rendering simple HTML that visually mimics a
//             button, text field, and navigation bar. Annotated as a single `webContent`
//             element spanning the WKWebView bounds. NOT as button/textField/navigationBar.
//             Note: WKWebView requires async loading; we use a static HTML string and a
//             semaphore to wait for didFinish before capture.
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
//   Type 2: HTML accent colors derived from seed
//   Type 3: gradient hues derived from seed

import UIKit
import WebKit

// MARK: - HardNegativeType

public enum HardNegativeType: Int, CaseIterable {
    case loadingOverlay  = 1
    case webContent      = 2
    case decorativeFill  = 3
}

// MARK: - HardNegativeViewController

@MainActor
public final class HardNegativeViewController: UIViewController, UIKitAnnotatable, WKNavigationDelegate {

    // MARK: - State

    private let hardNegativeType: HardNegativeType
    private let seed: UInt64
    private let runConfig: GeneratorRunConfig

    // Type 2 only
    private var webView: WKWebView?
    private var webViewDidLoad = false

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
        case .webContent:     setupWebContent()
        case .decorativeFill: setupDecorativeFill()
        }
    }

    public override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        switch hardNegativeType {
        case .loadingOverlay: layoutLoadingOverlay()
        case .webContent:     layoutWebContent()
        case .decorativeFill: layoutDecorativeFill()
        }
    }

    // MARK: - UIKitAnnotatable

    public var annotatedViews: [UIKitAnnotatedView] {
        switch hardNegativeType {
        case .loadingOverlay:
            // Spec: NO annotations — elements: []
            return []

        case .webContent:
            // Single webContent annotation spanning the WKWebView bounds
            guard let wv = webView else { return [] }
            return [UIKitAnnotatedView(
                id: "webContent_0",
                elementType: "webContent",
                view: wv,
                knownIssues: []
            )]

        case .decorativeFill:
            // Spec: zero annotations
            return []
        }
    }

    // MARK: - WKNavigationDelegate

    public func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        webViewDidLoad = true
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
        view.backgroundColor = UIColor.systemGroupedBackground

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
        spinner.startAnimating()
        // Freeze at a fixed frame (animationsEnabled=false above stops the rotation animation)
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

    // MARK: - Type 2: WKWebView with HTML that mimics native controls

    private var webContentView: WKWebView?

    private func setupWebContent() {
        var rng = SeededRNG(seed: seed)

        // Seed-derived accent color for the HTML content
        let hue = CGFloat(rng.next() % 100) / 100.0
        let accentHex = uiColorToHex(UIColor(hue: hue, saturation: 0.7, brightness: 0.8, alpha: 1))
        let bgHex = runConfig.colorScheme == .dark ? "#1c1c1e" : "#f2f2f7"
        let textHex = runConfig.colorScheme == .dark ? "#ffffff" : "#000000"

        // HTML that visually mimics a native nav bar, text field, and button
        // but is rendered by the web engine — should be detected as webContent only.
        let html = """
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body { font-family: -apple-system, sans-serif; background: \(bgHex); color: \(textHex); }
          .navbar {
            background: \(bgHex); border-bottom: 0.5px solid rgba(128,128,128,0.3);
            padding: 12px 16px; font-size: 17px; font-weight: 600; text-align: center;
          }
          .content { padding: 24px 16px; }
          .field {
            width: 100%; border: 1px solid rgba(128,128,128,0.3);
            border-radius: 10px; padding: 11px 14px; font-size: 17px;
            background: \(runConfig.colorScheme == .dark ? "#2c2c2e" : "#ffffff");
            color: \(textHex); margin-bottom: 16px;
          }
          .btn {
            display: block; width: 100%; padding: 14px; border-radius: 12px;
            background: \(accentHex); color: #fff; font-size: 17px;
            font-weight: 600; text-align: center; border: none;
            margin-top: 8px;
          }
          .secondary-btn {
            display: block; width: 100%; padding: 14px; border-radius: 12px;
            background: rgba(128,128,128,0.15); color: \(accentHex); font-size: 17px;
            font-weight: 600; text-align: center; border: none; margin-top: 12px;
          }
          label { font-size: 13px; color: rgba(128,128,128,0.9); margin-bottom: 4px; display: block; }
        </style>
        </head>
        <body>
          <div class="navbar">Sign In</div>
          <div class="content">
            <label>Email</label>
            <input class="field" type="text" placeholder="email@example.com" value="">
            <label>Password</label>
            <input class="field" type="password" placeholder="Password" value="">
            <button class="btn">Continue</button>
            <button class="secondary-btn">Forgot Password?</button>
          </div>
        </body>
        </html>
        """

        let wv = WKWebView()
        wv.navigationDelegate = self
        wv.isUserInteractionEnabled = false
        wv.scrollView.isScrollEnabled = false
        wv.backgroundColor = UIColor(named: bgHex) ?? .systemBackground
        wv.loadHTMLString(html, baseURL: nil)

        view.addSubview(wv)
        webView = wv
        webContentView = wv
    }

    private func layoutWebContent() {
        webView?.frame = view.bounds
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

    // MARK: - Helpers

    private func uiColorToHex(_ color: UIColor) -> String {
        var r: CGFloat = 0, g: CGFloat = 0, b: CGFloat = 0
        color.getRed(&r, green: &g, blue: &b, alpha: nil)
        return String(format: "#%02X%02X%02X",
                      Int(r * 255), Int(g * 255), Int(b * 255))
    }
}

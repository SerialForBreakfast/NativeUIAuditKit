// UIKitToggleFormViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Hard-negative template for textField confusion.
//
// PURPOSE: The Run 004 FP zone analysis showed the model calls toggle "textField"
// in the upper-mid strip zone (y=0.15-0.35, 49% of FPs) and calls primaryButton
// "textField" in the bottom strip zone (y=0.75-1.00, 87% of FPs). This template
// provides hard-negative training images: a form-lookalike layout with UISwitch
// rows and a bottom CTA button — but ZERO textField elements.
//
// Annotated elements:
//   navigationBar    (chrome — auto-detected)
//   toggle_0..N-1   UISwitch — 4–10 switches across 2–3 grouped sections
//   primaryButton    "Save" / "Apply" / "Done" CTA at bottom
//
// NOT annotated (absent from this template):
//   textField, secondaryButton, tabBar, searchField — all absent
//
// Layout: programmatic insetGrouped-style (rounded containers, no UITableView).
// Sections placed in upper-mid and center zones. Button at bottom content area.
// This directly covers the two FP zones identified in zone analysis.
//
// Seed determinism: SeededRNG drives section/row count, toggle states, tint,
// content strings, and section header visibility. Same seed → byte-identical output.

import UIKit

// MARK: - UIKitToggleFormViewController

@MainActor
public final class UIKitToggleFormViewController: UIViewController, UIKitAnnotatable {

    // MARK: - Configuration

    private let seed: UInt64
    private let runConfig: GeneratorRunConfig

    // MARK: - Views

    private let navBar = UINavigationBar()
    private var sectionContainers: [[UIView]] = []   // [section][row] — the rounded row views
    private var toggleViews: [UISwitch] = []
    private var rowLabels: [UILabel] = []
    private var separatorViews: [UIView?] = []        // parallel to rowLabels; nil for last row in section
    private var sectionHeaderLabels: [UILabel] = []
    private var ctaButton = UIButton(type: .custom)

    // Layout metadata
    private var sectionRowCounts: [Int] = []
    private var tintColor: UIColor = .systemBlue

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
        view.backgroundColor = .systemGroupedBackground
        setupViews()
    }

    public override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        layoutViews()
    }

    // MARK: - UIKitAnnotatable

    public var annotatedViews: [UIKitAnnotatedView] {
        var result: [UIKitAnnotatedView] = []
        for (i, sw) in toggleViews.enumerated() {
            result.append(UIKitAnnotatedView(
                id: "toggle_\(i)",
                elementType: "toggle",
                view: sw
            ))
        }
        result.append(UIKitAnnotatedView(
            id: "ctaButton",
            elementType: "primaryButton",
            view: ctaButton,
            visibleText: ctaButton.title(for: .normal)
        ))
        return result
    }

    // MARK: - Setup

    // Section header labels used across seeds (seeded pick)
    private static let sectionHeaders: [String] = [
        "PRIVACY", "NOTIFICATIONS", "GENERAL", "DISPLAY & BRIGHTNESS", "ACCESSIBILITY",
        "SECURITY", "ACCOUNT", "SOUND & HAPTICS", "FOCUS", "BATTERY",
        "STORAGE", "CONNECTED DEVICES", "LANGUAGE & REGION", "KEYBOARD", "ADVANCED",
        "LOCATION SERVICES", "PERMISSIONS", "MEDIA", "SHARING", "DEVELOPER",
    ]

    // Toggle row labels that look like real settings (no textField implied)
    private static let toggleLabels: [String] = [
        "Allow Notifications", "Show in Notification Center", "Sounds", "Badges",
        "Show Previews", "Time Sensitive Notifications", "Scheduled Summary",
        "Dark Mode", "True Tone", "Night Shift", "Auto-Brightness",
        "Reduce Motion", "Reduce Transparency", "Bold Text", "Button Shapes",
        "On/Off Labels", "Increase Contrast", "Smart Invert", "Differentiate Without Color",
        "Location Access", "Precise Location", "Background App Refresh", "Cellular Data",
        "Wi-Fi Calling", "Allow Roaming", "Low Data Mode", "Private Wi-Fi Address",
        "Two-Factor Authentication", "App Lock", "Face ID", "Require Passcode",
        "iCloud Backup", "iCloud Drive", "iCloud Photos", "Find My iPhone",
        "Health Access", "Fitness Tracking", "Motion & Fitness", "Sleep Tracking",
        "Airplane Mode", "Personal Hotspot", "Bluetooth", "AirDrop",
        "Do Not Disturb", "Driving Focus", "Work Focus", "Personal Focus",
        "Auto-Lock", "Raise to Wake", "Tap to Wake", "Always-On Display",
        "Haptic Feedback", "System Sounds", "Lock Sound", "Keyboard Clicks",
        "Analytics & Improvements", "Share with Apple", "Advertising",
        "In-App Purchases", "Ask to Buy", "Screen Time", "Communication Limits",
    ]

    private func setupViews() {
        var rng = SeededRNG(seed: seed)
        var corpus = ContentCorpus(seed: seed)

        // Tint from 8 hue families (same palette as other templates)
        let hueIndex = Int(rng.next() % 8)
        let hues: [CGFloat] = [0.0, 0.06, 0.13, 0.33, 0.55, 0.60, 0.75, 0.90]
        tintColor = UIColor(hue: hues[hueIndex], saturation: 0.85, brightness: 0.90, alpha: 1)
        view.tintColor = tintColor

        // Navigation bar
        let navItem = UINavigationItem(title: corpus.navigationTitle())
        // Vary: sometimes show an Edit/Back button
        if rng.next() % 3 != 0 {
            let rightItem = UIBarButtonItem(
                title: rng.next() % 2 == 0 ? "Edit" : "Reset",
                style: .plain,
                target: nil,
                action: nil
            )
            navItem.rightBarButtonItem = rightItem
        }
        navBar.items = [navItem]
        view.addSubview(navBar)

        // Pick a shuffled subset of toggle labels for this seed
        let labelPool = UIKitToggleFormViewController.toggleLabels
        let headerPool = UIKitToggleFormViewController.sectionHeaders

        // Section and row counts (seed-varied): 2–3 sections, 2–4 rows each
        let sectionCount = 2 + Int(rng.next() % 2)   // 2 or 3
        var labelOffset = Int(rng.next() % UInt64(max(1, labelPool.count - 20)))
        var headerOffset = Int(rng.next() % UInt64(max(1, headerPool.count - 5)))

        for _ in 0..<sectionCount {
            let rowCount = 2 + Int(rng.next() % 3)   // 2, 3, or 4 rows
            sectionRowCounts.append(rowCount)

            // Section header label (always present — provides upper-mid zone context)
            let header = UILabel()
            header.text = headerPool[headerOffset % headerPool.count].uppercased()
            headerOffset += 1
            header.font = .systemFont(ofSize: 13, weight: .regular)
            header.textColor = .secondaryLabel
            view.addSubview(header)
            sectionHeaderLabels.append(header)

            // Rows within this section
            var rowsInSection: [UIView] = []
            for r in 0..<rowCount {
                let rowView = UIView()
                rowView.backgroundColor = .secondarySystemGroupedBackground
                view.addSubview(rowView)

                // Row title label — pick from toggle labels corpus
                let label = UILabel()
                label.text = labelPool[labelOffset % labelPool.count]
                labelOffset += 1
                label.font = .systemFont(ofSize: 17, weight: .regular)
                label.textColor = .label
                label.numberOfLines = 1
                rowView.addSubview(label)
                rowLabels.append(label)

                // Row separator (all rows except last in section) — store reference for layout
                if r < rowCount - 1 {
                    let sep = UIView()
                    sep.backgroundColor = .separator
                    rowView.addSubview(sep)
                    separatorViews.append(sep)
                } else {
                    separatorViews.append(nil)
                }

                // UISwitch — state varied by seed
                let sw = UISwitch()
                let stateRoll = rng.next() % 4
                switch stateRoll {
                case 0:   sw.isOn = false                       // off — normal
                case 1:   sw.isOn = true                        // on — normal
                case 2:   sw.isOn = false; sw.isEnabled = false  // disabled off
                default:  sw.isOn = true;  sw.isEnabled = false  // disabled on
                }
                // Vary on-tint: 60% system green, 40% tinted
                if rng.next() % 5 < 2 {
                    sw.onTintColor = tintColor
                }
                rowView.addSubview(sw)
                toggleViews.append(sw)

                rowsInSection.append(rowView)
            }
            sectionContainers.append(rowsInSection)
        }

        // CTA button at bottom — visually a primary tinted button (legacy API for consistency)
        // This specifically covers the bottom zone (y=0.75-1.00) primaryButton → textField FP
        let ctaTitles = ["Save Changes", "Apply", "Done", "Save Settings", "Confirm"]
        let ctaTitle = ctaTitles[Int(rng.next() % UInt64(ctaTitles.count))]
        ctaButton.setTitle(ctaTitle, for: .normal)
        ctaButton.titleLabel?.font = .systemFont(ofSize: 17, weight: .semibold)
        ctaButton.setTitleColor(.white, for: .normal)
        ctaButton.backgroundColor = tintColor
        ctaButton.layer.cornerRadius = 14
        ctaButton.layer.masksToBounds = true
        view.addSubview(ctaButton)
    }

    // MARK: - Layout

    private func layoutViews() {
        let safeTop = runConfig.osProfile.safeAreaTopInset
        let width = view.bounds.width
        let height = view.bounds.height

        // Navigation bar
        navBar.frame = CGRect(x: 0, y: 0, width: width, height: safeTop + 44)

        // Layout constants
        let sectionHPad: CGFloat  = 16   // insetGrouped horizontal inset
        let sectionWidth: CGFloat = width - sectionHPad * 2
        let rowHeight: CGFloat    = 52
        let sectionHeaderH: CGFloat = 28
        let sectionSpacing: CGFloat = 8  // between sections
        let headerToSection: CGFloat = 4

        // CTA button — fixed at bottom, 16pt insets, 52pt tall
        let ctaH: CGFloat = 52
        let ctaBottomPad: CGFloat = 32
        let safeBottom = runConfig.osProfile.safeAreaBottomInset
        let ctaY = height - safeBottom - ctaBottomPad - ctaH
        ctaButton.frame = CGRect(x: sectionHPad, y: ctaY, width: sectionWidth, height: ctaH)

        // Sections fill from navBar.maxY downward, stopping before ctaButton with spacing
        var currentY = navBar.frame.maxY + 16

        for (s, rowViews) in sectionContainers.enumerated() {
            guard s < sectionHeaderLabels.count else { continue }

            // Section header
            let header = sectionHeaderLabels[s]
            header.frame = CGRect(x: sectionHPad + 8, y: currentY,
                                  width: sectionWidth - 8, height: sectionHeaderH)
            currentY += sectionHeaderH + headerToSection

            // Rows within section — rounded container uses UIView with clipped subviews
            let sectionH = CGFloat(rowViews.count) * rowHeight
            for (r, rowView) in rowViews.enumerated() {
                let rowY = currentY + CGFloat(r) * rowHeight

                // Apply corner radius only to first and last rows
                let isFirst = r == 0
                let isLast = r == rowViews.count - 1
                rowView.frame = CGRect(x: sectionHPad, y: rowY, width: sectionWidth, height: rowHeight)
                rowView.layer.masksToBounds = true

                if rowViews.count == 1 {
                    rowView.layer.cornerRadius = 12
                    rowView.layer.maskedCorners = .all
                } else if isFirst {
                    rowView.layer.cornerRadius = 12
                    rowView.layer.maskedCorners = [.layerMinXMinYCorner, .layerMaxXMinYCorner]
                } else if isLast {
                    rowView.layer.cornerRadius = 12
                    rowView.layer.maskedCorners = [.layerMinXMaxYCorner, .layerMaxXMaxYCorner]
                } else {
                    rowView.layer.cornerRadius = 0
                    rowView.layer.maskedCorners = []
                }

                // Title label — left inset, vertically centred
                let labelInset: CGFloat = 20
                let switchWidth: CGFloat = 51
                let switchRightPad: CGFloat = 16
                let labelWidth = sectionWidth - labelInset - switchWidth - switchRightPad - 8
                if let label = rowLabels[safe: globalRowIndex(section: s, row: r)] {
                    label.frame = CGRect(
                        x: labelInset, y: (rowHeight - 22) / 2,
                        width: labelWidth, height: 22
                    )
                }

                // UISwitch — flush right, vertically centred
                let switchH: CGFloat = 31
                let switchX = sectionWidth - switchWidth - switchRightPad
                if let sw = toggleViews[safe: globalRowIndex(section: s, row: r)] {
                    sw.frame = CGRect(
                        x: switchX, y: (rowHeight - switchH) / 2,
                        width: switchWidth, height: switchH
                    )
                }

                // Separator — left-inset, 0.5pt at bottom of row
                let flatIdx = globalRowIndex(section: s, row: r)
                if let sep = separatorViews[safe: flatIdx] {
                    sep?.frame = CGRect(x: labelInset, y: rowHeight - 0.5,
                                        width: sectionWidth - labelInset, height: 0.5)
                }
            }

            currentY += sectionH + sectionSpacing
        }

        // If content overflows into CTA territory, nudge CTA down (shouldn't happen with ≤3 sections)
        if currentY > ctaY - 16 {
            ctaButton.frame.origin.y = currentY + 16
        }
    }

    // MARK: - Helpers

    /// Convert section+row to a flat index into toggleViews / rowLabels.
    private func globalRowIndex(section: Int, row: Int) -> Int {
        var offset = 0
        for s in 0..<section {
            offset += sectionRowCounts[safe: s] ?? 0
        }
        return offset + row
    }
}

// MARK: - Safe subscript

private extension Array {
    subscript(safe index: Int) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}

// MARK: - CACornerMask convenience

private extension CACornerMask {
    static let all: CACornerMask = [
        .layerMinXMinYCorner, .layerMaxXMinYCorner,
        .layerMinXMaxYCorner, .layerMaxXMaxYCorner
    ]
}

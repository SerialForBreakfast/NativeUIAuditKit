// UIKitListViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// UIKit template: settings-style list with tab bar.
//
// Annotated elements:
//   navigationBar    (chrome — auto-detected)
//   tabBar           (chrome — auto-detected, 4 items → tabBarItem_0..3)
//   listRow_0..4     listRow — UIView rows with title label + optional subtitle
//   toggle_0         toggle  — UISwitch in row 1 (Notifications)
//   toggle_1         toggle  — UISwitch in row 3 (Do Not Disturb)
//
// Layout: programmatic; rows begin at navBar.maxY, end at tabBar.minY.
// Tab bar items are set so detectChromeFrames produces 4 tabBarItem annotations.
//
// Anti-overfitting requirement (Phase 4): all frames are computed via UIKit layout
// (not SwiftUI GeometryReader), so the model learns UIKit visual language too.

import UIKit

// MARK: - UIKitListViewController

@MainActor
public final class UIKitListViewController: UIViewController, UIKitAnnotatable {

    // MARK: - Configuration

    private let seed: UInt64
    private let runConfig: GeneratorRunConfig

    // MARK: - Views

    private let navBar = UINavigationBar()
    private let tabBarView = UITabBar()

    /// Row container views (non-toggle rows).
    private var rowViews: [UIView] = []
    private var rowLabels: [UILabel] = []
    private var rowSubtitleLabels: [UILabel] = []

    /// Toggle views in specific rows.
    private var toggleViews: [UISwitch] = []

    /// Search / filter text field at the top of the list — annotated as textField.
    private let searchField = UITextField()

    /// "See All" footer button — annotated as secondaryButton.
    private let seeAllButton = UIButton(type: .system)

    private let rowCount = 5
    private let toggleRowIndices = [1, 3] // rows that carry a UISwitch

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
        setupAppearance()
        setupViews()
    }

    public override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        layoutViews()
    }

    // MARK: - UIKitAnnotatable

    public var annotatedViews: [UIKitAnnotatedView] {
        var result: [UIKitAnnotatedView] = []
        result.append(UIKitAnnotatedView(
            id: "searchField",
            elementType: "textField",
            view: searchField,
            visibleText: searchField.placeholder
        ))
        for (i, row) in rowViews.enumerated() {
            result.append(UIKitAnnotatedView(
                id: "listRow_\(i)",
                elementType: "listRow",
                view: row,
                visibleText: rowLabels[safe: i]?.text
            ))
        }
        for (i, toggle) in toggleViews.enumerated() {
            result.append(UIKitAnnotatedView(
                id: "toggle_\(i)",
                elementType: "toggle",
                view: toggle
            ))
        }
        result.append(UIKitAnnotatedView(
            id: "seeAllButton",
            elementType: "secondaryButton",
            view: seeAllButton,
            visibleText: seeAllButton.title(for: .normal)
        ))
        return result
    }

    // MARK: - Setup

    private func setupAppearance() {
        overrideUserInterfaceStyle = runConfig.colorScheme == .dark ? .dark : .light
        view.backgroundColor = .systemGroupedBackground
    }

    private func setupViews() {
        var corpus = ContentCorpus(seed: seed)

        // Navigation bar
        let navItem = UINavigationItem(title: corpus.navigationTitle())
        navBar.items = [navItem]
        view.addSubview(navBar)

        // Tab bar — 4 items so detectChromeFrames yields tabBarItem_0..3
        let tabItems: [UITabBarItem] = [
            UITabBarItem(title: "Home",     image: UIImage(systemName: "house"),             tag: 0),
            UITabBarItem(title: "Search",   image: UIImage(systemName: "magnifyingglass"),   tag: 1),
            UITabBarItem(title: "Library",  image: UIImage(systemName: "books.vertical"),    tag: 2),
            UITabBarItem(title: "Profile",  image: UIImage(systemName: "person.circle"),     tag: 3),
        ]
        tabBarView.items = tabItems
        tabBarView.selectedItem = tabItems[0]
        view.addSubview(tabBarView)

        // Row labels & separators
        let rowTitles: [String] = [
            corpus.listRowTitle(),
            "Notifications",
            corpus.listRowTitle(),
            "Do Not Disturb",
            corpus.listRowTitle(),
        ]
        let showSubtitle = [false, false, true, false, true]

        for i in 0..<rowCount {
            let rowView = UIView()
            rowView.backgroundColor = .secondarySystemGroupedBackground
            view.addSubview(rowView)
            rowViews.append(rowView)

            let titleLabel = UILabel()
            titleLabel.text = rowTitles[i]
            titleLabel.font = .systemFont(ofSize: 17)
            titleLabel.textColor = .label
            rowView.addSubview(titleLabel)
            rowLabels.append(titleLabel)

            let subtitleLabel = UILabel()
            if showSubtitle[i] {
                subtitleLabel.text = corpus.listRowSubtitle()
                subtitleLabel.font = .systemFont(ofSize: 13)
                subtitleLabel.textColor = .secondaryLabel
            }
            rowView.addSubview(subtitleLabel)
            rowSubtitleLabels.append(subtitleLabel)

            // Add a separator line at the bottom of each row (except last)
            if i < rowCount - 1 {
                let sep = UIView()
                sep.backgroundColor = .separator
                rowView.addSubview(sep)
            }
        }

        // Search / filter text field at top of list
        let placeholders = ["Search", "Filter", "Find setting", "Search settings"]
        searchField.placeholder = placeholders[Int(seed % UInt64(placeholders.count))]
        searchField.borderStyle = .roundedRect
        searchField.font = .systemFont(ofSize: 17)
        searchField.backgroundColor = .tertiarySystemGroupedBackground
        view.addSubview(searchField)

        // "See All" footer secondary button — label varies by seed for diversity
        let footerLabels = ["See All", "Show More", "View History", "Manage"]
        let footerLabel = footerLabels[Int(seed % UInt64(footerLabels.count))]
        seeAllButton.setTitle(footerLabel, for: .normal)
        seeAllButton.titleLabel?.font = .systemFont(ofSize: 17)
        seeAllButton.setTitleColor(.systemBlue, for: .normal)
        view.addSubview(seeAllButton)

        // Toggles in designated rows
        let toggleOn = seed % 2 == 0
        for _ in toggleRowIndices {
            let sw = UISwitch()
            sw.isOn = toggleOn
            view.addSubview(sw)
            toggleViews.append(sw)
        }
    }

    private func layoutViews() {
        let safeTop = runConfig.osProfile.safeAreaTopInset
        let safeBottom = runConfig.osProfile.safeAreaBottomInset
        let width = view.bounds.width
        let height = view.bounds.height

        // Navigation bar
        navBar.frame = CGRect(x: 0, y: 0, width: width, height: safeTop + 44)

        // Tab bar — standard 49pt visual height + home indicator safe area
        let tabBarVisualHeight: CGFloat = 49
        tabBarView.frame = CGRect(
            x: 0,
            y: height - safeBottom - tabBarVisualHeight,
            width: width,
            height: tabBarVisualHeight + safeBottom
        )

        // Search field — below nav bar, above the rows
        let searchFieldH: CGFloat = 36
        let searchFieldY = navBar.frame.maxY + 8
        searchField.frame = CGRect(x: 16, y: searchFieldY, width: width - 32, height: searchFieldH)

        // Row layout: fill space between search field and tab bar
        let contentTop = searchField.frame.maxY + 8
        let contentBottom = tabBarView.frame.minY - 8
        let totalHeight = max(0, contentBottom - contentTop)
        let rowHeight: CGFloat = min(56, totalHeight / CGFloat(rowCount))
        let hPad: CGFloat = 0 // edge-to-edge rows in settings style

        for (i, rowView) in rowViews.enumerated() {
            let y = contentTop + CGFloat(i) * rowHeight
            rowView.frame = CGRect(x: hPad, y: y, width: width - hPad, height: rowHeight)

            // Title label inset
            let labelInset: CGFloat = 20
            let labelHeight: CGFloat = 22
            let hasSubtitle = !(rowSubtitleLabels[safe: i]?.text?.isEmpty ?? true)
            let labelY: CGFloat = hasSubtitle
                ? (rowHeight - labelHeight - 14) / 2
                : (rowHeight - labelHeight) / 2
            rowLabels[safe: i]?.frame = CGRect(
                x: labelInset, y: labelY,
                width: width - labelInset * 2 - 80, height: labelHeight
            )
            rowSubtitleLabels[safe: i]?.frame = CGRect(
                x: labelInset, y: labelY + labelHeight + 2,
                width: width - labelInset * 2 - 80, height: 16
            )

            // Bottom separator
            if let sep = rowView.subviews.last, sep.backgroundColor == .separator {
                sep.frame = CGRect(x: labelInset, y: rowHeight - 0.5, width: width - labelInset, height: 0.5)
            }
        }

        // "See All" footer button — centred below the last row
        let footerButtonH: CGFloat = 44
        let footerY = (rowViews.last?.frame.maxY ?? contentTop) + 12
        seeAllButton.frame = CGRect(x: 0, y: footerY, width: width, height: footerButtonH)

        // Toggles — positioned in their rows, flush right
        let switchWidth: CGFloat = 51
        let switchHeight: CGFloat = 31
        let switchRightPad: CGFloat = 20
        for (j, sw) in toggleViews.enumerated() {
            let rowIndex = toggleRowIndices[j]
            guard rowIndex < rowViews.count else { continue }
            let row = rowViews[rowIndex]
            let switchX = row.frame.minX + row.frame.width - switchWidth - switchRightPad
            let switchY = row.frame.minY + (row.frame.height - switchHeight) / 2
            sw.frame = CGRect(x: switchX, y: switchY, width: switchWidth, height: switchHeight)
        }
    }
}

// MARK: - Safe subscript helper

private extension Array {
    subscript(safe index: Int) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}

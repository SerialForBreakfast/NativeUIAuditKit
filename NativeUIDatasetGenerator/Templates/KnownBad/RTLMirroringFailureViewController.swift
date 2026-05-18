// RTLMirroringFailureViewController.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// TASK-5a-6: Known-bad template — RTL mirroring failure mode.
//
// Renders a layout with `layoutDirection: .rightToLeft` but contains elements
// that are intentionally LTR-pinned — they do not flip as expected in an RTL
// layout. This demonstrates the "RTL mirroring failure" failure mode.
//
// Failure patterns used:
//   Row 0: Back chevron icon pinned to left edge (should be right in RTL)
//   Row 1: Progress bar that fills left-to-right (should fill right-to-left in RTL)
//   Row 2: UILabel with hardcoded `.left` alignment (should be `.right` in RTL)
//   Row 3: Leading-aligned image + text group (image should trail in RTL)
//   Row 4: Checkmark pinned to right edge (should be left edge in RTL)
//   Row 5: Slider with fixed left anchor (should anchor right in RTL)
//
// Annotated elements: each mis-mirrored element annotated with its semantic
//   type and `knownIssues: ["rtlMirroringFailure"]`.
//
// The `GeneratorRunConfig.layoutDirection` is `.rtl` for this template family.
// The annotation metadata records `image.layoutDirection: "rtl"`.
//
// Seed determinism: text content, background colors derived from seed.

import UIKit

// MARK: - RTLMirroringFailureViewController

@MainActor
public final class RTLMirroringFailureViewController: UIViewController, UIKitAnnotatable {

    // MARK: - Types

    private enum FailurePattern {
        case backChevronLTR          // annotated as navigationBar-item (use primaryButton)
        case progressBarLTR          // annotated as progressView
        case leftAlignedLabel        // annotated as label
        case leadingImageGroup       // annotated as label (the text part of the group)
        case trailingCheckmarkLTR    // annotated as label (row with trailing-pinned checkmark)
        case sliderLeftAnchorLTR     // annotated as slider
    }

    private struct FailureRow {
        let pattern: FailurePattern
        let elementType: String
        let view: UIView      // the mis-mirrored element to annotate
        let containerView: UIView
    }

    // MARK: - State

    private let seed: UInt64
    private let runConfig: GeneratorRunConfig
    private var failureRows: [FailureRow] = []

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

        // Explicitly set RTL — the failure mode is that individual elements
        // do NOT respect this even though the root layout direction is RTL.
        view.semanticContentAttribute = .forceRightToLeft

        setupRows()
    }

    public override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        layoutRows()
    }

    // MARK: - UIKitAnnotatable

    public var annotatedViews: [UIKitAnnotatedView] {
        failureRows.enumerated().map { i, row in
            UIKitAnnotatedView(
                id: "\(row.elementType)_rtlFail_\(i)",
                elementType: row.elementType,
                view: row.view,
                knownIssues: ["rtlMirroringFailure"]
            )
        }
    }

    // MARK: - Setup

    private func setupRows() {
        var corpus = ContentCorpus(seed: seed)

        // Row 0: Back chevron pinned to LEFT (wrong in RTL — should be RIGHT)
        let row0Container = makeContainer()
        let backButton = UIButton(type: .system)
        backButton.setImage(UIImage(systemName: "chevron.left"), for: .normal)
        backButton.tintColor = .systemBlue
        // Intentionally NOT flipping for RTL — LTR-pinned
        backButton.semanticContentAttribute = .forceLeftToRight
        row0Container.addSubview(backButton)
        failureRows.append(FailureRow(pattern: .backChevronLTR,
                                      elementType: "primaryButton",
                                      view: backButton,
                                      containerView: row0Container))

        // Row 1: UIProgressView filling left→right (wrong in RTL)
        let row1Container = makeContainer()
        let progressView = UIProgressView(progressViewStyle: .default)
        progressView.progress = 0.6
        progressView.semanticContentAttribute = .forceLeftToRight   // LTR-pinned
        row1Container.addSubview(progressView)
        failureRows.append(FailureRow(pattern: .progressBarLTR,
                                      elementType: "progressView",
                                      view: progressView,
                                      containerView: row1Container))

        // Row 2: UILabel with hardcoded .left alignment (wrong in RTL)
        let row2Container = makeContainer()
        let leftLabel = UILabel()
        leftLabel.text = corpus.personName() + " " + corpus.placeName()
        leftLabel.textAlignment = .left     // should be .right or .natural in RTL
        leftLabel.font = .systemFont(ofSize: 17)
        leftLabel.textColor = .label
        row2Container.addSubview(leftLabel)
        failureRows.append(FailureRow(pattern: .leftAlignedLabel,
                                      elementType: "label",
                                      view: leftLabel,
                                      containerView: row2Container))

        // Row 3: Leading-image group — image on LEFT (wrong in RTL — should trail)
        let row3Container = makeContainer()
        let groupLabel = UILabel()
        groupLabel.text = corpus.companyName()
        groupLabel.font = .systemFont(ofSize: 15)
        groupLabel.textColor = .label
        // The leading image is separate — we annotate the label as the key element
        let groupImage = UIImageView(image: UIImage(systemName: "person.circle"))
        groupImage.tintColor = .systemBlue
        groupImage.semanticContentAttribute = .forceLeftToRight
        row3Container.addSubview(groupImage)
        row3Container.addSubview(groupLabel)
        failureRows.append(FailureRow(pattern: .leadingImageGroup,
                                      elementType: "label",
                                      view: groupLabel,
                                      containerView: row3Container))

        // Row 4: Checkmark pinned to RIGHT edge with fixed frame (wrong in RTL — should be LEFT)
        let row4Container = makeContainer()
        let checkLabel = UILabel()
        checkLabel.text = corpus.shortSentence()
        checkLabel.font = .systemFont(ofSize: 16)
        checkLabel.textColor = .label
        checkLabel.textAlignment = .left    // still left-aligned in RTL context
        row4Container.addSubview(checkLabel)
        let checkmark = UIImageView(image: UIImage(systemName: "checkmark"))
        checkmark.tintColor = .systemGreen
        checkmark.semanticContentAttribute = .forceLeftToRight
        row4Container.addSubview(checkmark)
        failureRows.append(FailureRow(pattern: .trailingCheckmarkLTR,
                                      elementType: "label",
                                      view: checkLabel,
                                      containerView: row4Container))

        // Row 5: UISlider with LTR fill direction (wrong in RTL)
        let row5Container = makeContainer()
        let slider = UISlider()
        slider.value = 0.35
        slider.minimumValue = 0
        slider.maximumValue = 1
        slider.semanticContentAttribute = .forceLeftToRight   // LTR-pinned
        row5Container.addSubview(slider)
        failureRows.append(FailureRow(pattern: .sliderLeftAnchorLTR,
                                      elementType: "slider",
                                      view: slider,
                                      containerView: row5Container))
    }

    private func makeContainer() -> UIView {
        let v = UIView()
        v.backgroundColor = .systemGray6
        v.layer.cornerRadius = 8
        v.clipsToBounds = true
        view.addSubview(v)
        return v
    }

    // MARK: - Layout

    private func layoutRows() {
        let safeTop = runConfig.osProfile.safeAreaTopInset
        let screenW = view.bounds.width
        let containerW = screenW - 32
        let containerX: CGFloat = 16
        let containerH: CGFloat = 52
        let vGap: CGFloat = 16
        let inset: CGFloat = 12

        var y = safeTop + 24

        for row in failureRows {
            row.containerView.frame = CGRect(
                x: containerX, y: y,
                width: containerW, height: containerH
            )

            // Layout the mis-mirrored element inside the container
            switch row.pattern {
            case .backChevronLTR:
                // Back button pinned to LEFT (wrong in RTL)
                row.view.frame = CGRect(x: inset, y: (containerH - 32) / 2, width: 32, height: 32)

            case .progressBarLTR:
                // Progress bar fills full width, LTR
                row.view.frame = CGRect(
                    x: inset, y: (containerH - 4) / 2,
                    width: containerW - 2 * inset, height: 4
                )

            case .leftAlignedLabel:
                // Label aligned left (wrong in RTL)
                row.view.frame = CGRect(
                    x: inset, y: (containerH - 22) / 2,
                    width: containerW - 2 * inset, height: 22
                )

            case .leadingImageGroup:
                // Image pinned left, label to its right (wrong in RTL)
                let imgV = row.containerView.subviews.first(where: { $0 is UIImageView })
                let imgSize: CGFloat = 28
                imgV?.frame = CGRect(x: inset, y: (containerH - imgSize) / 2,
                                     width: imgSize, height: imgSize)
                row.view.frame = CGRect(
                    x: inset + imgSize + 8, y: (containerH - 22) / 2,
                    width: containerW - inset - imgSize - 8 - inset, height: 22
                )

            case .trailingCheckmarkLTR:
                // Label left-aligned, checkmark pinned to right (wrong in RTL)
                let chkSize: CGFloat = 20
                let chkView = row.containerView.subviews.first(where: { $0 is UIImageView })
                chkView?.frame = CGRect(
                    x: containerW - inset - chkSize, y: (containerH - chkSize) / 2,
                    width: chkSize, height: chkSize
                )
                row.view.frame = CGRect(
                    x: inset, y: (containerH - 22) / 2,
                    width: containerW - 2 * inset - chkSize - 8, height: 22
                )

            case .sliderLeftAnchorLTR:
                // Slider fills width, LTR (wrong in RTL)
                row.view.frame = CGRect(
                    x: inset, y: (containerH - 31) / 2,
                    width: containerW - 2 * inset, height: 31
                )
            }

            y += containerH + vGap
        }
    }
}

// MARK: - ContentCorpus extension

private extension ContentCorpus {
    mutating func shortSentence() -> String {
        "\(personName()) from \(placeName())"
    }
}

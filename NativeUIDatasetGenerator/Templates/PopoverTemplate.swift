// PopoverTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI popover template (TASK-5b-11).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   popover         — the popover card (manual captureFrame on the card container)
//   label           — text items inside the popover
//   secondaryButton — action buttons inside the popover
//
// Popover is rendered manually (not via .popover(isPresented:)) so that
// captureFrame can attach to the precise card boundary. The system .popover
// renders in a separate UIPopoverPresentationController window inaccessible
// to GeometryReader preference keys.
//
// On iPhone, popovers present as sheets; this template renders the popover
// at a fixed mid-screen position to simulate that interaction state.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - PopoverConfig

/// Parameterised inputs for a single Popover rendering.
public struct PopoverConfig: Sendable {
    /// Popover title.
    public var title: String
    /// Action item labels inside the popover (2–4 items).
    public var actionItems: [String]
    /// Popover anchor position: top (near nav bar), mid, bottom (near tab bar).
    public var anchorPosition: PopoverAnchor
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        actionItems: [String],
        anchorPosition: PopoverAnchor,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.actionItems = actionItems
        self.anchorPosition = anchorPosition
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> PopoverConfig {
        var rng = SeededRNG(seed: seed)
        let dark        = rng.next() % 2 == 0
        let itemCount   = 2 + Int(rng.next() % 3)   // 2–4 items
        let anchorChoice = rng.next() % 3
        let anchor: PopoverAnchor
        switch anchorChoice {
        case 0:  anchor = .top
        case 1:  anchor = .mid
        default: anchor = .bottom
        }

        var items: [String] = []
        for _ in 0..<itemCount { items.append(corpus.buttonLabel()) }

        return PopoverConfig(
            title: corpus.navigationTitle(),
            actionItems: items,
            anchorPosition: anchor,
            colorScheme: dark ? .dark : .light
        )
    }
}

/// Where the popover is anchored on screen.
public enum PopoverAnchor: String, Sendable {
    case top, mid, bottom
}

// MARK: - PopoverTemplate

/// SwiftUI view rendering a simulated popover card over a content background.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct PopoverTemplate: View {
    public let config: PopoverConfig

    public init(config: PopoverConfig) {
        self.config = config
    }

    public var body: some View {
        GeometryReader { proxy in
            let popoverW: CGFloat = min(proxy.size.width - 64, 280)
            let popoverH: CGFloat = CGFloat(44 + config.actionItems.count * 44 + 16)

            let anchorX: CGFloat = proxy.size.width - popoverW - 16
            let anchorY: CGFloat = {
                switch config.anchorPosition {
                case .top:    return 80
                case .mid:    return proxy.size.height / 2 - popoverH / 2
                case .bottom: return proxy.size.height - popoverH - 120
                }
            }()

            ZStack(alignment: .topLeading) {
                // Background content (simulates the screen behind the popover)
                Color(UIColor.systemGroupedBackground)
                    .ignoresSafeArea()

                VStack(alignment: .leading, spacing: 0) {
                    // Title row
                    Text(config.title)
                        .font(.footnote.weight(.semibold))
                        .foregroundStyle(.secondary)
                        .captureFrame(id: "label_title")
                        .padding(.horizontal, 16)
                        .padding(.top, 12)
                        .padding(.bottom, 8)

                    Divider()

                    // Action buttons
                    ForEach(Array(config.actionItems.enumerated()), id: \.offset) { idx, item in
                        Button(item) {}
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .frame(height: 44)
                            .foregroundStyle(Color.accentColor)
                            .captureFrame(id: "secondaryButton_\(idx)")
                            .padding(.horizontal, 16)

                        if idx < config.actionItems.count - 1 {
                            Divider()
                                .padding(.leading, 16)
                        }
                    }

                    Spacer().frame(height: 8)
                }
                .frame(width: popoverW)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color(UIColor.systemBackground))
                        .shadow(color: .black.opacity(0.18), radius: 12, x: 0, y: 4)
                )
                .clipShape(RoundedRectangle(cornerRadius: 12))
                .captureFrame(id: "popover_0")
                .padding(.leading, anchorX)
                .padding(.top, anchorY)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}

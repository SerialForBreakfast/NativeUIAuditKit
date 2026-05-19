// SheetTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI sheet / half-sheet template (TASK-5b-2).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
// No platform guards needed — this file never compiles on macOS.
//
// Annotated elements:
//   sheet         — the presented sheet card (manual captureFrame on the ZStack background)
//   primaryButton — action button inside sheet
//   cancelAction  — dismiss / cancel button (top-right or bottom-row)
//   label         — title and subtitle text labels inside sheet
//
// Sheet height variants driven by `sheetHeight` field:
//   .full    — sheet covers ~90% of screen height
//   .half    — sheet covers ~50% of screen height
//   .third   — sheet covers ~35% of screen height
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All element offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout-spacing padding (BP-18)

import SwiftUI
import UIKit

// MARK: - SheetHeight

public enum SheetHeight: String, Sendable {
    case full   // ~90% screen
    case half   // ~50% screen
    case third  // ~35% screen

    var fraction: CGFloat {
        switch self {
        case .full:  return 0.90
        case .half:  return 0.50
        case .third: return 0.35
        }
    }
}

// MARK: - SheetConfig

/// Parameterised inputs for a single Sheet rendering.
public struct SheetConfig: Sendable {
    /// Sheet height variant.
    public var sheetHeight: SheetHeight
    /// Title displayed inside the sheet.
    public var title: String
    /// Subtitle / body text inside the sheet.
    public var subtitle: String
    /// Primary action button label.
    public var primaryLabel: String
    /// Cancel button label.
    public var cancelLabel: String
    /// When true, show a drag handle at the top of the sheet.
    public var showDragHandle: Bool
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        sheetHeight: SheetHeight,
        title: String,
        subtitle: String,
        primaryLabel: String,
        cancelLabel: String,
        showDragHandle: Bool,
        colorScheme: ColorScheme
    ) {
        self.sheetHeight = sheetHeight
        self.title = title
        self.subtitle = subtitle
        self.primaryLabel = primaryLabel
        self.cancelLabel = cancelLabel
        self.showDragHandle = showDragHandle
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> SheetConfig {
        var rng = SeededRNG(seed: seed)
        let heightChoice = rng.next() % 3
        let height: SheetHeight
        switch heightChoice {
        case 0:  height = .full
        case 1:  height = .half
        default: height = .third
        }
        let dark       = rng.next() % 2 == 0
        let dragHandle = rng.next() % 3 != 0   // ~67% show drag handle

        return SheetConfig(
            sheetHeight: height,
            title: corpus.navigationTitle(),
            subtitle: corpus.listRowTitle(),
            primaryLabel: corpus.buttonLabel(),
            cancelLabel: "Cancel",
            showDragHandle: dragHandle,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - SheetTemplate

/// SwiftUI view rendering a presented sheet over a dimmed background.
///
/// The sheet card is drawn manually (not via `.sheet(isPresented:)`) so that
/// `captureFrame(id: "sheet_0")` can be placed precisely on the card boundary.
/// `.sheet(isPresented:)` presents in a new window whose frame is inaccessible
/// to GeometryReader preference-key collection.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct SheetTemplate: View {
    public let config: SheetConfig

    public init(config: SheetConfig) {
        self.config = config
    }

    public var body: some View {
        GeometryReader { proxy in
            let screenH = proxy.size.height
            let sheetH  = screenH * config.sheetHeight.fraction

            ZStack(alignment: .bottom) {
                // Dimmed background
                Color.black.opacity(0.4)
                    .ignoresSafeArea()

                // Sheet card — annotated before the bottom-safe-area offset (BP-18)
                VStack(alignment: .leading, spacing: 0) {
                    // Drag handle
                    if config.showDragHandle {
                        HStack {
                            Spacer()
                            Capsule()
                                .fill(Color.secondary.opacity(0.5))
                                .frame(width: 36, height: 5)
                            Spacer()
                        }
                        .padding(.top, 8)
                        .padding(.bottom, 4)
                    }

                    // Cancel button row (top-right)
                    HStack {
                        Spacer()
                        Button(config.cancelLabel) {}
                            .foregroundStyle(Color.accentColor)
                            .captureFrame(id: "cancelAction_0")
                            .padding(.trailing, 20)
                            .padding(.top, config.showDragHandle ? 4 : 16)
                    }

                    // Title label
                    Text(config.title)
                        .font(.title2.bold())
                        .captureFrame(id: "label_title")
                        .padding(.horizontal, 20)
                        .padding(.top, 12)

                    // Subtitle label
                    Text(config.subtitle)
                        .font(.body)
                        .foregroundStyle(.secondary)
                        .captureFrame(id: "label_subtitle")
                        .padding(.horizontal, 20)
                        .padding(.top, 8)

                    Spacer()

                    // Primary button
                    Button(config.primaryLabel) {}
                        .frame(maxWidth: .infinity, minHeight: 50)
                        .background(Color.accentColor)
                        .foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                        .captureFrame(id: "primaryButton_0")
                        .padding(.horizontal, 20)
                        .padding(.bottom, 32)
                }
                .frame(width: proxy.size.width, height: sheetH)
                .background(Color(UIColor.systemBackground))
                .clipShape(
                    .rect(topLeadingRadius: 16, bottomLeadingRadius: 0,
                          bottomTrailingRadius: 0, topTrailingRadius: 16)
                )
                .captureFrame(id: "sheet_0")
            }
            .ignoresSafeArea()
            .colorScheme(config.colorScheme)
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}

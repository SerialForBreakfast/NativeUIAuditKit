// LoadingSkeletonTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI loading / skeleton state template (TASK-5b-6).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   activityIndicator — spinning progress indicator (navigationBar area or center)
//   progressView      — linear loading bar at the top of the content area
//   listRow           — each skeleton shimmer row (isSkeleton: true in metadata)
//
// The skeleton rows use a solid grey rounded-rectangle placeholder — no real text.
// AnnotatedElement.knownIssues is empty; isSkeleton state is carried in element state.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - LoadingSkeletonConfig

/// Parameterised inputs for a single LoadingSkeleton rendering.
public struct LoadingSkeletonConfig: Sendable {
    /// Number of skeleton list rows (3–7).
    public var rowCount: Int
    /// When true, show a linear progress bar below the nav bar.
    public var showProgressBar: Bool
    /// When true, show an activity indicator in the center of the screen.
    public var showCenterSpinner: Bool
    /// When true, show a nav bar (with activity indicator in the title area).
    public var showNavBar: Bool
    /// Navigation bar title.
    public var title: String
    /// Shimmer fill hue (0–1) — tint of the skeleton placeholder colour.
    public var shimmerHue: Double
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        rowCount: Int,
        showProgressBar: Bool,
        showCenterSpinner: Bool,
        showNavBar: Bool,
        title: String,
        shimmerHue: Double,
        colorScheme: ColorScheme
    ) {
        self.rowCount = rowCount
        self.showProgressBar = showProgressBar
        self.showCenterSpinner = showCenterSpinner
        self.showNavBar = showNavBar
        self.title = title
        self.shimmerHue = shimmerHue
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> LoadingSkeletonConfig {
        var rng = SeededRNG(seed: seed)
        let dark         = rng.next() % 2 == 0
        let rowCount     = 3 + Int(rng.next() % 5)   // 3–7 rows
        let showProgress = rng.next() % 2 == 0
        let showSpinner  = rng.next() % 3 != 0        // ~67%
        let showNav      = rng.next() % 3 != 0        // ~67%
        let shimmerHue   = Double(rng.next() % 1000) / 1000.0

        return LoadingSkeletonConfig(
            rowCount: rowCount,
            showProgressBar: showProgress,
            showCenterSpinner: showSpinner,
            showNavBar: showNav,
            title: corpus.navigationTitle(),
            shimmerHue: shimmerHue,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - LoadingSkeletonTemplate

/// SwiftUI view rendering a list screen in its loading / skeleton state.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct LoadingSkeletonTemplate: View {
    public let config: LoadingSkeletonConfig

    public init(config: LoadingSkeletonConfig) {
        self.config = config
    }

    private var shimmerColor: Color {
        // Desaturated placeholder colour — mimics skeleton shimmer in light/dark.
        config.colorScheme == .dark
            ? Color(white: 0.25)
            : Color(hue: config.shimmerHue, saturation: 0.05, brightness: 0.88)
    }

    @ViewBuilder
    private var content: some View {
        ZStack(alignment: .top) {
            Color(UIColor.systemGroupedBackground).ignoresSafeArea()

            VStack(spacing: 0) {
                // Linear progress bar
                if config.showProgressBar {
                    // ProgressView renders a UIProgressView inside the SwiftUI tree.
                    // We capture its frame via captureFrame immediately before layout padding.
                    ProgressView(value: 0.4)
                        .tint(Color.accentColor)
                        .captureFrame(id: "progressView_0")
                        .padding(.top, 0)
                }

                // Skeleton list rows
                VStack(spacing: 0) {
                    ForEach(0..<config.rowCount, id: \.self) { idx in
                        HStack(alignment: .center, spacing: 12) {
                            // Avatar placeholder
                            Circle()
                                .fill(shimmerColor)
                                .frame(width: 40, height: 40)

                            VStack(alignment: .leading, spacing: 6) {
                                // Title line — 60% width
                                RoundedRectangle(cornerRadius: 4)
                                    .fill(shimmerColor)
                                    .frame(height: 14)
                                    .frame(maxWidth: .infinity)
                                    .padding(.trailing, UIScreen.main.bounds.width * 0.35)

                                // Subtitle line — 40% width
                                RoundedRectangle(cornerRadius: 4)
                                    .fill(shimmerColor.opacity(0.7))
                                    .frame(height: 10)
                                    .frame(maxWidth: .infinity)
                                    .padding(.trailing, UIScreen.main.bounds.width * 0.55)
                            }
                        }
                        .padding(.horizontal, 16)
                        .padding(.vertical, 12)
                        .captureFrame(id: "listRow_skeleton_\(idx)")

                        Divider()
                            .padding(.leading, 68)
                    }
                }
                .background(Color(UIColor.systemBackground))
                .cornerRadius(12)
                .padding(.horizontal, 16)
                .padding(.top, 16)

                Spacer()
            }

            // Center activity indicator
            if config.showCenterSpinner {
                VStack {
                    Spacer()
                    ProgressView()
                        .scaleEffect(1.4)
                        .captureFrame(id: "activityIndicator_0")
                    Spacer()
                }
            }
        }
    }

    public var body: some View {
        if config.showNavBar {
            NavigationStack {
                content
                    .navigationTitle(config.title)
                    .navigationBarTitleDisplayMode(.inline)
                    .colorScheme(config.colorScheme)
            }
            .colorScheme(config.colorScheme)
        } else {
            content
                .colorScheme(config.colorScheme)
        }
    }
}

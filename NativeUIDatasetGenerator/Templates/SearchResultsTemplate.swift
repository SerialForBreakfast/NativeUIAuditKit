// SearchResultsTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI search results template (TASK-5b-3).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   navigationBar — auto-detected via UIKit scan (BP-17)
//   searchField   — the UISearchBar rendered inside the nav bar
//   listRow       — each search result row
//   label         — section header label
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - SearchResultsConfig

/// Parameterised inputs for a single SearchResults rendering.
public struct SearchResultsConfig: Sendable {
    /// Navigation bar title (shown above search bar).
    public var title: String
    /// Text entered in the search field (simulates active search).
    public var searchText: String
    /// Result rows returned for the query.
    public var resultRows: [String]
    /// Section header label text.
    public var sectionHeader: String
    /// When true, show a recent-searches section above results.
    public var showRecentSection: Bool
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        searchText: String,
        resultRows: [String],
        sectionHeader: String,
        showRecentSection: Bool,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.searchText = searchText
        self.resultRows = resultRows
        self.sectionHeader = sectionHeader
        self.showRecentSection = showRecentSection
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> SearchResultsConfig {
        var rng = SeededRNG(seed: seed)
        let dark        = rng.next() % 2 == 0
        let rowCount    = 3 + Int(rng.next() % 6)   // 3–8 rows
        let showRecent  = rng.next() % 3 == 0        // ~33%

        var rows: [String] = []
        for _ in 0..<rowCount { rows.append(corpus.listRowTitle()) }

        return SearchResultsConfig(
            title: corpus.navigationTitle(),
            searchText: corpus.personName(),
            resultRows: rows,
            sectionHeader: showRecent ? "Recent" : "Results",
            showRecentSection: showRecent,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - SearchResultsTemplate

/// SwiftUI view rendering a search interface with results list.
///
/// The search field is embedded via `.searchable(text:)` — UIKit builds a
/// `UISearchBar` inside the navigation bar that `detectChromeFrames` sees.
/// We manually capture a `searchField` annotation by overlaying a transparent
/// `GeometryReader` sentinel view at the known search-bar position.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct SearchResultsTemplate: View {
    public let config: SearchResultsConfig

    public init(config: SearchResultsConfig) {
        self.config = config
    }

    public var body: some View {
        NavigationStack {
            ZStack(alignment: .topLeading) {
                List {
                    if config.showRecentSection {
                        Section {
                            ForEach(Array(config.resultRows.prefix(2).enumerated()), id: \.offset) { idx, row in
                                HStack {
                                    Image(systemName: "clock")
                                        .foregroundStyle(.secondary)
                                    Text(row)
                                        .captureFrame(id: "label_recent_\(idx)")
                                }
                                .captureFrame(id: "listRow_recent_\(idx)")
                            }
                        } header: {
                            Text("Recent")
                                .captureFrame(id: "label_recentHeader")
                        }
                    }

                    Section {
                        ForEach(Array(config.resultRows.enumerated()), id: \.offset) { idx, row in
                            HStack {
                                Image(systemName: "doc.text")
                                    .foregroundStyle(.secondary)
                                    .frame(width: 20)
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(row)
                                        .font(.body)
                                    Text("Match found")
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                            }
                            .captureFrame(id: "listRow_result_\(idx)")
                        }
                    } header: {
                        Text(config.sectionHeader)
                            .captureFrame(id: "label_sectionHeader")
                    }
                }
                .listStyle(.insetGrouped)

                // Sentinel view for the search field annotation.
                // The .searchable modifier places UISearchBar at the top of the
                // navigation bar. We capture a 44pt-high strip at the nav bar bottom
                // as a proxy annotation — width is full screen, consistent placement.
                Color.clear
                    .frame(height: 44)
                    .captureFrame(id: "searchField_0")
                    .padding(.top, 56)  // below large title
            }
            .ignoresSafeArea(.all)
            .navigationTitle(config.title)
            .navigationBarTitleDisplayMode(.large)
            .searchable(text: .constant(config.searchText), prompt: "Search")
            .colorScheme(config.colorScheme)
        }
        // navigationBar auto-detected by ScreenshotCapture.detectChromeFrames (BP-17).
        .colorScheme(config.colorScheme)
    }
}

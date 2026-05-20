// SegmentedFilterTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI segmented control + filtered list template (TASK-5b-22).
// Covers SwiftUI Picker in .segmented style — distinct from UIKitControls segmented.
// Structural distinction: segmented control drives visible list content (filter UI pattern).
//
// Annotated elements:
//   segmentedControl — Picker(.segmented) with 2–4 segments
//   listRow          — filtered rows below the control
//   label            — row titles and subtitles
//   navigationBar    — auto-detected
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - SegmentedFilterConfig

public struct SegmentedFilterConfig: Sendable {
    public var title: String
    public var segments: [String]          // 2–4 segment labels
    public var selectedSegment: Int        // 0-based index
    /// Rows shown under the active segment (3–6 rows).
    public var rows: [(title: String, subtitle: String)]
    public var colorScheme: ColorScheme

    public init(
        title: String,
        segments: [String],
        selectedSegment: Int,
        rows: [(title: String, subtitle: String)],
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.segments = segments
        self.selectedSegment = selectedSegment
        self.rows = rows
        self.colorScheme = colorScheme
    }

    private static let segmentSets: [[String]] = [
        ["All", "Unread", "Flagged"],
        ["Today", "Week", "Month", "Year"],
        ["Active", "Inactive"],
        ["Photos", "Videos", "Files", "Links"],
        ["Inbox", "Sent", "Drafts"],
    ]

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> SegmentedFilterConfig {
        var rng = SeededRNG(seed: seed)
        let dark     = rng.next() % 2 == 0
        let sets     = segmentSets
        let setIdx   = Int(rng.next() % UInt64(sets.count))
        let segs     = sets[setIdx]
        let selected = Int(rng.next() % UInt64(segs.count))
        let rowCount = 3 + Int(rng.next() % 4)   // 3–6 rows

        var rows: [(title: String, subtitle: String)] = []
        for _ in 0..<rowCount {
            rows.append((title: corpus.listRowTitle(), subtitle: corpus.listRowSubtitle()))
        }

        return SegmentedFilterConfig(
            title: corpus.navigationTitle(),
            segments: segs,
            selectedSegment: selected,
            rows: rows,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - SegmentedFilterTemplate

public struct SegmentedFilterTemplate: View {
    public let config: SegmentedFilterConfig

    public init(config: SegmentedFilterConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemGroupedBackground).ignoresSafeArea()

            NavigationStack {
                VStack(spacing: 0) {
                    // Segmented control pinned below nav bar
                    Picker("", selection: .constant(config.selectedSegment)) {
                        ForEach(Array(config.segments.enumerated()), id: \.offset) { idx, seg in
                            Text(seg).tag(idx)
                        }
                    }
                    .pickerStyle(.segmented)
                    .captureFrame(id: "segmentedControl_0")
                    .padding(.horizontal, 16)
                    .padding(.vertical, 12)
                    .background(Color(UIColor.systemGroupedBackground))

                    // Filtered list content
                    List {
                        ForEach(Array(config.rows.enumerated()), id: \.offset) { idx, row in
                            VStack(alignment: .leading, spacing: 2) {
                                Text(row.title)
                                    .font(.body)
                                    .captureFrame(id: "label_row_title_\(idx)")
                                Text(row.subtitle)
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                                    .captureFrame(id: "label_row_subtitle_\(idx)")
                            }
                            .padding(.vertical, 4)
                            .captureFrame(id: "listRow_\(idx)")
                        }
                    }
                    .listStyle(.insetGrouped)
                }
                .navigationTitle(config.title)
                .navigationBarTitleDisplayMode(.inline)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}

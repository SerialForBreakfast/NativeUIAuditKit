// LinkRichTextTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI scrollable article template (TASK-5b-22, class: link).
// Covers SwiftUI Link / tappable URL text — not represented in any prior template.
//
// Annotated elements:
//   link         — tappable URL/reference links embedded in the text body
//   label        — article title, body paragraphs
//   imageView    — article hero image placeholder
//   navigationBar — auto-detected
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - LinkRichTextConfig

public struct LinkRichTextConfig: Sendable {
    public var title: String
    /// Article heading text.
    public var articleTitle: String
    /// Hero image hue (0–1).
    public var heroHue: Double
    /// Number of paragraph blocks (2–4).
    public var paragraphCount: Int
    /// Paragraph body texts.
    public var paragraphs: [String]
    /// Links shown (1–3 inline link labels + dummy URLs).
    public var links: [(label: String, displayURL: String)]
    public var colorScheme: ColorScheme

    public init(
        title: String,
        articleTitle: String,
        heroHue: Double,
        paragraphCount: Int,
        paragraphs: [String],
        links: [(label: String, displayURL: String)],
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.articleTitle = articleTitle
        self.heroHue = heroHue
        self.paragraphCount = paragraphCount
        self.paragraphs = paragraphs
        self.links = links
        self.colorScheme = colorScheme
    }

    private static let linkLabels = [
        "Learn more", "Read the guide", "Full documentation", "View source",
        "See also", "Related article", "Official reference", "Download"
    ]
    private static let domains = [
        "developer.apple.com", "swift.org", "docs.example.com",
        "support.apple.com", "github.com/example"
    ]
    private static let paragraphTexts = [
        "This section covers the fundamentals of the feature and how it integrates with existing workflows.",
        "Getting started requires only a few steps. The configuration options provide fine-grained control.",
        "Advanced users may want to customise the default behaviour by overriding the standard settings.",
        "Performance considerations are important when working at scale with large datasets.",
        "The framework automatically handles memory management in most common usage patterns.",
        "Refer to the source code for implementation details not covered in this overview.",
    ]

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> LinkRichTextConfig {
        var rng = SeededRNG(seed: seed)
        let dark       = rng.next() % 2 == 0
        let paraCount  = 2 + Int(rng.next() % 3)   // 2–4
        let linkCount  = 1 + Int(rng.next() % 3)   // 1–3
        let heroHue    = Double(rng.next() % 1000) / 1000.0

        var paras: [String] = []
        for _ in 0..<paraCount {
            paras.append(paragraphTexts[Int(rng.next() % UInt64(paragraphTexts.count))])
        }

        var links: [(label: String, displayURL: String)] = []
        for _ in 0..<linkCount {
            let label  = linkLabels[Int(rng.next() % UInt64(linkLabels.count))]
            let domain = domains[Int(rng.next() % UInt64(domains.count))]
            links.append((label: label, displayURL: domain))
        }

        return LinkRichTextConfig(
            title: corpus.navigationTitle(),
            articleTitle: corpus.listRowTitle(),
            heroHue: heroHue,
            paragraphCount: paraCount,
            paragraphs: paras,
            links: links,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - LinkRichTextTemplate

public struct LinkRichTextTemplate: View {
    public let config: LinkRichTextConfig

    public init(config: LinkRichTextConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemBackground).ignoresSafeArea()

            NavigationStack {
                ScrollView {
                    VStack(alignment: .leading, spacing: 0) {
                        // Hero image placeholder
                        Color(hue: config.heroHue, saturation: 0.35, brightness: 0.70)
                            .frame(maxWidth: .infinity)
                            .frame(height: 200)
                            .overlay(
                                Image(systemName: "photo")
                                    .font(.largeTitle)
                                    .foregroundStyle(.white.opacity(0.6))
                            )
                            .captureFrame(id: "imageView_hero")

                        VStack(alignment: .leading, spacing: 16) {
                            // Article title
                            Text(config.articleTitle)
                                .font(.title2.bold())
                                .captureFrame(id: "label_article_title")

                            // Body paragraphs interleaved with links
                            ForEach(Array(config.paragraphs.enumerated()), id: \.offset) { pIdx, para in
                                Text(para)
                                    .font(.body)
                                    .foregroundStyle(.primary.opacity(0.85))
                                    .captureFrame(id: "label_paragraph_\(pIdx)")

                                // Insert a link after some paragraphs
                                if pIdx < config.links.count {
                                    let linkData = config.links[pIdx]
                                    Link(destination: URL(string: "https://\(linkData.displayURL)")!) {
                                        HStack(spacing: 4) {
                                            Text(linkData.label)
                                                .font(.body)
                                                .foregroundStyle(.blue)
                                                .underline()
                                            Image(systemName: "arrow.up.right")
                                                .font(.caption)
                                                .foregroundStyle(.blue)
                                        }
                                    }
                                    .captureFrame(id: "link_\(pIdx)")
                                }
                            }
                        }
                        .padding(.horizontal, 20)
                        .padding(.top, 20)
                        .padding(.bottom, 48)
                    }
                }
                .navigationTitle(config.title)
                .navigationBarTitleDisplayMode(.inline)
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}

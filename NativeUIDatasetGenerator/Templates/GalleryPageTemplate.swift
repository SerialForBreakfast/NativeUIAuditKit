// GalleryPageTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI horizontal gallery carousel with page control (TASK-5b-22).
// Structural distinction: full-screen TabView paginator with large imageView cards
// and a pageControl at the bottom — distinct from OnboardingPageTemplate (hero+text
// layout) and MediaCardGridTemplate (multi-column grid layout).
//
// Annotated elements:
//   imageView    — full-screen gallery image cards
//   pageControl  — manual page dot indicator at bottom
//   label        — image title and caption beneath each card
//   primaryButton — action button overlaid on last slide
//   navigationBar — auto-detected
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - GallerySlide

public struct GallerySlide: Sendable {
    public var hue: Double
    public var iconName: String
    public var title: String
    public var caption: String
}

// MARK: - GalleryPageConfig

public struct GalleryPageConfig: Sendable {
    public var title: String
    public var slides: [GallerySlide]   // 3–5 slides
    public var currentSlide: Int
    public var ctaLabel: String          // call-to-action on last slide
    public var colorScheme: ColorScheme

    public init(
        title: String,
        slides: [GallerySlide],
        currentSlide: Int,
        ctaLabel: String,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.slides = slides
        self.currentSlide = currentSlide
        self.ctaLabel = ctaLabel
        self.colorScheme = colorScheme
    }

    private static let slideIcons = [
        "photo.artframe", "paintbrush.fill", "camera.fill",
        "star.fill", "heart.fill", "sparkles", "bolt.fill", "leaf.fill",
    ]
    private static let captions = [
        "A stunning view from the top of the ridge.",
        "Captured during the golden hour.",
        "The city skyline at dusk.",
        "Wildlife in their natural habitat.",
        "Abstract patterns found in everyday objects.",
    ]
    private static let ctaLabels = ["Start Exploring", "Get Started", "Continue", "View Collection"]

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> GalleryPageConfig {
        var rng   = SeededRNG(seed: seed)
        let dark  = rng.next() % 2 == 0
        let count = 3 + Int(rng.next() % 3)   // 3–5 slides
        let cur   = Int(rng.next() % UInt64(count))
        var slides: [GallerySlide] = []
        for _ in 0..<count {
            let hue     = Double(rng.next() % 1000) / 1000.0
            let iconIdx = Int(rng.next() % UInt64(slideIcons.count))
            let capIdx  = Int(rng.next() % UInt64(captions.count))
            slides.append(GallerySlide(
                hue: hue,
                iconName: slideIcons[iconIdx],
                title: corpus.listRowTitle(),
                caption: captions[capIdx]
            ))
        }
        let cta = ctaLabels[Int(rng.next() % UInt64(ctaLabels.count))]
        return GalleryPageConfig(
            title: corpus.navigationTitle(),
            slides: slides,
            currentSlide: cur,
            ctaLabel: cta,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - GalleryPageTemplate

public struct GalleryPageTemplate: View {
    public let config: GalleryPageConfig

    public init(config: GalleryPageConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            Color(UIColor.systemBackground).ignoresSafeArea()

            NavigationStack {
                VStack(spacing: 0) {
                    // Gallery card — current slide only (static render; TabView not used
                    // because paging TabView is non-deterministic across rendering cycles)
                    let slide = config.slides[config.currentSlide]

                    ZStack {
                        Color(hue: slide.hue, saturation: 0.45, brightness: 0.65)
                            .frame(maxWidth: .infinity)
                            .frame(height: 320)
                        Image(systemName: slide.iconName)
                            .font(.system(size: 80))
                            .foregroundStyle(.white.opacity(0.75))
                    }
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                    .padding(.horizontal, 20)
                    .padding(.top, 16)
                    .captureFrame(id: "imageView_slide_\(config.currentSlide)")

                    // Slide text
                    VStack(alignment: .leading, spacing: 6) {
                        Text(slide.title)
                            .font(.title3.bold())
                            .captureFrame(id: "label_slide_title")
                        Text(slide.caption)
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                            .captureFrame(id: "label_slide_caption")
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 24)
                    .padding(.top, 16)

                    Spacer()

                    // Manual page control dots
                    HStack(spacing: 8) {
                        ForEach(0..<config.slides.count, id: \.self) { idx in
                            Circle()
                                .fill(idx == config.currentSlide
                                      ? Color.accentColor
                                      : Color.secondary.opacity(0.3))
                                .frame(width: idx == config.currentSlide ? 10 : 7,
                                       height: idx == config.currentSlide ? 10 : 7)
                        }
                    }
                    .captureFrame(id: "pageControl_0")
                    .padding(.bottom, 20)

                    // CTA button on last slide, hidden otherwise
                    if config.currentSlide == config.slides.count - 1 {
                        Button(config.ctaLabel) {}
                            .font(.body.bold())
                            .frame(maxWidth: .infinity, minHeight: 50)
                            .background(Color.accentColor)
                            .foregroundStyle(.white)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                            .captureFrame(id: "primaryButton_0")
                            .padding(.horizontal, 24)
                            .padding(.bottom, 36)
                    } else {
                        Spacer().frame(height: 86)
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

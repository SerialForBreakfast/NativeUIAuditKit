// MapOverlaysTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI map with overlays template (TASK-5b-18).
// Compiled exclusively into the iOS GeneratorRunner Xcode target.
//
// Annotated elements:
//   mapView       — the map content area (simulated with a coloured tile grid)
//   navigationBar — auto-detected (BP-17)
//   primaryButton — floating action button (e.g. "Directions", "Locate Me")
//
// Note: Real MKMapView is not used here because:
//   (a) MapKit renders asynchronously and tile loading is non-deterministic.
//   (b) Network tile images would break seed reproducibility.
// Instead, the map is simulated with a procedurally-generated tile grid using
// seed-derived colours — visually distinct from other template types.
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - MapOverlaysConfig

/// Parameterised inputs for a single MapOverlays rendering.
public struct MapOverlaysConfig: Sendable {
    /// Navigation bar title.
    public var title: String
    /// Base map hue (0–1) — drives land colour tint.
    public var mapHue: Double
    /// Primary floating button label.
    public var primaryButtonLabel: String
    /// Number of "pin" markers overlaid (0–5).
    public var pinCount: Int
    /// Color scheme applied to the view.
    public var colorScheme: ColorScheme

    public init(
        title: String,
        mapHue: Double,
        primaryButtonLabel: String,
        pinCount: Int,
        colorScheme: ColorScheme
    ) {
        self.title = title
        self.mapHue = mapHue
        self.primaryButtonLabel = primaryButtonLabel
        self.pinCount = pinCount
        self.colorScheme = colorScheme
    }

    /// Deterministic factory — same `seed` always produces the same config.
    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> MapOverlaysConfig {
        var rng = SeededRNG(seed: seed)
        let dark        = rng.next() % 2 == 0
        // Land hue: green–teal range (0.28–0.50) — realistic map approximation.
        let hue         = 0.28 + Double(rng.next() % 240) / 1000.0
        let pinCount    = Int(rng.next() % 6)    // 0–5 pins

        return MapOverlaysConfig(
            title: corpus.navigationTitle(),
            mapHue: hue,
            primaryButtonLabel: corpus.buttonLabel(),
            pinCount: pinCount,
            colorScheme: dark ? .dark : .light
        )
    }
}

// MARK: - MapOverlaysTemplate

/// SwiftUI view rendering a simulated map screen with pin overlays and
/// a floating action button.
///
/// **Platform scope:** iOS GeneratorRunner target only.
public struct MapOverlaysTemplate: View {
    public let config: MapOverlaysConfig

    public init(config: MapOverlaysConfig) {
        self.config = config
    }

    // Deterministic pin positions from mapHue-based PRNG.
    private var pinPositions: [(CGFloat, CGFloat)] {
        var rng = SeededRNG(seed: UInt64(config.mapHue * 1_000_000))
        return (0..<config.pinCount).map { _ in
            let x = 0.1 + Double(rng.next() % 800) / 1000.0
            let y = 0.1 + Double(rng.next() % 700) / 1000.0
            return (CGFloat(x), CGFloat(y))
        }
    }

    public var body: some View {
        NavigationStack {
            ZStack {
                // Simulated map tile grid
                GeometryReader { proxy in
                    let w = proxy.size.width
                    let h = proxy.size.height
                    let tileSize: CGFloat = 60
                    let cols = Int(w / tileSize) + 2
                    let rows = Int(h / tileSize) + 2

                    ZStack(alignment: .topLeading) {
                        // Land tiles
                        ForEach(0..<rows, id: \.self) { row in
                            ForEach(0..<cols, id: \.self) { col in
                                let brightness = 0.72 + Double((row + col) % 3) * 0.04
                                RoundedRectangle(cornerRadius: 1)
                                    .fill(Color(
                                        hue: config.mapHue,
                                        saturation: 0.20 + Double((col + row) % 4) * 0.03,
                                        brightness: brightness
                                    ))
                                    .frame(width: tileSize, height: tileSize)
                                    .offset(x: CGFloat(col) * tileSize, y: CGFloat(row) * tileSize)
                            }
                        }

                        // Pin overlays
                        ForEach(Array(pinPositions.enumerated()), id: \.offset) { _, pos in
                            Image(systemName: "mappin.circle.fill")
                                .font(.system(size: 28))
                                .foregroundStyle(.red)
                                .offset(x: pos.0 * w - 14, y: pos.1 * h - 28)
                        }
                    }
                    .frame(width: w, height: h)
                }
                .captureFrame(id: "mapView_0")
                .ignoresSafeArea()

                // Floating action button — bottom-right corner
                VStack {
                    Spacer()
                    HStack {
                        Spacer()
                        Button(config.primaryButtonLabel) {}
                            .padding(.horizontal, 16)
                            .padding(.vertical, 12)
                            .background(Color.accentColor)
                            .foregroundStyle(.white)
                            .clipShape(Capsule())
                            .shadow(color: .black.opacity(0.2), radius: 6, x: 0, y: 3)
                            .captureFrame(id: "primaryButton_0")
                            .padding(.trailing, 16)
                            .padding(.bottom, 80)
                    }
                }
            }
            .ignoresSafeArea(.all)
            .navigationTitle(config.title)
            .navigationBarTitleDisplayMode(.inline)
            .colorScheme(config.colorScheme)
        }
        .colorScheme(config.colorScheme)
    }
}

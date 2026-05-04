import SwiftUI

// MARK: - Ground truth constants

/// Declared point-space ground truth for the three spike fixture elements.
///
/// These values are the authoritative source for all coordinate comparisons in
/// ``CoordSpikeHostedTests``. Expected pixel coordinates are obtained by multiplying
/// each value by `UIScreen.main.scale` (2.0 or 3.0).
enum CoordSpikeGroundTruth {
    /// Button: 200×44 pt at origin (40, 100).
    static let button    = CGRect(x: 40,  y: 100, width: 200, height: 44)
    /// TextField: 280×44 pt at origin (40, 164).
    static let textField = CGRect(x: 40,  y: 164, width: 280, height: 44)
    /// Label: 200×30 pt at origin (40, 228).
    static let label     = CGRect(x: 40,  y: 228, width: 200, height: 30)
}

// MARK: - Primary fixture

/// SwiftUI fixture for the Phase 1 coordinate spike.
///
/// Three elements are placed at fixed positions using **padding-based layout** inside a
/// `ZStack(alignment: .topLeading)`. This ensures `GeometryReader` captures the true
/// rendered global frame — unlike `.offset()`, which shifts the visual position without
/// moving the layout frame.
///
/// The background `Color.white.ignoresSafeArea()` pins the coordinate origin to the
/// physical screen top-left, eliminating safe area inset as a variable.
///
/// - Parameter onFramesCaptured: Called on the main actor whenever SwiftUI's preference
///   propagation delivers updated element frames. The dictionary is keyed by the
///   `accessibilityIdentifier` strings matching those in ``CoordSpikeGroundTruth``.
struct CoordSpikeView: View {

    /// Callback invoked when all three element frames have been captured.
    /// Runs on the main actor, called from `onPreferenceChange`.
    var onFramesCaptured: (([String: CGRect]) -> Void)?

    @State private var textInput = ""

    var body: some View {
        ZStack(alignment: .topLeading) {
            Color.white

            // Button: 200×44 pt at (40, 100) — blue background for pixel-color validation.
            Button("Primary Button") {}
                .frame(width: 200, height: 44)
                .background(Color.blue.opacity(0.15))
                .border(Color.blue, width: 1)
                .accessibilityIdentifier("coord_spike_button")
                .background(frameReader(id: "coord_spike_button"))
                .padding(.top, 100)
                .padding(.leading, 40)

            // TextField: 280×44 pt at (40, 164) — UIKit-backed; tests accessibilityFrame parity.
            TextField("Text Field", text: $textInput)
                .frame(width: 280, height: 44)
                .textFieldStyle(.roundedBorder)
                .accessibilityIdentifier("coord_spike_textfield")
                .background(frameReader(id: "coord_spike_textfield"))
                .padding(.top, 164)
                .padding(.leading, 40)

            // Label: 200×30 pt at (40, 228) — pure SwiftUI text element.
            Text("Static Label")
                .frame(width: 200, height: 30, alignment: .leading)
                .accessibilityIdentifier("coord_spike_label")
                .background(frameReader(id: "coord_spike_label"))
                .padding(.top, 228)
                .padding(.leading, 40)
        }
        // ignoresSafeArea on the ZStack pins the layout origin to the physical screen
        // top-left (0, 0). Without this the ZStack starts at the safe-area boundary
        // (~62 pt below the status bar on iPhone 17 Pro), shifting all declared
        // coordinates by the status bar height. The background Color does not need
        // its own ignoresSafeArea once the container ignores it.
        .ignoresSafeArea(.all)
        .onPreferenceChange(CoordSpikeFramePreference.self) { frames in
            onFramesCaptured?(frames)
        }
    }

    private func frameReader(id: String) -> some View {
        GeometryReader { proxy in
            Color.clear
                .preference(
                    key: CoordSpikeFramePreference.self,
                    value: [id: proxy.frame(in: .global)]
                )
        }
    }
}

// MARK: - No-safe-area variant

/// Identical layout to ``CoordSpikeView`` but **without** `.ignoresSafeArea(.all)`.
///
/// Used by `testSafeAreaOriginShift` to measure whether safe area insets shift the
/// reported element origins relative to the physical screen top-left.
///
/// Expected outcome: when safe area is active, elements appear shifted downward by the
/// status bar height (approximately 59 pt on iPhone 17 Pro). The generator must use
/// `ignoresSafeArea` or compensate for this shift.
struct CoordSpikeNoSafeAreaVariant: View {

    var onFramesCaptured: (([String: CGRect]) -> Void)?

    @State private var textInput = ""

    var body: some View {
        ZStack(alignment: .topLeading) {
            Color.white  // No ignoresSafeArea — container is bounded by safe area.

            Button("Primary Button") {}
                .frame(width: 200, height: 44)
                .background(Color.blue.opacity(0.15))
                .border(Color.blue, width: 1)
                .accessibilityIdentifier("coord_spike_button_nosafe")
                .background(frameReader(id: "coord_spike_button_nosafe"))
                .padding(.top, 100)
                .padding(.leading, 40)

            TextField("Text Field", text: $textInput)
                .frame(width: 280, height: 44)
                .textFieldStyle(.roundedBorder)
                .accessibilityIdentifier("coord_spike_textfield_nosafe")
                .background(frameReader(id: "coord_spike_textfield_nosafe"))
                .padding(.top, 164)
                .padding(.leading, 40)

            Text("Static Label")
                .frame(width: 200, height: 30, alignment: .leading)
                .accessibilityIdentifier("coord_spike_label_nosafe")
                .background(frameReader(id: "coord_spike_label_nosafe"))
                .padding(.top, 228)
                .padding(.leading, 40)
        }
        .onPreferenceChange(CoordSpikeFramePreference.self) { frames in
            onFramesCaptured?(frames)
        }
    }

    private func frameReader(id: String) -> some View {
        GeometryReader { proxy in
            Color.clear
                .preference(
                    key: CoordSpikeFramePreference.self,
                    value: [id: proxy.frame(in: .global)]
                )
        }
    }
}

// MARK: - Clipped variant

/// A fixture with a child element that overflows a clipped container.
///
/// Container: 120×60 pt at (40, 100).
/// Child element: 240×120 pt — overflows the container by 2× in both axes.
///
/// Used by `testClipToBoundsFrameReporting` to document that `GeometryReader` reports the
/// **layout frame** of the child (240×120), not the **visible clipped rect** (120×60).
/// The generator must intersect each element's GeometryReader frame with the parent
/// container's clipping bounds to produce accurate visible-area annotations.
struct CoordSpikeClippedVariant: View {

    var onFramesCaptured: (([String: CGRect]) -> Void)?

    var body: some View {
        ZStack(alignment: .topLeading) {
            Color.white

            // Clipping container: 120×60 pt — clips the oversized child.
            ZStack(alignment: .topLeading) {
                Color.orange.opacity(0.3)
                    .frame(width: 240, height: 120)
                    .background(frameReader(id: "coord_spike_clipped_child"))
            }
            .frame(width: 120, height: 60)
            .clipped()
            .background(frameReader(id: "coord_spike_clipped_container"))
            .accessibilityIdentifier("coord_spike_clipped")
            .padding(.top, 100)
            .padding(.leading, 40)
        }
        .ignoresSafeArea(.all)
        .onPreferenceChange(CoordSpikeFramePreference.self) { frames in
            onFramesCaptured?(frames)
        }
    }

    private func frameReader(id: String) -> some View {
        GeometryReader { proxy in
            Color.clear
                .preference(
                    key: CoordSpikeFramePreference.self,
                    value: [id: proxy.frame(in: .global)]
                )
        }
    }
}

// MARK: - Shared preference key

/// SwiftUI preference key for propagating `GeometryReader` frames to parent views.
///
/// Used by all spike fixture variants. Keys are `accessibilityIdentifier` strings.
private struct CoordSpikeFramePreference: PreferenceKey {
    static let defaultValue: [String: CGRect] = [:]
    static func reduce(value: inout [String: CGRect], nextValue: () -> [String: CGRect]) {
        value.merge(nextValue(), uniquingKeysWith: { $1 })
    }
}

// MARK: - Preview

#Preview {
    CoordSpikeView()
}

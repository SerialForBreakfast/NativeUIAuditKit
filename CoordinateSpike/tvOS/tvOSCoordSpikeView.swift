// tvOSCoordSpikeView.swift
// CoordinateSpike/tvOS
//
// tvOS-specific SwiftUI fixture for validating coordinate alignment and focus-state
// frame capture on tvOS (1920×1080 landscape).

import SwiftUI

// MARK: - tvOS Ground Truth Constants

/// Authoritative point-space ground truth for the tvOS spike fixture elements.
public enum tvOSCoordSpikeGroundTruth {
    /// Button: 300×80 pt at origin (120, 140).
    public static let button = CGRect(x: 120, y: 140, width: 300, height: 80)
    /// Label: 400×60 pt at origin (120, 260).
    public static let label = CGRect(x: 120, y: 260, width: 400, height: 60)
    /// App tile / card (unfocused): 308×175 pt at origin (120, 360).
    public static let appTileUnfocused = CGRect(x: 120, y: 360, width: 308, height: 175)
    /// Settings row: 600×70 pt at origin (120, 580).
    public static let settingsRow = CGRect(x: 120, y: 580, width: 600, height: 70)
    /// Centered Alert modal: 700×320 pt centered in 1920×1080 (origin: 610, 380).
    public static let alert = CGRect(x: 610, y: 380, width: 700, height: 320)
}

// MARK: - Frame Preference Key

public struct tvOSCoordSpikeFramePreference: PreferenceKey {
    public typealias Value = [String: CGRect]
    public static let defaultValue: [String: CGRect] = [:]

    public static func reduce(value: inout [String: CGRect], nextValue: () -> [String: CGRect]) {
        value.merge(nextValue()) { $1 }
    }
}

// MARK: - Primary tvOS Coordinate Fixture

public struct tvOSCoordSpikeView: View {
    public var onFramesCaptured: (([String: CGRect]) -> Void)?
    public var isTileFocused: Bool = false

    public init(isTileFocused: Bool = false, onFramesCaptured: (([String: CGRect]) -> Void)? = nil) {
        self.isTileFocused = isTileFocused
        self.onFramesCaptured = onFramesCaptured
    }

    public var body: some View {
        ZStack(alignment: .topLeading) {
            Color.black

            // 1. Button: 300×80 pt at (120, 140)
            Button(action: {}) {
                Text("Select Option")
                    .font(.headline)
                    .frame(width: 300, height: 80)
            }
            .buttonStyle(.plain)
            .background(Color.blue.opacity(0.3))
            .border(Color.blue, width: 2)
            .background(frameReader(id: "tvos_button"))
            .padding(.top, 140)
            .padding(.leading, 120)

            // 2. Label: 400×60 pt at (120, 260)
            Text("tvOS System Header")
                .font(.title2)
                .foregroundColor(.white)
                .frame(width: 400, height: 60, alignment: .leading)
                .background(frameReader(id: "tvos_label"))
                .padding(.top, 260)
                .padding(.leading, 120)

            // 3. App Tile: 308×175 pt at (120, 360) (with visual focus elevation when focused)
            ZStack {
                RoundedRectangle(cornerRadius: 16)
                    .fill(isTileFocused ? Color.white : Color.gray.opacity(0.4))
                Text("App Tile")
                    .font(.headline)
                    .foregroundColor(isTileFocused ? .black : .white)
            }
            .frame(width: 308, height: 175)
            .scaleEffect(isTileFocused ? 1.15 : 1.0)
            .shadow(color: isTileFocused ? Color.white.opacity(0.6) : Color.clear, radius: 20)
            .background(frameReader(id: "tvos_app_tile"))
            .padding(.top, 360)
            .padding(.leading, 120)

            // 4. Settings Row: 600×70 pt at (120, 580)
            HStack {
                Text("Network Connection")
                    .foregroundColor(.white)
                Spacer()
                Text("Connected")
                    .foregroundColor(.gray)
            }
            .padding(.horizontal, 24)
            .frame(width: 600, height: 70)
            .background(Color.white.opacity(0.1))
            .cornerRadius(12)
            .background(frameReader(id: "tvos_settings_row"))
            .padding(.top, 580)
            .padding(.leading, 120)
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
        .onPreferenceChange(tvOSCoordSpikeFramePreference.self) { frames in
            onFramesCaptured?(frames)
        }
    }

    private func frameReader(id: String) -> some View {
        GeometryReader { proxy in
            Color.clear
                .preference(
                    key: tvOSCoordSpikeFramePreference.self,
                    value: [id: proxy.frame(in: .global)]
                )
        }
    }
}

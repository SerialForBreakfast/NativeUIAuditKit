import CoreGraphics

/// Package diagnostics use the unchanged runtime fallback on fixed proposals.
package enum FocusFallbackReplay {
    package static func resolve(
        image: CGImage, observations: [NativeUIElementObservation]
    ) -> [NativeUIElementObservation] {
        NativeUIDetectionRequest.resolveTVOSFocus(in: image, observations: observations)
    }
}

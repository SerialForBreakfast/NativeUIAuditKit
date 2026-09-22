import Foundation
import CoreGraphics
enum TVTestRigError: Error { case invalidArgument }
nonisolated struct NormalizedRectangle: Codable, Equatable, Sendable {
    let x: Double
    let y: Double
    let width: Double
    let height: Double

    init(x: Double, y: Double, width: Double, height: Double) throws {
        let values = [x, y, width, height]
        guard values.allSatisfy(\.isFinite),
              x >= 0,
              y >= 0,
              width > 0,
              height > 0,
              x + width <= 1,
              y + height <= 1 else {
            throw TVTestRigError.invalidArgument
        }
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    }
}
enum LocalVisionOCRService {
nonisolated static func crop(_ image: CGImage, roi: NormalizedRectangle) -> CGImage? {
        let pixel = CGRect(
            x: floor(roi.x * Double(image.width)),
            y: floor(roi.y * Double(image.height)),
            width: max(1, ceil(roi.width * Double(image.width))),
            height: max(1, ceil(roi.height * Double(image.height)))
        )
        return image.cropping(to: pixel)
    }
}

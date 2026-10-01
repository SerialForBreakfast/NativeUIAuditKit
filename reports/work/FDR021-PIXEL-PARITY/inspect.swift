import Foundation
import CoreGraphics
import ImageIO
let url = URL(fileURLWithPath: CommandLine.arguments[1])
let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
let image = CGImageSourceCreateImageAtIndex(source, 0, [kCGImageSourceShouldCache:false] as CFDictionary)!
print(image.alphaInfo.rawValue, image.bitmapInfo.rawValue, image.bitsPerPixel, image.bytesPerRow)
let data = image.dataProvider!.data! as Data
print(Array(data.prefix(32)))

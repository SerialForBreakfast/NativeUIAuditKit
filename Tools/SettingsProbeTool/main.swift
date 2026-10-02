import Foundation
import Vision
import CoreGraphics
import ImageIO
import CryptoKit

// Offline spike. RGB crop bytes come from the existing production cropper.
struct Frame: Decodable, Sendable { let path: String; let sha256: String }
struct Item: Decodable, Sendable {
    let id: String
    let beforeRGB: Data?
    let afterRGB: Data?
    let clipped: Bool?
    let before: Frame?
    let after: Frame?
    let bounds: [Double]?
}
struct Request: Decodable, Sendable { let version: Int; let root: String; let mode: String; let items: [Item] }
struct Result: Encodable, Sendable {
    var id: String
    var decision: String? = nil
    var metrics: [String: Double]? = nil
    var coverage: [String: [Double]]? = nil
    var bounds: [Double]? = nil
    var confidence: Float? = nil
    var status: String? = nil
    var reason: String? = nil
    var milliseconds: Double = 0
}
enum Invalid: Error { case request, bytes, path, image, bounds }

func quantile(_ sorted: [Double], _ q: Double) -> Double {
    let x = Double(sorted.count - 1) * q, lo = Int(x), hi = min(lo + 1, sorted.count - 1)
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (x - Double(lo))
}

func edges(_ lum: [Double], before: Bool) -> ([Int], Double) {
    var xs = [Double](repeating: 0, count: 255), ys = xs
    for y in 64..<192 { for x in 0..<255 { xs[x] += abs(lum[y*256+x+1]-lum[y*256+x])/128 } }
    for y in 0..<255 { for x in 64..<192 { ys[y] += abs(lum[(y+1)*256+x]-lum[y*256+x])/128 } }
    let ranges = before ? [24..<48, 208..<232] : [8..<64, 192..<248]
    var positions: [Int] = [], strength = Double.infinity
    for profile in [xs, ys] {
        for range in ranges {
            var best = range.lowerBound
            for i in range where profile[i] > profile[best] { best = i }
            positions.append(best); strength = min(strength, profile[best])
        }
    }
    return (positions, strength)
}

func measure(_ item: Item) throws -> Result {
    guard let ad = item.beforeRGB, let bd = item.afterRGB,
          ad.count == 256*256*3, bd.count == ad.count else { throw Invalid.bytes }
    let a = [UInt8](ad), b = [UInt8](bd)
    var differences: [Double] = [], al = [Double](repeating: 0, count: 65536), bl = al
    differences.reserveCapacity(a.count)
    let weights = [0.2126, 0.7152, 0.0722]
    for i in 0..<65536 {
        for c in 0..<3 {
            al[i] += Double(a[i*3+c])*weights[c]/255
            bl[i] += Double(b[i*3+c])*weights[c]/255
            differences.append(abs(Double(b[i*3+c])/255-Double(a[i*3+c])/255))
        }
    }
    let sorted = differences.sorted()
    let mean = differences.reduce(0,+)/Double(differences.count)
    let p95 = quantile(sorted, 0.95), maximum = sorted.last!
    let changed = Double(differences.filter { $0 > 0.04 }.count)/Double(differences.count)
    var border: [Double] = [], delta = 0.0
    var up = [Double](repeating: 0, count: 4), down = up
    for y in 0..<256 { for x in 0..<256 {
        let d = bl[y*256+x]-al[y*256+x]
        if x < 24 || x >= 232 || y < 24 || y >= 232 { border.append(d) }
        if (32..<224).contains(x) && (32..<224).contains(y) { delta += d/36864 }
        if (64..<192).contains(x) && (64..<192).contains(y) {
            let q = ((y-64)/64)*2+(x-64)/64
            if d >= 0.08 { up[q] += 1.0/4096 }
            if -d >= 0.08 { down[q] += 1.0/4096 }
        }
    } }
    let illumination = quantile(border.sorted(), 0.5)
    let (ae, astrength) = edges(al, before: true), (be, bstrength) = edges(bl, before: false)
    let ratios = [Double(be[1]-be[0])/Double(ae[1]-ae[0]), Double(be[3]-be[2])/Double(ae[3]-ae[2])]
    let drift = max(abs(Double(ae[0]+ae[1]-be[0]-be[1]))/2, abs(Double(ae[2]+ae[3]-be[2]-be[3]))/2)
    var growth = "unknown"
    if min(astrength,bstrength) >= 0.015 && abs(ratios[0]-ratios[1]) <= 0.06 && drift <= 8 {
        if ratios.min()! >= 1.05 { growth = "arrival" }
        else if ratios.max()! <= 0.95 { growth = "departure" }
    }
    if item.clipped == true { growth = "unknown" }
    let brightness = delta >= 0.08 ? "arrival" : delta <= -0.08 ? "departure" : "unknown"
    let signals = Set([growth, brightness].filter { $0 != "unknown" })
    var decision = signals.count == 1 ? signals.first! : "unknown"
    if ad == bd { decision = "unchanged" }
    if abs(illumination) > 0.04 { decision = "unknown" }
    else if decision == "unknown" && mean <= 0.01 && p95 <= 0.03 && changed <= 0.02 && maximum <= 0.25 { decision = "unchanged" }
    if decision == "arrival" && up.min()! < 0.6 { decision = "unknown" }
    if decision == "departure" && down.min()! < 0.6 { decision = "unknown" }
    return Result(id:item.id,decision:decision,metrics:["mean":mean,"p95":p95,"maximum":maximum,
        "changedFraction":changed,"borderLumaDelta":illumination,"lumaDelta":delta],coverage:["arrival":up,"departure":down])
}

func load(_ frame: Frame, root: URL) throws -> CGImage {
    let url = URL(fileURLWithPath: frame.path).standardizedFileURL
    guard url.resolvingSymlinksInPath() == url, url.path.hasPrefix(root.path+"/"),
          let size = try url.resourceValues(forKeys:[.fileSizeKey]).fileSize, size <= 32*1024*1024 else { throw Invalid.path }
    let data = try Data(contentsOf:url)
    guard SHA256.hash(data:data).map({String(format:"%02x",$0)}).joined() == frame.sha256,
          let source = CGImageSourceCreateWithData(data as CFData,nil),
          let props = CGImageSourceCopyPropertiesAtIndex(source,0,nil) as? [String:Any],
          let w=props[kCGImagePropertyPixelWidth as String] as? Int,
          let h=props[kCGImagePropertyPixelHeight as String] as? Int,
          w > 0, h > 0, w <= 40_000_000/h,
          let image=CGImageSourceCreateImageAtIndex(source,0,nil) else { throw Invalid.image }
    return image
}

func locate(_ a: CGImage, _ b: CGImage, _ rect: CGRect) throws -> (CGRect, Float)? {
    let handler = VNSequenceRequestHandler()
    let observation = VNDetectedObjectObservation(boundingBox: rect)
    let request = VNTrackObjectRequest(detectedObjectObservation: observation)
    request.trackingLevel = .accurate
    request.revision = 1
    try handler.perform([request], on:a)
    guard let initial = request.results?.first as? VNDetectedObjectObservation else { return nil }
    request.inputObservation = initial
    try handler.perform([request], on:b)
    guard let result = request.results?.first as? VNDetectedObjectObservation else { return nil }
    return (result.boundingBox,result.confidence)
}

func track(_ item: Item, root: URL) throws -> Result {
    guard let af=item.before, let bf=item.after, let v=item.bounds,
          v.count==4, v.allSatisfy({$0.isFinite}), v[0]>=0, v[1]>=0, v[2]>0, v[3]>0 else { throw Invalid.bounds }
    let a=try load(af,root:root), b=try load(bf,root:root)
    guard a.width==b.width, a.height==b.height else { return Result(id:item.id,status:"unavailable",reason:"viewport_changed") }
    let w=Double(a.width), h=Double(a.height)
    guard v[0]+v[2]<=w, v[1]+v[3]<=h else { throw Invalid.bounds }
    if af.sha256==bf.sha256 { return Result(id:item.id,bounds:v,confidence:1,status:"identical") }
    let rect=CGRect(x:v[0]/w,y:1-(v[1]+v[3])/h,width:v[2]/w,height:v[3]/h)
    guard let (f,c)=try locate(a,b,rect), c >= 0.55,
          let (r,rc)=try locate(b,a,f), rc >= 0.55 else { return Result(id:item.id,status:"unavailable",reason:"vision_confidence") }
    let error=hypot((r.midX-rect.midX)*w,(r.midY-rect.midY)*h)
    guard error<=max(2,0.15*v[3]), abs(f.width/rect.width-1)<=0.06, abs(f.height/rect.height-1)<=0.06 else {
        return Result(id:item.id,status:"unavailable",reason:"reciprocal_or_scale")
    }
    // Translation-only comparison preserves the original row scale.
    let translated=[Double(f.midX)*w-v[2]/2,(1-Double(f.midY))*h-v[3]/2,v[2],v[3]]
    guard translated[0]>=0, translated[1]>=0, translated[0]+v[2]<=w, translated[1]+v[3]<=h else {
        return Result(id:item.id,status:"unavailable",reason:"outside")
    }
    return Result(id:item.id,bounds:translated,confidence:c,status:"matched")
}

do {
    var bytes=Data()
    while let part=try FileHandle.standardInput.read(upToCount:65536), !part.isEmpty {
        bytes.append(part); guard bytes.count<=32*1024*1024 else { throw Invalid.request }
    }
    let req=try JSONDecoder().decode(Request.self,from:bytes)
    guard req.version==1, !req.items.isEmpty, req.items.count<=32,
          Set(req.items.map(\.id)).count==req.items.count, ["measure","track"].contains(req.mode) else { throw Invalid.request }
    let root=URL(fileURLWithPath:req.root).standardizedFileURL
    guard root.path != "/", root.resolvingSymlinksInPath()==root else { throw Invalid.path }
    let results=try req.items.map { item in
        try autoreleasepool {
            let start=ProcessInfo.processInfo.systemUptime
            var r=try req.mode=="measure" ? measure(item) : track(item,root:root)
            r.milliseconds=(ProcessInfo.processInfo.systemUptime-start)*1000
            return r
        }
    }
    FileHandle.standardOutput.write(try JSONEncoder().encode(results))
} catch {
    FileHandle.standardError.write(Data("SettingsProbeTool: \(error)\n".utf8)); exit(2)
}

import Foundation
let url = URL(fileURLWithPath: CommandLine.arguments[1])
let data = try Data(contentsOf: url)
var document = try PropertyListSerialization.propertyList(from: data, options: [], format: nil) as! [String: Any]
var objects = document["objects"] as! [String: Any]
let key = "9BF1E0717B79C4D52EDF31D0"
var file = objects[key] as! [String: Any]
precondition(file["path"] as? String == "/Volumes/Data/xcode/NewsTV/NewsTV/NovaAPIServer.swift")
file["path"] = "NewsTV/NovaAPIServer.swift"
file["sourceTree"] = "SOURCE_ROOT"
objects[key] = file
 document["objects"] = objects
let updated = try PropertyListSerialization.data(fromPropertyList: document, format: .xml, options: 0)
try updated.write(to: url, options: .atomic)

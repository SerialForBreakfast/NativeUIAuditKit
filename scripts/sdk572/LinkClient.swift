import Foundation
let url = URL(fileURLWithPath: CommandLine.arguments[1])
let targetName = CommandLine.arguments[2]
var doc = try PropertyListSerialization.propertyList(from: Data(contentsOf: url), options: [], format: nil) as! [String: Any]
var objects = doc["objects"] as! [String: [String: Any]]
func id() -> String { String(UUID().uuidString.replacingOccurrences(of: "-", with: "").prefix(24)) }
let targetID = objects.first { $0.value["isa"] as? String == "PBXNativeTarget" && $0.value["name"] as? String == targetName }!.key
let packageID = objects.first { $0.value["relativePath"] as? String == "Vendor/TTRDiagnostics" }?.key ?? id()
if objects[packageID] == nil {
    objects[packageID] = ["isa": "XCLocalSwiftPackageReference", "relativePath": "Vendor/TTRDiagnostics"]
    let projectID = doc["rootObject"] as! String
    var project = objects[projectID]!
    project["packageReferences"] = (project["packageReferences"] as? [String] ?? []) + [packageID]
    objects[projectID] = project
}
var target = objects[targetID]!
let frameworkID = (target["buildPhases"] as! [String]).first { objects[$0]?["isa"] as? String == "PBXFrameworksBuildPhase" }!
var framework = objects[frameworkID]!
let prior = target["packageProductDependencies"] as? [String] ?? []
// The local HTTP server remains in Query. Client supplies the app observation API.
for name in ["TTRDiagnostics", "TTRDiagnosticsUI", "TTRDiagnosticsLink", "TTRDiagnosticsClient", "TTRDiagnosticsQuery"] {
    if prior.contains(where: { objects[$0]?["productName"] as? String == name }) { continue }
    let productID = id(), buildID = id()
    objects[productID] = ["isa": "XCSwiftPackageProductDependency", "package": packageID, "productName": name]
    objects[buildID] = ["isa": "PBXBuildFile", "productRef": productID]
    target["packageProductDependencies"] = (target["packageProductDependencies"] as? [String] ?? []) + [productID]
    framework["files"] = (framework["files"] as? [String] ?? []) + [buildID]
}
objects[targetID] = target; objects[frameworkID] = framework; doc["objects"] = objects
try PropertyListSerialization.data(fromPropertyList: doc, format: .xml, options: 0).write(to: url, options: .atomic)

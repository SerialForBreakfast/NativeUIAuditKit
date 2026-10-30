import Foundation
let url = URL(fileURLWithPath: CommandLine.arguments[1])
var doc = try PropertyListSerialization.propertyList(from: Data(contentsOf: url), options: [], format: nil) as! [String: Any]
var objects = doc["objects"] as! [String: [String: Any]]
precondition(!objects.values.contains { $0["relativePath"] as? String == "Vendor/TTRDiagnostics" }, "SDK is already linked")
let targetID = objects.first { $0.value["isa"] as? String == "PBXNativeTarget" && $0.value["name"] as? String == "NewsTV" }!.key
let projectID = doc["rootObject"] as! String
func id() -> String { String(UUID().uuidString.replacingOccurrences(of: "-", with: "").prefix(24)) }
let packageID = id()
objects[packageID] = ["isa": "XCLocalSwiftPackageReference", "relativePath": "Vendor/TTRDiagnostics"]
var project = objects[projectID]!
project["packageReferences"] = (project["packageReferences"] as? [String] ?? []) + [packageID]
objects[projectID] = project
var target = objects[targetID]!
let existingFrameworkID = (target["buildPhases"] as! [String]).first { objects[$0]?["isa"] as? String == "PBXFrameworksBuildPhase" }
let frameworkID = existingFrameworkID ?? id()
var framework = objects[frameworkID] ?? ["isa": "PBXFrameworksBuildPhase", "buildActionMask": 2147483647, "files": [String](), "runOnlyForDeploymentPostprocessing": 0]
if existingFrameworkID == nil { target["buildPhases"] = (target["buildPhases"] as! [String]) + [frameworkID] }
for name in ["TTRDiagnostics", "TTRDiagnosticsUI", "TTRDiagnosticsLink", "TTRDiagnosticsQuery"] {
    let productID = id(), buildID = id()
    objects[productID] = ["isa": "XCSwiftPackageProductDependency", "package": packageID, "productName": name]
    objects[buildID] = ["isa": "PBXBuildFile", "productRef": productID]
    target["packageProductDependencies"] = (target["packageProductDependencies"] as? [String] ?? []) + [productID]
    framework["files"] = (framework["files"] as? [String] ?? []) + [buildID]
}
objects[targetID] = target; objects[frameworkID] = framework; doc["objects"] = objects
try PropertyListSerialization.data(fromPropertyList: doc, format: .xml, options: 0).write(to: url, options: .atomic)

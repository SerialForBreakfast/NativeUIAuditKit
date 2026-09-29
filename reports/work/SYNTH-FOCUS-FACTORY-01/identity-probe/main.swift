import Foundation

// Run against the retained, hash-verified producer Foundation source, not a copy
// of consumer canonicalization. No device, model or network operations.
let input = FileHandle.standardInput.readDataToEndOfFile()
let values = try JSONDecoder().decode([FixtureAppearance].self, from: input)
let results = values.map { ["canonical": $0.canonicalDigestSource, "family": $0.familyID] }
let encoder = JSONEncoder()
encoder.outputFormatting = [.sortedKeys, .prettyPrinted]
FileHandle.standardOutput.write(try encoder.encode(results))

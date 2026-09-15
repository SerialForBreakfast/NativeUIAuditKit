// DeviceDimensionDatabaseTests.swift
// NativeUIAuditKitTests

import CoreGraphics
import Foundation
import Testing
@testable import NativeUIAuditKit

@Suite("DeviceDimensionDatabase Lookup")
struct DeviceDimensionDatabaseTests {

    @Test("iPhone 15 Pro resolution maps to iPhone 15 Pro candidates")
    func iPhone15ProResolutionLookup() {
        let results = DeviceDimensionDatabase.lookup(width: 1179, height: 2556)
        #expect(!results.isEmpty)

        let match = results.first { $0.candidates.contains("iPhone 15 Pro") }
        #expect(match != nil)
        #expect(match?.platform == .iOS)
        #expect(match?.scale == 3)
        #expect(match?.hasDynamicIsland == true)
        #expect(match?.hasHomeIndicator == true)
    }

    @Test("iPhone SE resolution maps to SE models")
    func iPhoneSEResolutionLookup() {
        let results = DeviceDimensionDatabase.lookup(width: 750, height: 1334)
        #expect(!results.isEmpty)

        let match = results.first { $0.candidates.contains("iPhone SE (3rd gen)") }
        #expect(match != nil)
        #expect(match?.platform == .iOS)
        #expect(match?.scale == 2)
        #expect(match?.hasDynamicIsland == false)
        #expect(match?.hasHomeIndicator == false)
    }

    @Test("Apple TV 1080p resolution maps to tvOS")
    func appleTVResolutionLookup() {
        let results = DeviceDimensionDatabase.lookup(width: 1920, height: 1080)
        #expect(!results.isEmpty)

        let tvMatch = results.first { $0.platform == .tvOS }
        #expect(tvMatch != nil)
        #expect(tvMatch?.candidates.contains("Apple TV HD") == true)
    }

    @Test("MacBook Air 1440x900 resolution maps to macOS")
    func macOSResolutionLookup() {
        let results = DeviceDimensionDatabase.lookup(width: 1440, height: 900)
        #expect(!results.isEmpty)

        let macMatch = results.first { $0.platform == .macOS }
        #expect(macMatch != nil)
        #expect(macMatch?.candidates.contains("MacBook Air (13-inch)") == true)
    }

    @Test("Landscape screenshot dimensions resolve identically to portrait")
    func landscapeRotationMatches() {
        let portrait = DeviceDimensionDatabase.lookup(width: 1179, height: 2556)
        let landscape = DeviceDimensionDatabase.lookup(width: 2556, height: 1179)

        #expect(!portrait.isEmpty)
        #expect(!landscape.isEmpty)
        #expect(portrait == landscape)
    }

    @Test("Ambiguous resolutions return multiple candidate models")
    func ambiguousResolutionReturnsMultipleCandidates() {
        let results = DeviceDimensionDatabase.lookup(width: 1170, height: 2532)
        #expect(!results.isEmpty)

        let match = results.first!
        #expect(match.candidates.count >= 3)
        #expect(match.candidates.contains("iPhone 12"))
        #expect(match.candidates.contains("iPhone 13"))
        #expect(match.candidates.contains("iPhone 14"))
    }
}

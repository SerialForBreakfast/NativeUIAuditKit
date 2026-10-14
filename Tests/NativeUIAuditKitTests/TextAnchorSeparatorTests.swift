import Testing
import NativeUIAuditKit
@testable import NativeUIAuditKitRuntime

@Suite("OCR anchor separator regression")
struct TextAnchorSeparatorTests {
    @Test func observedROISeparators() {
        #expect(TextAnchorVerifier.matches("toggle slider stepperControl", in: "toggle ' slider • stepperControl"))
        #expect(TextAnchorVerifier.matches("general settings", in: "General ’ Settings"))
        #expect(TextAnchorVerifier.matches("general", in: "› General Settings"))
    }

    @Test func semanticPunctuationAndTokensStayDistinct() {
        for (anchor, text) in [("Wi-Fi Settings", "Wi Fi Settings"), ("A B", "A-B"),
                               ("Version 1.2", "Version 12"), ("Don't Delete", "Dont Delete"),
                               ("A B", "A / B"), ("A B", "A + B"), ("A B", "A ' • B"),
                               ("General Settings", "General • SettingsExtra"),
                               ("", "anything"), ("A B", "A • Not B")] {
            #expect(!TextAnchorVerifier.matches(anchor, in: text))
        }
        #expect(TextAnchorVerifier.matches("Wi-Fi Settings", in: "Open Wi-Fi Settings"))
    }

    @Test func forbiddenAndOptionalUseSamePolicy() {
        let regions = [RecognizedTextRegion(text: "Reset • Settings", boundingBox: .init(x: 0, y: 0, width: 1, height: 1))]
        let result = TextAnchorVerifier.evaluate(.init(required: ["Reset Settings"], optional: ["Reset Settings"], forbidden: ["Reset Settings"]), against: regions)
        #expect(result.status == .unverified)
        #expect(result.matchedRequired.count == 1 && result.matchedForbidden.count == 1 && result.matchedOptional.count == 1)
        #expect(result.matchedRequired.first?.region.text == "Reset • Settings")
    }
}

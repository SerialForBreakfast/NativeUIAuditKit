import SwiftUI

@main struct SheetInteractionApp: App {
    @State private var presented = false
    var body: some Scene {
        WindowGroup {
            AccessoryList609(training: false, presented: $presented) { _ in }
        }
    }
}

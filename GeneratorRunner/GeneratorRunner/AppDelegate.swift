// AppDelegate.swift
// GeneratorRunner
//
// Minimal application delegate for the GeneratorRunner iOS app.
//
// This app has no visible UI. It exists solely as the host process for the
// iOS capture pipeline — ScreenshotCapture renders SwiftUI templates into
// off-screen UIWindow instances programmatically. All capture work is
// initiated by the macOS NativeUIDatasetGenerator orchestrator via
// xcrun simctl, which installs this app and triggers captures by writing
// a config JSON to the shared container, then launching the app.
//
// Concurrency: AppDelegate methods are called on the main thread by UIKit.

import UIKit

@main
final class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        true
    }
}

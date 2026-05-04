import UIKit

/// Minimal application delegate for the coordinate spike test host.
///
/// This app has no UI of its own — it exists solely to host the `CoordSpikeHostedTests`
/// unit test bundle. The test runner creates `UIWindow` instances and `UIHostingController`
/// objects directly inside test methods.
@main
final class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        true
    }
}

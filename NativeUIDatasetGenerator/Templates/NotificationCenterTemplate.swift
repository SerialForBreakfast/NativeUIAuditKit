// NotificationCenterTemplate.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Parameterised SwiftUI notification-style grouped rows template (TASK-5b-22).
// Structural distinction: no NavigationStack wrapper — standalone lock-screen/
// notification-center style layout with rounded cards, app icons, timestamps,
// and grouped rows. Teaches the model to recognise `listRow` outside a UITableView context.
//
// Annotated elements:
//   listRow    — each notification card (rounded background)
//   label      — notification title, body, timestamp, app name
//   imageView  — app icon placeholder in each notification
//
// Layout rules (Phase 1 mandates):
//   - Root ZStack carries .ignoresSafeArea(.all)
//   - All offsets use padding — never .offset()
//   - Every annotated element attaches .captureFrame(id:) BEFORE layout padding (BP-18)

import SwiftUI
import UIKit

// MARK: - NotificationItem

public struct NotificationItem: Sendable {
    public var appName: String
    public var title: String
    public var body: String
    public var timestamp: String
    public var iconHue: Double
    public var iconName: String
}

// MARK: - NotificationCenterConfig

public struct NotificationCenterConfig: Sendable {
    public var dateLabel: String
    /// 2–5 notifications.
    public var items: [NotificationItem]
    public var colorScheme: ColorScheme

    public init(dateLabel: String, items: [NotificationItem], colorScheme: ColorScheme) {
        self.dateLabel = dateLabel
        self.items = items
        self.colorScheme = colorScheme
    }

    private static let appNames   = ["Messages", "Mail", "Calendar", "Reminders", "News",
                                     "Health", "Finance", "Photos", "Maps", "Shortcuts"]
    private static let appIcons   = ["message.fill", "envelope.fill", "calendar",
                                     "checklist", "newspaper.fill", "heart.fill",
                                     "chart.line.uptrend.xyaxis", "photo.fill",
                                     "map.fill", "bolt.fill"]
    private static let bodies     = [
        "You have a new message waiting.",
        "Your appointment is confirmed for tomorrow.",
        "New article: Market trends this week.",
        "Reminder: Call back before 3 PM.",
        "Your photo memory is ready to view.",
        "Package out for delivery today.",
        "Low battery warning on your device.",
        "Weekly summary is now available.",
    ]
    private static let timestamps = [
        "now", "1m ago", "5m ago", "12m ago", "1h ago",
        "2h ago", "Yesterday", "Mon",
    ]
    private static let dateLabels = [
        "Today", "Yesterday", "Monday", "Tuesday", "Wednesday"
    ]

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> NotificationCenterConfig {
        var rng   = SeededRNG(seed: seed)
        let dark  = rng.next() % 2 == 0
        let count = 2 + Int(rng.next() % 4)   // 2–5 items
        var items: [NotificationItem] = []
        for _ in 0..<count {
            let appIdx = Int(rng.next() % UInt64(appNames.count))
            let hue    = Double(rng.next() % 1000) / 1000.0
            let body   = bodies[Int(rng.next() % UInt64(bodies.count))]
            let ts     = timestamps[Int(rng.next() % UInt64(timestamps.count))]
            items.append(NotificationItem(
                appName: appNames[appIdx],
                title: corpus.listRowTitle(),
                body: body,
                timestamp: ts,
                iconHue: hue,
                iconName: appIcons[appIdx]
            ))
        }
        let dl = dateLabels[Int(rng.next() % UInt64(dateLabels.count))]
        return NotificationCenterConfig(dateLabel: dl, items: items,
                                        colorScheme: dark ? .dark : .light)
    }
}

// MARK: - NotificationCenterTemplate

public struct NotificationCenterTemplate: View {
    public let config: NotificationCenterConfig

    public init(config: NotificationCenterConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack {
            // Dark wallpaper-like gradient background (lock screen aesthetic)
            LinearGradient(
                colors: [
                    Color(hue: 0.62, saturation: 0.55, brightness: config.colorScheme == .dark ? 0.18 : 0.80),
                    Color(hue: 0.70, saturation: 0.45, brightness: config.colorScheme == .dark ? 0.12 : 0.70),
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(alignment: .leading, spacing: 0) {
                // Date header
                Text(config.dateLabel)
                    .font(.footnote.weight(.semibold))
                    .foregroundStyle(config.colorScheme == .dark ? .white.opacity(0.7) : .black.opacity(0.5))
                    .padding(.horizontal, 20)
                    .padding(.top, 60)
                    .padding(.bottom, 10)
                    .captureFrame(id: "label_date_header")

                // Notification cards
                ScrollView {
                    VStack(spacing: 10) {
                        ForEach(Array(config.items.enumerated()), id: \.offset) { idx, item in
                            HStack(alignment: .top, spacing: 12) {
                                // App icon
                                ZStack {
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color(hue: item.iconHue, saturation: 0.7, brightness: 0.85))
                                        .frame(width: 40, height: 40)
                                    Image(systemName: item.iconName)
                                        .font(.body)
                                        .foregroundStyle(.white)
                                }
                                .captureFrame(id: "imageView_icon_\(idx)")

                                // Text content
                                VStack(alignment: .leading, spacing: 2) {
                                    HStack {
                                        Text(item.appName)
                                            .font(.caption.weight(.semibold))
                                            .foregroundStyle(.secondary)
                                            .captureFrame(id: "label_app_\(idx)")
                                        Spacer()
                                        Text(item.timestamp)
                                            .font(.caption2)
                                            .foregroundStyle(.secondary)
                                            .captureFrame(id: "label_ts_\(idx)")
                                    }
                                    Text(item.title)
                                        .font(.subheadline.weight(.medium))
                                        .captureFrame(id: "label_title_\(idx)")
                                    Text(item.body)
                                        .font(.subheadline)
                                        .foregroundStyle(.secondary)
                                        .lineLimit(2)
                                        .captureFrame(id: "label_body_\(idx)")
                                }
                            }
                            .padding(14)
                            .background(
                                RoundedRectangle(cornerRadius: 16)
                                    .fill(.ultraThinMaterial)
                            )
                            .captureFrame(id: "listRow_\(idx)")
                            .padding(.horizontal, 16)
                        }
                    }
                    .padding(.bottom, 48)
                }
            }
        }
        .ignoresSafeArea(.all)
        .colorScheme(config.colorScheme)
    }
}

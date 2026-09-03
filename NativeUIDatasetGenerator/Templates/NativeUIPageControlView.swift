// NativeUIPageControlView.swift
// NativeUIDatasetGenerator — iOS GeneratorRunner target only
//
// Shared page-indicator views for train templates (TASK-6a-8 / BP-32).
// Holdout OnboardingPage and GalleryPage use isolated SwiftUI dots; KitchenSink
// previously packed 7pt circles and Run 007 missed 97.5% of holdout pageControl.

import SwiftUI
import UIKit

/// Isolated `UIPageControl` at onboarding scale. Use this in train families so
/// the detector sees real UIKit dots, not packed kitchen-sink circles.
struct NativeUIPageControlView: UIViewRepresentable {
    var numberOfPages: Int
    var currentPage: Int

    func makeUIView(context: Context) -> UIPageControl {
        let control = UIPageControl()
        control.numberOfPages = max(2, numberOfPages)
        control.currentPage = max(0, min(currentPage, control.numberOfPages - 1))
        control.currentPageIndicatorTintColor = .label
        control.pageIndicatorTintColor = .tertiaryLabel
        control.isUserInteractionEnabled = false
        return control
    }

    func updateUIView(_ uiView: UIPageControl, context: Context) {
        uiView.numberOfPages = max(2, numberOfPages)
        uiView.currentPage = max(0, min(currentPage, uiView.numberOfPages - 1))
    }
}

/// Isolated SwiftUI page dots matching OnboardingPage / GalleryPage holdout chrome
/// (HStack of 7pt/10pt circles, 8pt spacing). Train families that never showed
/// this style caused the Run 007 pageControl miss.
struct NativeUIPageDotsView: View {
    var pageCount: Int
    var currentPage: Int

    var body: some View {
        let count = max(2, pageCount)
        let current = max(0, min(currentPage, count - 1))
        HStack(spacing: 8) {
            ForEach(0..<count, id: \.self) { idx in
                Circle()
                    .fill(idx == current
                          ? Color.accentColor
                          : Color.secondary.opacity(0.3))
                    .frame(
                        width: idx == current ? 10 : 7,
                        height: idx == current ? 10 : 7
                    )
            }
        }
    }
}

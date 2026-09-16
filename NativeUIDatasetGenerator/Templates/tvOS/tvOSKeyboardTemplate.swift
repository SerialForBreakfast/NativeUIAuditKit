// tvOSKeyboardTemplate.swift
// NativeUIDatasetGenerator — tvOS templates
//
// Parameterised on-screen keyboard template for tvOS OS UI detection (TASK-6b-E6).
// Models the Apple TV linear character grid, text field input with insertion cursor,
// space, delete, dictation, and search action keys.
//
// Annotated elements:
//   textField       — search/text entry input field with placeholder or typed text
//   searchField     — search box container
//   primaryButton   — "Search" / "Done" action button
//   secondaryButton — special keys (Space, Delete, Dictation, Shift, 123)
//   collectionItem  — individual character key caps (A-Z, 0-9)
//   label           — key characters, text field text, helper prompt
//   imageView       — search icon, dictation mic, backspace icon

import SwiftUI

// MARK: - tvOSKeyboardConfig

public struct tvOSKeyboardConfig: Sendable {
    public var enteredText: String
    public var placeholder: String
    public var keyRows: [[String]]
    public var focusedRow: Int
    public var focusedCol: Int
    public var isDictationActive: Bool
    public var bgHue: Double

    public init(
        enteredText: String = "Ted Lasso",
        placeholder: String = "Search Movies, TV Shows, and People",
        keyRows: [[String]] = [
            ["A", "B", "C", "D", "E", "F", "G"],
            ["H", "I", "J", "K", "L", "M", "N"],
            ["O", "P", "Q", "R", "S", "T", "U"],
            ["V", "W", "X", "Y", "Z", "1", "2"],
            ["3", "4", "5", "6", "7", "8", "9"]
        ],
        focusedRow: Int = 0,
        focusedCol: Int = 2,
        isDictationActive: Bool = false,
        bgHue: Double = 0.5
    ) {
        self.enteredText = enteredText
        self.placeholder = placeholder
        self.keyRows = keyRows
        self.focusedRow = focusedRow
        self.focusedCol = focusedCol
        self.isDictationActive = isDictationActive
        self.bgHue = bgHue
    }

    public static func make(seed: UInt64, corpus: inout ContentCorpus) -> tvOSKeyboardConfig {
        var rng = SeededRNG(seed: seed)
        let queries = ["Ted Lasso", "Severance", "Action Movies", "Sci-Fi", "Star Wars", "Apple TV+", "Comedy", ""]
        let query = queries[Int(rng.next() % UInt64(queries.count))]

        let r = Int(rng.next() % 5)
        let c = Int(rng.next() % 7)
        let hue = Double(rng.next() % 1000) / 1000.0

        return tvOSKeyboardConfig(
            enteredText: query,
            placeholder: "Search Movies, TV Shows, and People",
            focusedRow: r,
            focusedCol: c,
            isDictationActive: (rng.next() % 10 == 0),
            bgHue: hue
        )
    }
}

// MARK: - tvOSKeyboardTemplate View

public struct tvOSKeyboardTemplate: View {
    public let config: tvOSKeyboardConfig

    public init(config: tvOSKeyboardConfig) {
        self.config = config
    }

    public var body: some View {
        ZStack(alignment: .top) {
            // Dark wallpaper background
            Color(red: 0.06, green: 0.06, blue: 0.09).ignoresSafeArea()

            VStack(spacing: 36) {
                // Top Search / Text Field
                HStack(spacing: 16) {
                    Image(systemName: "magnifyingglass")
                        .font(.system(size: 26))
                        .foregroundColor(.white.opacity(0.6))
                        .captureFrame(id: "imageView_search_icon")

                    if config.enteredText.isEmpty {
                        Text(config.placeholder)
                            .font(.system(size: 28))
                            .foregroundColor(.white.opacity(0.4))
                            .captureFrame(id: "label_placeholder")
                    } else {
                        HStack(spacing: 2) {
                            Text(config.enteredText)
                                .font(.system(size: 30, weight: .semibold))
                                .foregroundColor(.white)
                                .captureFrame(id: "label_entered_text")

                            // Blinking insertion cursor
                            Rectangle()
                                .fill(Color.blue)
                                .frame(width: 3, height: 34)
                        }
                    }

                    Spacer()

                    if !config.enteredText.isEmpty {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(.white.opacity(0.5))
                            .captureFrame(id: "cancelAction_clear_text")
                    }
                }
                .padding(.horizontal, 28)
                .frame(width: 1080, height: 76)
                .background(Color.white.opacity(0.1))
                .cornerRadius(20)
                .overlay(RoundedRectangle(cornerRadius: 20).stroke(Color.white.opacity(0.2), lineWidth: 1))
                .captureFrame(id: "searchField_input_box")
                .padding(.top, 70)

                // Keyboard Container
                HStack(alignment: .top, spacing: 48) {
                    // Alphanumeric Key Grid (5 rows x 7 cols)
                    VStack(spacing: 12) {
                        ForEach(Array(config.keyRows.enumerated()), id: \.offset) { rIdx, row in
                            HStack(spacing: 12) {
                                ForEach(Array(row.enumerated()), id: \.offset) { cIdx, keyChar in
                                    let isFoc = (rIdx == config.focusedRow && cIdx == config.focusedCol)

                                    Text(keyChar)
                                        .font(.system(size: 26, weight: isFoc ? .bold : .medium))
                                        .foregroundColor(isFoc ? .black : .white)
                                        .frame(width: 68, height: 64)
                                        .background(isFoc ? Color.white : Color.white.opacity(0.08))
                                        .cornerRadius(14)
                                        .scaleEffect(isFoc ? 1.12 : 1.0)
                                        .shadow(color: isFoc ? Color.white.opacity(0.5) : Color.clear, radius: 10)
                                        .captureFrame(id: isFoc ? "collectionItem_key_\(keyChar)_focused" : "collectionItem_key_\(keyChar)_unfocused")
                                }
                            }
                        }
                    }

                    // Special Action Keys Column (Space, Delete, Dictation, Search)
                    VStack(spacing: 12) {
                        // Dictation Key
                        HStack(spacing: 12) {
                            Image(systemName: config.isDictationActive ? "mic.fill" : "mic")
                                .font(.system(size: 22))
                                .foregroundColor(config.isDictationActive ? .red : .white)
                            Text("Dictate")
                                .font(.system(size: 20, weight: .semibold))
                                .foregroundColor(.white)
                        }
                        .frame(width: 220, height: 64)
                        .background(Color.white.opacity(0.08))
                        .cornerRadius(14)
                        .captureFrame(id: "secondaryButton_dictate_unfocused")

                        // Space Key
                        HStack {
                            Text("Space")
                                .font(.system(size: 20, weight: .semibold))
                                .foregroundColor(.white)
                        }
                        .frame(width: 220, height: 64)
                        .background(Color.white.opacity(0.08))
                        .cornerRadius(14)
                        .captureFrame(id: "secondaryButton_space_unfocused")

                        // Delete Key
                        HStack(spacing: 10) {
                            Image(systemName: "delete.left")
                                .font(.system(size: 22))
                            Text("Delete")
                                .font(.system(size: 20, weight: .semibold))
                        }
                        .foregroundColor(.white)
                        .frame(width: 220, height: 64)
                        .background(Color.white.opacity(0.08))
                        .cornerRadius(14)
                        .captureFrame(id: "secondaryButton_delete_unfocused")

                        // Search / Done Action (Primary)
                        HStack {
                            Text("Search")
                                .font(.system(size: 22, weight: .bold))
                                .foregroundColor(.black)
                        }
                        .frame(width: 220, height: 64)
                        .background(Color.white)
                        .cornerRadius(14)
                        .captureFrame(id: "primaryButton_search_action_unfocused")
                    }
                }
                .padding(.top, 10)

                // Subtitle guide
                Text("Press and hold the Siri Remote button to dictate")
                    .font(.system(size: 20))
                    .foregroundColor(.white.opacity(0.5))
                    .captureFrame(id: "label_dictation_hint")
            }
        }
        .frame(width: 1920, height: 1080)
        .ignoresSafeArea(.all)
    }
}

// SeededRNG.swift
// NativeUIDatasetGenerator
//
// Deterministic xorshift64 random number generator.
// Platform-agnostic — compiles on macOS (SPM orchestrator) and iOS (GeneratorRunner).
//
// Used by ContentCorpus and template config factories to produce stable,
// reproducible text content and layout variations from a seed.

// MARK: - SeededRNG

/// A deterministic xorshift64 random number generator.
///
/// Same seed always produces the same sequence. Not cryptographically secure —
/// used only for reproducible dataset generation.
///
/// Conforms to `RandomNumberGenerator` so it can be passed directly to
/// standard library shuffle/random methods.
struct SeededRNG: RandomNumberGenerator {
    private var state: UInt64

    /// - Parameter seed: Initial state. A seed of `0` is treated as `1` to avoid the
    ///   degenerate all-zero xorshift state.
    init(seed: UInt64) {
        state = seed == 0 ? 1 : seed
    }

    mutating func next() -> UInt64 {
        state ^= state << 13
        state ^= state >> 7
        state ^= state << 17
        return state
    }
}

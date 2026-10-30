import Foundation

@main struct ContentChecks {
    static func main() {
        let expected = ProcessInfo.processInfo.arguments.contains("--expect-enabled")
        precondition(REAL543Content.enabled == expected)
        guard expected else { print("Controlled content disabled"); return }
        for year in [1900, 2015, 2024, 2035] {
            let a = GameUtils.generateYearOptions(correctYear: year)
            precondition(a.count == 8 && a.contains(year))
            precondition(a == GameUtils.generateYearOptions(correctYear: year))
        }
        let cities = ["Tokyo", "London", "Paris", "Rome", "Sydney", "New York"]
        let a = GameUtils.generateLocationOptions(correctValue: "Paris", allValues: cities)
        precondition(a == GameUtils.generateLocationOptions(correctValue: "Paris", allValues: cities.reversed()))
        precondition(a.count == 5 && a.contains("Paris"))
        precondition(GameUtils.daysInMonth(month: 2, year: 2024) == 29)
        precondition(GameUtils.firstWeekdayOfMonth(month: 1, year: 2026) == 4)
        let ids = (0..<10).map(REAL543Content.identifier)
        precondition(Set(ids).count == 10)
        print(ids.map { "\($0.uuidString):\(REAL543Content.hue($0))" }.joined(separator: "\n"))
        print(a.joined(separator: ","))
    }
}

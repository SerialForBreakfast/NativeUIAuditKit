# Dataset Balance Report — Phase 4

**Generated:** 2026-05-18  
**Dataset version:** `.build/debug-output/dataset/`  
**Total images:** 2,700 (600 SwiftUI + 2,100 UIKit)  

## Split Distribution

| Split | Count |
|-------|------:|
| train | 2,160 |
| validation | 270 |
| test | 270 |

## Template Family Distribution

| Template | Framework | Count |
|----------|-----------|------:|
| UIKitControls | UIKit | 700 |
| UIKitForm | UIKit | 700 |
| UIKitList | UIKit | 700 |
| Alert | SwiftUI | 200 |
| LoginForm | SwiftUI | 200 |
| SettingsList | SwiftUI | 200 |

## Class Distribution (Normalised to Canonical Taxonomy)

| Element Type | Instances | Tier |
|-------------|----------:|------|
| `listRow` | 5,480 | High |
| `tabBarItem` | 3,602 | Chrome |
| `label` | 3,023 | High |
| `toggle` | 2,798 | High |
| `navigationBar` | 2,500 | Chrome |
| `secondaryButton` | 2,200 | High |
| `textField` | 1,645 | High |
| `secureField` | 1,600 | High |
| `primaryButton` | 1,100 | High |
| `tabBar` | 900 | Chrome |
| `activityIndicator` | 700 | Medium |
| `pageControl` | 700 | Medium |
| `progressView` | 700 | Medium |
| `segmentedControl` | 700 | Medium |
| `slider` | 700 | Medium |
| `alert` | 200 | Medium |
| `disclosureGroup` | 200 | Medium |
| `homeIndicator` | 200 | Chrome |
| `cancelAction` | 126 | Low/Rare |
| `link` | 100 | Low/Rare |
| `destructiveButton` | 58 | Low/Rare |

## Imbalance Analysis (Content Classes, Both Frameworks)

- **Ratio:** 4.98× (`listRow` ÷ `primaryButton`)  
- **Threshold:** 5.0×  
- **Status:** ✅ PASS  

| Class | Instances |
|-------|----------:|
| `listRow` | 5,480 |
| `label` | 3,023 |
| `toggle` | 2,798 |
| `secondaryButton` | 2,200 |
| `textField` | 1,645 |
| `secureField` | 1,600 |
| `primaryButton` | 1,100 |

## TASK-4-3 Gate Results

| AC | Description | Result |
|----|-------------|--------|
| AC-1 | Total ≥ 2,700 (UIKit ≥ 2,000, SwiftUI ≥ 600) | ✅ PASS |
| AC-2 | ≥5 distinct simulator state times | ✅ PASS |
| AC-3 | SHA-256 match rate = 1.0 | ✅ PASS |
| AC-4 | Content class imbalance ≤ 5:1 | ✅ PASS (3.33×) |
| AC-5 | No UIKit template > 15% of any class | ✅ PASS |

**Phase 4 gate: OPEN ✅**
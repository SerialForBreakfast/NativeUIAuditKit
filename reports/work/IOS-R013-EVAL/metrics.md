# Run013 evaluation metrics

Source: [evaluation.json](evaluation.json). Custom all-point interpolated VOC AP,
not official COCO/Ultralytics AP. Values are fractions; unsupported classes are
unavailable and excluded from supported-class macro means, never imputed as zero.
Precision/recall and TP/FP/FN use confidence ≥0.25 and IoU ≥0.50; AP uses all
exported detections (confidence ≥0.001). Per-class AP50–95 averages ten thresholds.

Only the 2,000 identical withheld cases support Run009→Run013 deltas. The
400 addon cases are within-family diagnostics; 2,400 combined is supplementary.
The historical original-corpus 0.586 has no numerical delta here.

| Population | Images | Classes | mAP50 | mAP70 | mAP90 | mAP50–95 |
| --- | --- | --- | --- | --- | --- | --- |
| Run009 withheld | 2000 | 13 | 0.5549 | 0.4310 | 0.2302 | 0.3982 |
| Run013 addon | 400 | 33 | 0.9785 | 0.9697 | 0.9696 | 0.9703 |
| Run013 combined | 2400 | 38 | 0.8790 | 0.8551 | 0.8375 | 0.8527 |
| Run013 withheld | 2000 | 13 | 0.6322 | 0.5834 | 0.5299 | 0.5707 |

## Run009 withheld

| Class | GT boxes | AP50 | AP70 | AP90 | AP50–95 | Precision | Recall | TP | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| actionSheet | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| activityIndicator | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| alert | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 15 | 0 |
| cancelAction | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 309 | 0 |
| collectionItem | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| colorWell | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| contextMenu | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| destructiveButton | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 25 | 0 |
| disclosureGroup | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 53 | 0 |
| dynamicIsland | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 6 | 0 |
| homeIndicator | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| imageView | 1900 | 0.1571 | 0.1563 | 0.1088 | 0.1462 | 0.4049 | 0.1647 | 313 | 460 | 1587 |
| label | 9165 | 0.7004 | 0.6599 | 0.1244 | 0.5153 | 0.7074 | 0.7411 | 6792 | 2810 | 2373 |
| link | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 95 | 0 |
| listRow | 700 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 3474 | 700 |
| mapView | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 3 | 0 |
| menuButton | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 1 | 0 |
| navigationBar | 800 | 0.9998 | 0.9998 | 0.9818 | 0.9473 | 0.8999 | 1.0000 | 800 | 89 | 0 |
| pageControl | 600 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 90 | 600 |
| picker | 200 | 0.8053 | 0.0040 | 0.0000 | 0.2465 | 0.4639 | 0.7700 | 154 | 178 | 46 |
| popover | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| primaryButton | 1366 | 1.0000 | 1.0000 | 0.9984 | 0.9928 | 0.8706 | 1.0000 | 1366 | 203 | 0 |
| progressView | 200 | 0.9998 | 0.2462 | 0.0000 | 0.3492 | 1.0000 | 0.7450 | 149 | 0 | 51 |
| refreshControl | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| scrollIndicator | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| searchField | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| secondaryButton | 341 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 341 |
| secureField | 200 | 0.6001 | 0.6001 | 0.1300 | 0.5015 | 0.5161 | 0.5600 | 112 | 105 | 88 |
| segmentedControl | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 5 | 0 |
| sheet | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 391 | 0 |
| sidebar | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| slider | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 101 | 0 |
| statusBar | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| stepperControl | 200 | 0.5940 | 0.5940 | 0.0000 | 0.3564 | 0.5000 | 1.0000 | 200 | 200 | 0 |
| tabBar | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| textField | 503 | 0.5482 | 0.5482 | 0.0247 | 0.3963 | 0.7118 | 0.4911 | 247 | 100 | 256 |
| toggle | 1687 | 0.8085 | 0.7939 | 0.6249 | 0.7250 | 0.7512 | 0.7641 | 1289 | 427 | 398 |
| toolbar | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| tooltip | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| unknown | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| webContent | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |

### Per-family supported-class means

| Family | Images | Classes | mAP50 | mAP70 | mAP90 | mAP50–95 |
| --- | --- | --- | --- | --- | --- | --- |
| CardDetail | 200 | 4 | 0.7136 | 0.7136 | 0.5577 | 0.6627 |
| EmptyState | 400 | 3 | 0.4868 | 0.4068 | 0.3333 | 0.3978 |
| GalleryPage | 200 | 5 | 0.7872 | 0.7837 | 0.4683 | 0.6983 |
| MultiSectionForm | 200 | 8 | 0.7769 | 0.6655 | 0.3015 | 0.5781 |
| NotificationCenter | 200 | 3 | 0.3027 | 0.2998 | 0.0602 | 0.2304 |
| OnboardingPage | 400 | 4 | 0.3494 | 0.2754 | 0.2508 | 0.2884 |
| SettingsToggleDense | 200 | 3 | 0.9424 | 0.9424 | 0.6903 | 0.8526 |
| WizardStepFlow | 200 | 6 | 0.6403 | 0.5147 | 0.4064 | 0.4932 |

## Run013 addon

| Class | GT boxes | AP50 | AP70 | AP90 | AP50–95 | Precision | Recall | TP | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| actionSheet | 24 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| activityIndicator | 50 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 50 | 0 | 0 |
| alert | 14 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 14 | 0 | 0 |
| cancelAction | 80 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9524 | 1.0000 | 80 | 4 | 0 |
| collectionItem | 400 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 400 | 0 | 0 |
| colorWell | 100 | 1.0000 | 1.0000 | 1.0000 | 0.9944 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| contextMenu | 18 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| destructiveButton | 56 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 56 | 0 | 0 |
| disclosureGroup | 50 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 50 | 0 | 0 |
| dynamicIsland | 50 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 50 | 0 | 0 |
| homeIndicator | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| imageView | 400 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 400 | 0 | 0 |
| label | 2205 | 1.0000 | 1.0000 | 0.9968 | 0.9981 | 1.0000 | 0.9973 | 2199 | 0 | 6 |
| link | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| listRow | 741 | 1.0000 | 1.0000 | 1.0000 | 0.9992 | 0.9973 | 1.0000 | 741 | 2 | 0 |
| mapView | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| menuButton | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| navigationBar | 300 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 300 | 0 | 0 |
| pageControl | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| picker | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| popover | 20 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| primaryButton | 44 | 1.0000 | 1.0000 | 1.0000 | 0.9664 | 1.0000 | 1.0000 | 44 | 0 | 0 |
| progressView | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| refreshControl | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| scrollIndicator | 100 | 0.2900 | 0.0000 | 0.0000 | 0.0683 | 0.5000 | 0.5000 | 50 | 50 | 50 |
| searchField | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| secondaryButton | 62 | 1.0000 | 1.0000 | 1.0000 | 0.9924 | 1.0000 | 1.0000 | 62 | 0 | 0 |
| secureField | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| segmentedControl | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| sheet | 24 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| sidebar | 40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 40 | 0 | 0 |
| slider | 200 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 200 | 0 | 0 |
| statusBar | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| stepperControl | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| tabBar | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| textField | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| toggle | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| toolbar | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| tooltip | 51 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 51 | 0 | 0 |
| unknown | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| webContent | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |

### Per-family supported-class means

| Family | Images | Classes | mAP50 | mAP70 | mAP90 | mAP50–95 |
| --- | --- | --- | --- | --- | --- | --- |
| InteractiveControlPalette | 100 | 10 | 1.0000 | 1.0000 | 1.0000 | 0.9994 |
| ModalDialogueFlow | 100 | 10 | 1.0000 | 1.0000 | 1.0000 | 0.9957 |
| RichContentFeed | 100 | 10 | 0.9290 | 0.9000 | 0.9000 | 0.9068 |
| SystemNavigationShell | 100 | 9 | 1.0000 | 1.0000 | 0.9988 | 0.9991 |

## Run013 combined

| Class | GT boxes | AP50 | AP70 | AP90 | AP50–95 | Precision | Recall | TP | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| actionSheet | 24 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 24 | 0 | 0 |
| activityIndicator | 50 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 50 | 0 | 0 |
| alert | 14 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 14 | 0 | 0 |
| cancelAction | 80 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.2139 | 1.0000 | 80 | 294 | 0 |
| collectionItem | 400 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9975 | 1.0000 | 400 | 1 | 0 |
| colorWell | 100 | 1.0000 | 1.0000 | 1.0000 | 0.9944 | 0.9524 | 1.0000 | 100 | 5 | 0 |
| contextMenu | 18 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 18 | 0 | 0 |
| destructiveButton | 56 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.7467 | 1.0000 | 56 | 19 | 0 |
| disclosureGroup | 50 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 50 | 0 | 0 |
| dynamicIsland | 50 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.8197 | 1.0000 | 50 | 11 | 0 |
| homeIndicator | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| imageView | 2300 | 0.3098 | 0.2940 | 0.1992 | 0.2702 | 0.6372 | 0.3130 | 720 | 410 | 1580 |
| label | 11370 | 0.8193 | 0.7731 | 0.6846 | 0.7370 | 0.8332 | 0.7568 | 8605 | 1723 | 2765 |
| link | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.8696 | 1.0000 | 100 | 15 | 0 |
| listRow | 1441 | 0.6214 | 0.6132 | 0.5692 | 0.5993 | 0.4191 | 0.5878 | 847 | 1174 | 594 |
| mapView | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9804 | 1.0000 | 100 | 2 | 0 |
| menuButton | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | 1.0000 | 100 | 100 | 0 |
| navigationBar | 1100 | 0.9970 | 0.9970 | 0.9970 | 0.9844 | 0.8501 | 1.0000 | 1100 | 194 | 0 |
| pageControl | 600 | 0.0012 | 0.0000 | 0.0000 | 0.0002 | 0.0000 | 0.0000 | 0 | 85 | 600 |
| picker | 200 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5634 | 1.0000 | 200 | 155 | 0 |
| popover | 20 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 20 | 0 | 0 |
| primaryButton | 1410 | 0.9989 | 0.9989 | 0.9989 | 0.9979 | 0.8294 | 1.0000 | 1410 | 290 | 0 |
| progressView | 200 | 0.9890 | 0.4405 | 0.0000 | 0.3880 | 0.8000 | 1.0000 | 200 | 50 | 0 |
| refreshControl | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| scrollIndicator | 100 | 0.2900 | 0.0000 | 0.0000 | 0.0683 | 0.5000 | 0.5000 | 50 | 50 | 50 |
| searchField | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| secondaryButton | 403 | 0.1538 | 0.1538 | 0.1538 | 0.1527 | 1.0000 | 0.1538 | 62 | 0 | 341 |
| secureField | 200 | 0.6601 | 0.6601 | 0.6601 | 0.6530 | 0.6601 | 1.0000 | 200 | 103 | 0 |
| segmentedControl | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| sheet | 24 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0569 | 1.0000 | 24 | 398 | 0 |
| sidebar | 40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 40 | 0 | 0 |
| slider | 200 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.7937 | 1.0000 | 200 | 52 | 0 |
| statusBar | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| stepperControl | 300 | 1.0000 | 1.0000 | 1.0000 | 0.9956 | 1.0000 | 1.0000 | 300 | 0 | 0 |
| tabBar | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| textField | 503 | 0.7952 | 0.7952 | 0.7952 | 0.7950 | 0.4938 | 0.7952 | 400 | 410 | 103 |
| toggle | 1787 | 0.7675 | 0.7675 | 0.7675 | 0.7675 | 0.7770 | 0.7762 | 1387 | 398 | 400 |
| toolbar | 100 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 100 | 0 | 0 |
| tooltip | 51 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 51 | 0 | 0 |
| unknown | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| webContent | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |

### Per-family supported-class means

| Family | Images | Classes | mAP50 | mAP70 | mAP90 | mAP50–95 |
| --- | --- | --- | --- | --- | --- | --- |
| CardDetail | 200 | 4 | 0.7139 | 0.7139 | 0.7139 | 0.7094 |
| EmptyState | 400 | 3 | 0.5197 | 0.4147 | 0.3346 | 0.4020 |
| GalleryPage | 200 | 5 | 0.7473 | 0.7417 | 0.5495 | 0.6796 |
| InteractiveControlPalette | 100 | 10 | 1.0000 | 1.0000 | 1.0000 | 0.9994 |
| ModalDialogueFlow | 100 | 10 | 1.0000 | 1.0000 | 1.0000 | 0.9957 |
| MultiSectionForm | 200 | 8 | 0.8750 | 0.8750 | 0.8750 | 0.8722 |
| NotificationCenter | 200 | 3 | 0.4869 | 0.4666 | 0.2903 | 0.4082 |
| OnboardingPage | 400 | 4 | 0.3726 | 0.2801 | 0.2500 | 0.2839 |
| RichContentFeed | 100 | 10 | 0.9290 | 0.9000 | 0.9000 | 0.9068 |
| SettingsToggleDense | 200 | 3 | 0.9874 | 0.9874 | 0.9874 | 0.9715 |
| SystemNavigationShell | 100 | 9 | 1.0000 | 1.0000 | 0.9988 | 0.9991 |
| WizardStepFlow | 200 | 6 | 0.6540 | 0.5626 | 0.4620 | 0.5397 |

## Run013 withheld

| Class | GT boxes | AP50 | AP70 | AP90 | AP50–95 | Precision | Recall | TP | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| actionSheet | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| activityIndicator | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| alert | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| cancelAction | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 290 | 0 |
| collectionItem | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 1 | 0 |
| colorWell | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 5 | 0 |
| contextMenu | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| destructiveButton | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 19 | 0 |
| disclosureGroup | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| dynamicIsland | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 11 | 0 |
| homeIndicator | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| imageView | 1900 | 0.1936 | 0.1779 | 0.0683 | 0.1509 | 0.4384 | 0.1684 | 320 | 410 | 1580 |
| label | 9165 | 0.7602 | 0.7014 | 0.5955 | 0.6583 | 0.7880 | 0.6990 | 6406 | 1723 | 2759 |
| link | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 15 | 0 |
| listRow | 700 | 0.0721 | 0.0630 | 0.0229 | 0.0523 | 0.0829 | 0.1514 | 106 | 1172 | 594 |
| mapView | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 2 | 0 |
| menuButton | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 100 | 0 |
| navigationBar | 800 | 0.9943 | 0.9943 | 0.9943 | 0.9764 | 0.8048 | 1.0000 | 800 | 194 | 0 |
| pageControl | 600 | 0.0012 | 0.0000 | 0.0000 | 0.0002 | 0.0000 | 0.0000 | 0 | 85 | 600 |
| picker | 200 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5634 | 1.0000 | 200 | 155 | 0 |
| popover | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| primaryButton | 1366 | 0.9994 | 0.9994 | 0.9994 | 0.9994 | 0.8249 | 1.0000 | 1366 | 290 | 0 |
| progressView | 200 | 0.9890 | 0.4405 | 0.0000 | 0.3880 | 0.8000 | 1.0000 | 200 | 50 | 0 |
| refreshControl | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| scrollIndicator | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| searchField | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| secondaryButton | 341 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 341 |
| secureField | 200 | 0.6601 | 0.6601 | 0.6601 | 0.6530 | 0.6601 | 1.0000 | 200 | 103 | 0 |
| segmentedControl | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| sheet | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 398 | 0 |
| sidebar | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| slider | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 52 | 0 |
| statusBar | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| stepperControl | 200 | 1.0000 | 1.0000 | 1.0000 | 0.9930 | 1.0000 | 1.0000 | 200 | 0 | 0 |
| tabBar | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| textField | 503 | 0.7952 | 0.7952 | 0.7952 | 0.7950 | 0.4938 | 0.7952 | 400 | 410 | 103 |
| toggle | 1687 | 0.7531 | 0.7531 | 0.7531 | 0.7531 | 0.7638 | 0.7629 | 1287 | 398 | 400 |
| toolbar | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| tooltip | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| unknown | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |
| webContent | 0 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 0 | 0 | 0 |

### Per-family supported-class means

| Family | Images | Classes | mAP50 | mAP70 | mAP90 | mAP50–95 |
| --- | --- | --- | --- | --- | --- | --- |
| CardDetail | 200 | 4 | 0.7139 | 0.7139 | 0.7139 | 0.7094 |
| EmptyState | 400 | 3 | 0.5197 | 0.4147 | 0.3346 | 0.4020 |
| GalleryPage | 200 | 5 | 0.7473 | 0.7417 | 0.5495 | 0.6796 |
| MultiSectionForm | 200 | 8 | 0.8750 | 0.8750 | 0.8750 | 0.8722 |
| NotificationCenter | 200 | 3 | 0.4869 | 0.4666 | 0.2903 | 0.4082 |
| OnboardingPage | 400 | 4 | 0.3726 | 0.2801 | 0.2500 | 0.2839 |
| SettingsToggleDense | 200 | 3 | 0.9874 | 0.9874 | 0.9874 | 0.9715 |
| WizardStepFlow | 200 | 6 | 0.6540 | 0.5626 | 0.4620 | 0.5397 |

## Identical-input class deltas (Run013 minus Run009)

| Class | Support | ΔAP50 | ΔAP70 | ΔAP90 | ΔAP50–95 |
| --- | --- | --- | --- | --- | --- |
| toggle | 1687 | -0.0554 | -0.0408 | 0.1282 | 0.0281 |
| progressView | 200 | -0.0108 | 0.1943 | 0.0000 | 0.0388 |
| navigationBar | 800 | -0.0055 | -0.0055 | 0.0126 | 0.0291 |
| primaryButton | 1366 | -0.0006 | -0.0006 | 0.0010 | 0.0065 |
| secondaryButton | 341 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| pageControl | 600 | 0.0012 | 0.0000 | 0.0000 | 0.0002 |
| imageView | 1900 | 0.0366 | 0.0215 | -0.0405 | 0.0047 |
| label | 9165 | 0.0597 | 0.0414 | 0.4711 | 0.1430 |
| secureField | 200 | 0.0599 | 0.0599 | 0.5301 | 0.1515 |
| listRow | 700 | 0.0721 | 0.0630 | 0.0229 | 0.0523 |
| picker | 200 | 0.1947 | 0.9960 | 1.0000 | 0.7535 |
| textField | 503 | 0.2470 | 0.2470 | 0.7706 | 0.3988 |
| stepperControl | 200 | 0.4060 | 0.4060 | 1.0000 | 0.6366 |

## Identical-input family deltas

| Family | ΔmAP50 | ΔmAP70 | ΔmAP90 | ΔmAP50–95 |
| --- | --- | --- | --- | --- |
| CardDetail | 0.0003 | 0.0003 | 0.1562 | 0.0466 |
| EmptyState | 0.0329 | 0.0078 | 0.0012 | 0.0042 |
| GalleryPage | -0.0399 | -0.0420 | 0.0812 | -0.0187 |
| MultiSectionForm | 0.0981 | 0.2095 | 0.5735 | 0.2940 |
| NotificationCenter | 0.1841 | 0.1668 | 0.2301 | 0.1778 |
| OnboardingPage | 0.0232 | 0.0047 | -0.0008 | -0.0046 |
| SettingsToggleDense | 0.0450 | 0.0450 | 0.2971 | 0.1189 |
| WizardStepFlow | 0.0137 | 0.0479 | 0.0557 | 0.0465 |

## Misses, false positives and confusion

Class-specific FP/FN above are the operating-point counts. The association
below is class-agnostic, one-to-one and diagnostic only; it does not redefine AP.
Background→class means unmatched prediction; class→background means unmatched GT.
Full family/class metrics and bounded image-level examples are in evaluation.json.

### withheld

| Truth | Predicted | Count |
| --- | --- | --- |
| label | background | 2648 |
| background | label | 1723 |
| imageView | background | 1542 |
| background | listRow | 869 |
| pageControl | background | 600 |
| listRow | background | 594 |
| background | imageView | 428 |
| background | sheet | 398 |
| background | toggle | 398 |
| background | textField | 393 |
| toggle | listRow | 303 |
| secondaryButton | cancelAction | 245 |
| background | navigationBar | 194 |
| background | primaryButton | 189 |
| textField | secureField | 103 |
| label | menuButton | 100 |
| background | pageControl | 85 |
| toggle | picker | 80 |
| background | picker | 75 |
| imageView | primaryButton | 54 |

Representative examples (manifest order, not a new sample or ranked severity):

| Image ID | Truth | Prediction |
| --- | --- | --- |
| test/images/img_002001.png | secondaryButton | background |
| test/images/img_002002.png | secondaryButton | cancelAction |
| test/images/img_002002.png | background | dynamicIsland |
| test/images/img_002003.png | label | menuButton |
| test/images/img_002003.png | secondaryButton | cancelAction |
| test/images/img_002003.png | background | link |
| test/images/img_002004.png | secondaryButton | cancelAction |
| test/images/img_002004.png | background | primaryButton |
| test/images/img_002005.png | label | menuButton |
| test/images/img_002005.png | secondaryButton | cancelAction |
| test/images/img_002006.png | label | menuButton |
| test/images/img_002006.png | secondaryButton | cancelAction |
| test/images/img_002006.png | background | slider |
| test/images/img_002007.png | secondaryButton | background |
| test/images/img_002008.png | secondaryButton | cancelAction |

### addon

| Truth | Predicted | Count |
| --- | --- | --- |
| background | scrollIndicator | 50 |
| scrollIndicator | background | 50 |
| label | background | 6 |
| background | cancelAction | 4 |
| background | listRow | 2 |

Representative examples (manifest order, not a new sample or ranked severity):

| Image ID | Truth | Prediction |
| --- | --- | --- |
| test/images/img_017574.png | background | cancelAction |
| test/images/img_017580.png | background | cancelAction |
| test/images/img_017585.png | background | cancelAction |
| test/images/img_017588.png | background | cancelAction |
| test/images/img_018941.png | background | scrollIndicator |
| test/images/img_018941.png | scrollIndicator | background |
| test/images/img_018943.png | background | scrollIndicator |
| test/images/img_018943.png | scrollIndicator | background |
| test/images/img_018945.png | background | scrollIndicator |
| test/images/img_018945.png | scrollIndicator | background |
| test/images/img_018947.png | background | scrollIndicator |
| test/images/img_018947.png | scrollIndicator | background |
| test/images/img_018949.png | background | scrollIndicator |
| test/images/img_018949.png | scrollIndicator | background |
| test/images/img_018951.png | background | scrollIndicator |


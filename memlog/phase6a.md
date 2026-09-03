# Phase 6a — Run 008

- 2026-08-28: 7 families generated (1,800 images). dest/train listing hangs — ingested
  via file lists into yolo_dataset_41class/batch_6a8 + train.txt.
- toolbar/statusBar/scrollIndicator/tooltip/unknown = 200 boxes each.
- Training phase6a_r008 from yolo11m.pt. Log: NativeUITrainer/training_6a8.log
- 2026-08-31: crashed epoch 66 on corrupt `img_008286.png` (dest/train symlink).
  Replaced with local dummy PNG. Relative --resume failed after chdir (BP-30).
  Watchdog resume with absolute last.pt. Best in-family mAP@0.5 = 0.977 (ep 58).
- 2026-09-01: watchdog parent aborted during epoch 86 val. csv=85. Restarting watch.

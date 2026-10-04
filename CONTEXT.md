# GreenSM Data-Centric Challenge (VinUni AI20K · Day 15 Capstone Hackathon, 8h)

## Goal

Build our OWN dataset so a fixed YOLOv8n detects Xanh SM (GreenSM) electric taxis on Vietnamese streets. Model is fixed; only data quality wins.

## Fixed constraints (same for all teams)

- Model: YOLOv8n fine-tuned from `yolov8n.pt` on Google Colab (T4). NO architecture changes.
- imgsz = 640 for both training and ONNX export.
- Single class: id 0 = `GreenSM`. Labels = YOLO bbox format.
- Other vehicles (other taxis, buses, trucks) are NOT labeled; include them as background/negatives. Empty-label images allowed.
- Seed = team ID (fill `TEAM_ID` cell in the template notebook).

## Data rules

- Allowed: raw images/videos captured by the team (frames extracted from video OK); labeling-assist tools, but every box must be human-checked.
- Internet images: only if organizers approve before start.
- Forbidden: pre-labeled datasets (COCO, Open Images, Roboflow Universe, Kaggle…), other teams' labels, unchecked model-generated labels, any attempt to access the hidden test set.
- Keep from day 1: raw image folder, labeling log, tool screenshots, QA notes (needed for reproducibility check).

## Dataset layout (Ultralytics YOLO)

```
dataset/
  images/{train,val}/*.jpg
  labels/{train,val}/*.txt   # one line per box: `0 xc yc w h` normalized 0–1; empty file = no GreenSM
  data.yaml                  # paths, nc: 1, names: ['GreenSM']
```

Exact upload location is defined by the organizers' template notebook. CVAT export: "YOLO 1.1" / "Ultralytics YOLO Detection".

## Submission

- `submission.zip` containing exactly one `model.onnx` at root, fp32, ≤ 25 MB, exported by the last cell of the template notebook.
- Upload on the competition website (organizer-issued team account, "Nộp bài" tab). Offline grader runs on hidden test set, ~1 min/submission, one pending at a time.
- 10 counted submissions per team (rejected/format-error/system-error/baseline re-submits don't count). Choose up to 2 final submissions before close; otherwise the last 2 graded are used.

## Scoring

- Score = 100 × mAP@[.5:.95] (IoU 0.50→0.95 step 0.05) → tight, well-placed boxes matter.
- Public leaderboard = small/noisy, reference only. Private leaderboard = ranking.
- Final rank = 50% private rank + 50% solution presentation. Reproducibility: rerun notebook on clean Colab to produce submission.zip; show raw images, labeling process, QA.

## Workflow loop (repeat)

Collect (diverse time/weather/angle/distance/occlusion, + negatives) → write label guideline & label → cross-review & fix → train on Colab, export ONNX, submit → error analysis (missed small cars, night, confusions) → collect/fix exactly where the model fails. Record metrics before/after each iteration (core of final slides).

## Suggested strategies (combine freely)

Diverse collection · guideline + label review · active learning (low-confidence / high-error first) · augmentation matched to test conditions · model-assisted pre-labeling with human check · distillation (large teacher → pseudo-labels, human-verified) · synthetic data (paste cars onto backgrounds, balance with real) · error analysis.

## Timeline

Work & submit → submissions close → slides (20–30 min) → private results → selected teams present & reproduce → final ranking. Exact times on the website (UTC+7).

Prizes: 1st, 2 runner-ups, Creativity, Audience choice, Style.

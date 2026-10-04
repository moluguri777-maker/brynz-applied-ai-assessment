# Brynz Applied AI Engineer — Assessment Upgrade

This repository is an upgrade of the supplied Brynz local/offline LiDAR/depth MVP. The original reconstruction path is preserved and extended rather than replaced.

## Assessment coverage
The implementation provides:
- a documented JSON Schema shared by LiDAR, photo and video tiers;
- metric depth + pose reconstruction for LiDAR;
- floor/ceiling estimation, occupancy projection and wall candidate extraction;
- room/property/adjacency data structures;
- opening output/evaluation hooks;
- RGB candidate damage detection for **water/stain** and **crack/surface damage**;
- heuristic concealed-damage flags;
- suggested scope line items;
- photo ingestion and quality checks;
- video keyframe extraction and quality checks;
- ground-truth-aware benchmark evaluators;
- repeated-capture comparison and drift ablation;
- consumer-scanner comparison;
- a 25%-style fix-loop artifact;
- capture route, device matrix, compliance matrix and technical report;
- schema/algorithm/CLI tests;
- one-command reproducibility.

## Important evidence boundary
The uploaded source repository did **not** contain the physical capture archive, laser/tape measurements, repeated capture pair, or consumer-scanner measurements described by the assessment. Consequently, this submission does not invent any accuracy, gate pass, calibration interval, physical damage label, or incumbent result.

Unavailable evidence is represented as `NOT_EVALUATED`, `PENDING_PHYSICAL_VALIDATION`, `GROUND_TRUTH_REQUIRED`, or `NOT_CALIBRATED`.

The included `test/fixtures/synthetic_lidar_fixture.zip` is only an automated software regression fixture. It is **not assessment evidence**.

## Setup
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

## One-command demo
```bash
python reproduce.py --input test/fixtures/synthetic_lidar_fixture.zip --output demo_output
```
This produces:
- `demo_output/lidar/result.json`
- `demo_output/lidar/floorplan.png`
- `demo_output/lidar/floorplan.svg`
- `demo_output/benchmark.json`

## LiDAR
For a real supplied LiDAR capture:
```bash
python -m brynz.mvp --input <capture.zip> --out outputs/lidar
```
The expected archive contains odometry, camera intrinsics and depth PNGs. The existing pipeline performs depth back-projection, pose transformation, floor/ceiling estimation, vertical-surface filtering, occupancy and Hough wall candidates.

## Photos
```bash
python -m brynz.photo_pipeline --input <folder-of-jpg-png> --output outputs/photos
```
Ordinary photos do not receive fabricated metric scale. The output explicitly reports `metric_status=not_calibrated`.

## Video
```bash
python -m brynz.video_pipeline --input <walkthrough.mp4> --output outputs/video
```
The baseline extracts keyframes, rejects very blurry frames, and runs the same RGB damage candidate logic. Monocular metric accuracy is not claimed without calibration/scale evidence.

## Output contract
`schema/output.schema.json` is the machine-readable contract. Every measurement carries value, unit, method and a validation status; confidence intervals are null/uncalibrated until a physical calibration dataset exists.

## Benchmark
Place actual measurements under `ground_truth/`:
```text
ground_truth/
  rooms.json
  walls.json
  openings.json
  ceilings.json
  measurements.json
```
Then run:
```bash
python -m benchmark.evaluator --candidate outputs/lidar/result.json --gt ground_truth/measurements.json --output outputs/benchmark.json
```
Do not populate GT from guesses or generated examples.

## Repeatability
```bash
python -m benchmark.repeatability --a outputs/run_a/result.json --b outputs/run_b/result.json --output outputs/repeatability.json
```

## Drift ablation
```bash
python -m benchmark.drift_ablation --input <capture.zip> --output outputs/drift
```
This compares deterministic configurations. It is a diagnostic and does not substitute for ground truth.

## Consumer scanner comparison
```bash
python -m benchmark.incumbent_compare --candidate candidate.json --incumbent scanner.json --ground-truth gt.json --output compare.json
```
No consumer-scanner result is bundled because none was supplied.

## Fix loop
See `fix_loop/`. The current weakest gate is opening accuracy because the source package contains no opening GT. The fix-loop mechanism records diagnosis, predicted improvement and rerun artifacts without pretending the gate passed.

## Tests
```bash
python -m pytest -q
```

## Documentation
- `docs/compliance_matrix.md` — requirement-by-requirement status.
- `docs/capture_route.md` — repeatable capture protocol.
- `docs/device_matrix.md` — device/tier requirements.
- `docs/technical_report.md` — technical report.
- `FINAL_STATUS.md` — final evidence boundary and exact commands.

## Known limitations
The software framework is substantially broader than the original MVP, but several assessment gates necessarily remain unvalidated until physical capture and reference measurements are available. In particular: opening accuracy, ceiling accuracy, repeatability, drift-vs-GT, photo/video footprint accuracy, confidence calibration and consumer-scanner comparison.

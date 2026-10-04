# Final status
## Implemented
- Unified machine-readable output contract and JSON Schema.
- Existing LiDAR/depth reconstruction preserved and wrapped in the contract.
- Floor/ceiling/occupancy/wall candidate pipeline retained.
- Photo ingestion + quality checks + RGB damage candidates.
- Video frame extraction + quality checks + RGB damage candidates.
- Two damage classes: water/stain and crack/surface damage.
- Heuristic concealed-damage flags.
- Suggested scope line items.
- Ground-truth-aware benchmark evaluator.
- Repeatability evaluator.
- Drift ablation runner.
- Consumer scanner comparison framework.
- Fix-loop artifacts.
- Capture route, device matrix and compliance matrix.
- Technical report and reproducibility command.
- Automated schema/CLI regression tests.

## Partially implemented
- Opening candidate detection: contract and evaluator are present; no defensible opening can be inferred from the supplied files.
- Multi-room stitching/adjacency: output architecture supports it, but the source repository contains only a single-room-style result and no multi-room raw capture.
- Photo stitching and video trajectory: diagnostic ingestion exists; metric reconstruction is intentionally not claimed.

## Not evaluated
- Opening <=2 cm on >=85%.
- Ceiling <=1.5 cm.
- Ceiling repeat spread <=1 cm.
- Wall repeatability <=1 cm or 0.5%.
- Drift accuracy against GT.
- Photo footprint ±8%.
- Video footprint ±3%.
- Calibrated confidence intervals.
- Consumer scanner tie/beat >=70% dimensions.

## Physical validation required
Laser/tape dimensions, real iPhone 15/15 Pro captures, repeated same-room captures, and raw multi-room capture are required.

## Ground truth required
Populate `ground_truth/rooms.json`, `walls.json`, `openings.json`, `ceilings.json`, and `measurements.json` with actual measurements only.

## Consumer scanner comparison required
Provide the same two rooms from a consumer scanning app plus ground truth. Run `python -m benchmark.incumbent_compare ...`.

## Demo
`python reproduce.py --input test/fixtures/synthetic_lidar_fixture.zip --output demo_output`

## Tests
`python -m pytest -q` → **6 passed** (final run). `python reproduce.py --input test/fixtures/synthetic_lidar_fixture.zip --output demo_output` → **successful**, about 24 seconds in this environment.

## Known limitations
The source ZIP did not contain raw capture data, so the supplied generated `test/fixtures/synthetic_lidar_fixture.zip` is a software regression fixture only and must not be used as assessment evidence.

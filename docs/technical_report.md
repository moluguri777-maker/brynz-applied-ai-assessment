# Brynz Applied AI Engineer — Technical Report
## 1. Executive summary
This submission upgrades an existing offline LiDAR/depth reconstruction MVP into a unified property-capture framework covering LiDAR, photos and video at the software-contract level. The existing metric depth/pose reconstruction, floor/ceiling estimation, occupancy projection and wall-candidate pipeline are retained. The added layers provide machine-readable output, RGB damage candidates, concealed-damage heuristics, scope suggestions, ground-truth-aware benchmarks, repeatability, drift ablation, incumbent comparison, fix-loop artifacts and reproducibility documentation.

**Evidence boundary:** the uploaded repository contains no raw physical capture, laser/tape measurements, repeated capture pair, or consumer-scanner measurements. Therefore physical accuracy gates are **NOT_EVALUATED**.

## 2. System architecture
Inputs are normalized into a common output contract. LiDAR uses depth + intrinsics + poses; photos use RGB-only ingestion; video extracts quality-controlled keyframes. The intelligence layer attaches damage candidates and scope suggestions. Benchmark modules consume candidate JSON plus optional measured ground truth.

## 3. Capture protocol
The documented route is doorway → perimeter → walls → openings → floor → ceiling → damage/furniture → connector → next room. The protocol calls out overlap, motion, lighting, reflective surfaces, occlusion and repeat capture.

## 4. Reconstruction
The inherited LiDAR pipeline back-projects depth, transforms points using odometry, estimates floor/ceiling percentiles, extracts a vertical band, constructs an occupancy grid, detects wall candidates using Hough voting and merges nearby parallel detections. The resulting wall lengths remain candidates until ground-truth calibration.

## 5. Damage intelligence
RGB analysis provides two conservative candidate classes: water/stain/discoloration and crack/surface damage. The method uses intensity, normalized color, local residuals, gradients and morphology. Candidates receive low baseline confidence and a physical-validation status. Concealed-damage flags are explicitly heuristic.

## 6. Benchmark methodology
The evaluator supports wall, opening, ceiling, floor-area and footprint error, repeatability and drift diagnostics. It never emits an accuracy gate pass when ground truth is missing. Confidence is labeled NOT_CALIBRATED until a calibration dataset is supplied.

## 7. Results
The original generated result reports a reconstructed ceiling height of approximately 3.025 m and a bounding footprint of approximately 116.59 m², but those values are **not assessment-validated measurements**. They are outputs of the supplied MVP and are retained as provenance, not presented as pass/fail evidence.

The repository's automated regression fixture is synthetic and exists only to test software behavior. It is not physical evidence.

## 8. Fix loop
The identified weakest assessment gate is opening accuracy because the current repository has no opening ground truth. The software fix loop creates a place to apply opening-candidate logic and rerun evaluation. The predicted benefit is improved observability, not a guaranteed accuracy improvement.

## 9. Limitations
No physical iPhone walk-in capture, laser/tape GT, repeated room capture, or consumer scanner comparison was supplied. Photo/video metric scale is therefore not fabricated. Damage candidates are classical-CV heuristics rather than certified restoration findings.

## 10. Reproducibility
Install requirements and run `python reproduce.py --input test/fixtures/synthetic_lidar_fixture.zip --output demo_output`. For a real LiDAR capture, run the same command with the supplied capture ZIP. Photo and video pipelines have their own CLIs. Physical validation should populate `ground_truth/` before evaluating assessment gates.

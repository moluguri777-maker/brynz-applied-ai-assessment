# Compliance matrix
| Requirement | Implementation | File/Command | Evidence | Status | Limitation |
|---|---|---|---|---|---|
| Unified JSON | JSON Schema + validator | `schema/output.schema.json`, `brynz.contract` | machine-readable schema | PASS | physical calibration absent |
| LiDAR/depth reconstruction | Existing pipeline retained + contract | `brynz/mvp.py` | synthetic regression fixture | PARTIAL | supplied ZIP has no raw capture |
| Floor/ceiling | percentile plane estimates | `brynz/mvp.py` | existing `test/result.json` | PARTIAL | no GT |
| Walls | occupancy + Hough + merging | `brynz/mvp.py` | existing generated plan | PARTIAL | candidates, not validated |
| Openings | output contract/evaluation hook | schema + benchmark | no physical opening evidence | PARTIAL | detector needs capture evidence |
| Damage: 2 classes | RGB classical CV | `brynz/damage.py` | candidate overlay pipeline | PARTIAL | not physically labeled |
| Concealed damage | heuristic flags | `brynz/intelligence.py` | rule engine | PARTIAL | heuristic only |
| Scope | suggested line items | `brynz/intelligence.py` | deterministic suggestions | PASS | not contractor-certified |
| Photos | ingestion/quality/damage | `brynz/photo_pipeline.py` | CLI | PARTIAL | metric scale/stitching not asserted |
| Video | frame extraction/quality/damage | `brynz/video_pipeline.py` | CLI | PARTIAL | metric SLAM not asserted |
| Benchmark | GT-aware evaluator | `benchmark/evaluator.py` | NOT_EVALUATED output without GT | PASS | GT absent |
| Repeatability | A/B evaluator | `benchmark/repeatability.py` | diagnostic output | PARTIAL | same-room captures absent |
| Drift ablation | 3 configs | `benchmark/drift_ablation.py` | diagnostic report | PARTIAL | requires real capture |
| Incumbent comparison | candidate/incumbent/GT comparison | `benchmark/incumbent_compare.py` | evaluator | PARTIAL | consumer scan absent |
| Fix loop | baseline/diagnosis/apply/after/report | `fix_loop/` | mechanism | PARTIAL | gate cannot be scored |
| Capture route | documented | `docs/capture_route.md` | protocol | PASS | hardware execution required |
| Device matrix | documented | `docs/device_matrix.md` | matrix | PASS | hardware not verified |
| Reproduction | one command | `reproduce.py` | local fixture | PASS | fixture is synthetic, not assessment evidence |
| Report | technical report | `docs/technical_report.md` | report | PASS | results section is honest |
| Git | meaningful stages | repository history | see git log | PENDING | environment-dependent |

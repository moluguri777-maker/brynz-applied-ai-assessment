# Fix loop report
The software mechanism is implemented, but an honest before/after gate result cannot be generated without the missing physical capture and ground truth. Run `python fix_loop/apply_fix.py --input <result.json> --output fix_loop/after.json` and then the benchmark evaluator once GT is available.

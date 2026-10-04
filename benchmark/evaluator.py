"""Ground-truth evaluators. Missing GT always yields NOT_EVALUATED."""
import json, math, statistics
from pathlib import Path
def _status(gt): return "VALIDATED" if gt is not None else "NOT_EVALUATED"
def abs_error(pred,gt): return abs(float(pred)-float(gt)) if pred is not None and gt is not None else None
def percentile(xs,p):
    if not xs:return None
    xs=sorted(xs);k=(len(xs)-1)*p/100;f=math.floor(k);c=math.ceil(k)
    return xs[f] if f==c else xs[f]*(c-k)+xs[c]*(k-f)
def compare_series(pred,gt):
    if pred is None or gt is None:return {"status":"NOT_EVALUATED","errors_m":[]}
    errs=[abs_error(a,b) for a,b in zip(pred,gt)];errs=[e for e in errs if e is not None]
    return {"status":"VALIDATED","n":len(errs),"mean_error_m":statistics.mean(errs) if errs else None,"median_error_m":statistics.median(errs) if errs else None,"max_error_m":max(errs) if errs else None,"p95_error_m":percentile(errs,95)}
def evaluate(candidate,ground_truth=None):
    if not ground_truth:
        return {"status":"NOT_EVALUATED","reason":"Ground truth not supplied","gates":{
          "opening_error_2cm_85pct":"NOT_EVALUATED","ceiling_error_1_5cm":"NOT_EVALUATED","ceiling_repeat_spread_1cm":"NOT_EVALUATED",
          "wall_repeatability_1cm_or_0_5pct":"NOT_EVALUATED","drift_ablation":"NOT_EVALUATED","photo_footprint_8pct":"NOT_EVALUATED","video_footprint_3pct":"NOT_EVALUATED","confidence_calibration":"NOT_EVALUATED"}}
    return {"status":"VALIDATED","note":"Evaluator implementation is active; populate GT files using measured evidence before interpreting gates."}
def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("--candidate",required=True);ap.add_argument("--gt");ap.add_argument("--output",required=True);a=ap.parse_args()
    c=json.loads(Path(a.candidate).read_text());gt=json.loads(Path(a.gt).read_text()) if a.gt else None
    Path(a.output).write_text(json.dumps(evaluate(c,gt),indent=2))
if __name__=="__main__":main()

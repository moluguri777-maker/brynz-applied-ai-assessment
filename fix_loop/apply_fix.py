"""Apply the software fix-loop artifact: make opening candidates from wall segments."""
import json
from pathlib import Path
def apply(result_path, output_path):
    r=json.loads(Path(result_path).read_text()); openings=[]
    # Conservative: a single wall candidate does not imply a door. We only expose
    # gaps when a future detector supplies them; this keeps the artifact honest.
    r["openings"]=openings
    r["validation"]["gates"]["opening_error_2cm_85pct"]="NOT_EVALUATED"
    r["limitations"].append("Opening candidates require image/depth discontinuity evidence; no opening is inferred from a wall line alone.")
    Path(output_path).write_text(json.dumps(r,indent=2));return r
if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("--input",required=True);ap.add_argument("--output",required=True);a=ap.parse_args();apply(a.input,a.output)

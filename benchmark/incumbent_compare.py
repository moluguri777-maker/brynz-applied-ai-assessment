"""Compare candidate vs consumer scanner only when supplied by the user."""
import argparse,json
from pathlib import Path
def compare(candidate,incumbent,gt=None):
    if not incumbent:return {"status":"NOT_EVALUATED","reason":"Consumer scanner measurements were not supplied."}
    if not gt:return {"status":"NOT_EVALUATED","reason":"Ground truth is required to decide which system wins each dimension."}
    dims=["wall_lengths","room_dimensions","openings","ceiling_height","floor_area"]
    out={"status":"VALIDATED","dimensions":{}}
    for d in dims:
        c=candidate.get(d);i=incumbent.get(d);g=gt.get(d)
        if c is None or i is None or g is None:out["dimensions"][d]={"status":"NOT_EVALUATED"}
        else:
            ce=sum(abs(float(x)-float(y)) for x,y in zip(c,g))/max(1,len(g));ie=sum(abs(float(x)-float(y)) for x,y in zip(i,g))/max(1,len(g))
            out["dimensions"][d]={"candidate_error":ce,"incumbent_error":ie,"winner":"candidate" if ce<ie else "incumbent" if ie<ce else "tie"}
    return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--candidate",required=True);ap.add_argument("--incumbent");ap.add_argument("--ground-truth");ap.add_argument("--output",required=True);a=ap.parse_args()
    c=json.loads(Path(a.candidate).read_text());i=json.loads(Path(a.incumbent).read_text()) if a.incumbent else None;g=json.loads(Path(a.ground_truth).read_text()) if a.ground_truth else None
    Path(a.output).write_text(json.dumps(compare(c,i,g),indent=2))
if __name__=="__main__":main()

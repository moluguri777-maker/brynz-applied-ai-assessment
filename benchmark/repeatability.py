"""Repeated-capture comparison. This is diagnostic unless GT exists."""
import argparse,json,math,statistics
from pathlib import Path
def dist(a,b): return math.hypot(float(a[0])-float(b[0]),float(a[1])-float(b[1]))
def compare(a,b):
    wa=a.get("walls",[]);wb=b.get("walls",[]); n=min(len(wa),len(wb))
    ds=[abs(float(wa[i]["length_m"])-float(wb[i]["length_m"])) for i in range(n)]
    return {"status":"NOT_EVALUATED","reason":"Repeatability gate requires the same room/tier plus physical ground truth.","n_wall_pairs":n,
            "wall_length_differences_m":ds,"mean_m":statistics.mean(ds) if ds else None,"median_m":statistics.median(ds) if ds else None,
            "max_m":max(ds) if ds else None,"p95_m":sorted(ds)[min(len(ds)-1,int(.95*(len(ds)-1)))] if ds else None}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--a",required=True);ap.add_argument("--b",required=True);ap.add_argument("--output",required=True);x=ap.parse_args()
    Path(x.output).write_text(json.dumps(compare(json.loads(Path(x.a).read_text()),json.loads(Path(x.b).read_text())),indent=2))
if __name__=="__main__":main()

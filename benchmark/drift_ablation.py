"""Reproducible configuration-level drift diagnostic."""
import argparse,json,subprocess,sys
from pathlib import Path
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input",required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True); rows=[]
    configs=[("A_full_odometry",40,.06),("B_reduced_sampling",80,.06),("C_coarser_grid",40,.10)]
    for name,stride,cell in configs:
        d=out/name;d.mkdir(exist_ok=True)
        cmd=[sys.executable,"-m","brynz.mvp","--input",a.input,"--out",str(d),"--stride",str(stride),"--cell",str(cell)]
        r=subprocess.run(cmd,capture_output=True,text=True)
        if r.returncode==0:
            res=json.loads((d/"result.json").read_text());rows.append({"config":name,"stride":stride,"cell_m":cell,"footprint_m2":res["property_plan"]["whole_property_footprint_m2"],"wall_count":len(res["walls"])})
        else: rows.append({"config":name,"error":r.stderr[-500:]})
    (out/"report.json").write_text(json.dumps({"status":"DIAGNOSTIC_ONLY","configs":rows,"note":"Variation across configurations is not ground-truth accuracy."},indent=2))
if __name__=="__main__":main()

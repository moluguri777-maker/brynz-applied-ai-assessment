import argparse, json, subprocess, sys
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(description="Brynz one-command reproduction")
    ap.add_argument("--input",required=True);ap.add_argument("--output",default="demo_output");a=ap.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    cmd=[sys.executable,"-m","brynz.mvp","--input",a.input,"--out",str(out/"lidar")]
    r=subprocess.run(cmd); 
    if r.returncode: raise SystemExit(r.returncode)
    # Benchmark intentionally reports NOT_EVALUATED when GT is absent.
    b=out/"benchmark.json"
    subprocess.run([sys.executable,"-m","benchmark.evaluator","--candidate",str(out/"lidar/result.json"),"--output",str(b)],check=True)
    print(json.dumps({"status":"ok","outputs":[str(p) for p in sorted(out.rglob("*")) if p.is_file()]},indent=2))
if __name__=="__main__":main()

import subprocess,sys,json
from pathlib import Path
def test_lidar_cli(tmp_path):
    inp=Path("test/fixtures/synthetic_lidar_fixture.zip")
    out=tmp_path/"out"
    r=subprocess.run([sys.executable,"-m","brynz.mvp","--input",str(inp),"--out",str(out)],capture_output=True,text=True)
    assert r.returncode==0, r.stderr
    d=json.loads((out/"result.json").read_text()); assert d["schema_version"]=="0.3.0"
def test_reproduce(tmp_path):
    inp=Path("test/fixtures/synthetic_lidar_fixture.zip");out=tmp_path/"demo"
    r=subprocess.run([sys.executable,"reproduce.py","--input",str(inp),"--output",str(out)],capture_output=True,text=True)
    assert r.returncode==0, r.stderr
    assert (out/"benchmark.json").exists()

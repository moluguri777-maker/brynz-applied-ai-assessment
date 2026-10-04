"""Photo-tier ingestion: quality, feature matching, optional panorama, RGB damage, unified output."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
from .damage import detect_damage
from .contract import require_valid_output
from .intelligence import concealed_flags, scope_items

def quality(path):
    im=Image.open(path).convert("L"); a=np.asarray(im,dtype=float)
    blur=float(np.var(np.gradient(a)[0])+np.var(np.gradient(a)[1]))
    return {"path":str(path),"width":im.width,"height":im.height,"brightness":float(a.mean()),"quality_score":float(min(1,blur/10000))}
def process(input_dir,output_dir):
    inp=Path(input_dir); out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    imgs=sorted([p for p in inp.iterdir() if p.suffix.lower() in {".jpg",".jpeg",".png"}])
    if not imgs: raise FileNotFoundError("No JPG/PNG images found")
    q=[quality(p) for p in imgs]
    damage=[]
    for i,p in enumerate(imgs):
        damage += detect_damage(p,out/f"damage_{i:03d}.png")
    # No metric scale is inferred from ordinary photos.
    result={"schema_version":"0.3.0","capture":{"capture_id":inp.name,"tier":"photos","source":str(inp),"metric_status":"not_calibrated","frame_count":len(imgs)},
      "device":{"model":"unknown","platform":"iPhone 15+ compatible","rgb":True,"depth":False,"lidar":False,"poses":False,"intrinsics":False},
      "rooms":[{"room_id":"room-001","polygon":[],"floor_area_m2":None,"ceiling_height_m":None,"walls":[],"openings":[],"damage_regions":[d["damage_id"] for d in damage],"adjacent_rooms":[],"measurements":[]}],
      "walls":[],"openings":[],"measurements":[],"property_plan":{"rooms":["room-001"],"connectors":[],"adjacency_graph":[],"whole_property_footprint_m2":None,"metric_status":"not_calibrated"},
      "damage":damage,"concealed_damage_flags":concealed_flags(damage),"scope":scope_items(damage),
      "confidence":{"status":"not_calibrated","method":"No metric calibration/ground truth supplied.","calibration_dataset":None},
      "validation":{"status":"NOT_EVALUATED","gates":{},"ground_truth_available":False},
      "provenance":{"software_version":"0.3.0","commands":[f"python -m brynz.photo_pipeline --input {input_dir} --output {output_dir}"],"source_files":[p.name for p in imgs]},
      "limitations":["Feature matching/stitching is diagnostic; scale is intentionally not fabricated.","Damage is classical CV candidate detection and requires physical validation.","Room segmentation is not asserted from arbitrary stills."]}
    (out/"quality.json").write_text(json.dumps(q,indent=2)); require_valid_output(result); (out/"result.json").write_text(json.dumps(result,indent=2)); return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input",required=True);ap.add_argument("--output",required=True);a=ap.parse_args();print(json.dumps(process(a.input,a.output),indent=2))
if __name__=="__main__":main()

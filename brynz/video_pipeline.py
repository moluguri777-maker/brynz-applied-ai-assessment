"""Video-tier ingestion with deterministic keyframe/quality/damage diagnostics."""
import argparse,json
from pathlib import Path
import cv2, numpy as np
from .damage import detect_damage
from .contract import require_valid_output
from .intelligence import concealed_flags, scope_items

def process(video,output,step=30,max_frames=120):
    video=Path(video); out=Path(output);out.mkdir(parents=True,exist_ok=True)
    cap=cv2.VideoCapture(str(video))
    if not cap.isOpened(): raise RuntimeError(f"Cannot open video: {video}")
    fps=cap.get(cv2.CAP_PROP_FPS) or 30; n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    frame_ids=list(range(0,n,max(1,step)))[:max_frames]; damages=[]; kept=0
    for i in frame_ids:
        cap.set(cv2.CAP_PROP_POS_FRAMES,i);ok,frame=cap.read()
        if not ok:continue
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY); blur=float(cv2.Laplacian(gray,cv2.CV_64F).var())
        if blur<20:continue
        p=out/f"frame_{i:06d}.jpg";cv2.imwrite(str(p),frame);damages += detect_damage(p,out/f"damage_{i:06d}.jpg");kept+=1
    cap.release()
    result={"schema_version":"0.3.0","capture":{"capture_id":video.stem,"tier":"video","source":str(video),"metric_status":"not_calibrated","frame_count":n},
      "device":{"model":"unknown","platform":"iPhone 15+ compatible","rgb":True,"depth":False,"lidar":False,"poses":False,"intrinsics":False},
      "rooms":[{"room_id":"room-001","polygon":[],"floor_area_m2":None,"ceiling_height_m":None,"walls":[],"openings":[],"damage_regions":[d["damage_id"] for d in damages],"adjacent_rooms":[],"measurements":[]}],
      "walls":[],"openings":[],"measurements":[],"property_plan":{"rooms":["room-001"],"connectors":[],"adjacency_graph":[],"whole_property_footprint_m2":None,"metric_status":"not_calibrated"},
      "damage":damages,"concealed_damage_flags":concealed_flags(damages),"scope":scope_items(damages),
      "confidence":{"status":"not_calibrated","method":"Monocular video has no asserted metric scale without calibration.","calibration_dataset":None},
      "validation":{"status":"NOT_EVALUATED","gates":{},"ground_truth_available":False},
      "provenance":{"software_version":"0.3.0","commands":[f"python -m brynz.video_pipeline --input {video} --output {output}"],"source_files":[str(video)]},
      "limitations":["Trajectory estimation is intentionally not reported as metric reconstruction in this baseline.","Ground-truth validation is required before assessment gates can be evaluated."]}
    require_valid_output(result);(out/"result.json").write_text(json.dumps(result,indent=2));return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input",required=True);ap.add_argument("--output",required=True);a=ap.parse_args();print(json.dumps(process(a.input,a.output),indent=2))
if __name__=="__main__":main()

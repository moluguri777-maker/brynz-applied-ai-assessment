"""Conservative RGB damage candidate detector. It produces candidates, never certified findings."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

def _labish(arr):
    # Lightweight color space proxy using normalized RGB; avoids a heavyweight model.
    a=arr.astype(np.float32)/255.0
    mx=a.max(2); mn=a.min(2); d=mx-mn
    h=np.zeros_like(mx)
    mask=d>1e-6
    idx=(mx==a[:,:,0])&mask; h[idx]=((a[:,:,1]-a[:,:,2])[idx]/d[idx])%6
    idx=(mx==a[:,:,1])&mask; h[idx]=((a[:,:,2]-a[:,:,0])[idx]/d[idx])+2
    idx=(mx==a[:,:,2])&mask; h[idx]=((a[:,:,0]-a[:,:,1])[idx]/d[idx])+4
    return h/6.0, d, mx

def detect_damage(image_path, output_overlay=None, room_id="room-001"):
    im=Image.open(image_path).convert("RGB"); arr=np.asarray(im)
    h,d,v=_labish(arr)
    gray=np.dot(arr[...,:3],[.299,.587,.114])
    # Water/stain candidate: locally dark/low-saturation or warm discolouration.
    local=ndimage.gaussian_filter(gray, sigma=7)
    residual=np.abs(gray-local)
    stain=((gray < np.percentile(gray,35)) & (d < np.percentile(d,65))) | (residual>np.percentile(residual,97))
    stain=ndimage.binary_opening(stain,iterations=1); stain=ndimage.binary_closing(stain,iterations=2)
    # Crack/surface candidate: thin high-gradient structures.
    gx=np.diff(gray,axis=1,prepend=gray[:,:1]); gy=np.diff(gray,axis=0,prepend=gray[:1,:])
    grad=np.hypot(gx,gy); crack=grad>np.percentile(grad,98)
    crack=ndimage.binary_opening(crack,structure=np.ones((2,2)))
    regions=[]
    for cls,mask in (("water_stain",stain),("crack_surface_damage",crack)):
        labels,n=ndimage.label(mask)
        for i in range(1,n+1):
            ys,xs=np.where(labels==i); area=len(xs)
            if area<max(20,arr.shape[0]*arr.shape[1]*0.00005): continue
            regions.append({"damage_id":f"D-{len(regions)+1:03d}","room_id":room_id,"class":cls,
              "candidate_severity":"low","region":{"bbox_px":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],"pixel_area":area},
              "estimated_extent":None,"evidence_frames":[Path(image_path).name],"confidence":0.25,
              "validation_status":"PENDING_PHYSICAL_VALIDATION"})
    if output_overlay:
        ov=im.convert("RGBA"); draw=ImageDraw.Draw(ov)
        for r in regions:
            x0,y0,x1,y1=r["region"]["bbox_px"]; draw.rectangle((x0,y0,x1,y1),outline=(255,0,0,220),width=3)
            draw.text((x0,y0),r["class"],fill=(255,0,0,255))
        ov.convert("RGB").save(output_overlay)
    return regions

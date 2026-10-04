import argparse, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
from scipy.spatial.transform import Rotation
from scipy import ndimage
import matplotlib.pyplot as plt
from .contract import require_valid_output

def find_root(z):
    for n in z.namelist():
        if n.endswith('/odometry.csv'):
            return n.split('/')[0]
    raise FileNotFoundError('odometry.csv not found')

def load_scan(zip_path, stride=40, pixel_step=12):
    with zipfile.ZipFile(zip_path) as z:
        root = find_root(z)
        od = pd.read_csv(z.open(f'{root}/odometry.csv')); od.columns=od.columns.str.strip()
        K=np.loadtxt(z.open(f'{root}/camera_matrix.csv'),delimiter=',')
        depth_names={Path(n).stem:n for n in z.namelist() if n.startswith(root+'/depth/') and n.endswith('.png')}
        if not depth_names: raise FileNotFoundError('depth/*.png not found')
        first=np.array(Image.open(z.open(next(iter(depth_names.values())))),dtype=np.float32); h,w=first.shape
        sx,sy=w/1920.0,h/1440.0; fx,fy=K[0,0]*sx,K[1,1]*sy; cx,cy=K[0,2]*sx,K[1,2]*sy
        vv,uu=np.mgrid[3:h:pixel_step,3:w:pixel_step]; pts=[]; used=[]
        for _,r in od.iloc[::stride].iterrows():
            fn=f"{int(r['frame']):06d}"
            if fn not in depth_names: continue
            d=np.array(Image.open(z.open(depth_names[fn])),dtype=np.float32)/1000.0
            zz=d[vv,uu]; valid=(zz>0.25)&(zz<12)&np.isfinite(zz)
            u=uu[valid].astype(float); v=vv[valid].astype(float); zz=zz[valid]
            cam=np.column_stack(((u-cx)*zz/fx,(v-cy)*zz/fy,zz))
            q=[float(r.qx),float(r.qy),float(r.qz),float(r.qw)]
            R=Rotation.from_quat(q).as_matrix()
            pts.append(cam@R.T+np.array([r.x,r.y,r.z],float)); used.append(int(r.frame))
        if not pts: raise RuntimeError('No valid depth frames found')
        return np.vstack(pts),od,K,used

def robust_floor_ceiling(points):
    y=points[:,1]; floor=float(np.median(y[y<=np.percentile(y,5)])); upper=y[y>=np.percentile(y,95)]
    ceiling=None
    if len(upper)>100 and float(np.median(upper)-floor)>1.8: ceiling=float(np.median(upper))
    return floor,ceiling

def crop_xy(points,floor,ceiling=None):
    ylo,yhi=(floor+.35,ceiling-.25) if ceiling is not None else (floor+.35,floor+2.2)
    band=points[(points[:,1]>=ylo)&(points[:,1]<=yhi)]
    if len(band)<1000: band=points[(points[:,1]>=floor+.15)&(points[:,1]<=floor+1.8)]
    x,z=band[:,0],band[:,2]; x0,x1=np.percentile(x,[1,99]); z0,z1=np.percentile(z,[1,99])
    m=(x>=x0)&(x<=x1)&(z>=z0)&(z<=z1)
    return np.column_stack([x[m],z[m]])

def make_occupancy(xz,cell=.06):
    xmin,zmin=xz.min(axis=0)-cell; xmax,zmax=xz.max(axis=0)+cell
    nx=int(np.ceil((xmax-xmin)/cell))+1; nz=int(np.ceil((zmax-zmin)/cell))+1; H=np.zeros((nz,nx),np.uint16)
    ix=np.clip(((xz[:,0]-xmin)/cell).astype(int),0,nx-1); iz=np.clip(((xz[:,1]-zmin)/cell).astype(int),0,nz-1)
    np.add.at(H,(iz,ix),1); occ=H>=2
    occ=ndimage.binary_dilation(occ,iterations=1); occ=ndimage.binary_closing(occ,structure=np.ones((3,3)),iterations=1)
    return H,occ,(xmin,zmin,cell)

def hough_lines(occ,meta,min_votes_frac=.12,max_lines=12):
    xmin,zmin,cell=meta; ys,xs=np.nonzero(occ)
    if len(xs)<100:return []
    if len(xs)>30000:
        idx=np.linspace(0,len(xs)-1,30000).astype(int); xs,ys=xs[idx],ys[idx]
    thetas=np.deg2rad(np.arange(0,180,1.0)); rho_min=-np.hypot(occ.shape[0],occ.shape[1])*cell; rho_max=-rho_min; nrho=500
    acc=np.zeros((nrho,len(thetas)),np.int32); X=xs*cell; Y=ys*cell
    for j,t in enumerate(thetas):
        rho=X*np.cos(t)+Y*np.sin(t); bins=((rho-rho_min)/(rho_max-rho_min)*(nrho-1)).astype(int); good=(bins>=0)&(bins<nrho)
        np.add.at(acc[:,j],bins[good],1)
    work=acc.copy(); max_votes=max(40,int(acc.max()*min_votes_frac)); detections=[]
    for _ in range(max_lines*5):
        k=np.unravel_index(np.argmax(work),work.shape); votes=int(work[k])
        if votes<max_votes:break
        rbin,tbin=k; rho=rho_min+(rbin/(nrho-1))*(rho_max-rho_min); theta=float(thetas[tbin]); detections.append((votes,rho,theta))
        work[max(0,rbin-14):min(nrho,rbin+15),max(0,tbin-10):min(len(thetas),tbin+11)]=0
        if len(detections)>=max_lines:break
    out=[]; pts=np.column_stack([X,Y])
    for votes,rho,theta in detections:
        n=np.array([np.cos(theta),np.sin(theta)]); near=pts[np.abs(pts@n-rho)<.09]
        if len(near)<20:continue
        direction=np.array([-np.sin(theta),np.cos(theta)]); s=near@direction; s0,s1=np.percentile(s,[2,98])
        p0=direction*s0+n*rho; p1=direction*s1+n*rho; length=float(np.linalg.norm(p1-p0))
        if length<.7:continue
        p0=np.array([p0[0]+xmin,p0[1]+zmin]); p1=np.array([p1[0]+xmin,p1[1]+zmin])
        out.append({'votes':votes,'theta_deg':float(np.rad2deg(theta)%180),'p0':p0.tolist(),'p1':p1.tolist(),'length_m':length})
    return out

def merge_similar(lines):
    kept=[]
    for ln in sorted(lines,key=lambda q:-q['votes']):
        a=np.array(ln['p0']);b=np.array(ln['p1']);ang=np.rad2deg(np.arctan2(*(b-a)[::-1]))%180;mid=(a+b)/2;dup=False
        for k in kept:
            aa=np.array(k['p0']);bb=np.array(k['p1']);aang=np.rad2deg(np.arctan2(*(bb-aa)[::-1]))%180
            if abs(((ang-aang+90)%180)-90)<5 and np.linalg.norm(mid-(aa+bb)/2)<.8:dup=True;break
        if not dup:kept.append(ln)
    return kept[:8]

def render_plan(xz,lines,out_png,out_svg):
    fig,ax=plt.subplots(figsize=(10,8)); ax.scatter(xz[:,0],xz[:,1],s=.5,alpha=.12)
    for i,ln in enumerate(lines,1):
        p0,p1=ln['p0'],ln['p1'];ax.plot([p0[0],p1[0]],[p0[1],p1[1]],linewidth=2.5);mid=(np.array(p0)+p1)/2
        ax.text(mid[0],mid[1],f"W{i}: {ln['length_m']:.2f} m",fontsize=8)
    ax.set_aspect('equal','box');ax.set_xlabel('meters');ax.set_ylabel('meters');ax.set_title('Brynz — reconstructed plan with wall candidates');ax.grid(alpha=.15);fig.tight_layout()
    fig.savefig(out_png,dpi=180);fig.savefig(out_svg);plt.close(fig)

def build_result(input_name,points,od,used,floor,ceiling,xz,lines,tier='lidar'):
    x0,x1=np.percentile(xz[:,0],[1,99]);z0,z1=np.percentile(xz[:,1],[1,99]); room_id='room-001'
    measurements=[
      {'name':'floor_area','value':float((x1-x0)*(z1-z0)),'unit':'m2','confidence_interval':None,'not_calibrated':True,'method':'2D point-cloud bounding footprint','validation_status':'NOT_CALIBRATED'},
      {'name':'ceiling_height','value':None if ceiling is None else float(ceiling-floor),'unit':'m','confidence_interval':None,'not_calibrated':True,'method':'robust percentile plane estimate','validation_status':'GROUND_TRUTH_REQUIRED'}]
    walls=[]
    for i,l in enumerate(lines,1):
        walls.append({'wall_id':f'wall-{i:03d}','room_id':room_id,'p0':l['p0'],'p1':l['p1'],'length_m':l['length_m'],'confidence':min(1,l['votes']/max(1,lines[0]['votes'])) if lines else 0,'validation_status':'GROUND_TRUTH_REQUIRED'})
    room={'room_id':room_id,'polygon':[[x0,z0],[x1,z0],[x1,z1],[x0,z1],[x0,z0]],'floor_area_m2':float((x1-x0)*(z1-z0)),'ceiling_height_m':None if ceiling is None else float(ceiling-floor),
          'walls':[w['wall_id'] for w in walls],'openings':[],'damage_regions':[],'adjacent_rooms':[],'measurements':measurements}
    return {'schema_version':'0.3.0','capture':{'capture_id':Path(input_name).stem,'tier':tier,'source':input_name,'metric_status':'partial','frame_count':len(od)},
      'device':{'model':'unknown','platform':'iPhone-compatible capture schema','rgb':True,'depth':True,'lidar':True,'poses':True,'intrinsics':True},
      'rooms':[room],'walls':walls,'openings':[],'measurements':measurements,
      'property_plan':{'rooms':[room_id],'connectors':[],'adjacency_graph':[],'whole_property_footprint_m2':float((x1-x0)*(z1-z0)),'metric_status':'partial'},
      'damage':[],'concealed_damage_flags':[],'scope':[],
      'confidence':{'status':'not_calibrated','method':'Calibration requires physical ground truth; no intervals are claimed.','calibration_dataset':None},
      'validation':{'status':'NOT_EVALUATED','gates':{},'ground_truth_available':False},
      'provenance':{'software_version':'0.3.0','commands':[],'source_files':[input_name]},
      'limitations':['Wall candidates are experimental until ground-truth validation.','Monocular/photo/video metric scale is not inferred without calibration.','Damage detections require RGB input; no damage is asserted when no RGB evidence is available.','Physical gates remain NOT_EVALUATED without laser/tape ground truth.']}

def main():
    ap=argparse.ArgumentParser(description='Brynz LiDAR/depth reconstruction MVP')
    ap.add_argument('--input',required=True);ap.add_argument('--out',default='outputs');ap.add_argument('--stride',type=int,default=40);ap.add_argument('--cell',type=float,default=.06)
    args=ap.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    pts,od,K,used=load_scan(args.input,args.stride);floor,ceiling=robust_floor_ceiling(pts);xz=crop_xy(pts,floor,ceiling);_,occ,meta=make_occupancy(xz,args.cell);lines=merge_similar(hough_lines(occ,meta))
    render_plan(xz,lines,out/'floorplan.png',out/'floorplan.svg')
    result=build_result(Path(args.input).name,pts,od,used,floor,ceiling,xz,lines)
    result['provenance']['commands']=[f'python -m brynz.mvp --input {args.input} --out {args.out}']
    require_valid_output(result);(out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (out/'point_cloud.npz').write_bytes(b'') if False else None
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()

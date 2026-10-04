from PIL import Image
import numpy as np
from brynz.damage import detect_damage
def test_damage_pipeline(tmp_path):
    a=np.full((120,160,3),200,dtype=np.uint8);a[30:60,40:90]=80
    p=tmp_path/"x.png";o=tmp_path/"o.png";Image.fromarray(a).save(p)
    r=detect_damage(p,o); assert isinstance(r,list); assert o.exists()

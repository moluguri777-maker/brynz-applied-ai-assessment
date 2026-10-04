"""Rule-based concealed-damage flags and scope suggestions."""
def concealed_flags(damage, room_id="room-001"):
    flags=[]
    for d in damage:
        cls=d.get("class","unknown")
        if cls=="water_stain":
            flags.append({"flag_id":f"CF-{len(flags)+1:03d}","room_id":room_id,"reason":"stain candidate may indicate moisture near an occluded or wall-floor area","evidence":[d["damage_id"]],"confidence":0.2,"status":"HEURISTIC_FLAG_NOT_CONFIRMED"})
        flags.append({"flag_id":f"CF-{len(flags)+1:03d}","room_id":room_id,"reason":"RGB-only view may hide damage behind furniture/occlusion","evidence":[d["damage_id"]],"confidence":0.15,"status":"HEURISTIC_FLAG_NOT_CONFIRMED"})
    return flags
def scope_items(damage,room_id="room-001"):
    out=[]
    for d in damage:
        if d["class"]=="water_stain":
            descs=["inspect moisture source","affected surface remediation","repaint/refinish"]
        elif d["class"]=="crack_surface_damage":
            descs=["inspect crack extent","repair/preparation","refinish"]
        else: descs=["inspect candidate damage"]
        for desc in descs:
            out.append({"scope_id":f"S-{len(out)+1:03d}","room_id":room_id,"damage_id":d["damage_id"],"description":desc,"quantity":1.0,"unit":"item","confidence":d["confidence"],"status":"SUGGESTED_NOT_CONTRACTOR_CERTIFIED"})
    return out

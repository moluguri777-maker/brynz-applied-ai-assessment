# Capture route
## Shared route
**START → doorway → perimeter sweep → walls → doors/windows → floor → ceiling → furniture/damage → connector → next room → repeat → finish**

### Photos
Take 2–8 stills per room. Keep substantial overlap, stable exposure, no digital zoom. Photograph each wall, openings, floor/ceiling transitions and visible damage. Avoid mirrors/glass where possible; record occluded/low-light areas. Ordinary stills do **not** receive fabricated metric scale.

### Video
Walk continuously at slow, steady speed. Maintain overlap between adjacent views; pause briefly at corners, openings and damage. Avoid rapid pans, blur, reflective surfaces and severe exposure changes. Repeat the route for repeatability.

### LiDAR
Start outside the room, enter through the doorway, perform a perimeter sweep and capture walls/openings/floor/ceiling. Keep LiDAR-visible surfaces in view and avoid sudden motion. Record a second pass of the same room for repeatability. Preserve RGB, depth/confidence, intrinsics and poses.

## Difficult surfaces
Mirrors/glass: mark as ambiguous. Wet surfaces: mark as ambiguous. Low light: lower confidence. Furniture: treat occluded surfaces as unknown rather than clear. Connector spaces should be captured before moving to the next room.

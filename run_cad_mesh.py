#!/usr/bin/env python3
"""
CAD to 2D Mesh Example (WKT input -> Gmsh -> Matplotlib)
"""

import gmsh
import meshio
import matplotlib.pyplot as plt
from shapely import wkt
import numpy as np
import tempfile
import os

print("=" * 60)
print("CAD to 2D Mesh Example (WKT input -> Gmsh -> Matplotlib)")
print("=" * 60)

# -----------------------------
# 1. Define input geometry (WKT polygon)
# -----------------------------
print("\n1. Defining input geometry (WKT polygon)...")

wkt_polygon = """
POLYGON ((
  0 0,
  50 0,
  50 30,
  0 30,
  0 0
), (
  20 10,
  30 10,
  30 20,
  20 20,
  20 10
))
"""

geom = wkt.loads(wkt_polygon)
outer_coords = list(geom.exterior.coords)
holes = [list(ring.coords) for ring in geom.interiors]

print("Outer coordinates:", outer_coords)
print("Holes:", holes)

# -----------------------------
# 2. Gmsh Meshing
# -----------------------------
print("\n2. Starting Gmsh meshing...")

gmsh.initialize()
gmsh.model.add("wkt_mesh")

# Parameters
MIN_ELEM = 2.0
MAX_ELEM = 7.0
BASE_ELEM = 5.0

def add_polygon(coords):
    pts = []
    # Remove duplicate last point if it's the same as first point
    if len(coords) > 1 and coords[0] == coords[-1]:
        coords = coords[:-1]
    
    for x, y in coords:
        pts.append(gmsh.model.geo.addPoint(x, y, 0, BASE_ELEM))
    lines = []
    for i in range(len(pts)):
        next_i = (i + 1) % len(pts)  # Wrap around to close the loop
        lines.append(gmsh.model.geo.addLine(pts[i], pts[next_i]))
    return pts, lines

print("Gmsh initialized and model created")

# Outer boundary
_, outer_lines = add_polygon(outer_coords)
loop_outer = gmsh.model.geo.addCurveLoop(outer_lines)
print(f"Outer boundary created with {len(outer_lines)} lines")

# Holes
hole_loops = []
for i, hole in enumerate(holes):
    _, hole_lines = add_polygon(hole)
    loop_hole = gmsh.model.geo.addCurveLoop(hole_lines)
    hole_loops.append(loop_hole)
    print(f"Hole {i+1} created with {len(hole_lines)} lines")

print(f"Total holes: {len(hole_loops)}")

# Plane surface with holes
surf = gmsh.model.geo.addPlaneSurface([loop_outer] + hole_loops)
print(f"Plane surface created with {len(hole_loops)} holes")

# Mesh size control (Distance field + Threshold)
field_id = gmsh.model.mesh.field.add("Distance")
gmsh.model.mesh.field.setNumbers(field_id, "EdgesList", outer_lines)

th_id = gmsh.model.mesh.field.add("Threshold")
gmsh.model.mesh.field.setNumber(th_id, "InField", field_id)
gmsh.model.mesh.field.setNumber(th_id, "SizeMin", MIN_ELEM)
gmsh.model.mesh.field.setNumber(th_id, "SizeMax", MAX_ELEM)
gmsh.model.mesh.field.setNumber(th_id, "DistMin", 0.5 * MIN_ELEM)
gmsh.model.mesh.field.setNumber(th_id, "DistMax", 5 * MAX_ELEM)
gmsh.model.mesh.field.setAsBackgroundMesh(th_id)

print("Mesh size control fields configured")

gmsh.model.geo.synchronize()
gmsh.model.mesh.generate(2)
print("2D mesh generated")

# Save temporary .msh
tmpfile = tempfile.mktemp(suffix=".msh")
gmsh.write(tmpfile)
gmsh.finalize()

print(f"Mesh saved to temporary file: {tmpfile}")

# -----------------------------
# 3. Read mesh and visualize
# -----------------------------
print("\n3. Reading mesh and creating visualization...")

mesh = meshio.read(tmpfile)

# Extract points & cells
points = mesh.points[:, :2]
triangles = mesh.cells_dict["triangle"]

print(f"Mesh loaded: {len(points)} points, {len(triangles)} triangles")

# Plot mesh
plt.figure(figsize=(10, 6))
for tri in triangles:
    pts = points[tri]
    plt.fill(pts[:,0], pts[:,1], edgecolor="black", fill=False, linewidth=0.5)

plt.gca().set_aspect("equal")
plt.title("2D Mesh from WKT Polygon", fontsize=14, fontweight='bold')
plt.xlabel("X [mm]", fontsize=12)
plt.ylabel("Y [mm]", fontsize=12)
plt.grid(True, alpha=0.3)

# Add some statistics to the plot
plt.text(0.02, 0.98, f"Points: {len(points)}\nTriangles: {len(triangles)}", 
         transform=plt.gca().transAxes, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.savefig("mesh_visualization.png", dpi=300, bbox_inches='tight')
plt.show()

# Cleanup
os.remove(tmpfile)
print("Temporary file cleaned up")

print("\n" + "=" * 60)
print("CAD to 2D Mesh Example completed successfully!")
print("=" * 60)

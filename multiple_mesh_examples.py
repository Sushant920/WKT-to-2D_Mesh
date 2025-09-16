#!/usr/bin/env python3
"""
Multiple CAD to 2D Mesh Examples with Different WKT Geometries
"""

import gmsh
import meshio
import matplotlib.pyplot as plt
from shapely import wkt
import numpy as np
import tempfile
import os

def create_mesh_from_wkt(wkt_polygon, title, filename, figsize=(10, 6)):
    """
    Create a 2D mesh from WKT polygon and save visualization
    """
    print(f"\n{'='*60}")
    print(f"Creating mesh: {title}")
    print(f"{'='*60}")
    
    # Parse WKT geometry
    geom = wkt.loads(wkt_polygon)
    outer_coords = list(geom.exterior.coords)
    holes = [list(ring.coords) for ring in geom.interiors]
    
    print(f"Outer coordinates: {len(outer_coords)} points")
    print(f"Holes: {len(holes)}")
    
    # Initialize Gmsh
    gmsh.initialize()
    gmsh.model.add("mesh_example")
    
    # Parameters
    MIN_ELEM = 1.5
    MAX_ELEM = 5.0
    BASE_ELEM = 3.0
    
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
    
    # Create geometry
    _, outer_lines = add_polygon(outer_coords)
    loop_outer = gmsh.model.geo.addCurveLoop(outer_lines)
    
    # Add holes
    hole_loops = []
    for hole in holes:
        _, hole_lines = add_polygon(hole)
        loop_hole = gmsh.model.geo.addCurveLoop(hole_lines)
        hole_loops.append(loop_hole)
    
    # Create surface
    surf = gmsh.model.geo.addPlaneSurface([loop_outer] + hole_loops)
    
    # Mesh size control
    field_id = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(field_id, "EdgesList", outer_lines)
    
    th_id = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(th_id, "InField", field_id)
    gmsh.model.mesh.field.setNumber(th_id, "SizeMin", MIN_ELEM)
    gmsh.model.mesh.field.setNumber(th_id, "SizeMax", MAX_ELEM)
    gmsh.model.mesh.field.setNumber(th_id, "DistMin", 0.5 * MIN_ELEM)
    gmsh.model.mesh.field.setNumber(th_id, "DistMax", 5 * MAX_ELEM)
    gmsh.model.mesh.field.setAsBackgroundMesh(th_id)
    
    # Generate mesh
    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(2)
    
    # Save and read mesh
    tmpfile = tempfile.mktemp(suffix=".msh")
    gmsh.write(tmpfile)
    gmsh.finalize()
    
    mesh = meshio.read(tmpfile)
    points = mesh.points[:, :2]
    triangles = mesh.cells_dict["triangle"]
    
    print(f"Generated mesh: {len(points)} points, {len(triangles)} triangles")
    
    # Create visualization
    plt.figure(figsize=figsize)
    for tri in triangles:
        pts = points[tri]
        plt.fill(pts[:,0], pts[:,1], edgecolor="black", fill=False, linewidth=0.5)
    
    plt.gca().set_aspect("equal")
    plt.title(f"{title}\nPoints: {len(points)}, Triangles: {len(triangles)}", 
              fontsize=12, fontweight='bold')
    plt.xlabel("X [mm]", fontsize=10)
    plt.ylabel("Y [mm]", fontsize=10)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
    
    # Cleanup
    os.remove(tmpfile)
    return len(points), len(triangles)

# Define different WKT geometries
geometries = {
    "L-Shape": """
    POLYGON ((
      0 0,
      30 0,
      30 20,
      10 20,
      10 30,
      0 30,
      0 0
    ))
    """,
    
    "Circle with Square Hole": """
    POLYGON ((
      0 0,
      40 0,
      40 40,
      0 40,
      0 0
    ), (
      15 15,
      25 15,
      25 25,
      15 25,
      15 15
    ))
    """,
    
    "Complex Shape": """
    POLYGON ((
      0 0,
      50 0,
      50 20,
      40 20,
      40 30,
      30 30,
      30 40,
      20 40,
      20 30,
      10 30,
      10 20,
      0 20,
      0 0
    ))
    """,
    
    "T-Shape": """
    POLYGON ((
      0 0,
      40 0,
      40 10,
      30 10,
      30 30,
      20 30,
      20 10,
      10 10,
      10 30,
      0 30,
      0 0
    ))
    """,
    
    "Multiple Holes": """
    POLYGON ((
      0 0,
      60 0,
      60 40,
      0 40,
      0 0
    ), (
      10 10,
      20 10,
      20 20,
      10 20,
      10 10
    ), (
      40 10,
      50 10,
      50 20,
      40 20,
      40 10
    ), (
      30 25,
      40 25,
      40 35,
      30 35,
      30 25
    ))
    """,
    
    "Hexagon": """
    POLYGON ((
      25 0,
      45 15,
      45 35,
      25 50,
      5 35,
      5 15,
      25 0
    ))
    """
}

# Create meshes for all geometries
results = []
for name, wkt_geom in geometries.items():
    filename = f"mesh_{name.lower().replace(' ', '_').replace('-', '_')}.png"
    points, triangles = create_mesh_from_wkt(wkt_geom, name, filename)
    results.append((name, points, triangles))

# Summary
print(f"\n{'='*80}")
print("MESH GENERATION SUMMARY")
print(f"{'='*80}")
print(f"{'Geometry':<20} {'Points':<10} {'Triangles':<12} {'File'}")
print("-" * 80)
for name, points, triangles in results:
    filename = f"mesh_{name.lower().replace(' ', '_').replace('-', '_')}.png"
    print(f"{name:<20} {points:<10} {triangles:<12} {filename}")

print(f"\nAll mesh visualizations saved as PNG files!")
print(f"Total geometries processed: {len(geometries)}")

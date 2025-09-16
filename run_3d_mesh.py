#!/usr/bin/env python3
"""
3D CAD to Mesh Example - Command Line Version
Generate 3D meshes from various geometries using Gmsh
"""

import gmsh
import meshio
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import tempfile
import os

def create_3d_mesh(geometry_type, geometry_params, mesh_params, title="3D Mesh"):
    """
    Create a 3D mesh from geometry parameters
    """
    print(f"\n{'='*60}")
    print(f"Creating 3D mesh: {title}")
    print(f"Geometry: {geometry_type}")
    print(f"{'='*60}")
    
    try:
        # Initialize Gmsh
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.Verbosity", 0)
        gmsh.model.add("3d_mesh_example")
        
        # Parameters
        MIN_ELEM = mesh_params['min_elem']
        MAX_ELEM = mesh_params['max_elem']
        BASE_ELEM = mesh_params['base_elem']
        
        if geometry_type == "Box":
            # Create a box manually
            x, y, z = geometry_params['center']
            lx, ly, lz = geometry_params['dimensions']
            
            print(f"Creating box: center=({x}, {y}, {z}), dimensions=({lx}, {ly}, {lz})")
            
            # Create box points
            p1 = gmsh.model.geo.addPoint(x-lx/2, y-ly/2, z-lz/2, BASE_ELEM)
            p2 = gmsh.model.geo.addPoint(x+lx/2, y-ly/2, z-lz/2, BASE_ELEM)
            p3 = gmsh.model.geo.addPoint(x+lx/2, y+ly/2, z-lz/2, BASE_ELEM)
            p4 = gmsh.model.geo.addPoint(x-lx/2, y+ly/2, z-lz/2, BASE_ELEM)
            p5 = gmsh.model.geo.addPoint(x-lx/2, y-ly/2, z+lz/2, BASE_ELEM)
            p6 = gmsh.model.geo.addPoint(x+lx/2, y-ly/2, z+lz/2, BASE_ELEM)
            p7 = gmsh.model.geo.addPoint(x+lx/2, y+ly/2, z+lz/2, BASE_ELEM)
            p8 = gmsh.model.geo.addPoint(x-lx/2, y+ly/2, z+lz/2, BASE_ELEM)
            
            # Create lines
            l1 = gmsh.model.geo.addLine(p1, p2)
            l2 = gmsh.model.geo.addLine(p2, p3)
            l3 = gmsh.model.geo.addLine(p3, p4)
            l4 = gmsh.model.geo.addLine(p4, p1)
            l5 = gmsh.model.geo.addLine(p5, p6)
            l6 = gmsh.model.geo.addLine(p6, p7)
            l7 = gmsh.model.geo.addLine(p7, p8)
            l8 = gmsh.model.geo.addLine(p8, p5)
            l9 = gmsh.model.geo.addLine(p1, p5)
            l10 = gmsh.model.geo.addLine(p2, p6)
            l11 = gmsh.model.geo.addLine(p3, p7)
            l12 = gmsh.model.geo.addLine(p4, p8)
            
            # Create surfaces
            s1 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])])
            s2 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l5, l6, l7, l8])])
            s3 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l1, l10, l5, -l9])])
            s4 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l2, l11, l6, -l10])])
            s5 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l3, l12, l7, -l11])])
            s6 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l4, l9, l8, -l12])])
            
            # Create volume
            volume = gmsh.model.geo.addSurfaceLoop([s1, s2, s3, s4, s5, s6])
            gmsh.model.geo.addVolume([volume])
            
        elif geometry_type == "Cylinder":
            # Create a cylinder manually
            x, y, z = geometry_params['center']
            r = geometry_params['radius']
            h = geometry_params['height']
            
            print(f"Creating cylinder: center=({x}, {y}, {z}), radius={r}, height={h}")
            
            # Create cylinder using parametric approach
            # For simplicity, create a box for now
            p1 = gmsh.model.geo.addPoint(x-r, y-r, z, BASE_ELEM)
            p2 = gmsh.model.geo.addPoint(x+r, y-r, z, BASE_ELEM)
            p3 = gmsh.model.geo.addPoint(x+r, y+r, z, BASE_ELEM)
            p4 = gmsh.model.geo.addPoint(x-r, y+r, z, BASE_ELEM)
            p5 = gmsh.model.geo.addPoint(x-r, y-r, z+h, BASE_ELEM)
            p6 = gmsh.model.geo.addPoint(x+r, y-r, z+h, BASE_ELEM)
            p7 = gmsh.model.geo.addPoint(x+r, y+r, z+h, BASE_ELEM)
            p8 = gmsh.model.geo.addPoint(x-r, y+r, z+h, BASE_ELEM)
            
            # Create lines and surfaces (similar to box)
            l1 = gmsh.model.geo.addLine(p1, p2)
            l2 = gmsh.model.geo.addLine(p2, p3)
            l3 = gmsh.model.geo.addLine(p3, p4)
            l4 = gmsh.model.geo.addLine(p4, p1)
            l5 = gmsh.model.geo.addLine(p5, p6)
            l6 = gmsh.model.geo.addLine(p6, p7)
            l7 = gmsh.model.geo.addLine(p7, p8)
            l8 = gmsh.model.geo.addLine(p8, p5)
            l9 = gmsh.model.geo.addLine(p1, p5)
            l10 = gmsh.model.geo.addLine(p2, p6)
            l11 = gmsh.model.geo.addLine(p3, p7)
            l12 = gmsh.model.geo.addLine(p4, p8)
            
            s1 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])])
            s2 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l5, l6, l7, l8])])
            s3 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l1, l10, l5, -l9])])
            s4 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l2, l11, l6, -l10])])
            s5 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l3, l12, l7, -l11])])
            s6 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l4, l9, l8, -l12])])
            
            volume = gmsh.model.geo.addSurfaceLoop([s1, s2, s3, s4, s5, s6])
            gmsh.model.geo.addVolume([volume])
            
        elif geometry_type == "Sphere":
            # Create a sphere manually (approximated as octahedron for simplicity)
            x, y, z = geometry_params['center']
            r = geometry_params['radius']
            
            print(f"Creating sphere: center=({x}, {y}, {z}), radius={r}")
            
            # Create octahedron approximation
            p1 = gmsh.model.geo.addPoint(x, y, z+r, BASE_ELEM)
            p2 = gmsh.model.geo.addPoint(x+r, y, z, BASE_ELEM)
            p3 = gmsh.model.geo.addPoint(x, y+r, z, BASE_ELEM)
            p4 = gmsh.model.geo.addPoint(x-r, y, z, BASE_ELEM)
            p5 = gmsh.model.geo.addPoint(x, y-r, z, BASE_ELEM)
            p6 = gmsh.model.geo.addPoint(x, y, z-r, BASE_ELEM)
            
            # Create lines and surfaces for octahedron
            l1 = gmsh.model.geo.addLine(p1, p2)
            l2 = gmsh.model.geo.addLine(p2, p3)
            l3 = gmsh.model.geo.addLine(p3, p1)
            l4 = gmsh.model.geo.addLine(p1, p4)
            l5 = gmsh.model.geo.addLine(p4, p5)
            l6 = gmsh.model.geo.addLine(p5, p1)
            l7 = gmsh.model.geo.addLine(p2, p6)
            l8 = gmsh.model.geo.addLine(p6, p3)
            l9 = gmsh.model.geo.addLine(p4, p6)
            l10 = gmsh.model.geo.addLine(p6, p5)
            
            # Create triangular surfaces
            s1 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l1, l2, l3])])
            s2 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l4, l5, l6])])
            s3 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l2, l7, l8])])
            s4 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l5, l9, l10])])
            s5 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l1, l7, -l4])])
            s6 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l3, l8, -l6])])
            s7 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l9, l7, -l2])])
            s8 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l10, l8, -l5])])
            
            volume = gmsh.model.geo.addSurfaceLoop([s1, s2, s3, s4, s5, s6, s7, s8])
            gmsh.model.geo.addVolume([volume])
            
        elif geometry_type == "Torus":
            # Create a torus manually (simplified as a box for now)
            x, y, z = geometry_params['center']
            r1 = geometry_params['major_radius']
            r2 = geometry_params['minor_radius']
            
            print(f"Creating torus: center=({x}, {y}, {z}), major_radius={r1}, minor_radius={r2}")
            
            # Simplified as a box for now
            p1 = gmsh.model.geo.addPoint(x-r1, y-r1, z-r2, BASE_ELEM)
            p2 = gmsh.model.geo.addPoint(x+r1, y-r1, z-r2, BASE_ELEM)
            p3 = gmsh.model.geo.addPoint(x+r1, y+r1, z-r2, BASE_ELEM)
            p4 = gmsh.model.geo.addPoint(x-r1, y+r1, z-r2, BASE_ELEM)
            p5 = gmsh.model.geo.addPoint(x-r1, y-r1, z+r2, BASE_ELEM)
            p6 = gmsh.model.geo.addPoint(x+r1, y-r1, z+r2, BASE_ELEM)
            p7 = gmsh.model.geo.addPoint(x+r1, y+r1, z+r2, BASE_ELEM)
            p8 = gmsh.model.geo.addPoint(x-r1, y+r1, z+r2, BASE_ELEM)
            
            # Create lines and surfaces (similar to box)
            l1 = gmsh.model.geo.addLine(p1, p2)
            l2 = gmsh.model.geo.addLine(p2, p3)
            l3 = gmsh.model.geo.addLine(p3, p4)
            l4 = gmsh.model.geo.addLine(p4, p1)
            l5 = gmsh.model.geo.addLine(p5, p6)
            l6 = gmsh.model.geo.addLine(p6, p7)
            l7 = gmsh.model.geo.addLine(p7, p8)
            l8 = gmsh.model.geo.addLine(p8, p5)
            l9 = gmsh.model.geo.addLine(p1, p5)
            l10 = gmsh.model.geo.addLine(p2, p6)
            l11 = gmsh.model.geo.addLine(p3, p7)
            l12 = gmsh.model.geo.addLine(p4, p8)
            
            s1 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])])
            s2 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l5, l6, l7, l8])])
            s3 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l1, l10, l5, -l9])])
            s4 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l2, l11, l6, -l10])])
            s5 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l3, l12, l7, -l11])])
            s6 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l4, l9, l8, -l12])])
            
            volume = gmsh.model.geo.addSurfaceLoop([s1, s2, s3, s4, s5, s6])
            gmsh.model.geo.addVolume([volume])
            
        elif geometry_type == "Cone":
            # Create a cone manually (simplified as a box for now)
            x, y, z = geometry_params['center']
            r1 = geometry_params['bottom_radius']
            r2 = geometry_params['top_radius']
            h = geometry_params['height']
            
            print(f"Creating cone: center=({x}, {y}, {z}), bottom_radius={r1}, top_radius={r2}, height={h}")
            
            # Simplified as a box for now
            p1 = gmsh.model.geo.addPoint(x-r1, y-r1, z, BASE_ELEM)
            p2 = gmsh.model.geo.addPoint(x+r1, y-r1, z, BASE_ELEM)
            p3 = gmsh.model.geo.addPoint(x+r1, y+r1, z, BASE_ELEM)
            p4 = gmsh.model.geo.addPoint(x-r1, y+r1, z, BASE_ELEM)
            p5 = gmsh.model.geo.addPoint(x-r2, y-r2, z+h, BASE_ELEM)
            p6 = gmsh.model.geo.addPoint(x+r2, y-r2, z+h, BASE_ELEM)
            p7 = gmsh.model.geo.addPoint(x+r2, y+r2, z+h, BASE_ELEM)
            p8 = gmsh.model.geo.addPoint(x-r2, y+r2, z+h, BASE_ELEM)
            
            # Create lines and surfaces (similar to box)
            l1 = gmsh.model.geo.addLine(p1, p2)
            l2 = gmsh.model.geo.addLine(p2, p3)
            l3 = gmsh.model.geo.addLine(p3, p4)
            l4 = gmsh.model.geo.addLine(p4, p1)
            l5 = gmsh.model.geo.addLine(p5, p6)
            l6 = gmsh.model.geo.addLine(p6, p7)
            l7 = gmsh.model.geo.addLine(p7, p8)
            l8 = gmsh.model.geo.addLine(p8, p5)
            l9 = gmsh.model.geo.addLine(p1, p5)
            l10 = gmsh.model.geo.addLine(p2, p6)
            l11 = gmsh.model.geo.addLine(p3, p7)
            l12 = gmsh.model.geo.addLine(p4, p8)
            
            s1 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])])
            s2 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l5, l6, l7, l8])])
            s3 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l1, l10, l5, -l9])])
            s4 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l2, l11, l6, -l10])])
            s5 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l3, l12, l7, -l11])])
            s6 = gmsh.model.geo.addPlaneSurface([gmsh.model.geo.addCurveLoop([l4, l9, l8, -l12])])
            
            volume = gmsh.model.geo.addSurfaceLoop([s1, s2, s3, s4, s5, s6])
            gmsh.model.geo.addVolume([volume])
        
        # Mesh size control
        field_id = gmsh.model.mesh.field.add("Distance")
        gmsh.model.mesh.field.setNumbers(field_id, "NodesList", [1])
        
        th_id = gmsh.model.mesh.field.add("Threshold")
        gmsh.model.mesh.field.setNumber(th_id, "InField", field_id)
        gmsh.model.mesh.field.setNumber(th_id, "SizeMin", MIN_ELEM)
        gmsh.model.mesh.field.setNumber(th_id, "SizeMax", MAX_ELEM)
        gmsh.model.mesh.field.setNumber(th_id, "DistMin", 0.5 * MIN_ELEM)
        gmsh.model.mesh.field.setNumber(th_id, "DistMax", 5 * MAX_ELEM)
        gmsh.model.mesh.field.setAsBackgroundMesh(th_id)
        
        # Generate 3D mesh
        print("Generating 3D mesh...")
        gmsh.model.geo.synchronize()
        gmsh.model.mesh.generate(3)
        
        # Save and read mesh
        tmpfile = tempfile.mktemp(suffix=".msh")
        gmsh.write(tmpfile)
        gmsh.finalize()
        
        mesh = meshio.read(tmpfile)
        points = mesh.points
        tetrahedra = mesh.cells_dict.get("tetra", np.array([]).reshape(0, 4))
        hexahedra = mesh.cells_dict.get("hexahedron", np.array([]).reshape(0, 8))
        
        print(f"Generated mesh: {len(points)} points, {len(tetrahedra)} tetrahedra, {len(hexahedra)} hexahedra")
        
        # Cleanup
        os.remove(tmpfile)
        
        return {
            'success': True,
            'points': points,
            'tetrahedra': tetrahedra,
            'hexahedra': hexahedra,
            'num_points': len(points),
            'num_tetrahedra': len(tetrahedra),
            'num_hexahedra': len(hexahedra)
        }
        
    except Exception as e:
        try:
            gmsh.finalize()
        except:
            pass
        return {
            'success': False,
            'error': str(e)
        }

def plot_3d_mesh(points, tetrahedra, hexahedra, title, figsize=(12, 8)):
    """Create 3D mesh visualization"""
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot tetrahedra (limit for performance)
    if len(tetrahedra) > 0:
        print(f"Plotting {min(100, len(tetrahedra))} tetrahedra...")
        for tet in tetrahedra[:100]:
            pts = points[tet]
            # Create faces of tetrahedron
            faces = [
                [pts[0], pts[1], pts[2]],
                [pts[0], pts[1], pts[3]],
                [pts[0], pts[2], pts[3]],
                [pts[1], pts[2], pts[3]]
            ]
            for face in faces:
                face = np.array(face)
                ax.plot_trisurf(face[:, 0], face[:, 1], face[:, 2], alpha=0.3, color='lightblue')
    
    # Plot hexahedra (limit for performance)
    if len(hexahedra) > 0:
        print(f"Plotting {min(50, len(hexahedra))} hexahedra...")
        for hexa in hexahedra[:50]:
            pts = points[hexa]
            # Create faces of hexahedron
            faces = [
                [pts[0], pts[1], pts[2], pts[3]],  # bottom
                [pts[4], pts[5], pts[6], pts[7]],  # top
                [pts[0], pts[1], pts[5], pts[4]],  # front
                [pts[2], pts[3], pts[7], pts[6]],  # back
                [pts[0], pts[3], pts[7], pts[4]],  # left
                [pts[1], pts[2], pts[6], pts[5]]   # right
            ]
            for face in faces:
                face = np.array(face)
                ax.plot_trisurf(face[:, 0], face[:, 1], face[:, 2], alpha=0.3, color='lightgreen')
    
    # Plot points
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], c='red', s=1, alpha=0.6)
    
    ax.set_title(f"{title}\nPoints: {len(points)}, Tetrahedra: {len(tetrahedra)}, Hexahedra: {len(hexahedra)}", 
                 fontsize=12, fontweight='bold')
    ax.set_xlabel("X [mm]", fontsize=10)
    ax.set_ylabel("Y [mm]", fontsize=10)
    ax.set_zlabel("Z [mm]", fontsize=10)
    
    # Set equal aspect ratio
    max_range = np.array([points[:,0].max()-points[:,0].min(),
                         points[:,1].max()-points[:,1].min(),
                         points[:,2].max()-points[:,2].min()]).max() / 2.0
    mid_x = (points[:,0].max()+points[:,0].min()) * 0.5
    mid_y = (points[:,1].max()+points[:,1].min()) * 0.5
    mid_z = (points[:,2].max()+points[:,2].min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    plt.tight_layout()
    return fig

# Define 3D geometries to test
geometries = {
    "Box": {
        "center": [0, 0, 0],
        "dimensions": [20, 15, 10]
    },
    "Cylinder": {
        "center": [0, 0, 0],
        "radius": 10,
        "height": 20
    },
    "Sphere": {
        "center": [0, 0, 0],
        "radius": 12
    },
    "Torus": {
        "center": [0, 0, 0],
        "major_radius": 15,
        "minor_radius": 5
    },
    "Cone": {
        "center": [0, 0, 0],
        "bottom_radius": 10,
        "top_radius": 5,
        "height": 15
    }
}

# Mesh parameters
mesh_params = {
    'min_elem': 2.0,
    'max_elem': 8.0,
    'base_elem': 4.0
}

# Create meshes for all geometries
results = []
for name, geom_params in geometries.items():
    result = create_3d_mesh(name, geom_params, mesh_params, name)
    
    if result['success']:
        # Create visualization
        fig = plot_3d_mesh(result['points'], result['tetrahedra'], result['hexahedra'], name)
        
        # Save figure
        filename = f"3d_mesh_{name.lower()}.png"
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Saved visualization: {filename}")
        
        results.append((name, result['num_points'], result['num_tetrahedra'], result['num_hexahedra']))
        plt.close(fig)
    else:
        print(f"Failed to create {name}: {result['error']}")

# Summary
print(f"\n{'='*80}")
print("3D MESH GENERATION SUMMARY")
print(f"{'='*80}")
print(f"{'Geometry':<15} {'Points':<10} {'Tetrahedra':<12} {'Hexahedra':<12} {'File'}")
print("-" * 80)
for name, points, tetrahedra, hexahedra in results:
    filename = f"3d_mesh_{name.lower()}.png"
    print(f"{name:<15} {points:<10} {tetrahedra:<12} {hexahedra:<12} {filename}")

print(f"\nAll 3D mesh visualizations saved as PNG files!")
print(f"Total geometries processed: {len(results)}")

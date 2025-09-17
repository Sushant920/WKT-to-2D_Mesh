#!/usr/bin/env python3
"""
Streamlit CAD to 2D Mesh Application - Fixed Version
Interactive UI for generating meshes from WKT geometries
"""

import streamlit as st
import subprocess
import tempfile
import os
import json
import matplotlib.pyplot as plt
from shapely import wkt
import numpy as np
import io
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="CAD to 2D/3D Mesh Generator",
    page_icon="🔺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .geometry-info {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

def create_mesh_script(geometry_data, mesh_params, mesh_type="triangular", is_3d=False):
    """Create a temporary Python script for mesh generation"""
    script_content = f'''
import gmsh
import meshio
import json
import tempfile
import os
import sys

def create_mesh():
    try:
        # Initialize Gmsh
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.Verbosity", 0)
        gmsh.model.add("mesh_example")
        
        # Parameters
        MIN_ELEM = {mesh_params['min_elem']}
        MAX_ELEM = {mesh_params['max_elem']}
        BASE_ELEM = {mesh_params['base_elem']}
        MESH_TYPE = "{mesh_type}"
        IS_3D = {is_3d}
        
        if IS_3D:
            # Handle 3D geometry from dictionary
            geom_data = {geometry_data}
            
            if geom_data["type"] == "cube":
                # Create a cube using Gmsh's built-in box function
                x, y, z = geom_data["position"]
                dx, dy, dz = geom_data["dimensions"]
                
                # Use Gmsh's built-in box creation (more reliable)
                box = gmsh.model.occ.addBox(x, y, z, dx, dy, dz)
                gmsh.model.occ.synchronize()
                
                # Get the surfaces of the box for visualization
                surfaces = gmsh.model.getEntities(2)  # Get all 2D entities (surfaces)
                
                # Store face information for visualization
                faces = [
                    [[x, y, z], [x+dx, y, z], [x+dx, y+dy, z], [x, y+dy, z]],  # Bottom
                    [[x, y, z+dz], [x+dx, y, z+dz], [x+dx, y+dy, z+dz], [x, y+dy, z+dz]],  # Top
                    [[x, y, z], [x+dx, y, z], [x+dx, y, z+dz], [x, y, z+dz]],  # Front
                    [[x, y+dy, z], [x+dx, y+dy, z], [x+dx, y+dy, z+dz], [x, y+dy, z+dz]],  # Back
                    [[x, y, z], [x, y+dy, z], [x, y+dy, z+dz], [x, y, z+dz]],  # Left
                    [[x+dx, y, z], [x+dx, y+dy, z], [x+dx, y+dy, z+dz], [x+dx, y, z+dz]]   # Right
                ]
                
                # Set mesh algorithm for 3D surface meshing
                if MESH_TYPE == "quadrilateral":
                    # Use structured mesh for quads on 3D surfaces
                    gmsh.option.setNumber("Mesh.Algorithm", 8)  # Frontal-Delaunay for quads
                    gmsh.option.setNumber("Mesh.RecombineAll", 1)  # Recombine triangles into quads
                    gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)  # All quads
                    gmsh.option.setNumber("Mesh.ElementOrder", 1)  # Linear elements
                    # Force structured meshing on each face
                    # Get all surfaces of the box
                    v = gmsh.model.getEntities(3)  # Get 3D entities (volumes)
                    s = gmsh.model.getBoundary(v, False, False, True)  # Get surfaces
                    for surf_dimtag in s:
                        gmsh.model.mesh.setRecombine(surf_dimtag[0], surf_dimtag[1])
                else:
                    # Use triangular mesh
                    gmsh.option.setNumber("Mesh.Algorithm", 6)  # Frontal-Delaunay
                    gmsh.option.setNumber("Mesh.RecombineAll", 0)
                
                # Generate 2D surface mesh only (not volume)
                gmsh.model.geo.synchronize()
                gmsh.model.mesh.generate(2)  # Generate 2D surface mesh
                
            elif geom_data["type"] == "cylinder":
                # Create a cylinder
                x, y, z = geom_data["position"]
                r = geom_data["radius"]
                h = geom_data["height"]
                cylinder = gmsh.model.occ.addCylinder(x, y, z, 0, 0, h, r)
                gmsh.model.occ.synchronize()
                faces = []  # Cylinder faces will be auto-detected
                
                # Set mesh algorithm for 3D surface meshing
                if MESH_TYPE == "quadrilateral":
                    gmsh.option.setNumber("Mesh.Algorithm", 8)
                    gmsh.option.setNumber("Mesh.RecombineAll", 1)
                    gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)
                    gmsh.option.setNumber("Mesh.ElementOrder", 1)
                    v = gmsh.model.getEntities(3)
                    s = gmsh.model.getBoundary(v, False, False, True)
                    for surf_dimtag in s:
                        gmsh.model.mesh.setRecombine(surf_dimtag[0], surf_dimtag[1])
                else:
                    gmsh.option.setNumber("Mesh.Algorithm", 6)
                    gmsh.option.setNumber("Mesh.RecombineAll", 0)
                
                gmsh.model.geo.synchronize()
                gmsh.model.mesh.generate(2)
                
            elif geom_data["type"] == "pyramid":
                # Create a pyramid (square base)
                x, y, z = geom_data["position"]
                base_size = geom_data["base_size"]
                height = geom_data["height"]
                # Create pyramid as a cone with square base
                pyramid = gmsh.model.occ.addCone(x, y, z, 0, 0, height, base_size/2, 0)
                gmsh.model.occ.synchronize()
                faces = []
                
                # Set mesh algorithm for 3D surface meshing
                if MESH_TYPE == "quadrilateral":
                    gmsh.option.setNumber("Mesh.Algorithm", 8)
                    gmsh.option.setNumber("Mesh.RecombineAll", 1)
                    gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)
                    gmsh.option.setNumber("Mesh.ElementOrder", 1)
                    v = gmsh.model.getEntities(3)
                    s = gmsh.model.getBoundary(v, False, False, True)
                    for surf_dimtag in s:
                        gmsh.model.mesh.setRecombine(surf_dimtag[0], surf_dimtag[1])
                else:
                    gmsh.option.setNumber("Mesh.Algorithm", 6)
                    gmsh.option.setNumber("Mesh.RecombineAll", 0)
                
                gmsh.model.geo.synchronize()
                gmsh.model.mesh.generate(2)
                
            elif geom_data["type"] == "sphere":
                # Create a sphere
                x, y, z = geom_data["position"]
                r = geom_data["radius"]
                sphere = gmsh.model.occ.addSphere(x, y, z, r)
                gmsh.model.occ.synchronize()
                faces = []
                
                # Set mesh algorithm for 3D surface meshing
                if MESH_TYPE == "quadrilateral":
                    gmsh.option.setNumber("Mesh.Algorithm", 8)
                    gmsh.option.setNumber("Mesh.RecombineAll", 1)
                    gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)
                    gmsh.option.setNumber("Mesh.ElementOrder", 1)
                    v = gmsh.model.getEntities(3)
                    s = gmsh.model.getBoundary(v, False, False, True)
                    for surf_dimtag in s:
                        gmsh.model.mesh.setRecombine(surf_dimtag[0], surf_dimtag[1])
                else:
                    gmsh.option.setNumber("Mesh.Algorithm", 6)
                    gmsh.option.setNumber("Mesh.RecombineAll", 0)
                
                gmsh.model.geo.synchronize()
                gmsh.model.mesh.generate(2)
                
            elif geom_data["type"] == "cone":
                # Create a cone
                x, y, z = geom_data["position"]
                r = geom_data["radius"]
                h = geom_data["height"]
                cone = gmsh.model.occ.addCone(x, y, z, 0, 0, h, r, 0)
                gmsh.model.occ.synchronize()
                faces = []
                
                # Set mesh algorithm for 3D surface meshing
                if MESH_TYPE == "quadrilateral":
                    gmsh.option.setNumber("Mesh.Algorithm", 8)
                    gmsh.option.setNumber("Mesh.RecombineAll", 1)
                    gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)
                    gmsh.option.setNumber("Mesh.ElementOrder", 1)
                    v = gmsh.model.getEntities(3)
                    s = gmsh.model.getBoundary(v, False, False, True)
                    for surf_dimtag in s:
                        gmsh.model.mesh.setRecombine(surf_dimtag[0], surf_dimtag[1])
                else:
                    gmsh.option.setNumber("Mesh.Algorithm", 6)
                    gmsh.option.setNumber("Mesh.RecombineAll", 0)
                
                gmsh.model.geo.synchronize()
                gmsh.model.mesh.generate(2)
            
            # Save and read mesh
            tmpfile = tempfile.mktemp(suffix=".msh")
            gmsh.write(tmpfile)
            gmsh.finalize()
            
            mesh = meshio.read(tmpfile)
            points = mesh.points
            
            # Extract 2D surface elements (triangles and quads)
            triangles = []
            quads = []
            
            if "triangle" in mesh.cells_dict:
                triangles = mesh.cells_dict["triangle"]
            if "quad" in mesh.cells_dict:
                quads = mesh.cells_dict["quad"]
            
            # Cleanup
            os.remove(tmpfile)
            
            result = {{
                    'success': True,
                    'points': points.tolist(),
                    'triangles': triangles.tolist() if len(triangles) > 0 else [],
                    'quads': quads.tolist() if len(quads) > 0 else [],
                    'faces': faces,
                    'num_points': len(points),
                    'num_triangles': len(triangles),
                    'num_quads': len(quads),
                    'mesh_type': MESH_TYPE,
                    'is_3d': True
                }}
        else:
            # Handle 2D geometry (POLYGON)
            outer_coords = list(geom.exterior.coords)
            holes = [list(ring.coords) for ring in geom.interiors]
            
            def add_polygon(coords):
                pts = []
                if len(coords) > 1 and coords[0] == coords[-1]:
                    coords = coords[:-1]
                
                for x, y in coords:
                    pts.append(gmsh.model.geo.addPoint(x, y, 0, BASE_ELEM))
                lines = []
                for i in range(len(pts)):
                    next_i = (i + 1) % len(pts)
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
            
            # Set mesh algorithm based on type
            if MESH_TYPE == "quadrilateral":
                gmsh.option.setNumber("Mesh.Algorithm", 8)
                gmsh.option.setNumber("Mesh.RecombineAll", 1)
                gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)
            else:
                gmsh.option.setNumber("Mesh.Algorithm", 6)
                gmsh.option.setNumber("Mesh.RecombineAll", 0)
            
            # Generate mesh
            gmsh.model.geo.synchronize()
            gmsh.model.mesh.generate(2)
            
            # Save and read mesh
            tmpfile = tempfile.mktemp(suffix=".msh")
            gmsh.write(tmpfile)
            gmsh.finalize()
            
            mesh = meshio.read(tmpfile)
            points = mesh.points[:, :2]
            
            # Extract elements based on type
            triangles = []
            quads = []
            
            if "triangle" in mesh.cells_dict:
                triangles = mesh.cells_dict["triangle"]
            if "quad" in mesh.cells_dict:
                quads = mesh.cells_dict["quad"]
            
            # Cleanup
            os.remove(tmpfile)
            
            result = {{
                'success': True,
                'points': points.tolist(),
                'triangles': triangles.tolist() if len(triangles) > 0 else [],
                'quads': quads.tolist() if len(quads) > 0 else [],
                'outer_coords': outer_coords,
                'holes': holes,
                'num_points': len(points),
                'num_triangles': len(triangles),
                'num_quads': len(quads),
                'mesh_type': MESH_TYPE,
                'is_3d': False
            }}
        
        print(json.dumps(result))
        
    except Exception as e:
        result = {{
            'success': False,
            'error': str(e)
        }}
        print(json.dumps(result))

if __name__ == "__main__":
    create_mesh()
'''
    return script_content

def create_mesh_from_geometry(geometry_data, title, mesh_params, mesh_type="triangular", is_3d=False):
    """Create a 2D or 3D mesh from geometry data using subprocess"""
    try:
        # Create temporary script
        script_content = create_mesh_script(geometry_data, mesh_params, mesh_type, is_3d)
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        # Run the script in subprocess
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=60  # Increased timeout for 3D meshes
        )
        
        # Clean up script file
        os.unlink(script_path)
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': f"Script execution failed: {result.stderr}"
            }
        
        # Parse JSON result
        result_data = json.loads(result.stdout.strip())
        
        if result_data['success']:
            # Convert points back to numpy array
            result_data['points'] = np.array(result_data['points'])
            
            if is_3d:
                # Handle 3D surface mesh data
                result_data['triangles'] = np.array(result_data['triangles']) if result_data['triangles'] else np.array([])
                result_data['quads'] = np.array(result_data['quads']) if result_data['quads'] else np.array([])
            else:
                # Handle 2D mesh data
                result_data['triangles'] = np.array(result_data['triangles']) if result_data['triangles'] else np.array([])
                result_data['quads'] = np.array(result_data['quads']) if result_data['quads'] else np.array([])
        
        return result_data
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': "Mesh generation timed out (60 seconds)"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def create_mesh_from_wkt(wkt_geometry, title, mesh_params, mesh_type="triangular", is_3d=False):
    """Create a 2D mesh from WKT polygon using subprocess (for 2D geometries)"""
    try:
        # Create temporary script for 2D WKT geometries
        script_content = f'''
import gmsh
import meshio
import json
import tempfile
import os
import sys

def create_mesh():
    try:
        # Parse WKT geometry
        from shapely import wkt
        geom = wkt.loads("""{wkt_geometry}""")
        outer_coords = list(geom.exterior.coords)
        holes = [list(ring.coords) for ring in geom.interiors]
        
        # Initialize Gmsh
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.Verbosity", 0)
        gmsh.model.add("mesh_example")
        
        # Parameters
        MIN_ELEM = {mesh_params['min_elem']}
        MAX_ELEM = {mesh_params['max_elem']}
        BASE_ELEM = {mesh_params['base_elem']}
        MESH_TYPE = "{mesh_type}"
        
        def add_polygon(coords):
            pts = []
            if len(coords) > 1 and coords[0] == coords[-1]:
                coords = coords[:-1]
            
            for x, y in coords:
                pts.append(gmsh.model.geo.addPoint(x, y, 0, BASE_ELEM))
            lines = []
            for i in range(len(pts)):
                next_i = (i + 1) % len(pts)
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
        
        # Set mesh algorithm based on type
        if MESH_TYPE == "quadrilateral":
            gmsh.option.setNumber("Mesh.Algorithm", 8)
            gmsh.option.setNumber("Mesh.RecombineAll", 1)
            gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)
        else:
            gmsh.option.setNumber("Mesh.Algorithm", 6)
            gmsh.option.setNumber("Mesh.RecombineAll", 0)
        
        # Generate mesh
        gmsh.model.geo.synchronize()
        gmsh.model.mesh.generate(2)
        
        # Save and read mesh
        tmpfile = tempfile.mktemp(suffix=".msh")
        gmsh.write(tmpfile)
        gmsh.finalize()
        
        mesh = meshio.read(tmpfile)
        points = mesh.points[:, :2]
        
        # Extract elements based on type
        triangles = []
        quads = []
        
        if "triangle" in mesh.cells_dict:
            triangles = mesh.cells_dict["triangle"]
        if "quad" in mesh.cells_dict:
            quads = mesh.cells_dict["quad"]
        
        # Cleanup
        os.remove(tmpfile)
        
        result = {{
            'success': True,
            'points': points.tolist(),
            'triangles': triangles.tolist() if len(triangles) > 0 else [],
            'quads': quads.tolist() if len(quads) > 0 else [],
            'outer_coords': outer_coords,
            'holes': holes,
            'num_points': len(points),
            'num_triangles': len(triangles),
            'num_quads': len(quads),
            'mesh_type': MESH_TYPE,
            'is_3d': False
        }}
        
        print(json.dumps(result))
        
    except Exception as e:
        result = {{
            'success': False,
            'error': str(e)
        }}
        print(json.dumps(result))

if __name__ == "__main__":
    create_mesh()
'''
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        # Run the script in subprocess
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Clean up script file
        os.unlink(script_path)
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': f"Script execution failed: {result.stderr}"
            }
        
        # Parse JSON result
        result_data = json.loads(result.stdout.strip())
        
        if result_data['success']:
            # Convert points back to numpy array
            result_data['points'] = np.array(result_data['points'])
            result_data['triangles'] = np.array(result_data['triangles']) if result_data['triangles'] else np.array([])
            result_data['quads'] = np.array(result_data['quads']) if result_data['quads'] else np.array([])
        
        return result_data
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': "Mesh generation timed out (30 seconds)"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def plot_mesh_2d(points, triangles, quads, title, mesh_type, figsize=(10, 6)):
    """Create 2D mesh visualization"""
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot triangles
    if len(triangles) > 0:
        for tri in triangles:
            pts = points[tri]
            ax.fill(pts[:,0], pts[:,1], edgecolor="black", fill=False, linewidth=0.5)
    
    # Plot quads
    if len(quads) > 0:
        for quad in quads:
            pts = points[quad]
            ax.fill(pts[:,0], pts[:,1], edgecolor="black", fill=False, linewidth=0.5)
    
    ax.set_aspect("equal")
    
    # Update title based on mesh type
    total_elements = len(triangles) + len(quads)
    if mesh_type == "quadrilateral":
        title_text = f"{title}\nPoints: {len(points)}, Quads: {len(quads)}, Triangles: {len(triangles)}"
    else:
        title_text = f"{title}\nPoints: {len(points)}, Triangles: {len(triangles)}"
    
    ax.set_title(title_text, fontsize=12, fontweight='bold')
    ax.set_xlabel("X [mm]", fontsize=10)
    ax.set_ylabel("Y [mm]", fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_mesh_3d(points, triangles, quads, faces, title, mesh_type):
    """Create interactive 3D surface mesh visualization with gradient colors and visible mesh lines"""
    fig = go.Figure()
    
    # Use uniform light gray color for the entire cube
    uniform_color = 'lightgray'
    
    # Plot triangular surface elements with uniform color
    if len(triangles) > 0:
        # Create a single trace for all triangles with uniform color
        tri_points = []
        tri_i = []
        tri_j = []
        tri_k = []
        
        for i, tri in enumerate(triangles):
            pts = points[tri]
            start_idx = len(tri_points)
            
            # Add points
            tri_points.extend(pts)
            
            # Add triangle indices
            tri_i.append(start_idx)
            tri_j.append(start_idx + 1)
            tri_k.append(start_idx + 2)
        
        if tri_points:
            tri_points = np.array(tri_points)
            fig.add_trace(go.Mesh3d(
                x=tri_points[:, 0],
                y=tri_points[:, 1],
                z=tri_points[:, 2],
                i=tri_i,
                j=tri_j,
                k=tri_k,
                color=uniform_color,
                opacity=1.0,
                showscale=False,
                name='Triangles',
                flatshading=True,
                lighting=dict(ambient=0.6, diffuse=0.8, specular=0.3, roughness=0.1)
            ))
    
    # Plot quadrilateral surface elements as solid squares with uniform color
    if len(quads) > 0:
        # Create individual traces for each quad to ensure solid squares
        for i, quad in enumerate(quads):
            pts = points[quad]
            
            # Create quad as two triangles with identical color and no internal divisions
            # First triangle: vertices 0, 1, 2
            # Second triangle: vertices 0, 2, 3
            quad_i = [0, 0]
            quad_j = [1, 2] 
            quad_k = [2, 3]
            
            fig.add_trace(go.Mesh3d(
                x=pts[:, 0],
                y=pts[:, 1],
                z=pts[:, 2],
                i=quad_i,
                j=quad_j,
                k=quad_k,
                color=uniform_color,
                opacity=1.0,
                showscale=False,
                name=f'Quad {i}' if i < 5 else '',  # Only show legend for first few
                flatshading=True,
                lighting=dict(ambient=0.8, diffuse=0.8, specular=0.1, roughness=0.1),
                showlegend=False if i >= 5 else True,
                hovertemplate='<b>Quad %{text}</b><br>X: %{x}<br>Y: %{y}<br>Z: %{z}<extra></extra>',
                text=[f'Quad {i}'] * 4
            ))
    
    # Add wireframe for mesh lines visibility
    if len(triangles) > 0:
        # Create wireframe for triangles
        for tri in triangles:
            pts = points[tri]
            # Add edges of triangle
            for i in range(3):
                start = pts[i]
                end = pts[(i + 1) % 3]
                fig.add_trace(go.Scatter3d(
                    x=[start[0], end[0]],
                    y=[start[1], end[1]],
                    z=[start[2], end[2]],
                    mode='lines',
                    line=dict(color='black', width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
    
    if len(quads) > 0:
        # Create wireframe for quads
        for quad in quads:
            pts = points[quad]
            # Add edges of quad
            for i in range(4):
                start = pts[i]
                end = pts[(i + 1) % 4]
                fig.add_trace(go.Scatter3d(
                    x=[start[0], end[0]],
                    y=[start[1], end[1]],
                    z=[start[2], end[2]],
                    mode='lines',
                    line=dict(color='black', width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
    
    # Update layout for better 3D visualization with light gray background
    fig.update_layout(
        title=f"{title}<br>Points: {len(points)}, Triangles: {len(triangles)}, Quads: {len(quads)}",
        scene=dict(
            xaxis_title="X [mm]",
            yaxis_title="Y [mm]", 
            zaxis_title="Z [mm]",
            aspectmode='data',
            bgcolor='lightgray',
            xaxis=dict(backgroundcolor='lightgray', gridcolor='darkgray', color='black'),
            yaxis=dict(backgroundcolor='lightgray', gridcolor='darkgray', color='black'),
            zaxis=dict(backgroundcolor='lightgray', gridcolor='darkgray', color='black')
        ),
        width=800,
        height=600,
        plot_bgcolor='lightgray',
        paper_bgcolor='lightgray',
        font=dict(color='black')
    )
    
    return fig

# Predefined geometries
PREDEFINED_GEOMETRIES = {
    "3D Cube": {
        "type": "cube",
        "dimensions": [10, 10, 10],
        "position": [0, 0, 0]
    },
    
    "3D Cylinder": {
        "type": "cylinder",
        "radius": 5,
        "height": 10,
        "position": [0, 0, 0]
    },
    
    "3D Pyramid": {
        "type": "pyramid",
        "base_size": 8,
        "height": 10,
        "position": [0, 0, 0]
    },
    
    "3D Sphere": {
        "type": "sphere",
        "radius": 5,
        "position": [0, 0, 0]
    },
    
    "3D Cone": {
        "type": "cone",
        "radius": 5,
        "height": 10,
        "position": [0, 0, 0]
    },
    
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
    
    "Rectangle with Square Hole": """
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
    """,
    
    "Star Shape": """
    POLYGON ((
      25 0,
      30 20,
      50 20,
      35 30,
      40 50,
      25 40,
      10 50,
      15 30,
      0 20,
      20 20,
      25 0
    ))
    """
}

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">🔺 CAD to 2D/3D Mesh Generator</h1>', unsafe_allow_html=True)
    st.markdown("Generate high-quality 2D and 3D meshes from WKT geometries using Gmsh with interactive 3D visualization")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Geometry type selection
        geometry_type = st.radio(
            "Choose geometry type:",
            ["2D Polygon", "3D Polyhedral Surface"],
            help="2D for flat shapes, 3D for cubes and complex 3D objects"
        )
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Predefined Geometry", "Upload WKT File", "Manual Coordinates"]
        )
        
        # Mesh type selection
        st.subheader("Mesh Type")
        mesh_type = st.radio(
            "Choose mesh element type:",
            ["triangular", "quadrilateral"],
            help="Quadrilateral meshes use squares where possible, but triangles are still used in complex areas"
        )
        
        # Mesh parameters
        st.subheader("Mesh Parameters")
        min_elem = st.slider("Minimum Element Size", 0.5, 5.0, 1.5, 0.1)
        max_elem = st.slider("Maximum Element Size", 2.0, 10.0, 5.0, 0.1)
        base_elem = st.slider("Base Element Size", 1.0, 8.0, 3.0, 0.1)
        
        mesh_params = {
            'min_elem': min_elem,
            'max_elem': max_elem,
            'base_elem': base_elem
        }
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📐 Input Geometry")
        
        wkt_input = ""
        
        if input_method == "Predefined Geometry":
            # Filter geometries based on type
            if geometry_type == "3D Polyhedral Surface":
                available_geoms = [k for k in PREDEFINED_GEOMETRIES.keys() if k.startswith("3D")]
            else:
                available_geoms = [k for k in PREDEFINED_GEOMETRIES.keys() if not k.startswith("3D")]
            
            selected_geom = st.selectbox(
                "Select a predefined geometry:",
                available_geoms
            )
            geometry_data = PREDEFINED_GEOMETRIES[selected_geom]
            
            # Show geometry info
            with st.expander("Geometry Information"):
                if geometry_type == "3D Polyhedral Surface":
                    geom_type = geometry_data['type'].title()
                    pos = geometry_data['position']
                    
                    if geom_type == "Cube":
                        dims = geometry_data['dimensions']
                        st.markdown(f"""
                        <div class="geometry-info">
                            <strong>Type:</strong> {geom_type}<br>
                            <strong>Dimensions:</strong> {dims[0]} × {dims[1]} × {dims[2]}<br>
                            <strong>Position:</strong> ({pos[0]}, {pos[1]}, {pos[2]})<br>
                            <strong>Volume:</strong> {dims[0] * dims[1] * dims[2]} cubic units
                        </div>
                        """, unsafe_allow_html=True)
                    elif geom_type == "Cylinder":
                        radius = geometry_data['radius']
                        height = geometry_data['height']
                        st.markdown(f"""
                        <div class="geometry-info">
                            <strong>Type:</strong> {geom_type}<br>
                            <strong>Radius:</strong> {radius}<br>
                            <strong>Height:</strong> {height}<br>
                            <strong>Position:</strong> ({pos[0]}, {pos[1]}, {pos[2]})<br>
                            <strong>Volume:</strong> {3.14159 * radius**2 * height:.2f} cubic units
                        </div>
                        """, unsafe_allow_html=True)
                    elif geom_type == "Pyramid":
                        base_size = geometry_data['base_size']
                        height = geometry_data['height']
                        st.markdown(f"""
                        <div class="geometry-info">
                            <strong>Type:</strong> {geom_type}<br>
                            <strong>Base Size:</strong> {base_size} × {base_size}<br>
                            <strong>Height:</strong> {height}<br>
                            <strong>Position:</strong> ({pos[0]}, {pos[1]}, {pos[2]})<br>
                            <strong>Volume:</strong> {(base_size**2 * height) / 3:.2f} cubic units
                        </div>
                        """, unsafe_allow_html=True)
                    elif geom_type == "Sphere":
                        radius = geometry_data['radius']
                        st.markdown(f"""
                        <div class="geometry-info">
                            <strong>Type:</strong> {geom_type}<br>
                            <strong>Radius:</strong> {radius}<br>
                            <strong>Position:</strong> ({pos[0]}, {pos[1]}, {pos[2]})<br>
                            <strong>Volume:</strong> {(4/3) * 3.14159 * radius**3:.2f} cubic units
                        </div>
                        """, unsafe_allow_html=True)
                    elif geom_type == "Cone":
                        radius = geometry_data['radius']
                        height = geometry_data['height']
                        st.markdown(f"""
                        <div class="geometry-info">
                            <strong>Type:</strong> {geom_type}<br>
                            <strong>Radius:</strong> {radius}<br>
                            <strong>Height:</strong> {height}<br>
                            <strong>Position:</strong> ({pos[0]}, {pos[1]}, {pos[2]})<br>
                            <strong>Volume:</strong> {(1/3) * 3.14159 * radius**2 * height:.2f} cubic units
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    try:
                        geom = wkt.loads(geometry_data)
                        outer_coords = list(geom.exterior.coords)
                        holes = [list(ring.coords) for ring in geom.interiors]
                        
                        st.markdown(f"""
                        <div class="geometry-info">
                            <strong>Outer boundary:</strong> {len(outer_coords)} points<br>
                            <strong>Holes:</strong> {len(holes)}<br>
                            <strong>Area:</strong> {geom.area:.2f} square units
                        </div>
                        """, unsafe_allow_html=True)
                    except:
                        st.error("Invalid WKT geometry")
        
        elif input_method == "Upload WKT File":
            uploaded_file = st.file_uploader(
                "Upload a WKT file:",
                type=['txt', 'wkt'],
                help="Upload a text file containing WKT polygon data"
            )
            
            if uploaded_file is not None:
                try:
                    wkt_input = uploaded_file.read().decode('utf-8')
                    st.success("File uploaded successfully!")
                    
                    # Show preview
                    with st.expander("WKT Preview"):
                        st.code(wkt_input, language="text")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
        
        elif input_method == "Manual Coordinates":
            st.subheader("Enter Coordinates Manually")
            
            # Outer boundary
            st.write("**Outer Boundary Coordinates:**")
            outer_coords_input = st.text_area(
                "Enter coordinates as 'x1,y1; x2,y2; x3,y3; ...'",
                value="0,0; 30,0; 30,20; 10,20; 10,30; 0,30",
                help="Separate coordinates with semicolons, use comma for x,y"
            )
            
            # Holes (optional)
            st.write("**Holes (Optional):**")
            num_holes = st.number_input("Number of holes", 0, 5, 0)
            
            holes_input = []
            for i in range(num_holes):
                hole_coords = st.text_input(
                    f"Hole {i+1} coordinates:",
                    value="15,15; 25,15; 25,25; 15,25",
                    key=f"hole_{i}"
                )
                if hole_coords.strip():
                    holes_input.append(hole_coords)
            
            # Convert to WKT
            if outer_coords_input.strip():
                try:
                    # Parse outer coordinates
                    outer_points = []
                    for coord in outer_coords_input.split(';'):
                        x, y = map(float, coord.strip().split(','))
                        outer_points.append(f"{x} {y}")
                    
                    # Add first point at the end to close the polygon
                    outer_points.append(outer_points[0])
                    
                    # Parse holes
                    hole_rings = []
                    for hole_coords in holes_input:
                        hole_points = []
                        for coord in hole_coords.split(';'):
                            x, y = map(float, coord.strip().split(','))
                            hole_points.append(f"{x} {y}")
                        hole_points.append(hole_points[0])  # Close the hole
                        hole_rings.append(f"({', '.join(hole_points)})")
                    
                    # Construct WKT
                    wkt_parts = [f"({', '.join(outer_points)})"]
                    wkt_parts.extend(hole_rings)
                    wkt_input = f"POLYGON ({', '.join(wkt_parts)})"
                    
                    st.success("WKT generated successfully!")
                    with st.expander("Generated WKT"):
                        st.code(wkt_input, language="text")
                        
                except Exception as e:
                    st.error(f"Error parsing coordinates: {e}")
                    wkt_input = ""
    
    with col2:
        st.header("🔺 Generated Mesh")
        
        if geometry_data:
            if st.button("Generate Mesh", type="primary"):
                is_3d = (geometry_type == "3D Polyhedral Surface")
                with st.spinner("Generating mesh..."):
                    if is_3d:
                        result = create_mesh_from_geometry(geometry_data, "Generated Mesh", mesh_params, mesh_type, is_3d)
                    else:
                        # For 2D geometries, we still need to handle WKT strings
                        result = create_mesh_from_wkt(geometry_data, "Generated Mesh", mesh_params, mesh_type, is_3d)
                
                if result['success']:
                    # Display metrics
                    if is_3d:
                        col1_metric, col2_metric, col3_metric = st.columns(3)
                        with col1_metric:
                            st.metric("Points", result['num_points'])
                        with col2_metric:
                            st.metric("Triangles", result['num_triangles'])
                        with col3_metric:
                            st.metric("Quads", result['num_quads'])
                    else:
                        if mesh_type == "quadrilateral":
                            col1_metric, col2_metric, col3_metric = st.columns(3)
                            with col1_metric:
                                st.metric("Points", result['num_points'])
                            with col2_metric:
                                st.metric("Quads", result['num_quads'])
                            with col3_metric:
                                st.metric("Triangles", result['num_triangles'])
                        else:
                            col1_metric, col2_metric = st.columns(2)
                            with col1_metric:
                                st.metric("Points", result['num_points'])
                            with col2_metric:
                                st.metric("Triangles", result['num_triangles'])
                    
                    # Plot mesh
                    if is_3d:
                        fig = plot_mesh_3d(result['points'], result['triangles'], result['quads'], 
                                         result['faces'], "Generated 3D Surface Mesh", mesh_type)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        fig = plot_mesh_2d(result['points'], result['triangles'], result['quads'], 
                                         "Generated 2D Mesh", mesh_type)
                        st.pyplot(fig)
                    
                    # Download options
                    st.subheader("📥 Download Options")
                    
                    col1_dl, col2_dl = st.columns(2)
                    
                    if is_3d:
                        # For 3D plots, save as HTML
                        with col1_dl:
                            html_str = fig.to_html()
                            st.download_button(
                                label="Download 3D Visualization (HTML)",
                                data=html_str,
                                file_name="3d_mesh_visualization.html",
                                mime="text/html"
                            )
                    else:
                        # For 2D plots, save as PNG
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                        buf.seek(0)
                        
                        with col1_dl:
                            st.download_button(
                                label="Download PNG",
                                data=buf.getvalue(),
                                file_name="mesh_visualization.png",
                                mime="image/png"
                            )
                    
                    # Save mesh data
                    if is_3d:
                        mesh_data = {
                            'points': result['points'].tolist(),
                            'triangles': result['triangles'].tolist() if len(result['triangles']) > 0 else [],
                            'quads': result['quads'].tolist() if len(result['quads']) > 0 else [],
                            'faces': result['faces'],
                            'num_points': result['num_points'],
                            'num_triangles': result['num_triangles'],
                            'num_quads': result['num_quads'],
                            'mesh_type': mesh_type,
                            'is_3d': True
                        }
                    else:
                        mesh_data = {
                            'points': result['points'].tolist(),
                            'triangles': result['triangles'].tolist() if len(result['triangles']) > 0 else [],
                            'quads': result['quads'].tolist() if len(result['quads']) > 0 else [],
                            'num_points': result['num_points'],
                            'num_triangles': result['num_triangles'],
                            'num_quads': result['num_quads'],
                            'mesh_type': mesh_type,
                            'is_3d': False
                        }
                    
                    json_data = json.dumps(mesh_data, indent=2)
                    
                    with col2_dl:
                        st.download_button(
                            label="Download Mesh Data (JSON)",
                            data=json_data,
                            file_name="mesh_data.json",
                            mime="application/json"
                        )
                    
                    # Geometry details
                    with st.expander("Geometry Details"):
                        st.write(f"**Geometry Type:** {'3D' if is_3d else '2D'}")
                        st.write(f"**Mesh Type:** {mesh_type.title()}")
                        
                        if is_3d:
                            st.write(f"**Number of faces:** {len(result['faces'])}")
                            st.write(f"**Triangular elements:** {result['num_triangles']}")
                            st.write(f"**Quadrilateral elements:** {result['num_quads']}")
                            st.write(f"**Total surface elements:** {result['num_triangles'] + result['num_quads']}")
                            
                            st.write("**Face details:**")
                            for i, face in enumerate(result['faces']):
                                st.write(f"  - Face {i+1}: {len(face)} points")
                        else:
                            st.write(f"**Outer boundary points:** {len(result['outer_coords'])}")
                            st.write(f"**Number of holes:** {len(result['holes'])}")
                            
                            if mesh_type == "quadrilateral":
                                st.write(f"**Quadrilateral elements:** {result['num_quads']}")
                                st.write(f"**Triangular elements:** {result['num_triangles']}")
                                st.write(f"**Total elements:** {result['num_quads'] + result['num_triangles']}")
                            else:
                                st.write(f"**Triangular elements:** {result['num_triangles']}")
                            
                            if result['holes']:
                                st.write("**Hole details:**")
                                for i, hole in enumerate(result['holes']):
                                    st.write(f"  - Hole {i+1}: {len(hole)} points")
                
                else:
                    st.error(f"Mesh generation failed: {result['error']}")
        else:
            st.info("Please provide WKT geometry input to generate mesh")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🔺 CAD to 2D Mesh Generator | Powered by Gmsh, Shapely, and Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

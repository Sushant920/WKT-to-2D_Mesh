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

# Page configuration
st.set_page_config(
    page_title="CAD to 2D Mesh Generator",
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

def create_mesh_script(wkt_polygon, mesh_params):
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
        # Parse WKT geometry
        from shapely import wkt
        geom = wkt.loads("""{wkt_polygon}""")
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
        
        # Cleanup
        os.remove(tmpfile)
        
        # Return results as JSON
        result = {{
            'success': True,
            'points': points.tolist(),
            'triangles': triangles.tolist(),
            'outer_coords': outer_coords,
            'holes': holes,
            'num_points': len(points),
            'num_triangles': len(triangles)
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

def create_mesh_from_wkt(wkt_polygon, title, mesh_params):
    """Create a 2D mesh from WKT polygon using subprocess"""
    try:
        # Create temporary script
        script_content = create_mesh_script(wkt_polygon, mesh_params)
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        # Run the script in subprocess
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
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
            result_data['triangles'] = np.array(result_data['triangles'])
        
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

def plot_mesh(points, triangles, title, figsize=(10, 6)):
    """Create mesh visualization"""
    fig, ax = plt.subplots(figsize=figsize)
    
    for tri in triangles:
        pts = points[tri]
        ax.fill(pts[:,0], pts[:,1], edgecolor="black", fill=False, linewidth=0.5)
    
    ax.set_aspect("equal")
    ax.set_title(f"{title}\nPoints: {len(points)}, Triangles: {len(triangles)}", 
                 fontsize=12, fontweight='bold')
    ax.set_xlabel("X [mm]", fontsize=10)
    ax.set_ylabel("Y [mm]", fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

# Predefined geometries
PREDEFINED_GEOMETRIES = {
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
    st.markdown('<h1 class="main-header">🔺 CAD to 2D Mesh Generator</h1>', unsafe_allow_html=True)
    st.markdown("Generate high-quality 2D meshes from WKT geometries using Gmsh")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Predefined Geometry", "Upload WKT File", "Manual Coordinates"]
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
            selected_geom = st.selectbox(
                "Select a predefined geometry:",
                list(PREDEFINED_GEOMETRIES.keys())
            )
            wkt_input = PREDEFINED_GEOMETRIES[selected_geom]
            
            # Show geometry info
            with st.expander("Geometry Information"):
                try:
                    geom = wkt.loads(wkt_input)
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
        
        if wkt_input:
            if st.button("Generate Mesh", type="primary"):
                with st.spinner("Generating mesh..."):
                    result = create_mesh_from_wkt(wkt_input, "Generated Mesh", mesh_params)
                
                if result['success']:
                    # Display metrics
                    col1_metric, col2_metric = st.columns(2)
                    with col1_metric:
                        st.metric("Points", result['num_points'])
                    with col2_metric:
                        st.metric("Triangles", result['num_triangles'])
                    
                    # Plot mesh
                    fig = plot_mesh(result['points'], result['triangles'], "Generated Mesh")
                    st.pyplot(fig)
                    
                    # Download options
                    st.subheader("📥 Download Options")
                    
                    # Save as PNG
                    buf = io.BytesIO()
                    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                    buf.seek(0)
                    
                    col1_dl, col2_dl = st.columns(2)
                    with col1_dl:
                        st.download_button(
                            label="Download PNG",
                            data=buf.getvalue(),
                            file_name="mesh_visualization.png",
                            mime="image/png"
                        )
                    
                    # Save mesh data
                    mesh_data = {
                        'points': result['points'].tolist(),
                        'triangles': result['triangles'].tolist(),
                        'num_points': result['num_points'],
                        'num_triangles': result['num_triangles']
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
                        st.write(f"**Outer boundary points:** {len(result['outer_coords'])}")
                        st.write(f"**Number of holes:** {len(result['holes'])}")
                        
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

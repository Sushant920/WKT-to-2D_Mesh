#!/usr/bin/env python3
"""
Streamlit 3D CAD to Mesh Application - Fixed Version
Interactive UI for generating 3D meshes from various geometries
"""

import streamlit as st
import subprocess
import tempfile
import os
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import io

# Page configuration
st.set_page_config(
    page_title="3D CAD to Mesh Generator",
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

def create_3d_mesh_script(geometry_type, geometry_params, mesh_params):
    """Create a temporary Python script for 3D mesh generation"""
    script_content = f'''
import gmsh
import meshio
import json
import tempfile
import os
import sys
import numpy as np

def create_3d_mesh():
    try:
        # Initialize Gmsh
        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.Verbosity", 0)
        gmsh.model.add("3d_mesh_example")
        
        # Parameters
        MIN_ELEM = {mesh_params['min_elem']}
        MAX_ELEM = {mesh_params['max_elem']}
        BASE_ELEM = {mesh_params['base_elem']}
        
        geometry_type = "{geometry_type}"
        geometry_params = {json.dumps(geometry_params)}
        
        if geometry_type == "Box":
            # Create a box using Gmsh's built-in box
            x, y, z = geometry_params['center']
            lx, ly, lz = geometry_params['dimensions']
            
            # Use Gmsh's built-in box function
            box = gmsh.model.occ.addBox(x-lx/2, y-ly/2, z-lz/2, lx, ly, lz)
            gmsh.model.occ.synchronize()
            
        elif geometry_type == "Cylinder":
            # Create a cylinder using Gmsh's built-in cylinder
            x, y, z = geometry_params['center']
            r = geometry_params['radius']
            h = geometry_params['height']
            
            # Use Gmsh's built-in cylinder function
            cylinder = gmsh.model.occ.addCylinder(x, y, z, 0, 0, h, r)
            gmsh.model.occ.synchronize()
            
        elif geometry_type == "Sphere":
            # Create a sphere using Gmsh's built-in sphere
            x, y, z = geometry_params['center']
            r = geometry_params['radius']
            
            # Use Gmsh's built-in sphere function
            sphere = gmsh.model.occ.addSphere(x, y, z, r)
            gmsh.model.occ.synchronize()
            
        elif geometry_type == "Torus":
            # Create a torus using Gmsh's built-in torus
            x, y, z = geometry_params['center']
            r1 = geometry_params['major_radius']
            r2 = geometry_params['minor_radius']
            
            # Use Gmsh's built-in torus function
            torus = gmsh.model.occ.addTorus(x, y, z, r1, r2)
            gmsh.model.occ.synchronize()
            
        elif geometry_type == "Cone":
            # Create a cone using Gmsh's built-in cone
            x, y, z = geometry_params['center']
            r1 = geometry_params['bottom_radius']
            r2 = geometry_params['top_radius']
            h = geometry_params['height']
            
            # Use Gmsh's built-in cone function
            cone = gmsh.model.occ.addCone(x, y, z, 0, 0, h, r1, r2)
            gmsh.model.occ.synchronize()
        
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
        gmsh.model.mesh.generate(3)
        
        # Save and read mesh
        tmpfile = tempfile.mktemp(suffix=".msh")
        gmsh.write(tmpfile)
        gmsh.finalize()
        
        mesh = meshio.read(tmpfile)
        points = mesh.points
        tetrahedra = mesh.cells_dict.get("tetra", np.array([]).reshape(0, 4))
        hexahedra = mesh.cells_dict.get("hexahedron", np.array([]).reshape(0, 8))
        
        # Cleanup
        os.remove(tmpfile)
        
        # Return results as JSON
        result = {{
            'success': True,
            'points': points.tolist(),
            'tetrahedra': tetrahedra.tolist(),
            'hexahedra': hexahedra.tolist(),
            'num_points': len(points),
            'num_tetrahedra': len(tetrahedra),
            'num_hexahedra': len(hexahedra),
            'geometry_type': geometry_type,
            'geometry_params': geometry_params
        }}
        
        print(json.dumps(result))
        
    except Exception as e:
        result = {{
            'success': False,
            'error': str(e)
        }}
        print(json.dumps(result))

if __name__ == "__main__":
    create_3d_mesh()
'''
    return script_content

def create_3d_mesh_from_params(geometry_type, geometry_params, mesh_params):
    """Create a 3D mesh using subprocess"""
    try:
        # Create temporary script
        script_content = create_3d_mesh_script(geometry_type, geometry_params, mesh_params)
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        # Run the script in subprocess
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout for 3D meshing
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
            result_data['tetrahedra'] = np.array(result_data['tetrahedra'])
            result_data['hexahedra'] = np.array(result_data['hexahedra'])
        
        return result_data
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': "3D mesh generation timed out (60 seconds)"
        }
    except Exception as e:
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
        for tet in tetrahedra[:100]:  # Limit for performance
            pts = points[tet]
            # Create faces of tetrahedron using wireframe
            # Face 1: points 0,1,2
            ax.plot([pts[0,0], pts[1,0], pts[2,0], pts[0,0]], 
                   [pts[0,1], pts[1,1], pts[2,1], pts[0,1]], 
                   [pts[0,2], pts[1,2], pts[2,2], pts[0,2]], 'b-', alpha=0.3, linewidth=0.5)
            # Face 2: points 0,1,3
            ax.plot([pts[0,0], pts[1,0], pts[3,0], pts[0,0]], 
                   [pts[0,1], pts[1,1], pts[3,1], pts[0,1]], 
                   [pts[0,2], pts[1,2], pts[3,2], pts[0,2]], 'b-', alpha=0.3, linewidth=0.5)
            # Face 3: points 0,2,3
            ax.plot([pts[0,0], pts[2,0], pts[3,0], pts[0,0]], 
                   [pts[0,1], pts[2,1], pts[3,1], pts[0,1]], 
                   [pts[0,2], pts[2,2], pts[3,2], pts[0,2]], 'b-', alpha=0.3, linewidth=0.5)
            # Face 4: points 1,2,3
            ax.plot([pts[1,0], pts[2,0], pts[3,0], pts[1,0]], 
                   [pts[1,1], pts[2,1], pts[3,1], pts[1,1]], 
                   [pts[1,2], pts[2,2], pts[3,2], pts[1,2]], 'b-', alpha=0.3, linewidth=0.5)
    
    # Plot hexahedra (limit for performance)
    if len(hexahedra) > 0:
        for hexa in hexahedra[:50]:  # Limit for performance
            pts = points[hexa]
            # Create wireframe of hexahedron
            # Bottom face
            ax.plot([pts[0,0], pts[1,0], pts[2,0], pts[3,0], pts[0,0]], 
                   [pts[0,1], pts[1,1], pts[2,1], pts[3,1], pts[0,1]], 
                   [pts[0,2], pts[1,2], pts[2,2], pts[3,2], pts[0,2]], 'g-', alpha=0.3, linewidth=0.5)
            # Top face
            ax.plot([pts[4,0], pts[5,0], pts[6,0], pts[7,0], pts[4,0]], 
                   [pts[4,1], pts[5,1], pts[6,1], pts[7,1], pts[4,1]], 
                   [pts[4,2], pts[5,2], pts[6,2], pts[7,2], pts[4,2]], 'g-', alpha=0.3, linewidth=0.5)
            # Vertical edges
            for i in range(4):
                ax.plot([pts[i,0], pts[i+4,0]], 
                       [pts[i,1], pts[i+4,1]], 
                       [pts[i,2], pts[i+4,2]], 'g-', alpha=0.3, linewidth=0.5)
    
    # Plot points
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], c='red', s=2, alpha=0.8)
    
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

# Predefined 3D geometries
PREDEFINED_3D_GEOMETRIES = {
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

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">🔺 3D CAD to Mesh Generator</h1>', unsafe_allow_html=True)
    st.markdown("Generate high-quality 3D meshes from various geometries using Gmsh")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Geometry selection
        geometry_type = st.selectbox(
            "Select 3D geometry:",
            list(PREDEFINED_3D_GEOMETRIES.keys())
        )
        
        # Geometry parameters
        st.subheader("Geometry Parameters")
        geometry_params = PREDEFINED_3D_GEOMETRIES[geometry_type].copy()
        
        if geometry_type == "Box":
            st.write("**Box Dimensions:**")
            geometry_params['center'][0] = st.number_input("Center X", value=float(geometry_params['center'][0]))
            geometry_params['center'][1] = st.number_input("Center Y", value=float(geometry_params['center'][1]))
            geometry_params['center'][2] = st.number_input("Center Z", value=float(geometry_params['center'][2]))
            geometry_params['dimensions'][0] = st.number_input("Length X", value=float(geometry_params['dimensions'][0]), min_value=1.0)
            geometry_params['dimensions'][1] = st.number_input("Length Y", value=float(geometry_params['dimensions'][1]), min_value=1.0)
            geometry_params['dimensions'][2] = st.number_input("Length Z", value=float(geometry_params['dimensions'][2]), min_value=1.0)
            
        elif geometry_type == "Cylinder":
            st.write("**Cylinder Parameters:**")
            geometry_params['center'][0] = st.number_input("Center X", value=float(geometry_params['center'][0]))
            geometry_params['center'][1] = st.number_input("Center Y", value=float(geometry_params['center'][1]))
            geometry_params['center'][2] = st.number_input("Center Z", value=float(geometry_params['center'][2]))
            geometry_params['radius'] = st.number_input("Radius", value=float(geometry_params['radius']), min_value=0.1)
            geometry_params['height'] = st.number_input("Height", value=float(geometry_params['height']), min_value=0.1)
            
        elif geometry_type == "Sphere":
            st.write("**Sphere Parameters:**")
            geometry_params['center'][0] = st.number_input("Center X", value=float(geometry_params['center'][0]))
            geometry_params['center'][1] = st.number_input("Center Y", value=float(geometry_params['center'][1]))
            geometry_params['center'][2] = st.number_input("Center Z", value=float(geometry_params['center'][2]))
            geometry_params['radius'] = st.number_input("Radius", value=float(geometry_params['radius']), min_value=0.1)
            
        elif geometry_type == "Torus":
            st.write("**Torus Parameters:**")
            geometry_params['center'][0] = st.number_input("Center X", value=float(geometry_params['center'][0]))
            geometry_params['center'][1] = st.number_input("Center Y", value=float(geometry_params['center'][1]))
            geometry_params['center'][2] = st.number_input("Center Z", value=float(geometry_params['center'][2]))
            geometry_params['major_radius'] = st.number_input("Major Radius", value=float(geometry_params['major_radius']), min_value=0.1)
            geometry_params['minor_radius'] = st.number_input("Minor Radius", value=float(geometry_params['minor_radius']), min_value=0.1)
            
        elif geometry_type == "Cone":
            st.write("**Cone Parameters:**")
            geometry_params['center'][0] = st.number_input("Center X", value=float(geometry_params['center'][0]))
            geometry_params['center'][1] = st.number_input("Center Y", value=float(geometry_params['center'][1]))
            geometry_params['center'][2] = st.number_input("Center Z", value=float(geometry_params['center'][2]))
            geometry_params['bottom_radius'] = st.number_input("Bottom Radius", value=float(geometry_params['bottom_radius']), min_value=0.1)
            geometry_params['top_radius'] = st.number_input("Top Radius", value=float(geometry_params['top_radius']), min_value=0.0)
            geometry_params['height'] = st.number_input("Height", value=float(geometry_params['height']), min_value=0.1)
        
        # Mesh parameters
        st.subheader("Mesh Parameters")
        min_elem = st.slider("Minimum Element Size", 0.5, 5.0, 2.0, 0.1)
        max_elem = st.slider("Maximum Element Size", 2.0, 15.0, 8.0, 0.1)
        base_elem = st.slider("Base Element Size", 1.0, 10.0, 4.0, 0.1)
        
        mesh_params = {
            'min_elem': min_elem,
            'max_elem': max_elem,
            'base_elem': base_elem
        }
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📐 3D Geometry")
        
        # Show geometry info
        with st.expander("Geometry Information"):
            st.write(f"**Type:** {geometry_type}")
            st.write(f"**Parameters:**")
            for key, value in geometry_params.items():
                if isinstance(value, list):
                    st.write(f"  - {key}: {value}")
                else:
                    st.write(f"  - {key}: {value}")
    
    with col2:
        st.header("🔺 Generated 3D Mesh")
        
        if st.button("Generate 3D Mesh", type="primary"):
            with st.spinner("Generating 3D mesh..."):
                result = create_3d_mesh_from_params(geometry_type, geometry_params, mesh_params)
            
            if result['success']:
                # Display metrics
                col1_metric, col2_metric, col3_metric = st.columns(3)
                with col1_metric:
                    st.metric("Points", result['num_points'])
                with col2_metric:
                    st.metric("Tetrahedra", result['num_tetrahedra'])
                with col3_metric:
                    st.metric("Hexahedra", result['num_hexahedra'])
                
                # Plot 3D mesh
                fig = plot_3d_mesh(result['points'], result['tetrahedra'], result['hexahedra'], "Generated 3D Mesh")
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
                        file_name="3d_mesh_visualization.png",
                        mime="image/png"
                    )
                
                # Save mesh data
                mesh_data = {
                    'points': result['points'].tolist(),
                    'tetrahedra': result['tetrahedra'].tolist(),
                    'hexahedra': result['hexahedra'].tolist(),
                    'num_points': result['num_points'],
                    'num_tetrahedra': result['num_tetrahedra'],
                    'num_hexahedra': result['num_hexahedra'],
                    'geometry_type': result['geometry_type'],
                    'geometry_params': result['geometry_params']
                }
                
                json_data = json.dumps(mesh_data, indent=2)
                
                with col2_dl:
                    st.download_button(
                        label="Download Mesh Data (JSON)",
                        data=json_data,
                        file_name="3d_mesh_data.json",
                        mime="application/json"
                    )
                
                # Geometry details
                with st.expander("Mesh Details"):
                    st.write(f"**Total elements:** {result['num_tetrahedra'] + result['num_hexahedra']}")
                    st.write(f"**Element types:** Tetrahedra and Hexahedra")
                    st.write(f"**Mesh quality:** High-quality 3D mesh")
            
            else:
                st.error(f"3D mesh generation failed: {result['error']}")
        else:
            st.info("Click 'Generate 3D Mesh' to create a 3D mesh from the selected geometry")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🔺 3D CAD to Mesh Generator | Powered by Gmsh and Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

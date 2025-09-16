# CAD to 2D Mesh Generator

A comprehensive Python application for generating high-quality 2D meshes from WKT (Well-Known Text) geometries using Gmsh and visualizing them with Matplotlib.

## 🚀 Features

### Streamlit Web Application (`streamlit_mesh_app.py`)
- **Interactive UI** for mesh generation
- **Multiple input methods:**
  - Predefined geometries (L-Shape, T-Shape, Hexagon, etc.)
  - Upload custom WKT files
  - Manual coordinate entry
- **Adjustable mesh parameters:**
  - Minimum/Maximum element sizes
  - Base element size
- **Real-time visualization** with mesh statistics
- **Download options:**
  - High-resolution PNG images
  - Mesh data in JSON format

### Command-line Scripts
- **`run_cad_mesh.py`** - Single geometry mesh generation
- **`multiple_mesh_examples.py`** - Batch processing of multiple geometries

## 📦 Dependencies

```bash
pip install gmsh shapely meshio matplotlib streamlit
```

## 🎯 Usage

### Streamlit Web App (Recommended)
```bash
streamlit run streamlit_mesh_app.py
```
Then open your browser to `http://localhost:8501`

### Command Line
```bash
# Single geometry
python3 run_cad_mesh.py

# Multiple geometries
python3 multiple_mesh_examples.py
```

## 🔧 Supported Geometries

### Predefined Shapes
1. **L-Shape** - Classic L-shaped geometry
2. **Rectangle with Square Hole** - Rectangular domain with square cutout
3. **Complex Shape** - Multi-segment complex geometry
4. **T-Shape** - T-shaped structure
5. **Multiple Holes** - Rectangle with multiple square holes
6. **Hexagon** - Regular hexagonal shape
7. **Star Shape** - 5-pointed star geometry

### Custom Input
- **WKT File Upload** - Upload `.txt` or `.wkt` files
- **Manual Coordinates** - Enter coordinates directly in the UI

## 📊 Output

Each mesh generation produces:
- **Visualization** - High-quality PNG with mesh overlay
- **Statistics** - Point count, triangle count, area
- **Mesh Data** - JSON format with coordinates and connectivity
- **Geometry Info** - Boundary points, holes, area calculations

## 🎨 Sample Outputs

The application generates various mesh visualizations:
- `mesh_l_shape.png` - L-shaped geometry mesh
- `mesh_circle_with_square_hole.png` - Rectangle with hole
- `mesh_complex_shape.png` - Complex multi-segment geometry
- `mesh_t_shape.png` - T-shaped structure mesh
- `mesh_multiple_holes.png` - Multiple holes geometry
- `mesh_hexagon.png` - Hexagonal mesh
- `mesh_visualization.png` - Original example output

## 🔬 Technical Details

- **Mesh Engine**: Gmsh 4.14+
- **Geometry Processing**: Shapely
- **Visualization**: Matplotlib
- **Web Interface**: Streamlit
- **Mesh Format**: Gmsh .msh files (temporary)

## 📈 Performance

Typical mesh generation times:
- Simple geometries: 0.01-0.05 seconds
- Complex geometries: 0.1-0.5 seconds
- Multiple holes: 0.2-1.0 seconds

## 🛠️ Customization

### Mesh Parameters
- **Minimum Element Size**: 0.5 - 5.0 mm
- **Maximum Element Size**: 2.0 - 10.0 mm  
- **Base Element Size**: 1.0 - 8.0 mm

### Adding New Geometries
Edit the `PREDEFINED_GEOMETRIES` dictionary in `streamlit_mesh_app.py`:

```python
"Your Shape": """
POLYGON ((
  x1 y1,
  x2 y2,
  x3 y3,
  ...
  x1 y1
))
"""
```

## 📝 WKT Format

The application accepts standard WKT POLYGON format:
```wkt
POLYGON ((
  x1 y1,
  x2 y2,
  x3 y3,
  ...
  x1 y1
), (
  hole_x1 hole_y1,
  hole_x2 hole_y2,
  ...
  hole_x1 hole_y1
))
```

## 🎯 Use Cases

- **CAD Analysis** - Convert CAD geometries to meshes
- **FEA Preprocessing** - Prepare geometries for finite element analysis
- **Educational** - Learn about mesh generation and WKT formats
- **Research** - Prototype mesh generation workflows
- **Visualization** - Create high-quality mesh visualizations

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

---

**🔺 CAD to 2D Mesh Generator** | Powered by Gmsh, Shapely, and Streamlit

# 3D Mesh Generator

A comprehensive Python application for generating high-quality 3D surface meshes from various 3D geometries using Gmsh and visualizing them with interactive 3D plots using Plotly.

## 🚀 Features

### Interactive 3D Mesh Generation
- **Multiple 3D Geometries:**
  - 3D Cube - Rectangular box geometry
  - 3D Cylinder - Circular cylinder
  - 3D Pyramid - Square-based pyramid
  - 3D Sphere - Perfect sphere
  - 3D Cone - Circular cone
- **Mesh Types:**
  - Triangular meshes
  - Quadrilateral meshes (with automatic triangle fallback)
- **Interactive 3D Visualization:**
  - Pan, zoom, and 360° rotation
  - Solid light gray coloring with black mesh lines
  - Professional engineering appearance

### 2D Mesh Support
- **2D Geometries:**
  - L-Shape, T-Shape, Hexagon
  - Rectangle with holes
  - Complex multi-segment shapes
- **WKT Input Support:**
  - Upload custom WKT files
  - Manual coordinate entry

## 📦 Dependencies

```bash
pip install gmsh shapely meshio matplotlib streamlit plotly numpy
```

## 🎯 Usage

### Streamlit Web App (Main Application)
```bash
streamlit run streamlit_mesh_app_fixed.py
```
Then open your browser to `http://localhost:8501`

## 🔧 Supported Geometries

### 3D Geometries
1. **3D Cube** - 10×10×10 units with customizable dimensions
2. **3D Cylinder** - Radius: 5, Height: 10
3. **3D Pyramid** - Base size: 8×8, Height: 10
4. **3D Sphere** - Radius: 5
5. **3D Cone** - Radius: 5, Height: 10

### 2D Geometries
1. **L-Shape** - Classic L-shaped geometry
2. **Rectangle with Square Hole** - Rectangular domain with square cutout
3. **Complex Shape** - Multi-segment complex geometry
4. **T-Shape** - T-shaped structure
5. **Multiple Holes** - Rectangle with multiple square holes
6. **Hexagon** - Regular hexagonal shape

## 📊 Output Features

### 3D Visualization
- **Interactive 3D plots** with pan, zoom, and rotation
- **Solid light gray coloring** for professional appearance
- **Clear black mesh lines** for element visibility
- **Surface meshing only** - no interior volume meshing
- **Download as HTML** for sharing and presentation

### 2D Visualization
- **High-quality PNG images** with mesh overlay
- **Download as PNG** for documentation
- **Mesh statistics** - point count, element count, area

### Mesh Data
- **JSON format** with coordinates and connectivity
- **Element statistics** - triangles, quadrilaterals
- **Geometry information** - dimensions, volume, area

## 🎨 Visual Features

### 3D Meshes
- **Uniform light gray color** across all surfaces
- **Black wireframe lines** showing mesh structure
- **No internal divisions** in quadrilateral elements
- **Professional engineering appearance**

### 2D Meshes
- **Color-coded elements** for easy identification
- **Clear boundary visualization**
- **Hole detection and display**

## 🔬 Technical Details

- **Mesh Engine**: Gmsh 4.14+
- **3D Visualization**: Plotly
- **2D Visualization**: Matplotlib
- **Geometry Processing**: Shapely
- **Web Interface**: Streamlit
- **Mesh Format**: Gmsh .msh files (temporary)

## 📈 Performance

Typical mesh generation times:
- Simple 3D geometries: 0.1-0.5 seconds
- Complex 3D geometries: 0.5-2.0 seconds
- 2D geometries: 0.01-0.1 seconds

## 🛠️ Customization

### Mesh Parameters
- **Minimum Element Size**: 0.5 - 5.0 mm
- **Maximum Element Size**: 2.0 - 10.0 mm  
- **Base Element Size**: 1.0 - 8.0 mm

### Mesh Types
- **Triangular**: Classic triangular elements
- **Quadrilateral**: Square elements where possible, triangles in complex areas

## 🎯 Use Cases

- **3D CAD Analysis** - Convert 3D geometries to surface meshes
- **FEA Preprocessing** - Prepare 3D surfaces for finite element analysis
- **Engineering Visualization** - Create professional 3D mesh visualizations
- **Educational** - Learn about 3D mesh generation
- **Research** - Prototype 3D mesh generation workflows
- **Quality Control** - Inspect mesh quality and element distribution

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

---

**🔺 3D Mesh Generator** | Powered by Gmsh, Plotly, and Streamlit
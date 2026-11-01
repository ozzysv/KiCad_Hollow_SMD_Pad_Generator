KiCad Hollow SMD Pad Generator

A Python GUI tool for creating hollow, rounded-rectangle SMD footprints for KiCad, particularly for EMI/RFI shielding cans. Customize dimensions, corner radii, copper rim width, and shield wall thickness. The tool supports segmented `F.Paste` apertures, `F.Fab` outlines, automatic `F.CrtYd`, STEP/STP model preview and embedding, and `.kicad_mod` export.

### Main window
Set footprint dimensions and options with a live 2D preview.

![Main window](img/main_win.png)

### 3D preview
Load a STEP/STP model, inspect its placement on the pad, and adjust orientation and offset.

![3D preview](img/3d_preview.png)

### Generated footprint in KiCad
The hollow SMD pad opened in the KiCad Footprint Editor.

![Generated footprint](img/result.png)

### 3D model in KiCad
The STEP model embedded in the footprint and displayed in KiCad's 3D preview.

![3D model in KiCad](img/result_3d.png)

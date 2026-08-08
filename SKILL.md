# Image to Visio Skill

## Goal
Convert images, screenshots, papers and diagrams into real editable Microsoft Visio `.vsdx` files.

## Rules
- Never use a full-page source image as a fake editable result.
- Rebuild titles, text, tables, boxes, connectors, flows and diagrams as independent Visio shapes.
- Keep only unavoidable raster content such as scans, photos and book pages.
- Preserve geometry, alignment, spacing and typography hierarchy.

## Workflow
1. Analyze source image dimensions and layout.
2. Split into semantic regions.
3. Recreate with vector shapes and editable text.
4. Use a known-good Visio package structure.
5. Export VSDX → PDF → PNG.
6. Run structural and pixel QA.

## QA requirements
- Check VSDX XML validity.
- Detect full-page raster cheating.
- Verify exported image dimensions.
- Generate pixel difference report.

## Deliverables
- Editable `.vsdx`
- PDF preview
- Pixel comparison report
- Difference visualization

ROI Reader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ImageJ/FIJI ROI file format is an intermediate solution for reading shape information. You can create ROIs via ImageJ's/FIJI's `ROI manager <https://imagej.nih.gov/ij/docs/guide/146-30.html#sub:ROI-Manager...>`_. By selecting/exporting multiple ROIs ImageJ/FIJI creates a ZIP archive which contains all selected ROIs as individual files.

    Note: The ROI reader plugin currently support the following ROI types: polygon, rect, oval, line, freeline and freehand.

Given a ROI file or ZIP file contianing multiple ROIs, you can simple drag-n-drop the file into Napari or open the file from within Napari via the "File/Open File(s)..." menu.


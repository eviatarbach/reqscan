reqscan
=======

Dependencies
------------
The following are the names of the Ubuntu repository packages:
- python (2.7 or similar)
- python-tk
- python-zbar
- python-imaging
- scanimage
- dmtx-utils (optional, for DataMatrix scanning)

Options
-------
- dpi: integer
  - DPI to scan at
- source: string
  - For ADF scanners with multiple sources (such as a front and back loader). Names vary by scanner, but can be found by running `scanimage`
    without arguments.
- cropbox: `None` or four space-delimited integers
  - Crop image to a box specified by two points (for example, `0 0 10 10` will crop from (0, 0) to (10, 10))
- datamatrix: `True` or `False`
  - Whether to check for DataMatrix codes or not
- symbologies: space-delimited list of barcode symbologies. Options are `ean13`, `ean8`, `upca`, `upce`, `isbn13`, `isbn10`, `i25`, `code39`,
  `code128`, and `qrcode`
  - Only these symbologies will be looked for.
- resize: float between 0 and 1
  - Scaling factor for saving images

Instructions
------------
The visual interface can be invoked with `python gui.py`, or the scripts invoked separately with `python scan.py` or `python process.py`.

reqscan
=======

**reqscan** is a Python program for digitizing records containing barcodes with automatic document feeder (ADF) scanners, using SANE and ZBar. It provides a low-cost alternative to commercial systems which can cost tens of thousands of dollars. It can be installed on GNU/Linux and Mac OS X.

You can read more about it in [this open access article](http://jpathinformatics.org/article.asp?issn=2153-3539;year=2015;volume=6;issue=1;spage=3;epage=3;aulast=Bach) in the *Journal of Pathology Informatics*.

Dependencies
------------
The following are the names of the Ubuntu repository packages:
- python (2.7 or similar)
- python-tk (optional, for graphical interface)
- python-zbar
- python-imaging
- scanimage
- dmtx-utils (optional, for DataMatrix scanning)

Reqscan can be installed on OS X as well. The SANE interface can be installed from http://www.ellert.se/twain-sane/, ImageMagick from MacPorts, and ZBar can be built from source.

Instructions
------------
The visual interface can be invoked with `python gui.py`, or the scripts invoked separately with `python scan.py` or `python process.py`.

`scan.py` scans all the pages in the ADF source and saves them in a temporary folder. `process.py` then processes the scanned files, saving them in a directory named after the current date, with the filenames consisting of the barcode data. Files with multiple barcodes are saved multiple times, abd those with no barcodes are saved as `fail_*.pdf`. Options for the scripts can be set in `options.txt`.

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
  - Scaling factor for saving images (applied to each dimension, not the area)

Questions
---------
You may send me questions about reqscan at eviatarbach[AT]gmail.com.

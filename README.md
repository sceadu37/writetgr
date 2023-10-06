# writetgr
Simple script for packing png/jpg files into TGR portrait files for Kohan: Ahriman's Gift

Requires PIL to be installed

run with:```python writetgr name_of_input_file```

If the input image matches the size of a small portrait (74 X 80) or a large portrait (230 X 230), the matching portrait frame will be applied automatically to the output.
If the input image does not match these dimensions, it will still be converted but no border will be added and an error will be printed

For documentation of the .tgr file format as well as a tgr unpacking tool, see https://github.com/tim-de/tgrlib


# writetgr
Simple script for packing png/jpg files into TGR portrait files for Kohan: Ahriman's Gift

Requires PIL to be installed

run with: ```python writetgr name_of_input_file size artist_name```


'size' can be either 'small' for unit portraits or 'large' for campaign portraits (equivalent to the BIG_ portraits). Artist name will be written to the file metadata, along with program version and a link to this repo.

The input image will be automatically cropped and rescaled to match the specified size. Currently, borders are appended to small portraits, so the processed image size is 66 X 72 to account for it. Large portraits have the borders written on top of the image, so they are left full size at 230 X 230.
This automatic processing will always grab the middle of the input image, so it may be advisable to pre-crop the input image to a square centered on the subject of the portrait.

For small portraits, the image pixels adjacent to the border are lightened slightly to create a bit of a "pop".

Borders are then applied to the processed image, and the resulting pixels are written to the TGR portrait format.

For documentation of the .tgr file format as well as a tgr unpacking tool, see https://github.com/tim-de/tgrlib. This is very useful for checking what the new portrait looks like without having to load it in-game.


# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 00:01:01 2023

@author: Elijah
"""
import color_func as cf
from PIL import Image
from pathlib import Path
import sys

def parseInputImage(im):
    imW, imH = im.size
    
    if imW == 74 and imH == 80:
        print(f"Image size {imW} by {imH} matches for Small Portrait")
    elif imW == 230 and imH == 230:
        print(f"Image size {imW} by {imH} matches for Large Portrait")
    else:
        print(f"Image size {imW} by {imH} does not match a Portrait size\nGenerated TGR may not load correctly")
    
    pb = []
    for y in range(0,imH):
        for x in range(0, imW):
            p = im.getpixel((x, y))
            r, g, b = cf.rgb888_to_rgb565(p[0], p[1], p[2])
            tgr_pixel = cf.rgb565_to_bytes(r, g, b)
            pb.append(tgr_pixel)
    return pb

def encodeLines(im,pb):
    imW, imH = im.size
    lines = []
    for y in range(0,imH):
        line_data = ""
        pixels_to_write = imW
        
        while pixels_to_write > 0:
            
            if pixels_to_write >= 31:
                
                line_data += "5F"
                for p in pb[:31]:
                    line_data += f"{p:0{4}X}"
                    pixels_to_write -= 1
                pb = pb[31:]
                
            else:
                run_header = (0x40 | pixels_to_write)
                line_data += f"{run_header:0{2}X}"
                for p in pb[:pixels_to_write]:
                    line_data += f"{p:0{4}X}"
                pb = pb[pixels_to_write:]
                pixels_to_write = 0
        
        num_pixels = f"{(0x8000 | imW):0{4}X}" if imW > 0b01111111 else f"{imW:0{2}X}"
        offset = f"{0:0{2}X}"
        line_length = ((len(offset) + len(num_pixels) + len(line_data)) >> 1) + 1
        line_length = f"{(0x8000 | (line_length+1)):0{4}X}" if line_length > 0b01111111 else f"{line_length:0{2}X}"
        line_data = line_length + offset + num_pixels + line_data
        lines.append(line_data)
    
    return lines

def encodeFRAMHeader(im, lines):
    imW, imH = im.size
    
    chunk_length = 0
    for line in lines:
        chunk_length += len(line)>>1
    header = "4652414D" + f"{chunk_length:0{8}X}"
    
    return header

def encodeFooter(artist):
    return ("Artist: " + artist).encode('utf-8')

def encodeHEDR(im):
    imW, imH = im.size
    chunk_type = "48454452"
    chunk_length = "00000000"
    version = "00000000"
    misc = "0100100100020000"
    #f"{((imW&0b1111)<<4)|(imW>>4):0{4}X}"
    size_x = f"{imW:0{4}X}"
    size_x = size_x[2:] + size_x[:2]
    size_y = f"{imH:0{4}X}"
    size_y = size_y[2:] + size_y[:2]
    #print(size_x,size_y)
    hotspot = "00000000"
    x_min = "0000"
    y_min = "0000"
    x_max = f"{imW-1:0{4}X}"
    x_max = x_max[2:] + x_max[:2]
    y_max = f"{imH-1:0{4}X}"
    y_max = y_max[2:] + y_max[:2]
    size_and_hotspot2 = size_x + size_y + hotspot
    null = "00000000"
    frame_size = x_min + y_min + x_max + y_max
    frame_offset = "00000000"
    padding = "0100000001000100"
    
    s1 = version + misc + size_x + size_y + hotspot + x_min + y_min + x_max + y_max + size_and_hotspot2 + null + frame_size
    
    chunk_length_int = len(s1 + frame_offset + padding)>>1
    chunk_length = f"{chunk_length_int:0{8}X}"
    
    frame_offset_int = (len(chunk_type + chunk_length)>>1) + chunk_length_int + 8 +12
    #print(frame_offset_int)
    frame_offset = f"{frame_offset_int:0{8}X}"
    frame_offset = frame_offset[6:] + frame_offset[4:6] + frame_offset[2:4] + frame_offset[:2]
    #print(frame_offset)
    
    return (chunk_type + chunk_length + s1 + frame_offset + padding)

def encodeForm(hedr,fram_header,lines):
    chunk_name = "464F524D"
    file_size = "00000000"
    file_type = "54474152"
    file_size_int = len(hedr + fram_header)
    for line in lines:
        file_size_int += len(line)
    file_size_int = file_size_int>>1
    file_size = f"{file_size_int:0{8}X}"
    return chunk_name + file_size + file_type

def writeTGR(im, form, hedr, fram_header, lines, outfile):
    print(f"Writing to {outfile}")
    imW, imH = im.size
    with open(outfile, "wb") as out_fh:
        out_fh.write(bytes.fromhex(form))
        out_fh.write(bytes.fromhex(hedr))
        out_fh.write(bytes.fromhex(fram_header))
        
        for i in range(0,imH):   # For every row...
            out_fh.write(bytes.fromhex(lines[i]))
    
    return
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Provide a file to convert to TGR")
        sys.exit()
    infile = sys.argv[1]
    image_name = Path(infile).stem
    outfile = image_name+'.tgr'

    im = Image.open(infile)
    
    pb = parseInputImage(im)

    lines = encodeLines(im, pb)

    fram_header = encodeFRAMHeader(im, lines)

    hedr = encodeHEDR(im)

    form = encodeForm(hedr, fram_header, lines)

    writeTGR(im, form, hedr, fram_header, lines, outfile)

    
    
        
    
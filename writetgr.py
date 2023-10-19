# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 00:01:01 2023

@author: Elijah
"""
import color_func as cf
from PIL import Image
from pathlib import Path
import sys

VERSION = '0.1.2'
DEBUG = True

def rescaleInputImage(im,out_size):
    inW, inH = im.size
    if out_size == "small":     # rescale to 66 X 72 (internal size of portrait frame)
        outW, outH = 66, 72        
    elif out_size == "large":   # rescale to 230 X 230 (full size of large frame)
        outW, outH = 230, 230
    else:
        print(f'{out_size} is not a valid size')
        sys.exit()
    
    if inH < (inW * outH / outW):   # if height less than width * inverse scaling factor
        crW = int(inH*outW/outH)    # set width equal to height, then scale to maintain AR
        crop = int((inW - crW) / 2)
        box = (crop ,0 ,inW - crop , inH)
        if DEBUG:
            print(f'Cropping width from {inW} to {crW} using bounding box {box}')
    else:
        crH = int(inW*outH/outW)
        crop = int((inH - crH) / 2)
        box = (0 ,crop ,inW, inH - crop)
        if DEBUG:
            print(f'Cropping height from {inH} to {crH} using bounding box {box}')
        
    cropped_im = im.crop(box)
    
    #cropped_im.save('crop.png')
       
    cropped_im.thumbnail((outW, outH))
    
    cropped_im.save('rescale.png')
    
    return cropped_im

def embossEdge(im):
    imW, imH = im.size
    for y in range(0,imH):
        for x in range(0, imW):
            if x in (0, imW-1) or y in (0, imH-1):
                r, g, b = im.getpixel((x, y))[:3]
                h, s, v = cf.rgb888_to_hsv(r, g, b)
                s = (s - 0.05 if s > 0.05 else 0)
                r, g, b = cf.hsv_to_rgb888(h, s, v)
                im.putpixel((x, y), (r, g, b))
    im.save('emboss.png')
    return im
    


def parseInputImage(im):
    imW, imH = im.size
    oW, oH = imW, imH
    
    if imW == 74 and imH == 80:
        print(f"Image size {imW} by {imH} matches for Small Portrait, border-overwrite")
        frame_size = "S"
        mode = "overwrite"
        frame = Image.open("small-portrait-frame.png")
    if imW == 66 and imH == 72:
        print(f"Image size {imW} by {imH} matches for Small Portrait, border-append")
        frame_size = "S"
        mode = "append"
        frame = Image.open("small-portrait-frame.png")
    elif imW == 230 and imH == 230:
        print(f"Image size {imW} by {imH} matches for Large Portrait, border-overwrite")
        frame_size = "L"
        mode = "overwrite"
        frame = Image.open("large-portrait-frame.png")
    else:
        print(f"Image size {imW} by {imH} does not match a Portrait size\nGenerated TGR may not load correctly")
        frame_size = None
        mode = None
    
    
    pb = []
    if frame_size == "S" and mode == "append":
        fW, fH = frame.size
        if fW > imW or fH > imH:
            oW, oH = fW, fH
            
        if DEBUG:
            print(f'Border template: {fW} X {fH}')
            
        x_offset = int((fW - imW) / 2)
        y_offset = int((fH - imH) / 2)
        
        for y in range(0,fH):
            for x in range(0, fW):
                fp = frame.getpixel((x,y))
                if not(fp[0:3] == (255, 255, 255)):     # if pixel isn't white
                    r, g, b = cf.rgb888_to_rgb565(fp[0], fp[1], fp[2])
                    
                elif (x - x_offset >= 0) and (y - y_offset >= 0):     # if in bounds of image
                    p = im.getpixel((x - x_offset, y - y_offset))
                    r, g, b = cf.rgb888_to_rgb565(p[0], p[1], p[2])
                else:
                    r, g, b = cf.rgb888_to_rgb565(255, 0, 0)      # red pixel to fill gaps
                    
                tgr_pixel = cf.rgb565_to_bytes(r, g, b)
                pb.append(tgr_pixel)
    
    else:
        if DEBUG:
            print('Normal overwrite mode')
        for y in range(0,imH):
            for x in range(0, imW):
                p = im.getpixel((x, y))
                if frame_size:  # If frame loaded, apply the non-white pixels to the input image
                    fp = frame.getpixel((x,y))
                    if not(fp[0] == 255 and fp[1] == 255 and  fp[2] == 255):
                        #print(fp)
                        r, g, b = cf.rgb888_to_rgb565(fp[0], fp[1], fp[2])
                    else:
                        r, g, b = cf.rgb888_to_rgb565(p[0], p[1], p[2])
                else:
                    r, g, b = cf.rgb888_to_rgb565(p[0], p[1], p[2])
                tgr_pixel = cf.rgb565_to_bytes(r, g, b)
                pb.append(tgr_pixel)
    return pb, (oW, oH)

def encodeLines(pb, size):
    imW, imH = size
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

def encodeFRAMHeader(lines, size):
    imW, imH = size
    
    chunk_length = 0
    for line in lines:
        chunk_length += len(line)>>1
    header = "4652414D" + f"{chunk_length:0{8}X}"
    
    return header

def encodeFooter(artist,version):
    return (f"Artist: {artist}. Created with writetgr version {version}. https://github.com/sceadu37/writetgr").encode('utf-8')

def encodeHEDR(size):
    imW, imH = size
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

def encodeForm(hedr,fram_header,lines,footer):
    chunk_name = "464F524D"
    file_size = "00000000"
    file_type = "54474152"
    file_size_int = len(hedr + fram_header)
    for line in lines:
        file_size_int += len(line)
    file_size_int = (file_size_int>>1) + len(footer)    # footer is already a bytearray, so no need to bitshift len
    file_size = f"{file_size_int:0{8}X}"
    return chunk_name + file_size + file_type

def writeTGR(size, form, hedr, fram_header, lines, footer, outfile):
    print(f"Writing to {outfile}")
    imW, imH = size
    with open(outfile, "wb") as out_fh:
        out_fh.write(bytes.fromhex(form))
        out_fh.write(bytes.fromhex(hedr))
        out_fh.write(bytes.fromhex(fram_header))
        
        for i in range(0,imH):   # For every row...
            out_fh.write(bytes.fromhex(lines[i]))
        
        out_fh.write(footer)    # Already bytes
    
    return
    
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('Usage: writetgr filename [size: small, large] artist')
        sys.exit()
    infile = sys.argv[1]
    
    out_size = sys.argv[2]
    if out_size not in ('small', 'large'):
        print(f'{out_size} is not a valid size.\nUse "small" for unit portraits and "large" for campaign portraits')
    
    artist = sys.argv[3]
        
    image_name = Path(infile).stem
    outfile = image_name+'.tgr'

    im = Image.open(infile)
    
    im = rescaleInputImage(im,out_size)
    
    if out_size == 'small':
        im = embossEdge(im)
    
    pb, size = parseInputImage(im)

    lines = encodeLines(pb, size)

    fram_header = encodeFRAMHeader(lines, size)

    hedr = encodeHEDR(size)
    
    footer = encodeFooter(artist, VERSION)

    form = encodeForm(hedr, fram_header, lines, footer)

    writeTGR(size, form, hedr, fram_header, lines, footer, outfile)

    
    
        
    
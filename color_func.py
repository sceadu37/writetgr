# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 19:32:24 2023

@author: Elijah
"""
import math
import sys


def rgb565_to_rgb888(r5,g6,b5):
    r8 = round(r5 / 31 * 255)
    g8 = round(g6 / 63 * 255)
    b8 = round(b5 / 31 * 255)
    return (r8,g8,b8)

def rgb888_to_rgb565(r8,g8,b8):
    r5 = round(r8 / 255 * 31)
    g6 = round(g8 / 255 * 63)
    b5 = round(b8 / 255 * 31)
    return (r5,g6,b5)

def rgb565_to_bytes(r5,g6,b5):
    assert r5 <= 31, "red channel must be <= 31"
    assert g6 <= 63, "green channel must be <= 63"
    assert b5 <= 31, "blue channel must be <= 31"
    return ((g6 & 0b111) << 13) | (b5 << 8) | (r5 << 3) | (g6 >> 3)
    #return hex((b5 << 11) | ((g6 & 0b111) << 8) | (r5 << 3) | (g6 >> 3))

def bytes_to_rgb565(p):
    r5 = ((p >> 3) & 0b11111)
    #print("r5:",bin(r5))
    gh = p & 0b111
    #print("gh: ",gh)
    gl = (p>>13) & 0b111
    #print("gl: ",gl)
    g6 = (gh << 3) | gl
    #print("g6:",bin(g6))
    b5 = ((p >> 8) & 0b11111)
    #print("b5: ",bin(b5))
    return (r5,g6,b5)

def rgb888_to_hsv(r8,g8,b8):
    r = r8 / 255
    g = g8 / 255
    b = b8 / 255
    
    mx = max(r,g,b)
    mn = min(r,g,b)
    
    h = mx
    s = mx
    v = mx
    
    d = mx - mn
    s = 0 if mx == 0 else d / mx
    
    if mx == mn:
        h = 0 #achromatic
    else:
        if mx == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif mx == g:
            h = (b - r) / d + 2
        elif mx == b:
            h = (r - g) / d + 4
        h /= 6
    
    return (h,s,v)

def hsv_to_rgb888(h,s,v):
    i = math.floor(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    
    if i % 6 == 0:
        r, g, b = v, t, p
    elif i % 6 == 1:
        r, g, b = q, v, p
    elif i % 6 == 2:
        r, g, b = p, v, t
    elif i % 6 == 3:
        r, g, b = p, q, v
    elif i % 6 == 4:
        r, g, b = t, p, v
    elif i % 6 == 5:
        r, g, b = v, p, q
    
    return (round(r * 255), round(g * 255), round(b * 255))


# Rotates hue [h] by [d] degrees
def rotate_hue(h,d):
    return ((h * 360 + d) % 360) / 360


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Provide an RGB565 pixel")
        sys.exit()
        
    pixel = int(sys.argv[1],16)
    print(pixel)
    angle = int(sys.argv[2],10)
    print(angle)
    
    r, g, b = bytes_to_rgb565(pixel)
    
    print("565in: ",r,g,b)
    
    r, g, b = rgb565_to_rgb888(r, g, b)
    
    print(r,g,b)
    
    h, s, v = rgb888_to_hsv(r, g, b)
    
    h = rotate_hue(h, angle)
    
    r, g, b = hsv_to_rgb888(h, s, v)
    
    print (r, g, b)
    
    r, g, b = rgb888_to_rgb565(r, g, b)
    
    print("565out: ",r,g,b)
    
    new_pixel = rgb565_to_bytes(r, g, b)
    
    print(new_pixel)







# =============================================================================
# pixel = 0x936a
# red = ((pixel >> 3) & 0b11111)
# 
# green = (((pixel & 0b111) << 3) | ((pixel >> 8) & 0b111))
# 
# blue = (pixel >> 11)
# 
# v = (red/31 + green/63 +blue/31)/3
# 
# a = 1.6 #coefficient for blue
# 
# x = (3*v - (a*blue/31))/(red/31 + green/63)
# 
# #x = (3*v - (a*blue/31) - green/63)/(red/31)
# 
# red_s = round(red * x)
# 
# green_s = round(green * x)
# #green_s = round(green)
# 
# blue_s = round(blue * a)
# if blue_s > 31:
#     blue_s = 31
# 
# v_s = (red_s/31 + green_s/63 +blue_s/31)/3
# 
# new_pixel = hex((blue_s << 11) | ((green_s & 0b111) << 8) | (red_s << 3) | (green_s >> 3))
# 
# print("red:{0} green:{1} blue:{2}".format(red,green,blue))
# print("RGB888: {0} {1} {2}".format(round(red/31*255),round(green/63*255),round(blue/31*255)))
# print("recaling--------\nred:{0} green:{1} blue:{2}".format(red_s,green_s,blue_s))
# print("new pixel: {}".format(new_pixel))
# =============================================================================
        
    
    
    
    



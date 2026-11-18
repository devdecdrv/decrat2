import struct, os

def make_ico(path):
    # 16x16 single-color ICO — gear grey (RGB 128,128,128)
    w, h = 16, 16
    # BMP header for ICO (no file header, just DIB)
    planes, bpp = 1, 32
    row_size = w * 4
    pixel_data = bytes([80, 80, 80, 255] * w * h)  # BGRA grey
    and_mask = bytes([0x00] * (((w + 31) // 32) * 4 * h))
    dib_size = 40
    dib = struct.pack('<IiiHHIIiiII',
        dib_size, w, h * 2, planes, bpp, 0,
        len(pixel_data) + len(and_mask), 0, 0, 0, 0)
    image_data = dib + pixel_data + and_mask

    # ICO file: header + 1 directory entry + image
    ico_header = struct.pack('<HHH', 0, 1, 1)
    dir_entry  = struct.pack('<BBBBHHII',
        w, h, 0, 0, planes, bpp,
        len(image_data), 6 + 16)  # offset = header(6) + entry(16)
    with open(path, 'wb') as f:
        f.write(ico_header + dir_entry + image_data)
    print(f"ICO written: {path}")

make_ico("service.ico")

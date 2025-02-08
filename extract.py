import struct
from PIL import Image
import os
import sys

def iflip(n):
    """ Flip the byte order for 4-byte integers (big-endian to little-endian) """
    return flip(n, 4)

def sflip(n):
    """ Flip the byte order for 2-byte shorts (big-endian to little-endian) """
    return flip(n, 2)

def flip(n, b):
    """ Flip the byte order """
    a = 0
    for _ in range(b):
        a = (a << 8) | (n & 0xFF)
        n >>= 8
    return a

def extract_frames(file, output_dir):
    """ Extract frames from the given file """
    # In the orginal source, this value was 26. However, 3 is sufficient to get all the frames
    # for both .fsh and .mvy files. Values of 5 or above won't work for .mvy files.
    feature_count = 3

    with open(file, 'rb') as raf:
        # Read the name of the file (8 bytes starting at offset 0x0A)
        raf.seek(0x0A)
        name = ''.join([chr(raf.read(1)[0]) for _ in range(8)]).strip('\x00').lower()
        print(f"Extracting {name} from {file}")

        # Read the features (26 features starting at offset 0x8B)
        raf.seek(0x8B)
        features = [iflip(struct.unpack('>I', raf.read(4))[0]) for _ in range(feature_count)]

        # Extract sprites for each feature
        for j, feature in enumerate(features):
            if feature == 0:
                continue  # Skip if feature is 0
            print(f"\nDumping {j} from {feature}")
            extract_sprites(raf, name, j, feature, output_dir)

def extract_sprites(raf, name, j, feature, output_dir):
    """ Extract sprites from the given feature """
    n = 0
    while feature != 0:
        raf.seek(feature)
        fd = [iflip(struct.unpack('>I', raf.read(4))[0]) for _ in range(5)]
        raf.read(6)  # skip 6 bytes
        w = sflip(struct.unpack('>H', raf.read(2))[0])
        h = sflip(struct.unpack('>H', raf.read(2))[0])

        print(f"#{n} - Frame: {w}x{h}")
        if (w == 0 or h == 0):
            print("Zero sized frame, aborting...")
            return

        sprite = decode_frame(w, h, raf)
        save_sprite(sprite, f"{name}-{j}-{n}.png", output_dir)
        
        feature = fd[3]  # Move to the next feature
        n += 1

def decode_frame(w, h, raf):
    """ Decodes and returns a PIL image representing a frame """
    sprite = Image.new('P', (w, h))
    #palette_flat = [value for color in palette for value in (color >> 16, (color >> 8) & 0xFF, color & 0xFF)]
    #print(palette_flat)
    sprite.putpalette(palette)

    lbuf = [0] * w
    nh = 1

    while nh < h:
        len_segment = sflip(struct.unpack('>H', raf.read(2))[0])
        pos = sflip(struct.unpack('>H', raf.read(2))[0])

        if pos < 0x8000:
            # New line if pos is less than 0x8000
            nh += 1
            for x in range(w):
                sprite.putpixel((x, nh - 1), lbuf[x])
            lbuf = [0] * w
        else:
            # Adjust pos if it is greater than or equal to 0x8000
            pos = 0x10000 - pos

        for i in range(len_segment):
            lbuf[pos] = raf.read(1)[0]
            pos += 1

    return sprite

def save_sprite(sprite, filename, output_dir):
    """ Saves the sprite as an image """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    sprite.save(os.path.join(output_dir, filename))
    print(f"Saved {filename}")

palette = [
  0,   0,   0,   124, 128, 144,    48,  56,  76,   168, 164, 172,
  0,   0,   0,   252,  84,  84,   232, 252,  96,   168,   0,   0,
 88, 112, 136,   240, 240, 240,   112, 112, 128,   120, 152, 160,
 96,  96,  96,     0,   0,   0,   208,   0,   0,   252, 252, 252,
  0,   0,   0,    40,  40,  40,    80,  80,  80,   124, 124, 124,
164, 164, 164,   208, 208, 208,   248, 248, 248,    40,   0,   0,
 40,  40,   0,     0,  40,   0,     0,  40,  40,     0,   0,  40,
 40,   0,  40,    80,  40,  40,    80,  80,  40,    40,  80,  40,
 40,  80,  80,    40,  40,  80,    80,  40,  80,   124,  80,  80,
124, 124,  80,    80, 124,  80,    80, 124, 124,    80,  80, 124,
124,  80, 124,   164, 124, 124,   164, 164, 124,   124, 164, 124,
124, 164, 164,   124, 124, 164,   164, 124, 164,   208, 164, 164,
208, 208, 164,   164, 208, 164,   164, 208, 208,   164, 164, 208,
208, 164, 208,   248, 208, 208,   248, 248, 208,   208, 248, 208,
208, 248, 248,   208, 208, 248,   248, 208, 248,    80,   0,   0,
 80,  40,   0,    80,  80,   0,    40,  80,   0,     0,  80,   0,
  0,  80,  40,     0,  80,  80,     0,  40,  80,     0,   0,  80,
 40,   0,  80,    80,   0,  80,    80,   0,  40,   124,  40,  40,
124,  80,  40,   124, 124,  40,    80, 124,  40,    40, 124,  40,
 40, 124,  80,    40, 124, 124,    40,  80, 124,    40,  40, 124,
 80,  40, 124,   124,  40, 124,   124,  40,  80,   164,  80,  80,
164, 124,  80,   164, 164,  80,   124, 164,  80,    80, 164,  80,
 80, 164, 124,    80, 164, 164,    80, 124, 164,    80,  80, 164,
124,  80, 164,   164,  80, 164,   164,  80, 124,   208, 124, 124,
208, 164, 124,   208, 208, 124,   164, 208, 124,   124, 208, 124,
124, 208, 164,   124, 208, 208,   124, 164, 208,   124, 124, 208,
164, 124, 208,   208, 124, 208,   208, 124, 164,   248, 164, 164,
248, 208, 164,   248, 248, 164,   208, 248, 164,   164, 248, 164,
164, 248, 208,   164, 248, 248,   164, 208, 248,   164, 164, 248,
208, 164, 248,   248, 164, 248,   248, 164, 208,   124,   0,   0,
124,  48,   0,   124, 100,   0,   100, 124,   0,    48, 124,   0,
  0, 124,   0,     0, 124,  48,     0, 124, 100,     0, 100, 124,
  0,  48, 124,     0,   0, 124,    48,   0, 124,   100,   0, 124,
124,   0, 100,   124,   0,  48,   164,  40,  40,   164,  92,  40,
164, 140,  40,   140, 164,  40,    92, 164,  40,    40, 164,  40,
 40, 164,  92,    40, 164, 140,    40, 140, 164,    40,  92, 164,
 40,  40, 164,    92,  40, 164,   140,  40, 164,   164,  40, 140,
164,  40,  92,   208,  84,  84,   208, 132,  84,   208, 184,  84,
184, 208,  84,   132, 208,  84,    84, 208,  84,    84, 208, 132,
 84, 208, 184,    84, 184, 208,    84, 132, 208,    84,  84, 208,
132,  84, 208,   184,  84, 208,   208,  84, 184,   208,  84, 132,
248, 124, 124,   248, 176, 124,   248, 224, 124,   224, 248, 124,
176, 248, 124,   124, 248, 124,   124, 248, 176,   124, 248, 224,
124, 224, 248,   124, 176, 248,   124, 124, 248,   176, 124, 248,
224, 124, 248,   248, 124, 224,   248, 124, 176,   164,   0,   0,
164,  64,   0,   164, 132,   0,   132, 164,   0,    64, 164,   0,
  0, 164,   0,     0, 164,  64,     0, 164, 132,     0, 132, 164,
  0,  64, 164,     0,   0, 164,    64,   0, 164,   132,   0, 164,
164,   0, 132,   164,   0,  64,   208,  40,  40,   208, 108,  40,
208, 176,  40,   176, 208,  40,   108, 208,  40,    40, 208,  40,
 40, 208, 108,    40, 208, 176,    40, 176, 208,    40, 108, 208,
 40,  40, 208,   108,  40, 208,   176,  40, 208,   208,  40, 176,
208,  40, 108,   248,  84,  84,   248, 148,  84,   248, 216,  84,
216, 248,  84,   148, 248,  84,    84, 248,  84,    84, 248, 148,
 84, 248, 216,    84, 216, 248,    84, 148, 248,    84,  84, 248,
148,  84, 248,   216,  84, 248,   248,  84, 216,   248,  84, 148,
208,   0,   0,   208,  76,   0,   208, 156,   0,   180, 208,   0,
104, 208,   0,    24, 208,   0,     0, 208,  52,     0, 208, 128,
  0, 208, 208,     0, 128, 208,     0,  52, 208,    24,   0, 208,
104,   0, 208,   180,   0, 208,   208,   0, 156,   208,   0,  76,
248,  40,  40,   248, 120,  40,   248, 196,  40,   224, 248,  40,
144, 248,  40,    68, 248,  40,    40, 248,  92,    40, 248, 172,
 40, 248, 248,    40, 172, 248,    40,  92, 248,    68,  40, 248,
144,  40, 248,   224,  40, 248,   248,  40, 196,   248,  40, 120
]

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract.py <input_file> <output_dir>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    extract_frames(input_file, output_dir)

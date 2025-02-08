# El-Fish Extractor

Elfish Extractor is a tool for extracting frames from `.fsh`, `.mvy`, `.aqu` and `.isb` files used by the 1994 El-Fish software. It reads the input file, extracts the frames, and saves them as images in the specified output directory.

This is based on the work of Vidar Holen: https://www.vidarholen.net/contents/elfish/

I ported the java tool to python in the hopes that after doing so, I'd understand enough of the file format to write something that can pack the frames back in to the file. This would be the holy grail for El-Fish: the ability to create new animated objects. The first new feature for El-Fish in over 30 years! However, I wasn't able to crack it. This repo is provided in the hope that somebody else can solve this.

For properity, I included Vidar's information on the file-format at the bottom of this file.

## Requirements

- Python 3.x
- Pillow library

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/elfish-extractor.git
    ```
2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To use the Elfish Extractor, run the following command:

```sh
python extract.py <input_file> <output_dir>
```

- `<input_file>`: Path to the `.fsh`, `.mvy`, `.aqu` or `.isb` file.
- `<output_dir>`: Directory where the extracted frames will be saved.

### Example

```sh
python extract.py example.fsh output/
```

This command will extract frames from `example.fsh` and save them in the `output/` directory.

## File Format information

Each file is encoded in streams, each stream has a number of frames. All integers are little-endian.

```
8 bytes   Unknown (magic?)
2 bytes   Unknown (zero)

--(offset now 0A)--
8 bytes   Fish name, zero-padded at end.
4 bytes   Unknown (zero)
2 bytes   Unknown (rendering progress?)
2 bytes   Unknown (rendering total?)
2 bytes   Unknown (Total number of animation frames + 7 ?)
4 bytes   Unknown

--(offset now 20)--
4 bytes   Total file length
103 bytes Unknown

--(offset now 8B)--
4 bytes   Stream offset - Detailed frame
4 bytes   Stream offset - Icon frame
4 bytes   Stream offset - Animation frames

Each stream is a linked list of frames. Each frame has a 30 byte header:

4 bytes   Frame length (from start of header)
4 bytes   Frame number
4 bytes   Previous entry (absolute seek), or 0 if first frame in the series
4 bytes   Next entry (absolute seek), or 0 if last frame in the series
4 bytes   Unknown (same as frame length)
2 bytes   Unknown (movement increment?)
2 bytes   X offset (?)
2 bytes   Y offset (?)
2 bytes   Frame width
2 bytes   Frame height

Then follows frame data. Each frame is encoded in lines, each line is built up from plot sections. Each plot section has a length, position, and pixels:

      2 bytes      2 bytes     'Length' bytes
  [ Data length  | Position  |  Pixel data (1 byte per) ]
```

If the position is positive (two's complement), this is the start of a line. If it's negative, take its absolute value and plot on the current line (the first line only have negative sections). Simply put the pixel data in the line buffer linearly at the specified position. Any part of a line that is not explicitly colored is transparent. Each pixel is encoded in a fixed palette, which can be found in extract.py

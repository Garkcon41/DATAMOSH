# DATAMOSH – Glitch aesthetics playground

This repository contains a small collection of glitch-inspired image utilities
implemented without third-party dependencies. All operations work on binary
PPM (P6) images to keep the code lightweight – you can convert to and from PPM
with tools such as ImageMagick (`convert input.png output.ppm`).

It is designed to emulate the look of broken video compression: keyframes stop
refreshing, motion smears and melts between frames, subjects drag into colorful
streaks, and abrupt jumps create ghosting silhouettes with unstable timing.
The result feels like a damaged early-era MP4 upload.

## Features

* **JPEG/DCT blockiness** – quantises luminance in 8×8 blocks while smearing
  chrominance, mimicking heavy JPEG compression.
* **Row/column slicing and shifting** – randomly offsets scan-lines and
  vertical slices with wrap-around to create tearing artefacts.
* **Pixel sorting** – reorders pixels in bright or colourful segments to create
  shimmering streaks.
* **Temporal datamosh smear** – when given a sequence of frames the tool keeps
  motion data alive to bleed one frame into the next.

## How do I open it?

Short answer: this project is a **command-line tool**, not a desktop app with a window.
You "open" it by opening a terminal in the project folder and running commands.

### 1) Open a terminal in the DATAMOSH folder

- **Windows**: open File Explorer, go to the `DATAMOSH` folder, click the path bar,
  type `cmd` and press Enter.
- **macOS**: open Terminal, then run:
  ```bash
  cd /path/to/DATAMOSH
  ```
- **Linux**: open Terminal, then run:
  ```bash
  cd /path/to/DATAMOSH
  ```

### 2) Verify it starts

Run:
```bash
python -m glitcher.cli --help
```

If you see a list of commands (`jpeg`, `slice`, `sort`, `smear`), it is opened correctly.

### 3) Run one effect

```bash
python -m glitcher.cli jpeg input.ppm output.ppm
```

If your input is PNG/JPG, convert first:
```bash
convert input.png input.ppm
```

## Beginner quickstart (first run)

If you're new to app making, follow this exact path:

1. **Install Python 3.10+** and confirm it works:
   ```bash
   python --version
   ```
2. **Open a terminal in this project folder** (`DATAMOSH`).
3. **Check the CLI loads**:
   ```bash
   python -m glitcher.cli --help
   ```
4. **Prepare one image** (PNG/JPG is okay) and convert it to PPM:
   ```bash
   convert my_photo.png input.ppm
   ```
   If `convert` is missing, install ImageMagick first.
5. **Apply one effect** (example: JPEG glitch):
   ```bash
   python -m glitcher.cli jpeg input.ppm output.ppm
   ```
6. **Convert back to PNG** so you can view/share it easily:
   ```bash
   convert output.ppm output.png
   ```

You can now repeat step 5 using other effects (`slice`, `sort`, `smear`).

## Quick command examples

All effects are available through a command line interface:

```text
python -m glitcher.cli <effect> [...options]
```

Each command reads and writes PPM images:

* `python -m glitcher.cli jpeg input.ppm output.ppm` – apply JPEG style
  blockiness. Optional flags control the block size, luminance quantisation
  strength, and chroma bleed.
* `python -m glitcher.cli slice input.ppm output.ppm --seed 1234` – perform
  row/column slicing. You can tweak the maximum offset and the probability for
  rows/columns to be affected.
* `python -m glitcher.cli sort input.ppm output.ppm --mode hue` – perform pixel
  sorting. Segments of pixels whose metric (brightness or hue) exceeds the
  threshold are sorted.
* `python -m glitcher.cli smear frames_in frames_out --seed 42` – process a
  directory containing input frames (e.g. `frame0000.ppm`). The processed
  frames are saved to the output directory. Adjust block size, smear strength,
  and the probability that motion is preserved between frames.

## Make a datamosh-style video (simple workflow)

1. Extract frames from a video:
   ```bash
   ffmpeg -i input.mp4 frames/frame%04d.png
   ```
2. Convert frames to PPM:
   ```bash
   mkdir -p frames_ppm
   for f in frames/*.png; do
     b=$(basename "$f" .png)
     convert "$f" "frames_ppm/${b}.ppm"
   done
   ```
3. Apply temporal smear:
   ```bash
   python -m glitcher.cli smear frames_ppm glitched_ppm --seed 42
   ```
4. Convert glitched frames back to PNG:
   ```bash
   mkdir -p glitched_png
   for f in glitched_ppm/*.ppm; do
     b=$(basename "$f" .ppm)
     convert "$f" "glitched_png/${b}.png"
   done
   ```
5. Rebuild MP4:
   ```bash
   ffmpeg -framerate 30 -i glitched_png/frame%04d.png -pix_fmt yuv420p output.mp4
   ```

## Python usage

All effects are also available as Python functions in `glitcher.effects`. The
module works with the simple `glitcher.image.Image` container which stores
pixels as nested Python lists. This makes it straightforward to script or
experiment with the effects without installing additional libraries.

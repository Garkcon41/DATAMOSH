+# DATAMOSH – Glitch aesthetics playground
+
+This repository contains a small collection of glitch-inspired image utilities
+implemented without third-party dependencies.  All operations work on binary
+PPM (P6) images to keep the code lightweight – you can convert to and from PPM
+with tools such as ImageMagick (`convert input.png output.ppm`).
+
+## Features
+
+* **JPEG/DCT blockiness** – quantises luminance in 8×8 blocks while smearing
+  chrominance, mimicking heavy JPEG compression.
+* **Row/column slicing and shifting** – randomly offsets scan-lines and
+  vertical slices with wrap-around to create tearing artefacts.
+* **Pixel sorting** – reorders pixels in bright or colourful segments to create
+  shimmering streaks.
+* **Temporal datamosh smear** – when given a sequence of frames the tool keeps
+  motion data alive to bleed one frame into the next.
+
+All effects are available through a command line interface:
+
+```text
+python -m glitcher.cli <effect> [...options]
+```
+
+Each command reads and writes PPM images:
+
+* `python -m glitcher.cli jpeg input.ppm output.ppm` – apply JPEG style
+  blockiness.  Optional flags control the block size, luminance quantisation
+  strength, and chroma bleed.
+* `python -m glitcher.cli slice input.ppm output.ppm --seed 1234` – perform
+  row/column slicing.  You can tweak the maximum offset and the probability for
+  rows/columns to be affected.
+* `python -m glitcher.cli sort input.ppm output.ppm --mode hue` – perform pixel
+  sorting.  Segments of pixels whose metric (brightness or hue) exceeds the
+  threshold are sorted.
+* `python -m glitcher.cli smear frames_in frames_out --seed 42` – process a
+  directory containing input frames (e.g. `frame0000.ppm`).  The processed
+  frames are saved to the output directory.  Adjust block size, smear strength
+  and the probability that motion is preserved between frames.
+
+## Python usage
+
+All effects are also available as Python functions in `glitcher.effects`.  The
+module works with the simple `glitcher.image.Image` container which stores
+pixels as nested Python lists.  This makes it straightforward to script or
+experiment with the effects without installing additional libraries.
 
EOF
)

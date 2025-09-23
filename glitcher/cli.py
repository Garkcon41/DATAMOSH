 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/glitcher/cli.py
index 0000000000000000000000000000000000000000..c841644a611d1c29b9a4ef90b4a09be133a3ebd3 100644
--- a//dev/null
+++ b/glitcher/cli.py
@@ -0,0 +1,124 @@
+"""Simple command line interface for the glitch effects."""
+from __future__ import annotations
+
+import argparse
+from pathlib import Path
+from typing import List, Sequence
+
+from . import effects
+from .image import Image, read_ppm, write_ppm
+
+
+def main(argv: Sequence[str] | None = None) -> int:
+    parser = argparse.ArgumentParser(description="Apply glitch aesthetics to PPM images.")
+    subparsers = parser.add_subparsers(dest="command", required=True)
+
+    jpeg_parser = subparsers.add_parser("jpeg", help="JPEG/DCT inspired block artifacts")
+    jpeg_parser.add_argument("input", help="Input PPM image")
+    jpeg_parser.add_argument("output", help="Output PPM image")
+    jpeg_parser.add_argument("--block-size", type=int, default=8)
+    jpeg_parser.add_argument("--luma-quant", type=int, default=24)
+    jpeg_parser.add_argument("--chroma-bleed", type=float, default=0.6)
+
+    slice_parser = subparsers.add_parser("slice", help="Row/column slicing and shifting")
+    slice_parser.add_argument("input")
+    slice_parser.add_argument("output")
+    slice_parser.add_argument("--max-offset", type=int, default=16)
+    slice_parser.add_argument("--row-probability", type=float, default=0.6)
+    slice_parser.add_argument("--column-probability", type=float, default=0.35)
+    slice_parser.add_argument("--seed", type=int, default=None)
+
+    sort_parser = subparsers.add_parser("sort", help="Pixel sorting based on brightness or hue")
+    sort_parser.add_argument("input")
+    sort_parser.add_argument("output")
+    sort_parser.add_argument("--threshold", type=float, default=180.0)
+    sort_parser.add_argument("--segment-length", type=int, default=12)
+    sort_parser.add_argument("--mode", choices=["brightness", "hue"], default="brightness")
+
+    smear_parser = subparsers.add_parser("smear", help="Temporal datamosh-style smearing")
+    smear_parser.add_argument("input_dir", help="Directory containing ordered PPM frames")
+    smear_parser.add_argument("output_dir", help="Directory to store processed frames")
+    smear_parser.add_argument("--pattern", default="*.ppm", help="Glob pattern for frames")
+    smear_parser.add_argument("--hold-probability", type=float, default=0.65)
+    smear_parser.add_argument("--smear-strength", type=float, default=0.7)
+    smear_parser.add_argument("--block-size", type=int, default=16)
+    smear_parser.add_argument("--seed", type=int, default=None)
+
+    args = parser.parse_args(argv)
+
+    if args.command == "jpeg":
+        image = read_ppm(args.input)
+        glitched = effects.apply_jpeg_glitch(
+            image,
+            block_size=args.block_size,
+            luma_quant=args.luma_quant,
+            chroma_bleed=args.chroma_bleed,
+        )
+        write_ppm(glitched, args.output)
+        return 0
+
+    if args.command == "slice":
+        image = read_ppm(args.input)
+        rng = None if args.seed is None else random_random(args.seed)
+        glitched = effects.apply_slice_shift(
+            image,
+            max_offset=args.max_offset,
+            row_probability=args.row_probability,
+            column_probability=args.column_probability,
+            rng=rng,
+        )
+        write_ppm(glitched, args.output)
+        return 0
+
+    if args.command == "sort":
+        image = read_ppm(args.input)
+        glitched = effects.apply_pixel_sort(
+            image,
+            threshold=args.threshold,
+            segment_length=args.segment_length,
+            mode=args.mode,
+        )
+        write_ppm(glitched, args.output)
+        return 0
+
+    if args.command == "smear":
+        rng = None if args.seed is None else random_random(args.seed)
+        frames = _load_frames(args.input_dir, pattern=args.pattern)
+        if not frames:
+            raise SystemExit("No frames matched the given pattern")
+        processed = effects.apply_temporal_smear(
+            frames,
+            hold_probability=args.hold_probability,
+            smear_strength=args.smear_strength,
+            block_size=args.block_size,
+            rng=rng,
+        )
+        _write_frames(args.output_dir, processed)
+        return 0
+
+    parser.error("Unknown command")
+    return 2
+
+
+def random_random(seed: int):
+    import random
+
+    rng = random.Random(seed)
+    return rng
+
+
+def _load_frames(directory: str, *, pattern: str) -> List[Image]:
+    paths = sorted(Path(directory).glob(pattern))
+    return [read_ppm(str(path)) for path in paths]
+
+
+def _write_frames(directory: str, frames: Sequence[Image]) -> None:
+    path = Path(directory)
+    path.mkdir(parents=True, exist_ok=True)
+    for idx, frame in enumerate(frames):
+        out_path = path / f"frame{idx:04d}.ppm"
+        write_ppm(frame, str(out_path))
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
 
EOF
)

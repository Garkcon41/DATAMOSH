"""Glitch effects implemented without external dependencies."""
from __future__ import annotations

import random
from typing import List, Sequence

from .image import Image, RGBTuple, blend_pixels


def apply_jpeg_glitch(
    image: Image,
    *,
    block_size: int = 8,
    luma_quant: int = 24,
    chroma_bleed: float = 0.6,
) -> Image:
    """Approximate JPEG style block artifacts and chroma bleeding."""
    if block_size <= 0:
        raise ValueError("block_size must be > 0")
    if luma_quant <= 0:
        raise ValueError("luma_quant must be > 0")
    if not 0 <= chroma_bleed <= 1:
        raise ValueError("chroma_bleed must be between 0 and 1")

    out = image.clone()
    height = image.height
    width = image.width

    for by in range(0, height, block_size):
        for bx in range(0, width, block_size):
            block_coords = []
            chroma_cb: List[float] = []
            chroma_cr: List[float] = []
            luma_values: List[float] = []
            for y in range(by, min(by + block_size, height)):
                for x in range(bx, min(bx + block_size, width)):
                    r, g, b = image.pixels[y][x]
                    yv, cb, cr = _rgb_to_ycbcr(r, g, b)
                    block_coords.append((x, y))
                    chroma_cb.append(cb)
                    chroma_cr.append(cr)
                    luma_values.append(yv)

            if not block_coords:
                continue

            avg_cb = sum(chroma_cb) / len(chroma_cb)
            avg_cr = sum(chroma_cr) / len(chroma_cr)

            for (x, y), yv, cb, cr in zip(block_coords, luma_values, chroma_cb, chroma_cr):
                quant_y = round(yv / luma_quant) * luma_quant
                quant_y = max(0, min(255, quant_y))
                cb_mix = cb * (1 - chroma_bleed) + avg_cb * chroma_bleed
                cr_mix = cr * (1 - chroma_bleed) + avg_cr * chroma_bleed
                out.pixels[y][x] = _ycbcr_to_rgb(quant_y, cb_mix, cr_mix)

    return out


def apply_slice_shift(
    image: Image,
    *,
    max_offset: int = 16,
    row_probability: float = 0.6,
    column_probability: float = 0.35,
    rng: random.Random | None = None,
) -> Image:
    """Slice and shift random rows/columns with wrap-around."""
    if max_offset < 0:
        raise ValueError("max_offset must be >= 0")
    if not 0 <= row_probability <= 1:
        raise ValueError("row_probability must be in [0, 1]")
    if not 0 <= column_probability <= 1:
        raise ValueError("column_probability must be in [0, 1]")

    rng = rng or random.Random()
    out = image.clone()

    if max_offset == 0:
        return out

    for y, row in enumerate(image.pixels):
        if rng.random() <= row_probability:
            offset = rng.randint(-max_offset, max_offset)
            if offset:
                shift = offset % len(row)
                out.pixels[y] = row[shift:] + row[:shift]

    width = image.width
    height = image.height
    for x in range(width):
        if rng.random() <= column_probability:
            offset = rng.randint(-max_offset, max_offset)
            if offset:
                column = [out.pixels[y][x] for y in range(height)]
                shift = offset % height
                shifted = column[shift:] + column[:shift]
                for y in range(height):
                    out.pixels[y][x] = shifted[y]

    return out


def apply_pixel_sort(
    image: Image,
    *,
    threshold: float = 180.0,
    segment_length: int = 12,
    mode: str = "brightness",
) -> Image:
    """Sort pixels in runs where the metric passes ``threshold``."""
    if segment_length <= 0:
        raise ValueError("segment_length must be > 0")

    out = image.clone()

    for y, row in enumerate(image.pixels):
        x = 0
        while x < image.width:
            if _pixel_metric(row[x], mode) >= threshold:
                end = min(image.width, x + segment_length)
                while end < image.width and _pixel_metric(row[end], mode) >= threshold:
                    end += 1
                out.pixels[y][x:end] = sorted(row[x:end], key=lambda p: _pixel_metric(p, mode))
                x = end
            else:
                x += 1

    return out


def apply_temporal_smear(
    frames: Sequence[Image],
    *,
    hold_probability: float = 0.65,
    smear_strength: float = 0.7,
    block_size: int = 16,
    rng: random.Random | None = None,
) -> List[Image]:
    """Apply a datamosh-like smear across a sequence of frames."""
    if not frames:
        return []
    if block_size <= 0:
        raise ValueError("block_size must be > 0")
    if not 0 <= hold_probability <= 1:
        raise ValueError("hold_probability must be in [0, 1]")
    if not 0 <= smear_strength <= 1:
        raise ValueError("smear_strength must be in [0, 1]")

    rng = rng or random.Random()
    buffer = frames[0].clone()
    result = [frames[0].clone()]

    for frame in frames[1:]:
        working = frame.clone()
        for by in range(0, frame.height, block_size):
            for bx in range(0, frame.width, block_size):
                if rng.random() <= hold_probability:
                    for y in range(by, min(by + block_size, frame.height)):
                        for x in range(bx, min(bx + block_size, frame.width)):
                            working.pixels[y][x] = blend_pixels(
                                working.pixels[y][x], buffer.pixels[y][x], smear_strength
                            )
                else:
                    for y in range(by, min(by + block_size, frame.height)):
                        for x in range(bx, min(bx + block_size, frame.width)):
                            buffer.pixels[y][x] = frame.pixels[y][x]
        result.append(working)

    return result


def _rgb_to_ycbcr(r: int, g: int, b: int) -> tuple[float, float, float]:
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = -0.168736 * r - 0.331264 * g + 0.5 * b + 128
    cr = 0.5 * r - 0.418688 * g - 0.081312 * b + 128
    return y, cb, cr


def _ycbcr_to_rgb(y: float, cb: float, cr: float) -> RGBTuple:
    r = y + 1.402 * (cr - 128)
    g = y - 0.344136 * (cb - 128) - 0.714136 * (cr - 128)
    b = y + 1.772 * (cb - 128)
    return (
        max(0, min(255, int(round(r)))),
        max(0, min(255, int(round(g)))),
        max(0, min(255, int(round(b)))),
    )


def _pixel_metric(pixel: RGBTuple, mode: str) -> float:
    r, g, b = pixel
    if mode == "brightness":
        return 0.299 * r + 0.587 * g + 0.114 * b
    if mode == "hue":
        return _rgb_to_hue(pixel)
    raise ValueError(f"Unsupported mode: {mode}")


def _rgb_to_hue(pixel: RGBTuple) -> float:
    r, g, b = (channel / 255.0 for channel in pixel)
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    delta = max_c - min_c
    if delta == 0:
        return 0.0
    if max_c == r:
        hue = ((g - b) / delta) % 6
    elif max_c == g:
        hue = (b - r) / delta + 2
    else:
        hue = (r - g) / delta + 4
    return hue * 60

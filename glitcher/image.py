"""Minimal image container and binary PPM I/O helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

RGBTuple = Tuple[int, int, int]


@dataclass
class Image:
    width: int
    height: int
    pixels: List[List[RGBTuple]]

    def clone(self) -> "Image":
        return Image(
            width=self.width,
            height=self.height,
            pixels=[[tuple(pixel) for pixel in row] for row in self.pixels],
        )


def blend_pixels(base: RGBTuple, overlay: RGBTuple, strength: float) -> RGBTuple:
    strength = max(0.0, min(1.0, strength))
    return (
        _mix_channel(base[0], overlay[0], strength),
        _mix_channel(base[1], overlay[1], strength),
        _mix_channel(base[2], overlay[2], strength),
    )


def _mix_channel(a: int, b: int, strength: float) -> int:
    return int(round(a * (1.0 - strength) + b * strength))


def read_ppm(path: str) -> Image:
    with open(path, "rb") as f:
        magic = f.readline().strip()
        if magic != b"P6":
            raise ValueError("Only binary PPM (P6) is supported")

        tokens: List[bytes] = []
        while len(tokens) < 3:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if not line or line.startswith(b"#"):
                continue
            tokens.extend(line.split())

        if len(tokens) < 3:
            raise ValueError("Malformed PPM header")

        width = int(tokens[0])
        height = int(tokens[1])
        max_value = int(tokens[2])
        if max_value != 255:
            raise ValueError("Only max value 255 is supported")

        data = f.read(width * height * 3)
        if len(data) != width * height * 3:
            raise ValueError("PPM payload size does not match width/height")

    pixels: List[List[RGBTuple]] = []
    idx = 0
    for _ in range(height):
        row: List[RGBTuple] = []
        for _ in range(width):
            row.append((data[idx], data[idx + 1], data[idx + 2]))
            idx += 3
        pixels.append(row)

    return Image(width=width, height=height, pixels=pixels)


def write_ppm(image: Image, path: str) -> None:
    header = f"P6\n{image.width} {image.height}\n255\n".encode("ascii")
    payload = bytearray()
    for row in image.pixels:
        if len(row) != image.width:
            raise ValueError("Row width does not match image width")
        for r, g, b in row:
            payload.extend((r, g, b))

    if len(image.pixels) != image.height:
        raise ValueError("Image height does not match number of rows")

    with open(path, "wb") as f:
        f.write(header)
        f.write(payload)

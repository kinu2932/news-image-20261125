#!/usr/bin/env python3
"""news-image-20261125: sum up Wednesday 25 November 2026 world news in one
1024x1024 PNG. Pure stdlib (zlib/struct/os/sys) - no Pillow, no network.
Deterministic: same bytes on every run.
"""
import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font 5x7
# Each glyph: 7 rows of 5 bits, '#' = on.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
}

CREAM = (242, 234, 216)
PAPER = (247, 240, 224)
NAVY = (22, 40, 63)
INK = (28, 32, 40)
RED = (179, 39, 30)
BLUE = (31, 78, 121)
TEAL = (14, 124, 123)
ORANGE = (217, 108, 30)
GOLD = (201, 162, 39)
GREEN = (46, 125, 50)
PURPLE = (106, 61, 154)
PINK = (194, 24, 91)
BROWN = (121, 85, 72)
GREY = (93, 109, 126)
WHITE = (255, 255, 255)
BLACK = (12, 12, 14)
SKY = (140, 180, 205)
SEA = (24, 68, 110)
SEADARK = (16, 48, 84)
MAPBG = (214, 226, 232)
LAND = (232, 214, 170)


class Img:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.buf), 3):
            self.buf[i] = r
            self.buf[i + 1] = g
            self.buf[i + 2] = b

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = c
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x1 - x0):
                i = base + xx * 3
                self.buf[i] = r
                self.buf[i + 1] = g
                self.buf[i + 2] = b

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.px(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.px(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if abs(d - r) <= t / 2.0:
                    self.px(xx, yy, c)

    def poly(self, pts, c):
        # even-odd scanline fill
        if not pts:
            return
        ymin = min(p[1] for p in pts)
        ymax = max(p[1] for p in pts)
        n = len(pts)
        for y in range(ymin, ymax + 1):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    xs.append(x)
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.px(x, y, c)

    def star(self, cx, cy, r1, r2, n, c):
        import math
        pts = []
        for i in range(2 * n):
            r = r1 if i % 2 == 0 else r2
            a = -math.pi / 2 + i * math.pi / n
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        self.poly(pts, c)

    def text(self, x, y, s, c, txt):
        txt = txt.upper()
        cx = x
        for ch in txt:
            g = FONT.get(ch)
            if g is None:
                cx += 6 * s
                continue
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.fill_rect(cx + col * s, y + row * s, s, s, c)
            cx += 6 * s
        return cx

    def text_w(self, s, txt):
        return len(txt) * 6 * s - s

    def text_c(self, cx, y, s, c, txt):
        w = self.text_w(s, txt)
        return self.text(cx - w // 2, y, s, c, txt)


def png_bytes(img):
    raw = bytearray()
    stride = img.w * 3
    for y in range(img.h):
        raw.append(0)
        raw += img.buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack('>I', len(data)) + typ + data
        out += struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack('>IIBBBBB', img.w, img.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', comp) + chunk(b'IEND', b''))


# ---------------------------------------------------------------- icons
# Each icon draws inside a box (bx, by, size) in one foreground colour.
def _ic_ship(im, bx, by, s, fg):
    im.poly([(bx + 2, by + s * 0.55), (bx + s - 2, by + s * 0.55),
             (bx + s - 8, by + s * 0.8), (bx + 8, by + s * 0.8)], fg)
    im.fill_rect(bx + s // 2 - 2, by + 4, 4, int(s * 0.4), fg)
    im.fill_rect(bx + s // 2 + 2, by + 8, int(s * 0.28), 6, fg)
    im.line(bx + 2, by + s - 6, bx + s - 2, by + s - 6, fg, 2)
    im.line(bx + 6, by + s - 2, bx + s - 6, by + s - 2, fg, 2)


def _ic_boom(im, bx, by, s, fg):
    im.star(bx + s // 2, by + s // 2, s // 2, s // 5, 8, fg)
    im.disc(bx + s // 2, by + s // 2, s // 6, (255, 220, 120))


def _ic_flame(im, bx, by, s, fg):
    im.poly([(bx + s // 2, by + 2), (bx + s - 4, by + s * 0.55),
             (bx + s * 0.7, by + s - 4), (bx + s * 0.3, by + s - 4),
             (bx + 4, by + s * 0.55)], fg)
    im.poly([(bx + s // 2, by + s * 0.45), (bx + s * 0.65, by + s * 0.75),
             (bx + s * 0.35, by + s * 0.75)], (255, 220, 120))


def _ic_gavel(im, bx, by, s, fg):
    im.fill_rect(bx + 4, by + 6, int(s * 0.6), int(s * 0.22), fg)
    im.line(bx + s // 2, by + int(s * 0.28), bx + s - 6, by + s - 6, fg, 4)
    im.fill_rect(bx + 4, by + s - 10, s - 8, 5, fg)


def _ic_bug(im, bx, by, s, fg):
    im.rect(bx + 6, by + 8, s - 12, int(s * 0.55), fg, 3)
    im.line(bx + 2, by + s - 8, bx + s - 2, by + s - 8, fg, 3)
    im.disc(bx + s // 2, by + int(s * 0.35), 4, fg)
    for dx in (-10, -5, 5, 10):
        im.line(bx + s // 2 + dx, by + int(s * 0.35) + 6,
                bx + s // 2 + dx, by + int(s * 0.55), fg, 2)


def _ic_tower(im, bx, by, s, fg):
    im.poly([(bx + s // 2 - 6, by + s - 4), (bx + s // 2 - 4, by + 6),
             (bx + s // 2 + 4, by + 6), (bx + s // 2 + 6, by + s - 4)], fg)
    for yy in range(by + 14, by + s - 8, 8):
        im.fill_rect(bx + s // 2 - 2, yy, 4, 4, (255, 220, 120))
    im.line(bx + s // 2, by + 2, bx + s // 2, by + 6, fg, 2)


def _ic_bird(im, bx, by, s, fg):
    im.disc(bx + s // 2, by + s // 2 + 4, s // 4, fg)
    im.disc(bx + s // 2 + 8, by + s // 2 - 6, s // 7, fg)
    for a in range(-2, 3):
        im.line(bx + s // 2 - 10 + a * 3, by + s // 2 - 2,
                bx + s // 2 - 14 + a * 4, by + 2, fg, 2)
    im.line(bx + s // 2 + 8, by + s // 2 - 6, bx + s // 2 + 14, by + s // 2 - 4, fg, 2)


def _ic_medal(im, bx, by, s, fg):
    im.poly([(bx + s // 2 - 8, by + 2), (bx + s // 2 - 2, by + 2),
             (bx + s // 2 + 2, by + int(s * 0.4)), (bx + s // 2 + 8, by + 2),
             (bx + s // 2 + 4, by + 2), (bx + s // 2, by + int(s * 0.35))], fg)
    im.disc(bx + s // 2, by + int(s * 0.68), s // 4, (255, 220, 120))
    im.ring(bx + s // 2, by + int(s * 0.68), s // 4, fg, 2)
    im.text(bx + s // 2 - 3, by + int(s * 0.68) - 3, 1, fg, "1")


def _ic_plane(im, bx, by, s, fg):
    im.poly([(bx + 2, by + s // 2), (bx + s - 4, by + s // 2 - 4),
             (bx + s - 2, by + s // 2), (bx + s - 4, by + s // 2 + 4)], fg)
    im.poly([(bx + s // 2, by + s // 2 - 2), (bx + s // 2 + 8, by + 4),
             (bx + s // 2 + 12, by + 4), (bx + s // 2 + 2, by + s // 2 + 2)], fg)
    im.poly([(bx + s // 2, by + s // 2 + 2), (bx + s // 2 + 8, by + s - 6),
             (bx + s // 2 + 12, by + s - 6), (bx + s // 2 + 2, by + s // 2 - 2)], fg)


def _ic_cross(im, bx, by, s, fg):
    im.fill_rect(bx + s // 2 - 3, by + 6, 6, s - 12, fg)
    im.fill_rect(bx + 6, by + s // 2 - 10, s - 12, 6, fg)


def _ic_virus(im, bx, by, s, fg):
    cx, cy = bx + s // 2, by + s // 2
    im.disc(cx, cy, s // 4, fg)
    for k in range(8):
        import math
        a = k * math.pi / 4
        im.line(cx + int(s * 0.22 * math.cos(a)), cy + int(s * 0.22 * math.sin(a)),
                cx + int(s * 0.38 * math.cos(a)), cy + int(s * 0.38 * math.sin(a)), fg, 2)
    im.disc(cx - 4, cy - 3, 2, (255, 220, 120))
    im.disc(cx + 5, cy + 4, 2, (255, 220, 120))


def _ic_flag(im, bx, by, s, fg):
    im.line(bx + 8, by + 4, bx + 8, by + s - 4, fg, 3)
    im.poly([(bx + 8, by + 4), (bx + s - 4, by + 10), (bx + 8, by + 18)], fg)
    im.disc(bx + 8, by + 4, 3, fg)


def _ic_ballot(im, bx, by, s, fg):
    im.rect(bx + 6, by + 10, s - 12, s - 16, fg, 3)
    im.line(bx + 10, by + s // 2 + 2, bx + s // 2 - 2, by + s - 8, fg, 3)
    im.line(bx + s // 2 - 2, by + s - 8, bx + s - 8, by + 8, fg, 3)


def _ic_trophy(im, bx, by, s, fg):
    im.poly([(bx + 8, by + 6), (bx + s - 8, by + 6), (bx + s - 10, by + s // 2),
             (bx + 10, by + s // 2)], (255, 220, 120))
    im.line(bx + 8, by + 10, bx + 2, by + 16, fg, 3)
    im.line(bx + s - 8, by + 10, bx + s - 2, by + 16, fg, 3)
    im.fill_rect(bx + s // 2 - 2, by + s // 2, 4, 8, fg)
    im.fill_rect(bx + s // 2 - 10, by + s - 8, 20, 5, fg)


def _ic_radar(im, bx, by, s, fg):
    cx, cy = bx + s // 2, by + s // 2 + 4
    for r in (8, 14, 20):
        im.ring(cx, cy, r, fg, 1)
    im.line(cx, cy, cx + 14, cy - 12, fg, 2)
    im.disc(cx, cy, 4, (255, 220, 120))


def _ic_shield(im, bx, by, s, fg):
    im.poly([(bx + 6, by + 4), (bx + s - 6, by + 4), (bx + s - 6, by + s // 2),
             (bx + s // 2, by + s - 4), (bx + 6, by + s // 2)], fg)
    im.line(bx + s // 2 - 6, by + s // 2, bx + s // 2 - 1, by + s // 2 + 6, (255, 220, 120), 3)
    im.line(bx + s // 2 - 1, by + s // 2 + 6, bx + s // 2 + 8, by + s // 2 - 6, (255, 220, 120), 3)


def _ic_handshake(im, bx, by, s, fg):
    im.poly([(bx + 4, by + s // 2 - 4), (bx + s // 2, by + s // 2 - 4),
             (bx + s // 2, by + s // 2 + 8), (bx + 4, by + s // 2 + 8)], fg)
    im.poly([(bx + s - 4, by + s // 2 - 8), (bx + s // 2, by + s // 2 - 8),
             (bx + s // 2, by + s // 2 + 4), (bx + s - 4, by + s // 2 + 4)], (255, 220, 120))
    for dx in range(0, 4):
        im.line(bx + s // 2 - 2 + dx * 4, by + s // 2 + 4,
                bx + s // 2 - 2 + dx * 4, by + s // 2 + 12, fg, 2)


def _ic_rocket(im, bx, by, s, fg):
    im.poly([(bx + s // 2, by + 2), (bx + s // 2 + 8, by + s // 2),
             (bx + s // 2 - 8, by + s // 2)], fg)
    im.fill_rect(bx + s // 2 - 8, by + s // 2, 16, 10, fg)
    im.poly([(bx + s // 2 - 8, by + s // 2 + 10), (bx + s // 2 - 14, by + s - 8),
             (bx + s // 2 - 8, by + s // 2 + 10)], fg)
    im.poly([(bx + s // 2 + 8, by + s // 2 + 10), (bx + s // 2 + 14, by + s - 8),
             (bx + s // 2 + 8, by + s // 2 + 10)], fg)
    im.poly([(bx + s // 2, by + s - 12), (bx + s // 2 + 5, by + s - 4),
             (bx + s // 2 - 5, by + s - 4)], (255, 160, 60))


def _ic_siren(im, bx, by, s, fg):
    im.poly([(bx + s // 2, by + 6), (bx + s - 6, by + s - 8), (bx + 6, by + s - 8)], fg)
    im.text(bx + s // 2 - 3, by + s // 2 - 2, 1, (255, 220, 120), "!")
    for a in range(-2, 3):
        im.line(bx + s // 2 + a * 8, by + 2, bx + s // 2 + a * 10, by - 2, fg, 1)


def _ic_chip(im, bx, by, s, fg):
    im.fill_rect(bx + 10, by + 10, s - 20, s - 20, fg)
    im.fill_rect(bx + s // 2 - 6, by + s // 2 - 6, 12, 12, (255, 220, 120))
    for k in range(3):
        im.line(bx + 12 + k * 8, by + 4, bx + 12 + k * 8, by + 10, fg, 2)
        im.line(bx + 12 + k * 8, by + s - 10, bx + 12 + k * 8, by + s - 4, fg, 2)
        im.line(bx + 4, by + 12 + k * 8, bx + 10, by + 12 + k * 8, fg, 2)
        im.line(bx + s - 10, by + 12 + k * 8, bx + s - 4, by + 12 + k * 8, fg, 2)


def _ic_chart(im, bx, by, s, fg):
    for k, h in enumerate((10, 18, 14, 26)):
        im.fill_rect(bx + 6 + k * 9, by + s - 6 - h, 6, h, fg)
    im.line(bx + 4, by + s - 14, bx + s - 4, by + 6, (255, 220, 120), 3)
    im.poly([(bx + s - 4, by + 6), (bx + s - 12, by + 6), (bx + s - 4, by + 14)],
            (255, 220, 120))


def _ic_volcano(im, bx, by, s, fg):
    im.poly([(bx + s // 2, by + 10), (bx + s - 6, by + s - 4), (bx + 6, by + s - 4)], fg)
    im.disc(bx + s // 2, by + 8, 6, (255, 160, 60))
    im.disc(bx + s // 2 - 8, by + 4, 4, (200, 200, 200))
    im.disc(bx + s // 2 + 8, by + 4, 4, (200, 200, 200))


def _ic_film(im, bx, by, s, fg):
    im.rect(bx + 4, by + 8, s - 8, s - 16, fg, 3)
    for yy in (12, 20, 28):
        im.fill_rect(bx + 7, by + yy, 4, 4, fg)
        im.fill_rect(bx + s - 11, by + yy, 4, 4, fg)
    im.poly([(bx + s // 2 - 2, by + 14), (bx + s // 2 + 8, by + 20),
             (bx + s // 2 - 2, by + 26)], (255, 220, 120))


def _ic_coins(im, bx, by, s, fg):
    for k, yy in enumerate((s - 14, s - 22, s - 30)):
        im.fill_rect(bx + 8 + k * 3, by + yy, s - 16 - k * 3, 6, (255, 220, 120))
        im.rect(bx + 8 + k * 3, by + yy, s - 16 - k * 3, 6, fg, 1)
    im.text(bx + s // 2 - 6, by + s - 30, 1, fg, "EU")


def _ic_bridge(im, bx, by, s, fg):
    im.fill_rect(bx + 4, by + s // 2 + 4, s - 8, 5, fg)
    im.line(bx + 4, by + s // 2 + 4, bx + s // 2, by + 8, fg, 3)
    im.line(bx + s - 4, by + s // 2 + 4, bx + s // 2, by + 8, fg, 3)
    im.line(bx + s // 2, by + 8, bx + s // 2, by + s // 2 + 4, fg, 3)
    im.line(bx + 4, by + s - 4, bx + s - 4, by + s - 4, fg, 2)


def _ic_missile(im, bx, by, s, fg):
    im.poly([(bx + s - 4, by + s // 2), (bx + s // 2, by + s // 2 - 6),
             (bx + 8, by + s // 2 - 6), (bx + 8, by + s // 2 + 6),
             (bx + s // 2, by + s // 2 + 6)], fg)
    im.poly([(bx + 14, by + s // 2 - 6), (bx + 20, by + 4),
             (bx + 20, by + s // 2 - 6)], fg)
    im.poly([(bx + 14, by + s // 2 + 6), (bx + 20, by + s - 4),
             (bx + 20, by + s // 2 + 6)], fg)
    im.poly([(bx + 8, by + s // 2), (bx + 2, by + s // 2 - 4),
             (bx + 2, by + s // 2 + 4)], (255, 160, 60))


def _ic_globe(im, bx, by, s, fg):
    cx, cy = bx + s // 2, by + s // 2
    im.ring(cx, cy, s // 2 - 3, fg, 2)
    im.line(cx - s // 2 + 3, cy, cx + s // 2 - 3, cy, fg, 1)
    im.line(cx, cy - s // 2 + 3, cx, cy + s // 2 - 3, fg, 1)
    im.disc(cx - 6, cy - 8, 5, fg)
    im.disc(cx + 8, cy + 6, 6, fg)


def _ic_bars(im, bx, by, s, fg):
    for k in range(4):
        im.fill_rect(bx + 6 + k * 9, by + 4, 4, s - 8, fg)
    im.fill_rect(bx + 4, by + 4, s - 8, 4, fg)
    im.fill_rect(bx + 4, by + s - 8, s - 8, 4, fg)


def _ic_heli(im, bx, by, s, fg):
    im.line(bx + 4, by + 6, bx + s - 4, by + 6, fg, 3)
    im.disc(bx + s // 2, by + s // 2, s // 4, fg)
    im.fill_rect(bx + s // 2 + 6, by + s // 2 - 4, 14, 6, fg)
    im.line(bx + s // 2 - 6, by + s // 2 + 8, bx + s // 2 - 12, by + s - 4, fg, 2)
    im.line(bx + s // 2 + 6, by + s // 2 + 8, bx + s // 2 + 12, by + s - 4, fg, 2)


def _ic_pause(im, bx, by, s, fg):
    im.fill_rect(bx + s // 2 - 10, by + 8, 7, s - 16, fg)
    im.fill_rect(bx + s // 2 + 3, by + 8, 7, s - 16, fg)


ICONS = {
    'ship': _ic_ship, 'boom': _ic_boom, 'flame': _ic_flame, 'gavel': _ic_gavel,
    'bug': _ic_bug, 'tower': _ic_tower, 'bird': _ic_bird, 'medal': _ic_medal,
    'plane': _ic_plane, 'cross': _ic_cross, 'virus': _ic_virus, 'flag': _ic_flag,
    'ballot': _ic_ballot, 'trophy': _ic_trophy, 'radar': _ic_radar,
    'shield': _ic_shield, 'handshake': _ic_handshake, 'rocket': _ic_rocket,
    'siren': _ic_siren, 'chip': _ic_chip, 'chart': _ic_chart,
    'volcano': _ic_volcano, 'film': _ic_film, 'coins': _ic_coins,
    'bridge': _ic_bridge, 'missile': _ic_missile, 'globe': _ic_globe,
    'bars': _ic_bars, 'heli': _ic_heli, 'pause': _ic_pause,
}


# ---------------------------------------------------------------- stories
# Grid: 30 stories. (line1, line2, kicker, colour, icon)
GRID = [
    ("COP31", "COLLAPSES", "ANTALYA: NO DEAL", RED, "globe"),
    ("CIA+ODNI", "BREACHED", "UNCLASSIFIED HACK", BLUE, "bug"),
    ("HUAWEI", "CONVICTED", "US JURY: SECRETS", PURPLE, "gavel"),
    ("HOUTHI HIT", "RIYADH TOWER", "11 HURT IN CAPITAL", ORANGE, "tower"),
    ("TURKEYS", "PARDONED", "TRUMP: FREEDOM+FEATHERS", BROWN, "bird"),
    ("GIULIANI", "HONOURED", "MEDAL OF FREEDOM", GOLD, "medal"),
    ("NATO JETS", "TO POLAND", "EARLY WARNING OK", TEAL, "plane"),
    ("700,000", "RUSSIAN DEAD", "MEDUZA ESTIMATE", GREY, "cross"),
    ("WHO FLEES", "DR CONGO", "EBOLA: 5,775 DEAD", GREEN, "virus"),
    ("GAZA TOLL", "74,746 DEAD", "WAR COUNT RISES", RED, "flag"),
    ("BJP-SAD", "ALLIANCE", "PUNJAB POLLS 2027", ORANGE, "ballot"),
    ("ENGLAND WIN", "V AUSTRALIA", "2ND T20I", GREEN, "trophy"),
    ("RUSSIAN JETS", "PROBE NATO", "25 VIOLATIONS 2026", BLUE, "radar"),
    ("EU NEW", "SANCTIONS", "BANKS, TROOPS", NAVY, "shield"),
    ("ARMENIA", "PEACE DRAFT", "KARABAKH CLAIM OUT", PURPLE, "handshake"),
    ("SHENZHOU-24", "CREW NAMED", "1ST PAKISTANI UP", BLUE, "rocket"),
    ("SEOUL", "TAKE SHELTER", "RUSSIAN JETS NEAR", RED, "siren"),
    ("HUANG", "PARDON TALK", "TRUMP BEFORE CONGRESS", GOLD, "chip"),
    ("NEW TARIFFS", "INDIA+CHINA", "14 MORE HIT", ORANGE, "chart"),
    ("HASINA", "TO RETURN", "DHAKA: EXTRADITION", TEAL, "flag"),
    ("CARTAGENA", "HOSTAGES", "DOZENS HELD IN MARKET", RED, "bars"),
    ("TURKISH", "CHOPPER DOWN", "TRAINING FLIGHT", GREY, "heli"),
    ("UK SANCTIONS", "HOUTHIS", "4 OFFICIALS NAMED", NAVY, "gavel"),
    ("SAUDI HITS", "HODEIDAH", "AFTER RED SEA THREATS", ORANGE, "boom"),
    ("DEEP VOLCANO", "FOUND", "MARIANA TRENCH", BROWN, "volcano"),
    ("RAMAYANA", "SHORTLISTED", "CRITICS CHOICE 2027", PINK, "film"),
    ("EU LOAN", "45BN TO KYIV", "FOR UKRAINE 2027", BLUE, "coins"),
    ("KERCH BRIDGE", "SPAN LOST", "SUPPLY LINE HIT", GREY, "bridge"),
    ("PATRIOT", "DELAYED", "PENTAGON HOLDS BACK", GREEN, "missile"),
    ("US-IRAN", "HORMUZ TALKS", "QATAR MEDIATES", TEAL, "handshake"),
]


def draw_masthead(im):
    im.fill_rect(0, 0, W, 76, NAVY)
    im.fill_rect(0, 76, W, 4, RED)
    im.text_c(W // 2, 10, 4, CREAM, "THE WORLD IN ONE PAGE")
    im.text_c(W // 2, 48, 2, GOLD, "WEDNESDAY 25 NOVEMBER 2026 - 34 STORIES, ONE DAY")


def draw_hero(im):
    x0, y0, x1, y1 = 8, 84, 508, 296
    # sky bands
    im.fill_rect(x0, y0, x1 - x0, 40, (58, 84, 110))
    im.fill_rect(x0, y0 + 40, x1 - x0, 26, (196, 120, 70))
    im.fill_rect(x0, y0 + 66, x1 - x0, 14, (232, 150, 80))
    # sea
    im.fill_rect(x0, y0 + 80, x1 - x0, y1 - y0 - 80 - 60, SEA)
    im.fill_rect(x0, y0 + 80, x1 - x0, 4, (90, 140, 190))
    # waves
    for wx in range(x0 + 10, x1 - 10, 46):
        im.line(wx, y0 + 118, wx + 22, y0 + 118, (150, 200, 235), 2)
        im.line(wx + 8, y0 + 140, wx + 30, y0 + 140, (120, 175, 220), 2)
    # distant cargo ship (Finland story)
    im.poly([(398, 168), (470, 168), (462, 182), (406, 182)], GREY)
    im.fill_rect(420, 156, 22, 12, (70, 80, 95))
    im.line(398, 184, 472, 184, (150, 200, 235), 2)
    # main warship, listing, on fire
    im.poly([(90, 178), (330, 178), (312, 202), (108, 202)], (120, 130, 145))
    im.fill_rect(150, 158, 60, 20, (90, 100, 115))
    im.fill_rect(230, 164, 34, 14, (90, 100, 115))
    im.line(180, 158, 180, 138, (70, 80, 95), 3)
    im.line(180, 138, 196, 146, (70, 80, 95), 2)
    # explosion starburst above the ship
    im.star(300, 132, 46, 18, 9, (255, 170, 40))
    im.star(300, 132, 28, 12, 9, (255, 220, 110))
    im.disc(300, 132, 12, (255, 240, 180))
    # smoke
    im.disc(268, 108, 12, (90, 90, 95))
    im.disc(288, 96, 15, (110, 110, 115))
    im.disc(312, 104, 11, (80, 80, 85))
    # drone boat with wake
    im.poly([(60, 210), (96, 210), (88, 220), (68, 220)], (30, 34, 40))
    im.line(96, 215, 140, 215, WHITE, 2)
    im.line(96, 219, 132, 219, (200, 220, 235), 1)
    # headline band
    hy = y1 - 64
    im.fill_rect(x0, hy, x1 - x0, 64, NAVY)
    im.text_c((x0 + x1) // 2, hy + 4, 3, CREAM, "UKRAINE SINKS RUSSIAN")
    im.text_c((x0 + x1) // 2, hy + 27, 3, (255, 200, 90), "WARSHIP OFF BENGHAZI")
    im.text_c((x0 + x1) // 2, hy + 53, 1, (200, 210, 225),
              "FINLAND HIT TOO - PUTIN VOWS REVENGE")
    im.rect(x0, y0, x1 - x0, y1 - y0, NAVY, 2)


def draw_map(im):
    x0, y0, x1, y1 = 516, 84, 1016, 296
    im.fill_rect(x0, y0, x1 - x0, y1 - y0, MAPBG)
    im.text(x0 + 10, y0 + 6, 2, NAVY, "WHERE IT HAPPENED")
    im.text(x1 - 118, y0 + 8, 1, GREY, "25 NOV 2026")
    # graticule
    for gx in range(x0 + 40, x1, 50):
        im.line(gx, y0 + 26, gx, y0 + 150, (190, 205, 215), 1)
    for gy in range(y0 + 50, y0 + 150, 34):
        im.line(x0, gy, x1, gy, (190, 205, 215), 1)
    # continents (rough)
    im.poly([(540, 120), (600, 112), (640, 120), (645, 140), (620, 150),
             (600, 165), (575, 160), (550, 145), (535, 130)], LAND)
    im.poly([(650, 105), (665, 105), (665, 115), (650, 115)], LAND)
    im.poly([(600, 170), (630, 168), (640, 185), (625, 215), (610, 225),
             (600, 200), (595, 180)], LAND)
    im.poly([(740, 118), (775, 110), (790, 120), (780, 135), (755, 135),
             (740, 128)], LAND)
    im.poly([(745, 140), (790, 140), (805, 155), (795, 190), (770, 205),
             (750, 180), (740, 155)], LAND)
    im.poly([(795, 110), (960, 105), (985, 120), (970, 150), (930, 165),
             (880, 160), (840, 150), (800, 135)], LAND)
    im.poly([(900, 200), (950, 195), (960, 210), (920, 218), (895, 210)], LAND)
    im.poly([(735, 112), (742, 112), (742, 120), (735, 120)], LAND)
    # numbered hotspots
    spots = [(782, 152, "1"), (766, 106, "2"), (794, 128, "3"),
             (818, 162, "4"), (802, 148, "5"), (766, 184, "6"),
             (945, 128, "7"), (575, 135, "8")]
    for sx, sy, n in spots:
        im.disc(sx, sy, 8, RED)
        im.ring(sx, sy, 8, WHITE, 1)
        im.text(sx - 3, sy - 3, 1, WHITE, n)
    im.text_c((x0 + x1) // 2, y0 + 148, 1, NAVY,
              "1 BENGHAZI  2 FINLAND  3 ANTALYA  4 RIYADH")
    im.text_c((x0 + x1) // 2, y0 + 158, 1, NAVY,
              "5 GAZA  6 CONGO  7 SEOUL  8 WASHINGTON")
    # callout: story 34
    cy = y1 - 52
    im.fill_rect(x0, cy, x1 - x0, 52, RED)
    im.text(x0 + 12, cy + 6, 2, WHITE, "IOWA LEAD BLAST ON HOLD")
    im.text(x0 + 12, cy + 30, 1, (255, 220, 210),
            "TRUMP ORDERS ARMY TO WAIT FOR COURT")
    im.text(x1 - 30, cy + 6, 2, WHITE, "34")
    im.rect(x0, y0, x1 - x0, y1 - y0, NAVY, 2)


def draw_grid(im):
    cw, ch, gx, gy = 163, 132, 6, 8
    for idx, (l1, l2, kick, col, icon) in enumerate(GRID):
        r, c = divmod(idx, 6)
        x = 8 + c * (cw + gx)
        y = 304 + r * (ch + gy)
        im.fill_rect(x, y, cw, ch, WHITE)
        im.rect(x, y, cw, ch, (200, 195, 180), 1)
        im.fill_rect(x, y, cw, 52, col)
        ICONS[icon](im, x + cw // 2 - 22, y + 4, 44, WHITE)
        im.text(x + 5, y + 6, 1, (255, 255, 255), "%02d" % (idx + 4))
        im.text(x + 6, y + 58, 2, INK, l1)
        im.text(x + 6, y + 74, 2, INK, l2)
        im.fill_rect(x + 6, y + 94, cw - 12, 2, col)
        im.text(x + 6, y + 102, 1, (90, 90, 95), kick)


def draw_footer(im):
    im.text_c(W // 2, 1006, 1, (110, 105, 95),
              "SOURCES: REUTERS - AP - BBC - NYT - THE GUARDIAN - MIDDLE EAST EYE")


def render():
    im = Img(W, H, PAPER)
    draw_masthead(im)
    draw_hero(im)
    draw_map(im)
    draw_grid(im)
    draw_footer(im)
    return im


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(render())
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()

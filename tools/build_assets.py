#!/usr/bin/env python3
"""캐릭터 스프라이트 누끼·정렬·WebP 내보내기, 배경 리사이즈.

표정마다 다시 그려진 원본이라 몸 높이와 위치가 조금씩 다르다.
실루엣 bbox 높이를 공통 기준으로 맞추고, 발끝을 아래에, 몸 중심을 가로 가운데에
정렬해 표정을 바꿔도 얼굴 크기와 위치가 흔들리지 않게 한다.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

RAW = "../../downloads/magic-vn-raw"
OUT = "../assets/img"

CHARS = {
    "elize": ["base", "blush", "surprised", "serious"],
    "seia": ["base", "blush", "surprised", "serious"],
}
BGS = ["bg_hall", "bg_greenhouse", "bg_observatory", "bg_lake"]

MX_T, SAT_T, ERODE, BLUR = 246, 9, 5, 0.8
TARGET_H = 1400


def alpha_of(path):
    """흰 배경을 안쪽부터 채워 실루엣을 잡고, 테두리 색을 안쪽 색으로 바꾼다."""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    mx = a.max(axis=2)
    mn = a.min(axis=2)
    ink = (mx < MX_T) | ((mx - mn) > SAT_T)

    m = Image.fromarray(np.where(ink, 255, 0).astype(np.uint8), "L")
    w, h = m.size
    padded = Image.new("L", (w + 2, h + 2), 0)
    padded.paste(m, (1, 1))
    ImageDraw.floodfill(padded, (0, 0), 128, thresh=0)
    bg = (np.asarray(padded) == 128)[1:-1, 1:-1]

    al = Image.fromarray(np.where(~bg, 255, 0).astype(np.uint8), "L")
    al = al.filter(ImageFilter.MinFilter(ERODE)).filter(ImageFilter.GaussianBlur(BLUR))

    alpha = np.asarray(al).astype(np.float32)
    rgb = np.asarray(im).astype(np.float32)

    # 테두리 색 오염 제거: 불투명 픽셀 색을 바깥으로 8px 번지게 채운다
    core = alpha > 235
    filled = rgb.copy()
    have = core.copy()
    for _ in range(8):
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            s_rgb = np.roll(filled, (dy, dx), axis=(0, 1))
            s_have = np.roll(have, (dy, dx), axis=(0, 1))
            take = (~have) & s_have
            filled[take] = s_rgb[take]
            have = have | take
    edge = (~core) & (alpha > 0)
    out = rgb.copy()
    out[edge] = filled[edge]

    arr = np.dstack([out.astype(np.uint8), alpha.astype(np.uint8)])
    return Image.fromarray(arr, "RGBA")


def cut(name, expr):
    rgba = alpha_of(os.path.join(RAW, "ch_%s_%s.png" % (name, expr)))
    bbox = rgba.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    pad = 4
    box = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
           min(rgba.width, bbox[2] + pad), min(rgba.height, bbox[3] + pad))
    return rgba.crop(box)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, exprs in CHARS.items():
        cuts = {}
        for e in exprs:
            c = cut(name, e)
            th = TARGET_H
            tw = max(1, round(c.width * th / c.height))
            cuts[e] = c.resize((tw, th), Image.LANCZOS)
            print("%s_%s 원본 %s -> %s" % (name, e, c.size, (tw, th)))
        cw = max(c.width for c in cuts.values())
        for e, c in cuts.items():
            canvas = Image.new("RGBA", (cw, TARGET_H), (0, 0, 0, 0))
            canvas.paste(c, ((cw - c.width) // 2, TARGET_H - c.height), c)
            out = os.path.join(OUT, "%s_%s.webp" % (name, e))
            canvas.save(out, "WEBP", quality=90, method=6)
            print(" ", os.path.basename(out), canvas.size, os.path.getsize(out))

    for b in BGS:
        im = Image.open(os.path.join(RAW, "%s.png" % b)).convert("RGB")
        im = im.resize((1536, 864), Image.LANCZOS)
        out = os.path.join(OUT, "%s.webp" % b.replace("bg_", ""))
        im.save(out, "WEBP", quality=85, method=6)
        print(" ", os.path.basename(out), os.path.getsize(out))


if __name__ == "__main__":
    main()

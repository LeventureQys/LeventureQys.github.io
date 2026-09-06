# -*- coding: utf-8 -*-
from PIL import Image
from itertools import zip_longest

for pair in [("balance_selftest_plain_on.png", "balance_selftest_plain_off.png"),
             ("balance_selftest_layout_on.png", "balance_selftest_layout_off.png")]:
    a = Image.open(pair[0]).convert("RGB")
    b = Image.open(pair[1]).convert("RGB")
    diff = 0
    purple_a = 0
    purple_b = 0
    pa, pb = a.load(), b.load()
    for y in range(a.height):
        for x in range(a.width):
            ra, ga, ba = pa[x, y]
            rb, gb, bb = pb[x, y]
            if abs(ra - rb) + abs(ga - gb) + abs(ba - bb) > 18:
                diff += 1
            if ba > ga + 15 and ba > 45:
                purple_a += 1
            if bb > gb + 15 and bb > 45:
                purple_b += 1
    print(f"{pair[0]}: purple_on={purple_a} purple_off={purple_b} diff_px={diff}")

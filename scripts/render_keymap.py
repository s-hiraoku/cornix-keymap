#!/usr/bin/env python3
"""Draw the current Cornix bindings as self-contained, GitHub-friendly SVGs."""
import argparse
import re
from html import escape
from pathlib import Path

from import_kobitokey import POSITIONS, bindings

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config/cornix.keymap"
WIDTH = 1120
CARD_HEIGHT = 400
FONT = "'Noto Sans CJK JP','Hiragino Kaku Gothic ProN','Yu Gothic',sans-serif"
KEYS = {
    "LSHFT": "LShift", "RSHFT": "RShift", "LALT": "LAlt", "RALT": "RAlt",
    "LCMD": "LCmd", "LCTRL": "LCtrl", "SPACE": "Space", "ENTER": "Enter",
    "BSPC": "Bksp", "ESC": "Esc", "TAB": "Tab", "DEL": "Delete",
    "SEMI": ";", "APOS": "'", "COMMA": ",", "DOT": ".", "SLASH": "/",
    "BSLH": "\\", "PLUS": "+", "MINUS": "-", "ASTRK": "*", "EQUAL": "=",
    "PRCNT": "%", "LPAR": "(", "RPAR": ")", "EXCL": "!", "AT": "@",
    "HASH": "#", "DLLR": "$", "CARET": "^", "AMPS": "&", "TILDE": "~",
    "GRAVE": "`", "LBRC": "{", "RBRC": "}", "UNDER": "_", "PIPE": "|",
    "LBKT": "[", "RBKT": "]", "LT": "<", "GT": ">", "QMARK": "?",
    "DQT": '"', "COLON": ":", "C_MUTE": "Mute", "C_VOL_DN": "Vol −",
    "C_VOL_UP": "Vol +", "LEFT": "←", "DOWN": "↓", "UP": "↑", "RIGHT": "→",
    "HOME": "Home", "END": "End", "PG_DN": "PgDn", "PG_UP": "PgUp",
    "LANG1": "かな", "LANG2": "英数",
    **{f"N{i}": str(i) for i in range(10)},
}
SHORT_LAYERS = {
    1: "L1 Fn", 2: "L2 Num", 3: "L3 Symbol",
}
SUBTITLES = {
    0: "通常入力  ·  青い下段は長押しの動作  ·  Alt = Option / Cmd = Command",
    1: "Space を押しながら操作  ·  Fキー / カーソル / ページ移動",
    2: "親指 Enter を押しながら操作  ·  数字 / 四則演算  ·  親指 Bksp は Delete",
    3: "親指 Symbol（タップ側は RShift）を押しながら操作  ·  Shift 不要の記号入力",
    4: "親指 Bksp + Symbol の同時押しで入る  ·  LCtrl / RAlt の位置で通常へ戻る",
}


def key(code):
    return KEYS.get(code, code)


def label(binding):
    p = binding.split()
    op = p[0]
    if op == "&trans":
        return "▽", ""
    if op == "&kp":
        return key(p[1]), ""
    if op in ("&lt_l", "&lt_r"):
        return key(p[2]), SHORT_LAYERS[int(p[1])]
    if op == "&mt":
        return key(p[2]), key(p[1])
    if op == "&to":
        return "通常へ", "Layer " + p[1]
    if op == "&bt":
        if p[1] == "BT_SEL":
            return "BT " + p[2], "接続先を選択"
        if p[1] == "BT_CLR":
            return "BT消去", "現在の接続先"
        if p[1] == "BT_CLR_ALL":
            return "BT全消去", "全ペアリング"
    raise ValueError(f"Add an explicit SVG label for {binding}")


def text(x, y, value, size=18, color="#18304b", weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>')


def rect(x, y, w, h, fill, stroke="none", radius=12):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}"/>')


def layer_card(index, name, keys, y):
    parts = [f'<g id="layer-{index}">', rect(16, y, 1088, 384, "#fff", "#d8e1ec"),
             rect(32, y + 20, 5, 32, "#246bc4", radius=2),
             text(49, y + 44, f"{index:02d}  {name}", 25, weight=700),
             text(36, y + 73, SUBTITLES[index], 15, "#52667e")]
    active = [keys[p] for p in POSITIONS]
    for i, binding in enumerate(active):
        row, col = divmod(i, 10)
        side, column = divmod(col, 5)
        x, ky = 36 + side * 576 + column * 96, y + 92 + row * 66
        tap, hold = label(binding)
        transparent = binding == "&trans"
        is_hold = binding.split()[0] in ("&lt_l", "&lt_r", "&mt")
        fill = "#f0f3f7" if transparent else "#eaf3ff" if is_hold else "#fff"
        parts.extend([f'<g><title>{escape(binding)}</title>',
                      rect(x, ky, 88, 58, fill, "#d2dce8", 9)])
        # Japanese labels need more room than single Latin key legends.
        size = 16 if any(ord(c) > 127 for c in tap) and len(tap) > 2 else 22
        if len(tap) > 8:
            size = 14
        parts.append(text(x + 44, ky + (28 if hold else 37), tap, size,
                          "#8796a8" if transparent else "#18304b", 600, "middle"))
        if hold:
            parts.append(text(x + 44, ky + 47, hold, 12,
                              "#195eb4" if is_hold else "#52667e", 500, "middle"))
        parts.append("</g>")
    parts.append("</g>")
    return parts


def combo_card(source, base, y):
    combos = re.findall(r'\bcombo_\w+\s*\{(.*?)\n\s*};', source, re.S)
    parts = [rect(16, y, 1088, 238, "#fff", "#d8e1ec"),
             text(36, y + 39, "同時押し / COMBOS", 24, weight=700)]
    for i, body in enumerate(combos):
        positions = [int(p) for p in re.search(r'key-positions\s*=\s*<([^>]+)>', body)[1].split()]
        names = []
        for p in positions:
            tap, hold = label(base[p])
            names.append("Symbol" if hold == "L3 Symbol" else tap)
        output = bindings(re.search(r'bindings\s*=\s*<(.*?)>', body, re.S)[1])[0]
        result = "BT 設定へ" if output == "&to 4" else label(output)[0]
        timeout = re.search(r'timeout-ms\s*=\s*<(\d+)>', body)[1]
        scope = "基本レイヤーのみ" if re.search(r'\blayers\s*=', body) else "全レイヤー"
        x, cy = 36 + (i % 2) * 534, y + 60 + (i // 2) * 55
        parts.extend([rect(x, cy, 516, 46, "#f1f6fc", radius=8),
                      text(x + 14, cy + 20, " + ".join(names) + "  →  " + result, 16, weight=600),
                      text(x + 14, cy + 38, f"{scope}  ·  {timeout} ms", 12, "#52667e")])
    return parts


def render(source, layers):
    height = 140 + len(layers) * CARD_HEIGHT + 254
    title = "Cornix LP — KobitoKey / 40 keys"
    desc = "現在のキーマップから生成。上段はタップ、青い下段は長押し。透過は▽。元の40キーのみを図示。"
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
             f'viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc">',
             f'<title id="title">{escape(title)}</title>', f'<desc id="desc">{escape(desc)}</desc>',
             f'<g font-family="{escape(FONT, quote=True)}">',
             rect(0, 0, WIDTH, height, "#f5f8fc", radius=0),
             text(32, 45, title, 29, weight=700),
             text(32, 78, "上段：タップ / 動作　　青い下段：長押し　　▽：下位の有効なレイヤーを使う", 17, "#52667e"),
             text(32, 106, "40キー・5レイヤー。Y / H / P は通常の文字キー。外周・追加位置・ノブは無効。",
                  16, "#52667e")]
    for index, (name, keys) in enumerate(layers):
        parts.extend(layer_card(index, name, keys, 124 + index * CARD_HEIGHT))
    parts.extend(combo_card(source, layers[0][1], 124 + len(layers) * CARD_HEIGHT))
    parts.extend(["</g>", "</svg>", ""])
    return "\n".join(parts)


def generate():
    source = SOURCE.read_text()
    layers = [(name, bindings(body)) for name, body in re.findall(
        r'display-name\s*=\s*"([^"]+)";\s*bindings\s*=\s*<(.*?)>;', source, re.S)]
    if len(layers) != 5 or any(len(keys) != 50 for _, keys in layers):
        raise ValueError("Expected 5 Cornix layers with 50 hardware positions")
    return {
        ROOT / "docs/keymap.svg": render(source, layers),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if committed SVGs differ")
    args = parser.parse_args()
    for path, svg in generate().items():
        if args.check:
            if not path.exists() or path.read_text() != svg:
                raise SystemExit(f"Regenerate {path.relative_to(ROOT)}: python3 scripts/render_keymap.py")
        else:
            path.write_text(svg)
            print(path.relative_to(ROOT))

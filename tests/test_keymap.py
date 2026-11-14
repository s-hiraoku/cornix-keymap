"""Source fidelity checks; real firmware compilation is a separate CI job."""
import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "tests/fixtures/KobitoKey.keymap").read_text()
TARGET = (ROOT / "config/cornix.keymap").read_text()


def layer_bindings(text):
    layers = re.findall(r"\b(default_layer|layer\d+)\s*\{.*?bindings\s*=\s*<(.*?)>;", text, re.S)
    return [[" ".join(s.split()) for s in re.findall(r"&\w+(?:\s+[A-Za-z0-9_]+)*", body)] for _, body in layers]


def node(text, name):
    return re.search(r"\b" + name + r"(?:\s*:\s*\w+)?\s*\{(.*?)\n\s*};", text, re.S)[1]


class SourceFidelity(unittest.TestCase):
    def test_all_560_source_bindings_match(self):
        old, new = layer_bindings(SOURCE), layer_bindings(TARGET)
        self.assertEqual(len(old), 14)
        self.assertEqual(len(new), 14)
        # Independently describe the physical character rows and bottom row.
        positions = [*range(1, 11), *range(13, 23), *range(25, 30), *range(32, 37),
                     38, 39, 40, 42, 43, 44, 45, 46, 48, 49]
        self.assertEqual(len(set(positions)), 40)
        for layer in range(14):
            self.assertEqual(len(old[layer]), 40)
            self.assertEqual(len(new[layer]), 50)
            for i, position in enumerate(positions):
                with self.subTest(layer=layer, source=i, cornix=position):
                    self.assertEqual(new[layer][position], old[layer][i])

    def test_ctrl_space_physical_order(self):
        base = layer_bindings(TARGET)[0]
        self.assertEqual(base[42], "&lt_l 1 SPACE")
        self.assertEqual(base[43], "&kp LCTRL")
        for layer in (4, 8, 13):
            self.assertEqual(layer_bindings(TARGET)[layer][43], "&to 0")
        self.assertEqual(layer_bindings(TARGET)[10][43], "&drag_cancel")

    def test_combos_keep_physical_positions_timing_and_scope(self):
        combos = {
            "combo_eisu": ([15, 16], 80, "&kp LANG2", None),
            "combo_kana": ([19, 20], 80, "&kp LANG1", None),
            "combo_esc": ([1, 2], 50, "&kp ESC", [0]),
            "combo_tab": ([13, 14], 50, "&kp TAB", [0]),
            "combo_bt": ([44, 46], 50, "&to 8", [0]),
        }
        for name, (positions, timeout, binding, scope) in combos.items():
            body = node(TARGET, name)
            values = lambda key: [int(x) for x in re.search(key + r"\s*=\s*<([^>]+)>", body)[1].split()]
            self.assertEqual(values("key-positions"), positions)
            self.assertEqual(values("timeout-ms"), [timeout])
            self.assertIn("<" + binding + ">", body)
            if scope is None:
                self.assertNotRegex(body, r"\blayers\s*=")
            else:
                self.assertEqual(values("layers"), scope)

    def test_custom_behaviors_are_copied_verbatim(self):
        for name in ("zoom_hold", "drag_on", "drag_off", "drag_cancel", "dl", "menu_lt",
                     "menu_zoom", "lt_l", "lt_r"):
            self.assertEqual(node(TARGET, name), node(SOURCE, name), name)
        for behavior in ("lt", "mt"):
            pattern = r"&" + behavior + r"\s*\{(.*?)\n};"
            self.assertEqual(re.search(pattern, TARGET, re.S)[1], re.search(pattern, SOURCE, re.S)[1])
        self.assertIn("retro-tap;", node(TARGET, "lt_l"))
        self.assertNotIn("retro-tap;", node(TARGET, "lt_r"))

    def test_drag_cancel_releases_button_before_leaving(self):
        body = node(TARGET, "drag_cancel")
        self.assertLess(body.index("&macro_release &mkp MB1"), body.index("&macro_tap &to 0"))

    def test_no_invented_gesture_direction_bindings(self):
        layers = layer_bindings(TARGET)
        for layer in (5, 6, 7, 9, 11, 12, 13):
            self.assertNotIn("LCTL(KC_LEFT)", " ".join(layers[layer]))
            self.assertNotIn("&kp LC(LEFT)", " ".join(layers[layer]))
        self.assertNotIn("input/processors.dtsi", TARGET)
        self.assertIn("&studio_unlock", layers[8])

    def test_generated_file_is_current(self):
        spec = importlib.util.spec_from_file_location("adapter", ROOT / "scripts/import_kobitokey.py")
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        self.assertEqual(TARGET, adapter.generate())

    def test_encoder_scroll_uses_pointing_behavior(self):
        self.assertIn("<&msc SCRL_UP>, <&msc SCRL_DOWN>", node(TARGET, "cornix_scroll"))
        self.assertNotIn("&inc_dec_kp SCRL", TARGET)
        self.assertEqual(TARGET.count("sensor-bindings = <&inc_dec_kp C_VOL_UP C_VOL_DN &cornix_scroll>;"), 14)


if __name__ == "__main__":
    unittest.main()

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
    def test_keyboard_layers_match_source_with_explicit_cornix_changes(self):
        old, new = layer_bindings(SOURCE), layer_bindings(TARGET)
        self.assertEqual(len(old), 14)
        self.assertEqual(len(new), 5)
        # Independently describe the physical character rows and bottom row.
        positions = [*range(1, 11), *range(13, 23), *range(25, 30), *range(32, 37),
                     38, 39, 40, 42, 43, 44, 45, 46, 48, 49]
        self.assertEqual(len(set(positions)), 40)
        for layer, source_layer in enumerate((0, 1, 2, 3, 8)):
            self.assertEqual(len(old[source_layer]), 40)
            self.assertEqual(len(new[layer]), 50)
            for i, position in enumerate(positions):
                with self.subTest(layer=layer, source=i, cornix=position):
                    expected = old[source_layer][i]
                    if layer == 0 and i in (5, 9, 15):
                        expected = {5: "&kp Y", 9: "&kp P", 15: "&kp H"}[i]
                    self.assertEqual(new[layer][position], expected)

    def test_default_y_h_p_are_plain_repeatable_letters(self):
        base = layer_bindings(TARGET)[0]
        for position, binding in ((6, "&kp Y"), (18, "&kp H"), (10, "&kp P")):
            self.assertEqual(base[position], binding)

    def test_ctrl_space_physical_order(self):
        base = layer_bindings(TARGET)[0]
        self.assertEqual(base[42], "&lt_l 1 SPACE")
        self.assertEqual(base[43], "&kp LCTRL")
        self.assertEqual(layer_bindings(TARGET)[4][43], "&to 0")
        self.assertEqual(layer_bindings(TARGET)[4][48], "&to 0")

    def test_combos_keep_physical_positions_timing_and_scope(self):
        combos = {
            "combo_eisu": ([15, 16], 80, "&kp LANG2", None),
            "combo_kana": ([19, 20], 80, "&kp LANG1", None),
            "combo_esc": ([1, 2], 50, "&kp ESC", [0]),
            "combo_tab": ([13, 14], 50, "&kp TAB", [0]),
            "combo_bt": ([44, 46], 50, "&to 4", [0]),
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
        for name in ("lt_l", "lt_r"):
            self.assertEqual(node(TARGET, name), node(SOURCE, name), name)
        for behavior in ("lt", "mt"):
            pattern = r"&" + behavior + r"\s*\{(.*?)\n};"
            self.assertEqual(re.search(pattern, TARGET, re.S)[1], re.search(pattern, SOURCE, re.S)[1])
        self.assertIn("retro-tap;", node(TARGET, "lt_l"))
        self.assertNotIn("retro-tap;", node(TARGET, "lt_r"))

    def test_trackball_modes_and_macros_are_absent(self):
        for name in ("MOUSE", "GESTURE", "DESKTOP", "TAB", "ZOOM", "DRAG",
                     "PRECISION", "HSCROLL", "SCROLL MENU"):
            self.assertNotIn(f'display-name = "{name}"', TARGET)
        for behavior in ("menu_lt", "menu_zoom", "zoom_hold", "drag_on", "drag_off",
                         "drag_cancel", "dl", "mkp"):
            self.assertNotRegex(TARGET, r"\b" + behavior + r"\s*:")
            self.assertNotRegex(TARGET, r"&" + behavior + r"\b")
        self.assertNotIn("input/processors.dtsi", TARGET)

    def test_all_layer_targets_exist(self):
        layers = layer_bindings(TARGET)
        for body in layers:
            for binding in body:
                if binding.split()[0] in ("&lt_l", "&lt_r", "&mo", "&to", "&tog"):
                    self.assertLess(int(binding.split()[1]), len(layers))
        self.assertIn("bindings = <&to 4>;", node(TARGET, "combo_bt"))

    def test_generated_file_is_current(self):
        spec = importlib.util.spec_from_file_location("adapter", ROOT / "scripts/import_kobitokey.py")
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        self.assertEqual(TARGET, adapter.generate())

    def test_unused_positions_never_perform_an_action(self):
        # These ten positions have no counterpart in the original 40-key map.
        unused = (0, 11, 12, 23, 24, 30, 31, 37, 41, 47)
        for index, layer in enumerate(layer_bindings(TARGET)):
            for position in unused:
                with self.subTest(layer=index, position=position):
                    self.assertEqual(layer[position], "&none")
        self.assertNotIn("&studio_unlock", TARGET)

    def test_no_encoder_actions_are_added(self):
        self.assertNotIn("sensor-bindings", TARGET)
        self.assertNotIn("cornix_scroll", TARGET)


if __name__ == "__main__":
    unittest.main()

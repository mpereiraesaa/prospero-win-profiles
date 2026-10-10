#!/usr/bin/env python3
"""Cases for tools/check_profiles.py. Each expected verdict is what
prospero-win's own parser returned for the same text."""
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("check_profiles", ROOT / "tools" / "check_profiles.py")
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

BASE = (ROOT / "profiles" / "pinball.profile").read_text()
PRESET = (ROOT / "input" / "pinball.input").read_text()


def accepted(parse, text):
    try:
        parse(text.encode())
        return True
    except cp.Refused:
        return False


class ProfileRules(unittest.TestCase):
    def test_goldsrc_pointer_keeps_controller(self):
        preset=(ROOT / "input" / "goldsrc.input").read_text()
        self.assertTrue(accepted(cp.parse_preset,preset))
        self.assertIn("mode = xinput",preset)
        self.assertIn("mouse = right_stick",preset)
        self.assertIn("touchpad = mouse_left",preset)
        self.assertIn("options = escape",preset)
        for game in ("half-life","counter-strike-16"):
            profile=(ROOT / "profiles" / (game+".profile")).read_text()
            self.assertTrue(accepted(cp.parse_profile,profile))
            self.assertIn("preset = goldsrc",profile)
            self.assertIn("graphics = opengl",profile)
    def test_profile_forms(self):
        edit = lambda old, new: BASE.replace(old, new)
        cases = [
            (BASE, True),
            (edit("pe32", "pe16"), False),
            (edit("id = pinball", "id = Pinball"), False),
            (edit("PINBALL.EXE", "PINBALL.COM"), False),
            (edit("C:\\Games\\Pinball\\PINBALL", "C:/Games/Pinball/PINBALL"), False),
            (edit("C:\\Games\\Pinball\\P", "C:\\Games\\..\\P"), False),
            (edit("scaling = fit", "scaling = zoom"), False),
            (edit("desktop = 800x600", "desktop = 100x100"), False),
            (edit("desktop = 800x600", "desktop = 3840x2160"), True),
            (BASE + "\n[display]\nview = window\n", False),
            (BASE + "\n[sound]\nx = 1\n", False),
            (BASE + "\n[debug]\nwinedebug = err+all,+seh\n", True),
            (BASE + "\n[debug]\nwinedebug = +seh;rm\n", False),
            (BASE + "\n[debug]\nwinedebug = +seh all\n", False),
            (BASE + "\n[debug]\nwinedebug =\n", False),
            (BASE + "\n[debug]\nrelay = on\n", False),
            (BASE + "\n[debug]\nwinedebug = +seh\nwinedebug = +relay\n", False),
            (BASE + "\n[debug]\nwinedebug = +" + "a" * 127 + "\n", False),
            (edit("preset = pinball", "preset = pinball\nmode = xinput\ncross = f24\nl1 = vk:0x41"), True),
            (edit("preset = pinball", "preset = pinball\nr1 = vk:0x00"), False),
            (edit("preset = pinball", "preset = pinball\ncross = f25"), False),
            (edit("preset = pinball", "preset = Pin"), False),
            (edit("preset = pinball", "preset = pinball\nplayer2 = pinball-p2"), True),
            (edit("preset = pinball", "preset = pinball\nplayer2 = P2"), False),
            (edit("preset = pinball", "preset = pinball\nplayer2 = a\nplayer2 = b"), False),
            (edit("graphics = gdi", "graphics = gdi\ngraphics = gdi"), False),
            (edit("graphics = gdi", "graphics = DXVK"), True),
            (edit("graphics = gdi", "graphics = OPENGL"), True),
            (edit("name = Space Cadet Pinball\n", ""), False),
            (edit("prefix = default", "prefix = default\narguments ="), True),
            (edit("prefix = default", "prefix = default\nstartup_command_id = 65536"), False),
            (edit("prefix = default", "prefix = default\nstartup_command_id = 406"), True),
            ("[display]\nscaling = fit\n" + BASE, False),
            (edit("[input]", "[input]\nmouse_speed = 0"), False),
            (edit("[input]", "[input]\nmouse_speed = 20000"), True),
            (edit("working_directory = C:\\Games\\Pinball", "working_directory = C:\\Games\\Pinball\\"), True),
            (edit("executable", "Executable"), True),
            (edit("[input]", "[input]\ntouchpad = none\ncreate = mouse_middle\nsquare = 7"), True),
            (edit("[input]", "[input]\nsquare = ab"), False),
            (edit("prefix = default", "prefix = default\ndll_overrides = d3d11,dxgi=n;d3d9=n,b"), True),
            (edit("prefix = default", "prefix = default\ndll_overrides = *d3d8.dll="), True),
            (edit("prefix = default", "prefix = default\ndll_overrides = d3d11 dxgi=n"), False),
            (edit("prefix = default", "prefix = default\ndll_overrides = C:\\x.dll=n"), False),
            (edit("prefix = default", "prefix = default\ndll_overrides ="), False),
            (edit("prefix = default", "prefix = default\ndll_overrides = a=n\ndll_overrides = b=n"), False),
            (edit("prefix = default", "prefix = default\ndll_overrides = " + "a" * 257), False),
            ("", False),
            (edit("[application]", "[application"), False),
            (edit("prefix = default", "prefix = default\nfoo"), False),
            (edit("prefix = default", "prefix = default\n = x"), False),
            (edit("C:\\Games\\Pinball\\PINBALL.EXE", "C:x.exe"), False),
            (edit("C:\\Games\\Pinball\\PINBALL", "C:\\Games\\\\PINBALL"), False),
            (edit("C:\\Games\\Pinball\\PINBALL", "C:\\Ga:mes\\PINBALL"), False),
            (edit("Space Cadet", "Space\x01Cadet"), False),
            (edit("prefix = default", "prefix = default\ncolor = red"), False),
            (edit("prefix = default", "prefix = default\nstartup_command_id = abc"), False),
            (edit("graphics = gdi", "graphics = vulkan"), False),
            ("[input]\nmode = xinput\n", False),
            ("id = x\n" + BASE, False),
            (edit("scaling = fit", "scaling = fit\ndesktop = 640x480"), False),
            (edit("scaling = fit", "scaling = fit\nzoom = 2"), False),
            (edit("scaling = fit", "scaling = fit\nview = desktop"), True),
            (edit("scaling = fit", "scaling = fit\nview = full"), False),
            (edit("scaling = fit", "scaling = fit\nshow_fps = true"), True),
            (edit("scaling = fit", "scaling = fit\nshow_fps = FALSE"), True),
            (edit("scaling = fit", "scaling = fit\nshow_fps = yes"), False),
            (edit("scaling = fit", "scaling = fit\nshow_fps ="), False),
            (edit("scaling = fit", "scaling = fit\nshow_fps = true\nshow_fps = false"), False),
            (edit("scaling = fit", "scaling = fit\nrefresh = 120"), True),
            (edit("scaling = fit", "scaling = fit\nrefresh = 90"), False),
            (edit("scaling = fit", "scaling = fit\nopengl_thread = true"), True),
            (edit("scaling = fit", "scaling = fit\nopengl_thread = yes"), False),
            (edit("scaling = fit", "scaling = fit\nopengl_thread = true\nopengl_thread = false"), False),
            (edit("preset = pinball", "preset = pinball\nmode = xinput\nmode = keyboard"), False),
            (edit("preset = pinball", "preset = pinball\nmouse = up"), False),
            (edit("preset = pinball", "preset = pinball\njump = x"), False),
            ("; " + "x" * cp.MAX_BYTES + "\n" + BASE, False),
        ]
        for text, expected in cases:
            with self.subTest(text=text[:200]):
                self.assertEqual(accepted(cp.parse_profile, text), expected)

    def test_preset_forms(self):
        cases = [
            (PRESET, True),
            (PRESET + "preset = x\n", False),
            (PRESET + "player2 = x\n", False),
            (PRESET.replace("mode = keyboard", "mode = arcade"), False),
            (PRESET + "[display]\nscaling = fit\n", False),
            (PRESET.replace("l1 = z", "l1 = z\nl1 = x"), False),
            ("[input]\n", True),
            ("mode = xinput\n", False),
            ("[input]\n[input]\n", False),
            ("[display]\nscaling = fit\n", False),
        ]
        for text, expected in cases:
            with self.subTest(text=text[:200]):
                self.assertEqual(accepted(cp.parse_preset, text), expected)

    def test_catalog(self):
        self.assertEqual(cp.parse_catalog(b"# order\r\na.profile\r\n\n ; x\n b-2.profile \t\n"),
                         ["a.profile", "b-2.profile"])
        for text in (b"a.profile\na.profile\n", b"../a.profile\n", b"A.profile\n",
                     b"".join(b"p%d.profile\n" % i for i in range(cp.CATALOG_MAX + 1))):
            with self.subTest(text=text[:40]):
                self.assertRaises(cp.Refused, cp.parse_catalog, text)


class RepositoryRules(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        shutil.copytree(ROOT / "profiles", self.root / "profiles")
        shutil.copytree(ROOT / "benchmarks" / "profiles", self.root / "benchmarks" / "profiles")
        shutil.copytree(ROOT / "input", self.root / "input")

    def test_this_repository(self):
        self.assertEqual(cp.main(ROOT), 0)

    def test_id_must_match_file_name(self):
        (self.root / "profiles" / "pinball.profile").rename(self.root / "profiles" / "flipper.profile")
        self.assertEqual(cp.main(self.root), 1)

    def test_preset_must_exist(self):
        (self.root / "input" / "pinball.input").unlink()
        self.assertEqual(cp.main(self.root), 1)

    def test_player2_preset_must_exist(self):
        profile = self.root / "profiles" / "pinball.profile"
        profile.write_text(profile.read_text().replace("preset = pinball", "preset = pinball\nplayer2 = ghost"))
        self.assertEqual(cp.main(self.root), 1)
        (self.root / "input" / "ghost.input").write_text("[input]\ncross = s\n")
        self.assertEqual(cp.main(self.root), 0)

    def test_catalog_must_list_every_profile(self):
        lst = self.root / "profiles" / "profiles.lst"
        lst.write_text(lst.read_text().replace("pinball.profile\n", ""))
        self.assertEqual(cp.main(self.root), 1)

    def test_bad_files_fail(self):
        (self.root / "input" / "notes.txt").write_text("x")
        (self.root / "input" / "broken.input").write_text("mode = xinput\n")
        (self.root / "profiles" / "Bad Name.profile").write_text(BASE)
        (self.root / "profiles" / "broken.profile").write_text("[input]\n")
        self.assertEqual(cp.main(self.root), 1)

    def test_catalog_must_exist_and_parse(self):
        lst = self.root / "profiles" / "profiles.lst"
        lst.write_text("../pinball.profile\n")
        self.assertEqual(cp.main(self.root), 1)
        lst.unlink()
        self.assertEqual(cp.main(self.root), 1)

    def test_benchmark_profiles_stay_out_of_the_catalog(self):
        self.assertFalse(list((self.root / "profiles").glob("*bench*.profile")))
        lst = self.root / "profiles" / "profiles.lst"
        self.assertNotIn("sevenzip-bench", lst.read_text())
        self.assertEqual(cp.main(self.root), 0)

    def test_benchmark_profiles_are_checked_too(self):
        (self.root / "benchmarks" / "profiles" / "pi-x87.profile").write_text("[input]\n")
        self.assertEqual(cp.main(self.root), 1)

    def test_catalog_entries_must_exist(self):
        lst = self.root / "profiles" / "profiles.lst"
        lst.write_text(lst.read_text() + "ghost.profile\n")
        self.assertEqual(cp.main(self.root), 1)


if __name__ == "__main__":
    unittest.main()

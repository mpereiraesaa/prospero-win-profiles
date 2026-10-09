#!/usr/bin/env python3
"""Checks for plugins/sa-shadow-edges, the optional San Andreas plugin.

The index is compared with the game's toggle written out in C on every run.
Where the tools are there, the plugin is also built, its entry is called as
the game calls it under Wine, and, with SA_GTA_EXE naming your gta_sa.exe
1.0, the index is compared with the game's own code."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "sa-shadow-edges"
TESTS = ROOT / "tests"


def run(*args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, text=True, **kwargs)


class ShadowEdges(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    @unittest.skipUnless(shutil.which("cc"), "no C compiler")
    def test_index_matches_the_games_toggle(self):
        exe = self.tmp / "sa_shadow_edges_test"
        run("cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(TESTS / "sa_shadow_edges_test.c"),
            str(PLUGIN / "shadow_edges.c"), "-o", str(exe))
        self.assertIn("matches the game's toggle", run(str(exe)).stdout)

    @unittest.skipUnless(shutil.which("i686-w64-mingw32-gcc"), "no i686 MinGW compiler")
    def test_plugin_builds(self):
        run(str(PLUGIN / "build.sh"), str(self.tmp))
        asi = (self.tmp / "ShadowEdgeIndex.asi").read_bytes()
        self.assertEqual(asi[:2], b"MZ")
        # It needs nothing a prefix lacks.
        imports = run("i686-w64-mingw32-objdump", "-p", str(self.tmp / "ShadowEdgeIndex.asi")).stdout
        names = {line.split()[-1].lower() for line in imports.splitlines() if "DLL Name:" in line}
        self.assertEqual(names, {"kernel32.dll", "msvcrt.dll"})

    @unittest.skipUnless(shutil.which("i686-w64-mingw32-gcc") and shutil.which("wine"), "no MinGW or Wine")
    def test_entry_as_the_game_calls_it(self):
        exe = self.tmp / "thunk.exe"
        run("i686-w64-mingw32-gcc", "-std=gnu11", "-O2", "-Wall", "-Wextra", "-Werror", "-static-libgcc",
            "-o", str(exe), str(TESTS / "sa_shadow_edges_thunk.c"), str(PLUGIN / "plugin.c"),
            str(PLUGIN / "shadow_edges.c"))
        env = dict(os.environ, WINEDEBUG="-all", WINEPREFIX=str(self.tmp / "prefix"))
        result = subprocess.run(["wine", str(exe)], capture_output=True, text=True, env=env, timeout=300)
        self.assertIn("registers as the game expects", result.stdout, result.stdout + result.stderr)

    @unittest.skipUnless(os.environ.get("SA_GTA_EXE"), "SA_GTA_EXE does not name gta_sa.exe 1.0")
    def test_index_matches_the_games_code(self):
        exe = self.tmp / "oracle"
        run("gcc", "-m32", "-std=gnu11", "-O2", "-Wall", "-Wextra", "-Werror",
            str(TESTS / "sa_shadow_edges_oracle.c"), str(PLUGIN / "shadow_edges.c"), "-o", str(exe))
        self.assertIn("match the game's code", run(str(exe), os.environ["SA_GTA_EXE"]).stdout)


if __name__ == "__main__":
    unittest.main()

# ShadowEdgeIndex: faster stencil shadows for GTA San Andreas 1.0

An optional plugin for the `gta-san-andreas` profile. It makes the game's
realtime shadows cheaper to build without changing what is drawn.

San Andreas draws the shadows of cars, bikes and people as stencil shadow
volumes. To find a volume's outline it toggles every edge of every triangle
that faces the light in a list: an edge already in the list is removed, a new
one is added at the end. The game finds the edge by reading the whole list
each time, so a shadow with a few hundred edges costs tens of thousands of
comparisons, every frame. In PS5 profiles of Grove Street and the roads
around it, this one function took 4–13% of the time the main thread spent in
the game's code.

The plugin replaces that function (at `0x70FA70` in the 1.0 executable) with
the same toggle backed by a hash index from edge to position. It produces the
same list, entry for entry, as the game's code. The tests check this against
a C copy of the game's toggle and, if you point them at your `gta_sa.exe`,
against the game's own machine code. If the executable is not 1.0, or another
mod has already changed that function, the plugin leaves the game alone.

## Build and install

```sh
plugins/sa-shadow-edges/build.sh out     # needs i686-w64-mingw32-gcc
```

Copy `out/ShadowEdgeIndex.asi` into the game's `scripts` folder, next to the
other plugins. The Ultimate ASI Loader that the profile's recipe installs
loads it. To remove it, delete the file.

## Tests

```sh
python3 -m unittest -v tests/test_sa_shadow_edges.py
SA_GTA_EXE=/path/to/gta_sa.exe python3 -m unittest -v tests/test_sa_shadow_edges.py
```

The second form also runs the comparison against the game's code. It reads
the function from your copy at run time; none of the game's code is in this
repository.

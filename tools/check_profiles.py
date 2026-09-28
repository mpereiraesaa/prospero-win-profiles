#!/usr/bin/env python3
"""Checks the profiles, input presets and profiles.lst the way the title reads them.

The rules follow prospero-win's parsers (src/pw_app_profile.c,
src/pw_game_profile.c, src/pw_profile_catalog.c): a file the title would
refuse fails here. It also checks what only this repository promises: each
profile's id is its file name, its preset exists, and profiles.lst lists
every profile.

    tools/check_profiles.py [repository root]
"""
import re
import sys
from pathlib import Path

MAX_BYTES = 8192
CATALOG_MAX = 16
NAME_MAX = 64            # profile file names, including ".profile"
ID_CAP, NAME_CAP, PATH_CAP, ARGS_CAP = 65, 97, 260, 513
BUTTONS = ("cross circle square triangle l1 r1 l2 r2 l3 r3 up down left right "
           "options create touchpad").split()
KEYS = set(("space enter escape tab backspace shift ctrl alt pause pageup pagedown end home "
            "left up right down insert delete semicolon equals comma minus period slash "
            "backquote lbracket backslash rbracket quote").split())
IDENT = re.compile(r"[a-z0-9][a-z0-9_-]*\Z")
FILE_NAME = re.compile(r"[a-z0-9_-]+\.profile\Z")


class Refused(Exception):
    pass


def lines(data):
    """(section or None, key, value) for each meaningful line, as the title splits them."""
    for raw in re.split(rb"[\r\n]+", data):
        line = raw.strip(b" \t")
        if not line or line[:1] in (b";", b"#"):
            continue
        text = line.decode("latin-1")
        if text.startswith("["):
            if len(text) < 3 or not text.endswith("]"):
                raise Refused(f"bad section line {text!r}")
            yield text[1:-1].lower(), None, None
            continue
        if "=" not in text:
            raise Refused(f"line without '=': {text!r}")
        key, value = text.split("=", 1)
        key, value = key.strip(" \t"), value.strip(" \t")
        if not key:
            raise Refused(f"line without a key: {text!r}")
        yield None, key.lower(), value


def windows_path(path):
    if len(path) < 3 or not path[0].isascii() or not path[0].isalpha() or path[1:3] != ":\\":
        return False
    segments = path[3:].split("\\")
    for i, segment in enumerate(segments):
        if "/" in segment or ":" in segment or any(ord(c) < 0x20 for c in segment):
            return False
        if segment == "" and i != len(segments) - 1:
            return False
        if segment == "..":
            return False
    return True


def text_value(key, value, capacity, allow_empty=False):
    if (not value and not allow_empty) or len(value.encode("latin-1")) >= capacity:
        raise Refused(f"{key}: empty or too long")
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in value):
        raise Refused(f"{key}: control character")
    return value


def application(fields, key, value):
    if key in fields:
        raise Refused(f"duplicate {key}")
    caps = {"id": ID_CAP, "name": NAME_CAP, "executable": PATH_CAP, "working_directory": PATH_CAP,
            "prefix": ID_CAP, "runtime": ID_CAP}
    if key in caps:
        fields[key] = text_value(key, value, caps[key])
    elif key == "arguments":
        fields[key] = text_value(key, value, ARGS_CAP, allow_empty=True)
    elif key == "startup_command_id":
        if not value.isdigit() or not value.isascii() or int(value) > 0xFFFF:
            raise Refused("startup_command_id: not a number up to 65535")
        fields[key] = value
    elif key == "architecture":
        if value.lower() not in ("pe32", "pe64"):
            raise Refused(f"architecture {value!r}")
        fields[key] = value.lower()
    elif key == "graphics":
        if value.lower() not in ("auto", "gdi", "dxvk"):
            raise Refused(f"graphics {value!r}")
        fields[key] = value.lower()
    else:
        raise Refused(f"unknown [application] key {key!r}")


def binding(button, value):
    v = value.lower()
    if v in ("none", "mouse_left", "mouse_right", "mouse_middle") or v in KEYS:
        return
    if len(v) == 1 and (v.isascii() and v.isalnum()):
        return
    if re.fullmatch(r"f[0-9]{1,2}", v) and 1 <= int(v[1:]) <= 24:
        return
    if re.fullmatch(r"vk:0x[0-9a-f]{2}", v) and int(v[5:], 16):
        return
    raise Refused(f"{button} = {value!r}: not a key, mouse button or none")


def input_line(seen, key, value, allow_preset):
    if key in seen:
        raise Refused(f"duplicate {key}")
    seen.add(key)
    if key == "preset":
        if not allow_preset:
            raise Refused("preset inside a preset file")
        if not value or len(value) >= ID_CAP or not re.fullmatch(r"[a-z0-9_-]+", value):
            raise Refused(f"preset {value!r}")
    elif key == "mode":
        if value.lower() not in ("keyboard", "xinput"):
            raise Refused(f"mode {value!r}")
    elif key == "mouse":
        if value.lower() not in ("none", "left_stick", "right_stick"):
            raise Refused(f"mouse {value!r}")
    elif key == "mouse_speed":
        if not re.fullmatch(r"[0-9]{1,9}", value) or not 1 <= int(value) <= 20000:
            raise Refused(f"mouse_speed {value!r}")
    elif key in BUTTONS:
        binding(key, value)
    else:
        raise Refused(f"unknown [input] key {key!r}")


def display_line(seen, key, value):
    if key in seen:
        raise Refused(f"duplicate {key}")
    seen.add(key)
    if key == "desktop":
        m = re.fullmatch(r"([0-9]{1,9})x([0-9]{1,9})", value)
        if not m or not (320 <= int(m[1]) <= 3840 and 200 <= int(m[2]) <= 2160):
            raise Refused(f"desktop {value!r}")
    elif key == "scaling":
        if value.lower() not in ("fit", "integer", "stretch"):
            raise Refused(f"scaling {value!r}")
    elif key == "view":
        if value.lower() not in ("window", "desktop"):
            raise Refused(f"view {value!r}")
    else:
        raise Refused(f"unknown [display] key {key!r}")


def check_size(data):
    if not data:
        raise Refused("empty file")
    if len(data) > MAX_BYTES:
        raise Refused(f"larger than {MAX_BYTES} bytes")


def parse_profile(data):
    """The profile's [application] fields and its preset name ('' if none)."""
    check_size(data)
    section, sections, fields, seen_display, seen_input = None, [], {}, set(), set()
    for name, key, value in lines(data):
        if key is None:
            if name not in ("application", "display", "input") or name in sections:
                raise Refused(f"section [{name}] unknown or repeated")
            if (not sections) != (name == "application"):
                raise Refused("[application] must come first")
            sections.append(name)
            section = name
        elif section is None:
            raise Refused("line before any section")
        elif section == "application":
            application(fields, key, value)
        elif section == "display":
            display_line(seen_display, key, value)
        else:
            input_line(seen_input, key, value, allow_preset=True)
    if "application" not in sections:
        raise Refused("no [application] section")
    missing = {"id", "name", "executable", "working_directory", "prefix", "runtime",
               "architecture", "graphics"} - fields.keys()
    if missing:
        raise Refused(f"missing {', '.join(sorted(missing))}")
    for key in ("id", "prefix", "runtime"):
        if not IDENT.match(fields[key]):
            raise Refused(f"{key} {fields[key]!r} is not a lowercase identifier")
    for key in ("executable", "working_directory"):
        if not windows_path(fields[key]):
            raise Refused(f"{key} {fields[key]!r} is not an absolute Windows path")
    if not fields["executable"].lower().endswith(".exe"):
        raise Refused("executable does not end in .exe")
    preset = ""
    for raw in re.split(rb"[\r\n]+", data):
        m = re.fullmatch(rb"[ \t]*preset[ \t]*=[ \t]*([^ \t]*)[ \t]*", raw, re.I)
        if m:
            preset = m[1].decode()
    return fields, preset


def parse_preset(data):
    check_size(data)
    sections, seen = [], set()
    for name, key, value in lines(data):
        if key is None:
            if name != "input" or sections:
                raise Refused("a preset holds one [input] section")
            sections.append(name)
        elif not sections:
            raise Refused("line before [input]")
        else:
            input_line(seen, key, value, allow_preset=False)
    if not sections:
        raise Refused("no [input] section")


def parse_catalog(data):
    names = []
    for raw in data.split(b"\n"):
        line = raw.strip(b" \t").rstrip(b" \t\r").decode("latin-1")
        if not line or line[0] in "#;":
            continue
        if len(line) >= NAME_MAX or not FILE_NAME.match(line):
            raise Refused(f"bad entry {line!r}")
        if line in names:
            raise Refused(f"duplicate entry {line!r}")
        names.append(line)
        if len(names) > CATALOG_MAX:
            raise Refused(f"more than {CATALOG_MAX} entries")
    return names


def main(root):
    root = Path(root)
    errors = []

    def fail(path, message):
        errors.append(f"{path.relative_to(root)}: {message}")

    presets = {}
    for path in sorted((root / "input").glob("*")):
        try:
            if path.suffix != ".input":
                raise Refused("not an .input file")
            parse_preset(path.read_bytes())
            presets[path.stem] = path
        except Refused as error:
            fail(path, error)

    profiles = {}
    for path in sorted((root / "profiles").glob("*")):
        if path.name == "profiles.lst":
            continue
        try:
            if path.suffix != ".profile" or len(path.name) >= NAME_MAX or not FILE_NAME.match(path.name):
                raise Refused("file name must be <lowercase id>.profile")
            fields, preset = parse_profile(path.read_bytes())
            if fields["id"] != path.stem:
                raise Refused(f"id {fields['id']!r} differs from the file name")
            if preset and preset not in presets:
                raise Refused(f"preset {preset!r} has no input/{preset}.input")
            profiles[path.name] = fields
        except Refused as error:
            fail(path, error)

    catalog = root / "profiles" / "profiles.lst"
    try:
        names = parse_catalog(catalog.read_bytes())
        for name in names:
            if not (root / "profiles" / name).is_file():
                fail(catalog, f"lists {name}, which does not exist")
        for name in sorted(set(profiles) - set(names)):
            fail(catalog, f"does not list {name}")
    except FileNotFoundError:
        fail(catalog, "missing")
    except Refused as error:
        fail(catalog, error)

    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print(f"profiles ok: {len(profiles)} profiles, {len(presets)} presets, profiles.lst complete")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent))

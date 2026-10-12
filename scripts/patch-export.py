#!/usr/bin/env python3

import pathlib
import re
import sys


def main() -> None:
    export_path = pathlib.Path(sys.argv[1])
    script_path = export_path.with_suffix(".js")
    source = script_path.read_text()
    source, count = re.subn(r"^DOTNET\.setup\([^\n]+\);;\n", "", source, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"Expected one .NET JS host setup call in {script_path}, found {count}")
    script_path.write_text(source)


if __name__ == "__main__":
    main()

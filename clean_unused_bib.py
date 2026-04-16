"""
Remove unused bibliography entries from a .bib file.

Prerequisites:
- A TeX distribution providing `pdflatex` and `texlua` on PATH
  (e.g., MacTeX: `brew install mactex`)
- `checkcites.lua` available on PATH or alongside this script
  (from https://github.com/luffy-yu/checkcites.git)
- Python 3.8+ with `bibtexparser` pre-release: `pip install bibtexparser --pre`

Usage:
    python clean_unused_bib.py --tex input.tex --bib refs.bib
    python clean_unused_bib.py --tex input.tex --bib refs.bib --overwrite

Outputs (next to the .tex file, using the tex basename):
    <texbase>-unused.json   list of unused citation keys from checkcites
    <texbase>-clean.bib     cleaned bibliography (unless --overwrite is set,
                            in which case the input .bib is overwritten)
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import bibtexparser


def run(cmd, cwd=None, check=True):
    print(f"$ {' '.join(str(c) for c in cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=cwd)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result.returncode


def find_checkcites():
    found = shutil.which("checkcites.lua")
    if found:
        return [found]
    local = Path(__file__).parent / "checkcites.lua"
    if local.exists():
        texlua = shutil.which("texlua")
        if not texlua:
            sys.exit("texlua not found on PATH; install a TeX distribution.")
        return [texlua, str(local)]
    sys.exit("checkcites.lua not found on PATH or next to this script.")


def main():
    parser = argparse.ArgumentParser(
        description="Remove unused bibliography entries from a .bib file."
    )
    parser.add_argument("--tex", required=True, help="Path to the .tex file.")
    parser.add_argument("--bib", required=True, help="Path to the .bib file.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the input .bib file instead of writing <texbase>-clean.bib.",
    )
    parser.add_argument(
        "--aux",
        help="Path to an existing .aux file to use. If given, pdflatex is skipped.",
    )
    parser.add_argument(
        "--skip-pdflatex",
        action="store_true",
        help="Skip pdflatex and use the existing <texbase>.aux file.",
    )
    args = parser.parse_args()

    tex_path = Path(args.tex).resolve()
    bib_path = Path(args.bib).resolve()
    if not tex_path.is_file():
        sys.exit(f"tex file not found: {tex_path}")
    if not bib_path.is_file():
        sys.exit(f"bib file not found: {bib_path}")

    tex_dir = tex_path.parent
    tex_base = tex_path.stem
    aux_path = Path(args.aux).resolve() if args.aux else tex_dir / f"{tex_base}.aux"
    json_path = tex_dir / f"{tex_base}-unused.json"
    clean_bib_path = bib_path if args.overwrite else tex_dir / f"{tex_base}-clean.bib"

    skip_pdflatex = args.skip_pdflatex or args.aux is not None or aux_path.is_file()
    if skip_pdflatex:
        print(f"Skipping pdflatex; using existing aux: {aux_path}", flush=True)
    else:
        run(["pdflatex", "-interaction=nonstopmode", tex_path.name], cwd=tex_dir)
    if not aux_path.is_file():
        sys.exit(
            f"aux file not available: {aux_path}\n"
            "Compile the document first, or pass --aux <path> to point at an existing .aux."
        )

    aux_dir = aux_path.parent
    run(
        find_checkcites() + ["-u", aux_path.name, "-j", str(json_path)],
        cwd=aux_dir,
        check=False,
    )
    if not json_path.is_file():
        sys.exit(f"unused json not produced: {json_path}")

    data = json.loads(json_path.read_text(encoding="utf-8"))
    unused = set(data["results"]["unused"]["occurrences"])

    bib_text = bib_path.read_text(encoding="utf-8")
    v2 = hasattr(bibtexparser, "parse_string") and hasattr(bibtexparser, "write_string")
    if v2:
        from bibtexparser.model import Entry, String, Preamble

        library = bibtexparser.parse_string(bib_text)
        toremove = [e for e in library.entries if e.key in unused]
        library.remove(toremove)
        keep = [b for b in library.blocks if isinstance(b, (Entry, String, Preamble))]
        library.remove([b for b in library.blocks if b not in keep])
        out_text = bibtexparser.write_string(library)
        remaining = len(library.entries)
    else:
        parser = bibtexparser.bparser.BibTexParser(common_strings=True)
        parser.ignore_nonstandard_types = False
        db = bibtexparser.loads(bib_text, parser=parser)
        before = len(db.entries)
        db.entries = [e for e in db.entries if e.get("ID") not in unused]
        toremove = [None] * (before - len(db.entries))
        db.comments = []
        out_text = bibtexparser.dumps(db)
        remaining = len(db.entries)

    clean_bib_path.write_text(out_text, encoding="utf-8")
    print(f"Removed {len(toremove)} unused entries; {remaining} remain.")
    print(f"Unused keys: {json_path}")
    print(f"Cleaned bib: {clean_bib_path}")


if __name__ == "__main__":
    main()

# `checkcites.lua`

## About

`checkcites` is a Lua script written for the sole purpose of detecting
unused or undefined references from both LaTeX auxiliary or bibliography
files. We use the term *unused reference* to refer to the reference
present the bibliography file - with the `.bib` extension - but not
cited in the `.tex` file. The term *undefined reference* is exactly the
opposite, i.e, the item cited in the `.tex` file, but not present in the
`.bib` file.

The original idea came from a question posted in the TeX community at
Stack Exchange about how to check which bibliography entries were not
used. We decided to write a script to check references. We opted for
Lua, since it's a very straightforward language and it has an
interpreter available on every modern TeX distribution.

## Usage

The script is pretty simple to use. The only requirement is a recent
TeX distribution, such as TeX Live.

`checkcites` uses the generated auxiliary files to start the analysis.
From version 2.0 on, the scripts supports two backends:

### `bibtex`

Default behavior, the script checks `.aux` files looking for citations,
in the form of `\citation{a}`. For every `\citation` line found, `checkcites`
will extract the citations and add them to a table, even for multiple
citations separated by commas, like `\citation{a,b,c}`. The citation
table contains no duplicate values. At the same time checkcites also
looks for bibliography data, in the form of `\bibdata{a}`. Similarly,
for every `\bibdata` line found, the script will extract the bibliography
data and add them to a table, even if they are separated by commas, like
`\bibdata{d,e,f}`. Again, no duplicate values are allowed. Stick with this
backend if you are using BibTeX or BibLaTeX with the `backend=bibtex`
package option.

### `biber`

With this backend, the script checks `.bcf` files (which are XML-based)
looking for citations, in the form of `bcf:citekey` tags. For every tag
found, `checkcites` will extract the corresponding values and add them to
a table. The citation table contains no duplicate values. At the same
time `checkcites` also looks for bibliography data, in the form of
`bcf:datasource` tags. Similarly, for every tag found, the script will
extract the bibliography data and add them to a table. Again, no duplicate
values are allowed. Stick with this backend if you are using BibLaTeX with
the default options or with the `backend=biber` option explicitly set.
It is important to note, however, that the `glob=true` option is not
supported yet.

### Command line

Open a terminal and run `checkcites`:

```bash
$ checkcites
```

When you run `checkcites` without providing any argument to it, the a message
error will appear. Do not panic! Try again with the `--help` flag:

```bash
$ checkcites --help
```

If you are using BibTeX, simply provide the auxiliary file - the one with
the `.aux` extension - which is generated when you compile your main `.tex`
file. For example, if your main document is named `foo.tex`, you probably
have a `foo.aux` file too. Then simply invoke

```bash
$ checkcites foo.aux
```

`checkcites` allows an additional argument that will tell it how to
behave. For example

```bash
$ checkcites --unused foo.aux
```

will make the script only look for unused references in your `.bib`
file. The argument order doesn't matter, you can also run

```bash
$ checkcites foo.aux --unused
```

and get the same behaviour. Similarly, you can use

```bash
$ checkcites --undefined foo.aux
```

to make the script only look for undefined references in your
`.tex` file. If you want `checkcites` to look for both unused and
undefined references, go with

```bash
$ checkcites --all foo.aux
```

If no special argument is provided, `--all` is set as default.

If you are using BibLaTeX, we need to inspect `.bcf` files instead. For
example, if your main document is named `foo.tex`, you probably have a
`foo.bcf` file too. Then invoke

```bash
$ checkcites foo.aux --backend biber
```

Note the `--backend` flag used for BibLaTeX support. We can even omit the
file extension, the script will automatically assign one based on the
current backend.

## `clean_unused_bib.py`

A small Python helper that drives `pdflatex` and `checkcites.lua` for you,
then removes the unused entries from your `.bib` file.

### Requirements

- A TeX distribution on `PATH` that provides `pdflatex` and `texlua`
  (TeX Live, MiKTeX, or MacTeX).
- `checkcites.lua` either on `PATH` or next to the script.
- Python 3.8+ with `bibtexparser`. Either the stable v1 (`pip install bibtexparser`)
  or the v2 pre-release (`pip install bibtexparser --pre`) works; the script
  detects which is installed.

### Usage

```bash
python clean_unused_bib.py --tex input.tex --bib refs.bib
```

Arguments:

- `--tex` — path to the main `.tex` file.
- `--bib` — path to the `.bib` file to clean.
- `--overwrite` — optional flag. When set, the input `.bib` is overwritten
  in place. Otherwise (default), a new `<texbase>-clean.bib` is written.

### What it does

1. Runs `pdflatex -interaction=nonstopmode <tex>` in the tex file's directory
   to (re)generate the `.aux` file.
2. Runs `checkcites.lua -u <texbase>.aux -j <texbase>-unused.json` from the
   same directory so bib lookup via `kpse` works.
3. Parses `<texbase>-unused.json` and removes those citation keys from the
   bib, writing the result to either `<texbase>-clean.bib` or — with
   `--overwrite` — back to the input `.bib`.

### Outputs

Written next to the `.tex` file, using the tex basename:

- `<texbase>-unused.json` — the list of unused citation keys from `checkcites`.
- `<texbase>-clean.bib` — the cleaned bibliography (omitted when `--overwrite`
  is used; the input `.bib` is rewritten instead).

### Example

```bash
$ python clean_unused_bib.py --tex main.tex --bib main.bib
...
Removed 5 unused entries; 46 remain.
Unused keys: .../main-unused.json
Cleaned bib: .../main-clean.bib
```

Note: `checkcites.lua` exits with a non-zero status when it finds unused
references. The helper script treats that as a normal result (not an error)
and proceeds as long as the JSON report was produced.

## License

This script is licensed under the LaTeX Project Public License.
If you want to support LaTeX development by a donation, the best
way to do this is donating to the TeX Users Group.

## The team

checkcites is brought to you by the Island of TeX. If you want to support TeX
development by a donation, the best way to do this is donating to the
[TeX Users Group](https://www.tug.org/donate.html).

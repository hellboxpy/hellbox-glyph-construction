# hellbox-glyph-construction

A hellbox job that applies a `.glyphConstruction` file to a UFO source.

## Usage

```python
from hellbox import Hellbox
from hellbox.jobs.glyph_construction import GlyphConstruction

with Hellbox("build") as task:
    task.read("source/*.ufo") \
        >> GlyphConstruction("MyFont.glyphConstruction") \
        >> task.write("./build/ufo")
```

## Installation

```sh
hell add hellbox-glyph-construction
```

## Development

```sh
uv sync
uv run pytest
```

### Updating the vendored glyphConstruction library

```sh
git submodule update --remote vendor/GlyphConstruction
cp vendor/GlyphConstruction/Lib/glyphConstruction.py \
    src/hellbox/jobs/glyph_construction/_vendor/glyphConstruction.py
git add vendor src/hellbox/jobs/glyph_construction/_vendor/glyphConstruction.py
git commit -m "vendor: update glyphConstruction to <version>"
```

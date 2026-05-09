from contextvars import ContextVar
from pathlib import Path

import ufoLib2

from hellbox import Hellbox
from hellbox.chutes.chute import Chute
from hellbox.source_file import SourceFile
from hellbox.jobs.glyph_construction._vendor.glyphConstruction import (
    GlyphConstructionBuilder,
    ParseGlyphConstructionListFromString,
)

# Holds the default layer of the font currently being processed so the
# bounds property patch below can forward it to getBounds().
_current_layer: ContextVar = ContextVar("_current_layer", default=None)

# The vendored glyphConstruction.py accesses glyph.bounds as a property, which
# is the defcon/robofab API. ufoLib2 exposes this as getBounds(layer=None).
# Patch the property onto the ufoLib2 Glyph class to ensure we use our layer-aware
# version. Glyphs that contain components require the layer to resolve them; we read
# the layer from the context variable set during processing.
def _bounds(self):
    return self.getBounds(_current_layer.get())

ufoLib2.objects.glyph.Glyph.bounds = property(_bounds)


class GlyphConstruction(Chute):
    def __init__(self, construction_file: str) -> None:
        self.construction_file = Path(construction_file)

    def process(self, file: SourceFile) -> SourceFile:
        Hellbox.info(f"Applying glyph construction: {file.name}")
        copy = file.copy()

        font = ufoLib2.Font.open(copy.content_path)
        token = _current_layer.set(font.layers.defaultLayer)
        try:
            with open(self.construction_file) as f:
                constructions = ParseGlyphConstructionListFromString(f, font)

            for construction in constructions:
                if not construction:
                    continue
                built = GlyphConstructionBuilder(construction, font)
                if built.name in font:
                    glyph = font[built.name]
                    glyph.clear()
                else:
                    glyph = font.newGlyph(built.name)
                built.drawPoints(glyph.getPointPen())
                glyph.width = built.width
                glyph.unicodes = built.unicodes
        finally:
            _current_layer.reset(token)

        font.save(copy.content_path, overwrite=True)
        return copy

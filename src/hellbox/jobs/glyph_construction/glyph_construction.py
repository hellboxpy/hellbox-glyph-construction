from pathlib import Path

import ufoLib2

from hellbox import Hellbox
from hellbox.chutes.chute import Chute
from hellbox.source_file import SourceFile
from hellbox.jobs.glyph_construction._vendor.glyphConstruction import (
    GlyphConstructionBuilder,
    ParseGlyphConstructionListFromString,
)

# The vendored glyphConstruction.py accesses glyph.bounds as a property, which
# is the defcon/robofab API. ufoLib2 exposes this as getBounds(layer=None).
# Patch the property onto the ufoLib2 Glyph class if it's not already present.
if not hasattr(ufoLib2.objects.glyph.Glyph, "bounds"):
    ufoLib2.objects.glyph.Glyph.bounds = property(
        lambda self: tuple(self.getBounds()) if self.getBounds() is not None else None
    )


class GlyphConstruction(Chute):
    def __init__(self, construction_file: str) -> None:
        self.construction_file = Path(construction_file)

    def process(self, file: SourceFile) -> SourceFile:
        Hellbox.info(f"Applying glyph construction: {file.name}")
        copy = file.copy()

        font = ufoLib2.Font.open(copy.content_path)

        with open(self.construction_file) as f:
            constructions = ParseGlyphConstructionListFromString(f, font)

        for construction in constructions:
            built = GlyphConstructionBuilder(construction, font)
            if built.name in font:
                glyph = font[built.name]
                glyph.clear()
            else:
                glyph = font.newGlyph(built.name)
            built.drawPoints(glyph.getPointPen())
            glyph.width = built.width
            glyph.unicodes = built.unicodes

        font.save(copy.content_path, overwrite=True)
        return copy

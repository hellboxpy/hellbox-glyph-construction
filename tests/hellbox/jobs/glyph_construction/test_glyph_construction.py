from pathlib import Path

import pytest
import ufoLib2

from hellbox.source_file import SourceFile
from hellbox.jobs.glyph_construction import GlyphConstruction


@pytest.fixture
def test_ufo(tmp_path):
    font = ufoLib2.Font()

    a = font.newGlyph("a")
    a.width = 500
    pen = a.getPen()
    pen.moveTo((0, 0))
    pen.lineTo((500, 0))
    pen.lineTo((500, 700))
    pen.lineTo((0, 700))
    pen.closePath()

    acute = font.newGlyph("acute")
    acute.width = 0
    pen = acute.getPen()
    pen.moveTo((200, 750))
    pen.lineTo((300, 900))
    pen.lineTo((100, 900))
    pen.closePath()

    ufo_path = tmp_path / "Test.ufo"
    font.save(ufo_path)
    return ufo_path


class TestGlyphConstruction:
    def test_init(self):
        chute = GlyphConstruction("test.glyphConstruction")
        assert chute.construction_file == Path("test.glyphConstruction")

    def test_process_builds_composites(self, test_ufo, tmp_path):
        construction_file = tmp_path / "test.glyphConstruction"
        construction_file.write_text("aacute = a + acute@top\n")

        source = SourceFile(test_ufo, test_ufo, tmp_path)
        result = GlyphConstruction(str(construction_file)).process(source)

        font = ufoLib2.Font.open(result.content_path)
        assert "aacute" in font
        assert len(font["aacute"].components) == 2
        base_glyphs = {c.baseGlyph for c in font["aacute"].components}
        assert base_glyphs == {"a", "acute"}

    def test_process_handles_blank_lines_in_construction_file(self, test_ufo, tmp_path):
        construction_file = tmp_path / "test.glyphConstruction"
        construction_file.write_text("aacute = a + acute@top\n\nacute2 = acute\n")

        source = SourceFile(test_ufo, test_ufo, tmp_path)
        result = GlyphConstruction(str(construction_file)).process(source)

        font = ufoLib2.Font.open(result.content_path)
        assert "aacute" in font
        assert "acute2" in font

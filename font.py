# Raylib doesn't support rendering TTF fonts without anti-aliasing, which ruins 
# my vibe! I ported this workaround from C. Let's "C" if it works. Hawhawhaw.
# https://github.com/raysan5/raylib/issues/5385

# I got lots of FFI code for function calls from openpilot. It's a lot easier
# to use raylib in C than Python for weird stuff apparently!
# https://github.com/commaai/openpilot/blob/master/selfdrive/assets/fonts/process.py

# I really wanted to load a non-anti-aliased version of MS Gothic. It's by far
# my favorite font but certain complications make it really really annoying to
# load here:
# - It's not an English font! The font itself is Japanese and the characters I'm
#   in love with are manually-drawn English fallback characters. This also
#   messes with with glyph spacing... etc.
# - RayLib really, really, REALLY does not want you loading non-anti-aliased
#   fonts.
# - I don't want to write Python reimplementations of C code in FFI hell 
#   anymore. I've spent 4 hours trying to load the font and I am TIRED!!

from typing import Any
import pyray as rl

CHARS = "abcdefghijklmnopqrstuvwxyz"
CHARS += CHARS.upper()
CHARS += "01234567890"
CHARS += "!@#$%^&*()_+-=`~,.<>;':\"/?[]{}\\|"
CODEPOINTS = tuple(ord(c) for c in CHARS)

def load_jagged_ttf(file_name: str, font_size: int):
    with open(file_name, "rb") as file:
        data = file.read()

    font = rl.Font()
    font.baseSize = font_size
    font.glyphPadding = 4
    font.glyphCount = len(CODEPOINTS)

    file_buf = rl.ffi.new("unsigned char[]", data)
    codepoint_buf = rl.ffi.new("int[]", CODEPOINTS)
    codepoint_ptr = rl.ffi.cast("int *", codepoint_buf)

    font.glyphs = rl.load_font_data(
        rl.ffi.cast("unsigned char *", file_buf),
        len(data),
        font_size,
        codepoint_ptr,
        font.glyphCount,
        rl.FONT_DEFAULT
    )

    assert font.glyphs != rl.ffi.NULL

    rects_ptr = rl.ffi.new("Rectangle **")
    image = rl.gen_image_font_atlas(
        font.glyphs,
        rects_ptr,
        len(CODEPOINTS),
        font_size,
        font.glyphPadding,
        0
    )

    # TODO: Edit texture to do manual flooring so it's not weird and wide

    font.recs = rects_ptr[0]
    font.texture = rl.load_texture_from_image(image);
    rl.set_texture_filter(font.texture, rl.TEXTURE_FILTER_POINT)

    for i in range(font.glyphCount):
        rl.unload_image(font.glyphs[i].image)
        font.glyphs[i].image = rl.image_from_image(image, font.recs[i]);

    rl.unload_image(image);

    return font

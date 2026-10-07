"""Shared theme + layout helpers for the M2-P1 'Seeing Shapes' deck.

Design tokens and geometry are lifted directly from the reference deck
Slides/myCobot_08.pptx (a Google Slides export) so the new deck is visually
indistinguishable from it.
"""

import functools
import math

from PIL import ImageFont

from pptx.util import Cm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE

# ---------------------------------------------------------------- palette ---
BG      = RGBColor(0x2E, 0x33, 0x8C)   # slide background (deep indigo)
PANEL   = RGBColor(0x3B, 0x41, 0xA0)   # callout / code panel
PANEL2  = RGBColor(0x38, 0x3E, 0x96)   # oversized numeral
ROW     = RGBColor(0x57, 0x5B, 0xA4)   # table body
PALE    = RGBColor(0xB5, 0xB3, 0xE5)   # table gridlines
YELLOW  = RGBColor(0xFF, 0xCF, 0x08)   # accent
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)

# ------------------------------------------------------------------ fonts ---
F_TITLE = 'Bungee'
F_BODY  = 'Avenir'
F_EMPH  = 'Google Sans'
F_CODE  = 'Courier New'

# ------------------------------------------------- reference geometry (cm) ---
X_L, X_BULLET, X_ITEM = 1.91, 2.06, 3.48
W_BODY, W_WIDE, W_ITEM = 20.95, 24.13, 22.55
Y_TITLE_STD, H_TITLE_STD = 1.91, 1.21      # concept / step slides
Y_TITLE_EXT, H_TITLE_EXT = 1.47, 1.57      # extension + wrap slides
Y_BODY_STD, Y_BODY_EXT = 3.75, 3.71
SLIDE_H = 21.59                           # reference slide height
Y_BOTTOM = SLIDE_H - 0.4                  # keep text boxes inside the slide

SZ_TITLE, SZ_DIVIDER = 28.27, 44.0
SZ_BODY, SZ_SMALL, SZ_TINY, SZ_CMD = 20.27, 15.0, 16.5, 20.0
SZ_CODE, SZ_NUMBER = 16.0, 13.0

# ------------------------------------------------------- text measurement ---
# Courier New is installed, so code measurements are exact.  The sans faces
# are not necessarily present, so Verdana stands in for width: it is wider
# than Avenir or Google Sans, which makes every wrap estimate conservative.
CM_PER_PT = 2.54 / 72.0
_COURIER_ASPECT = (1705 + 615) / 2048   # winAscent+winDescent / unitsPerEm
_SANS_ASPECT = 1.20
_FONTS = {}


def _pil(size, code, bold=False):
    key = (round(size, 1), code, bold)
    if key not in _FONTS:
        name = ('courbd.ttf' if bold else 'cour.ttf') if code else \
               ('verdanab.ttf' if bold else 'verdana.ttf')
        _FONTS[key] = ImageFont.truetype(r'C:\Windows\Fonts\\' + name,
                                         max(1, int(round(size))))
    return _FONTS[key]


def _chunks(chunks):
    """[(text, face, size, bold), ...] for a paragraph's chunk list."""
    out = []
    for chunk in chunks:
        text, style = (chunk, None) if isinstance(chunk, str) else chunk
        out.append((text, style))
    return out


def para_height(chunks, size, w_cm, ls=1.0, base_font=F_BODY, bold=False):
    """Rendered height in cm of one paragraph of `chunks` in a `w_cm` box."""
    if isinstance(chunks, str):
        chunks = [(chunks, None)]
    aspects, max_pt, width_pt = [], 0.0, 0.0
    for text, style in chunks:
        face, sz, bd = base_font, size, bold
        if style == 'b':
            face, bd = F_EMPH, True
        elif style == 'c':
            face, sz = F_CODE, size * 0.86
        elif style == 'y':
            bd = True
        code = face == F_CODE
        width_pt += _pil(sz, code, bd).getlength(text)
        max_pt = max(max_pt, sz)
        aspects.append(_COURIER_ASPECT if code else _SANS_ASPECT)
    if width_pt <= 0:
        return 0.0
    lines = max(1, math.ceil(width_pt / max(w_cm / CM_PER_PT, 1e-6) - 1e-9))
    return lines * max_pt * CM_PER_PT * max(aspects) * ls


def rendered_height(tf, w_cm, default=SZ_BODY):
    """Rendered height in cm of a whole text frame.

    Mirrors the layout audit's para_metrics exactly: empty/spacer paragraphs
    count a 14 pt line, and each run is measured with its real size and bold,
    so the pack pass and the audit can never disagree about a frame's height.
    """
    total = 0.0
    for p in tf.paragraphs:
        runs = [(r.text, (r.font.size.pt if r.font.size else 14.0),
                 (r.font.name or ''), bool(r.font.bold))
                for r in p.runs if r.text]
        if not runs:
            total += 14.0 * CM_PER_PT * _SANS_ASPECT * 1.2
            continue
        width_pt, max_pt, aspects = 0.0, 0.0, []
        for text, pt, face, bd in runs:
            is_code = face == F_CODE
            width_pt += _pil(pt, is_code, bd).getlength(text)
            max_pt = max(max_pt, pt)
            aspects.append(_COURIER_ASPECT if is_code else _SANS_ASPECT)
        avail = w_cm / CM_PER_PT
        lines = max(1, math.ceil(width_pt / avail - 1e-9))
        ls = p.line_spacing if isinstance(p.line_spacing, float) else 1.0
        total += lines * max_pt * CM_PER_PT * max(aspects) * ls
    return total


# --------------------------------------------------------- block tagging ---
# Every public composite helper is tagged with a block id so the layout pack
# pass can move a panel together with the text and bullet that belong to it.
_BLOCK = [0]


def block(fn):
    @functools.wraps(fn)
    def wrap(slide, *args, **kwargs):
        start = len(slide.shapes)
        out = fn(slide, *args, **kwargs)
        _BLOCK[0] += 1
        tag = 'blk%04d' % _BLOCK[0]
        for i in range(start, len(slide.shapes)):
            try:
                slide.shapes[i].name = tag
            except Exception:
                pass
        return out
    return wrap


# ---------------------------------------------------------------- helpers ---
def _style(run, font, size, color, bold=False, italic=False):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    # keep east-asian / complex-script faces in step with the latin face
    rPr = run._r.get_or_add_rPr()
    for tag in ('a:ea', 'a:cs', 'a:sym'):
        el = rPr.makeelement(
            '{http://schemas.openxmlformats.org/drawingml/2006/main}' + tag.split(':')[1],
            {'typeface': font},
        )
        rPr.append(el)
    return run


def textbox(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP, wrap=True):
    box = slide.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return box, tf


def para(tf, first, chunks, font, size, color, align=PP_ALIGN.LEFT,
         line_spacing=None, bold=False, italic=False):
    """Append one paragraph. `chunks` is a str or a list of (text, style) pairs.

    Style codes: None plain | 'b' bold emphasis face | 'c' inline code |
    'y' bold yellow | 'i' italic yellow
    """
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    if line_spacing:
        p.line_spacing = line_spacing
    if isinstance(chunks, str):
        chunks = [(chunks, None)]
    for chunk in chunks:
        text, style = (chunk, None) if isinstance(chunk, str) else chunk
        f, sz, col, bd, it = font, size, color, bold, italic
        if style == 'b':
            f, bd = F_EMPH, True
        elif style == 'c':
            f, sz = F_CODE, size * 0.86
        elif style == 'y':
            col, bd = YELLOW, True
        elif style == 'i':
            col, it = YELLOW, True
        _style(p.add_run(), f, sz, col, bd, it).text = text
    return p


def spacer(tf, size, first=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = PP_ALIGN.LEFT
    _style(p.add_run(), F_BODY, size, WHITE).text = ''
    return p


def shape(slide, kind, x, y, w, h, fill=None, line=None, line_w=1.0, adj=None):
    sp = slide.shapes.add_shape(kind, Cm(x), Cm(y), Cm(w), Cm(h))
    sp.shadow.inherit = False
    if adj is not None:
        sp.adjustments[0] = adj
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
        sp.line.width = Pt(line_w)
    sp.text_frame.text = ''
    return sp


# ------------------------------------------------------- composite blocks ---
@block
def title(slide, chunks, ext=False):
    y, h = (Y_TITLE_EXT, H_TITLE_EXT) if ext else (Y_TITLE_STD, H_TITLE_STD)
    _, tf = textbox(slide, X_L, y, W_WIDE, h)
    para(tf, True, chunks, F_TITLE,
         24.0 if ext else SZ_TITLE, WHITE)


@block
def body(slide, y, paras, ext=False, size=SZ_BODY, w=W_BODY, ls=None):
    """Body copy. `paras` items are str, or list of (text, style) chunks."""
    h = max(1.0, min(14.0, Y_BOTTOM - y))
    _, tf = textbox(slide, X_L, y, w, h)
    first = True
    for item in paras:
        if item is None:
            spacer(tf, size, first)
        else:
            para(tf, first, item, F_BODY, size, WHITE, line_spacing=ls or 1.0)
        first = False
    return tf


@block
def note(slide, y, chunks, h=2.0, size=SZ_TINY, italic=False, color=WHITE):
    """A short aside under the body copy.

    Accepts a plain string or a list of (text, style) chunks; a single
    wrapped chunk list is unwrapped so callers need not be fussy.
    """
    h = max(0.8, min(h, Y_BOTTOM - y))
    _, tf = textbox(slide, X_L, y, W_BODY, h)
    if isinstance(chunks, str):
        chunks = [(chunks, None)]
    elif len(chunks) == 1 and isinstance(chunks[0], list):
        chunks = chunks[0]
    para(tf, True, chunks, F_BODY, size, color, line_spacing=1.2, italic=italic)
    return tf


# Courier New line metrics: (winAscent + winDescent) / unitsPerEm = 2320/2048.
# PowerPoint sets a single-spaced line to that height, then multiplies by the
# paragraph's line_spacing value -- so this is the real cm-per-code-line.
_F_CODE_ASPECT = (1705 + 615) / 2048
CM_PER_PT = 2.54 / 72.0


def code_line_h(size, ls=1.15):
    """Rendered height of one code line, in cm."""
    return size * CM_PER_PT * _F_CODE_ASPECT * ls


def code_height(n_lines, size=SZ_CODE, ls=1.15, pad=0.9):
    """Panel height that actually contains `n_lines` at `size`."""
    return code_line_h(size, ls) * n_lines + pad


@block
def code(slide, y, lines, size=SZ_CODE, x=X_L, w=W_WIDE, panel=True):
    """Python snippet on a rounded panel, matching the callout styling.

    The panel is sized from the real Courier New line metrics so it always
    encloses the text; returns the bottom edge for flow layout.  If the
    widest source line cannot fit the pane at `size`, the whole frame drops
    to the largest size that does, so a long line never wraps or spills.
    """
    code_w = w - 1.24 if panel else w
    limit = code_w - 0.35

    def _line_pt_width(line):
        if isinstance(line, str):
            line = [(line, None)]
        return sum(_pil(size, True, style in ('b', 'y')).getlength(txt)
                   for chunk in line for txt, style in (
                       (chunk, None) if isinstance(chunk, str) else (chunk,)))
    widest = max((_line_pt_width(ln) for ln in lines), default=0.0)
    if widest > 0.0 and widest * CM_PER_PT > limit:
        size = math.floor(size * limit / (widest * CM_PER_PT))

    h = code_height(len(lines), size)
    if panel:
        shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h,
              fill=PANEL, line=PANEL, adj=0.08319)
        x += 0.62
        w -= 1.24
    _, tf = textbox(slide, x, y + 0.45, w, h - 0.9)
    for i, ln in enumerate(lines):
        para(tf, i == 0, ln if isinstance(ln, list) else [(ln, None)],
             F_CODE, size, WHITE, line_spacing=1.15)
    return y + h


@block
def command(slide, y, text, x=X_L, w=W_WIDE, size=SZ_CMD):
    """A terminal command -- deliberately plain, no panel."""
    _, tf = textbox(slide, x, y, w, 0.9)
    para(tf, True, text, F_CODE, size, WHITE, line_spacing=1.15)
    return y + 0.9


@block
def callout(slide, y, chunks, h=2.44):
    # grow the panel when the copy needs more room than the caller estimated
    h = max(h, para_height(chunks, SZ_SMALL, 22.10, ls=1.2) + 0.6)
    shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, X_L, y, W_WIDE, h,
          fill=PANEL, line=PANEL, adj=0.08319)
    shape(slide, MSO_SHAPE.OVAL, X_L + 0.55, y + (h - 0.38) / 2, 0.38, 0.38,
          fill=YELLOW, line=YELLOW)
    _, tf = textbox(slide, 3.23, y + 0.4, 22.10, h - 0.8, anchor=MSO_ANCHOR.MIDDLE)
    para(tf, True, chunks, F_BODY, SZ_SMALL, YELLOW, line_spacing=1.2, italic=True)
    return y + h


@block
def bullet(slide, y, chunks, h=2.3, size=16.0):
    shape(slide, MSO_SHAPE.OVAL, X_BULLET, y + 0.08, 0.36, 0.36,
          fill=YELLOW, line=YELLOW)
    _, tf = textbox(slide, X_ITEM, y, W_ITEM, h)
    para(tf, True, chunks, F_BODY, size, WHITE, line_spacing=1.2)


@block
def num_item(slide, y, n, head, chunks, h=2.3):
    """Numbered circle + yellow heading + white explanation."""
    shape(slide, MSO_SHAPE.OVAL, X_L, y, 1.07, 1.07, fill=YELLOW, line=YELLOW)
    _, tf = textbox(slide, X_L, y, 1.07, 1.07, anchor=MSO_ANCHOR.MIDDLE)
    para(tf, True, str(n), F_TITLE, SZ_NUMBER, BG, align=PP_ALIGN.CENTER)
    _, tf = textbox(slide, X_ITEM, y - 0.06, W_ITEM, 0.95)
    para(tf, True, head, F_BODY, SZ_TINY, YELLOW, bold=True)
    _, tf = textbox(slide, X_ITEM, y + 0.83, W_ITEM, h)
    para(tf, True, chunks, F_BODY, SZ_SMALL, WHITE, line_spacing=1.2)


@block
def check_item(slide, y, chunks, h=2.0):
    shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, X_L + 0.05, y, 0.66, 0.66,
          fill=BG, line=YELLOW, line_w=1.75, adj=0.19231)
    _, tf = textbox(slide, X_ITEM, y - 0.06, W_ITEM, h)
    para(tf, True, chunks, F_BODY, 16.0, WHITE, line_spacing=1.2)


@block
def question_item(slide, y, n, chunks):
    _, tf = textbox(slide, X_L, y, 1.27, 0.91)
    para(tf, True, f'{n}.', F_BODY, SZ_TINY, YELLOW, bold=True)
    _, tf = textbox(slide, X_ITEM, y, W_ITEM, 2.0)
    para(tf, True, chunks, F_BODY, SZ_TINY, WHITE, line_spacing=1.2)


@block
def table(slide, y, rows, col_w, row_h=1.15, head_h=1.25, size=13.5):
    """Header row in PANEL, body rows in BG with pale gridlines."""
    n_r, n_c = len(rows), len(rows[0])
    total_w = sum(col_w)
    gf = slide.shapes.add_table(n_r, n_c, Cm(X_L), Cm(y),
                                Cm(total_w), Cm(head_h + row_h * (n_r - 1)))
    tbl = gf.table
    # kill the inherited banded style
    tblPr = tbl._tbl.find(
        '{http://schemas.openxmlformats.org/drawingml/2006/main}tblPr')
    if tblPr is not None:
        tblPr.set('firstRow', '0')
        tblPr.set('bandRow', '0')
        for child in list(tblPr):
            if child.tag.endswith('tableStyleId'):
                tblPr.remove(child)

    for c, w in enumerate(col_w):
        tbl.columns[c].width = Cm(w)
    tbl.rows[0].height = Cm(head_h)
    for r in range(1, n_r):
        tbl.rows[r].height = Cm(row_h)

    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.margin_left = cell.margin_right = Cm(0.2)
            cell.margin_top = cell.margin_bottom = Cm(0.1)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = PANEL if r == 0 else BG
            tf = cell.text_frame
            tf.word_wrap = True
            chunks = val if isinstance(val, list) else [(str(val), None)]
            if r == 0:
                chunks = [(t, None) for t, _ in chunks]
            para(tf, True, chunks, F_BODY, size,
                 YELLOW if r == 0 else WHITE,
                 align=PP_ALIGN.CENTER if c else PP_ALIGN.LEFT,
                 bold=(r == 0))
            for p in tf.paragraphs:
                p.line_spacing = 1.0
    return gf


# --------------------------------------------------------------- packing ---
def _block_metrics(shapes):
    """(orig_top, left, right, height) for one block, using rendered text.

    Text boxes are measured rather than using their declared height, because
    body() deliberately asks for a tall box and must not drag later blocks
    down with it.
    """
    top = min(sh.top for sh in shapes) / 360000
    left = min(sh.left for sh in shapes) / 360000
    right = max(sh.left + (sh.width or 0) for sh in shapes) / 360000
    bottom = top
    for sh in shapes:
        t = sh.top / 360000
        h = (sh.height or 0) / 360000
        if sh.has_text_frame and sh.text_frame.text.strip():
            rh = rendered_height(sh.text_frame, (sh.width or 0) / 360000)
            a = sh.text_frame.vertical_anchor
            if a == MSO_ANCHOR.MIDDLE:
                t = t + (h - rh) / 2.0
            elif a == MSO_ANCHOR.BOTTOM:
                t = t + h - rh
            h = rh
        bottom = max(bottom, t + h)
    return top, left, right, bottom - top


def pack_slide(slide, gap=0.30, limit=Y_BOTTOM):
    """Push tagged blocks down until none overlap.

    Blocks are only moved when they actually collide, so a slide that already
    laid out cleanly keeps its original spacing.  Returns (max_bottom, moved).
    """
    groups = {}
    for sh in slide.shapes:
        name = sh.name or ''
        if name.startswith('blk'):
            groups.setdefault(name, []).append(sh)
    blocks = []
    for shapes in groups.values():
        top, left, right, height = _block_metrics(shapes)
        blocks.append(dict(shapes=shapes, top=top, left=left,
                           right=right, h=height))
    blocks.sort(key=lambda b: b['top'])

    cursor = None
    cursor_right = None
    moved = 0
    for b in blocks:
        new_top = b['top']
        if (cursor is not None and cursor_right is not None
                and b['left'] < cursor_right - 0.12
                and new_top < cursor + gap):
            new_top = cursor + gap
        shift = new_top - b['top']
        if shift > 1e-6:
            for sh in b['shapes']:
                sh.top = Cm(sh.top / 360000 + shift)
            moved += 1
        bottom = new_top + b['h']
        if cursor is None or bottom > cursor:
            cursor, cursor_right = bottom, b['right']
    return (cursor or 0.0), moved


def pack_deck(prs, gap=0.30, limit=Y_BOTTOM):
    """Pack every slide; returns [(1-based index, bottom, moved), ...] that
    still run past `limit`."""
    tight = []
    for i, slide in enumerate(prs.slides, 1):
        bottom, moved = pack_slide(slide, gap=gap, limit=limit)
        if bottom > limit:
            tight.append((i, round(bottom, 2), moved))
    return tight

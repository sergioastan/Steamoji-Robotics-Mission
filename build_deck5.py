# -*- coding: utf-8 -*-
"""Build Slides/M2/myCobot_05.pptx -- 'Sorting Good Parts' (M2-P5).

Rebuilds the deck from the theme/layouts of the reference sample
Slides/myCobot_08.pptx, but teaches the HSV colour + contour quality-control
inspection that students complete in M2/M2-P5-Starter.py.

Every code snippet below is copied verbatim from M2/M2-P5-Base.py, except the
two shell commands, the sample terminal output, and the worksheet blanks.
"""

import os
import shutil
import zipfile

from pptx import Presentation
from pptx.util import Cm

from build_deck_theme import (
    BG, PANEL2, YELLOW, WHITE,
    F_TITLE, F_BODY, F_CODE,
    X_L, W_BODY, W_WIDE,
    Y_TITLE_STD, Y_TITLE_EXT, Y_BODY_STD, Y_BODY_EXT,
    SZ_BODY, SZ_CODE, SZ_DIVIDER,
    textbox, para, title, body, note, code, command,
    callout, bullet, num_item, check_item, question_item, table,
    Y_BOTTOM, pack_deck,
)

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'Slides', 'myCobot_08.pptx')
OUT = os.path.join(HERE, 'Slides', 'M2', 'myCobot_05.pptx')
TMP = os.path.join(HERE, 'tmp_media')

STARTER = 'M2-P5-Starter.py'
SCP = f'scp {STARTER} er@192.168.1.149:Documents'
RUN = f'python {STARTER}'


def media():
    """Pull the generic title artwork out of the reference deck."""
    os.makedirs(TMP, exist_ok=True)
    z = zipfile.ZipFile(REF)
    for name in ('image1.png', 'image2.png'):
        with z.open('ppt/media/' + name) as src, \
                open(os.path.join(TMP, name), 'wb') as dst:
            shutil.copyfileobj(src, dst)
    z.close()
    return {n: os.path.join(TMP, n) for n in ('image1.png', 'image2.png')}


def new_deck():
    prs = Presentation(REF)
    lst = prs.slides._sldIdLst
    for sld in list(lst):
        prs.part.drop_rel(sld.get(
            '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'))
        lst.remove(sld)

    def add(layout=1, master=0):
        s = prs.slides.add_slide(prs.slide_masters[master].slide_layouts[layout])
        for ph in list(s.placeholders):
            ph._element.getparent().remove(ph._element)
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = BG
        return s

    return prs, add


def build():
    art = media()
    prs, add = new_deck()

    # ============================================================ 1. TITLE ===
    s = add(0)
    s.shapes.add_picture(art['image1.png'], Cm(17.39), Cm(3.81), Cm(11.18), Cm(11.38))
    s.shapes.add_picture(art['image2.png'], Cm(1.91), Cm(2.54), Cm(9.68), Cm(3.00))
    _, tf = textbox(s, 1.90, 12.71, 24.45, 6.98, anchor=3)  # BOTTOM
    para(tf, True, 'Introduction to', F_TITLE, SZ_DIVIDER, WHITE, line_spacing=1.0)
    para(tf, False, 'Advanced Robotics', F_TITLE, SZ_DIVIDER, WHITE, line_spacing=1.0)

    # ========================================================== 2. DIVIDER ===
    s = add(1)
    _, tf = textbox(s, X_L, 15.41, W_WIDE, 4.28, anchor=3)
    para(tf, True, 'Project 5', F_TITLE, SZ_DIVIDER, YELLOW, line_spacing=1.0)
    para(tf, False, 'Sorting Good Parts', F_TITLE, SZ_DIVIDER, WHITE, line_spacing=1.0)

    # ================================================== 3. WHAT IT DECIDES ===
    s = add()
    title(s, [('What this project decides', None)])
    body(s, Y_BODY_STD, [
        [('Project 4 asked a question about your hand. This one asks a question '
          'about an object, and it has to answer it the same way every time.', None)],
        [('Put a part in the inspection zone and the program returns one of two '
          'words, plus a reason you can read from across the room:', None)],
    ])
    code(s, 9.6, [
        'PASS   Good Part (2841px)',
        'FAIL   Too Small (940px)',
        'FAIL   Shape Defect (Ratio: 1.62)',
        'FAIL   No Item / Wrong Color',
    ], size=15.0)
    callout(s, 13.6, [
        ('The reason is the whole point. A quality control system that says only '
         '"no" is useless, because somebody still has to work out what to do about '
         'it. Every ', None),
        ('return', 'c'),
        (' in this program carries its own explanation.', None),
    ], h=2.44)

    # ============================================== 4. THE ROBOT IS OPTIONAL ===
    s = add()
    title(s, [('The robot is optional this time', None)])
    body(s, Y_BODY_STD, [
        [('Read the robot setup in Project 4 again: the arm was created at the top '
          'level, outside any ', None), ('try', 'c'), (', so no arm meant no '
          'program. This project does the opposite.', None)],
    ])
    code(s, 8.4, [
        'except Exception as e:',
        '    print(f"Robot hardware warning: {e}")',
        '    print("Continuing with OpenCV camera pipeline only...\\n")',
    ], size=13.0)
    body(s, 12.0, [
        [('If the arm is missing, unplugged, or sulking, this program says so and '
          'carries on with the camera. You can do this entire project on a laptop.', None)],
    ])
    note(s, 14.0, [
        [('Now notice something stranger. Look at what the arm is actually used for '
          'in this file: it is switched on and folded into a home position, and then '
          'never mentioned again. The inspection runs entirely on the camera. That '
          'is worth knowing before you go looking for the part the arm is supposed '
          'to be doing.', None)],
    ], h=2.8)

    # ================================================= 5. TWO QUESTIONS ===
    s = add()
    title(s, [('Two questions, asked in order', None)])
    body(s, Y_BODY_STD, [
        [('Everything in ', None), ('inspect_part', 'c'), (' is an answer to one of '
          'two questions, asked in this order and never any other:', None)],
    ])
    num_item(s, 8.6, 1, 'Is anything there, and is it the right colour?',
             [('Find the green pixels. If there are none, stop immediately.', None)], h=1.9)
    num_item(s, 10.5, 2, 'Is it the right size and the right shape?',
             [('Measure the biggest green shape and compare it to the spec.', None)], h=1.9)
    body(s, 12.8, [
        [('Colour first, then size and shape. The order is not arbitrary — without '
          'the first question there is nothing for the second one to measure.', None)],
    ])
    callout(s, 15.0, [
        ('This is the shape of almost every inspection program you will ever write: '
         'cheap and decisive tests first, expensive and fiddly ones last.', None),
    ], h=1.9)

    # ============================================= 6. COLOUR IS THREE NUMBERS ===
    s = add()
    title(s, [('Colour is three numbers, badly', None)])
    body(s, Y_BODY_STD, [
        [('A pixel in the pictures you have been using is three numbers: blue, '
          'green, red, each from 0 to 255. To ask "is this green?" in that system '
          'you have to accept a fuzzy three-dimensional region — high green, low '
          'red, low-ish blue — and describe it as a shape in a cube.', None)],
        [('It works, and it is miserable to tune. Move the lamp and the region you '
          'need moves with it.', None)],
    ])
    note(s, 12.4, [
        [('This is the same problem Project 4 had with colour order, seen from the '
          'other side. There, the fix was a swap that made detection quietly better. '
          'Here the fix is a whole colour space, and it is the single most useful '
          'idea in this project.', None)],
    ], h=2.8)

    # ==================================================== 7. HSV, HUE IS ONE ===
    s = add()
    title(s, [('HSV puts colour on one axis', None)])
    body(s, Y_BODY_STD, [
        [('HSV is a different way of writing the same three numbers. Hue is the '
          'colour itself, as a single number around a wheel. Saturation is how '
          'strong the colour is. Value is how bright it is.', None)],
        [('Because hue is one axis, "green" stops being a region and becomes an '
          'interval. Two numbers now describe it.', None)],
    ])
    body(s, 11.4, [
        [('Saturation and Value are what make it survive bad lighting. A dark green '
          'and a bright green have the same hue, so a range on hue alone still '
          'finds both — which is exactly what you want when the lighting in the lab '
          'is not what you planned for.', None)],
    ])
    note(s, 15.4, [
        [('You still have to give inRange a value for S and V, and this project '
          'gives them the widest legal range: 70 up to 255. Only the hue is being '
          'restricted. That is deliberate, and it is worth saying out loud in the '
          'debrief: this scanner accepts any brightness and any richness of green, '
          'and only cares which colour it is.', None)],
    ], h=2.8)

    # ==================================================== 8. HUE STOPS AT 179 ===
    s = add()
    title(s, [('OpenCV stops at 179', None)])
    body(s, Y_BODY_STD, [
        [('In mathematics, hue runs from 0 to 360. In OpenCV it runs from 0 to '
          '179, because the value is squeezed into a single byte.', None)],
        [('So green, which you might expect to sit at 120, is actually near 60. '
          'And the numbers in this file bracket it:', None)],
    ])
    code(s, 11.4, [
        'LOWER_GREEN = np.array([35, 70, 70])',
        'UPPER_GREEN = np.array([85, 255, 255])',
    ], size=15.0)
    body(s, 13.8, [
        [('35 to 85 is a band around 60 — green, with room on both sides. Hue 0 is '
          'red, and because the wheel closes, red is also at the far end of the '
          'scale. That wrap-around is why a colour at one end cannot be described '
          'by a single range.', None)],
    ])
    note(s, 16.5, [
        [('A hue band this wide is a wide net. If the mask surprises you, print '
          'the hue of the pixels you did not want — read, then choose.', None)],
    ], h=2.2)

    # ==================================================== 9. WHY np.array ===
    s = add()
    title(s, [('Why those brackets are arrays', None)])
    body(s, Y_BODY_STD, [
        [('A Python list would have been the obvious way to write those two lines. '
          'It is a NumPy array instead, because the next function is about to hand '
          'all three numbers to OpenCV at once and it wants something it can index '
          'numerically.', None)],
        [('This is the first project where numpy earns its import. Project 4 '
          'imported it and never used it; here it appears twice — once for these '
          'bounds and once for the kernel in a few slides.', None)],
    ])
    callout(s, 12.6, [
        ('Every project in this module carries ', None),
        ('import numpy as np', 'c'),
        (' in the same place whether or not it needs it, so seeing it in the import '
         'block tells you nothing. What tells you something is where it gets used.', None),
    ], h=2.44)

    # ======================================================== 10. INRANGE ===
    s = add()
    title(s, [('inRange: your first threshold', None)])
    body(s, Y_BODY_STD, [
        [('One line, and it is the moment this project turns into computer vision:', None)],
    ])
    code(s, 6.4, [
        '    hsv = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2HSV)',
        '    mask = cv2.inRange(hsv, LOWER_GREEN, UPPER_GREEN)',
    ], size=14.0)
    body(s, 10.0, [
        [('The mask is another picture, the same size as the region you passed in. '
          'Every pixel is now either ', None), ('255', 'c'), (' — in range, so it '
          'is green — or ', None), ('0', 'c'), (' — out of range, so it is black. '
          'Nothing in between.', None)],
    ])
    note(s, 13.0, [
        [('This is the same idea as the thresholds in Project 4, but cruder and more '
          'useful: it does not produce a score, it produces an image you can look '
          'at. That is why this program opens a second window. When the mask does '
          'not match what you expected, you can see exactly which pixels are being '
          'counted and which are being thrown away.', None)],
    ], h=2.8)

    # ==================================================== 11. THE MASK WINDOW ===
    s = add()
    title(s, [('The mask is a picture too', None)])
    body(s, Y_BODY_STD, [
        [('Two windows come up at the end of this program, and the second one is '
          'the reason this project is teachable:', None)],
    ])
    code(s, 8.4, [
        '        cv2.imshow("Mission 02 - Project 05: QC Scanner", frame)',
        '        cv2.imshow("Mask View", mask)',
    ], size=13.0)
    body(s, 11.4, [
        [('The first window is what the part looks like to a person. The second is '
          'what the program actually believes: white where it thinks there is a '
          'part, black everywhere else.', None)],
    ])
    callout(s, 14.4, [
        ('When the two disagree, the mask is not lying and neither is the camera — '
         'your colour range is simply wrong. That single window turns an hour of '
         'guessing numbers into ten seconds of looking.', None),
    ], h=2.0)

    # ===================================================== 12. SPECKLED MASKS ===
    s = add()
    title(s, [('Speckled masks lie', None)])
    body(s, Y_BODY_STD, [
        [('A raw mask is never clean. Real images have sensor noise, and a single '
          'stray bright pixel inside the range becomes its own white dot. Left alone, '
          'those dots turn into their own contours later, and the "largest contour" '
          'picks whichever speck happens to be biggest.', None)],
    ])
    body(s, 10.6, [
        [('The fix is two lines:', None)],
    ])
    code(s, 12.2, [
        '    kernel = np.ones((5, 5), np.uint8)',
        '    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)',
    ], size=14.0)
    body(s, 15.2, [
        [('np.ones', 'c'), (' builds a 5 by 5 block of ones — a small square of '
          'tool. ', None), ('MORPH_OPEN', 'c'), (' shrinks everything with it, then '
          'grows it back.', None)],
    ])
    note(s, 17.2, [
        [('Shrinking then growing is an opening: it removes anything too thin to '
          'survive the squeeze and leaves the chunky shapes roughly as they were. '
          'It is the standard first move whenever a mask comes out speckled.', None)],
    ], h=2.0)

    # ====================================================== 13. THE TRAP ===
    s = add()
    title(s, [('The trap inside opening', None)])
    body(s, Y_BODY_STD, [
        [('Here is the thing to be careful about, and it connects two constants '
          'that look unrelated.', None)],
        [('A 5 by 5 opening deletes any blob smaller than about that size. So if a '
          'part is genuinely small — or far away, or only partly green — the noise '
          'filter removes it entirely, and by the time the rules run there is '
          'nothing left to measure.', None)],
    ])
    callout(s, 12.4, [
        ('A part that is too small is supposed to report ', None),
        ('Too Small', 'c'),
        ('. If the opening is aggressive enough, it reports ', None),
        ('No Item / Wrong Color', 'c'),
        (' instead — a completely different fault, pointing at the colour range '
         'rather than at the size. Same part, wrong diagnosis.', None),
    ], h=2.44)
    note(s, 16.2, [
        [('This is the single most useful thing to understand about the whole '
          'project. When a fault message does not match the fault, suspect the step '
          'before the message, not the message itself. The mask window shows you '
          'this immediately: if the small part is not in the mask, it never reached '
          'the rules.', None)],
    ], h=2.8)

    # ========================================================= 14. CONTOURS ===
    s = add()
    title(s, [('Contours are outlines', None)])
    body(s, Y_BODY_STD, [
        [('A mask is a field of loose white pixels. What the rules need is an '
          'object with a shape you can measure. That is what a contour is: the '
          'boundary traced around each connected white region.', None)],
    ])
    code(s, 9.4, [
        '    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)',
    ], size=12.5)
    body(s, 11.6, [
        [('Two values come back. ', None), ('contours', 'c'), (' is the list you '
          'want. The second, thrown away here with ', None), ('_', 'c'), (', is the '
          'hierarchy — the tree saying which contour is inside which, which this '
          'project never asks about.', None)],
    ])
    callout(s, 14.6, [
        ('RETR_EXTERNAL', 'c'),
        (' keeps only outer boundaries and ignores holes. ', None),
        ('CHAIN_APPROX_SIMPLE', 'c'),
        (' stores straight runs as single points instead of every pixel along them. '
         'That second flag is not a choice about correctness — it is a choice about '
         'how much memory the list uses, and it makes straight edges cheaper.', None),
    ], h=2.44)

    # ================================================== 15. NOTHING IS A RESULT ===
    s = add()
    title(s, [('Finding nothing is a result', None)])
    body(s, Y_BODY_STD, [
        [('The next two lines were written for you, and they exist because the line '
          'after them would crash:', None)],
    ])
    code(s, 8.0, [
        '    if not contours:',
        '        return "FAIL", "No Item / Wrong Color", mask',
    ], size=14.0)
    body(s, 10.8, [
        [('An empty list is falsy, so ', None), ('if not contours', 'c'), (' catches '
          'it. Without this, ', None), ('max(contours, key=cv2.contourArea)', 'c'),
         (' on the next slide would raise ', None), ('ValueError: max() arg is an '
          'empty sequence', 'c'), (' — and a quality control system that crashes on '
          'a bad part is worse than useless.', None)],
    ])
    note(s, 14.8, [
        [('An empty zone is not an error condition here. It is a perfectly ordinary '
          'answer, and the program treats it as one. Notice also that all three '
          'returns from this function hand back ', None),
         ('mask', 'c'), (' as the third value, including this early one, so the '
          'caller always has something to display.', None)],
    ], h=2.8)

    # ==================================================== 16. THE BIGGEST BLOB ===
    s = add()
    title(s, [('The biggest blob is the part', None)])
    body(s, Y_BODY_STD, [
        [('The mask may contain several shapes. This program assumes the part is '
          'the largest one, and says so in the comment:', None)],
    ])
    code(s, 8.6, [
        '    largest_contour = max(contours, key=cv2.contourArea)',
        '    area = cv2.contourArea(largest_contour)',
    ], size=14.0)
    body(s, 11.6, [
        [('Two different measurements of the same shape, and both are used. ', None),
         ('max', 'c'), (' searches the list using ', None), ('cv2.contourArea', 'c'),
         (' as its key, so it never builds a list of areas to compare. Then ', None),
         ('cv2.contourArea', 'c'), (' measures the winner, and that number goes '
          'straight into the size rules.', None)],
    ])
    note(s, 15.4, [
        [('The assumption is the weak point, and it is worth being able to defend. '
          'Put a green pen on the table next to the part and the pen may well win, '
          'because it is a smooth solid shape while the part has holes and edges. '
          'Picking the largest contour is a decision, not a truth.', None)],
    ], h=2.8)

    # ====================================================== 17. THE BOX ===
    s = add()
    title(s, [('A box, not a rotated box', None)])
    body(s, Y_BODY_STD, [
        [('The next two lines measure shape, and the first one has a trap in its '
          'name:', None)],
    ])
    code(s, 7.4, [
        '    x, y, w, h = cv2.boundingRect(largest_contour)',
        '    aspect_ratio = float(w) / h',
    ], size=15.0)
    body(s, 10.2, [
        [('boundingRect', 'c'), (' returns the smallest axis-aligned rectangle '
          'around the shape — aligned to the picture, never rotated. A part lying '
          'at an angle still gets an upright box.', None)],
        [('That is why the aspect ratio is a rough measure rather than a good one. '
          'A square rotated 20 degrees has a box that is wider than it is tall, and '
          'a quality check written this way will call it defective.', None)],
    ])
    note(s, 15.4, [
        [('The ', None), ('float()', 'c'), (' is not decoration. In Python 3, ', None),
         ('w / h', 'c'), (' already gives a float, so the call is unnecessary here — '
          'but it is the habit you want from code written for Python 2, and it makes '
          'the intent obvious to whoever reads it next.', None)],
    ], h=2.8)

    # ================================================ 18. THREE RULES, FIRST WINS ===
    s = add()
    title(s, [('Three rules, first one wins', None)])
    body(s, Y_BODY_STD, [
        [('This is the only place in the project where a verdict is reached:', None)],
    ])
    code(s, 6.6, [
        '    if area < MIN_AREA:',
        '        return "FAIL", f"Too Small ({int(area)}px)", mask',
        '    if area > MAX_AREA:',
        '        return "FAIL", f"Too Large ({int(area)}px)", mask',
        '    if abs(aspect_ratio - TARGET_ASPECT) > ASPECT_TOLERANCE:',
        '        return "FAIL", f"Shape Defect (Ratio: {aspect_ratio:.2f})", mask',
    ], size=12.5)
    body(s, 12.6, [
        [('Three separate tests, each returning immediately. There is no score and '
          'no combined judgement — the first test that fails is the answer you get.', None)],
    ])
    note(s, 15.2, [
        [('So a part that is both too small and the wrong shape reports only ', None),
         ('Too Small', 'c'), (', and never mentions the shape. That is a deliberate '
          'trade: simple to read, simple to write, and it always tells you the '
          'first thing that is wrong. If your factory needed all the faults at once, '
          'this is the shape of code you would have to rewrite.', None)],
    ], h=2.8)

    # =================================================== 19. ROWS THEN COLUMNS ===
    s = add()
    title(s, [('Rows first, then columns', None)])
    body(s, Y_BODY_STD, [
        [('This is the line students get wrong most often, and it is worth reading '
          'twice:', None)],
    ])
    code(s, 7.4, [
        '        roi = frame[y1:y2, x1:x2]',
    ], size=16.0)
    body(s, 9.6, [
        [('A NumPy slice takes rows first and columns second. ', None),
         ('y1:y2', 'c'), (' picks the vertical span, ', None), ('x1:x2', 'c'),
         (' picks the horizontal span. It is the opposite order to how you say it '
          'out loud, and swapping them produces an error rather than a wrong answer '
          '— which is a small mercy.', None)],
        [('The constants are in the same order, which helps and hurts in equal '
          'measure:', None)],
    ])
    code(s, 14.6, [
        '# Base ROI Coordinates [y_min, y_max, x_min, x_max] on 640x480 frame',
        'BASE_ROI = [120, 360, 200, 440]',
    ], size=13.0)
    note(s, 17.6, [
        [('Rows, then columns, in the comment, in the constant and in the slice. '
          'Consistent, and still the most common source of a transposed crop.', None)],
    ], h=1.8)

    # ================================================ 20. SCALE AND OFFSET ===
    s = add()
    title(s, [('Scale and offset around the middle', None)])
    body(s, Y_BODY_STD, [
        [('The inspection zone is not hard-coded. It is built at run time from a '
          'centre, a scale and an offset, so you can retune it without touching '
          'any arithmetic:', None)],
    ])
    code(s, 9.4, [
        'ROI_SCALE = 0.95      # 1.0 = original size, 0.5 = half size, 2.0 = double size',
        'ROI_OFFSET_X = -15     # Horizontal offset (pixels), positive = right',
        'ROI_OFFSET_Y = -70     # Vertical offset (pixels), positive = down',
    ], size=9.8)
    body(s, 12.6, [
        [('Scale 0.95 shrinks the box slightly. The offsets move it — negative X '
          'moves left, negative Y moves up. Three numbers, and you can retune the '
          'whole zone by editing three lines.', None)],
    ])
    note(s, 14.8, [
        [('Note that 0.95 does not mean 5 percent smaller in each direction. The '
          'scale is applied to the width and height before the centre is '
          'recalculated, so it is genuinely a scale of the box and not a fudge.', None)],
    ], h=2.2)

    # ======================================================== 21. CLAMPING AGAIN ===
    s = add()
    title(s, [('Clamping, again', None)])
    body(s, Y_BODY_STD, [
        [('At the bottom of ', None), ('calculate_roi_bounds', 'c'), (' there are '
          'four lines that look like they are tidying up. They are not. They are '
          'the reason this function cannot crash.', None)],
    ])
    code(s, 9.0, [
        '    new_x1 = max(0, min(new_x1, 640))',
        '    new_x2 = max(0, min(new_x2, 640))',
    ], size=15.0)
    body(s, 11.6, [
        [('Push the offsets far enough and the box hangs off the edge of the '
          'picture. A NumPy slice with an out-of-range end is not an error — it '
          'silently returns a smaller region, or an empty one. These lines make '
          'sure the region is always inside the frame.', None)],
    ])
    callout(s, 14.6, [
        ('This is the same clamp as ', None),
        ('map_value', 'c'),
        (' in Project 4, doing the same job on a different type. Once you have seen '
         'it twice you start looking for it everywhere, and in this module it is '
         'never wrong.', None),
    ], h=2.0)

    # ==================================================== 22. THE SPEC NUMBERS ===
    s = add()
    title(s, [('The numbers you will actually tune', None)])
    body(s, Y_BODY_STD, [
        [('Four constants decide what passes, and all four are at the top of the '
          'file for exactly this reason:', None)],
    ])
    code(s, 8.8, [
        'MIN_AREA = 2000       # Minimum contour area (pixels)',
        'MAX_AREA = 6000       # Maximum contour area (pixels)',
        'TARGET_ASPECT = 1.0   # Expected width/height ratio (Square = 1.0)',
        'ASPECT_TOLERANCE = 0.25',
    ], size=12.5)
    bullet(s, 12.6, [
        ('MIN_AREA', 'c'), ('  rejects specks and far-away parts', None),
    ], h=1.4)
    bullet(s, 14.0, [
        ('MAX_AREA', 'c'), ('  rejects parts that are far too big to be the same part', None),
    ], h=1.4)
    bullet(s, 15.4, [
        ('TARGET_ASPECT', 'c'), ('  1.0 because the part is meant to be square', None),
    ], h=1.4)
    bullet(s, 16.8, [
        ('ASPECT_TOLERANCE', 'c'), ('  how far off square is still acceptable', None),
    ], h=1.4)
    note(s, 17.9, [
        [('They look like measurements of one specific part — and that is the '
          'problem. They describe the parts you had, not the parts you are '
          'supposed to make; derive them from the specification, not a sample.', None)],
    ], h=2.0)

    # ======================================================== 23. STEP 1 ===
    s = add()
    title(s, [('Step 1', None)])
    body(s, Y_BODY_STD, [
        [('Three imports, and for once every one of them is used:', None)],
    ])
    code(s, 7.4, [
        'import cv2',
        'import numpy as np',
        'import time',
    ], size=15.0)
    body(s, 10.4, [
        [('cv2', 'c'), (' for the camera, colour, contours and drawing. ', None),
         ('numpy', 'c'), (' for the colour bounds and the kernel. ', None),
         ('time', 'c'), (' for the three waits in the robot setup.', None)],
    ])
    note(s, 13.0, [
        [('This is the smallest import block in the module so far. Project 3 needed '
          'os and threading, Project 4 needed math and mediapipe, and this one needs '
          'three. If an import is missing you will find out immediately with a '
          'NameError naming it, which makes this the easiest project in the module '
          'to get running.', None)],
    ], h=2.8)

    # ======================================================== 24. STEP 2 ===
    s = add()
    title(s, [('Step 2', None)])
    body(s, Y_BODY_STD, [
        [('The arm import, unchanged from every project before it:', None)],
    ])
    code(s, 6.4, [
        'from pymycobot.mycobot280 import MyCobot280',
    ], size=15.0)
    body(s, 8.4, [
        [('And this time it genuinely may go unused, because the robot setup is '
          'inside a ', None), ('try', 'c'), (' that carries on when it fails.', None)],
    ])
    note(s, 10.8, [
        [('Import the name even if you are working without hardware. The import is '
          'harmless when there is no arm, and it means the one line you would have '
          'to change to enable the robot is already correct.', None)],
    ], h=2.4)

    # ============================================ 25. GETTING IT ONTO THE ARM ===
    s = add()
    title(s, [('Copy it, and start it once', None)])
    body(s, Y_BODY_STD, [
        [('One file, and this time you do not need the arm at all:', None)],
    ])
    command(s, 6.8, SCP)
    command(s, 9.2, RUN)
    body(s, 11.6, [
        [('Run it now, with every TODO still empty. It fails, but not where you '
          'would expect:', None)],
    ])
    code(s, 13.2, [
        'Robot ready.',
        'Traceback (most recent call last):',
        '  File "M2-P5-Starter.py", line 51, in <module>',
        '    LOWER_GREEN = np.array([35, 70, 70])',
        "NameError: name 'np' is not defined",
    ], size=12.5)
    note(s, 17.3, [
        [('Read those two lines together — the lesson. It prints ', None),
         ('Robot ready.', 'c'),
         (' and there is no robot: the empty TODO removed the connection code, '
          'so the ', None),
         ('try', 'c'), (' had nothing to fail on. Success means no exception.', None)],
    ], h=3.0)

    # ======================================================== 26. STEP 3 ===
    s = add()
    title(s, [('Step 3', None)])
    body(s, Y_BODY_STD, [
        [('Connect, wait, power on, wait. The two sleeps are not padding:', None)],
    ])
    code(s, 7.4, [
        '    print("Connecting to myCobot280...")',
        "    mc = MyCobot280('/dev/ttyAMA0', 1000000)",
        '    time.sleep(0.5)',
        '    mc.power_on()',
        '    time.sleep(0.5)',
    ], size=14.0)
    body(s, 12.0, [
        [('The first wait is for the arm to finish booting after the serial port '
          'opens. The second is after ', None), ('power_on()', 'c'), (', which is a '
          'command with real work to do behind it.', None)],
    ])
    note(s, 14.6, [
        [('If any of this raises, the ', None), ('except', 'c'), (' catches it and '
          'the program continues. That means a genuinely broken arm is not a fatal '
          'error here — so if your camera window never appears, look for a message '
          'about the robot that you scrolled past without reading.', None)],
    ], h=2.8)

    # ======================================================== 27. STEP 4 ===
    s = add()
    title(s, [('Step 4', None)])
    body(s, Y_BODY_STD, [
        [('Fold the arm out of the way and leave it there:', None)],
    ])
    code(s, 6.8, [
        '    home_pos = [0, 45, -90, -45, 0, 0]',
        '    mc.send_angles(home_pos, 50)',
        '    time.sleep(2.0)',
    ], size=15.0)
    callout(s, 9.4, [
        ('Two things are new here. ', None),
        ('send_angles', 'c'),
        (' takes six joint angles, where Project 4 used ', None),
        ('send_coords', 'c'),
        (' and took millimetres — same robot, two completely different ways of '
         'telling it where to go. And the position is a list of six numbers, not a '
         'single coordinate.', None),
    ], h=2.44)
    body(s, 13.4, [
        [('The two second wait afterwards is not a guess. It is roughly how long the '
          'arm takes to travel there, and the program does not do anything else '
          'until it has arrived.', None)],
    ])
    note(s, 15.6, [
        [('Once this has run, the arm is not used again anywhere in Project 5. The '
          'inspection is entirely camera work. It is a slightly odd thing to write, '
          'and it is worth being able to explain why it is there: it puts the arm in '
          'a known safe position at the start of every run, which is a habit worth '
          'keeping in code that does move a robot later.', None)],
    ], h=3.0)

    # ======================================================== 28. STEP 5 ===
    s = add()
    title(s, [('Step 5', None)])
    body(s, Y_BODY_STD, [
        [('The whole ROI function, signature included. Sixteen lines, and most of '
          'them are arithmetic about the middle:', None)],
    ])
    code(s, 6.6, [
        'def calculate_roi_bounds():',
        '    y1, y2, x1, x2 = BASE_ROI',
        '    center_x = (x1 + x2) // 2',
        '    center_y = (y1 + y2) // 2',
        '    width = (x2 - x1) * ROI_SCALE',
        '    height = (y2 - y1) * ROI_SCALE',
        '    new_x1 = int(center_x - width // 2 + ROI_OFFSET_X)',
        '    new_x2 = int(center_x + width // 2 + ROI_OFFSET_X)',
        '    new_y1 = int(center_y - height // 2 + ROI_OFFSET_Y)',
        '    new_y2 = int(center_y + height // 2 + ROI_OFFSET_Y)',
        '    new_x1 = max(0, min(new_x1, 640))',
        '    new_x2 = max(0, min(new_x2, 640))',
        '    new_y1 = max(0, min(new_y1, 480))',
        '    new_y2 = max(0, min(new_y2, 480))',
        '    return [new_y1, new_y2, new_x1, new_x2]',
    ], size=11.0)
    note(s, 14.4, [
        [('Six steps hidden in there: unpack, find the centre, scale the size, apply '
          'the offset, clamp to the frame, return. The ', None),
         ('//', 'c'), (' is floor division, so a width of 239 becomes 119 rather '
          'than 120 — which is why the box can come out a pixel smaller than you '
          'asked for, and why nobody minds.', None)],
    ], h=2.6)

    # ======================================================== 29. STEP 6 ===
    s = add()
    title(s, [('Step 6', None)])
    body(s, Y_BODY_STD, [
        [('This one is already done for you. Look closely at what your file '
          'already contains:', None)],
    ])
    code(s, 8.0, [
        'def inspect_part(roi_frame):',
        '    """',
        '    Analyzes an item within the ROI frame.',
        '    Returns: status (str), reason (str), color_overlay (image)',
        '    """',
    ], size=13.0)
    body(s, 12.6, [
        [('The signature and the docstring are already in the starter file, so '
          'there is nothing to type for this TODO. The real work is the five steps '
          'inside it, and they are the next five slides.', None)],
    ])
    callout(s, 15.4, [
        ('Read that docstring carefully, because it tells you the contract: a '
         'status word, a reason, and an image. Every single ', None),
        ('return', 'c'),
        (' in this function must produce all three, which is why each one ends with ', None),
        ('mask', 'c'),
        (' even the ones that bail out early.', None),
    ], h=2.44)

    # ======================================================== 30. STEP 7 ===
    s = add()
    title(s, [('Step 7', None)])
    body(s, Y_BODY_STD, [
        [('One line: blue-green-red into hue-saturation-value.', None)],
    ])
    code(s, 6.4, [
        '    hsv = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2HSV)',
    ], size=15.0)
    body(s, 8.6, [
        [('It is the same colour conversion as Project 4, with a different answer. '
          'There the point was to give MediaPipe the order it expected; here the '
          'point is the space itself.', None)],
    ])
    note(s, 11.4, [
        [('Notice this converts ', None), ('roi_frame', 'c'), (', not ', None),
         ('frame', 'c'), ('. Only the part inside the inspection zone is ever '
          'converted, measured or judged. Everything outside it is ignored — which '
          'is what makes the zone adjustable at all.', None)],
    ], h=2.6)

    # ======================================================== 31. STEP 8 ===
    s = add()
    title(s, [('Step 8', None)])
    body(s, Y_BODY_STD, [
        [('The threshold, and the first moment this program actually decides '
          'anything:', None)],
    ])
    code(s, 7.4, [
        '    mask = cv2.inRange(hsv, LOWER_GREEN, UPPER_GREEN)',
    ], size=15.0)
    body(s, 9.6, [
        [('One picture in, one picture out. Everything green becomes white, '
          'everything else becomes black, and the rest of the function works on the '
          'black and white version rather than on the original.', None)],
    ])
    note(s, 12.4, [
        [('This is the line to change when the scanner accepts the wrong thing or '
          'rejects the right thing. Look at the mask window while you change it: you '
          'are adjusting which pixels count, and you can see exactly which ones you '
          'just gained or lost.', None)],
    ], h=2.6)

    # ======================================================== 32. STEP 9 ===
    s = add()
    title(s, [('Step 9', None)])
    body(s, Y_BODY_STD, [
        [('Clean the mask before trusting it:', None)],
    ])
    code(s, 6.4, [
        '    kernel = np.ones((5, 5), np.uint8)',
        '    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)',
    ], size=14.0)
    body(s, 9.6, [
        [('The kernel is 25 ones in a square. ', None), ('np.uint8', 'c'),
         (' is required — OpenCV will not accept a different type here, and it is '
          'the reason this line cannot simply be a Python list.', None)],
    ])
    note(s, 12.2, [
        [('Keep an eye on the small parts while you work on this. If the mask '
          'loses something, the opening took it, and no amount of adjusting the '
          'colour range will bring it back. The Mask View window is where you catch '
          'that immediately.', None)],
    ], h=2.6)

    # ======================================================= 33. STEP 10 ===
    s = add()
    title(s, [('Step 10', None)])
    body(s, Y_BODY_STD, [
        [('Turn the white blobs into outlines:', None)],
    ])
    code(s, 6.4, [
        '    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)',
    ], size=12.5)
    body(s, 8.6, [
        [('The mask is modified in place by this call, which is a long-standing '
          'OpenCV behaviour and worth knowing about: the ', None), ('mask', 'c'),
         (' you get back afterwards is not the mask you passed in.', None)],
    ])
    note(s, 11.6, [
        [('That is not a problem here, because the only use of ', None),
         ('mask', 'c'), (' afterwards is to display it in the second window. But if '
          'you ever need the original mask back, take a copy before calling this.', None)],
    ], h=2.4)

    # ======================================================= 34. STEP 11 ===
    s = add()
    title(s, [('Step 11', None)])
    body(s, Y_BODY_STD, [
        [('Pick the part out of whatever else was in the zone:', None)],
    ])
    code(s, 6.8, [
        '    largest_contour = max(contours, key=cv2.contourArea)',
        '    area = cv2.contourArea(largest_contour)',
    ], size=14.0)
    body(s, 10.0, [
        [('This is the assumption of the whole project in two lines. It works '
          'beautifully on a clean background and fails quietly on a cluttered one.', None)],
    ])
    note(s, 12.4, [
        [('If you want to see how much it depends on the assumption, put two parts '
          'in the zone at once. Only one is measured and the other is invisible to '
          'the program. The mask window will show you both, which is the quickest '
          'way to prove that "largest" is a policy rather than a measurement.', None)],
    ], h=2.8)

    # ======================================================= 35. STEP 12 ===
    s = add()
    title(s, [('Step 12', None)])
    body(s, Y_BODY_STD, [
        [('Measure the shape:', None)],
    ])
    code(s, 6.4, [
        '    x, y, w, h = cv2.boundingRect(largest_contour)',
        '    aspect_ratio = float(w) / h',
    ], size=15.0)
    body(s, 9.4, [
        [('The x, y and h are measured and then not used. Only w, h and the ratio '
          'matter here — the rectangle is a local measurement, not the one drawn on '
          'screen. The box you see comes from the ROI, not from this.', None)],
    ])
    note(s, 12.2, [
        [('That is a small thing worth noticing: two different rectangles are in '
          'play in this program. ', None),
         ('boundingRect', 'c'), (' describes the part, and it never leaves the '
          'function. The rectangle drawn on the picture later is the inspection '
          'zone, which is fixed. Keep them apart in your head or the debugging will '
          'confuse you.', None)],
    ], h=2.8)

    # ======================================================= 36. STEP 13 ===
    s = add()
    title(s, [('Step 13', None)])
    body(s, Y_BODY_STD, [
        [('The verdict, and the end of the function:', None)],
    ])
    code(s, 6.4, [
        '    if area < MIN_AREA:',
        '        return "FAIL", f"Too Small ({int(area)}px)", mask',
        '    if area > MAX_AREA:',
        '        return "FAIL", f"Too Large ({int(area)}px)", mask',
        '    if abs(aspect_ratio - TARGET_ASPECT) > ASPECT_TOLERANCE:',
        '        return "FAIL", f"Shape Defect (Ratio: {aspect_ratio:.2f})", mask',
        '',
        '    return "PASS", f"Good Part ({int(area)}px)", mask',
    ], size=12.0)
    note(s, 13.4, [
        [('The f-strings are doing real work here. Each message carries the number '
          'that caused the verdict, which is what turns "no" into "no, and here is '
          'by how much". Note the rounding on the ratio: two decimal places is '
          'enough to tell a 1.62 defect from a 1.05 pass, without a number too long '
          'to read from across a bench.', None)],
    ], h=2.8)

    # ======================================================= 37. STEP 14 ===
    s = add()
    title(s, [('Step 14', None)])
    body(s, Y_BODY_STD, [
        [('The camera, identical to Projects 3 and 4:', None)],
    ])
    code(s, 6.4, [
        'cap = cv2.VideoCapture(0)',
        'cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)',
        'cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)',
    ], size=13.0)
    body(s, 9.8, [
        [('This time the resolution is not a suggestion. ', None), ('BASE_ROI', 'c'),
         (' is described in the comment as coordinates on a 640 by 480 frame, and '
          'the clamp in ', None), ('calculate_roi_bounds', 'c'), (' hard-codes 640 '
          'and 480 for the same reason.', None)],
    ])
    note(s, 12.8, [
        [('If the camera gives you a different size, the ROI will be in the wrong '
          'place and the clamp will be wrong too, and neither will complain. This '
          'is the first project in the module where the frame size is load-bearing, '
          'so it is worth printing ', None),
         ('frame.shape', 'c'), (' once to confirm what you are actually getting.', None)],
    ], h=2.8)

    # ======================================================= 38. STEP 15 ===
    s = add()
    title(s, [('Step 15', None)])
    body(s, Y_BODY_STD, [
        [('Read the frame:', None)],
    ])
    code(s, 6.4, [
        '        ret, frame = cap.read()',
        '        if not ret:',
        '            break',
    ], size=14.0)
    body(s, 9.4, [
        [('Almost identical to Project 4, with one deliberate difference. There '
          'the line was ', None), ('success, frame', 'c'), (' and the body was ', None),
         ('continue', 'c'), ('; here it is ', None), ('ret, frame', 'c'),
         (' and the body is ', None), ('break', 'c'), ('.', None)],
    ])
    note(s, 12.4, [
        [('Both are correct, and the difference is about what you want to happen. ', None),
         ('continue', 'c'), (' says this frame is bad, try the next one — right for '
          'a program where frames arrive at 30 a second and one bad frame means '
          'nothing. ', None),
         ('break', 'c'), (' says the camera is finished, stop the program — right '
          'when there is nothing to read and waiting will not help. A dropped frame '
          'and a closed camera look identical from inside the loop, and this project '
          'decides to treat both as the end.', None)],
    ], h=3.0)

    # ======================================================= 39. STEP 16 ===
    s = add()
    title(s, [('Step 16', None)])
    body(s, Y_BODY_STD, [
        [('Build the zone and cut the part out of the picture:', None)],
    ])
    code(s, 7.4, [
        '        ROI_BOUNDS = calculate_roi_bounds()',
        '        y1, y2, x1, x2 = ROI_BOUNDS',
        '        roi = frame[y1:y2, x1:x2]',
    ], size=14.0)
    body(s, 11.4, [
        [('Three steps: get the bounds, unpack them, slice. The result is a NumPy '
          'array, not an OpenCV image object — which does not matter, because every '
          'function it is about to meet takes a NumPy array.', None)],
    ])
    note(s, 14.2, [
        [('This runs inside the loop, every frame, even though the answer never '
          'changes unless you edit the constants. It is a function call per frame '
          'doing arithmetic on four numbers — utterly negligible, and it means you '
          'can move the zone without restarting the program.', None)],
    ], h=2.6)

    # ======================================================= 40. STEP 17 ===
    s = add()
    title(s, [('Step 17', None)])
    body(s, Y_BODY_STD, [
        [('One line, and it is the whole point of the project:', None)],
    ])
    code(s, 7.4, [
        '        status, reason, mask = inspect_part(roi)',
    ], size=15.0)
    body(s, 9.6, [
        [('Three values back, unpacked into names that describe what they are. '
          'Compare that with Project 4, where the model returned nested lists you '
          'had to dig through — a function that hands back three well-named values '
          'is doing you a real favour.', None)],
    ])
    note(s, 12.6, [
        [('Worth being precise about what the mask actually is. It is not a picture '
          'of the outlines — it is the cleaned mask, the one morphology produced and ', None),
         ('findContours', 'c'),
         (' read. Since OpenCV 3.2 that call does not modify the mask handed to it, so '
          'what comes back is exactly what went in: the same image the decisions were '
          'made from. That is why it is the one worth displaying.', None)],
    ], h=3.0)

    # ============================================== 41. STEP 18 (PART ONE) ===
    s = add()
    title(s, [('Step 18', None)])
    body(s, Y_BODY_STD, [
        [('The colour was already chosen for you, one line above this TODO:', None)],
    ])
    code(s, 6.8, [
        '        status_color = (0, 255, 0) if status == "PASS" else (0, 0, 255)',
    ], size=11.5)
    code(s, 9.4, [
        '        cv2.rectangle(frame, (x1, y1), (x2, y2), status_color, 2)',
        '        cv2.putText(frame, "INSPECTION ZONE", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)',
    ], size=9.6)
    body(s, 12.4, [
        [('The rectangle uses the ROI bounds from Step 16, not the bounding '
          'rectangle from Step 12. It is showing you where the scanner is looking, '
          'which is what you want while tuning the zone.', None)],
    ])
    note(s, 15.0, [
        [('One colour value, decided once, used for the rectangle and the label. '
          'If you ever find yourself computing the colour in two places, that is '
          'the moment to notice you should have kept the line that was written for '
          'you.', None)],
    ], h=2.6)

    # ============================================ 42. STEP 18 (PART TWO) ===
    s = add()
    title(s, [('Step 18, continued', None)])
    body(s, Y_BODY_STD, [
        [('And the telemetry, anchored to the bottom of the picture:', None)],
    ])
    code(s, 6.8, [
        '        h, w = frame.shape[:2]',
        '        cv2.putText(frame, f"STATUS: {status}", (20, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, status_color, 3)',
        '        cv2.putText(frame, f"REASON: {reason}", (20, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)',
    ], size=9.4)
    body(s, 11.4, [
        [('Those last two lines are the longest in the project, which is why they '
          'are set small here. In your file they are 112 and 108 characters, one '
          'line each, and you should type them exactly as they are.', None)],
        [('Note ', None), ('frame.shape[:2]', 'c'), (' rather than the full shape — '
          'a shorter way of saying "height and width, ignore the channels".', None)],
    ])
    note(s, 14.6, [
        [('Text at 1.0 scale with thickness 3 for the verdict, and 0.6 with '
          'thickness 2 for the reason. That is not decoration: the status is the '
          'answer and has to be readable from across the bench, while the reason is '
          'detail for whoever walks over to look. Two different sizes, two '
          'different jobs.', None)],
    ], h=2.8)

    # ======================================================= 43. STEP 19 ===
    s = add()
    title(s, [('Step 19', None)])
    body(s, Y_BODY_STD, [
        [('Two windows, and the last TODO:', None)],
    ])
    code(s, 6.4, [
        '        cv2.imshow("Mission 02 - Project 05: QC Scanner", frame)',
        '        cv2.imshow("Mask View", mask)',
    ], size=12.5)
    body(s, 9.2, [
        [('The camera view for the human, the mask for you. Then the exit check, '
          'also already written:', None)],
    ])
    code(s, 11.6, [
        "        if cv2.waitKey(1) & 0xFF == ord('q'):",
        '            break',
    ], size=12.5)
    body(s, 13.6, [
        [('And the very last thing in the file:', None)],
    ])
    code(s, 15.2, [
        'finally:',
        '    cap.release()',
        '    cv2.destroyAllWindows()',
    ], size=12.5)
    note(s, 17.9, [
        [('No ', None),
         ('mc.release_all_servos()', 'c'),
         (' here — fine, the arm never moves, but the next project that moves '
          'the arm will want it back.', None)],
    ], h=2.4)

    # ================================================= 44. READING THE WINDOWS ===
    s = add()
    title(s, [('Reading the two windows', None)])
    body(s, Y_BODY_STD, [
        [('When something is wrong, look in this order:', None)],
    ])
    bullet(s, 8.0, [
        ('The mask.', 'b'), ('  White where the program thinks there is a part. If '
         'the part is missing here, the problem is the colour range or the opening '
         '— nothing downstream has even seen it yet.', None),
    ], h=2.3)
    bullet(s, 10.3, [
        ('The inspection box.', 'b'), ('  Green means PASS, red means FAIL. This '
         'colour is the verdict, so it is the fastest read on the screen.', None),
    ], h=2.3)
    bullet(s, 12.6, [
        ('The reason line.', 'b'), ('  This is the fault, named in words with a '
         'number attached. Read it before changing anything.', None),
    ], h=2.3)
    bullet(s, 14.9, [
        ('The zone position.', 'b'), ('  If the part is half in and half out of '
         'the box, retune the offsets before you touch a single threshold.', None),
    ], h=2.3)
    note(s, 17.6, [
        [('The order runs from raw pixels to final verdict, which is the order the '
          'data flows in. Working backwards from the verdict is what turns a vague '
          '"it does not work" into a specific fault.', None)],
    ], h=2.2)

    # ============================================ 45. BEFORE YOU TUNE ANYTHING ===
    s = add()
    title(s, [('Before you tune anything', None)])
    table(s, 4.2, [
        ['What you see', 'What it means', 'What to do'],
        ['No Item / Wrong Color, part present',
         'Hue range wrong, or opening ate it',
         'Watch the mask, then adjust the range'],
        ['Too Small on a normal part',
         'MIN_AREA too high, or it is too far away',
         'Check the distance before the number'],
        ['Too Large on a normal part',
         'MAX_AREA too low',
         'Compare against the real spec'],
        ['Shape Defect on a square part',
         'Part is rotated, or h is very small',
         'Axis-aligned box cannot see rotation'],
        ['Flashing between PASS and FAIL',
         'Lighting is changing between frames',
         'Fix the lighting, do not widen ranges'],
        ['Reason never matches the fault',
         'A step earlier removed the evidence',
         'Read the mask window first'],
        ['Robot warning in the terminal',
         'No arm — and it does not matter here',
         'Expected on a laptop, carry on'],
    ], [7.0, 7.2, 9.93], row_h=1.12, head_h=1.25, size=12.5)
    note(s, 16.6, [
        [('The last row is not a fault at all. Everything else on this table is, and '
          'each one points at a single step. "Reason never matches the fault" is the '
          'row worth memorising, because it is the one that saves the most time.', None)],
    ], h=2.4)

    # ================================================== 46. THRESHOLD COSTS ===
    s = add()
    title(s, [('What the numbers actually cost', None)])
    body(s, Y_BODY_STD, [
        [('Five numbers decide everything, and every one of them is a trade rather '
          'than a setting to maximise:', None)],
    ])
    num_item(s, 9.0, 1, '35 to 85, the hue range',
             [('wider accepts more shades of green, including olive and teal', None)], h=1.9)
    num_item(s, 10.9, 2, '5 by 5, the kernel',
             [('bigger removes more noise, and more real parts with it', None)], h=1.9)
    num_item(s, 12.8, 3, '2000, the minimum area',
             [('higher rejects more, including parts that are merely further away', None)], h=1.9)
    num_item(s, 14.7, 4, '6000, the maximum area',
             [('lower starts rejecting parts that are closer than expected', None)], h=1.9)
    num_item(s, 16.6, 5, '0.25, the aspect tolerance',
             [('tighter means squarer; too tight and a good part rotates into a fail', None)], h=1.9)
    note(s, 18.4, [
        [('Same shape every time: too tight rejects good parts, too loose accepts '
          'bad ones. A decision, not a number to optimise.', None)],
    ], h=2.4)

    # ================================================ 47. EXTENSION DIVIDER ===
    s = add(0, master=1)
    _, tf = textbox(s, X_L, 15.41, W_WIDE, 4.28, anchor=3)
    para(tf, True, 'Challenge', F_TITLE, SZ_DIVIDER, YELLOW, line_spacing=1.0)
    para(tf, False, 'YOUR MOVE', F_TITLE, SZ_DIVIDER, WHITE, line_spacing=1.0)

    # ======================================================== 48. THE BRIEF ===
    s = add(0, master=1)
    s.shapes.add_picture(art['image2.png'], Cm(17.39), Cm(3.81), Cm(9.36), Cm(9.54))
    title(s, [('The Brief', None)], ext=True)
    body(s, Y_BODY_EXT, [
        [('Build a scanner that judges a part and explains itself.', None)],
        [('Not "does it detect green" — that is a mechanism. The deliverable is a '
          'verdict, a reason, and a mask somebody can check your work with.', None)],
        [('The arm is connected, powered and folded, and then left alone. That is '
          'deliberate, and you should be able to say why.', None)],
    ], ext=True)
    check_item(s, 13.6, [
        ('Good parts report PASS with a plausible area.', None),
    ], h=1.8)
    check_item(s, 15.4, [
        ('Bad parts fail with a reason that names the actual fault.', None),
    ], h=1.8)
    check_item(s, 17.2, [
        ('The mask window shows the part, and only the part.', None),
    ], h=1.8)
    check_item(s, 19.0, [
        ('The zone can be retuned by editing three constants.', None),
    ], h=1.4)

    # ======================================================= 49. THE MISSION ===
    s = add()
    title(s, [('YOUR MISSION: ', None), ('RIGHT FOR THE WRONG REASON COUNTS AS WRONG', None)])
    body(s, Y_BODY_STD, [
        [('Five things to get right before you touch a threshold:', None)],
    ])
    num_item(s, 7.4, 1, 'A good part reports PASS',
             [('Area between 2000 and 6000, ratio within 0.25 of 1.0', None)], h=2.0)
    num_item(s, 9.4, 2, 'A part that is too small says Too Small',
             [('Not No Item. If the opening ate it, fix the kernel', None)], h=2.0)
    num_item(s, 11.4, 3, 'The wrong colour says No Item',
             [('And the mask is empty, which proves it', None)], h=2.0)
    num_item(s, 13.4, 4, 'Nothing outside the box is judged',
             [('Move the zone with three constants, not arithmetic', None)], h=2.0)
    num_item(s, 15.4, 5, 'Every reason carries a number',
             [('The area in pixels, or the ratio to two places', None)], h=2.0)
    callout(s, 17.6, [
        ('Point 2 is the one that separates a scanner from a guessing machine. A '
         'verdict is only useful if it names the real fault, and the fastest way to '
         'name the real fault is to check that the evidence was still there when the '
         'verdict was reached.', None),
    ], h=2.2)

    # ======================================================== 50. DATA LOG ===
    s = add()
    title(s, [('YOUR DATA LOG', None)])
    body(s, 4.0, [
        [('Measure before you adjust. Ten rows, and every cell is an observation.', None)],
    ])
    table(s, 6.0, [
        ['What you put in the zone', 'Mask looks right?', 'Status', 'Reason', 'Area / ratio'],
        ['Good part, well lit', '______', '______', '________________', '__________'],
        ['Good part, dimmer', '______', '______', '________________', '__________'],
        ['Part slightly too small', '______', '______', '________________', '__________'],
        ['Clearly too small', '______', '______', '________________', '__________'],
        ['Wrong colour', '______', '______', '________________', '__________'],
        ['Square part, rotated', '______', '______', '________________', '__________'],
        ['Nothing at all', '______', '______', '________________', '__________'],
        ['Two parts at once', '______', '______', '________________', '__________'],
        ['Hand steadying the part', '______', '______', '________________', '__________'],
    ], [6.2, 3.3, 2.8, 6.3, 5.53], row_h=1.02, head_h=1.3, size=11.5)
    callout(s, 17.3, [
        ('Rows 5, 6 and 7 are where the interesting faults live. If "clearly too '
         'small" and "slightly too small" both report ', None), ('No Item', 'c'),
        (', the opening is removing them before the rules ever run, and no threshold '
         'you change afterwards will make them appear.', None),
    ], h=2.4)

    # ============================================= 51. DEFINITION OF DONE ===
    s = add()
    title(s, [('DEFINITION OF DONE', None)])
    body(s, 4.2, [
        [('Tick every line. A scanner that opens two windows is not finished.', None)],
    ])
    check_item(s, 6.8, [
        ('All 19 TODOs filled in, with the comments copied as written.', None),
    ], h=1.9)
    check_item(s, 8.7, [
        ('Ten data log rows completed from observation, not expectation.', None),
    ], h=1.9)
    check_item(s, 10.6, [
        ('Every fault message reproduced at least once, deliberately.', None),
    ], h=1.9)
    check_item(s, 12.5, [
        ('The mask window never shows anything outside the zone.', None),
    ], h=1.9)
    check_item(s, 14.4, [
        ('All five tuning numbers explained in one sentence each.', None),
    ], h=1.9)
    check_item(s, 16.3, [
        ('You can say why the arm is connected but never used.', None),
    ], h=1.9)
    note(s, 18.6, [
        [('The third line is the one people skip, and it is the one that proves the '
          'scanner works. A program that only ever reports PASS has not been '
          'tested. Deliberately feed it a blue part, a bolt, and your own hand.', None)],
    ], h=2.0)

    # ==================================================== 52. GO FURTHER ===
    s = add()
    title(s, [('GO FURTHER', None)])
    body(s, Y_BODY_STD, [
        [('Each of these is a small change to code you have already written.', None)],
    ])
    bullet(s, 7.4, [
        ('Stop assuming the biggest blob.', 'b'), ('  Sort the contours by area and '
         'judge the second largest, or the one nearest the centre of the zone.', None),
    ], h=2.3)
    bullet(s, 9.7, [
        ('Inspect every part, not one.', 'b'), ('  Split the zone into a grid, run '
         'the same function on each cell, and list what you found.', None),
    ], h=2.3)
    bullet(s, 12.0, [
        ('Stop rotating into failure.', 'b'), ('  Replace boundingRect with '
         'minAreaRect, which returns a rotated box, and compare the four corner '
         'lengths instead of one ratio.', None),
    ], h=2.3)
    bullet(s, 14.3, [
        ('Inspect a second colour.', 'b'), ('  Copy the pipeline, change the two '
         'bounds, and prove that red needs two ranges because of the hue wrap-around.', None),
    ], h=2.3)
    bullet(s, 16.6, [
        ('Log the results.', 'b'), ('  Append each verdict to a file with a '
         'timestamp. Then you have data instead of opinions.', None),
    ], h=2.3)
    note(s, 19.2, [
        [('The third is the most valuable: an axis-aligned box cannot tell a square '
          'from a rotated square, and no amount of tolerance tuning fixes that.', None)],
    ], h=2.0)

    # ==================================================== 53. DEBRIEF ===
    s = add(0, master=1)
    _, tf = textbox(s, X_L, 14.0, W_WIDE, 5.5, anchor=3)
    para(tf, True, 'MISSION', F_TITLE, SZ_DIVIDER, YELLOW, line_spacing=1.0)
    para(tf, False, 'DEBRIEF', F_TITLE, SZ_DIVIDER, WHITE, line_spacing=1.0)

    OUTDIR = os.path.dirname(OUT)
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    # ------------------------------------------------------- layout pass ---
    tight = pack_deck(prs, gap=0.30, limit=Y_BOTTOM)
    if tight:
        print('OVERFLOW:', tight)
    prs.save(OUT)
    print('wrote %s with %d slides' % (OUT, len(prs.slides._sldIdLst)))


if __name__ == '__main__':
    build()
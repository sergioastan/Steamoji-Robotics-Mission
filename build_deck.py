# -*- coding: utf-8 -*-
"""Build Slides/M2/myCobot_01.pptx -- 'Seeing Shapes' (M2-P1).

Rebuilds the deck from the theme/layouts of the reference sample
Slides/myCobot_08.pptx, but teaches the shape-detection pipeline that
students complete in M2/M2-P1-Starter.py.

Every code snippet below is copied verbatim from M2/M2-P1-Base.py.
"""

import os
import shutil
import zipfile

from pptx import Presentation
from pptx.util import Cm, Pt
from pptx.enum.shapes import MSO_SHAPE

from build_deck_theme import (
    BG, PANEL, PANEL2, ROW, YELLOW, WHITE,
    F_TITLE, F_BODY, F_CODE,
    X_L, X_ITEM, W_BODY, W_WIDE, W_ITEM,
    Y_TITLE_STD, Y_TITLE_EXT, Y_BODY_STD, Y_BODY_EXT,
    SZ_BODY, SZ_DIVIDER,
    textbox, para, shape, title, body, note, code, command,
    callout, bullet, num_item, check_item, question_item, table,
    Y_BOTTOM, pack_deck,
)

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'Slides', 'myCobot_08.pptx')
OUT = os.path.join(HERE, 'Slides', 'M2', 'myCobot_01.pptx')
TMP = os.path.join(HERE, 'tmp_media')

STARTER = 'M2-P1-Starter.py'
SCP = f'scp {STARTER} er@192.168.1.149:Documents'
RUN = f'python {STARTER}'

# The decision chain, verbatim from M2-P1-Base.py
CHAIN = [
    'object_type = "Unknown"',
    '',
    'if extent < 0.65 or num_vertices == 3:',
    '    object_type = "Triangle"',
    'elif extent >= 0.82 and aspect_ratio >= 0.78:',
    '    object_type = "Square"',
    'elif circularity >= 0.85 or (0.68 <= extent < 0.82 and aspect_ratio >= 0.80):',
    '    object_type = "Circle"',
    'else:',
    '    object_type = "Rectangle"',
]

# Metrics chain, verbatim
METRICS = [
    'extent = float(area) / rect_area',
    'circularity = (4 * np.pi * area) / (peri ** 2)',
    'aspect_ratio = float(min(w, h)) / max(w, h) if max(w, h) > 0 else 0',
]


def media():
    """Pull the generic title/closing artwork out of the reference deck."""
    os.makedirs(TMP, exist_ok=True)
    z = zipfile.ZipFile(REF)
    for name in ('image1.png', 'image2.png', 'image5.png', 'image6.png'):
        with z.open('ppt/media/' + name) as src, \
                open(os.path.join(TMP, name), 'wb') as dst:
            shutil.copyfileobj(src, dst)
    z.close()
    return {n: os.path.join(TMP, n)
            for n in ('image1.png', 'image2.png', 'image5.png', 'image6.png')}


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
    para(tf, True, 'Project 1', F_TITLE, SZ_DIVIDER, YELLOW, line_spacing=1.0)
    para(tf, False, 'Seeing Shapes', F_TITLE, SZ_DIVIDER, WHITE, line_spacing=1.0)

    # ====================================================== 3. WHAT’S NEXT ===
    s = add()
    title(s, [('What’s ', None), ('next', None), ('?', None)])
    body(s, Y_BODY_STD, [
        'In Module 1 you built a program that could tell red from yellow. '
        'That worked because every colour has a number attached to it, so the '
        'computer could look up a range and make a decision.',
        None,
        'This project asks a much harder question. Nobody tells the computer '
        'what colour a block is. It has to work out the shape from the picture '
        'alone — triangle, square, circle or rectangle — and then put a name on '
        'screen.',
        None,
        [('The starter file already contains all of the difficult mathematics. '
          'Your job is to supply the missing ', None),
         ('measurements', 'b'),
         (' and the ', None),
         ('decision', 'b'),
         (' that turns them into a single word.', None)],
    ])
    note(s, 12.6, [
        ('Two windows will open when the program runs: ', None),
        ('Shape Detection', 'c'),
        (' with your label drawn on it, and ', None),
        ('Threshold View (Binary)', 'c'),
        (' with the cleaned-up black and white picture the computer actually '
         'sees. Keep both open. Most of your debugging happens in the second '
         'one.', None)], h=3.0)

    # ================================================== 4. COLOUR -> SHAPE ===
    s = add()
    title(s, [('From colour to shape', None)])
    body(s, Y_BODY_STD, [
        'Colour detection asks a question about a pixel: which numbers fall '
        'inside a range? Shape detection asks a question about an outline: how '
        'far around is it, and how much of its own box does it fill?',
        None,
        'That means hue, saturation and value are no longer needed at all. We '
        'throw the colour away on purpose and keep only light and dark.',
        None,
        [('This is the first project where OpenCV does the seeing and you do '
          'the deciding. Every number that ends up on screen is a number you '
          'wrote.', 'b')],
    ])

    # ======================================================== 5. PIPELINE ===
    s = add()
    title(s, [('The ', None), ('pipeline', None)])
    body(s, Y_BODY_STD, [
        'Five lines turn a camera frame into a list of candidate shapes. You '
        'will not change any of these five lines — they are already written for '
        'you — but you need to know what each one hands to the next.',
    ])
    steps = [
        ('Greyscale', 'One brightness number per pixel instead of three colour numbers.'),
        ('Blur', 'Smooths sensor noise so the outline is not full of holes.'),
        ('Threshold', 'Turns everything darker than 110 white, everything else black.'),
        ('Close', 'Darns small holes so one shape stays one shape.'),
        ('Contours', 'Traces each outline and hands you a list of them.'),
    ]
    for i, (h, b) in enumerate(steps):
        num_item(s, 5.75 + i * 2.42, i + 1, h, b, h=1.6)

    # ========================================================= 6. GREYSCALE ===
    s = add()
    title(s, [('Greyscale', None)])
    body(s, Y_BODY_STD, [
        'A camera hands you a three-number pixel: blue, green, red. For shape '
        'work that is three times more data than you need, and the colour values '
        'only add noise.',
        None,
        [('cvtColor', 'c'), (' converts the frame to one brightness number per '
         'pixel. White stays 255, black stays 0, and everything in between keeps '
         'its place on the grey scale.', None)],
    ])
    code(s, 8.9, [
        'img_h, img_w = img.shape[:2]',
        'gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)',
    ])
    note(s, 11.6, [
        ('Two things to notice. ', None),
        ('img.shape[:2]', 'c'),
        (' gives you height and width only — the trailing ', None),
        ('3', 'c'),
        (', which is the colour channels, is chopped off by the ', None),
        (':2', 'c'),
        ('. And ', None),
        ('BGR2GRAY', 'c'),
        (' is not a colour choice: it is the channel order OpenCV uses, which '
         'is the reverse of the ', None),
        ('RGB', 'c'),
        (' you are used to.', None)], h=2.6)

    # ============================================================= 7. BLUR ===
    s = add()
    title(s, [('Blur', None)])
    body(s, Y_BODY_STD, [
        'The camera’s sensor is never perfect. A single dark pixel of noise '
        'becomes a hole in your shape, and a hole becomes a broken contour.',
        None,
        'A Gaussian blur replaces every pixel with the average of itself and its '
        'neighbours. That pushes isolated noise down while leaving large solid '
        'regions alone.',
    ])
    code(s, 8.1, ['blurred = cv2.GaussianBlur(gray, (5, 5), 0)'])
    note(s, 10.4, [
        ('The ', None), ('(5, 5)', 'c'),
        (' is a window size: five pixels across, five pixels down. Bigger '
         'numbers smooth more. The ', None),
        ('0', 'c'),
        (' at the end means ‘work out the standard deviation for me’, and it is '
         'the only value you will ever need.', None)], h=2.4)

    # ======================================================== 8. THRESHOLD ===
    s = add()
    title(s, [('Threshold', None)])
    body(s, Y_BODY_STD, [
        'Now you make a decision about every single pixel: is it dark enough to '
        'be part of a shape, or not?',
        None,
        [('THRESH_BINARY_INV', 'c'),
         (' is the important half. ‘INV’ means inverted — the dark pixels become '
          'white and the pale background becomes black. That is deliberate. We '
          'want white shapes on a black background, because that is what '
          'contour finding expects.', None)],
    ])
    code(s, 8.9, ['_, thresh = cv2.threshold(blurred, 110, 255, cv2.THRESH_BINARY_INV)'])
    note(s, 11.1, [
        ('110', 'c'),
        (' is the only number on this slide you will ever be asked to change. '
         'Turn it up and pale shapes disappear; turn it down and every shadow on '
         'the table becomes a shape. If a shape refuses to detect, this number is '
         'the first thing to touch.', None)], h=2.6)
    note(s, 14.3, [
        ('The ', None), ('_', 'c'),
        (' on the left is a variable you are deliberately throwing away. '
         'OpenCV returns the threshold value as well as the image, and this '
         'program has no use for it.', None)], h=2.0)

    # ============================================================= 9. CLOSE ===
    s = add()
    title(s, [('Closing the ', None), ('outline', None)])
    body(s, Y_BODY_STD, [
        'Blur helps, but it never quite finishes the job. The outline is still '
        'broken in places, and a broken outline is detected as two smaller '
        'shapes instead of one.',
        None,
        'A morphological close swells the outline by a few pixels and then '
        'shrinks it back. The net effect is that small gaps vanish while the '
        'overall size stays the same.',
    ])
    code(s, 8.5, [
        'kernel = np.ones((5, 5), np.uint8)',
        'thresh_clean = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)',
    ])
    note(s, 11.0, [
        ('np.ones((5, 5), np.uint8)', 'c'),
        (' builds a 5×5 block of ones, and that block is the brush. Swapping ', None),
        ('MORPH_CLOSE', 'c'),
        (' for ', None),
        ('MORPH_OPEN', 'c'),
        (' would do the opposite job: remove specks instead of gaps.', None)], h=2.4)

    # ========================================================= 10. CONTOURS ===
    s = add()
    title(s, [('Contours', None)])
    body(s, Y_BODY_STD, [
        'This is the step that actually produces the list you are about to '
        'measure.',
        None,
        [('findContours', 'c'),
         (' walks along every white shape and returns the pixels on its border, '
          'in order, as a list of points. Each shape comes back as one NumPy '
          'array of coordinates.', None)],
    ])
    code(s, 7.9, [
        'contours, _ = cv2.findContours(',
        '    thresh_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE',
        ')',
    ])
    note(s, 10.4, [
        'Two flags are doing real work here. ', ('RETR_EXTERNAL', 'c'),
        ' keeps only the outermost outline, so a shape drawn inside another '
        'shape is not reported twice. ', ('CHAIN_APPROX_SIMPLE', 'c'),
(' throws away points sitting in a straight line between two others — '
         'fewer numbers to store, and a square arrives as four corners '
         'instead of a hundred.', None)], h=3.0)
    note(s, 13.6, [
        ('The ', None), ('_', 'c'),
        (' on the left of the equals sign is OpenCV’s hierarchy — a map of which '
         'shape sits inside which. This program has no use for it, so it goes '
         'straight in the bin.', None)], h=2.0)

    # =================================================== 11. THREE MEASUREMENTS ===
    s = add()
    title(s, [('Three ', None), ('measurements', None)])
    body(s, Y_BODY_STD, [
        'Everything that follows is built from three numbers. Take them one at '
        'a time, and give each one its own guard.',
    ], size=18.0)
    meas = [
        ('area', 'cv2.contourArea(cnt)', 'How many pixels the shape covers. This is also how you throw away noise.'),
        ('perimeter', 'cv2.arcLength(cnt, True)', 'The distance all the way around the outline. The True means the contour is closed.'),
        ('bounding box', 'cv2.minAreaRect(cnt)', 'The smallest rectangle that still contains the shape, rotated to hug it.'),
    ]
    for i, (n, call, b) in enumerate(meas):
        y = 5.5 + i * 2.5
        _, tf = textbox(s, X_ITEM, y, W_ITEM, 0.95)
        para(tf, True, [(n, None), ('  —  ', None), (call, 'c')],
             F_BODY, 16.5, YELLOW, bold=True)
        _, tf = textbox(s, X_ITEM, y + 0.83, W_ITEM, 1.6)
        para(tf, True, b, F_BODY, 15.0, WHITE, line_spacing=1.2)
    code(s, 12.6, [
        'area = cv2.contourArea(cnt)',
        'peri = cv2.arcLength(cnt, True)',
        'rect = cv2.minAreaRect(cnt)',
        '(cx, cy), (w, h), angle = rect',
        'rect_area = w * h',
    ])
    note(s, 16.3, [
        ('Notice the fourth line. ', None), ('(cx, cy), (w, h), angle = rect', 'c'),
        (' is Python unpacking: one returned value, immediately split into three '
         'differently named ones. You will use this pattern constantly.', None)], h=2.0)

    # ===================================================== 12. THREE METRICS ===
    s = add()
    title(s, [('Three ', None), ('metrics', None)])
    body(s, Y_BODY_STD, [
        'Raw measurements are awkward to compare. A circle of 3000 pixels and a '
        'square of 3000 pixels are the same size and nothing else. These three '
        'ratios turn size into shape.',
    ], size=18.0)
    code(s, 5.9, METRICS)
    note(s, 8.5, [
        ('Two Python ideas in three lines. ', None), ('**', 'c'),
        (' is the power operator, so ', None), ('peri ** 2', 'c'),
        (' squares the perimeter. The third line ends in ', None),
        ('... if ... else 0', 'c'),
        (', a conditional expression: divide only when the larger side is not '
         'zero, otherwise fall back to zero.', None)], h=2.4)
    table(s, 11.3, [
        ['Metric', 'Formula', 'Triangle', 'Square', 'Circle', 'Rectangle'],
        ['extent', [('area / rect_area', 'c')], '~0.50', '~1.00', '~0.79', '~1.00'],
        ['circularity', [('4π·area / peri²', 'c')], '~0.60', '~0.79', '~1.00', '~0.70'],
        ['aspect_ratio', [('min(w,h) / max(w,h)', 'c')], '~0.87', '~1.00', '~1.00', '~0.50'],
    ], col_w=[3.9, 6.2, 3.2, 3.2, 3.2, 3.6])
    note(s, 17.4, [
        ('Extent', 'b'),
        (' fills how much of its own box the shape takes up. ', None),
        ('Circularity', 'b'),
        (' scores how close the outline is to a perfect circle. ', None),
        ('Aspect ratio', 'b'),
        (' compares the sides: 1.0 means a square.', None)], h=2.0)

    # ========================================================= 13. CORNERS ===
    s = add()
    title(s, [('Counting ', None), ('corners', None)])
    body(s, Y_BODY_STD, [
        'Extent and circularity are not enough on their own. A square and a '
        'rectangle both fill their box almost completely, so you need one more '
        'clue: how many corners has this shape got?',
        None,
        [('approxPolyDP', 'c'),
         (' simplifies the outline, discarding points that do not change the '
          'direction much, and hands back the corners that are left.', None)],
    ])
    code(s, 8.4, [
        'approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)',
        'num_vertices = len(approx)',
    ], panel=False)
    note(s, 10.7, [
        ('0.04 * peri', 'c'),
        (' is the tolerance, and it scales with the shape — a big shape is '
         'allowed to be sloppy, a small one is not. Set it to 0 and you get every '
         'original pixel back; set it far too high and a square collapses to a '
         'single line.', None)], h=2.6)
    callout(s, 13.8, 'These two lines are already written for you in the starter '
                     'file. Do not retype them — just notice that num_vertices is '
                     'the number you will test in a moment.', h=2.44)

    # =================================================== 14. GATES AND GUARDS ===
    s = add()
    title(s, [('Gates and ', None), ('guards', None)])
    body(s, Y_BODY_STD, [
        'Before a shape is measured, the program throws most contours away. '
        'Before a shape is divided, it checks the divisor is not zero. Both '
        'habits are worth copying.',
    ], size=18.0)
    num_item(s, 5.5, 1, 'The area gate',
             [('A shape has to occupy between 2% and 80% of the cropped view. '
               'Anything smaller is dust or a shadow; anything larger is your '
               'hand, or the rim of the plate.', None)], h=1.8)
    num_item(s, 8.4, 2, 'The zero guards',
             [('peri == 0', 'c'), (' and ', None), ('rect_area == 0', 'c'),
              (' look fussy, but dividing by zero raises ', None),
              ('ZeroDivisionError', 'c'),
              (' and kills the whole program. A camera pointed at nothing will '
               'do this to you within a minute.', None)], h=2.2)
    code(s, 11.6, [
        'if area < (img_h * img_w * 0.02) or area > (img_h * img_w * 0.80):',
        '    continue',
    ])
    note(s, 14.1, [
        ('The ', None), ('or', 'c'),
        (' matters. Either condition on its own is enough to reject the contour, '
         'so the line is long and hard to read on purpose — split it across lines '
         'with brackets if that helps you.', None)], h=2.0)

    # ======================================================== 15. DECISION ===
    s = add()
    title(s, [('The ', None), ('decision', None)])
    body(s, Y_BODY_STD, [
        'Now the payoff. Four tests, tried in order, and the first one that '
        'succeeds names the shape.',
    ], size=18.0)
    code(s, 5.6, CHAIN)
    note(s, 10.3, [
        ('Starting at ', None), ('"Unknown"', 'c'),
        (' is not decoration. It guarantees the variable exists before any test '
         'runs, so nothing downstream can trip over an undefined name. If you '
         'later make the thresholds aggressive enough that every test fails, ', None),
        ('Unknown', 'c'),
        (' is what appears on screen instead of a crash.', None)], h=2.6)
    note(s, 13.4, [
        ('Read the branches as English: ‘if it fills less than 65% of its box, '
         'or it has three corners, it is a triangle. Otherwise, if it fills at '
         'least 82% and its sides are nearly equal, it is a square.’ That is the '
         'whole trick — the numbers are just the shape of the sentence.', None)],
        h=2.6)

    # ====================================================== 16. WHY ORDER ===
    s = add()
    title(s, [('Why ', None), ('order matters', None)])
    body(s, Y_BODY_STD, [
        [('Look at the square test and the circle test again. Both ask for ', None),
         ('aspect_ratio >= 0.78', 'c'),
         (', and a perfect circle has an aspect ratio of 1.00. A circle would '
          'satisfy the square test if the square test ran second.', None)],
        None,
        [('This is why the chain is an ', None), ('if / elif / elif / else', 'c'),
         (' and not four independent ', None), ('if', 'c'),
         (' statements. Python runs the tests top to bottom and stops at the '
          'first match, so the order you write is part of the meaning.', None)],
        None,
        [('It is also why the triangle test comes first. A triangle fills only '
          'half of its own box, so ', None), ('extent < 0.65', 'c'),
         (' claims it before any other test has a chance to guess.', None)],
    ])
    callout(s, 12.6, 'Before you write the chain, predict the order yourself. '
                     'For each of the four shapes, look at the table on the Three '
                     'metrics slide and decide which test should claim it. Then '
                     'check your answer against the code.', h=2.44)

    # ========================================================= 17. STEP 1 ===
    s = add()
    title(s, [('Step 1', None)])
    body(s, Y_BODY_STD, [
        [('On your computer, open VS Code, open your project folder, and open '
          'the file labelled ', None), (STARTER, 'b'), ('.', None)],
        None,
        [('You will see sections marked ', None), ('# TODO:', 'c'),
         (' with the code missing between the ', None), ('# ---', 'c'),
         (' lines. There are eleven of them, and they run from the imports at the '
          'top of the file to the camera setup near the bottom.', None)],
        None,
        'Before you fill in any of them, send the file across and run it. Seeing '
        'it fail first tells you exactly which errors belong to the missing code.',
        None,
        'Turn the arm on and give it about two minutes to boot, then run this in '
        'the VS Code terminal.',
    ], size=18.0)
    command(s, 13.6, SCP)

    # ========================================================= 18. STEP 2 ===
    s = add()
    title(s, [('Step 2', None)])
    body(s, Y_BODY_STD, [
        'Open Real VNC Viewer and connect to the Arm - Pump device. Open '
        '‘er’s Home’, then the Documents folder on the left panel.',
        None,
        [('Right-click the empty space in the folder, choose ', None),
         ('Open in Terminal', 'c'), (', and run the starter file.', None)],
    ], size=18.0)
    command(s, 7.5, RUN)
    body(s, 9.0, [
        [('You will not get as far as the camera, and the two failures are worth '
          'reading carefully, because they are different kinds of failure.', None)],
        None,
        [('The robot section sits inside a ', None), ('try / except', 'c'),
         (' block, so the missing ', None), ('MyCobot280', 'c'),
         (' import does not stop the program — it prints a hardware warning and '
          'carries on. The missing ', None), ('cv2', 'c'),
         (' import is not inside that block, so that one does stop you.', None)],
    ], size=18.0)
    code(s, 12.2, [
        'Robot hardware warning: name \'MyCobot280\' is not defined',
        'Continuing with OpenCV camera pipeline only...',
        '',
        'NameError: name \'cv2\' is not defined',
    ])
    note(s, 15.2, [
        ('Neither is a broken camera. ', None),
        ('try / except', 'c'),
        (' lets the problem be reported, then ignored — the message just tells '
         'you which import is missing.', None)], h=2.4)

    # ========================================================= 19. STEP 3 ===
    s = add()
    title(s, [('Step 3', None)])
    body(s, Y_BODY_STD, [
        [('Fill in the first TODO at the very top of the file. Four imports, and '
          'each one earns its place:', None)],
    ], size=18.0)
    imports = [
        ('cv2', 'OpenCV — every cv2. call in this project comes from here.'),
        ('numpy as np', 'NumPy under the alias np, used for arrays and math in the shape code.'),
        ('time', 'The standard library. time.sleep() paces the program against the arm.'),
        ('MyCobot280', 'The arm driver from pymycobot. Written specifically for this course.'),
    ]
    for i, (n, b) in enumerate(imports):
        y = 5.4 + i * 2.05
        _, tf = textbox(s, X_ITEM, y, W_ITEM, 0.9)
        para(tf, True, [(n, 'c')], F_BODY, 16.5, YELLOW, bold=True)
        _, tf = textbox(s, X_ITEM, y + 0.72, W_ITEM, 1.3)
        para(tf, True, b, F_BODY, 15.0, WHITE, line_spacing=1.2)
    code(s, 13.5, [
        'import cv2',
        'import numpy as np',
        'import time',
        '',
        'from pymycobot.mycobot280 import MyCobot280',
    ])
    note(s, 16.5, [
        [('The ', None), ('as np', 'c'),
         (' is an alias: ', None), ('np', 'c'), (' is a short nickname for ', None),
         ('numpy', 'c'),
         ('. Keep the blank line — it separates other people’s code from yours.', None)]],
        h=2.4)

    # ========================================================= 20. STEP 4 ===
    s = add()
    title(s, [('Step 4', None)])
    body(s, Y_BODY_STD, [
        [('The next TODO sits inside the ', None), ('try', 'c'),
         (' block. This is the code that wakes the arm up.', None)],
        None,
        [('MyCobot280(\'/dev/ttyAMA0\', 1000000)', 'c'),
         (' takes two arguments: which serial port the arm is plugged into, and '
          'how fast to talk to it. On another machine the port may be ', None),
         ('ttyUSB0', 'c'), (', so if this line throws, check the port before you '
          'suspect the arm.', None)],
        None,
        [('Each ', None), ('sleep', 'c'),
         (' gives the command before it time to finish. Remove them and the arm '
          'misses instructions — which looks exactly like a broken arm.', None)],
    ], size=18.0)
    code(s, 10.4, [
        'print("Connecting to myCobot280...")',
        '',
        'mc = MyCobot280(\'/dev/ttyAMA0\', 1000000)',
        'time.sleep(0.5)',
        'mc.power_on()',
        'time.sleep(0.5)',
    ])
    note(s, 14.0, [
        [('mc', 'c'),
         (' is the name you give the arm. Every later line that talks to the '
          'hardware goes through it, so you only ever type the port once.', None)]],
        h=1.8)

    # ========================================================= 21. STEP 5 ===
    s = add()
    title(s, [('Step 5', None)])
    body(s, Y_BODY_STD, [
        [('One TODO left in this section: park the arm somewhere safe before the '
          'camera work starts.', None)],
        None,
        [('Six numbers, one per joint, in degrees. Zero means ‘no bend’, and the '
          'signs say which way. Folding the arm up and out of shot is deliberate '
          '— a metal arm parked in view is a shape your program will try to '
          'measure.', None)],
        None,
        [('The ', None), ('50', 'c'), (' is how fast to travel there.', None)],
    ], size=18.0)
    code(s, 10.4, [
        'home_pos = [0, 45, -90, -45, 0, 0]',
        'mc.send_angles(home_pos, 50)',
        'time.sleep(2.0)',
    ])
    note(s, 13.6, [
        [('This is a ', None), ('list', 'c'),
         (', not a tuple. The ', None), ('[ ]', 'c'),
         (' brackets mean you can change it later, which is exactly what you will '
          'want when you go on to record positions for the sorting bins.', None)]],
        h=2.2)

    # ========================================================= 22. STEP 6 ===
    s = add()
    title(s, [('Step 6', None)])
    body(s, Y_BODY_STD, [
        'Send the file across again and run it. This time all four imports exist, '
        'so the robot should wake up and two windows should open.',
    ], size=18.0)
    command(s, 5.5, SCP)
    command(s, 6.6, RUN)
    body(s, 8.2, [
        [('The status line will say ', None), ('Searching...', 'c'),
         (' and stay there. Put a shape on the plate and nothing happens.', None)],
        None,
        [('That is expected, and it is worth pausing on. Five stages of image '
          'processing are running correctly — greyscale, blur, threshold, close '
          'and the contour search have all executed. What is missing is the part '
          'that ', None), ('measures', 'b'), ('.', None)],
    ], size=18.0)
    note(s, 12.2, [
        [('Read the two windows before you change anything. In ', None),
         ('Threshold View (Binary)', 'c'),
         (' your shape should already be a clean white blob on black. If it is '
          'not, the problem is upstream of the TODOs and no amount of typing will '
          'help. Learn to look at the boring picture first.', None)]], h=2.8)

    # ========================================================= 23. STEP 7 ===
    s = add()
    title(s, [('Step 7', None)])
    body(s, Y_BODY_STD, [
        [('First measurement TODO. How much of the view does the shape cover, '
          'and is it worth measuring at all?', None)],
    ], size=18.0)
    code(s, 5.9, [
        'area = cv2.contourArea(cnt)',
        'if area < (img_h * img_w * 0.02) or area > (img_h * img_w * 0.80):',
        '    continue',
    ])
    note(s, 8.7, [
        [('img_h * img_w', 'c'),
         (' is the total pixel count of the cropped view, so the gate is '
          'expressed as a percentage and survives you changing the camera '
          'resolution later.', None)]], h=2.0)
    note(s, 11.2, [
        [('continue', 'c'),
         (' does not mean ‘skip this one line’. It abandons the whole loop '
          'iteration and moves on to the next contour. Forgetting that is how '
          'people end up measuring a dust speck.', None)]], h=2.4)

    # ========================================================= 24. STEP 8 ===
    s = add()
    title(s, [('Step 8', None)])
    body(s, Y_BODY_STD, [
        [('Second measurement. How far is it all the way around?', None)],
    ], size=18.0)
    code(s, 5.9, [
        'peri = cv2.arcLength(cnt, True)',
        'if peri == 0:',
        '    continue',
    ])
    note(s, 8.7, [
        [('The ', None), ('True', 'c'),
         (' asks for a closed outline — join the last point back to the first. '
          'Leave it off and you lose one edge in three on a triangle, which is '
          'more than enough to make the circularity figure wrong without looking '
          'obviously broken.', None)]], h=2.8)
    note(s, 12.2, [
        [('The guard underneath looks pedantic, but remember that this perimeter '
          'is about to become a divisor. Guard the divisor, not the symptom.', None)]],
        h=1.8)

    # ========================================================= 25. STEP 9 ===
    s = add()
    title(s, [('Step 9', None)])
    body(s, Y_BODY_STD, [
        [('Third measurement, and the one that needs unpacking.', None)],
    ], size=18.0)
    code(s, 5.5, [
        'rect = cv2.minAreaRect(cnt)',
        '(cx, cy), (w, h), angle = rect',
        'rect_area = w * h',
        'if rect_area == 0:',
        '    continue',
    ])
    note(s, 8.9, [
        [('minAreaRect', 'c'),
         (' does not give you an upright box. It rotates one to hug the shape, so '
          'a shape leaning at 30° still gets a tight fit. That is why it hands '
          'back an ', None), ('angle', 'c'),
         (', and why you get ', None), ('(w, h)', 'c'),
         (' rather than ', None), ('(left, top, right, bottom)', 'c'), ('.', None)]],
        h=2.8)
    note(s, 12.4, [
        [('Read the second line right to left: the centre arrives first, then the '
          'size, then the angle. And note that ', None), ('cx', 'c'), (' and ', None),
         ('cy', 'c'),
         (' are never used by the decision — they are where the label gets drawn. '
          'Not every value you are handed has to be used.', None)]], h=2.6)

    # ======================================================== 26. STEP 10 ===
    s = add()
    title(s, [('Step 10', None)])
    body(s, Y_BODY_STD, [
        [('Now turn the raw measurements into the three ratios. These three lines '
          'are what the whole project turns on.', None)],
    ], size=18.0)
    code(s, 6.3, METRICS)
    note(s, 9.1, [
        [('Two Python ideas in three lines. ', None), ('**', 'c'),
         (' is the power operator, so ', None), ('peri ** 2', 'c'),
         (' squares the perimeter. And the third line ends in ', None),
         ('if ... else 0', 'c'),
         (', a conditional expression written out longhand it would be four lines '
          'with an ', None), ('if', 'c'), (' and a ', None), ('pass', 'c'), ('.', None)]],
        h=2.8)
    callout(s, 12.6, 'Type these three lines exactly as they appear. A single '
                     'missing bracket here will not be reported until the program '
                     'is already running.', h=2.44)

    # ======================================================== 27. STEP 11 ===
    s = add()
    title(s, [('Step 11', None)])
    body(s, Y_BODY_STD, [
        [('One line, and it is not filler.', None)],
    ], size=18.0)
    code(s, 5.9, ['object_type = "Unknown"'])
    note(s, 7.9, [
        [('This guarantees the variable exists before any test runs, so nothing '
          'downstream can trip over an undefined name. In this project the ', None),
         ('else', 'c'),
         (' branch always overwrites it — but tune the thresholds hard enough that '
          'every test fails, and ', None), ('Unknown', 'c'),
         (' is what appears on screen instead of a crash.', None)]], h=2.8)
    callout(s, 11.4, 'Set the safe default first, then overwrite it. This one '
                     'habit prevents an entire class of beginner bug.', h=2.44)
    note(s, 14.4, [
        [('In Python a name has to exist before it is used, and reading an '
          'undefined name is an error, not an empty string. Declaring it up front '
          'is cheaper than debugging that later.', None)]], h=2.0)

    # ======================================================== 28. STEP 12 ===
    s = add()
    title(s, [('Step 12', None)])
    body(s, Y_BODY_STD, [
        [('The last big TODO. Four tests in order; the first match names the '
          'shape.', None)],
    ], size=18.0)
    code(s, 5.9, CHAIN)
    note(s, 10.6, [
        [('Copy the indentation exactly. The lines inside each branch sit four '
          'spaces further right than the ', None), ('if', 'c'),
         (' that owns them. Python has no braces, so that indentation is the only '
          'thing telling it where a block starts and stops.', None)]], h=2.4)
    note(s, 13.6, [
        [('If you see ', None), ('IndentationError', 'c'),
         (', you have mixed tabs and spaces. In VS Code, click ', None),
         ('Spaces: 4', 'c'),
         (' in the status bar to switch the file to spaces, and stay there.', None)]],
        h=2.2)

    # ======================================================== 29. STEP 13 ===
    s = add()
    title(s, [('Step 13', None)])
    body(s, Y_BODY_STD, [
        [('Two TODOs left, both down in ', None), ('main()', 'c'),
         ('. This one is about which camera to open.', None)],
    ], size=18.0)
    code(s, 5.9, [
        'cap_num = find_working_camera()',
        'if cap_num is None:',
        '    print("Error: No working camera stream found.")',
        '    return',
    ])
    note(s, 8.9, [
        [('find_working_camera()', 'c'),
         (' tries indexes 0 to 4 and returns the first one that produces a '
          'picture. Linux does not promise a camera is always index 0 — plugging '
          'one in can push the other to index 1.', None)]], h=2.4)
    note(s, 12.0, [
        [('The ', None), ('is None', 'c'),
         (' test asks whether the function found nothing at all, and ', None),
         ('return', 'c'),
         (' leaves ', None), ('main()', 'c'),
         (' immediately rather than carrying on with a camera that does not '
          'exist.', None)]], h=2.2)

    # ======================================================== 30. STEP 14 ===
    s = add()
    title(s, [('Step 14', None)])
    body(s, Y_BODY_STD, [
        [('Open the camera and ask for a sensible picture size.', None)],
    ], size=18.0)
    code(s, 5.9, [
        'cap = cv2.VideoCapture(cap_num, cv2.CAP_V4L2)',
        'cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)',
        'cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)',
    ])
    note(s, 8.9, [
        [('CAP_V4L2', 'c'),
         (' is the Video4Linux2 backend, which is what the arm’s Linux system '
          'uses. The two ', None), ('set', 'c'),
         (' lines request 640×480.', None)]], h=2.0)
    note(s, 11.5, [
        [('Note the wording: you are ', None), ('asking', 'b'),
         (', not telling. Some cameras ignore the request, so if the window looks '
          'wrong, print ', None),
         ('cap.get(cv2.CAP_PROP_FRAME_WIDTH)', 'c'),
         (' and find out what you actually got.', None)]], h=2.4)
    note(s, 14.6, [
        [('Both lines live inside ', None), ('main()', 'c'),
         (' rather than at the top of the file, because the camera is opened as '
          'late as possible and released as early as possible.', None)]], h=2.0)

    # ======================================================== 31. STEP 15 ===
    s = add()
    title(s, [('Step 15', None)])
    body(s, Y_BODY_STD, [
        [('Send the file across and run it one more time. Then place one shape at '
          'a time on the plate and watch the label.', None)],
    ], size=18.0)
    command(s, 5.6, SCP)
    command(s, 6.7, RUN)
    tests = [
        [('Triangle', 'b'), (' — should print ', None), ('Verts: 3', 'c'),
         (' and an extent near 0.50', None)],
        [('Square', 'b'), (' — extent near 1.00 and aspect ratio near 1.00', None)],
        [('Circle', 'b'), (' — circularity near 1.00 and extent near 0.79', None)],
        [('Rectangle', 'b'), (' — the long thin one; circularity 0.70 or lower, '
          'aspect ratio near 0.50', None)],
    ]
    for i, t in enumerate(tests):
        check_item(s, 7.9 + i * 1.75, t, h=1.6)
    callout(s, 15.3, 'Test each shape at least three times, and move it around '
                     'the plate. A detector that only works in the middle of the '
                     'frame is not finished.', h=2.44)

    # ==================================================== 32. READING OUTPUT ===
    s = add()
    title(s, [('Reading the ', None), ('output', None)])
    body(s, Y_BODY_STD, [
        [('The line printed under the windows is your diagnostic. It looks like '
          'this:', None)],
    ], size=18.0)
    code(s, 5.9, ['[Detected] Square | Extent: 0.99 | Circ: 0.78 | Verts: 4'])
    outs = [
        [('The word before the first pipe is the answer', 'b'),
         (' — the only part the arm would ever act on.', None)],
        [('Extent, Circ and Verts are the evidence', 'b'),
         ('. When the answer is wrong, these three tell you which measurement to '
          'distrust.', None)],
        [('If ', None), ('Verts', 'c'),
         (' says 3 but the answer is not Triangle, then the shape is a poor '
          'drawing rather than your code being broken.', None)],
    ]
    y = 8.4
    for t in outs:
        bullet(s, y, t, h=2.2)
        y += 2.4
    callout(s, 15.6, 'Change one threshold, retest, and write down what moved. '
                     'Changing three numbers at once is how a whole afternoon '
                     'disappears.', h=2.44)

    # ================================================== 33. EXTENSION DIVIDER ===
    s = add(0, master=1)
    _, tf = textbox(s, 14.22, 2.29, 12.70, 11.68)
    para(tf, True, '1', F_TITLE, 260.0, PANEL2, align=2)  # CENTER
    _, tf = textbox(s, X_L, 15.80, 24.89, 1.68)
    para(tf, True, 'EXTENSION 1', F_TITLE, 32.0, YELLOW)
    _, tf = textbox(s, X_L, 17.58, 24.89, 1.83)
    para(tf, True, 'MAKE THE ARM SORT BY SHAPE', F_TITLE, 34.0, WHITE)

    # ========================================================== 34. BRIEF ===
    s = add(0, master=1)
    title(s, [('THE ', None), ('BRIEF', None)], ext=True)
    body(s, Y_BODY_EXT, [
        'You have a program that names a shape. A sorting program needs one more '
        'thing: somewhere for each shape to go.',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    body(s, 6.6, [
        'Add that, and the machine you have been building all module becomes a '
        'shape sorter. Then change what ‘sort’ means, because recognising four '
        'shapes is the easy half.',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    callout(s, 10.5, 'This challenge has no single correct answer. It has a '
                     'working machine and a written explanation, and you need '
                     'both.', h=2.44)

    # ========================================================= 35. MISSION ===
    s = add(0, master=1)
    title(s, [('YOUR MISSION: ', None), ('SORT BY SHAPE', None)], ext=True)
    body(s, Y_BODY_EXT, [
        'Record every shape’s home position, then move it.',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    items = [
        ('Move the arm to each bin',
         [('Pick four positions on the plate. Each one is a list of six joint '
           'angles plus a gripper value, exactly like ', None), ('home_pos', 'c'),
          ('. Send the arm there when a shape is recognised.', None)]),
        ('Prove all four still work',
         [('Twelve placements, three of each shape, every one identified '
           'correctly and sent to the right bin. If tuning a threshold fixed one '
           'shape and broke another, you have moved the problem rather than '
           'solved it.', None)]),
        ('Change the rule',
         [('One shape per bin is the boring version. Try size instead of '
           'identity: big shapes into one bin, small into another. Or send '
           'triangles and squares to quality control and let only circles and '
           'rectangles through. Write your rule as plain sentences before you '
           'code it.', None)]),
        ('Hand it over',
         [('Write the handover page: your thresholds, your sorting rule in plain '
           'language, and one thing you would fix with another hour.', None)]),
    ]
    for i, (h, b) in enumerate(items):
        num_item(s, 5.3 + i * 3.0, i + 1, h, b, h=2.1)
    callout(s, 17.0, 'Implement your rule by changing the logic, not by '
                     're-recording coordinates. Re-teaching the arm where the bins '
                     'are means you solved the wrong problem.', h=2.44)

    # ======================================================== 36. DATA LOG ===
    s = add(0, master=1)
    title(s, [('YOUR ', None), ('DATA LOG', None)], ext=True)
    body(s, Y_BODY_EXT, [
        'Write down what you measured before you tune anything. If a threshold '
        'is about to change, you need to know what it was.',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    table(s, 5.5, [
        ['Shape', 'Extent', 'Circ', 'Aspect', 'Verts', 'My values'],
        ['Triangle', '', '', '', '', ''],
        ['Square', '', '', '', '', ''],
        ['Circle', '', '', '', '', ''],
        ['Rectangle', '', '', '', '', ''],
    ], col_w=[4.2, 3.4, 3.4, 3.4, 3.0, 5.6])
    body(s, 12.3, [
        'Then write your sorting rule as a set of conditions before you code it:',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    code(s, 13.8, [
        'IF the shape is  ______________   THEN send it to  ______________',
        'IF the shape is  ______________   THEN send it to  ______________',
        'OTHERWISE                          ______________',
    ], size=15.0)
    callout(s, 16.6, 'A rule you cannot say out loud is a rule you have not '
                     'decided yet.', h=2.2)

    # ================================================= 37. DEFINITION OF DONE ===
    s = add(0, master=1)
    title(s, [('DEFINITION OF ', None), ('DONE', None)], ext=True)
    dones = [
        [('All four shapes detected correctly from three different places on '
          'the plate', None)],
        [('Every threshold change recorded in your data log, before and after', None)],
        [('Twelve placements sorted correctly into four bins', None)],
        [('A sorting rule of your own design, implemented in the ', None),
         ('logic', 'b'), (' rather than the coordinates', None)],
        [('Handover page written, and understood by your facilitator from the '
          'page alone', None)],
    ]
    for i, t in enumerate(dones):
        check_item(s, 4.4 + i * 2.5, t, h=2.2)

    # ======================================================= 38. GO FURTHER ===
    s = add(0, master=1)
    title(s, [('GO ', None), ('FURTHER', None)], ext=True)
    more = [
        [('Add a fifth shape. ', None),
         ('A cross or a five-pointed star needs a new test and a new place in the '
          'chain — decide where it goes before you write it, and remember that '
          'order matters.', None)],
        [('Make the program refuse to guess. ', None),
         ('If a shape’s measurements sit within a hair of two thresholds, leave '
          'it on the plate and print a warning instead of naming it.', None)],
        [('Give the operator a choice of sorting rule ', None),
         ('when the program starts, so one machine can do several jobs.', None)],
        [('Log every detection to a file with a timestamp. ', None),
         ('Run the sorter for an hour and you will find shapes you never tested '
          'for.', None)],
    ]
    for i, t in enumerate(more):
        bullet(s, 4.6 + i * 3.2, t, h=2.9)

    # ========================================================= 39. DEBRIEF ===
    s = add(0, master=1)
    title(s, [('MISSION ', None), ('DEBRIEF', None)], ext=True)
    qs = [
        'Why does a circle score about 0.79 on extent rather than 1.00?',
        [('The square test and the circle test both look at ', None),
         ('aspect_ratio', 'c'),
         ('. What would happen if you swapped them?', None)],
        'You changed a threshold to make one shape work. How would you know you '
        'had not broken another?',
        'If the camera could see colour as well as shape, what would you sort by '
        'instead — and which would you trust more?',
    ]
    for i, q in enumerate(qs):
        question_item(s, 4.6 + i * 3.3, i + 1, q)

    # ====================================================== 40. MISSION DONE ===
    s = add(0, master=1)
    s.shapes.add_picture(art['image5.png'], Cm(16.64), Cm(3.25), Cm(11.30), Cm(13.16))
    s.shapes.add_picture(art['image6.png'], Cm(1.78), Cm(2.08), Cm(10.03), Cm(3.76))
    _, tf = textbox(s, X_L, 15.44, 24.89, 1.83)
    para(tf, True, 'MISSION', F_TITLE, 34.0, WHITE)
    _, tf = textbox(s, X_L, 17.32, 24.89, 1.83)
    para(tf, True, 'COMPLETE', F_TITLE, 34.0, YELLOW)

    # ------------------------------------------------------- layout pass ---
    tight = pack_deck(prs, gap=0.30, limit=Y_BOTTOM)
    if tight:
        print('OVERFLOW:', tight)

    prs.save(OUT)
    print(f'wrote {OUT} with {len(prs.slides._sldIdLst)} slides')


if __name__ == '__main__':
    build()

# -*- coding: utf-8 -*-
"""Build Slides/M2/myCobot_07.pptx -- 'Read the Board' (M2-P7).

Rebuilds the deck from the theme/layouts of the reference sample
Slides/myCobot_08.pptx, but teaches the tic-tac-toe board-state vision scanner
that students complete in M2/M2-P7-Starter.py.

Ordering rule: concepts first, then all twenty-one steps, and only then the
correction section. Nothing in the concept section refers to a line number, so
the mechanisms can be taught without spoiling which code turns out to need them.

Every code snippet is copied verbatim from M2/M2-P7-Base.py, except the two
shell commands, the sample terminal output, the "before" listing in the
correction section (the earlier, faulty quit check, labelled as such), and the
worksheet blanks.
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
OUT = os.path.join(HERE, 'Slides', 'M2', 'myCobot_07.pptx')
TMP = os.path.join(HERE, 'tmp_media')

STARTER = 'M2-P7-Starter.py'
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
    para(tf, True, 'Project 7', F_TITLE, SZ_DIVIDER, YELLOW, line_spacing=1.0)
    para(tf, False, 'Read the Board', F_TITLE, SZ_DIVIDER, WHITE, line_spacing=1.0)

    # ================================================== 3. WHAT THIS BUILDS ===
    s = add()
    title(s, [('What this project builds', None)])
    body(s, Y_BODY_STD, [
        [('Draw a tic-tac-toe board on paper, put the camera above it, and let the '
          'program read the board nine times a second. Red pieces become X, blue '
          'pieces become O, and an empty cell stays empty.', None)],
        [('No arm movement. No rules. No winning. This project is the part that looks '
          'at the board, and it is deliberately the smallest interesting thing that '
          'can look at a board.', None)],
    ])
    bullet(s, 9.6, [
        ('A region of interest', 'b'), (' — one rectangle of the picture, defined '
         'by numbers, that everything else works inside.', None),
    ], h=2.0)
    bullet(s, 11.7, [
        ('A colour test per cell', 'b'), (' — the red wraparound trick you already '
         'built in Project 5, reused on a smaller picture.', None),
    ], h=2.0)
    bullet(s, 13.8, [
        ('A board as data', 'b'), (' — nine single characters in a 3x3 list, which '
         'is something a program can reason about.', None),
    ], h=2.0)
    callout(s, 16.4, [
        ('The output of this project is not a game. It is a truth about the world, '
         'refreshed continuously: what is on the board, right now.', None),
    ], h=2.0)
    note(s, 18.6, [
        [('Project 8 builds a real opponent on this ', None), ('parse_board_state', 'c'),
         ('. Everything you write this week feeds it.', None)],
    ], h=2.4)

    # ================================================== 4. NINE CELLS, ONE LOOP ===
    s = add()
    title(s, [('Nine cells, one loop', None)])
    body(s, Y_BODY_STD, [
        [('The entire program is one loop that runs forever and does four things, '
          'over and over:', None)],
    ])
    num_item(s, 7.0, 1, 'Read a frame',
             [('One picture from the camera, 640 by 480.', None)], h=1.9)
    num_item(s, 8.9, 2, 'Cut it into nine',
             [('Nine rectangles, using arithmetic rather than a mouse.', None)], h=1.9)
    num_item(s, 10.8, 3, 'Test each one',
             [('Red, blue, or nothing. One character returned.', None)], h=1.9)
    num_item(s, 12.7, 4, 'Draw it back',
             [('The grid, the pieces, and a label, over the top of the picture.', None)],
             h=1.9)
    note(s, 14.8, [
        [('Steps 2 and 3 are the whole project. Step 4 exists so that a human can '
          'check the answer without reading a single line of Python — and in this '
          'module that has turned out to matter more than expected.', None)],
    ], h=2.4)
    callout(s, 17.6, [
        ('Nothing here is slow. Nine small colour tests take well under a '
         'millisecond, which is why a plain loop with no threading is enough.', None),
    ], h=1.8)

    # ==================================================== 5. BGR IS NOT A NAME ===
    s = add()
    title(s, [('BGR is not a colour name', None)])
    body(s, Y_BODY_STD, [
        [('OpenCV does not hand you "red". It hands you three numbers per pixel, in '
          'the order blue, green, red — and each one ranges from 0 to 255. So the '
          'brightest red is not ', None), ('(255, 0, 0)', 'c'), (', it is ', None),
         ('(0, 0, 255)', 'c'), ('.', None)],
        [('Testing a colour that way means writing down a range of possibilities for '
          'all three numbers at once. The conversion below moves the problem into a '
          'space where one number carries the hue:', None)],
    ])
    code(s, 9.6, [
        '    hsv = cv2.cvtColor(cell_roi, cv2.COLOR_BGR2HSV)',
    ], size=14.0)
    bullet(s, 12.2, [
        ('H', 'c'), (' is hue — where on the colour wheel the colour sits, 0 to 180 '
         'in OpenCV.', None),
    ], h=1.9)
    bullet(s, 14.1, [
        ('S', 'c'), (' is saturation — how vivid it is. Low S means grey, whatever '
         'the hue says.', None),
    ], h=1.9)
    bullet(s, 16.0, [
        ('V', 'c'), (' is value — how bright it is. Low V means dark, and dark red '
         'is black.', None),
    ], h=1.9)
    note(s, 18.2, [
        [('Converting does not make the threshold easier to write. It makes it '
          'possible to write one that survives a change in lighting, because hue is '
          'roughly stable under brightness changes and BGR is not.', None)],
    ], h=2.4)

    # ======================================================= 6. HUE IS A CIRCLE ===
    s = add()
    title(s, [('Hue is a circle', None)])
    body(s, Y_BODY_STD, [
        [('This is the detail that makes hue different from the other two channels, '
          'and it is the whole reason this project has two red ranges instead of '
          'one.', None)],
        [('Hue starts at 0 for red and runs to 180 for red again. There is no 181. '
          'Red is at both ends of the scale, so a single ', None), ('inRange', 'c'),
         (' can never capture it.', None)],
    ])
    code(s, 8.8, [
        'RED = 0     ... and RED = 180     # the same colour, opposite ends',
    ], size=13.0)
    body(s, 11.0, [
        [('Two ranges are written to cover both ends, and each is a valid slice of '
          'the wheel on its own. The first is the 0 end, the second is the 180 end:',
          None)],
    ])
    code(s, 13.0, [
        'LOWER_RED1 = np.array([0, 120, 100])',
        'UPPER_RED1 = np.array([10, 255, 255])',
        'LOWER_RED2 = np.array([170, 120, 100])',
        'UPPER_RED2 = np.array([180, 255, 255])',
    ], size=12.0)
    callout(s, 17.4, [
        ('You wrote this exact structure in Project 5 for a red ball on a blue '
         'table. It is the same problem at a smaller scale, which is the point — a '
         'pattern worth learning once should be recognisable the second time.',
         None),
    ], h=2.4)

    # ==================================================== 7. A MASK IS A PICTURE ===
    s = add()
    title(s, [('A mask is a picture', None)])
    body(s, Y_BODY_STD, [
        [('Every colour test in OpenCV produces an image of the same size as its '
          'input, where each pixel is one of two values. Inside the range it is '
          '255. Outside the range it is 0. That picture is called a mask, and it is '
          'why colour detection is arithmetic rather than guessing.', None)],
    ])
    code(s, 8.6, [
        '    # Blue Mask',
        '    mask_blue = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)',
    ], size=13.0)
    body(s, 11.2, [
        [('For blue, one range is enough, because blue sits in the middle of the '
          'hue scale and wraps around nothing:', None)],
    ])
    code(s, 13.2, [
        'LOWER_BLUE = np.array([90, 120, 100])',
        'UPPER_BLUE = np.array([130, 255, 255])',
    ], size=13.0)
    callout(s, 16.4, [
        ('The mask for a red piece is built from two ranges, which means two masks. '
         'The next line combines them, and a pixel counts as red if it landed in '
         'either one.', None),
    ], h=2.2)
    note(s, 18.8, [
        [('The S and V floors — 120 and 100 — stop a shadowed white cell from reading '
          'as a piece.', None)],
    ], h=2.2)

    # ======================================================== 8. TWO REDS, ONE COLOUR ===
    s = add()
    title(s, [('Two masks, one colour', None)])
    body(s, Y_BODY_STD, [
        [('Because red needed two ranges, it needs two masks — and then a way to '
          'treat them as a single answer:', None)],
    ])
    code(s, 6.8, [
        '    mask_red1 = cv2.inRange(hsv, LOWER_RED1, UPPER_RED1)',
        '    mask_red2 = cv2.inRange(hsv, LOWER_RED2, UPPER_RED2)',
        '    mask_red = cv2.bitwise_or(mask_red1, mask_red2)',
    ], size=12.5)
    body(s, 10.2, [
        [('Read that third line as a sentence: a pixel is part of ', None),
         ('mask_red', 'c'), (' if it is part of ', None), ('mask_red1', 'c'),
         (' or part of ', None), ('mask_red2', 'c'),
         ('. The output is a new mask of the same size, not a count and not a '
          'boolean.', None)],
    ])
    callout(s, 13.6, [
        ('This is the line that would be wrong if the two ranges were merged with '
         'a single ', None), ('inRange', 'c'),
        (' covering 0 to 180. That would match every colour in between — orange, '
         'yellow, green, cyan, all of it — and the board would be full of pieces '
         'that are not there.', None),
    ], h=3.0)
    note(s, 17.0, [
        [('Bitwise, not arithmetic. ', None), ('bitwise_or', 'c'),
         (' does not add pixel values together; it merges two pictures by rule. The '
          'distinction matters the moment a mask stops being a yes-or-no thing.',
          None)],
    ], h=2.4)

    # ======================================================== 9. COUNTING PIXELS ===
    s = add()
    title(s, [('Counting pixels', None)])
    body(s, Y_BODY_STD, [
        [('You have two masks. Each one answers a question about every pixel, and '
          'the answer you actually want is a single number: how many of them said '
          'yes.', None)],
    ])
    code(s, 7.0, [
        '    red_pixels = cv2.countNonZero(mask_red)',
        '    blue_pixels = cv2.countNonZero(mask_blue)',
    ], size=13.5)
    body(s, 9.6, [
        [('No thresholding step, no image comparison, no per-pixel loop in Python. '
          'OpenCV counts the non-zero entries and hands back an integer, which is '
          'exactly the number of pixels inside the colour range.', None)],
    ])
    bullet(s, 12.6, [
        ('A number is easier to test than a picture.', 'b'), ('  Once you have 4,182 '
         'red pixels, every remaining decision is a comparison.', None),
    ], h=2.1)
    bullet(s, 14.7, [
        ('This runs nine times per frame', 'b'), (' — once per cell — so the number '
         'has to be small. It is.', None),
    ], h=2.1)
    callout(s, 17.2, [
        ('Counting is also why the cell size matters. The same 800-pixel threshold '
         'means something completely different in a 75x75 cell than in a '
         '30x30 one, and that is the next idea.', None),
    ], h=2.2)

    # ======================================================= 10. 800 OF 5,625 ===
    s = add()
    title(s, [('A threshold is a fraction', None)])
    body(s, Y_BODY_STD, [
        [('The line that decides everything is this one:', None)],
    ])
    code(s, 5.8, [
        '    MIN_PIXELS = 800',
    ], size=14.0)
    body(s, 7.4, [
        [('800 is not a guess: it is a fraction of the cell — here 75 by 75 pixels, '
          '5,625 in total:', None)],
    ])
    code(s, 10.6, [
        '    # cell area',
        '    75 * 75   # = 5625 px',
        '',
        '    # threshold as a fraction of that area',
        '    800 / 5625   # = 0.142, about 14%',
    ], size=13.0)
    body(s, 13.0, [
        [('So 800 means "a piece has to fill at least a seventh of its cell" — forgiving '
          'about shape, strict about colour.', None)],
    ])
    callout(s, 16.2, [
        ('Change the frame resolution and this number goes wrong silently — the '
         'geometry behind it must stay fixed.', None),
    ], h=1.6)
    note(s, 19.0, [
        [('It is defined inside the function, so it is rebuilt on all nine calls '
          'per frame — cheap, but worth knowing.', None)],
    ], h=1.6)

    # ======================================================= 11. CELL BY CELL ===
    s = add()
    title(s, [('Cell by cell', None)])
    body(s, Y_BODY_STD, [
        [('Everything above happens inside one function that is handed a small '
          'picture and returns one character. It knows nothing about grids, rows, '
          'columns, or the board:', None)],
    ])
    code(s, 7.4, [
        'def scan_cell(cell_roi):',
        '    """Inspects a single cell ROI and returns \'X\', \'O\', or \' \'."""',
    ], size=13.0)
    body(s, 10.0, [
        [('One job, one return value, three possible answers. The caller will '
          'assemble nine of these characters into a board, but this function never '
          'has to know that.', None)],
    ])
    code(s, 12.6, [
        '    if red_pixels > MIN_PIXELS and red_pixels > blue_pixels:',
        '        return \'X\'',
        '    elif blue_pixels > MIN_PIXELS and blue_pixels > red_pixels:',
        '        return \'O\'',
        '    return \' \'',
    ], size=12.5)
    note(s, 15.8, [
        [('Both halves matter: the threshold says the colour is present; the '
          'comparison says which one won.', None)],
    ], h=2.8)
    callout(s, 19.0, [
        ('A space means an untouched cell is already the answer.', None),
    ], h=1.6)

    # ======================================================= 12. SLICING IS A RECTANGLE ===
    s = add()
    title(s, [('Slicing is a rectangle', None)])
    body(s, Y_BODY_STD, [
        [('Getting a single cell out of the frame is two brackets and four numbers. '
          'The frame is a list of rows, so the first bracket takes rows and the '
          'second takes columns inside each row:', None)],
    ])
    code(s, 7.8, [
        'frame[y1:y2, x1:x2]',
    ], size=15.0)
    body(s, 10.2, [
        [('The first bracket takes rows, the second takes columns. Row first, '
          'column second — that order is the only thing worth memorising here.',
          None)],
    ])
    body(s, 12.4, [
        [('Order is row first, column second — the only part worth memorising. The '
          'result is a real array, not a view onto the original.', None)],
    ])
    callout(s, 15.8, [
        ('Nothing checks the rectangle is inside the picture.', None),
    ], h=2.8)
    note(s, 19.0, [
        [('The calibration in this project keeps every cell inside the frame, so '
          'this is a thing to know rather than a bug to hit.', None)],
    ], h=1.6)

    # ==================================================== 13. NINE CELLS TO A MATRIX ===
    s = add()
    title(s, [('Nine cells to a matrix', None)])
    body(s, Y_BODY_STD, [
        [('The outer function cuts nine rectangles and calls the first one nine '
          'times. The arithmetic is two lines because the grid is evenly divided:',
          None)],
    ])
    code(s, 7.2, [
        '    for row in range(3):',
        '        for col in range(3):',
        '            x1 = GRID_X_MIN + col * CELL_W',
        '            y1 = GRID_Y_MIN + row * CELL_H',
        '            x2 = x1 + CELL_W',
        '            y2 = y1 + CELL_H',
    ], size=12.5)
    body(s, 11.4, [
        [('Multiplying by the cell size walks across or down; adding the grid origin '
          'converts a cell index into a pixel. Every number in the picture comes '
          'from that one pattern, which is why the drawing code later in the file '
          'looks almost identical.', None)],
    ])
    code(s, 14.8, [
        '            cell_roi = frame[y1:y2, x1:x2]',
        '            board[row][col] = scan_cell(cell_roi)',
    ], size=13.0)
    callout(s, 17.2, [
        ('Look closely at the indexing order: ', None), ('board[row][col]', 'c'),
        (' and ', None), ('x1', 'c'), (' from ', None), ('col', 'c'), (' while ', None),
        ('y1', 'c'), (' comes from ', None), ('row', 'c'),
        ('. Swapping those two is the single most likely mistake in this function, '
         'and it produces a board that is transposed rather than wrong.', None),
    ], h=2.8)

    # ==================================================== 14. ROW, COLUMN, INDEX ===
    s = add()
    title(s, [('Row, column, index', None)])
    body(s, Y_BODY_STD, [
        [('The board is a list of lists, and it starts as nine spaces — already '
          'correct before anything is detected:', None)],
    ])
    code(s, 6.8, [
        '    board = [[\' \' for _ in range(3)] for _ in range(3)]',
    ], size=13.5)
    body(s, 9.0, [
        [('Each ', None), ('_', 'c'),
         (' is a throwaway variable that repeats the inner pattern three times, '
          'giving three separate lists rather than three references to one. The '
          'same question comes up in Project 8.', None)],
    ])
    code(s, 12.6, [
        'board[0][0] = \'X\'',
        'board[2][2] = \'O\'',
    ], size=13.5)
    callout(s, 15.4, [
        ('Printing the board is the fastest possible test of whether the indexing is '
          'right, and it costs one line. Put a token in the top left and check that '
          'it appears in the top left.', None),
    ], h=2.2)
    note(s, 17.8, [
        [('This is the first project where the program holds a description of '
          'something in the world rather than a reaction to it. The list is the '
          'whole point of the project.', None)],
    ], h=2.4)

    # ======================================================= 15. DRAWING THE ANSWER ===
    s = add()
    title(s, [('Drawing the answer', None)])
    body(s, Y_BODY_STD, [
        [('A scanner nobody can check is not much use, so the loop writes its answer '
          'back onto the picture. Three calls:', None)],
    ])
    code(s, 6.8, [
        '                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)',
    ], size=11.5)
    body(s, 8.6, [
        [('Two corners and a thickness. Nine of these produce a grid, and you can '
          'check instantly whether the calibration is right — a grid that is off '
          'the paper is a grid that will misread the paper.', None)],
    ])
    code(s, 11.4, [
        '                if token != \' \':',
        '                    cv2.putText(frame, token, (x1 + CELL_W // 3, y1 + 2 * CELL_H // 3),',
        '                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)',
    ], size=9.5)
    body(s, 14.4, [
        [('The character is written at roughly two thirds across and down, which is '
          'a compromise position that happens to look centred. The ', None),
         ('token != \' \'', 'c'), (' test is what stops nine spaces from being drawn '
          'nine times over empty cells.', None)],
    ])
    callout(s, 17.2, [
        ('The colour is chosen one line earlier from the token itself, which is why '
          'the text is drawn in the same red or blue the detector just found.', None),
    ], h=2.2)

    # ========================================================= 16. TELEMETRY ===
    s = add()
    title(s, [('Telemetry is evidence', None)])
    body(s, Y_BODY_STD, [
        [('One more line of text, placed in the corner, naming what the program '
          'thinks it is doing:', None)],
    ])
    code(s, 6.0, [
        '        cv2.putText(frame, "Tic-Tac-Toe Vision Parser", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)',
    ], size=9.0)
    body(s, 8.0, [
        [('If that line is missing, the window you are looking at is not from this '
          'program. That sounds trivial. It is not — a stale window from a previous '
          'run is the single most common way to spend an hour debugging a program '
          'that is working perfectly.', None)],
    ])
    bullet(s, 11.4, [
        ('It proves the loop reached this line.', 'b'), (' Not a guess — proof.', None),
    ], h=2.0)
    bullet(s, 13.5, [
        ('It gives the frame a version.', 'b'), (' Useful when a behaviour changes '
         'between one run and the next.', None),
    ], h=2.0)
    note(s, 15.6, [
        [('This project prints far less than Project 6 did. There are no counters, '
          'no scores, no state. The evidence here is visual, and the overlay is the '
          'instrument panel.', None)],
    ], h=2.4)
    callout(s, 18.4, [
        ('Two lines in this file make claims about what the program does. One of them '
         'is true. You will find out which, and not from a stack trace.', None),
    ], h=2.0)

    # ==================================================== 17. WHAT SCANNER MEANS ===
    s = add()
    title(s, [('What "scanner" does not mean', None)])
    body(s, Y_BODY_STD, [
        [('It is worth being precise about the scope, because the name suggests more '
          'than the file does. This program does not:', None)],
    ])
    bullet(s, 7.6, [
        ('know the rules', 'b'), ('  — nothing checks for three in a row, and '
         'nothing decides whose turn it is.', None),
    ], h=2.1)
    bullet(s, 9.9, [
        ('move the arm', 'b'), ('  — the arm is powered on and sent home at '
         'startup, then never touched again.', None),
    ], h=2.1)
    bullet(s, 12.2, [
        ('remember anything', 'b'), ('  — the board from the previous frame is '
         'overwritten without ever being compared.', None),
    ], h=2.1)
    bullet(s, 14.5, [
        ('care about perspective', 'b'), ('  — the calibration assumes a flat board '
         'seen from roughly above.', None),
    ], h=2.1)
    callout(s, 17.2, [
        ('Those are not omissions, they are the syllabus. Rules and robot moves are '
         'Project 8. A module that builds a whole game in one file builds something '
         'nobody can debug.', None),
    ], h=2.4)

    # ==================================================== 18. CLAIMS AND EVIDENCE ===
    s = add()
    title(s, [('Claims and evidence', None)])
    body(s, Y_BODY_STD, [
        [('Most of this module has taught you to write code that tells you when it '
          'fails. This project mostly works, and that creates a different problem: '
          'a working program gives you very little to check against.', None)],
        [('So the habit for this week is the Project 6 habit applied to a project '
          'that mostly succeeds. Before you move on, find the claims, write them '
          'down, and verify each one by hand.', None)],
    ])
    callout(s, 10.4, [
        ('Two lines in this program make a statement about behaviour. One of them is '
         'checked every single time you press a key, and you have probably pressed '
         'the key a hundred times without noticing that it does nothing.', None),
    ], h=2.8)
    bullet(s, 13.8, [
        ('A promise made by a program', 'b'), (' is a testable statement, exactly '
         'like a promise made by a person.', None),
    ], h=2.1)
    bullet(s, 16.0, [
        ('A promise that holds', 'b'), (' is worth recording too. It is the only way '
         'to know which of your instincts are reliable.', None),
    ], h=2.1)
    note(s, 18.4, [
        [('Three of the four things this project appears to claim are true, and '
          'verifying those took as much work as catching the false one did.', None)],
    ], h=2.0)

    # ================================================ 19. BEFORE YOU TYPE ANYTHING ===
    s = add()
    title(s, [('Before you type anything', None)])
    body(s, Y_BODY_STD, [
        [('Copy the starter across and run it once before filling in a single TODO. '
          'This is the output, on a machine with no robot attached:', None)],
    ])
    code(s, 6.4, [
        'Robot ready.',
        'Traceback (most recent call last):',
        '  File "M2-P7-Starter.py", line 58, in <module>',
        '    LOWER_RED1 = np.array([0, 120, 100])',
        '                     ^^',
        "NameError: name 'np' is not defined",
    ], size=12.0)
    body(s, 11.4, [
        [('Two things to notice, and the first one is the interesting one.', None)],
    ])
    bullet(s, 12.8, [
        ('It printed "Robot ready." first.', 'b'), ('  That line is outside the '
         'TODO you have not filled in yet, so it runs and reports success before '
         'anything has actually been initialised.', None),
    ], h=2.4)
    bullet(s, 15.4, [
        ('It failed on line 58, not line 131.', 'b'), ('  The first use of ', None),
        ('np', 'c'), (' is in a threshold constant, well before the camera code. '
         'Read errors from the top: the first missing name is the one to fix.', None),
    ], h=2.4)
    note(s, 18.2, [
        [('Nothing here is a bug in your starter file. This is what an empty TODO '
          'looks like, and seeing it once makes the shape of the problem obvious.',
          None)],
    ], h=2.0)

    # ==================================== 20. STEP 1 ===
    s = add()
    title(s, [('Step 1', None), ('  —  ', None), ('import the three libraries', 'y')])
    body(s, Y_BODY_STD, [
        [('The first TODO in the file. Three names you have used in every project '
          'so far:', None)],
    ])
    code(s, 6.6, [
        'import cv2',
        'import numpy as np',
        'import time',
    ], size=15.0)
    bullet(s, 9.8, [
        ('cv2', 'c'), ('  — the OpenCV functions, including everything colour '
         'related.', None),
    ], h=1.9)
    bullet(s, 11.7, [
        ('numpy as np', 'c'), ('  — the arrays that hold the colour thresholds. This '
         'project needs it where Project 6 did not.', None),
    ], h=1.9)
    callout(s, 13.8, [
        ('If you skip this step, the first error you will see is the one from the '
         'previous slide, at line 58 — not at the line you would expect.', None),
    ], h=2.2)
    note(s, 16.6, [
        [('This is the step that removes the ', None), ('NameError', 'c'),
         (' you just watched happen. Same error, same fix, and the error itself told '
          'you exactly which line was missing what.', None)],
    ], h=2.4)

    # ==================================== 21. STEP 2 ===
    s = add()
    title(s, [('Step 2', None), ('  —  ', None), ('import the robot', 'y')])
    body(s, Y_BODY_STD, [
        [('One line. Importing it does not touch the hardware — it only makes the '
          'class available when the ', None), ('try', 'c'), (' block runs.', None)],
    ])
    code(s, 6.6, [
        'from pymycobot.mycobot280 import MyCobot280',
    ], size=15.0)
    body(s, 9.4, [
        [('Two package names, not one. ', None), ('pymycobot', 'c'), (' is the '
          'library; ', None), ('mycobot280', 'c'), (' is the module inside it; ', None),
         ('MyCobot280', 'c'), (' is the class you instantiate. The numbers in the '
          'name are the model number, not a version.', None)],
    ])
    note(s, 12.6, [
        [('This import has to succeed even when you are running without an arm, '
          'because it happens at the top of the file before the ', None), ('try', 'c'),
         (' block gives you any protection at all. The library has to be installed; '
          'the hardware does not.', None)],
    ], h=3.0)
    callout(s, 16.0, [
        ('Remember this project: the arm is initialised and then never used again. '
         'The import is required by the file, not by the task.', None),
    ], h=2.2)

    # ==================================== 22. STEP 3 ===
    s = add()
    title(s, [('Step 3', None), ('  —  ', None), ('connect and power on', 'y')])
    body(s, Y_BODY_STD, [
        [('Inside the ', None), ('try', 'c'),
         (' block that already exists in the file. Identical to Project 6:', None)],
    ])
    code(s, 6.8, [
        '    print("Connecting to myCobot280...")',
        '',
        '    mc = MyCobot280(\'/dev/ttyAMA0\', 1000000)',
        '    time.sleep(0.5)',
        '    mc.power_on()',
        '    time.sleep(0.5)',
    ], size=13.5)
    body(s, 11.2, [
        [('Two numbers that must match your hardware exactly: which serial port, '
          'and at what baud rate. The sleeps are there so the board can finish '
          'booting and acknowledge the power command before you send anything else.',
          None)],
    ])
    note(s, 14.4, [
        [('If the arm is not connected, the constructor raises, the ', None),
         ('except', 'c'), (' block runs, and the program continues. We will come back '
          'to whether that promise is actually kept.', None)],
    ], h=2.4)

    # ==================================== 23. STEP 4 ===
    s = add()
    title(s, [('Step 4', None), ('  —  ', None), ('move to the home pose', 'y')])
    body(s, Y_BODY_STD, [
        [('Three lines. The pose is different from Project 6, and the reason is '
          'given in the comment above it:', None)],
    ])
    code(s, 6.6, [
        '    home_pos = [0, 45, -90, -45, 0, 0]',
        '    mc.send_angles(home_pos, 50)',
        '    time.sleep(2.0)',
    ], size=14.5)
    body(s, 9.6, [
        [('This is the folded position, defined by the module for this project so '
          'the arm is out of the way of the board the camera is looking at. The '
          'shape of the list is six joint angles, and ', None), ('50', 'c'),
         (' is a deliberately slow speed.', None)],
    ])
    callout(s, 13.0, [
        ('Compare with Project 6, where the pose lived at module level because two '
         'functions needed it. Here it is defined inside the ', None), ('try', 'c'),
         (' block and never used again — so its position in the file causes no '
          'problem at all. The rule is about use, not about where code sits.', None),
    ], h=2.8)
    note(s, 16.2, [
        [('This is the last time you touch the arm in this entire project.', None)],
    ], h=1.4)

    # ==================================== 24. STEP 5 ===
    s = add()
    title(s, [('Step 5', None), ('  —  ', None), ('calculate the grid', 'y')])
    body(s, Y_BODY_STD, [
        [('The first TODO with real arithmetic in it. The constants above it are '
          'given to you, and they are the calibration:', None)],
    ])
    code(s, 6.6, [
        'GRID_SCALE = 0.75       # Scale factor for grid size (1.0 = original)',
        'GRID_OFFSET_X = -10      # Horizontal offset in pixels (+X = right)',
        'GRID_OFFSET_Y = -70      # Vertical offset in pixels (+Y = down)',
        '',
        '_BASE_GRID_X_MIN, _BASE_GRID_X_MAX = 170, 470',
        '_BASE_GRID_Y_MIN, _BASE_GRID_Y_MAX = 90, 390',
    ], size=11.0)
    body(s, 11.0, [
        [('Three numbers to change if your board is in the wrong place or the wrong '
          'size, and the TODO turns them into the four corners the rest of the '
          'program uses:', None)],
    ])
    code(s, 13.6, [
        'grid_w = (_BASE_GRID_X_MAX - _BASE_GRID_X_MIN) * GRID_SCALE',
        'grid_h = (_BASE_GRID_Y_MAX - _BASE_GRID_Y_MIN) * GRID_SCALE',
        'center_x = (_BASE_GRID_X_MIN + _BASE_GRID_X_MAX) / 2',
        'center_y = (_BASE_GRID_Y_MIN + _BASE_GRID_Y_MAX) / 2',
        '',
        'GRID_X_MIN = int(center_x - grid_w / 2 + GRID_OFFSET_X)',
        'GRID_X_MAX = int(center_x + grid_w / 2 + GRID_OFFSET_X)',
        'GRID_Y_MIN = int(center_y - grid_h / 2 + GRID_OFFSET_Y)',
        'GRID_Y_MAX = int(center_y + grid_h / 2 + GRID_OFFSET_Y)',
    ], size=9.5)
    note(s, 18.6, [
        [('With the shipped numbers that is X 197 to 422, Y 57 to 282 — well inside '
          'a 640x480 frame.', None)],
    ], h=2.6)

    # ==================================== 25. STEP 6 ===
    s = add()
    title(s, [('Step 6', None), ('  —  ', None), ('divide into three', 'y')])
    body(s, Y_BODY_STD, [
        [('A 3x3 board is just a region divided three times. Two lines:', None)],
    ])
    code(s, 6.6, [
        'CELL_W = (GRID_X_MAX - GRID_X_MIN) // 3',
        'CELL_H = (GRID_Y_MAX - GRID_Y_MIN) // 3',
    ], size=15.0)
    body(s, 9.4, [
        [('225 pixels wide and 225 tall, so each cell is exactly 75 by 75. That '
          'number is the one that matters later, because it is the denominator for '
          'the colour threshold.', None)],
    ])
    bullet(s, 12.4, [
        ('The double slash', 'b'), (' is floor division. It guarantees a whole '
         'number, which matters because the two results are subtracted from each '
         'other when the last cell is cut.', None),
    ], h=2.3)
    bullet(s, 14.9, [
        ('If the region is not evenly divisible', 'b'), (', floor division throws '
         'away the remainder rather than making one cell a pixel wider. A tiny '
         'error, and much better than nine mismatched cells.', None),
    ], h=2.3)
    note(s, 17.6, [
        [('Work out the value of 800 against 5,625 pixels now, before you need it '
          'later. It is a percentage, and knowing the percentage is what makes the '
          'threshold adjustable rather than magic.', None)],
    ], h=2.6)

    # ==================================== 26. STEP 7 ===
    s = add()
    title(s, [('Step 7', None), ('  —  ', None), ('the cell function', 'y')])
    body(s, Y_BODY_STD, [
        [('The signature and the docstring are inside this TODO, along with the '
          'conversion that turns a colour question into a hue question:', None)],
    ])
    code(s, 7.2, [
        'def scan_cell(cell_roi):',
        '    """Inspects a single cell ROI and returns \'X\', \'O\', or \' \'."""',
        '    hsv = cv2.cvtColor(cell_roi, cv2.COLOR_BGR2HSV)',
    ], size=12.5)
    body(s, 10.8, [
        [('The docstring is not decoration. It states the return contract — three '
          'possible values — before a single line of logic exists, which is the '
          'cheapest way to make a function testable.', None)],
    ])
    callout(s, 13.6, [
        ('This function will be called nine times per frame, so it is written to be '
          'completely ignorant of the board. It receives a picture and returns a '
          'character. It has no idea nine of its answers will be assembled into '
          'rows.', None),
    ], h=2.8)
    note(s, 17.0, [
        [('If you wanted to test this function without a camera, you would save one '
          'cell as a small image file and call ', None), ('scan_cell', 'c'),
         (' on it. Separating the question from the input is what makes that possible.',
          None)],
    ], h=2.4)

    # ==================================== 27. STEP 8 ===
    s = add()
    title(s, [('Step 8', None), ('  —  ', None), ('the red mask', 'y')])
    body(s, Y_BODY_STD, [
        [('Two ranges because red wraps around the hue scale, and a combination '
          'step because two ranges make two masks:', None)],
    ])
    code(s, 6.8, [
        '    # Red Mask (handles HSV wraparound)',
        '    mask_red1 = cv2.inRange(hsv, LOWER_RED1, UPPER_RED1)',
        '    mask_red2 = cv2.inRange(hsv, LOWER_RED2, UPPER_RED2)',
        '    mask_red = cv2.bitwise_or(mask_red1, mask_red2)',
    ], size=12.0)
    body(s, 10.4, [
        [('Each ', None), ('inRange', 'c'),
         (' call produces a full-size black and white picture. The fourth line '
          'merges them into one mask that answers a single question: is this pixel '
          'red enough to count?', None)],
    ])
    callout(s, 13.6, [
        ('The comment is the documentation here, and it is load-bearing. Without '
         'the word "wraparound" the next reader sees a redundant-looking pair of '
         'masks and is likely to "simplify" them into one broken range.', None),
    ], h=2.6)
    note(s, 16.6, [
        [('This is the third project in a row that uses this exact pattern. It is '
          'worth being able to write it without looking.', None)],
    ], h=1.6)

    # ==================================== 28. STEP 9 ===
    s = add()
    title(s, [('Step 9', None), ('  —  ', None), ('the blue mask', 'y')])
    body(s, Y_BODY_STD, [
        [('Blue sits in the middle of the hue scale and wraps around nothing, so '
          'one range is genuinely enough:', None)],
    ])
    code(s, 6.8, [
        '    # Blue Mask',
        '    mask_blue = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)',
    ], size=14.0)
    body(s, 9.4, [
        [('The thresholds are given to you above the function. Read them as three '
          'questions: is the hue between 90 and 130, is the saturation at least '
          '120, is the brightness at least 100.', None)],
    ])
    note(s, 12.4, [
        [('The saturation floor is doing more work than the hue range. Pale blue '
          'and grey-blue pixels have a correct hue but a saturation below 120, and '
          'the floor is what rejects them.', None)],
    ], h=2.8)
    callout(s, 15.6, [
        ('Two ranges for one colour and one range for another is not inconsistent '
         '— it is the shape of the hue scale deciding how many slices the colour '
         'needs. Red sits at both ends, blue at one.', None),
    ], h=2.6)

    # ==================================== 29. STEP 10 ===
    s = add()
    title(s, [('Step 10', None), ('  —  ', None), ('count the pixels', 'y')])
    body(s, Y_BODY_STD, [
        [('The simplest line in the project, and the one that turns a picture into '
          'something comparable:', None)],
    ])
    code(s, 6.6, [
        '    red_pixels = cv2.countNonZero(mask_red)',
        '    blue_pixels = cv2.countNonZero(mask_blue)',
    ], size=14.0)
    body(s, 9.4, [
        [('Two integers. Everything downstream is a comparison between them and a '
          'constant, which means you could debug this entire project by printing '
          'numbers instead of looking at pictures.', None)],
    ])
    callout(s, 12.6, [
        ('Do that when it misbehaves. Print ', None), ('red_pixels', 'c'), (' and ',
         None), ('blue_pixels', 'c'), (' for one cell and you learn far more than '
         'from staring at the window. A count of 0 means the colour was never in '
         'range; a count of 200 means it was, but not enough.', None),
    ], h=3.0)
    note(s, 16.0, [
        [('Also print ', None), ('cell_roi.shape', 'c'),
         (' if a cell seems to be reading wrong for no obvious reason. The shape '
          'tells you whether the region you cut was the size you expected.', None)],
    ], h=2.4)

    # ==================================== 30. STEP 11 ===
    s = add()
    title(s, [('Step 11', None), ('  —  ', None), ('decide the token', 'y')])
    body(s, Y_BODY_STD, [
        [('The threshold is already defined above this TODO. Your job is the logic '
          'that uses it:', None)],
    ])
    code(s, 6.4, [
        '    if red_pixels > MIN_PIXELS and red_pixels > blue_pixels:',
        '        return \'X\'',
        '    elif blue_pixels > MIN_PIXELS and blue_pixels > red_pixels:',
        '        return \'O\'',
        '    return \' \'',
    ], size=13.0)
    bullet(s, 10.4, [
        ('First half of each test', 'b'), ('  — is this colour present at all? Below '
         '800 pixels is noise, whatever colour it is.', None),
    ], h=2.1)
    bullet(s, 12.7, [
        ('Second half', 'b'), ('  — which colour dominates? A cell can easily hold '
         'more than 800 pixels of both.', None),
    ], h=2.1)
    callout(s, 15.2, [
        ('The final ', None), ('return', 'c'), (' is not a fallback — it is the '
         'normal case. Nine out of ten cells on an empty board land here, and an '
         'empty cell should be the easiest thing this function can return.', None),
    ], h=2.6)

    # ==================================== 31. STEP 12 ===
    s = add()
    title(s, [('Step 12', None), ('  —  ', None), ('the board function', 'y')])
    body(s, Y_BODY_STD, [
        [('The signature is in this TODO. The rest of the function is already '
          'written for you above it:', None)],
    ])
    code(s, 6.4, [
        'def parse_board_state(frame):',
        '    """Scans all 9 grid cells and returns a 3x3 matrix."""',
    ], size=13.0)
    code(s, 9.4, [
        '    for row in range(3):',
        '        for col in range(3):',
        '            x1 = GRID_X_MIN + col * CELL_W',
        '            y1 = GRID_Y_MIN + row * CELL_H',
        '            x2 = x1 + CELL_W',
        '            y2 = y1 + CELL_H',
    ], size=12.5)
    code(s, 13.0, [
        '            cell_roi = frame[y1:y2, x1:x2]',
        '            board[row][col] = scan_cell(cell_roi)',
    ], size=13.0)
    note(s, 15.6, [
        [('All you typed is the function header. The behaviour was already decided; '
          'your job was to make it callable.', None)],
    ], h=2.4)
    callout(s, 18.2, [
        ('That is not a shortcut, it is the shape of the project: assemble '
         'logic that was already right.', None),
    ], h=2.4)

    # ==================================== 32. STEP 13 ===
    s = add()
    title(s, [('Step 13', None), ('  —  ', None), ('open the camera', 'y')])
    body(s, Y_BODY_STD, [
        [('Three lines, and the last two are new for this module:', None)],
    ])
    code(s, 6.6, [
        'cap = cv2.VideoCapture(0)',
        'cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)',
        'cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)',
    ], size=13.5)
    body(s, 10.0, [
        [('A plain ', None), ('VideoCapture', 'c'), (', not the threaded class '
         'from Project 6. Nothing in this loop blocks for long enough to need a '
          'thread, and a plain capture keeps the code short.', None)],
    ])
    callout(s, 13.2, [
        ('The 640x480 request is not a suggestion. ', None), ('GRID_SCALE', 'c'),
        (', the offsets, and ', None), ('MIN_PIXELS', 'c'),
        (' are all calibrated against a 640x480 frame. OpenCV will often give you a '
         'different size anyway, and the calibration constants are what you adjust '
         'when it does.', None),
    ], h=2.8)
    note(s, 16.4, [
        [('Print ', None), ('frame.shape', 'c'),
         (' once if the grid lands in the wrong place. The camera ignoring your '
          'requested resolution is a common and confusing source of that.', None)],
    ], h=2.4)

    # ==================================== 33. STEP 14 ===
    s = add()
    title(s, [('Step 14', None), ('  —  ', None), ('open the loop', 'y')])
    body(s, Y_BODY_STD, [
        [('Two lines, and the ', None), ('try', 'c'),
         (' above them is already in the file:', None)],
    ])
    code(s, 6.6, [
        'try:',
        '    while cap.isOpened():',
    ], size=15.0)
    body(s, 9.4, [
        [('The loop tests whether the capture is still open, not whether there is a '
          'picture — that distinction matters at Step 15.', None)],
    ])
    note(s, 12.0, [
        [('The ', None), ('finally', 'c'), (' block at the bottom is paired with '
          'this ', None), ('try', 'c'),
         (': it releases the camera and closes the window whatever way you '
          'leave the loop.', None)],
    ], h=2.4)
    code(s, 13.0, [
        'finally:',
        '    cap.release()',
        '    cv2.destroyAllWindows()',
    ], size=13.0)
    note(s, 17.2, [
        [('Those are the only two lines in that block, and both are things that '
          'exist — note the total absence of the arm.', None)],
    ], h=2.2)
    callout(s, 15.4, [
        ('Code under the ', None), ('while', 'c'),
        (' runs every frame, until you break out.', None),
    ], h=1.6)

    # ==================================== 34. STEP 15 ===
    s = add()
    title(s, [('Step 15', None), ('  —  ', None), ('read a frame', 'y')])
    body(s, Y_BODY_STD, [
        [('The first thing that happens in every iteration:', None)],
    ])
    code(s, 6.6, [
        '        ret, frame = cap.read()',
        '        if not ret:',
        '            break',
    ], size=14.0)
    body(s, 9.4, [
        [('Two return values, and the first is the one people forget. ', None),
         ('ret', 'c'), (' is a boolean saying whether a picture was actually '
          'delivered; ', None), ('frame', 'c'), (' is the picture itself, or ', None),
         ('None', 'c'), (' if it failed.', None)],
    ])
    callout(s, 12.6, [
        ('The three lines are a set, not a sequence. Calling ', None), ('read', 'c'),
        (' without checking ', None), ('ret', 'c'),
        (' means the next line tries to slice a picture that does not exist. This '
          'is the difference between a camera that is unplugged mid-run and a '
          'program that stops with a sensible message.', None),
    ], h=3.0)
    note(s, 16.0, [
        [('This is the same lesson as Project 5, where a dropped frame produced a '
          'confusing colour error instead of an obvious camera error.', None)],
    ], h=2.4)

    # ==================================== 35. STEP 16 ===
    s = add()
    title(s, [('Step 16', None), ('  —  ', None), ('parse the board', 'y')])
    body(s, Y_BODY_STD, [
        [('One line, and it is the point of the whole project:', None)],
    ])
    code(s, 6.6, [
        '        board_state = parse_board_state(frame)',
    ], size=15.0)
    body(s, 9.4, [
        [('Nine colour tests, returning a 3x3 list of characters. From this line '
          'onward, the program has an answer it can reason about rather than a '
          'picture it has to keep re-examining.', None)],
    ])
    bullet(s, 12.4, [
        ('The name is different from the function.', 'b'), (' ', None),
        ('parse_board_state', 'c'), (' is the function; ', None),
        ('board_state', 'c'), (' is this frame\'s result. The underscore is doing '
         'real work there.', None),
    ], h=2.3)
    callout(s, 15.4, [
        ('You now have a truth about the board, nine times a second, in a form that '
         'could drive a robot. Everything after this line is either drawing it or '
         'showing it to a human.', None),
    ], h=2.4)

    # ==================================== 36. STEP 17 ===
    s = add()
    title(s, [('Step 17', None), ('  —  ', None), ('draw the grid', 'y')])
    body(s, Y_BODY_STD, [
        [('You are inside the given double loop that walks the nine cells, one line '
          'below where ', None), ('board_state', 'c'), (' came from. Its own TODO is '
          'a single call:', None)],
    ])
    code(s, 8.4, [
        '                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)',
    ], size=12.0)
    body(s, 10.6, [
        [('Look at where ', None), ('x1', 'c'), (', ', None), ('y1', 'c'), (', ', None),
         ('x2', 'c'), (' and ', None), ('y2', 'c'),
         (' come from. They are the given code in that loop, and they are the same '
          'four values ', None), ('parse_board_state', 'c'),
         (' used to cut the cells. One set of numbers, used twice, for cutting and '
          'for drawing.', None)],
    ])
    callout(s, 14.4, [
        ('That is why the grid appears exactly where the detection happened. If the '
          'white outline sits on your drawn lines, the calibration is right. If it '
          'does not, no amount of threshold tuning will fix anything.', None),
    ], h=2.8)
    note(s, 17.6, [
        [('Drawing is a debugging tool before it is a user interface.', None)],
    ], h=1.2)

    # ==================================== 37. STEP 18 ===
    s = add()
    title(s, [('Step 18', None), ('  —  ', None), ('draw the token', 'y')])
    body(s, Y_BODY_STD, [
        [('The last multi-line TODO. Text, positioned inside the cell it belongs '
          'to:', None)],
    ])
    code(s, 7.0, [
        '                if token != \' \':',
        '                    cv2.putText(frame, token, (x1 + CELL_W // 3, y1 + 2 * CELL_H // 3),',
        '                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)',
    ], size=10.0)
    body(s, 10.6, [
        [('Three arguments carry most of the meaning: the character to draw, where '
          'to draw it, and how big to draw it. The position is computed from ', None),
         ('CELL_W', 'c'), (' and ', None), ('CELL_H', 'c'),
         (', so the text lands inside the right cell for any calibration.', None)],
    ])
    note(s, 13.8, [
        [('The ', None), ('if', 'c'), (' test above it is what keeps nine empty '
          'spaces from being drawn nine times. Without it you get a board covered '
          'in faint grey spaces.', None)],
    ], h=2.4)
    callout(s, 16.6, [
        ('The character is drawn in red or blue because ', None), ('color', 'c'),
        (' was chosen from the detected token, not hard-coded. The picture is '
          'reporting its own finding back to you in colour.', None),
    ], h=2.6)

    # ==================================== 38. STEP 19 ===
    s = add()
    title(s, [('Step 19', None), ('  —  ', None), ('write the telemetry', 'y')])
    body(s, Y_BODY_STD, [
        [('One line, positioned in the corner of the frame rather than inside the '
          'grid:', None)],
    ])
    code(s, 6.2, [
        '        cv2.putText(frame, "Tic-Tac-Toe Vision Parser", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)',
    ], size=9.0)
    body(s, 8.4, [
        [('Different from the other two ', None), ('putText', 'c'),
         (' calls in this file: smaller scale, thinner line, fixed coordinates, and '
          'no test in front of it. That last part is the design decision — it is '
          'unconditional, so it is on screen every single frame.', None)],
    ])
    callout(s, 12.0, [
        ('This line is also how you tell this program apart from any other OpenCV '
          'window you might have open. It names itself, once, every frame.', None),
    ], h=2.2)

    # ==================================== 39. STEP 20 ===
    s = add()
    title(s, [('Step 20', None), ('  —  ', None), ('show the frame', 'y')])
    body(s, Y_BODY_STD, [
        [('The last TODO in the file:', None)],
    ])
    code(s, 6.6, [
        '        cv2.imshow("Mission 02 - Project 07: Board State Scanner", frame)',
    ], size=12.0)
    body(s, 9.4, [
        [('Two arguments: a window title and the picture. The title is the one thing '
          'that identifies your program in the taskbar, and the string in it is the '
          'only place the project name appears on screen.', None)],
    ])
    note(s, 12.6, [
        [('Notice this is not drawing — ', None), ('imshow', 'c'),
         (' puts the finished frame on screen. Everything before it modifies the '
          'frame in memory; this line is what you actually look at.', None)],
    ], h=2.8)

    # ==================================== 40. STEP 21 ===
    s = add()
    title(s, [('Step 21', None), ('  —  ', None), ('read the keyboard', 'y')])
    body(s, Y_BODY_STD, [
        [('The final TODO is the display line above. These two lines come with it, '
          'already written in the file:', None)],
    ])
    code(s, 6.8, [
        '        if (cv2.waitKey(1) & 0xFF) == ord(\'q\'):',
        '            break',
    ], size=14.0)
    body(s, 9.8, [
        [('Three things happening in one line. ', None), ('waitKey(1)', 'c'),
         (' waits about a millisecond and returns a key code. ', None),
         ('& 0xFF', 'c'), (' masks that code down to eight bits. ', None),
         ("== ord('q')", 'c'), (' compares it to the character q.', None)],
    ])
    bullet(s, 13.2, [
        ('The wait is what makes the window responsive.', 'b'), (' Without it the '
         'picture freezes and no key is ever read.', None),
    ], h=2.1)
    bullet(s, 15.5, [
        ('The mask is not optional.', 'b'), (' Key codes can carry more than eight '
         'bits, and unmasked values will occasionally match 113 by accident.', None),
    ], h=2.1)
    callout(s, 18.0, [
        ('Read that first line carefully, including the brackets. The exact '
         'parenthesisation is load-bearing, and there is a reason for it that we '
         'are about to look at.', None),
    ], h=2.0)

    # ==================================== 41. RUN IT ===
    s = add()
    title(s, [('Run it', None)])
    body(s, Y_BODY_STD, [
        [('Send the file across and start it:', None)],
    ])
    command(s, 5.6, SCP)
    command(s, 6.7, RUN)
    body(s, 8.4, [
        [('Expected console output:', None)],
    ])
    code(s, 10.0, [
        'Connecting to myCobot280...',
        'Robot ready.',
        'Starting Tic-Tac-Toe Vision Scanner. Press \'q\' to quit.',
    ], size=12.5)
    body(s, 13.6, [
        [('Then a window opens with your camera feed, a white grid, and the '
          'telemetry line in the top left. Place a red token in a cell and the '
          'letter X appears on it.', None)],
    ])
    callout(s, 16.2, [
        ('Three claims have now been made about this program. Two of them are about '
          'your setup; one is about the keyboard. All three are checkable by hand, '
          'and we are going to check them.', None),
    ], h=2.4)

    # ==================================== 42. VERIFY THE CLAIMS ===
    s = add()
    title(s, [('Verify the claims', None)])
    body(s, Y_BODY_STD, [
        [('Three claims. Checked one at a time, without changing any code.', None)],
    ])
    table(s, 6.4, [
        ['#', 'The claim', 'Result'],
        ['1', 'Runs without the robot attached', 'True'],
        ['2', 'Identifies X and O correctly', 'True'],
        ['3', 'Press q to quit', 'False'],
    ], [1.4, 10.6, 4.6])
    body(s, 12.6, [
        [('The first one deserves a note. It is the promise that was a lie in Project '
          '6, so it was the obvious one to suspect — and it holds.', None)],
    ])
    callout(s, 15.0, [
        ('Verify every claim, not the ones you already distrust. The instinct to '
         'find a specific bug is not evidence, and a program that fails the test '
         'you expected is as surprising as one that passes.', None),
    ], h=2.6)

    # ==================================== 43. CLAIM 1 HOLDS ===
    s = add()
    title(s, [('Claim 1', None), ('  —  ', None), ('the fallback holds', 'y')])
    body(s, Y_BODY_STD, [
        [('Unplug the arm, run the program, and this is what you get:', None)],
    ])
    code(s, 6.4, [
        'Robot hardware warning: [Errno 2] No such file or directory: \'/dev/ttyAMA0\'',
        'Continuing with OpenCV camera pipeline only...',
        '',
        'Starting Tic-Tac-Toe Vision Scanner. Press \'q\' to quit.',
    ], size=11.0)
    body(s, 10.4, [
        [('The program does keep going. Here is why, and the reason is structural '
          'rather than lucky:', None)],
    ])
    bullet(s, 12.6, [
        ('mc is only used inside the try block.', 'b'), (' Search the file after the '
         'handler and you will not find one.', None),
    ], h=2.3)
    bullet(s, 15.0, [
        ('The finally block does not touch it.', 'b'), (' That block releases the '
         'camera and closes the window — two things that always exist.', None),
    ], h=2.3)
    callout(s, 18.0, [
        ('Same message, same file shape, opposite outcome to Project 6. Identical '
         'wording tells you nothing; what the code does after the print is the '
         'whole answer.', None),
    ], h=2.0)

    # ==================================== 44. CLAIM 2 HOLDS ===
    s = add()
    title(s, [('Claim 2', None), ('  —  ', None), ('four things lined up', 'y')])
    body(s, Y_BODY_STD, [
        [('The claim that the project\'s whole purpose rests on: red pieces read as '
          'X, blue pieces as O, empty cells as nothing.', None)],
    ])
    body(s, 7.0, [
        [('Four properties had to be true at once for that claim to hold:', None)],
    ])
    question_item(s, 8.6, 1, [
        ('The hue wraparound was handled.', 'b'), ('  Two ranges and a ', None),
        ('bitwise_or', 'c'), (', so the 0 end and the 180 end of the scale are both '
         'reachable.', None)])
    question_item(s, 11.2, 2, [
        ('The calibration put every cell inside the frame.', 'b'),
        ('  X 197 to 422 and Y 57 to 282 in a 640x480 picture.', None)])
    question_item(s, 13.4, 3, [
        ('The threshold matched the cell size.', 'b'),
        ('  800 of 5,625 pixels, about 14%.', None)])
    question_item(s, 15.6, 4, [
        ('Row and column were not swapped.', 'b'), ('  ', None),
        ('board[row][col]', 'c'), (' fed by ', None), ('y1', 'c'), (' from ', None),
        ('row', 'c'), (' and ', None), ('x1', 'c'), (' from ', None), ('col', 'c'),
        ('.', None)])
    note(s, 18.4, [
        [('Any one of those failing would produce a board that reads wrong in a way '
          'that looks like a colour problem. Four independent things had to be right, '
          'and all four were.', None)],
    ], h=2.4)

    # ==================================== 45. CLAIM 3 FAILS ===
    s = add()
    title(s, [('Claim 3', None), ('  —  ', None), ('the key that did nothing', 'y')])
    body(s, Y_BODY_STD, [
        [('The program announces its exit condition before it starts:', None)],
    ])
    code(s, 5.8, [
        'print("Starting Tic-Tac-Toe Vision Scanner. Press \'q\' to quit.")',
    ], size=11.0)
    body(s, 7.6, [
        [('Press q during a run and the scanner keeps going. Press it twenty times. '
          'Nothing happens — no error, no message, no crash. The window has to be '
          'closed with the mouse or the program killed from another terminal.', None)],
    ])
    body(s, 11.0, [
        [('This is the version from before this project was corrected:', None)],
    ])
    code(s, 12.6, [
        '        if cv2.waitKey(1) & 0xFF == ord(\'q\'):',
        '            break',
    ], size=14.0)
    note(s, 14.8, [
        [('The corrected file you have now reads ', None),
         ('if (cv2.waitKey(1) & 0xFF) == ord(\'q\'):', 'c'),
         (' — identical apart from two brackets, which is exactly the point: the '
          'bug is the absence of something, and absence is easy to miss.', None)],
    ], h=2.4)

    # ==================================== 46. WHY BRACKETS MATTER ===
    s = add()
    title(s, [('Why two brackets matter', None)])
    body(s, Y_BODY_STD, [
        [('Python does not read that line the way it looks. Comparisons bind tighter '
          'than bitwise operators, so the line groups as:', None)],
    ])
    code(s, 7.4, [
        'cv2.waitKey(1)  &  (0xFF == ord(\'q\'))',
    ], size=15.0)
    body(s, 9.8, [
        [('The mask and the comparison swap places. Which makes the second half a '
          'constant, evaluated once and never again:', None)],
    ])
    code(s, 12.4, [
        '0xFF == 113   ->   False',
        'waitKey(1) & False   ->   0',
    ], size=14.0)
    body(s, 15.0, [
        [('And ', None), ('0', 'c'), (' is false, so the condition is never true and '
          'the ', None), ('break', 'c'), (' is unreachable. Every key, every frame, '
          'forever.', None)],
    ])
    callout(s, 18.0, [
        ('This is the most dangerous kind of bug: not a crash, not a wrong number, '
         'but a line that reads plausibly and evaluates to nothing at all.', None),
    ], h=2.0)

    # ==================================== 47. WHAT IT COST ===
    s = add()
    title(s, [('What that actually cost', None)])
    body(s, Y_BODY_STD, [
        [('Worth being concrete about the price of two missing brackets, because '
          '"the quit key did not work" undersells it.', None)],
    ])
    bullet(s, 7.4, [
        ('The frame loop could not be left cleanly.', 'b'), ('  The only exit was '
         'killing the process, so the ', None), ('finally', 'c'),
         (' block never ran and the camera was not released.', None),
    ], h=2.5)
    bullet(s, 10.3, [
        ('Ctrl+C raised KeyboardInterrupt', 'b'), (' partway through, which means '
         'the loop died wherever it happened to be rather than at a known point.',
         None),
    ], h=2.5)
    bullet(s, 13.2, [
        ('The camera stayed claimed by the process.', 'b'), (' Running again quickly '
         'produced a camera that would not open — a second failure caused entirely '
         'by the first.', None),
    ], h=2.5)
    bullet(s, 16.1, [
        ('The banner taught a lie.', 'b'), (' Anyone reading the printed instructions '
         'was told q worked. It did not, and nothing on screen suggested otherwise.',
         None),
    ], h=2.5)
    note(s, 18.0, [
        [('None of that is visible in the line itself. It appears only when you '
          'trace what the expression evaluates to.', None)],
    ], h=1.8)

    # ==================================== 48. THE HABIT ===
    s = add()
    title(s, [('The habit', None)])
    body(s, Y_BODY_STD, [
        [('One bug, and it was found by the same method that found four in Project '
          '6: write down what the program claims, then go and check.', None)],
    ])
    bullet(s, 7.0, [
        ('Printed text is a promise.', 'y'), ('  A banner telling you how to exit '
         'is testable in ten seconds, and nobody tests it.', None),
    ], h=2.4)
    bullet(s, 9.5, [
        ('Check the claims you expect to pass.', 'y'), ('  Two of the three here '
         'were true, and confirming them is what made the third credible.', None),
    ], h=2.4)
    bullet(s, 12.0, [
        ('Brackets are not formatting.', 'y'), ('  Grouping in an expression is '
         'part of the meaning, and it is invisible at a glance.', None),
    ], h=2.4)
    note(s, 15.0, [
        [('This project was almost entirely correct. That is worth saying plainly, '
          'because the temptation after a quiet bug is to assume the file is full of '
          'them. It is not. One claim out of three was false, and it was the one '
          'nobody had any reason to doubt.', None)],
    ], h=3.2)
    callout(s, 18.8, [
        ('A program that mostly works is harder to check than one that crashes, '
         'because a crash tells you where to look.', None),
    ], h=1.6)

    # ==================================== 49. THE BRIEF ===
    s = add()
    title(s, [('The Brief', None)])
    body(s, Y_BODY_STD, [
        [('Read the Board', 'y'), ('\n', None)],
        [('Nine squares. Each one is cut out of a camera frame, converted to a colour '
          'space where hue is meaningful, reduced to two pixel counts, and turned '
          'into a single character.', None)],
        [('Do that nine times and you have the state of a game — which is the only '
          'thing a tic-tac-toe program actually needs to know. Not the picture. '
          'The state.', None)],
        [('Which means this project is mostly arithmetic, and the arithmetic is the '
          'part that has to be right.', None)],
    ])

    # ==================================== 50. YOUR MISSION ===
    s = add()
    title(s, [('Your Mission', None)])
    body(s, Y_BODY_STD, [
        [('Three parts, in order.', None)],
    ])
    question_item(s, 6.8, 1, [
        ('Recalibrate.', 'b'), ('  Change ', None), ('GRID_SCALE', 'c'), (' and the '
         'two offsets until the white grid lands on your drawn board. Record the '
         'three values you ended up with.', None)])
    question_item(s, 9.6, 2, [
        ('Move the threshold.', 'b'), ('  Set ', None), ('MIN_PIXELS', 'c'),
        (' low enough to read a piece that is only a corner of its cell, then work '
         'backwards to the highest value that still works. Record the number.', None)])
    question_item(s, 12.4, 3, [
        ('Break a claim on purpose.', 'b'), ('  Put both tokens in the same cell and '
         'record which one wins and why. Then take a piece away and record which '
         'count decides it.', None)])
    note(s, 15.4, [
        [('All three are about the relationship between a number and what it means '
          'in the physical world — which is the actual subject of this project, and '
          'the reason it is not just an OpenCV exercise.', None)],
    ], h=2.6)
    callout(s, 18.4, [
        ('Somewhere in part 3 you will find yourself wanting to press q to get out. '
         'It works. That was not always true.', None),
    ], h=1.6)

    # ==================================== 51. YOUR DATA LOG ===
    s = add()
    title(s, [('Your Data Log', None)])
    table(s, 6.6, [
        ['Measurement', 'Your value', 'What you changed'],
        ['GRID_SCALE', '', ''],
        ['GRID_OFFSET_X', '', ''],
        ['GRID_OFFSET_Y', '', ''],
        ['MIN_PIXELS', '', ''],
        ['Cell size (W x H)', '', ''],
    ], [5.6, 4.4, 6.5], row_h=1.75)
    note(s, 17.2, [
        [('Write MIN_PIXELS as a percentage of the cell, not as a bare number. The '
          'whole point of Step 11 was that 800 is really 14% — a percentage '
          'survives a change of resolution and a bare integer does not.', None)],
    ], h=2.6)

    # ==================================== 52. DEFINITION OF DONE ===
    s = add()
    title(s, [('Definition of Done', None)])
    check_item(s, 6.8, [('All twenty-one TODOs filled in and the file runs on the Pi.',
                         None)])
    check_item(s, 8.6, [('No ', None), ('TODO', 'c'),
                        (' markers left anywhere in the file.', None)])
    check_item(s, 10.4, [('The white grid sits on your drawn board, in every cell.', None)])
    check_item(s, 12.2, [('A red piece reads as X and a blue piece as O, from any '
                         'position in the frame.', None)])
    check_item(s, 14.0, [('An empty cell stays empty even under a shadow.', None)])
    check_item(s, 15.8, [('q quits the program and the camera is released cleanly.', None)])
    callout(s, 17.8, [
        ('That last one is the difference between this file and the version it was '
         'corrected from. Both of them draw the board correctly.', None),
    ], h=2.0)

    # ==================================== 53. GO FURTHER ===
    s = add()
    title(s, [('Go Further', None)])
    bullet(s, 6.8, [
        ('Break the calibration.', 'b'), ('  Set ', None), ('GRID_OFFSET_Y', 'c'),
        (' far enough off that cells fall outside the frame, and find out what a '
         'mis-sized ROI does to ', None), ('cvtColor', 'c'), ('.', None),
    ], h=2.3)
    bullet(s, 9.1, [
        ('Report the counts.', 'b'), ('  Print ', None), ('red_pixels', 'c'),
        (' and ', None), ('blue_pixels', 'c'), (' for the centre cell each frame, and '
         'watch them move as you slide a piece across it.', None),
    ], h=2.3)
    bullet(s, 11.4, [
        ('Notice the dead branch.', 'b'), ('  The ', None), ('color', 'c'),
        (' value for an empty cell is computed on every iteration and then never '
         'used. Find every one of those in your own code.', None),
    ], h=2.3)
    bullet(s, 13.7, [
        ('Compare consecutive frames.', 'b'), ('  Keep the last board and report '
         'only when it changes. That is the first step towards not re-reading a '
         'board that has not moved.', None),
    ], h=2.3)
    note(s, 16.2, [
        [('Pick one. Not all four.', None)],
    ], h=1.0)

    # ==================================== 54. DEBRIEF ===
    s = add(0, master=1)
    title(s, [('Debrief', None)], ext=True)
    body(s, Y_BODY_EXT, [
        [('This was the shortest project so far, and almost all of it was '
          'arithmetic.', None)],
        [('The vision was the part we already knew — hue, masks, a threshold — and '
          'almost all of the real work was deciding where the grid was and how big '
          'each cell was. Two claims out of three were true, and the one that was '
          'false came down to a pair of missing brackets in a line that read '
          'perfectly well.', None)],
        [('Nothing crashed. Nothing printed an error. The program simply did not do '
          'the one thing it said it would let you do.', None)],
        [('Write the claim down first. Run it second.', None)],
    ], ext=True)

    # ------------------------------------------------------- layout pass ---
    tight = pack_deck(prs, gap=0.30, limit=Y_BOTTOM)
    if tight:
        print('OVERFLOW:', tight)

    # ------------------------------------------------------------------ save
    if os.path.exists(OUT):
        os.remove(OUT)
    prs.save(OUT)
    shutil.rmtree(TMP, ignore_errors=True)
    print(f'saved {OUT} ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)')


if __name__ == '__main__':
    build()
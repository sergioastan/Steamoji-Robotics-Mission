# -*- coding: utf-8 -*-
"""Build Slides/M2/myCobot_02.pptx -- 'Finding the Board' (M2-P2).

Rebuilds the deck from the theme/layouts of the reference sample
Slides/myCobot_08.pptx, but teaches the ArUco marker detection and 3D
pose estimation pipeline that students complete in
M2/M2-P2-Starter.py.

Every code snippet below is copied verbatim from M2/M2-P2-Base.py.
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
OUT = os.path.join(HERE, 'Slides', 'M2', 'myCobot_02.pptx')
TMP = os.path.join(HERE, 'tmp_media')

STARTER = 'M2-P2-Starter.py'
SCP = f'scp {STARTER} er@192.168.1.149:Documents'
RUN = f'python {STARTER}'

# Courier New advances exactly 0.6 em, so one character is this many cm
# per point of font size. code() insets its panel by 0.62 cm each side.
CM_PER_CHAR_PT = 0.6 * 2.54 / 72.0
CODE_INSET = 1.24


def codefit(lines, w=W_WIDE, pad=0.6, lo=10.0, hi=SZ_CODE):
    """Pick the largest font size at which every line fits inside the panel."""
    longest = max(len(ln) for ln in lines)
    avail = w - CODE_INSET - pad
    return max(lo, min(hi, avail / (longest * CM_PER_CHAR_PT)))


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
    para(tf, True, 'Project 2', F_TITLE, SZ_DIVIDER, YELLOW, line_spacing=1.0)
    para(tf, False, 'Finding the Board', F_TITLE, SZ_DIVIDER, WHITE, line_spacing=1.0)

    # ====================================================== 3. WHAT'S NEXT ===
    s = add()
    title(s, [('What’s ', None), ('next', None), ('?', None)])
    body(s, Y_BODY_STD, [
        [('In Project 1 you built something that could name a shape. It was a '
          'good program, and it had one very specific blind spot: it could tell '
          'you ', None),
         ('what', 'b'),
         (' something was, but never ', None),
         ('where', 'b'),
         (' it was.', None)],
        None,
        [('That is enough to print a word on screen. It is not enough to move an '
          'arm. To pick something up you need to know how far away it is and '
          'which way to turn — numbers, not nouns.', None)],
        None,
        [('So this project changes what the program looks for. Instead of hunting '
          'for shapes, it hunts for ', None),
         ('markers', 'b'),
         (' you have taped to the board, works out exactly where each one is in '
          'three dimensions, and prints the numbers in millimetres.', None)],
    ])
    note(s, 15.2, [
        ('Everything you already know carries over. Imports, the robot startup, '
         'the camera scan and the display loop are all still here. What changes is '
         'the middle of the program, where the shape maths used to be.', None),
    ], h=2.4)

    # ================================================ 4. WHAT P1 COULD NOT DO ===
    s = add()
    title(s, [('Two squares, ', None), ('one answer', None)])
    body(s, Y_BODY_STD, [
        [('Put a large square on the left of the plate and a small square on the '
          'right. Both of them measure an extent of about 0.99, both score well '
          'on circularity, both have four corners. Your Project 1 decision chain '
          'would call them ', None),
         ('Square', 'c'),
         (' — the same word, for two things in different places.', None)],
        None,
        [('The decision chain was never broken. It was answering the only question '
          'it had been given. ', None),
         ('Shape answers what. A machine that moves things needs where.', 'b')],
        None,
        [('This project supplies the missing half. You already know what the '
          'things on your board look like, because you put them there. So the '
          'computer has something it can measure against.', None)],
    ])
    callout(s, 15.4, 'A measurement you can repeat is worth more than a clever '
                     'guess. You already know what the things on your board look '
                     'like, because you put them there.', h=2.44)

    # ==================================================== 5. PHYSICAL SETUP ===
    s = add()
    title(s, [('Before you type ', None), ('anything', None)])
    body(s, Y_BODY_STD, [
        [('The very first line of the starter file is not Python. It is an '
          'instruction to a human:', None)],
    ])
    code(s, 5.6, [
        '# Remember to cover the two markers on the board for this project!',
    ], size=15.0)
    body(s, 7.4, [
        [('Two printed ArUco markers are taped to the board, and the camera looks '
          'down at them from above. Cover them when you are not using them.', None)],
        None,
        [('The reason is simple. A marker the camera can see is a marker the '
          'program will measure, and a marker left on the board is a marker your '
          'arm may try to reach. You will be sending this arm to real coordinates '
          'later in the module.', None)],
        None,
        [('Check three things before you start: the markers are flat and not '
          'curled, the camera can see both of them at once, and you have measured '
          'one marker edge with a ruler. That measurement becomes a number in the '
          'program, and every distance it prints depends on it.', None)],
    ])
    note(s, 15.4, [
        ('A damaged or half-hidden marker is read wrongly, or ignored.', None),
    ], h=2.2)

    # ================================================= 6. WHAT IS AN ARUCO ===
    s = add()
    title(s, [('What is an ', None), ('ArUco marker', None), ('?', None)])
    body(s, Y_BODY_STD, [
        [('A square of pure black and pure white: a thick black border all the way '
          'round, and a grid of black and white squares inside it.', None)],
        None,
        [('The border is identical on every marker ever made. The grid inside is '
          'the part that carries the identity. The program already knows what all '
          '250 valid grids look like, so when it sees one it can say which marker '
          'it is just by looking.', None)],
        None,
        [('This is what computer people call a ', None),
         ('fiducial', 'b'),
         (' — an ordinary object placed in the scene purely so the computer has '
          'something known to measure against. The marker is not the subject of '
          'the picture. It is the ruler.', None)],
    ])
    note(s, 14.6, [
        ('Two properties make this work in a real classroom. Markers are cheap to '
         'print and they are designed so the black border cannot be confused with '
         'the grid inside it, which is what lets the detector find a marker at an '
         'angle instead of only face-on.', None),
    ], h=2.6)

    # ========================================================= 7. DICTIONARY ===
    s = add()
    title(s, [('DICT_6X6_', None), ('250', None)])
    code(s, 4.6, [
        'self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)',
    ], size=12.5)
    body(s, 7.0, [
        [('6X6', 'c'),
         (' means the inner grid is six squares across and six down. ', None),
         ('250', 'c'),
         (' means there are 250 different valid patterns in this dictionary.', None)],
        None,
        [('Why a dictionary at all? Because the marker has to be unambiguous. The '
          'detector must never mistake a row of payload squares for the border, '
          'and no two markers in the dictionary may look alike from any angle.', None)],
        None,
        [('Changing the dictionary is therefore a decision with consequences: it '
          'decides which physical markers your program is willing to recognise. '
          'Change it without changing the markers on the board and the program '
          'will report nothing at all — with no error message to explain why.', None)],
    ])
    note(s, 14.8, [
        ('The detector also needs the marker’s known size in millimetres, from your '
         'earlier ruler measurement.', None),
    ], h=2.2)

    # ============================================== 8. CAMERA CALIBRATION ===
    s = add()
    title(s, [('The camera is not ', None), ('perfect', None)])
    code(s, 4.6, [
        'self.camera_matrix = np.array([',
        '    [781.33379113, 0.0, 347.53500524],',
        '    [0.0, 783.79074192, 246.67627253],',
        '    [0.0, 0.0, 1.0]',
        '], dtype=np.float32)',
    ], size=15.0)
    body(s, 9.4, [
        [('781.33 and 783.79 are ', None),
         ('focal lengths', 'b'),
         (', measured in pixels. They say how far the lens "sees", in the same '
          'units as the picture itself.', None)],
        None,
        [('347.53 and 246.67 are the ', None),
         ('principal point', 'b'),
         (' — the pixel where the camera’s own line of sight lands on the '
          'sensor. Usually near the middle of the picture, but not exactly.', None)],
        None,
        [('The bottom row of zeros and a one is bookkeeping, not a measurement. '
          'It is there because matrix maths expects this shape.', None)],
    ])
    note(s, 15.0, [
        ('Produced from a checkerboard photo, they belong to this exact camera '
         'and lens. Copy them exactly.', None),
    ], h=2.4)

    # ================================================== 9. LENS DISTORTION ===
    s = add()
    title(s, [('And the lens is not ', None), ('flat', None)])
    _d = [
        'self.dist_coeffs = np.array([',
        '    [3.41360787e-01, -2.52114260e+00, -1.28012469e-03, 6.70503562e-03, 2.57018000e+00]',
        '], dtype=np.float32)',
    ]
    code(s, 4.6, _d, size=codefit(_d))
    body(s, 7.6, [
        [('Five numbers describing how badly this particular lens bends light. '
          'Cheap lenses bend more towards the edges than in the middle, so a '
          'square photographed near the corner of the picture comes out slightly '
          'rounded.', None)],
        None,
        [('They are written in scientific notation, which is just a compact way of '
          'saying a very small or very large number. ', None),
         ('3.41e-01', 'c'),
         (' is ', None),
         ('0.341', 'c'),
         ('. ', None),
         ('-2.52e+00', 'c'),
         (' is ', None),
         ('-2.52', 'c'),
         ('.', None)],
        None,
        [('Without these five numbers every distance would be slightly wrong — and '
          'wrong by a ', None),
         ('different amount', 'b'),
         (' depending on where in the picture the marker happened to be sitting. '
          'A marker in the centre and the same marker in the corner would give two '
          'different answers.', None)],
    ])

    # ==================================================== 10. MARKER SIZE ===
    s = add()
    title(s, [('Pixels are not a ', None), ('distance', None)])
    code(s, 4.6, [
        '# ArUco marker size in meters (30mm)',
        'self.marker_size_m = 0.03',
    ], size=15.0)
    body(s, 7.4, [
        [('Here is the whole trick. The camera hands you a marker as ', None),
         ('pixels', 'b'),
         (', and pixels have no units. You cannot move an arm by an amount of '
          'pixels.', None)],
        None,
        [('So you give the program one real measurement — how wide the marker '
          'actually is — and it works backwards from the marker’s size on screen '
          'to how far away it must be.', None)],
        None,
        [('Measure it once, with a ruler, carefully. ', None),
         ('0.03', 'c'),
         (' metres is 30 millimetres, which is why the comment spells it out: a '
          'bare ', None),
         ('3', 'c'),
         (' would mean three kilometres.', None)],
    ])
    note(s, 14.4, [
        ('This is the single measurement your program trusts. If it is wrong, '
         'nothing downstream can detect it — the program has no way to know that '
         'the marker was printed at 29mm instead of 30mm, and it will report '
         'confident, tidy, incorrect distances forever.', None),
    ], h=2.6)

    # =================================================== 11. POSE ESTIMATION ===
    s = add()
    title(s, [('Asking where it ', None), ('is', None)])
    code(s, 4.6, [
        'rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(',
        '    corners, self.marker_size_m, self.camera_matrix, self.dist_coeffs',
        ')',
    ], size=14.0)
    body(s, 8.4, [
        [('One line, three inputs, two answers. Corners in pixels, the marker’s '
          'real size, and the two calibration arrays go in; a rotation and a '
          'position come out — for every marker in the picture at once.', None)],
        None,
        [('rvecs', 'c'),
         (' is rotation. ', None),
         ('tvecs', 'c'),
         (' is translation. The third return value is thrown away here, which is '
          'what the underscore is for.', None)],
        None,
        [('The word ', None),
         ('pose', 'b'),
         (' means both halves at once: where the marker is ', None),
         ('and', 'i'),
         (' which way it is facing. For sorting shapes you could ignore the '
          'second half. For a robot that has to line up a gripper, you cannot.', None)],
    ])
    note(s, 14.8, [
('SingleMarkers', 'c'),
         (' treats each marker on its own — the right choice when markers move '
          'independently.', None),
    ], h=2.2)

    # ==================================================== 12. READING TVEC ===
    s = add()
    title(s, [('Three numbers: ', None), ('X, Y, Z', None)])
    code(s, 4.6, [
        'tvec = tvecs[i][0]  # [X, Y, Z] in meters',
    ], size=15.0)
    body(s, 7.4, [
        [('tvecs[i]', 'c'),
         (' is the translation of marker number ', None),
         ('i', 'c'),
         ('. The ', None),
         ('[0]', 'c'),
         (' unwraps it down to a plain array of three numbers, which is much easier '
          'to work with.', None)],
        None,
        [('Two of the three describe sideways movement and the third is ', None),
         ('depth', 'b'),
         (' — how far away the marker is. All three are in metres, and all three '
          'are measured from the camera, not from the robot.', None)],
        None,
        [('A negative number is not an error. It simply means the marker is to '
          'the left, or below the camera’s own origin, or nearer than the camera '
          'itself. The signs carry real information about where things are.', None)],
    ])
    note(s, 14.4, [
        ('The loop that follows goes round ', None),
        ('for i in range(len(ids))', 'c'),
        (' — one pass per marker found. Everything inside that loop is about '
         'marker number ', None),
        ('i', 'c'),
        (', and nothing inside it should assume there is more than one marker.', None),
    ], h=2.4)

    # ==================================================== 13. READING RVEC ===
    s = add()
    title(s, [('The rotation you ', None), ('cannot read', None)])
    body(s, Y_BODY_STD, [
        [('rvecs[i]', 'c'),
         (' is also three numbers, and unlike ', None),
         ('tvecs[i]', 'c'),
         (' they are not coordinates. A rotation vector packs two separate ideas '
          'into three values.', None)],
        None,
        [('Its ', None),
         ('length', 'b'),
         (' is the angle turned, in radians. Its ', None),
         ('direction', 'b'),
         (' is the axis you turned about. Together they say "tip this far, around '
          'this line".', None)],
        None,
        [('OpenCV represents it this way because it composes cleanly: add two '
          'rotation vectors and you get another valid rotation. Three separate '
          'Euler angles do not behave that way, and roll over.', None)],
    ])
    callout(s, 12.0, [
        ('Notice what the program does with it: nothing. ', None),
        ('rvecs[i]', 'c'),
        (' is handed straight to the drawing function, which does the trigonometry '
         'and draws the answer. A library doing the hard arithmetic is the whole '
         'point of using a library.', None),
    ], h=2.44)

    # ============================================= 14. TWO COORDINATE FRAMES ===
    s = add()
    title(s, [('Whose ', None), ('coordinates', None), ('?', None)])
    body(s, Y_BODY_STD, [
        [('Everything so far is measured ', None),
         ('from the camera', 'b'),
         ('. But the arm does not live inside the camera. The robot has no idea '
          'where the lens is, and moving to a camera-relative coordinate would put '
          'the gripper in completely the wrong place.', None)],
        None,
        [('So there are two frames in this program, and one conversion between '
          'them. This is the single most important idea on the next few slides.', None)],
    ])
    table(s, 9.4, [
        ['What', 'Camera frame', 'End-effector frame'],
        ['Measured from', 'The lens', 'The pump on the wrist'],
        ['Unit', 'metres', 'millimetres'],
        ['X and Y mean', 'sideways on screen', 'sideways from the wrist'],
        ['Z means', 'depth from the lens', 'depth from the wrist'],
        ['Used by', 'the maths library', 'the arm'],
    ], col_w=[5.6, 8.6, 9.9])
    note(s, 16.4, [
        ('A coordinate is only ever meaningful once you have said ', None),
        ('relative to what', 'b'),
        ('. Two systems using the same three numbers and different origins will '
         'send an arm to two completely different places.', None),
    ], h=1.9)

    # ================================================== 15. THE PUMP OFFSETS ===
    s = add()
    title(s, [('Moving from one frame ', None), ('to the other', None)])
    code(s, 4.4, [
        '# Pump / End-effector spatial offsets (mm)',
        'self.pump_x = 15',
        'self.pump_y = -55',
    ], size=15.0)
    code(s, 7.6, [
        'rel_x = round(tvec[0] * 1000 + self.pump_y, 2)',
        'rel_y = round(tvec[1] * 1000 + self.pump_x, 2)',
        'rel_z = round(tvec[2] * 1000, 2)',
    ], size=15.0)
    body(s, 10.8, [
        [('The ', None),
         ('* 1000', 'c'),
         (' is the unit change — metres become millimetres. The two offsets are the '
          'measured gap between where the camera thinks it is and where the pump '
          'really is, and they are added in to correct for it.', None)],
        None,
        [('Now read those two lines carefully, because they will catch you out. '
          'The value named ', None),
         ('pump_y', 'c'),
         (' is added to ', None),
         ('X', 'c'),
         (', and ', None),
         ('pump_x', 'c'),
         (' is added to ', None),
         ('Y', 'c'),
         ('. The names are crossed over.', None)],
    ])
    callout(s, 15.0, [
        ('Do not "fix" it — the crossing is deliberate: the camera axes run the '
         'other way. Check one known marker if you change these.', None),
    ], h=2.44)

    # ==================================================== 16. DRAWING RESULTS ===
    s = add()
    title(s, [('Three overlays, three ', None), ('jobs', None)])
    code(s, 4.4, [
        'cv2.aruco.drawDetectedMarkers(frame, corners, ids)',
    ], size=15.0)
    code(s, 6.2, [
        'cv2.drawFrameAxes(',
        '    frame, self.camera_matrix, self.dist_coeffs,',
        '    rvecs[i], tvecs[i], self.marker_size_m * 0.5',
        ')',
    ], size=14.0)
    code(s, 9.8, [
        'cv2.putText(',
        '    frame, label_text, (corner_center[0] - 80, corner_center[1] - 15),',
        '    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2',
        ')',
    ], size=13.0)
    body(s, 13.6, [
        [('drawDetectedMarkers', 'c'),
         (' draws the outline and the ID number.', None)],
        None,
        [('drawFrameAxes', 'c'),
         (' stands a small RGB tripod on the marker showing which way it faces. ',
          None),
         ('marker_size_m * 0.5', 'c'),
         (' keeps it in proportion at any range.', None)],
        None,
        [('putText', 'c'),
         (' writes your numbers on the picture. ', None),
         ('(0, 255, 0)', 'c'),
         (' is green — OpenCV lists colour channels blue, green, red.', None)],
    ])

    # =================================================== 17. VERSION TROUBLE ===
    s = add()
    title(s, [('Two versions of the ', None), ('same library', None)])
    code(s, 4.4, [
        'try:',
        '    self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)',
        '    self.aruco_params = cv2.aruco.DetectorParameters()',
        '    self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)',
        '    self.use_new_aruco = True',
        'except AttributeError:',
        '    self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)',
        '    self.aruco_params = cv2.aruco.DetectorParameters_create()',
        '    self.use_new_aruco = False',
    ], size=11.5)
    body(s, 12.4, [
        [('OpenCV moved the ArUco API: newer builds give you a detector object '
          'to keep; older builds pass a dictionary each call.', None)],
        None,
        [('The ', None),
         ('except AttributeError', 'c'),
         (' catches one situation: this version has no such name — a missing '
          'attribute, not a crash.', None)],
        None,
        [('self.use_new_aruco', 'c'),
         (' is set once here and read each frame to pick which call style to use. '
          'Detect the version once, then branch cheaply in the loop.', None)],
    ], size=18.0)
    note(s, 17.0, [
        ('A pattern worth copying: four lines and the same file runs on the '
         'classroom laptop and the arm, even with different OpenCV versions.', None),
    ], h=1.9)

    # ======================================================== 18. THE PIPELINE ===
    s = add()
    title(s, [('The whole pipeline on ', None), ('one line', None)])
    code(s, 4.6, [
        'display_frame, log_info = vision.process_frame(frame)',
    ], size=15.0)
    body(s, 6.4, [
        [('That single call, once per frame, does all of this:', None)],
    ])
    steps = [
        ('Grey the picture', 'ArUco detection works on greyscale, not colour.'),
        ('Detect the markers', 'Find every corner of every marker in view.'),
        ('Draw the outlines', 'So you can see what it found.'),
        ('Estimate the pose', 'Pixels plus marker size become metres and radians.'),
        ('Convert frames', 'Camera metres to wrist millimetres.'),
        ('Draw axes and text', 'Put the answer on the picture.'),
    ]
    for i, (h_, b_) in enumerate(steps):
        num_item(s, 7.7 + i * 1.95, i + 1, h_, [(b_, None)], h=1.4)
    note(s, 17.2, [
        ('It returns two things: the picture with the overlays drawn on it, and a '
         'line of text for the terminal. One for your eyes, one for your log.', None),
    ], h=1.6)

    # ======================================================= 19. STEP 1 ===
    s = add()
    title(s, [('Step 1', None)])
    body(s, Y_BODY_STD, [
        [('The first TODO sits at the very top of the file, before anything else '
          'can possibly work. Three packages, in this order:', None)],
    ])
    code(s, 6.0, [
        'import time',
        'import cv2',
        'import numpy as np',
    ], size=15.0)
    body(s, 9.4, [
        [('Order does not matter here, but do not leave one out. ', None),
         ('time', 'c'),
         (' gives you the pauses that let the arm finish a movement, ', None),
         ('cv2', 'c'),
         (' is OpenCV, and ', None),
         ('numpy', 'c'),
         (' holds the calibration arrays.', None)],
    ])
    note(s, 12.6, [
        [('The next TODO imports ', None), ('MyCobot280', 'c'),
         (' from ', None), ('pymycobot', 'c'),
         ('. That one is not in any standard library, so it is the import most '
          'likely to fail on a machine that has never run the arm before.', None)],
    ], h=2.4)

    # ======================================================= 20. STEP 2 ===
    s = add()
    title(s, [('Step 2', None)])
    body(s, Y_BODY_STD, [
        [('The robot import lives on its own line:', None)],
    ])
    code(s, 5.6, [
        'from pymycobot.mycobot280 import MyCobot280',
    ], size=15.0)
    body(s, 8.0, [
        [('This reads as: from the ', None),
         ('mycobot280', 'c'),
         (' part of the ', None),
         ('pymycobot', 'c'),
         (' package, bring in the ', None),
         ('MyCobot280', 'c'),
         (' class. Importing a class rather than a whole module means you can type '
          'the shorter name afterwards.', None)],
        None,
        [('If this line fails, the package is not installed on that machine. That '
          'is a different problem from a missing import, and the error message '
          'will tell you which one you have.', None)],
    ])
    note(s, 13.4, [
        ('The rest of the deck assumes this import works. On a laptop that has '
         'never had the arm connected, expect to see it fail and be told to skip '
         'to Step 5 — the vision pipeline does not need the robot at all.', None),
    ], h=2.4)

    # ======================================================= 21. STEP 3 ===
    s = add()
    title(s, [('Step 3', None)])
    body(s, Y_BODY_STD, [
        [('This whole section sits inside a ', None),
         ('try', 'c'),
         (' block, which is deliberate. Watch what each line does:', None)],
    ])
    code(s, 6.4, [
        'print("Connecting to myCobot280...")',
        "mc = MyCobot280('/dev/ttyAMA0', 1000000)",
        'time.sleep(0.5)',
        'mc.power_on()',
        'time.sleep(0.5)',
    ], size=15.0)
    body(s, 10.6, [
        [('The port ', None),
         ('/dev/ttyAMA0', 'c'),
         (' is which serial socket the arm is plugged into, and ', None),
         ('1000000', 'c'),
         (' is the speed both ends agree to talk at. On another machine this may '
          'be ', None),
         ('ttyUSB0', 'c'),
         (', so if this line throws, check the port before you suspect the arm.', None)],
        None,
        [('Each ', None),
         ('sleep', 'c'),
         (' gives the command before it time to finish. Delete them and the arm '
          'misses instructions, which looks exactly like a broken arm.', None)],
    ])
    note(s, 15.4, [
        [('If the arm is not connected, this block prints ', None),
         ('Robot hardware warning:', 'c'),
         (' and carries on. That is the design working, not a failure you need to '
          'fix — the vision pipeline runs perfectly well without hardware.', None)],
    ], h=2.0)

    # ======================================================= 22. STEP 4 ===
    s = add()
    title(s, [('Step 4', None)])
    body(s, Y_BODY_STD, [
        [('Park the arm somewhere safe before the camera work starts:', None)],
    ])
    code(s, 5.8, [
        'folded_angles = [0, 45, -90, -45, 0, 0]',
        'print("Moving arm to initial folded position...")',
        'mc.send_angles(folded_angles, 20)',
        'time.sleep(2.0)',
    ], size=15.0)
    body(s, 9.4, [
        [('Six numbers, one per joint, in degrees. Zero means ', None),
         ('no bend', 'c'),
         (', and the signs say which way. Folding the arm up and out of shot is '
          'deliberate: a metal arm parked in view of the camera is a large shiny '
          'object that will confuse everything you measure.', None)],
        None,
        [('The ', None),
         ('20', 'c'),
         (' is how fast to travel there, and the ', None),
         ('2.0', 'c'),
         (' second sleep gives it time to arrive before the camera starts.', None)],
    ])
    note(s, 14.8, [
        [('Notice this is a ', None), ('list', 'c'),
         (', not a tuple. Later in the module you will want to change these values '
          'while the program runs, and the ', None),
         ('[ ]', 'c'),
         (' brackets are what allow that.', None)],
    ], h=2.2)

    # ================================================ 23. RUN IT AND SEE IT FAIL ===
    s = add()
    title(s, [('Run it before you fix ', None), ('anything', None)])
    body(s, Y_BODY_STD, [
        [('Send the starter across and run it with the four vision TODOs still '
          'empty. Seeing the failures first is worth the two minutes.', None)],
    ])
    command(s, 6.6, SCP)
    command(s, 8.2, RUN)
    body(s, 10.2, [
        [('The robot block will warn and continue. Then the camera opens, a frame '
          'arrives, and ', None),
         ('process_frame', 'c'),
         (' runs with the detection code missing. Expect:', None)],
    ])
    code(s, 13.0, [
        "NameError: name 'ids' is not defined",
    ], size=14.0)
    note(s, 15.0, [
        [('Read that message properly. It is not a camera fault and it is not a '
          'marker fault — it says a variable the program expected to have been '
          'created was never created. That is Step 6, and nothing after it.', None)],
    ], h=2.2)

    # ======================================================= 24. STEP 5 ===
    s = add()
    title(s, [('Step 5', None)])
    body(s, Y_BODY_STD, [
        [('Now we move into the class. This TODO asks for the dictionary and the '
          'detector — the version-tolerant block from the concepts section:', None)],
    ])
    code(s, 6.6, [
        'try:',
        '    self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)',
        '    self.aruco_params = cv2.aruco.DetectorParameters()',
        '    self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)',
        '    self.use_new_aruco = True',
        'except AttributeError:',
        '    self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)',
        '    self.aruco_params = cv2.aruco.DetectorParameters_create()',
        '    self.use_new_aruco = False',
    ], size=11.5)
    note(s, 13.0, [
        ('This runs once, when the object is created — not once per frame. Read '
         'it as setup, not as part of the loop.', None),
    ], h=1.4)
    note(s, 14.8, [
        ('If you want proof it worked, print ', None),
        ('self.use_new_aruco', 'c'),
        (' after the block. It tells you which half of the ', None),
        ('try', 'c'),
        (' your machine took, and that is genuinely useful to know when something '
         'downstream misbehaves.', None),
    ], h=2.6)

    # ======================================================= 25. STEP 6 ===
    s = add()
    title(s, [('Step 6', None)])
    body(s, Y_BODY_STD, [
        [('This is the TODO the error message was pointing at. Detect the '
          'markers, choosing the call style the flag decided on:', None)],
    ])
    code(s, 6.6, [
        'if self.use_new_aruco:',
        '    corners, ids, _ = self.detector.detectMarkers(gray)',
        'else:',
        '    corners, ids, _ = cv2.aruco.detectMarkers(',
        '        gray, self.aruco_dict, parameters=self.aruco_params',
        '    )',
    ], size=14.0)
    body(s, 11.0, [
        [('The greyscale conversion happens just above this block, on its own '
          'line. ArUco detection works on brightness, not colour.', None)],
        None,
        [('Three things come back. ', None),
         ('corners', 'c'),
         (' holds four points per marker, ', None),
         ('ids', 'c'),
         (' which marker each one was, and the third is rejected. When nothing is '
          'found, ', None),
         ('ids', 'c'),
         (' is ', None),
         ('None', 'c'),
         (', not an empty list — which is why the next line tests both.', None)],
    ])
    note(s, 16.0, [
        ('Once this works, the terminal stops shouting and the window appears — '
         'still blank, since nothing is drawn yet. Correct progress.', None),
    ], h=1.9)

    # ======================================================= 26. STEP 7 ===
    s = add()
    title(s, [('Step 7', None)])
    body(s, Y_BODY_STD, [
        [('Detection found something. Now put it on the screen:', None)],
    ])
    code(s, 5.8, [
        'cv2.aruco.drawDetectedMarkers(frame, corners, ids)',
    ], size=15.0)
    body(s, 8.2, [
        [('One line, no configuration, no return value. It draws an outline around '
          'each marker and stamps its ID number beside it.', None)],
        None,
        [('Look closely at what it did ', None),
         ('not', 'i'),
         (' do: the outlines have no depth. Nothing on screen yet tells you whether '
          'the marker is 200mm away or 800mm — this is still a flat picture.', None)],
    ])
    note(s, 12.4, [
        [('Run the program now. A coloured rectangle with a number on it is the '
          'single best checkpoint in this project: it proves the camera, the '
          'dictionary, the lighting and your marker printing are all fine, and it '
          'narrows every later fault to the maths that remains.', None)],
    ], h=2.6)

    # ======================================================= 27. STEP 8 ===
    s = add()
    title(s, [('Step 8', None)])
    body(s, Y_BODY_STD, [
        [('Now the hard part. One call turns corners into a position and a tilt:', None)],
    ])
    code(s, 5.8, [
        'rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(',
        '    corners, self.marker_size_m, self.camera_matrix, self.dist_coeffs',
        ')',
    ], size=14.0)
    body(s, 9.2, [
        [('Every input here was prepared earlier in the file: ', None),
         ('corners', 'c'),
         (' from Step 6, ', None),
         ('marker_size_m', 'c'),
         (' from your ruler, and the two calibration arrays that were already '
          'written in for you.', None)],
        None,
        [('This call is where the mathematics actually happens. It undoes the lens '
          'distortion, works out how far away a marker of that known size must be, '
          'and works out which way it is tilted — all from four corners.', None)],
    ])
    note(s, 13.8, [
        ('Four numbers in, two sets of three numbers out, for every marker at once. '
         'Nothing here is approximate and nothing is random: the same four corners '
         'always give the same answer.', None),
    ], h=2.2)

    # ======================================================= 28. STEP 9 ===
    s = add()
    title(s, [('Step 9', None)])
    body(s, Y_BODY_STD, [
        [('This is the conversion from the camera’s world to the robot’s:', None)],
    ])
    code(s, 5.8, [
        'rel_x = round(tvec[0] * 1000 + self.pump_y, 2)',
        'rel_y = round(tvec[1] * 1000 + self.pump_x, 2)',
        'rel_z = round(tvec[2] * 1000, 2)',
    ], size=15.0)
    body(s, 9.2, [
        [('Three operations per axis. Unwrap the array, convert metres to '
          'millimetres, add the offset that accounts for the pump not being exactly '
          'where the camera is, then round to two decimal places.', None)],
        None,
        [('These are the first numbers in the whole program that the ', None),
         ('arm', 'b'),
         (' could act on. Everything before this point was maths for the sake of '
          'maths; from here on, a wrong number means the gripper goes somewhere '
          'real.', None)],
    ])
    note(s, 14.0, [
        [('Cross-check before you trust them: cover one marker and watch the '
          'other’s numbers. Then move a marker a known distance — 100mm further '
          'away — and confirm Z changes by about 100. A unit error shows up '
          'immediately at this scale.', None)],
    ], h=2.4)

    # ======================================================= 29. STEP 10 ===
    s = add()
    title(s, [('Step 10', None)])
    body(s, Y_BODY_STD, [
        [('The numbers are correct but invisible. This draws them:', None)],
    ])
    code(s, 5.8, [
        'cv2.drawFrameAxes(',
        '    frame, self.camera_matrix, self.dist_coeffs,',
        '    rvecs[i], tvecs[i], self.marker_size_m * 0.5',
    ], size=14.0)
    body(s, 9.2, [
        [('A small tripod of coloured lines standing on the marker: red for one '
          'axis, green for another, blue for the third. Where the lines point is '
          'which way the marker is facing.', None)],
        None,
        [('This is the ', None),
         ('rvecs[i]', 'c'),
         (' you never had to understand, made visible. Half the marker size keeps '
          'the tripod in proportion whether the marker is near or far.', None)],
    ])
    note(s, 13.6, [
        [('The axes are also a sanity check. If they point sideways while the '
          'marker is clearly lying flat on the board, your rotation is being '
          'interpreted in a different order than you assumed — check the axes '
          'before trusting any number printed beside them.', None)],
    ], h=2.4)

    # ======================================================= 30. STEP 11 ===
    s = add()
    title(s, [('Step 11', None)])
    body(s, Y_BODY_STD, [
        [('Last of the drawing. Work out where to put the text, build the label, '
          'and write it:', None)],
    ])
    code(s, 6.0, [
        'corner_center = np.mean(corners[i][0], axis=0).astype(int)',
        'label_text = f"ID:{marker_id} X:{rel_x} Y:{rel_y} Z:{rel_z}mm"',
    ], size=14.0)
    code(s, 8.8, [
        'cv2.putText(',
        '    frame, label_text, (corner_center[0] - 80, corner_center[1] - 15),',
        '    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2',
        ')',
    ], size=13.0)
    body(s, 13.2, [
        [('np.mean', 'c'),
         (' averages the four corners into the middle of the marker, and ', None),
         ('astype(int)', 'c'),
         (' turns the result into whole numbers, because OpenCV will not draw text '
          'at a fractional pixel position.', None)],
        None,
        [('The ', None),
         ('f"..."', 'c'),
         (' is an f-string: the letters stay as they are and each ', None),
         ('{...}', 'c'),
         (' is replaced by the value of the variable inside it. Notice ', None),
         ('mm', 'c'),
         (' sits outside the braces — that is literal text, not a variable.', None)],
    ])

    # ======================================================= 31. STEP 12 ===
    s = add()
    title(s, [('Step 12', None)])
    body(s, Y_BODY_STD, [
        [('Down near the bottom of the file, outside the class. This one finds a '
          'camera that actually works:', None)],
    ])
    code(s, 6.0, [
        'def find_working_camera(max_tests=5):',
        '    """Scans video indices and returns the first camera that produces frames."""',
        '    for idx in range(max_tests):',
        '        cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)',
        '        if cap.isOpened():',
        '            ret, frame = cap.read()',
        '            cap.release()',
        '            if ret and frame is not None and frame.size > 0:',
        '                print(f"Found active camera at index {idx}")',
        '                return idx',
        '    return None',
    ], size=12.0)
    body(s, 13.6, [
        [('Opening a camera successfully does not mean it works. ', None),
         ('isOpened', 'c'),
         (' only reports that the handle was created, so the code goes one step '
          'further and tries to read an actual frame from it.', None)],
        None,
        [('Note the ', None),
         ('cap.release()', 'c'),
         (' before the frame check. Every failed attempt is closed as it is '
          'rejected — otherwise a five-camera scan leaves four cameras held open '
          'and the good one unable to start.', None)],
    ])

    # ======================================================= 32. STEP 13 ===
    s = add()
    title(s, [('Step 13', None)])
    body(s, Y_BODY_STD, [
        [('The last big TODO wraps the whole camera loop. Most of it is already '
          'written; three lines are yours.', None)],
    ])
    code(s, 6.2, [
        'cap_num = find_working_camera()',
        'if cap_num is None:',
        '    print("Error: No working camera stream found.")',
        '    return',
    ], size=14.0)
    code(s, 9.2, [
        'cap = cv2.VideoCapture(cap_num, cv2.CAP_V4L2)',
        'cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)',
        'cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)',
    ], size=14.0)
    body(s, 12.4, [
        [('The ', None),
         ('is None', 'c'),
         (' test asks whether the scan found anything at all, and ', None),
         ('return', 'c'),
         (' leaves the whole function immediately rather than carrying on with a '
          'camera that does not exist.', None)],
        None,
        [('Note the wording of the two ', None),
         ('cap.set', 'c'),
         (' lines: you are asking, not telling. Some cameras ignore the request, '
          'so print ', None),
         ('cap.get(cv2.CAP_PROP_FRAME_WIDTH)', 'c'),
         (' if the window looks wrong.', None)],
    ])
    note(s, 16.4, [
        [('This function runs once, and ', None),
         ('while True', 'c'),
         (' below it runs forever. Anything inside the loop happens thirty times '
          'a second, so keep it cheap.', None)],
    ], h=1.9)

    # ======================================================= 33. STEP 14 ===
    s = add()
    title(s, [('Step 14', None)])
    body(s, Y_BODY_STD, [
        [('Inside the loop, the call that ties the whole class together:', None)],
    ])
    code(s, 5.8, [
        'display_frame, log_info = vision.process_frame(frame)',
    ], size=15.0)
    body(s, 8.2, [
        [('Two return values, unpacked into two names. ', None),
         ('display_frame', 'c'),
         (' is the picture with everything drawn on it; ', None),
         ('log_info', 'c'),
         (' is the line of text for the terminal.', None)],
        None,
        [('Both names are worth keeping. The picture is for your eyes and the text '
          'is for your log — and the text is far easier to copy into a spreadsheet '
          'than anything you could read off a screenshot.', None)],
    ])
    code(s, 12.0, [
        'if "Searching" not in log_info and "No Frame" not in log_info:',
        '    print(f"\\r[Detected] {log_info}", end="")',
    ], size=13.5)
    note(s, 15.0, [
        [('This next block is already written, and it is the first thing that '
          'reads ', None),
         ('log_info', 'c'),
         ('. It deliberately stays quiet while the program is still searching, so '
          'the terminal is not flooded with a new line per frame. The ', None),
         ('\\r', 'c'),
         (' and ', None),
         ('end=""', 'c'),
         (' are what turn sixty prints a second into one updating line.', None)],
    ], h=3.0)

    # ======================================================= 34. STEP 15 ===
    s = add()
    title(s, [('Step 15', None)])
    body(s, Y_BODY_STD, [
        [('The last TODO. Without it the program runs perfectly and shows you '
          'nothing at all:', None)],
    ])
    code(s, 6.0, [
        'if display_frame is not None and display_frame.size > 0:',
        '    cv2.imshow("ArUco Marker Pose Detection", display_frame)',
    ], size=14.0)
    body(s, 9.4, [
        [('The window title is the first thing a beginner searches for when the '
          'program appears to do nothing, so give it a name that says what is '
          'inside.', None)],
        None,
        [('The guard above it is not decoration. A camera that has just been '
          'unplugged can hand back an empty frame, and ', None),
         ('imshow', 'c'),
         (' on an empty frame throws on some systems.', None)],
    ])
    code(s, 13.0, [
        'if cv2.waitKey(1) & 0xFF == ord(\'q\'):',
        '    break',
    ], size=14.0)
    note(s, 15.2, [
        [('waitKey(1)', 'c'),
         (' waits one millisecond and returns the key that was pressed. ', None),
         ('& 0xFF', 'c'),
         (' masks off the extra bits some platforms report, and ', None),
         ('ord(\'q\')', 'c'),
         (' turns the letter into the number the comparison needs.', None)],
    ], h=2.4)

    # ================================================ 35. READING THE OUTPUT ===
    s = add()
    title(s, [('Reading the ', None), ('output', None)])
    code(s, 4.6, [
        'status_msg = f"ID: {marker_id} | X: {rel_x}mm | Y: {rel_y}mm | Z: {rel_z}mm"',
    ], size=12.5)
    body(s, 7.4, [
        [('One line per marker, per frame. Example:', None)],
    ])
    code(s, 9.0, [
        'ID: 0 | X: -142.5mm | Y: 88.0mm | Z: 415.7mm',
    ], size=14.0)
    body(s, 11.4, [
        [('Break it into the four things it tells you. The ', None),
         ('ID', 'c'),
         (' is which physical marker you are looking at. ', None),
         ('X', 'c'),
         (' and ', None),
         ('Y', 'c'),
         (' are sideways offsets from the pump, and ', None),
         ('Z', 'c'),
         (' is how far in front of the pump it is.', None)],
        None,
        [('While the camera sees nothing, the line reads ', None),
         ('Searching for markers...', 'c'),
         (' instead. That is your cue to check lighting, focus and marker '
          'condition — not to change any code.', None)],
    ])
    note(s, 14.8, [
        [('The numbers jitter slightly frame to frame — sensor noise, not a fault. '
          'You want a reading that stays roughly steady with your hand off the '
          'board, and moves smoothly and predictably when you move a marker.', None)],
    ], h=2.6)

    # ============================================== 36. STABILITY AND FAULTS ===
    s = add()
    title(s, [('Before you tune ', None), ('anything', None)])
    body(s, Y_BODY_STD, [
        [('Three faults account for almost every bad reading. Learn to recognise '
          'them from the symptom rather than changing code at random.', None)],
    ])
    table(s, 6.4, [
        ['Symptom', 'Most likely cause', 'Check'],
        ['Never finds a marker', 'Markers too dark, blurred or too small on screen',
         'Lighting, focus, distance'],
        ['Finds then loses it repeatedly', 'Glare or reflection on the marker',
         'Matte card, change the angle of the light'],
        ['Numbers jump when still', 'Marker not flat, or board not rigid',
         'Re-tape it, flatten the board'],
        ['Numbers roughly right, all too large', 'marker_size_m too small',
         'Re-measure the marker edge'],
        ['Numbers drift as the arm moves', 'Vibration reaching the camera',
         'Wait for the arm to settle before reading'],
    ], col_w=[7.4, 9.4, 7.2])
    note(s, 15.4, [
        [('Notice how four of those five are physical problems with the setup '
          'rather than faults in the program. Before you change a line of code, '
          'ask whether the camera can physically see what it is being asked to '
          'see.', None)],
    ], h=2.2)

    # ================================================= 37. EXTENSION DIVIDER ===
    s = add(0, master=1)
    _, tf = textbox(s, 14.22, 2.29, 12.70, 11.68)
    para(tf, True, '1', F_TITLE, 260.0, PANEL2, align=2)  # CENTER
    _, tf = textbox(s, X_L, 15.80, 24.89, 1.68)
    para(tf, True, 'EXTENSION 1', F_TITLE, 32.0, YELLOW)
    _, tf = textbox(s, X_L, 17.58, 24.89, 1.83)
    para(tf, True, 'MAKE THE ARM AIM AT THE MARKER', F_TITLE, 34.0, WHITE)

    # ========================================================== 38. BRIEF ===
    s = add(0, master=1)
    title(s, [('THE ', None), ('BRIEF', None)], ext=True)
    body(s, Y_BODY_EXT, [
        'You have a program that measures a marker and prints where it is. '
        'A robot needs to do something with that number.',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    body(s, 6.6, [
        'Close the loop. Read the marker position, convert it into joint angles, '
        'and let the arm move towards it — then find out how accurate your '
        'measurement actually was.',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    callout(s, 10.5, 'Accuracy is the whole point. You are about to find out how '
                     'far a 30mm ruler measurement and a real camera agree, and '
                     'the answer is more interesting than you expect.', h=2.44)

    # ========================================================= 39. MISSION ===
    s = add(0, master=1)
    title(s, [('YOUR MISSION: ', None), ('AIM AT THE MARKER', None)], ext=True)
    body(s, Y_BODY_EXT, [
        'Turn a printed number into a movement, then measure how wrong you were.',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    items = [
        ('Move the arm to the marker',
         [('Use the X, Y and Z you already print to build a set of joint angles '
           'and send the arm there. Start with a small movement — this arm is '
           'real hardware and the marker size on screen is not the marker size in '
           'the room.', None)]),
        ('Prove the reading is repeatable',
         [('Twenty readings from a marker that has not moved. Record the spread. '
           'Then move the marker a known 100mm and check that Z changes by 100. If '
           'it does not, your error is in the calibration, not in the maths.', None)]),
        ('Change the rule',
         [('One marker is easy. Try a two-marker board and aim at whichever you '
           'moved, or use distance to trigger a pick when a shape sits in place.', None)]),
        ('Hand it over',
         [('Write the handover page: your marker size, your measured accuracy, '
           'what you would recalibrate, and one safety limit for the next person.', None)]),
    ]
    for i, (h, b) in enumerate(items):
        num_item(s, 5.3 + i * 3.0, i + 1, h, b, h=2.1)
    callout(s, 17.0, 'Implement aiming by changing arithmetic, not by re-teaching '
                     'the arm a new pose each time. A table of recorded angles '
                     'solves the wrong problem.', h=2.44)

    # ======================================================== 40. DATA LOG ===
    s = add(0, master=1)
    title(s, [('YOUR ', None), ('DATA LOG', None)], ext=True)
    body(s, Y_BODY_EXT, [
        'Write down what you measured before you tune anything. Every number in '
        'this project depends on one ruler measurement.',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    table(s, 5.5, [
        ['Marker ID', 'X (mm)', 'Y (mm)', 'Z (mm)', 'My values'],
        ['0, marker still', '', '', '', ''],
        ['0, moved 100mm', '', '', '', ''],
        ['1, marker still', '', '', '', ''],
        ['1, moved 100mm', '', '', '', ''],
    ], col_w=[5.4, 3.4, 3.4, 3.4, 6.4])
    body(s, 12.3, [
        'Then write your aiming rule as a set of conditions before you code it:',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    code(s, 13.8, [
        'IF Z is  ______________   THEN move to  ______________',
        'IF Z is  ______________   THEN move to  ______________',
        'OTHERWISE                     ______________',
    ], size=15.0)
    callout(s, 16.6, 'A rule you cannot say out loud is a rule you have not '
                     'decided yet.', h=2.2)

    # ================================================ 41. DEFINITION OF DONE ===
    s = add(0, master=1)
    title(s, [('DEFINITION OF ', None), ('DONE', None)], ext=True)
    dones = [
        [('Both markers detected, outlined and numbered, from three different '
          'positions on the board', None)],
        [('Axis tripod and coordinate text drawn on every detected marker', None)],
        [('Your measured marker size recorded in millimetres, with the ruler '
          'reading it came from', None)],
        [('Twenty repeat readings logged, and the spread written down', None)],
        [('Arm moved to a marker position, and the achieved accuracy compared '
          'against the reading you aimed with', None)],
    ]
    for i, t in enumerate(dones):
        check_item(s, 4.4 + i * 2.5, t, h=2.2)

    # ======================================================= 42. GO FURTHER ===
    s = add(0, master=1)
    title(s, [('GO ', None), ('FURTHER', None)], ext=True)
    more = [
        [('Average several frames. ', None),
         ('Pose estimates jitter by a millimetre or two. Averaging a handful of '
          'readings gives a steadier number for free, and it teaches you that some '
          'noise can be filtered rather than fixed.', None)],
        [('Build a board from several markers. ', None),
         ('Four markers in a fixed arrangement let you compute where the camera is '
          'relative to the whole board, not just to one corner of it.', None)],
        [('Make the program refuse to guess. ', None),
         ('If consecutive readings jump more than a few millimetres, treat that as '
          'a lost marker rather than a moved one, and keep the last position '
          'instead of chasing the noise.', None)],
        [('Log every reading to a file with a timestamp. ', None),
         ('Run it for an hour and you will see exactly how much the numbers drift '
          'as the arm warms up.', None)],
    ]
    for i, t in enumerate(more):
        bullet(s, 4.6 + i * 3.2, t, h=2.9)

    # ======================================================== 43. DEBRIEF ===
    s = add(0, master=1)
    title(s, [('MISSION ', None), ('DEBRIEF', None)], ext=True)
    qs = [
        'The program stores distance in metres and prints it in millimetres. Why '
        'keep both?',
        [('The pump offsets are crossed over in the code. What would you check '
          'before deciding that was a bug and correcting it?', None)],
        [('Your readings are roughly 3% too large. Which of ', None),
         ('marker_size_m', 'c'), (', the calibration, or the lens distortion is '
          'the most likely cause, and how would you tell them apart?', None)],
        [('Why does the program need both ', None), ('rvecs', 'c'), (' and ', None),
         ('tvecs', 'c'), ('? Name a task that would fail with only one of them.', None)],
    ]
    for i, q in enumerate(qs):
        question_item(s, 4.6 + i * 3.3, i + 1, q)

    # ===================================================== 44. MISSION DONE ===
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
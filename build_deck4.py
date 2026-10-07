# -*- coding: utf-8 -*-
"""Build Slides/M2/myCobot_04.pptx -- 'Copying Your Hand' (M2-P4).

Rebuilds the deck from the theme/layouts of the reference sample
Slides/myCobot_08.pptx, but teaches the MediaPipe hand-tracking control loop
that students complete in M2/M2-P4-Starter.py.

Every code snippet below is copied verbatim from M2/M2-P4-Base.py, except:
  * the two shell commands (scp / python),
  * sample terminal output,
  * worksheet blanks,
  * four over-long source lines, wrapped at a comma or at their trailing
    comment so they stay legible at projector size. No character is changed,
    dropped or reordered -- see the notes on those slides.
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
OUT = os.path.join(HERE, 'Slides', 'M2', 'myCobot_04.pptx')
TMP = os.path.join(HERE, 'tmp_media')

STARTER = 'M2-P4-Starter.py'
# Project 4 is the first one that physically moves the arm, so the copy step
# also assumes the arm is powered on and connected.
SCP = f'scp {STARTER} er@192.168.1.149:Documents'
RUN = f'python {STARTER}'

# Courier New advances exactly 0.6 em, so one character is this many cm
# per point of font size. code() insets its panel by 0.62 cm each side.
CM_PER_CHAR_PT = 0.6 * 2.54 / 72.0
CODE_INSET = 1.24


def codefit(lines, w=W_WIDE, pad=0.6, lo=9.0, hi=SZ_CODE):
    """Pick the largest font size at which every line fits inside the panel."""
    longest = max(len(ln) for ln in lines)
    avail = w - CODE_INSET - pad
    return max(lo, min(hi, avail / (longest * CM_PER_CHAR_PT)))


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
    para(tf, True, 'Project 4', F_TITLE, SZ_DIVIDER, YELLOW, line_spacing=1.0)
    para(tf, False, 'Copying Your Hand', F_TITLE, SZ_DIVIDER, WHITE, line_spacing=1.0)

    # ============================================== 3. WHAT CHANGED IN P4 ===
    s = add()
    title(s, [('What is different about Project 4', None)])
    body(s, Y_BODY_STD, [
        [('The first three projects all ended the same way. Look at the board, '
          'decide something, draw a box, stop. Do it once and you are finished.', None)],
        [('This project has no finish. The camera looks at your hand, the arm '
          'moves to match it, the camera looks again, and that happens sixty times '
          'a second until you press ', None), ('q', 'c'), ('.', None)],
    ])
    callout(s, 10.2, [
        ('That is the whole difference, and it changes how you write the code. A '
         'one-shot program has one answer to get right. A control loop has to be '
         'right sixty times a second, forever, while a real arm is attached.', None),
    ])
    note(s, 14.4, [
        [('This is the first project where the arm actually moves while you watch. '
          'In Projects 1 to 3 a bug meant a wrong number on the screen. In Project 4 '
          'a bug can mean the arm drives into a limit while you are standing next '
          'to it. Every safety habit in this module was built for this week.', None)],
    ], h=2.6)

    # ================================================== 4. THE CLOSED LOOP ===
    s = add()
    title(s, [('A loop that never finishes', None)])
    body(s, Y_BODY_STD, [
        [('Project 3 had a helper that captured frames in the background. This '
          'project does not need one. The loop is short enough to sit in the '
          'foreground, and the arm commands have to be issued from the same place '
          'as the decisions that cause them.', None)],
    ])
    code(s, 8.4, [
        'try:',
        '    while cap.isOpened():',
        '        ...                      # look, decide, move, repeat',
        '',
        'finally:',
        '    cap.release()',
        '    cv2.destroyAllWindows()',
        '    mc.release_all_servos()',
    ], size=15.0)
    body(s, 15.4, [
        [('Read that ', None), ('finally', 'c'), (' carefully. There is no ', None),
         ('except', 'c'), (' in this program at all. It is not handling errors — it '
          'is guaranteeing that the arm lets go no matter how the program ends, '
          'including ', None), ('Ctrl+C', 'c'), ('.', None)],
    ])
    note(s, 17.4, [
        [('That is the difference: an except swallows a mistake and carries on; '
          'a finally runs on the way out, always.', None)],
    ], h=2.4)

    # ============================================= 5. HARDWARE FIRST, ALWAYS ===
    s = add()
    title(s, [('Put the arm on first', None)])
    body(s, Y_BODY_STD, [
        [('Project 4 is the first project that will not run at all without the '
          'robot. Look at where the arm is created:', None)],
    ])
    code(s, 7.6, [
        "mc = MyCobot280('/dev/ttyAMA0', 1000000)",
        'time.sleep(0.5)',
    ], size=15.0)
    body(s, 10.4, [
        [('That is line 16. It sits at the top level of the file, outside the ', None),
         ('try', 'c'), (' block, and outside any function. Nothing in it is a TODO. '
          'So it runs before you have written a single line of your own work.', None)],
    ])
    callout(s, 13.4, [
        ('No arm connected means no program. If the arm is off or unplugged you '
         'get a ', None),
        ('serial error at line 16', 'c'),
        (' and you will never reach any of the code you actually came to write. '
         'Power the arm on, plug the cable in, then start typing.', None),
    ], h=2.0)
    note(s, 16.2, [
        [('Compare Projects 1 to 3: the arm was created inside main() behind a '
          'try/except, so a missing robot printed a friendly message. Project 4 '
          'deliberately does not — it assumes real hardware is present.', None)],
    ], h=2.8)

    # ================================================== 6. A HAND IS 21 NUMS ===
    s = add()
    title(s, [('A hand is 21 numbers', None)])
    body(s, Y_BODY_STD, [
        [('MediaPipe is not OpenCV. In Project 3 you loaded a YOLO model and it '
          'handed back boxes and class names. MediaPipe has a model built in, '
          'trained on hands, and it hands back ', None),
         ('21 landmarks', 'c'), (' — one point per joint, from wrist to fingertip.', None)],
    ])
    body(s, 10.6, [
        [('Every landmark carries three numbers:', None)],
        [('.x', 'c'), ('  how far across the picture, ', None), ('0.0', 'c'),
         (' at the left edge to ', None), ('1.0', 'c'), (' at the right edge', None)],
        [('.y', 'c'), ('  how far down the picture, ', None), ('0.0', 'c'),
         (' at the top to ', None), ('1.0', 'c'), (' at the bottom', None)],
        [('.z', 'c'), ('  roughly how far the joint is from the camera, in the '
          'same 0.0 to 1.0 units', None)],
    ])
    note(s, 16.4, [
        [('The bundle of 21 is what MediaPipe calls a hand landmark set, and in '
          'this program it arrives as results.multi_hand_landmarks — a list of '
          'hands, each one a list of 21 landmarks. Two lists deep before you get to '
          'any real data.', None)],
    ], h=2.2)

    # ===================================================== 7. NAMES, NOT NUMS ===
    s = add()
    title(s, [('Names instead of counting', None)])
    body(s, Y_BODY_STD, [
        [('You could reach the fingertip with hand_landmarks.landmark[8]. It '
          'works. It also means that if your memory of which finger is number 8 is '
          'wrong, the arm will do something baffling.', None)],
        [('MediaPipe ships a list of names instead, and this project uses it:', None)],
    ])
    code(s, 10.2, [
        '                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]',
        '                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]',
    ], size=11.5)
    body(s, 14.0, [
        [('INDEX_FINGER_TIP', 'c'), (' says exactly what it is. When the arm moves '
          'the wrong way in Project 4, this is the first place to look, because '
          'the alternative — a bare ', None), ('8', 'c'), (' — tells you nothing '
          'about which finger you actually grabbed.', None)],
    ])
    note(s, 16.8, [
        [('Note the attribute name: hand_landmarks.landmark is singular even though '
          'it holds 21 of them. That is not a typo in your file, and it is not a '
          'typo in this slide. Typing .landmarks there is the single most common '
          'error in this project and the error message will tell you nothing '
          'helpful.', None)],
    ], h=2.4)

    # ==================================================== 8. FRACTIONS, NOT PX ===
    s = add()
    title(s, [('Fractions, not pixels', None)])
    body(s, Y_BODY_STD, [
        [('This is the change that catches people who are comfortable with '
          'Project 3. In Project 3 the ArUco corners gave you pixel coordinates: '
          '640 by 480, big numbers, easy to reason about.', None)],
        [('MediaPipe gives you fractions of the picture instead. ', None),
         ('index_tip.x', 'c'), (' of ', None), ('0.5', 'c'),
         (' means the fingertip is halfway across the frame, whatever resolution '
          'the camera happens to be running at.', None)],
    ])
    callout(s, 12.6, [
        ('This matters for two reasons. It works at any camera size, and it means '
         'you never have to divide by the frame width yourself. It also means a '
         'distance like the pinch threshold is a fraction of the picture, not a '
         'count of pixels — ', None),
        ('a fact you will want again in two slides.', 'c'),
    ], h=2.44)
    note(s, 16.2, [
        [('One consequence worth noticing now: because these are fractions rather '
          'than pixels, moving your hand towards the camera makes your fingers '
          'look further apart on screen even though your pinch is identical. '
          'Nothing has gone wrong. The measurement changed with the distance.', None)],
    ], h=2.2)

    # ========================================================== 9. THE MIRROR ===
    s = add()
    title(s, [('The mirror', None)])
    body(s, Y_BODY_STD, [
        [('A camera sees you. You see the picture.', None)],
        [('The two are opposite. If the picture is not flipped, moving your hand to '
          'your right moves it to the left of the screen, and the arm — which '
          'faithfully copies what it sees — moves to your left instead of your '
          'right. Everything is working perfectly and feels broken.', None)],
    ])
    code(s, 10.8, [
        '        frame = cv2.flip(frame, 1)',
    ], size=15.0)
    body(s, 12.8, [
        [('The ', None), ('1', 'c'), (' means flip horizontally. No vertical flip, '
          'so up is still up.', None)],
    ])
    note(s, 14.6, [
        [('This one line is the difference between the arm feeling like a mirror '
          'and feeling like it is arguing with you. If the arm responds but the '
          'wrong way along one axis, check this line before you check the map '
          'values — and remember this flip happens after the read and before the '
          'colour conversion, so everything downstream sees the flipped picture.', None)],
    ], h=2.8)

    # ==================================================== 10. WRONG COLOURS ===
    s = add()
    title(s, [('Wrong order, wrong colours', None)])
    body(s, Y_BODY_STD, [
        [('Project 3 also converted colour, for the same reason. OpenCV reads '
          'pictures as blue, green, red. MediaPipe was trained on red, green, '
          'blue.', None)],
    ])
    code(s, 8.2, [
        '        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)',
        '        results = hands.process(rgb_frame)',
    ], size=13.0)
    body(s, 11.4, [
        [('Two separate jobs on two lines, and the order is fixed. Convert first, '
          'then process the converted picture.', None)],
        [('You are also about to draw the skeleton back onto ', None),
         ('frame', 'c'), (', which is still blue-green-red — so the drawing code '
          'later in the loop wants ', None), ('frame', 'c'), (' and the detection '
          'code here wants ', None), ('rgb_frame', 'c'), ('. Both names are in the '
          'file for a reason.', None)],
    ])
    note(s, 16.0, [
        [('A swapped colour order does not crash. It quietly makes the model worse '
          'at its job, so this is the kind of mistake that looks like bad lighting '
          'rather than like a bug. If the skeleton is found but the detection is '
          'odd, swap the order back and watch what changes.', None)],
    ], h=2.4)

    # ================================================ 11. TRACKING VS IMAGES ===
    s = add()
    title(s, [('Watching beats looking', None)])
    body(s, Y_BODY_STD, [
        [('MediaPipe can treat every frame as a fresh photograph, or as the next '
          'frame in a video. Project 4 asks for the second one:', None)],
    ])
    code(s, 8.0, [
        'hands = mp_hands.Hands(',
        '    static_image_mode=False,',
        '    max_num_hands=1,',
        '    min_detection_confidence=0.7,',
        '    min_tracking_confidence=0.7',
        ')',
    ], size=13.0)
    body(s, 14.0, [
        [('static_image_mode', 'c'), (' set to ', None), ('False', 'c'),
         (' means the first frame is expensive — it looks for a hand from scratch '
          '— and every frame after that is cheap, because it only has to follow '
          'the hand it already found.', None)],
    ])
    note(s, 16.8, [
        [('This is the same idea as the threaded camera in Project 3, aimed at the '
          'model instead of the sensor. Switch it to True and the program still '
          'works, just several times slower, which for a program that has to keep '
          'up with a hand is not fast enough.', None)],
    ], h=2.2)

    # ========================================================== 12. ONE HAND ===
    s = add()
    title(s, [('Only one hand', None)])
    body(s, Y_BODY_STD, [
        [('max_num_hands=1', 'c'), (' is a safety limit wearing a disguise. It '
          'looks like a setting, and it is, but read it as a promise: this program '
          'will never be confused about whose hand it is copying.', None)],
        [('The loop agrees. Even if MediaPipe did report two hands, the code walks '
          'through them one at a time and the last one wins — which would be a '
          'terrible way to control a real arm.', None)],
    ])
    callout(s, 12.0, [
        ('Two people in front of the camera is a genuinely dangerous situation for '
         'this program, and the setting is the only thing standing between them '
         'and a fight over who the arm is listening to. ', None),
        ('Keep it at 1.', 'c'),
    ], h=2.0)
    note(s, 15.2, [
        [('Both confidences sit at 0.7. Lower them and the program becomes '
          ' twitchier and more likely to invent a hand that is not there; raise '
          'them and it stops tracking when your hand moves quickly. 0.7 is a '
          'reasonable middle, and it is a value you will be asked to justify in '
          'the debrief.', None)],
    ], h=2.4)

    # ================================================= 13. FRACTIONS TO MM ===
    s = add()
    title(s, [('From fractions to millimetres', None)])
    body(s, Y_BODY_STD, [
        [('The arm does not want 0.5. It wants 190 millimetres. This is the job '
          'of the mapping function, and it is the single idea holding this project '
          'together.', None)],
    ])
    code(s, 7.4, [
        'def map_value(value, in_min, in_max, out_min, out_max):',
        '    """Maps a value from one range to another and clamps it."""',
        '    clamped_val = max(in_min, min(in_max, value))',
        '    return out_min + (clamped_val - in_min) * (out_max - out_min) / (in_max - in_min)',
    ], size=12.5)
    body(s, 13.4, [
        [('Five arguments, and the last two are allowed to be backwards. Read the '
          'middle of the return line as ', None),
         ('how far through the input range am I, times the output range, plus the '
          'output minimum', 'c'), ('.', None)],
    ])
    note(s, 15.4, [
        [('Because out_min and out_max can be in either order, the same function '
          'maps forwards and backwards. That is not a trick, it is just arithmetic '
          '— a negative range flips the direction. Step 10 needs both directions '
          'on the same axis.', None)],
    ], h=2.4)

    # ==================================================== 14. THE CLAMP MATTERS ===
    s = add()
    title(s, [('The clamp is the safety', None)])
    body(s, Y_BODY_STD, [
        [('Look again at that function and find the line that is not arithmetic:', None)],
    ])
    code(s, 7.4, [
        '    clamped_val = max(in_min, min(in_max, value))',
    ], size=15.0)
    body(s, 9.4, [
        [('It pulls ', None), ('value', 'c'), (' inside ', None),
         ('[in_min, in_max]', 'c'), (' before doing anything else. If a landmark '
          'ever reports 1.4 or -0.3 or something absurd, this function cannot pass '
          'that on.', None)],
    ])
    callout(s, 12.6, [
        ('This one line is what stops the arm being told to go somewhere it must '
         'never go. The workspace limits in this file are X between 130 and 250, Y '
         'between -160 and 160, and a fixed 180 of height. The clamp is what turns '
         'those four numbers into ', None),
        ('a guarantee rather than a suggestion.', 'c'),
    ], h=2.44)
    note(s, 16.4, [
        [('Notice the order inside: min first, then max. min(in_max, value) can '
          'only be at or below in_max; max lifts it back to in_min. Written the '
          'other way round, the two bounds would be supplied opposite.', None)],
    ], h=2.6)

    # ================================================== 15. MIDDLE 60% ONLY ===
    s = add()
    title(s, [('Only the middle sixty percent', None)])
    body(s, Y_BODY_STD, [
        [('Now watch the numbers that get passed in during Step 10. The input '
          'range is not 0.0 to 1.0. It is 0.2 to 0.8.', None)],
    ])
    callout(s, 8.4, [
        ('So the top fifth and bottom fifth of your picture do nothing at all. Your '
         'hand has to be inside the middle sixty percent before the arm moves, and '
         'anywhere in that dead band the arm sits at its limit and stays there. '
         'This is deliberate: ', None),
        ('you cannot drive the arm to either end of its travel by accident.', 'c'),
    ], h=2.44)
    body(s, 12.2, [
        [('It also makes the control feel better. Without the dead band, the arm '
          'would creep very slowly near the top and bottom of the range, because '
          'small hand movements map to large arm movements when you are near a '
          'limit.', None)],
    ])
    note(s, 15.4, [
        [('You can change 0.2 and 0.8 later and the arm will still work, which is '
          'exactly why they are worth writing down before you start. In the '
          'debrief you should be able to say what they buy you.', None)],
    ], h=2.0)

    # ================================================== 16. TWO POINTS, ONE PINCH ===
    s = add()
    title(s, [('Two points make a pinch', None)])
    body(s, Y_BODY_STD, [
        [('A pinch has no key to press. It has a distance: thumb tip to index '
          'tip. That is all the information a pinch is.', None)],
    ])
    code(s, 8.4, [
        'def calculate_distance(p1, p2):',
        '    """Calculates 2D Euclidean distance between two MediaPipe landmarks."""',
        '    return math.hypot(p1.x - p2.x, p1.y - p2.y)',
    ], size=12.5)
    body(s, 12.6, [
        [('Two landmarks in, one number out. ', None), ('math.hypot', 'c'),
         (' is the straight-line distance between two points, and it saves you '
          'writing the square-root-of-the-squares yourself.', None)],
        [('The result is in fractions of the picture, not pixels — because the '
          'inputs were fractions.', None)],
    ])
    note(s, 16.4, [
        [('Only two dimensions are used. The z value of each landmark is ignored, '
          'which means this measures how close the fingers look on screen rather '
          'than how close they are in the room. That is a deliberate simplification, '
          'and for a hand held roughly upright in front of a camera it behaves well.', None)],
    ], h=2.6)

    # ==================================================== 17. ONE NUMBER DECIDES ===
    s = add()
    title(s, [('One number decides', None)])
    body(s, Y_BODY_STD, [
        [('The gesture itself is a comparison and nothing else:', None)],
    ])
    code(s, 7.4, [
        '                pinch_distance = calculate_distance(thumb_tip, index_tip)',
        '                is_pinching = pinch_distance < 0.08  # Threshold for closed pinch',
    ], size=13.0)
    body(s, 10.6, [
        [('A boolean. Every later decision in this program hangs off ', None),
         ('is_pinching', 'c'), (' — the gripper command, the colour of the circle, '
          'and the colour of the text on screen. Set it once and three things '
          'follow.', None)],
    ])
    note(s, 13.6, [
        [('0.08 is a fraction of the picture, so it is roughly eight percent of '
          'the frame. Because it is measured in fractions and not pixels, moving '
          'your hand closer to the camera shrinks the apparent distance and the '
          'same physical pinch stops registering — you have to pinch tighter. Keep '
          'your hand at a roughly constant distance from the camera and this '
          'behaves predictably.', None)],
    ], h=2.8)

    # ==================================================== 18. SIX NUMBERS MOVE IT ===
    s = add()
    title(s, [('Six numbers move the arm', None)])
    body(s, Y_BODY_STD, [
        [('The arm is told where to go with one call carrying six values:', None)],
    ])
    code(s, 7.6, [
        '                    mc.send_coords([robot_x, robot_y, Z_HEIGHT, -180, 0, -135], ARM_SPEED, 0)',
    ], size=11.0)
    body(s, 10.0, [
        [('X, Y and Z are millimetres from the base of the arm. The other three are '
          'degrees of wrist rotation, and in this program ', None),
         ('they never change', 'c'), ('. Only two numbers in the whole list are '
          'ever anything else.', None)],
        [('The last argument is 0, meaning move there now. ', None),
         ('ARM_SPEED', 'c'), (' of 50 out of 100 is a deliberate middle — fast '
          'enough to feel responsive, slow enough that a mistake does not become '
          'an incident.', None)],
    ])
    note(s, 15.4, [
        [('Because X, Y and Z arrive as a list of plain numbers, the arm is given '
          'an absolute destination rather than a nudge. There is no memory '
          'between commands — move your hand and the next command describes the '
          'new place entirely.', None)],
    ], h=2.8)

    # ======================================================= 19. OPEN / CLOSED ===
    s = add()
    title(s, [('Open and closed', None)])
    body(s, Y_BODY_STD, [
        [('The gripper is two commands, both inside the rate-limited block:', None)],
    ])
    code(s, 7.6, [
        '                    if is_pinching:',
        '                        mc.set_gripper_state(1, 80) # Close gripper / activate pump',
        '                        status_text = "Pinch Active (GRIP)"',
        '                    else:',
        '                        mc.set_gripper_state(0, 80) # Open gripper / deactivate pump',
        '                        status_text = "Tracking (OPEN)"',
    ], size=11.5)
    body(s, 12.4, [
        [('The first argument is the state — 1 for closed, 0 for open. The second '
          'is a speed. The comments mention a pump because the same command drives '
          'one, and reading the comments is how you know that.', None)],
    ])
    note(s, 15.4, [
        [('Notice that this block sends a gripper command every time the rate limit '
          'allows, whether or not the pinch state has changed. Sending close twenty '
          'times when you have not moved is wasteful, but it is also simple and it '
          'is safe: the arm cannot be left gripping by accident if you shake your '
          'hand open. Simplicity wins here.', None)],
    ], h=2.8)

    # ============================================== 20. THE ARM IS THE BOTTLENECK ===
    s = add()
    title(s, [('The arm is slower than the camera', None)])
    body(s, Y_BODY_STD, [
        [('The camera produces about thirty frames a second. The serial cable to '
          'the arm is far slower than that, and if you ask it for a move on every '
          'single frame the queue behind it grows until the program stalls.', None)],
    ])
    code(s, 9.0, [
        'last_command_time = 0',
        'COMMAND_INTERVAL = 0.15  # Send move command every 150ms',
    ], size=15.0)
    body(s, 11.8, [
        [('A tenth of a second between commands means the arm is told where to go '
          'at most six or seven times a second, while the picture is still examined '
          'thirty times a second.', None)],
    ])
    callout(s, 14.6, [
        ('This is the fix for a problem you have not hit yet, and it is the reason '
         'the program feels smooth rather than twitchy. Notice also where the '
         'telemetry drawing sits — outside this rate limit. ', None),
        ('Drawing is free; moving the arm is not.', 'c'),
    ], h=2.0)

    # ================================================= 21. RATE LIMIT, HONESTLY ===
    s = add()
    title(s, [('Rate limiting, honestly', None)])
    body(s, Y_BODY_STD, [
        [('Here is the whole mechanism:', None)],
    ])
    code(s, 6.8, [
        '                current_time = time.time()',
        '                if current_time - last_command_time > COMMAND_INTERVAL:',
        '                    # Send position command: [X, Y, Z, Rx, Ry, Rz]',
        '                    print(f"Target: X={robot_x:.1f}, Y={robot_y:.1f}, Z={Z_HEIGHT}")',
        '                    mc.send_coords([robot_x, robot_y, Z_HEIGHT, -180, 0, -135], ARM_SPEED, 0)',
        '',
        '                    # Control end-effector based on pinch state',
        '                    if is_pinching:',
        '                        mc.set_gripper_state(1, 80) # Close gripper / activate pump',
        '                        status_text = "Pinch Active (GRIP)"',
        '                    else:',
        '                        mc.set_gripper_state(0, 80) # Open gripper / deactivate pump',
        '                        status_text = "Tracking (OPEN)"',
        '',
        '                    last_command_time = current_time',
    ], size=11.0)
    body(s, 12.0, [
        [('Compare, act, then update the record. On the very first frame the stored '
          'time is 0, so the difference is enormous and the block always runs at '
          'least once.', None)],
    ])
    note(s, 15.6, [
        [('status_text looks like a bug: assigned inside the if block, read far '
          'below it. It works because the block runs on the first frame, so the '
          'name always exists from then on.', None)],
    ], h=3.0)

    # ======================================================= 22. LETTING GO ===
    s = add()
    title(s, [('Letting go at the end', None)])
    body(s, Y_BODY_STD, [
        [('The last three lines of the file are the ones that matter when '
          'something has gone wrong:', None)],
    ])
    code(s, 8.0, [
        'finally:',
        '    cap.release()',
        '    cv2.destroyAllWindows()',
        '    mc.release_all_servos()',
    ], size=15.0)
    body(s, 12.0, [
        [('cap.release()', 'c'), (' hands the camera back so the next program can '
          'have it. ', None), ('destroyAllWindows()', 'c'), (' closes the window. '
          'And ', None), ('release_all_servos()', 'c'), (' lets the arm go limp.', None)],
    ])
    callout(s, 14.8, [
        ('Limp means you can move the arm by hand afterwards, and it means the '
         'motors are not holding position against your fingers while you reach in '
         'to unplug something. If the servos buzz or the arm will not budge after '
         'the program exits, ', None),
        ('this line has been deleted or skipped.', 'c'),
    ], h=2.2)
    note(s, 17.0, [
        [('Because it is a finally block, it runs even when the program crashes — '
          'the entire reason the cleanup lines live here.', None)],
    ], h=2.0)

    # ==================================================== 23. SAFETY SUMMARY ===
    s = add()
    title(s, [('What could actually hurt someone', None)])
    body(s, Y_BODY_STD, [
        [('Before any code, the list of things standing between this program and an '
          'injury. Every one of them is a decision already made for you:', None)],
    ])
    check_item(s, 8.6, [
        ('The mapping is clamped to 0.2–0.8 before it becomes millimetres.', None),
    ])
    check_item(s, 10.6, [
        ('The arm is confined to X 130–250, Y -160–160, and a fixed height of 180.', None),
    ])
    check_item(s, 12.6, [
        ('Only one hand is ever listened to.', None),
    ])
    check_item(s, 14.6, [
        ('The arm moves at half speed, six times a second, never faster.', None),
    ])
    check_item(s, 16.6, [
        ('If the hand leaves the picture the arm is not given any new instruction '
          'at all.', None),
    ])
    check_item(s, 18.6, [
        ('And if you stop the program, the servos are released.', None),
    ])

    # ======================================================== 24. STEP 1 ===
    s = add()
    title(s, [('Step 1', None)])
    body(s, Y_BODY_STD, [
        [('The module’s standard import block, with two additions for this project:', None)],
    ])
    code(s, 7.6, [
        'import cv2',
        'import mediapipe as mp',
        'import math',
        'import time',
        'import numpy as np',
    ], size=15.0)
    body(s, 12.6, [
        [('cv2', 'c'), (' is the camera, the drawing and the colour conversion. ', None),
         ('math', 'c'), (' is for one function. ', None), ('time', 'c'),
         (' does the rate limiting. ', None), ('mediapipe', 'c'), (' is the new one.', None)],
    ])
    note(s, 15.2, [
        [('numpy is in this list and is not used anywhere in Project 4 — not once. '
          'It is in the import block of every project in this module, and it earns '
          'its place in Projects 1, 2 and 3. Here it does nothing. That is harmless, '
          'and it is also a clue: if you are wondering why your frame shape behaves '
          'as an object rather than a list, this is where that comes from.', None)],
    ], h=2.8)

    # ======================================================== 25. STEP 2 ===
    s = add()
    title(s, [('Step 2', None)])
    body(s, Y_BODY_STD, [
        [('The arm, exactly as in the previous three projects:', None)],
    ])
    code(s, 6.4, [
        'from pymycobot.mycobot280 import MyCobot280',
    ], size=15.0)
    body(s, 8.4, [
        [('Then the two lines of setup that are not a TODO but which you should '
          'read carefully anyway:', None)],
    ])
    code(s, 11.0, [
        "mc = MyCobot280('/dev/ttyAMA0', 1000000)",
        'time.sleep(0.5)',
        '',
        'X_MIN, X_MAX = 130, 250   # Forward / Backward range',
        'Y_MIN, Y_MAX = -160, 160  # Left / Right range',
        'Z_HEIGHT = 180            # Fixed height above surface (mm)',
        'ARM_SPEED = 50            # Movement speed (1-100)',
    ], size=12.5)
    note(s, 17.4, [
        [('The workspace numbers sit at the top so every later calculation uses '
          'them once. The half-second sleep lets the arm finish booting after the '
          'serial port opens — a command to a still-starting robot is a classic '
          'lost first command.', None)],
    ], h=2.4)

    # ============================================== 26. GETTING IT ONTO THE ARM ===
    s = add()
    title(s, [('Copy it, and start it once', None)])
    body(s, Y_BODY_STD, [
        [('One file this time — but the arm must be powered on and plugged in '
          'before you run anything:', None)],
    ])
    command(s, 6.8, SCP)
    command(s, 9.2, RUN)
    body(s, 11.6, [
        [('Run it now, with every vision TODO still empty. Expect this:', None)],
    ])
    code(s, 13.2, [
        'Traceback (most recent call last):',
        '  File "M2-P4-Starter.py", line 63, in <module>',
        '    while cap.isOpened():',
        'NameError: name \'cap\' is not defined',
    ], size=12.5)
    body(s, 16.2, [
        [('The camera TODO stayed empty, so ', None), ('cap', 'c'),
         (' was never created and the loop asked for it anyway.', None)],
    ])
    note(s, 17.8, [
        [('A serial error at line 16 means the arm is not there. Power it on '
          'and run again before changing any code.', None)],
    ], h=1.8)

    # ======================================================== 27. STEP 3 ===
    s = add()
    title(s, [('Step 3', None)])
    body(s, Y_BODY_STD, [
        [('Two lines to name the parts of MediaPipe you will use, then the model '
          'itself:', None)],
    ])
    code(s, 7.4, [
        'mp_hands = mp.solutions.hands',
        'mp_drawing = mp.solutions.drawing_utils',
        '',
        'hands = mp_hands.Hands(',
        '    static_image_mode=False,',
        '    max_num_hands=1,',
        '    min_detection_confidence=0.7,',
        '    min_tracking_confidence=0.7',
        ')',
    ], size=12.5)
    body(s, 14.4, [
        [('The first two lines are shortcuts so the rest of the file can say ', None),
         ('mp_hands', 'c'), (' instead of ', None), ('mp.solutions.hands', 'c'),
         ('. This is the first project in the module to use MediaPipe, and '
          'Project 6 will use it again the same way.', None)],
    ])

    # ======================================================== 28. STEP 4 ===
    s = add()
    title(s, [('Step 4', None)])
    body(s, Y_BODY_STD, [
        [('The camera, the same three lines as Project 3:', None)],
    ])
    code(s, 6.4, [
        'cap = cv2.VideoCapture(0)',
        'cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)',
        'cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)',
    ], size=13.0)
    body(s, 10.2, [
        [('Nothing to think about here beyond one point: the resolution you ask for '
          'is not a promise. Some cameras give you 640 by 480, some ignore the '
          'request, and that is fine.', None)],
        [('It is fine because everything downstream works in fractions. '
          'MediaPipe does not care what the frame is called, and the code never '
          'multiplies a landmark by a width.', None)],
    ])
    note(s, 15.4, [
        [('That is the payoff for the choice on slide eight. In Project 3 you had to '
          'know the pixel size, because the detector returned pixel coordinates. '
          'Here you never do, so this step cannot be the reason the program fails '
          'later.', None)],
    ], h=2.6)

    # ======================================================== 29. STEP 5 ===
    s = add()
    title(s, [('Step 5', None)])
    body(s, Y_BODY_STD, [
        [('The mapping function, the whole of it:', None)],
    ])
    code(s, 6.4, [
        'def map_value(value, in_min, in_max, out_min, out_max):',
        '    """Maps a value from one range to another and clamps it."""',
        '    clamped_val = max(in_min, min(in_max, value))',
        '    return out_min + (clamped_val - in_min) * (out_max - out_min) / (in_max - in_min)',
    ], size=12.5)
    body(s, 12.4, [
        [('Do not simplify the return line. The whole expression is one line in '
          'the file and it is worth typing exactly.', None)],
    ])
    note(s, 14.4, [
        [('If you want to be sure it is right, test it away from the robot: '
          'map_value(0.5, 0.2, 0.8, 130, 250) is 190, the middle of the range. '
          'map_value(0.9, 0.2, 0.8, 130, 250) is still 250, because of the clamp. '
          'Those two numbers are worth being able to produce on request.', None)],
    ], h=2.6)

    # ======================================================== 30. STEP 6 ===
    s = add()
    title(s, [('Step 6', None)])
    body(s, Y_BODY_STD, [
        [('The distance function. Three lines, and the middle one is a docstring '
          'that you should keep:', None)],
    ])
    code(s, 8.4, [
        'def calculate_distance(p1, p2):',
        '    """Calculates 2D Euclidean distance between two MediaPipe landmarks."""',
        '    return math.hypot(p1.x - p2.x, p1.y - p2.y)',
    ], size=12.5)
    body(s, 12.6, [
        [('This is the first project where a helper takes MediaPipe objects as '
          'arguments. It works because a landmark has ', None), ('.x', 'c'),
         (' and ', None), ('.y', 'c'), (' on it, so this function never needs to '
          'know what it is measuring.', None)],
    ])
    note(s, 15.4, [
        [('Two independent guesses about what the arguments are will both fail '
          'loudly and differently: forget the parentheses and you get a TypeError '
          'about missing arguments; pass two whole hands instead of two landmarks '
          'and you get an AttributeError about .x. Both messages point straight at '
          'this function.', None)],
    ], h=2.6)

    # ======================================================== 31. STEP 7 ===
    s = add()
    title(s, [('Step 7', None)])
    body(s, Y_BODY_STD, [
        [('Reading the frame, flipping it, converting it, and asking MediaPipe. '
          'Five lines, in that order:', None)],
    ])
    code(s, 8.0, [
        '        success, frame = cap.read()',
        '        if not success:',
        '            continue',
        '',
        '        # Flip horizontally for intuitive mirror view',
        '        frame = cv2.flip(frame, 1)',
        '        h, w, _ = frame.shape',
        '        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)',
        '        results = hands.process(rgb_frame)',
    ], size=12.5)
    body(s, 15.2, [
        [('The ', None), ('continue', 'c'), (' matters more than it looks: it '
          'skips the rest of the loop body and goes straight back for another '
          'frame, rather than carrying on with a frame that was never filled in.', None)],
    ])
    note(s, 17.0, [
        [('h, w, _ = frame.shape is the Project 1 unpacking, read here because it '
          'is the first line in the loop with a frame to measure.', None)],
    ], h=2.2)

    # ======================================================== 32. STEP 8 ===
    s = add()
    title(s, [('Step 8', None)])
    body(s, Y_BODY_STD, [
        [('Draw the skeleton. One line, and it draws onto ', None),
         ('frame', 'c'), (' — not onto ', None), ('rgb_frame', 'c'), (':', None)],
    ])
    code(s, 7.6, [
        '                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)',
    ], size=11.5)
    body(s, 10.4, [
        [('Three arguments: the image to draw on, the landmarks, and the list of '
          'pairs describing which joints connect to which. The connections list is '
          'part of MediaPipe, which is why it is reached through ', None),
         ('mp_hands', 'c'), (' rather than being written out here.', None)],
    ])
    note(s, 14.4, [
        [('This line runs before the landmarks are extracted on the next step, and '
          'that is fine — drawing does not need to know which two joints you are '
          'about to use. Read the loop as: draw everything, then use what you need. '
          'If the skeleton appears but the circle does not, this step is done and '
          'Step 13 is not.', None)],
    ], h=3.0)

    # ======================================================== 33. STEP 9 ===
    s = add()
    title(s, [('Step 9', None)])
    body(s, Y_BODY_STD, [
        [('Now pick out the two joints the rest of the program cares about:', None)],
    ])
    code(s, 7.4, [
        '                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]',
        '                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]',
    ], size=11.5)
    body(s, 10.6, [
        [('Two names, and from here on the program stops thinking about hands '
          'entirely. It has an ', None), ('index_tip', 'c'), (' and a ', None),
         ('thumb_tip', 'c'), (', and it never needs the other nineteen landmarks '
          'again.', None)],
    ])
    note(s, 13.8, [
        [('Two of twenty-one landmarks is all this project uses. Project 6 counts '
          'fingers instead, and needs rather more of them. It is worth noticing how '
          'little of the model output Project 4 actually touches — the hard part '
          'was never the landmarks, it was the millimetres.', None)],
    ], h=2.8)

    # ======================================================= 34. STEP 10 ===
    s = add()
    title(s, [('Step 10', None)])
    body(s, Y_BODY_STD, [
        [('The heart of the project. Two lines, one per axis:', None)],
    ])
    code(s, 6.8, [
        '                robot_x = map_value(index_tip.y, 0.2, 0.8, X_MAX, X_MIN)',
        '                # Vertical hand position -> Robot Forward/Back',
        '                robot_y = map_value(index_tip.x, 0.2, 0.8, Y_MIN, Y_MAX)',
        '                # Horizontal hand position -> Robot Left/Right',
    ], size=13.0)
    body(s, 11.4, [
        [('Both lines are wrapped here so they fit the screen — in your file each '
          'is one long line with its comment at the end. Every character is the '
          'same.', None)],
        [('Look at the ', None), ('X', 'c'), (' line carefully. The finger’s ', None),
         ('height', 'b'), (' sets how far forward the arm reaches, and the output '
          'range is given as ', None), ('X_MAX, X_MIN', 'c'), (' — backwards.', None)],
    ])
    note(s, 15.6, [
        [('Backwards on purpose. y is small at the top of the picture, so raising '
          'your hand maps to X_MAX and the arm reaches forward. Combined with the '
          'mirror flip, that is the behaviour you want; if the arm goes the other '
          'way, swap those two arguments.', None)],
    ], h=3.0)

    # ======================================================= 35. STEP 11 ===
    s = add()
    title(s, [('Step 11', None)])
    body(s, Y_BODY_STD, [
        [('The pinch. Call the function you wrote, then compare:', None)],
    ])
    code(s, 6.8, [
        '                pinch_distance = calculate_distance(thumb_tip, index_tip)',
        '                is_pinching = pinch_distance < 0.08  # Threshold for closed pinch',
    ], size=13.0)
    body(s, 9.8, [
        [('Nothing here is new — Step 6 built the measurement and slide seventeen '
          'explained the comparison. What is new is that this boolean now decides '
          'whether the gripper closes.', None)],
    ])
    note(s, 12.6, [
        [('Change 0.08 too early and you will spend an afternoon convinced the '
          'gripper is broken. Leave it exactly as it is until the whole program '
          'runs, then tune it once with the telemetry on screen. There is a slide '
          'on the cost of moving it near the end.', None)],
    ], h=2.8)

    # ======================================================= 36. STEP 12 ===
    s = add()
    title(s, [('Step 12', None)])
    body(s, Y_BODY_STD, [
        [('The longest block in the project, and the one that moves the arm:', None)],
    ])
    code(s, 6.6, [
        '                current_time = time.time()',
        '                if current_time - last_command_time > COMMAND_INTERVAL:',
        '                    # Send position command: [X, Y, Z, Rx, Ry, Rz]',
        '                    print(f"Target: X={robot_x:.1f}, Y={robot_y:.1f}, Z={Z_HEIGHT}")',
        '                    mc.send_coords([robot_x, robot_y, Z_HEIGHT, -180, 0, -135], ARM_SPEED, 0)',
        '',
        '                    # Control end-effector based on pinch state',
        '                    if is_pinching:',
        '                        mc.set_gripper_state(1, 80) # Close gripper / activate pump',
        '                        status_text = "Pinch Active (GRIP)"',
        '                    else:',
        '                        mc.set_gripper_state(0, 80) # Open gripper / deactivate pump',
        '                        status_text = "Tracking (OPEN)"',
        '',
        '                    last_command_time = current_time',
    ], size=11.0)
    note(s, 12.2, [
        [('Two details to get right. Everything that touches the arm sits inside '
          'the if, including the gripper calls and the assignment to '
          'last_command_time. And the print comes before the move, so if the arm '
          'is not moving at all but numbers are appearing in the terminal, the '
          'program has already calculated a target and failed to deliver it — which '
          'is a different fault from producing no numbers at all.', None)],
    ], h=2.6)

    # ============================================= 37. STEP 13 (PART ONE) ===
    s = add()
    title(s, [('Step 13', None)])
    body(s, Y_BODY_STD, [
        [('Telemetry, part one: the circle, and the position readout.', None)],
    ])
    code(s, 6.4, [
        '                cx, cy = int(index_tip.x * w), int(index_tip.y * h)',
        '                cv2.circle(frame, (cx, cy), 10, (0, 255, 0) if not is_pinching else (0, 0, 255), -1)',
        '',
        '                telemetry = f"Robot Target -> X: {int(robot_x)}mm | Y: {int(robot_y)}mm"',
        '                cv2.putText(frame, telemetry, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)',
    ], size=9.5)
    body(s, 12.8, [
        [('Here the fractions finally become pixels. ', None), ('index_tip.x * w', 'c'),
         (' turns "halfway across" into an actual column number, which is the only '
          'kind of thing ', None), ('cv2.circle', 'c'), (' can use.', None)],
        [('Green circle means open, red means pinching — the same condition as the '
          'gripper, read one more time.', None)],
    ])
    note(s, 16.8, [
        [('This whole block sits outside the rate limit on purpose, so the overlay '
          'updates smoothly even though the arm is commanded only seven times a '
          'second. The screen rounds with int() and the terminal prints one '
          'decimal — neither is wrong; do not be surprised they differ.', None)],
    ], h=2.8)

    # ============================================ 38. STEP 13 (PART TWO) ===
    s = add()
    title(s, [('Step 13, continued', None)])
    body(s, Y_BODY_STD, [
        [('And the state readout, which is the longest line in the project:', None)],
    ])
    code(s, 7.4, [
        '                cv2.putText(frame, f"State: {status_text}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, ',
        '                (0, 255, 0) if not is_pinching else (0, 0, 255), 2)',
    ], size=10.5)
    body(s, 10.6, [
        [('Wrapped across two lines here for the same reason as Step 10 — in the '
          'file it is a single line of 152 characters. The colour is chosen the '
          'same way as the circle: green while open, red while pinching.', None)],
    ])
    note(s, 13.4, [
        [('This is the third and last read of is_pinching in one loop: the gripper '
          'command, the circle colour, and now this text. One boolean, three '
          'consequences. If you ever find yourself writing the pinch test a fourth '
          'time, something has gone wrong with your plan rather than your typing.', None)],
    ], h=2.8)

    # ======================================================= 39. STEP 14 ===
    s = add()
    title(s, [('Step 14', None)])
    body(s, Y_BODY_STD, [
        [('The last TODO. Show the picture:', None)],
    ])
    code(s, 6.4, [
        '        cv2.imshow("Mission 2 - Project 04: Hand Control", frame)',
    ], size=13.0)
    body(s, 8.6, [
        [('That is the whole of it. The exit check was already written for you:', None)],
    ])
    code(s, 10.8, [
        "        if cv2.waitKey(1) & 0xFF == ord('q'):",
        '            break',
    ], size=13.0)
    body(s, 13.6, [
        [('The window title is not decoration. It is how you know which program has '
          'the camera, and in a lab where four of these are running it is the only '
          'honest answer to "why can I not see anything".', None)],
    ])
    note(s, 16.4, [
        [('Wait, then show, then go round again. The order matters: waitKey(1) '
          'keeps the window responsive, imshow puts the picture in it, and the loop '
          'condition re-checks that the camera is still open. Press q and the loop '
          'breaks, the finally block runs, and the arm lets go.', None)],
    ], h=2.6)

    # ================================================= 40. READING THE SCREEN ===
    s = add()
    title(s, [('Reading the screen', None)])
    body(s, Y_BODY_STD, [
        [('Four things on the window at once, and each one tells you something:', None)],
    ])
    bullet(s, 8.6, [
        ('The skeleton', 'b'), (' — MediaPipe found a hand. No skeleton means the '
          'problem is lighting, distance, or confidence, not your mapping code.', None),
    ], h=2.2)
    bullet(s, 10.8, [
        ('The circle', 'b'), (' — green while the gripper is open, red while it is '
          'closed. If it never turns red, your pinch threshold or your hand '
          'distance is wrong.', None),
    ], h=2.2)
    bullet(s, 13.0, [
        ('X and Y in millimetres', 'b'), (' — the numbers the arm was last told. '
          'They should move as you move your hand, and they should never leave '
          '130–250 or -160–160.', None),
    ], h=2.2)
    bullet(s, 15.2, [
        ('The state line', 'b'), (' — the same pinch, in words.', None),
    ], h=1.4)
    note(s, 17.0, [
        [('Read them in that order when something is wrong. No skeleton rules out '
          'every step after Step 9. A skeleton but a still circle rules out Steps '
          '10 and 11. Numbers on screen but a motionless arm means Step 12.', None)],
    ], h=2.2)

    # ============================================ 41. BEFORE YOU TUNE ANYTHING ===
    s = add()
    title(s, [('Before you tune anything', None)])
    table(s, 4.2, [
        ['What you see', 'What it means', 'What to do'],
        ['Serial error at line 16',
         'The arm is not connected',
         'Power it on, check the cable, run again'],
        ['NameError: name \'cap\'',
         'Camera TODO still empty',
         'Finish Step 4 before debugging'],
        ['No window at all',
         'Program died before imshow',
         'Read the traceback from the bottom up'],
        ['No skeleton on screen',
         'No hand found in frame',
         'Check lighting and hand distance'],
        ['Skeleton, circle never red',
         'Pinch not reaching 0.08',
         'Tighten the pinch, move the hand closer'],
        ['Arm moves the wrong way',
         'Axis inverted on one direction',
         'Swap X_MAX and X_MIN, not the function'],
        ['Arm will not budge afterwards',
         'Servos never released',
         'Put release_all_servos() back'],
    ], [6.6, 7.2, 10.33], row_h=1.12, head_h=1.25, size=12.5)
    note(s, 16.6, [
        [('Two of these are not really faults. A silent program with no window is '
          'a TODO you have not filled in yet, and an arm that will not move by hand '
          'is the servos doing exactly what they were told. Everything else in that '
          'table is a real fault, and each one points at a single step.', None)],
    ], h=2.4)

    # ================================================ 42. THRESHOLD COSTS ===
    s = add()
    title(s, [('What the thresholds actually cost', None)])
    body(s, Y_BODY_STD, [
        [('Project 3 had three thresholds and no way to reason about them. You have '
          'four, and you can now say what each one trades away.', None)],
    ])
    num_item(s, 9.4, 1, '0.7 detection confidence',
             [('too low and it invents hands that are not there', None)], h=1.9)
    num_item(s, 11.3, 2, '0.2 and 0.8 mapping range',
             [('too wide and the arm can be driven to either limit by accident', None)], h=1.9)
    num_item(s, 13.2, 3, '0.08 pinch distance',
             [('too tight and the gripper will not close on a real object', None)], h=1.9)
    num_item(s, 15.1, 4, '0.15 command interval',
             [('too tight and the arm stutters or stops responding entirely', None)], h=1.9)
    note(s, 17.4, [
        [('Every one of them is a trade, not a setting to maximise. A threshold '
          'is a decision about which mistake you would rather make — different '
          'for a gripper that must not drop something and a display that must '
          'not flicker.', None)],
    ], h=2.6)

    # ================================================ 43. EXTENSION DIVIDER ===
    s = add(0, master=1)
    _, tf = textbox(s, X_L, 15.41, W_WIDE, 4.28, anchor=3)
    para(tf, True, 'Challenge', F_TITLE, SZ_DIVIDER, YELLOW, line_spacing=1.0)
    para(tf, False, 'YOUR MOVE', F_TITLE, SZ_DIVIDER, WHITE, line_spacing=1.0)

    # ==================================================== 44. THE BRIEF ===
    s = add(0, master=1)
    s.shapes.add_picture(art['image2.png'], Cm(17.39), Cm(3.81), Cm(9.36), Cm(9.54))
    title(s, [('The Brief', None)], ext=True)
    body(s, Y_BODY_EXT, [
        [('Make the arm copy your hand.', None)],
        [('Move your hand and the arm follows. Pinch and the gripper closes. '
          'Keep it smooth, keep it safe, and keep it inside the workspace.', None)],
        [('Every decision is already made for you in the constants at the top of '
          'the file. Your job is not to choose safety — it is to understand why it '
          'was chosen, well enough to explain it.', None)],
    ], ext=True)
    check_item(s, 13.2, [
        ('The arm tracks a single hand, in two axes, at a fixed height.', None),
    ], h=1.8)
    check_item(s, 15.0, [
        ('The gripper responds to a pinch, and nothing else.', None),
    ], h=1.8)
    check_item(s, 16.8, [
        ('The arm never leaves the workspace, whatever your hand does.', None),
    ], h=1.8)
    check_item(s, 18.6, [
        ('The servos are released when you stop.', None),
    ], h=1.4)

    # ===================================================== 45. THE MISSION ===
    s = add()
    title(s, [('YOUR MISSION: ', None), ('SMOOTH OR IT DOES NOT COUNT', None)])
    body(s, Y_BODY_STD, [
        [('A control loop is judged on how it behaves while nothing is wrong. Get '
          'these four and the project is finished:', None)],
    ])
    num_item(s, 8.8, 1, 'Move your hand left. The arm moves left.',
             [('Not right. If it is inverted, fix the map, not the flip.', None)], h=2.1)
    num_item(s, 10.9, 2, 'Raise your hand. The arm reaches forward.',
             [('X_MAX and X_MIN in that order, on purpose.', None)], h=2.1)
    num_item(s, 13.0, 3, 'Pinch. The gripper closes. Open. It releases.',
             [('Green circle to red circle, no drift in between.', None)], h=2.1)
    num_item(s, 15.1, 4, 'Move fast. The arm does not stutter.',
             [('If it judders, COMMAND_INTERVAL is too small.', None)], h=2.1)
    callout(s, 17.6, [
        ('Take your hand out of frame. The arm must stay exactly where it was and '
         'say nothing new. If it keeps moving, ', None),
        ('you have given it an instruction during a frame with no hand in it.', 'c'),
    ], h=1.9)

    # ===================================================== 46. DATA LOG ===
    s = add()
    title(s, [('YOUR DATA LOG', None)])
    body(s, 4.0, [
        [('Fill this in before you change any threshold. Every row should be a '
          'measurement, not a guess.', None)],
    ])
    table(s, 6.0, [
        ['Where your hand is', 'X commanded', 'Y commanded', 'Gripper', 'Did it feel right?'],
        ['Low and centred', '______', '______', '______', '________________'],
        ['Middle and centred', '______', '______', '______', '________________'],
        ['High and centred', '______', '______', '______', '________________'],
        ['Middle and far left', '______', '______', '______', '________________'],
        ['Middle and far right', '______', '______', '______', '________________'],
        ['Pinched, hand still', '______', '______', '______', '________________'],
        ['Hand leaves the frame', '______', '______', '______', '________________'],
    ], [6.0, 3.5, 3.5, 3.0, 8.13], row_h=1.15, head_h=1.35, size=12.0)
    callout(s, 16.4, [
        ('That last row is the one to get right. Write what the arm actually did, '
         'not what you hoped it did. If the X and Y cells in that row contain new '
         'numbers, ', None),
        ('your program is still instructing the arm with no hand in view.', 'c'),
    ], h=2.2)

    # ============================================= 47. DEFINITION OF DONE ===
    s = add()
    title(s, [('DEFINITION OF DONE', None)])
    body(s, 4.2, [
        [('Tick every line. A project is not finished because the window opens.', None)],
    ])
    check_item(s, 7.0, [
        ('All 14 TODOs filled in, with the comments copied as written.', None),
    ], h=2.0)
    check_item(s, 9.0, [
        ('Every threshold in the file explained in one sentence each.', None),
    ], h=2.0)
    check_item(s, 11.0, [
        ('Data log complete for all seven rows.', None),
    ], h=2.0)
    check_item(s, 13.0, [
        ('Hand leaves frame three times: arm holds position, every time.', None),
    ], h=2.0)
    check_item(s, 15.0, [
        ('q exits cleanly, window closes, servos released, arm moves by hand.', None),
    ], h=2.0)
    check_item(s, 17.0, [
        ('One person’s hand at a time. No exceptions during testing.', None),
    ], h=2.0)
    note(s, 18.3, [
        [('The second line is the one that separates someone who ran this once from '
          'someone who understands it. The first four are only finished when you '
          'can say what each number is for without looking.', None)],
    ], h=1.6)

    # ==================================================== 48. GO FURTHER ===
    s = add()
    title(s, [('GO FURTHER', None)])
    body(s, Y_BODY_STD, [
        [('Each of these is a small change to code you have already written.', None)],
    ])
    bullet(s, 7.6, [
        ('Smooth it.', 'b'), ('  Average the last few index_tip values before '
          'mapping them, and watch the arm stop trembling. A short list and a '
          'sum() will do it.', None),
    ], h=2.3)
    bullet(s, 9.9, [
        ('Two hands.', 'b'), ('  Raise max_num_hands and average both index '
          'tips. Now decide what should happen when they disagree.', None),
    ], h=2.3)
    bullet(s, 12.2, [
        ('Fingers instead of pinch.', 'b'), ('  Count how many fingertips sit '
          'above the wrist and use that as the gripper command. You already have '
          'all 21 landmarks.', None),
    ], h=2.3)
    bullet(s, 14.5, [
        ('Record and replay.', 'b'), ('  Log the X and Y values to a file, then '
          'drive the arm from the file instead of from the camera.', None),
    ], h=2.3)
    bullet(s, 16.8, [
        ('Make it stop safely.', 'b'), ('  Have the program return the arm to a '
          'home position when it loses the hand, rather than holding still '
          'forever.', None),
    ], h=2.3)
    note(s, 18.6, [
        [('The first one is the most valuable and the least dramatic. Most of the '
          'work is deciding how much of the noise to believe.', None)],
    ], h=1.6)

    # ================================================== 49. DEBRIEF ===
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
# -*- coding: utf-8 -*-
"""Build Slides/M2/myCobot_06.pptx -- 'Rock, Paper, Robot' (M2-P6).

Rebuilds the deck from the theme/layouts of the reference sample
Slides/myCobot_08.pptx, but teaches the MediaPipe hand-gesture rock-paper-scissors
game that students complete in M2/M2-P6-Starter.py.

Ordering rule: concepts first, then all twenty steps, and only then the
correction section. Nothing in the concept section refers to a line number,
so the mechanisms can be taught without spoiling which code turns out to
need them.

Every code snippet is copied verbatim from M2/M2-P6-Base.py, except the two
shell commands, the sample terminal output, the "before" listings in the
correction section (which are the earlier, faulty versions and are labelled
as such), and the worksheet blanks.
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
OUT = os.path.join(HERE, 'Slides', 'M2', 'myCobot_06.pptx')
TMP = os.path.join(HERE, 'tmp_media')

STARTER = 'M2-P6-Starter.py'
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
    para(tf, True, 'Project 6', F_TITLE, SZ_DIVIDER, YELLOW, line_spacing=1.0)
    para(tf, False, 'Rock, Paper, Robot', F_TITLE, SZ_DIVIDER, WHITE, line_spacing=1.0)

    # ================================================== 3. WHAT THIS BUILDS ===
    s = add()
    title(s, [('What this project builds', None)])
    body(s, Y_BODY_STD, [
        [('Show the camera a closed fist, a flat hand, or two fingers. The program '
          'reads the gesture, picks a move of its own, moves the arm to show it, and '
          'keeps score.', None)],
        [('Three systems have to agree for that to happen:', None)],
    ])
    bullet(s, 8.6, [
        ('A hand tracker', 'b'), (' that turns a picture of your hand into a number.', None),
    ], h=1.7)
    bullet(s, 10.3, [
        ('A set of rules', 'b'), (' that decides who won the round.', None),
    ], h=1.7)
    bullet(s, 12.0, [
        ('An arm', 'b'), (' that physically performs the robot gesture.', None),
    ], h=1.7)
    callout(s, 14.4, [
        ('This is the first project where the arm is not decoration. If it does not '
         'move, the project is not finished.', None),
    ], h=2.0)
    note(s, 16.9, [
        [('Project 5 was careful to keep the robot optional. This one is the opposite '
          'on purpose — but "the arm is essential" and "the program dies without the '
          'arm" are two different claims, and this project is about the gap between '
          'them.', None)],
    ], h=2.8)

    # ================================================== 4. THREE SYSTEMS ===
    s = add()
    title(s, [('Three systems, one loop', None)])
    body(s, Y_BODY_STD, [
        [('The main loop is short enough to hold in your head, and it does the same '
          'five things forever:', None)],
    ])
    num_item(s, 7.0, 1, 'Get a frame',
             [('From a background thread, not straight off the camera.', None)], h=1.9)
    num_item(s, 8.9, 2, 'Find the hand',
             [('MediaPipe returns landmarks, not an image of a hand.', None)], h=1.9)
    num_item(s, 10.8, 3, 'Count and decide',
             [('Fingers to a gesture, both gestures to a winner.', None)], h=1.9)
    num_item(s, 12.7, 4, 'Move the arm',
             [('Four and a half seconds of sleeping, in the middle of the loop.', None)], h=1.9)
    num_item(s, 14.6, 5, 'Draw and show',
             [('The picture you actually look at.', None)], h=1.9)
    note(s, 17.0, [
        [('Step 4 is the one that surprises people. A blocking call in the middle of '
          'a real-time loop does not make the loop slower — it stops it completely. '
          'Everything in this project that feels wrong at first is downstream of '
          'those four and a half seconds.', None)],
    ], h=2.6)

    # =========================================== 5. A ROBOT THAT CAN BE ABSENT ===
    s = add()
    title(s, [('A robot that can be absent', None)])
    body(s, Y_BODY_STD, [
        [('The arm is essential to this project, but it is not essential to the '
          'program running. Those are different requirements, and the file is built '
          'to satisfy both.', None)],
    ])
    code(s, 7.4, [
        '# The robot handle. None means "no arm", and every use of it below is',
        '# guarded, so the gesture game still runs on a machine with no robot.',
        'mc = None',
        '',
        '# Home pose. Used at startup and again at the end of every round, so it',
        '# lives at module level rather than inside the try block below.',
        'home_pos = [0, 0, 0, 0, 0, 0]',
    ], size=12.0)
    body(s, 12.4, [
        [('Two decisions in six lines. The handle starts as ', None), ('None', 'c'),
         (' so it always exists, whatever the hardware does. And the home pose moves '
          'out of the ', None), ('try', 'c'),
         (' block, because two functions need it and only one of them runs inside '
          'that block.', None)],
    ])
    note(s, 15.4, [
        [('Anything created inside a ', None), ('try', 'c'),
         (' block may not exist when you reach the handler. Hoisting a shared '
          'constant out is the quiet fix that prevents a whole family of late, '
          'confusing crashes.', None)],
    ], h=2.6)

    # ============================================ 6. WHAT MEDIAPIPE HANDS YOU ===
    s = add()
    title(s, [('What MediaPipe hands you', None)])
    body(s, Y_BODY_STD, [
        [('Project 5 asked OpenCV for a colour. This project asks MediaPipe for a '
          'hand, and it gets back a list of 21 numbered points — one per finger '
          'joint, plus a wrist.', None)],
        [('The points come in a fixed order, every time, for every hand:', None)],
    ])
    code(s, 8.6, [
        '    tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips',
        '    pips = [3, 6, 10, 14, 18]  # Corresponding PIP joints',
    ], size=13.5)
    body(s, 11.8, [
        [('Two parallel lists. The thumb is 4, the index finger is 8, the middle is '
          '12, and so on. Because the order never changes, you can count fingers by '
          'comparing numbers in a list instead of reasoning about a picture.', None)],
    ])
    callout(s, 15.4, [
        ('This is the whole reason to use a tracker. A shape recogniser gives you a '
         'label; a hand tracker gives you coordinates you can ask your own questions '
         'of.', None),
    ], h=2.4)

    # ========================================= 7. FRACTIONS, NOT PIXELS ===
    s = add()
    title(s, [('Fractions, not pixels', None)])
    body(s, Y_BODY_STD, [
        [('Every landmark has ', None), ('.x', 'c'), (' and ', None), ('.y', 'c'),
         (' values, and they are not pixel coordinates. They are normalised: 0.0 is '
          'the left or top edge of the frame, 1.0 is the right or bottom edge.', None)],
        [('That single decision removes a whole class of bugs. The code below never '
          'converts to pixels, and it does not need to:', None)],
    ])
    code(s, 9.4, [
        '    if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[pips[0]].x:',
        '        extended += 1',
    ], size=12.0)
    note(s, 12.6, [
        [('Because the values scale with the frame, the same comparison works at '
          '640x480 and at 1280x720, and it still works if the hand moves toward the '
          'far side of the picture. Only the ordering is being tested — is this '
          'number smaller than that one — and ordering does not care about units.',
          None)],
    ], h=3.0)

    # ============================================ 8. WHY THE THUMB IS DIFFERENT ===
    s = add()
    title(s, [('Why the thumb is different', None)])
    body(s, Y_BODY_STD, [
        [('The thumb sticks out sideways. Comparing its tip to its joint on the ', None),
         ('y', 'c'), (' axis tells you almost nothing — a raised thumb and a thumb '
          'folded across the palm can sit at the same height. So the thumb gets its '
          'own test, on ', None), ('x', 'c'), (':', None)],
    ])
    code(s, 8.6, [
        '    # Thumb: compare x-coordinates (horizontal)',
        '    if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[pips[0]].x:',
        '        extended += 1',
    ], size=12.0)
    body(s, 11.8, [
        [('The other four fingers all point the same way, so one loop covers them:', None)],
    ])
    code(s, 13.6, [
        '    # Other 4 fingers: compare y-coordinates (vertical, tip above pip = extended)',
        '    for i in range(1, 5):',
        '        if hand_landmarks.landmark[tips[i]].y < hand_landmarks.landmark[pips[i]].y:',
        '            extended += 1',
    ], size=10.5)
    callout(s, 17.0, [
        ('Note the loop starts at ', None), ('1', 'c'), (', not 0. The thumb was '
         'already counted by hand, so index 0 is skipped. An off-by-one here is the '
         'classic bug in this function, and it shows up as a hand that always reports '
         'one finger too many.', None),
    ], h=2.4)

    # ============================================== 9. COUNT TO GESTURE ===
    s = add()
    title(s, [('Count, then gesture', None)])
    body(s, Y_BODY_STD, [
        [('Counting is done. Turning a count into a name is four branches and no '
          'cleverness at all:', None)],
    ])
    code(s, 6.8, [
        '    if finger_count == 0:',
        '        return "Rock"',
        '    elif finger_count == 5:',
        '        return "Paper"',
        '    elif finger_count == 2:',
        '        return "Scissors"',
        '    else:',
        '        return "Unknown"',
    ], size=13.0)
    body(s, 12.4, [
        [('Three numbers are meaningful and everything else is refused. That last '
          'branch is not laziness — it is what lets the main loop wait for a proper '
          'gesture instead of guessing.', None)],
    ])
    callout(s, 15.0, [
        ('Returning the string ', None), ('"Unknown"', 'c'), (' rather than a number '
         'or ', None), ('None', 'c'), (' is a good habit. Later code can test it '
         'against the list of real gestures with one ', None), ('in', 'c'),
         (' check and never has to guess what an unusual value meant.', None),
    ], h=2.6)

    # ====================================== 10. THE LIMIT OF COUNTING ===
    s = add()
    title(s, [('The limit of counting', None)])
    body(s, Y_BODY_STD, [
        [('Two fingers means Scissors. But which two?', None)],
    ])
    code(s, 6.4, [
        '    # 2 fingers (index + middle) = Scissors',
    ], size=14.0)
    body(s, 8.4, [
        [('The comment claims index and middle. The code cannot tell. A peace sign '
          'and a finger-gun both report a count of two, and both are classified as '
          'Scissors.', None)],
    ])
    bullet(s, 11.4, [
        ('Counting throws away identity', 'b'), ('  — it answers how many, never '
         'which.', None),
    ], h=1.9)
    bullet(s, 13.3, [
        ('The landmarks still know', 'b'), ('  — the tips list has a name for every '
         'finger, and nothing stops you testing each one individually.', None),
    ], h=1.9)
    note(s, 16.0, [
        [('Knowing what a limitation costs you is the difference between a program '
          'that works and one you understand. If identity mattered — say the robot '
          'had to point at a specific finger — you would compare ', None),
         ('landmark[8]', 'c'), (' against ', None), ('landmark[12]', 'c'),
         (' directly instead of counting.', None)],
    ], h=2.8)

    # ==================================== 11. WHY A PLAIN CAMERA FEELS LAGGY ===
    s = add()
    title(s, [('Why a plain camera feels laggy', None)])
    body(s, Y_BODY_STD, [
        [('Every project so far opened the camera and read it once per loop. That '
          'works fine. This project is different, because it adds ', None),
         ('blocking', 'b'), (' work to the loop — and that turns a small problem '
          'into an obvious one.', None)],
    ])
    callout(s, 9.0, [
        ('A camera does not deliver the frame you just asked for. It delivers the '
          'newest frame it has, and it keeps capturing while your code is busy. '
          'Those two facts are the whole problem.', None),
    ], h=2.8)
    body(s, 12.4, [
        [('When your loop is fast, you read roughly the newest frame and nothing '
          'builds up. When your loop stalls for four seconds doing arm movements, '
          'the camera fills a buffer with four seconds of pictures. The next read '
          'hands you the oldest of them, not the newest.', None)],
    ])
    note(s, 16.0, [
        [('So the lag you see is not the robot. It is the queue. The fix is not to '
          'make the loop faster — the loop has a genuine four and a half seconds of '
          'work in it — it is to stop the queue from ever building.', None)],
    ], h=2.6)

    # ==================================== 12. THE FIX: NO QUEUE ===
    s = add()
    title(s, [('The fix: never let a queue form', None)])
    body(s, Y_BODY_STD, [
        [('There are two ways to stop the queue building. One is to ask the driver '
          'for a smaller buffer. The class tries that first:', None)],
    ])
    code(s, 7.2, [
        'class ThreadedCamera:',
        '    """Asynchronous camera reader thread to eliminate V4L2 frame buffer latency."""',
        '    def __init__(self, src=0):',
        '        self.cap = cv2.VideoCapture(src, cv2.CAP_V4L2)',
        '        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)',
        '        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)',
        '        # Reduce buffer size to minimize latency',
        '        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)',
    ], size=12.5)
    body(s, 11.6, [
        [('Look closely at that last line. It is passed a sensible value, it does '
          'not raise an error, and on many V4L2 setups it does nothing at all. '
          'Setting a property is not the same as the property taking effect.', None)],
    ])
    callout(s, 14.6, [
        ('Never trust a silent success. This one is worth remembering because it '
         'looks like it worked, and the lag it was supposed to remove is still '
         'there.', None),
    ], h=2.2)
    note(s, 17.2, [
        [('The line is not wasted — it helps on backends that do honour it, and it '
          'documents the intent. But the real fix is the next slide.', None)],
    ], h=1.8)

    # ==================================== 13. A THREAD AND A LOCK ===
    s = add()
    title(s, [('A thread, a lock, and a copy', None)])
    body(s, Y_BODY_STD, [
        [('So the class pulls frames continuously on its own thread and hands over '
          'only the latest one. Three pieces make that safe:', None)],
    ])
    code(s, 8.0, [
        '        self.lock = threading.Lock()',
        '        self.running = True',
        '        self.ret, self.frame = self.cap.read()',
        '',
        '        # Start background thread to continually pull frames from the V4L2 buffer',
        '        self.thread = threading.Thread(target=self._update, daemon=True)',
        '        self.thread.start()',
    ], size=11.5)
    body(s, 13.4, [
        [('The thread runs forever in the background. The main loop never waits for '
          'the camera; it just takes whatever the most recent frame happens to be. '
          'The queue still exists, but it is now exactly one frame deep.', None)],
    ])
    callout(s, 15.9, [
        ('The lock is not optional. Without it, the main loop could be halfway '
         'through drawing on a frame while the thread replaced it underneath.',
         None),
    ], h=2.2)

    # ==================================== 14. THE THREAD BODY ===
    s = add()
    title(s, [('The thread body', None)])
    body(s, Y_BODY_STD, [
        [('One method does all the reading, and it is short:', None)],
    ])
    code(s, 6.4, [
        '    def _update(self):',
        '        while self.running:',
        '            if self.cap.isOpened():',
        '                ret, frame = self.cap.read()',
        '                if ret and frame is not None:',
        '                    with self.lock:',
        '                        self.ret = ret',
        '                        self.frame = frame',
        '            time.sleep(0.005)  # Prevents high CPU usage on dedicated thread execution',
    ], size=11.5)
    note(s, 13.2, [
        [('Three details worth naming. The ', None), ('self.running', 'c'),
         (' flag is the only way this loop ever stops. The ', None), ('with', 'c'),
         (' block is what makes the assignment atomic. And the five-millisecond '
          'sleep stops the thread from spinning on a camera that cannot keep up — '
          'without it this is a busy loop that will heat the Pi.', None)],
    ], h=3.0)

    # ==================================== 15. WHY read() COPIES ===
    s = add()
    title(s, [('Why read() hands back a copy', None)])
    body(s, Y_BODY_STD, [
        [('Here is the method the main loop calls. The last line is the important '
          'one:', None)],
    ])
    code(s, 6.8, [
        '    def read(self):',
        '        with self.lock:',
        '            if self.frame is None:',
        '                return False, None',
        '            return self.ret, self.frame.copy()',
    ], size=13.5)
    body(s, 11.2, [
        [('Your drawing code mutates the frame it is given. ', None),
         ('cv2.putText', 'c'), (', ', None), ('cv2.rectangle', 'c'),
         (' and ', None), ('cv2.flip', 'c'),
         (' all write straight into the image. If this returned the shared frame '
          'itself, every rectangle and every letter would be scribbled onto the '
          'frame the next detection pass is about to analyse.', None)],
    ])
    callout(s, 15.2, [
        ('The copy is what makes the shared frame safe. It costs a few milliseconds '
         'and it buys you a picture that is yours to draw on.', None),
    ], h=2.2)

    # ==================================== 16. SHUTTING THE THREAD DOWN ===
    s = add()
    title(s, [('Shutting the thread down', None)])
    body(s, Y_BODY_STD, [
        [('A background thread that is never stopped will keep the program alive. '
          'This is the shutdown, and it happens in the right order:', None)],
    ])
    code(s, 7.4, [
        '    def release(self):',
        '        self.running = False',
        '        if self.thread.is_alive():',
        '            self.thread.join(timeout=0.5)',
        '        if self.cap.isOpened():',
        '            self.cap.release()',
    ], size=13.0)
    body(s, 12.4, [
        [('Flag first, then join, then release the camera. The join has a timeout, '
          'so even if the thread is stuck inside a blocking read the program still '
          'shuts down instead of hanging.', None)],
    ])
    note(s, 15.2, [
        [('The daemon flag on the constructor is the safety net, not the plan. It '
          'means that even if ', None), ('release()', 'c'), (' is never called, '
          'Python will still exit. Relying on that alone is how you end up with a '
          'camera that stays locked after a crash.', None)],
    ], h=2.8)

    # ==================================== 17. WIN LOGIC AS A LOOKUP ===
    s = add()
    title(s, [('Win logic as a lookup table', None)])
    body(s, Y_BODY_STD, [
        [('Rock paper scissors is a bad fit for ', None), ('if', 'c'), (' chains. '
          'There are nine combinations and only six of them are wins, which is the '
          'wrong shape for branching. The program uses a dictionary instead:', None)],
    ])
    code(s, 8.6, [
        'WIN_MAP = {',
        '    (0, 2): "PLAYER", (2, 0): "ROBOT",  # Rock > Scissors',
        '    (1, 0): "PLAYER", (0, 1): "ROBOT",  # Paper > Rock',
        '    (2, 1): "PLAYER", (1, 2): "ROBOT",  # Scissors > Paper',
        '}',
    ], size=13.0)
    body(s, 12.8, [
        [('Each key is the pair of gesture indices, player first. Each value is who '
          'won. Two entries per line, six lines of behaviour total. Adding a fourth '
          'gesture would mean adding rows, not new branches.', None)],
    ])
    note(s, 15.6, [
        [('The ', None), ('.get()', 'c'), (' call with a default of ', None),
         ('"DRAW"', 'c'), (' means an unknown pair can never raise a ', None),
         ('KeyError', 'c'), (' and crash the game mid-round. In this program the '
          'draw case is already handled earlier, so the default is genuinely '
          'unreachable — but it is the right defensive choice.', None)],
    ], h=2.8)

    # ==================================== 18. FOUR AND A HALF SECONDS ===
    s = add()
    title(s, [('Four and a half seconds of sleep', None)])
    body(s, Y_BODY_STD, [
        [('Every round ends with the robot physically performing its gesture. Add '
          'up the sleeps in that function:', None)],
    ])
    code(s, 7.4, [
        '    mc.send_coords(pose, ARM_SPEED, 1)',
        '    time.sleep(1.5)',
        '    # Set gripper',
        '    mc.set_gripper_state(grip, 80)',
        '    time.sleep(0.5)',
        '    ...',
        '    time.sleep(1.0)',
        '    ...',
        '    mc.send_angles(home_pos, ARM_SPEED)',
        '    time.sleep(1.5)',
    ], size=13.0)
    body(s, 13.6, [
        [('Four and a half seconds, all of it inside the main loop. Nothing is '
          'drawn during that time, so the window shows the same frozen frame '
          'until the arm is home.', None)],
    ])
    callout(s, 16.4, [
        ('The threaded camera keeps working throughout, so when the loop wakes up it '
         'gets a genuinely fresh frame. The picture is current. It just arrives more '
         'than five seconds late.', None),
    ], h=2.2)

    # ==================================== 19. TWO CLOCKS ===
    s = add()
    title(s, [('Two clocks, and why it matters', None)])
    body(s, Y_BODY_STD, [
        [('This program reads the time in two different ways, and the difference '
          'between them is the difference between a working feature and a dead one.',
          None)],
    ])
    bullet(s, 7.8, [
        ('Once per frame', 'b'), ('  — the loop captures a timestamp near the top of '
         'each iteration, and everything later in that iteration reuses it.', None),
    ], h=2.3)
    bullet(s, 10.1, [
        ('At the moment you need it', 'b'), ('  — a fresh ', None), ('time.time()', 'c'),
         (' read at the point of use.', None),
    ], h=2.3)
    body(s, 12.9, [
        [('The first is cheaper and slightly stale — fine for measuring how long '
          'you have held a gesture, since being a frame late changes nothing. The '
          'second is correct whenever something slow happened in between:', None)],
    ])
    code(s, 16.3, [
        '                cooldown_ready = (time.time() - last_game_time) > GAME_COOLDOWN',
    ], size=11.0)
    callout(s, 18.2, [
        ('Had that line used the frame timestamp, the elapsed time would have '
         'measured from before the arm delay — and cooldowns are where stale '
         'clocks go wrong.', None),
    ], h=2.4)

    # ==================================== 20. DRAWING AT A FIXED POSITION ===
    s = add()
    title(s, [('Drawing text at a fixed position', None)])
    body(s, Y_BODY_STD, [
        [('Almost everything on this screen is ', None), ('cv2.putText', 'c'),
         ('. The one technique worth noticing is that the position never moves while '
          'the content does:', None)],
    ])
    code(s, 7.8, [
        '    if player_gesture != "Unknown":',
        '        cv2.putText(frame, f"Your Move: {player_gesture}", (20, 130),',
        '                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)',
        '    else:',
        '        cv2.putText(frame, f"Fingers: {finger_count} - Make a clear gesture!", (20, 130),',
        '                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)',
    ], size=11.0)
    note(s, 12.8, [
        [('Both branches draw at y = 130, so whichever one runs, the text lands in '
          'the same place. That is the trick for a line of text whose content '
          'changes: hold the position constant and swap the words. The two branches '
          'even use different sizes and colours, which is why the fallback line is '
          'readable at a glance while the confirmation line is easy to miss.', None)],
    ], h=3.0)
    callout(s, 16.2, [
        ('The fingers count only appears while the gesture is unrecognised, which '
         'makes it a genuinely useful debugging aid. It shows you the raw input '
         'exactly when the interpretation is failing.', None),
    ], h=2.4)

    # ==================================== 21. CLAIMS AND EVIDENCE ===
    s = add()
    title(s, [('Claims and evidence', None)])
    body(s, Y_BODY_STD, [
        [('One habit runs through this whole project, and it is worth stating before '
          'you write any code.', None)],
    ])
    callout(s, 7.2, [
        ('Every message your program prints is a claim about how it behaves. The '
         'comment in your code is a claim about why. Both are untested until you '
         'check them.', None),
    ], h=2.4)
    body(s, 10.0, [
        [('This project makes four claims about how it behaves — three of them '
          'printed on startup, one of them implied by the interface. None of them '
          'can be checked by watching the program start, because the program starts '
          'perfectly well whether they are true or not.', None)],
    ])
    note(s, 13.0, [
        [('So the check has to be deliberate: read each claim, then write down what '
          'you would expect to see if it were true, then run it. If the two differ, '
          'you have found something. Most people never do this, because a program '
          'that starts up and does not crash feels like a program that works.',
          None)],
    ], h=3.0)
    callout(s, 16.4, [
        ('After the twenty steps we come back to those four claims and look at what '
         'this project actually did. All four were wrong.', None),
    ], h=2.2)

    # ==================================== 22. BEFORE YOU TYPE ANYTHING ===
    s = add()
    title(s, [('Before you type anything', None)])
    body(s, Y_BODY_STD, [
        [('Copy the starter file across and run it, exactly as it arrived:', None)],
    ])
    command(s, 6.6, SCP)
    command(s, 8.4, RUN)
    body(s, 10.4, [
        [('This is the real output of the starter file with every ', None),
         ('TODO', 'c'), (' still empty:', None)],
    ])
    code(s, 12.0, [
        'Robot ready.',
        'Starting Rock-Paper-Scissors!',
        'Gestures: Fist=Rock, Open Hand=Paper, Peace Sign=Scissors',
        'Hold gesture steady for 1 second to play.',
        'Traceback (most recent call last):',
        '  File "M2-P6-Starter.py", line 208, in <module>',
        '    while cap.isOpened():',
        'NameError: name \'cap\' is not defined',
    ], size=12.5)
    note(s, 16.6, [
        [('Every ', None), ('TODO', 'c'), (' marker you leave empty is a gap. '
          'The file still parses, starts, and prints its banner — then dies at '
          'the first line that needs something unwritten.', None)],
    ], h=3.0)

    # ==================================== 23. STEP 1 ===
    s = add()
    title(s, [('Step 1', None), ('  —  ', None), ('import the tools', 'y')])
    body(s, Y_BODY_STD, [
        [('Six imports. Four of them you have used in every project so far:', None)],
    ])
    code(s, 6.6, [
        'import cv2',
        'import mediapipe as mp',
        'import numpy as np',
        'import time',
        'import random',
        'import threading',
    ], size=14.0)
    body(s, 10.6, [
        [('Two of these are doing new work. ', None), ('random', 'c'),
         (' is what lets the robot pick a move, and ', None), ('threading', 'c'),
         (' is the whole answer to the lag problem. ', None), ('numpy', 'c'),
         (' comes along for the ride because MediaPipe hands back arrays.', None)],
    ])
    note(s, 13.8, [
        [('Notice what is ', None), ('not', 'b'), (' imported. The ', None),
         ('MyCobot280', 'c'), (' class does not come from any of these — it comes '
          'from a library, and it gets its own line in the next step.', None)],
    ], h=2.6)

    # ==================================== 24. STEP 2 ===
    s = add()
    title(s, [('Step 2', None), ('  —  ', None), ('import the arm', 'y')])
    body(s, Y_BODY_STD, [
        [('One import, on its own, because it is not part of the standard set of '
          'tools:', None)],
    ])
    code(s, 6.6, [
        'from pymycobot.mycobot280 import MyCobot280',
    ], size=15.0)
    body(s, 9.2, [
        [('Read that as: from the ', None), ('pymycobot.mycobot280', 'c'),
         (' module, take the ', None), ('MyCobot280', 'c'), (' class. The package '
          'lives on the Raspberry Pi, not in this file — which is why the import '
          'line has to be typed exactly as written.', None)],
    ])
    callout(s, 13.0, [
        ('A mistyped import fails immediately, at the top of the file, before a '
         'single line of your own logic has run. That is a gift: the error message '
         'tells you the module is missing rather than leaving you to work out why '
         'the program stopped.', None),
    ], h=2.8)
    note(s, 16.4, [
        [('It will also fail if you try to run this file on a laptop that has never '
          'seen the robot libraries installed. For this project the code has to be '
          'run on the Pi.', None)],
    ], h=1.8)

    # ==================================== 25. STEP 3 ===
    s = add()
    title(s, [('Step 3', None), ('  —  ', None), ('connect and power on', 'y')])
    body(s, Y_BODY_STD, [
        [('Five lines inside the ', None), ('try', 'c'),
         (' block that already exists. Two device paths, two short waits, and a '
          'confirmation line:', None)],
    ])
    code(s, 7.0, [
        '    print("Connecting to myCobot280...")',
        '',
        '    mc = MyCobot280(\'/dev/ttyAMA0\', 1000000)',
        '    time.sleep(0.5)',
        '    mc.power_on()',
        '    time.sleep(0.5)',
    ], size=13.5)
    body(s, 12.4, [
        [('Read the constructor as two questions. Which serial port? ', None),
         ('/dev/ttyAMA0', 'c'), ('. At what baud rate? ', None), ('1000000', 'c'),
         ('. Both are wrong-looking numbers on purpose, and both must match the '
          'arm exactly.', None)],
    ])
    note(s, 15.6, [
        [('The two ', None), ('time.sleep(0.5)', 'c'), (' calls are not padding — '
          'they are giving the board time to finish booting and to acknowledge the '
          'power command. Send commands faster than it can accept them and the very '
          'first one is the one that gets lost.', None)],
    ], h=2.8)

    # ==================================== 26. STEP 4 ===
    s = add()
    title(s, [('Step 4', None), ('  —  ', None), ('go to the home pose', 'y')])
    body(s, Y_BODY_STD, [
        [('Two lines that tell the arm where to start and how long to settle there.',
          None)],
    ])
    code(s, 6.6, [
        '    mc.send_angles(home_pos, 50)',
        '    time.sleep(2.0)',
    ], size=15.0)
    body(s, 9.2, [
        [('The two-second sleep is the longest single wait in the whole file, and it '
          'is at startup, where nothing is waiting on you yet. There is no reason to '
          'rush it.', None)],
    ])
    callout(s, 12.4, [
        ('Where is home_pos defined? You did not type it in this step. It is the '
         'line given to you near the top of the file, before the try block, because '
         'the main loop needs it too and the loop is nowhere near this code.', None),
    ], h=2.8)
    note(s, 15.8, [
        [('The speed of ', None), ('50', 'c'), (' is deliberately slow. This is a '
          'starting position, not a demonstration — you want the arm to arrive '
          'without knocking anything over.', None)],
    ], h=2.2)

    # ==================================== 27. STEP 5 ===
    s = add()
    title(s, [('Step 5', None), ('  —  ', None), ('set up MediaPipe', 'y')])
    body(s, Y_BODY_STD, [
        [('This is the step that finally replaces colour detection with a hand '
          'tracker. Five lines of setup:', None)],
    ])
    code(s, 7.0, [
        'mp_hands = mp.solutions.hands',
        'mp_drawing = mp.solutions.drawing_utils',
        '',
        'hands = mp_hands.Hands(',
        '    static_image_mode=False,',
        '    max_num_hands=1,',
        '    min_detection_confidence=0.7,',
        '    min_tracking_confidence=0.7',
        ')',
    ], size=13.5)
    bullet(s, 13.4, [
        ('static_image_mode=False', 'c'), ('  — a live video feed, not a photo, so '
         'keep the previous frame as a hint.', None),
    ], h=1.9)
    bullet(s, 15.3, [
        ('max_num_hands=1', 'c'), ('  — one pair of hands, which is all this game '
         'needs and all the loop can track.', None),
    ], h=1.9)
    callout(s, 17.6, [
        ('Those last two confidence values are the only tuning knobs in the entire '
         'detection path. Raise them and the tracker gets faster but shakier; lower '
         'them and steadier but slower to notice a new hand.', None),
    ], h=2.2)

    # ==================================== 28. STEP 6 ===
    s = add()
    title(s, [('Step 6', None), ('  —  ', None), ('open the camera', 'y')])
    body(s, Y_BODY_STD, [
        [('One line, and it is not ', None), ('cv2.VideoCapture', 'c'), (':', None)],
    ])
    code(s, 6.6, [
        'cap = ThreadedCamera(0)',
    ], size=15.0)
    body(s, 9.2, [
        [('The class is already written for you, above the ', None), ('TODO', 'c'),
         (' markers. The ', None), ('0', 'c'), (' is the camera index — zero is the '
          'first one. Everything that made the class complicated is a response to '
          'the four and a half seconds of blocking work that comes later in the '
          'loop.', None)],
    ])
    callout(s, 13.4, [
        ('Every call in the main loop stays the same as the other projects. ', None),
        ('cap.read()', 'c'), (', ', None), ('cap.isOpened()', 'c'), (', ', None),
        ('cap.release()', 'c'),
        (' — the class was written to be a drop-in replacement for a normal capture '
         'object, so the loop code never has to know there is a thread in here.', None),
    ], h=2.8)

    # ==================================== 29. STEP 7A ===
    s = add()
    title(s, [('Step 7', None), ('  —  ', None), ('count fingers, part one', 'y')])
    body(s, Y_BODY_STD, [
        [('The function signature, the docstring, and the two lists of landmark '
          'indices that make this project possible:', None)],
    ])
    code(s, 7.2, [
        'def count_fingers(hand_landmarks):',
        '    """',
        '    Count extended fingers using MediaPipe landmarks.',
        '    Returns: number of extended fingers (0-5)',
        '    """',
        '    tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips',
        '    pips = [3, 6, 10, 14, 18]  # Corresponding PIP joints',
        '    ',
        '    extended = 0',
    ], size=13.0)
    note(s, 13.6, [
        [('Index 0 of each list is the thumb, so the two lists stay parallel — '
          'position 2 is the middle finger in both. That is the property the rest '
          'of the function depends on.', None)],
    ], h=2.6)

    # ==================================== 30. STEP 7B ===
    s = add()
    title(s, [('Step 7', None), ('  —  ', None), ('count fingers, part two', 'y')])
    body(s, Y_BODY_STD, [
        [('Two different comparisons, because there are two different kinds of '
          'finger:', None)],
    ])
    code(s, 7.0, [
        '    # Thumb: compare x-coordinates (horizontal)',
        '    if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[pips[0]].x:',
        '        extended += 1',
        '    ',
        '    # Other 4 fingers: compare y-coordinates (vertical, tip above pip = extended)',
        '    for i in range(1, 5):',
        '        if hand_landmarks.landmark[tips[i]].y < hand_landmarks.landmark[pips[i]].y:',
        '            extended += 1',
        '            ',
        '    return extended',
    ], size=11.5)
    callout(s, 14.0, [
        ('The thumb is handled first and outside the loop, then the loop starts at '
         '1. If it started at 0 the thumb would be counted a second time and every '
         'gesture in the game would be wrong by exactly one finger.', None),
    ], h=2.6)
    note(s, 17.0, [
        [('Smaller ', None), ('y', 'c'), (' means higher up in the frame, so a '
          'tip above its joint means the finger is pointing up. That single '
          'inequality is the whole test.', None)],
    ], h=1.8)

    # ==================================== 31. STEP 8 ===
    s = add()
    title(s, [('Step 8', None), ('  —  ', None), ('count to gesture', 'y')])
    body(s, Y_BODY_STD, [
        [('Four branches. The comments matter as much as the code, because they '
          'define what each pose is meant to be:', None)],
    ])
    code(s, 7.2, [
        'def classify_gesture(finger_count):',
        '    """',
        '    Classify gesture based on finger count.',
        '    Returns: "Rock", "Paper", "Scissors", or "Unknown"',
        '    """',
        '    # 0 fingers (fist) = Rock',
        '    # 5 fingers (open hand) = Paper  ',
        '    # 2 fingers (index + middle) = Scissors',
        '    # Anything else = Unknown',
        '    if finger_count == 0:',
        '        return "Rock"',
        '    elif finger_count == 5:',
        '        return "Paper"',
        '    elif finger_count == 2:',
        '        return "Scissors"',
        '    else:',
        '        return "Unknown"',
    ], size=10.5)
    callout(s, 16.6, [
        ('Three counts are accepted and the fourth case is refused on purpose. '
         'Returning ', None), ('"Unknown"', 'c'), (' is how the main loop knows to '
         'keep waiting instead of scoring a round nobody made.', None),
    ], h=2.4)

    # ==================================== 32. STEP 9 ===
    s = add()
    title(s, [('Step 9', None), ('  —  ', None), ('let the robot choose', 'y')])
    body(s, Y_BODY_STD, [
        [('This is the entire function:', None)],
    ])
    code(s, 6.4, [
        'def get_robot_move():',
        '    """',
        '    Robot randomly chooses Rock, Paper, or Scissors.',
        '    Returns: gesture string',
        '    """',
        '    return random.choice(GESTURES)',
    ], size=14.0)
    body(s, 11.4, [
        [('It picks from ', None), ('GESTURES', 'c'), (', the same list the main '
          'loop uses to test whether a gesture is valid, so the robot can never '
          'choose something the program does not understand.', None)],
    ])
    callout(s, 14.4, [
        ('No seeding. Every call draws a fresh move, so the robot is genuinely '
         'unpredictable — which is what makes the game worth replaying and what '
         'makes it worth fixing the cooldown.', None),
    ], h=2.4)

    # ==================================== 33. STEP 10 ===
    s = add()
    title(s, [('Step 10', None), ('  —  ', None), ('decide the winner', 'y')])
    body(s, Y_BODY_STD, [
        [('Handle the tie first, then translate both names to indices and ask the '
          'lookup table:', None)],
    ])
    code(s, 7.2, [
        'def determine_winner(player_move, robot_move):',
        '    """',
        '    Determine round winner.',
        '    Returns: "PLAYER", "ROBOT", or "DRAW"',
        '    """',
        '    if player_move == robot_move:',
        '        return "DRAW"',
        '    ',
        '    p_idx = GESTURE_IDX[player_move]',
        '    r_idx = GESTURE_IDX[robot_move]',
        '    ',
        '    return WIN_MAP.get((p_idx, r_idx), "DRAW")',
    ], size=12.5)
    note(s, 14.4, [
        [('The tie is pulled out first because the dictionary has no entry for it. '
          'Leaving that in the table would mean filling all three tie pairs with '
          '"DRAW" for no benefit — and the early return also means the dictionary '
          'only ever holds the six interesting cases.', None)],
    ], h=3.0)

    # ==================================== 34. STEP 11A ===
    s = add()
    title(s, [('Step 11', None), ('  —  ', None), ('the guard comes first', 'y')])
    body(s, Y_BODY_STD, [
        [('The most important three lines in the project, and they are not about '
          'gestures at all:', None)],
    ])
    code(s, 7.0, [
        'def execute_robot_gesture(gesture):',
        '    global last_robot_move',
        '    ',
        '    # Record the move first, so the on-screen label is right even when',
        '    # there is no arm to move.',
        '    last_robot_move = gesture',
        '    ',
        '    # No arm attached: the gesture is still recorded and scored, it just',
        '    # is not performed. This is what lets the game run without hardware.',
        '    if mc is None:',
        '        return',
    ], size=13.0)
    bullet(s, 14.4, [
        ('global', 'c'), ('  — this function assigns to a variable the loop owns, '
         'so Python needs to be told.', None),
    ], h=1.9)
    bullet(s, 16.3, [
        ('Record first', 'b'), (', guard second. Reversing those two lines makes the '
         'on-screen label blank exactly when hardware is missing.', None),
    ], h=1.9)

    # ==================================== 35. STEP 11B ===
    s = add()
    title(s, [('Step 11', None), ('  —  ', None), ('the movement', 'y')])
    body(s, Y_BODY_STD, [
        [('Everything past the guard runs only when there is an arm. Choose the '
          'pose, move, hold, and come home:', None)],
    ])
    code(s, 7.2, [
        '    if gesture == "Rock":',
        '        pose = POSE_ROCK',
        '        grip = GRIP_ROCK',
        '    elif gesture == "Paper":',
        '        pose = POSE_PAPER',
        '        grip = GRIP_PAPER',
        '    else:  # Scissors',
        '        pose = POSE_SCISSORS',
        '        grip = GRIP_SCISSORS',
        '    # Move to gesture pose',
        '    mc.send_coords(pose, ARM_SPEED, 1)',
        '    time.sleep(1.5)',
        '    # Set gripper',
        '    mc.set_gripper_state(grip, 80)',
        '    time.sleep(0.5)',
        '    # Hold pose briefly for player to see',
        '    time.sleep(1.0)',
        '    # Return to home',
        '    mc.send_angles(home_pos, ARM_SPEED)',
        '    time.sleep(1.5)',
    ], size=10.5)
    callout(s, 17.4, [
        ('The gripper is doing real work here: a closed gripper is a fist, an open '
         'one is a flat hand, and the two-finger pose is faked with the same open '
         'gripper. The arm is not pointing at a label, it is shaping a gesture.', None),
    ], h=2.2)

    # ==================================== 36. STEP 12A ===
    s = add()
    title(s, [('Step 12', None), ('  —  ', None), ('draw the UI, part one', 'y')])
    body(s, Y_BODY_STD, [
        [('This is the longest function in the file — ', None), ('draw_ui', 'c'),
         (' — and it is only ', None), ('cv2.putText', 'c'), (' calls on one frame. '
          'The signature takes the data in and draws it, and reads nothing global '
          'except the scores:', None)],
    ])
    code(s, 8.2, [
        'def draw_ui(frame, player_gesture, robot_gesture, result, finger_count):',
        '    """',
        '    Draw game UI on frame.',
        '    """',
        '    h, w = frame.shape[:2]',
        '    ',
        '    # Title',
        '    cv2.putText(frame, "Rock Paper Scissors!", (20, 40),',
        '                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)',
        '    ',
        '    # Score',
        '    score_text = f"Player: {player_score}  |  Robot: {robot_score}  |  Round: {rounds_played}"',
        '    cv2.putText(frame, score_text, (20, 80),',
        '                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)',
    ], size=10.5)
    note(s, 15.0, [
        [('Notice the asymmetry: the scores are read straight out of the enclosing '
          'scope without being passed in, while the result and the gestures arrive '
          'as parameters. That is inconsistent, and it is harmless, because '
          'assigning to a name like ', None), ('game_result', 'c'),
         (' inside this function would create a new local variable instead of '
          'updating the one the loop is about to read.', None)],
    ], h=3.2)

    # ==================================== 37. STEP 12B ===
    s = add()
    title(s, [('Step 12', None), ('  —  ', None), ('draw the UI, part two', 'y')])
    body(s, Y_BODY_STD, [
        [('The player line, the robot line, and the one piece of information that '
          'makes this project debuggable:', None)],
    ])
    code(s, 7.2, [
        '    # Player gesture detection',
        '    if player_gesture != "Unknown":',
        '        cv2.putText(frame, f"Your Move: {player_gesture}", (20, 130),',
        '                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)',
        '    else:',
        '        cv2.putText(frame, f"Fingers: {finger_count} - Make a clear gesture!", (20, 130),',
        '                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)',
        '    ',
        '    # Robot gesture',
        '    if robot_gesture:',
        '        cv2.putText(frame, f"Robot Move: {robot_gesture}", (20, 170),',
        '                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)',
    ], size=10.5)
    callout(s, 14.6, [
        ('That yellow fallback line is a debugging tool that ships in the final '
         'program. When the game refuses to score a round, this line tells you '
         'whether it read zero fingers or four.', None),
    ], h=2.4)

    # ==================================== 38. STEP 12C ===
    s = add()
    title(s, [('Step 12', None), ('  —  ', None), ('draw the UI, part three', 'y')])
    body(s, Y_BODY_STD, [
        [('The verdict. Four outcomes, four colours, one line of output:', None)],
    ])
    code(s, 7.0, [
        '    # Result',
        '    if result == "PLAYER":',
        '        color = (0, 255, 0)',
        '        text = "YOU WIN!"',
        '    elif result == "ROBOT":',
        '        color = (0, 0, 255)',
        '        text = "ROBOT WINS!"',
        '    elif result == "DRAW":',
        '        color = (255, 255, 0)',
        '        text = "DRAW!"',
        '    else:',
        '        color = (255, 255, 255)',
        '        text = game_result',
        '    ',
        '    cv2.putText(frame, text, (20, 230),',
        '                cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)',
    ], size=11.5)
    body(s, 14.4, [
        [('The fourth branch is the default prompt, and it reads ', None),
         ('game_result', 'c'), (' from the enclosing scope.', None)],
    ])
    callout(s, 17.2, [
        ('Whatever you do not recognise becomes the idle message.', None),
    ], h=1.8)

    # ==================================== 39. STEP 13 ===
    s = add()
    title(s, [('Step 13', None), ('  —  ', None), ('read a frame', 'y')])
    body(s, Y_BODY_STD, [
        [('At the top of the loop, five lines that are almost identical to previous '
          'projects:', None)],
    ])
    code(s, 6.8, [
        '        ret, frame = cap.read()',
        '        if not ret:',
        '            break',
        '        ',
        '        # Flip for mirror view',
        '        frame = cv2.flip(frame, 1)',
        '        h, w = frame.shape[:2]',
        '        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)',
        '        results = hands.process(rgb_frame)',
    ], size=12.5)
    bullet(s, 13.4, [
        ('cv2.flip(frame, 1)', 'c'), ('  — horizontal flip, so moving right moves '
         'right on screen.', None),
    ], h=1.9)
    bullet(s, 15.3, [
        ('cvtColor', 'c'), ('  — MediaPipe expects RGB, OpenCV hands back BGR, and '
         'the tracker quietly performs badly if you skip this.', None),
    ], h=1.9)
    callout(s, 17.6, [
        ('The ', None), ('break', 'c'), (' on a failed read is what stops this loop '
         'on a camera that has been unplugged mid-session, instead of spinning on '
         'None forever.', None),
    ], h=2.0)

    # ==================================== 40. STEP 14 ===
    s = add()
    title(s, [('Step 14', None), ('  —  ', None), ('draw the hand skeleton', 'y')])
    body(s, Y_BODY_STD, [
        [('Three lines of drawing, inside the hand loop, so the skeleton is '
          'overlaid on the picture you are about to analyse:', None)],
    ])
    code(s, 7.2, [
        '                mp_drawing.draw_landmarks(',
        '                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,',
        '                    mp_drawing.DrawingSpec(color=(0, 255, 0),',
        '                        thickness=2, circle_radius=2),',
        '                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)',
        '                )',
    ], size=11.5)
    body(s, 12.4, [
        [('Two ', None), ('DrawingSpec', 'c'), (' objects because MediaPipe draws '
          'the points and the bones separately, and they are styled independently. '
          'The connections themselves come from ', None), ('HAND_CONNECTIONS', 'c'),
         (' — the library already knows the bone layout, so you do not draw any of '
          'it by hand.', None)],
    ])
    note(s, 15.8, [
        [('Draw before you count, not after. The landmark positions do not change '
          'because you drew on the frame, but if you ever start cropping the frame '
          'for display you must do it after this block, or the coordinates will '
          'no longer line up with the picture.', None)],
    ], h=2.8)

    # ==================================== 41. STEP 15 ===
    s = add()
    title(s, [('Step 15', None), ('  —  ', None), ('count and classify', 'y')])
    body(s, Y_BODY_STD, [
        [('Two lines, and they are the only two in the whole loop that talk to the '
          'functions you wrote:', None)],
    ])
    code(s, 6.6, [
        '                finger_count = count_fingers(hand_landmarks)',
        '                player_gesture = classify_gesture(finger_count)',
    ], size=14.0)
    body(s, 9.2, [
        [('One counts, one names. Keeping them apart means you can test the second '
          'half of the project without a camera at all — call ', None),
         ('classify_gesture(2)', 'c'), (' directly and you get ', None),
         ('"Scissors"', 'c'), (', no hand required.', None)],
    ])
    callout(s, 12.6, [
        ('Note what is not here. Nothing checks that the count is stable, and nothing '
         'checks that this gesture is different from the last one. Two lines that '
         'look complete are not the same as two lines that are enough.', None),
    ], h=2.8)
    note(s, 16.0, [
        [('This is the exact place where a real gesture game needs more than a '
          'counting function, and we will come back to it.', None)],
    ], h=2.0)

    # ==================================== 42. STEP 16 ===
    s = add()
    title(s, [('Step 16', None), ('  —  ', None), ('robot move and winner', 'y')])
    body(s, Y_BODY_STD, [
        [('Still inside the gesture check. Two calls, and the order matters:', None)],
    ])
    code(s, 6.6, [
        '                    robot_gesture = get_robot_move()',
        '                    result = determine_winner(player_gesture, robot_gesture)',
    ], size=14.0)
    body(s, 9.4, [
        [('The robot picks first, then the winner is computed from both moves. '
          'Swapping them computes the same answer, which is a good reminder that '
          'the winner function takes both moves rather than asking the robot.', None)],
    ])
    note(s, 12.6, [
        [('Both lines sit inside the ', None), ('if valid_gesture and cooldown_ready', 'c'),
         (' condition, so neither runs unless the gesture has been held and the '
          'cooldown has expired. Those two flags are the entire rate limit for the '
          'game, and Step 15 never mentioned them.', None)],
    ], h=3.0)

    # ==================================== 43. STEP 17 ===
    s = add()
    title(s, [('Step 17', None), ('  —  ', None), ('update the scores', 'y')])
    body(s, Y_BODY_STD, [
        [('Straightforward, and worth reading closely because it decides whether '
          'the score and the round counter agree:', None)],
    ])
    code(s, 6.8, [
        '                    rounds_played += 1',
        '                    if result == "PLAYER":',
        '                        player_score += 1',
        '                    elif result == "ROBOT":',
        '                        robot_score += 1',
    ], size=13.5)
    bullet(s, 11.8, [
        ('rounds_played', 'b'), (' counts rounds, not points — it increments on a '
         'draw too.', None),
    ], h=1.9)
    bullet(s, 13.7, [
        ('So the score line can read', 'b'), (' 1  |  0  |  Round: 3', 'c'),
         (', and that is correct rather than a bug.', None),
    ], h=1.9)
    note(s, 16.2, [
        [('The reset key at the bottom of the loop resets all three together, which '
          'is why they belong together here.', None)],
    ], h=2.0)

    # ==================================== 44. STEP 18 ===
    s = add()
    title(s, [('Step 18', None), ('  —  ', None), ('perform the gesture', 'y')])
    body(s, Y_BODY_STD, [
        [('One line. Everything expensive happens inside the function it calls.',
          None)],
    ])
    code(s, 6.6, [
        '                    execute_robot_gesture(robot_gesture)',
    ], size=15.0)
    callout(s, 9.4, [
        ('This single line is where the loop stops for four and a half seconds. '
         'Nothing is drawn, nothing is detected, and nothing is checked. The '
         'gameplay logic is frozen for the entire duration of the arm movement.',
         None),
    ], h=2.8)
    body(s, 13.0, [
        [('If the arm is not attached, Step 11 returned early and this line costs '
          'microseconds instead. So the four and a half seconds are not a property '
          'of the game — they are a property of the hardware.', None)],
    ])
    note(s, 16.2, [
        [('Keep that in mind. It changes which of the problems ahead are always '
          'present and which only appear once you plug the arm in.', None)],
    ], h=2.0)

    # ==================================== 45. STEP 19 ===
    s = add()
    title(s, [('Step 19', None), ('  —  ', None), ('draw the game UI', 'y')])
    body(s, Y_BODY_STD, [
        [('Call the function you wrote in Step 12, near the bottom of the loop:', None)],
    ])
    code(s, 6.6, [
        '        draw_ui(frame, player_gesture, last_robot_move, game_result, finger_count)',
    ], size=13.0)
    body(s, 9.6, [
        [('Five arguments, all of them values the loop already has. Note the '
          'second one: it passes ', None), ('last_robot_move', 'c'),
         (', the label recorded in Step 11, not a live reading of the arm. The '
          'screen describes the last round, not the current pose.', None)],
    ])
    callout(s, 13.0, [
        ('This is also the last chance the verdict gets to appear. Whatever ', None),
        ('game_result', 'c'), (' holds at the moment this line runs is what the '
         'player sees — so the order of the lines below it is not a style '
         'preference.', None),
    ], h=2.8)

    # ==================================== 46. STEP 20 ===
    s = add()
    title(s, [('Step 20', None), ('  —  ', None), ('show the frame', 'y')])
    body(s, Y_BODY_STD, [
        [('The last TODO in the file:', None)],
    ])
    code(s, 6.6, [
        '        cv2.imshow("Mission 02 - Project 06: Rock Paper Scissors", frame)',
    ], size=14.0)
    body(s, 9.4, [
        [('Then the two lines that come with it. ', None), ('waitKey(1)', 'c'),
         (' is what makes the window interactive — without it the picture freezes '
          'and no key is ever read:', None)],
    ])
    code(s, 12.4, [
        '        key = cv2.waitKey(1) & 0xFF',
        '        if key == ord(\'q\'):',
        '            break',
        '        elif key == ord(\'r\'):',
        '            player_score = 0',
        '            robot_score = 0',
        '            rounds_played = 0',
        '            last_robot_move = None',
        '            game_result = "Score reset!"',
    ], size=12.5)
    callout(s, 17.4, [
        ('You have now filled in all twenty TODOs. The program is complete, it runs, '
         'and every message it prints is true. We are about to check that last '
         'part.', None),
    ], h=2.0)

    # ==================================== 47. READING THE SCREEN ===
    s = add()
    title(s, [('Reading the screen', None)])
    body(s, Y_BODY_STD, [
        [('The project is finished. Before changing a single line, learn to read '
          'what the program is already telling you.', None)],
    ])
    bullet(s, 7.4, [
        ('The yellow fallback line', 'b'), ('  — how many fingers were counted. '
         'If it says 3, the problem is your hand, not your code.', None),
    ], h=2.3)
    bullet(s, 9.7, [
        ('The score line', 'b'), ('  — rounds played and points scored. If rounds '
         'climb but points do not, the robot is drawing every time.', None),
    ], h=2.3)
    bullet(s, 12.0, [
        ('The verdict line', 'b'), ('  — the biggest text on the screen, at 1.2 '
         'scale, and the one you will forget to look at.', None),
    ], h=2.3)
    bullet(s, 14.3, [
        ('The console', 'b'), ('  — three banner lines on startup, and the hardware '
         'warning block if the arm is not found.', None),
    ], h=2.3)
    callout(s, 17.0, [
        ('Each of those is a measurement. A project that prints its own state is '
         'giving you the evidence you need before you have written a single print '
         'statement yourself.', None),
    ], h=2.4)

    # ==================================== 48. BEFORE YOU CHANGE ANYTHING ===
    s = add()
    title(s, [('Before you change anything', None)])
    body(s, Y_BODY_STD, [
        [('This project made four claims about its own behaviour. All four were '
          'wrong, and none of them was wrong in a way that crashes.', None)],
    ])
    table(s, 7.2, [
        ['#', 'The claim', 'What actually happened'],
        ['1', 'Hold steady for 1 second',
         'A single noisy frame triggered a 4.5 second arm movement'],
        ['2', 'The verdict appears',
         'It was cleared before it was ever drawn'],
        ['3', 'Rounds cannot repeat instantly',
         'The cooldown was measured across the arm delay, so it never blocked'],
        ['4', 'Runs without a robot',
         'The handler crashed on a name it never defined'],
    ], [1.4, 7.4, 12.8])
    note(s, 16.4, [
        [('Three of those four are the same mistake wearing different clothes: a '
          'timestamp taken at the wrong moment.', None)],
    ], h=1.6)

    # ==================================== 49. HOW IT WAS CORRECTED ===
    s = add()
    title(s, [('How this project was corrected', None)])
    body(s, Y_BODY_STD, [
        [('Every fix is already in the file you have. It starts with new state, '
          'because two of the four failures needed somewhere to remember when '
          'something happened:', None)],
    ])
    code(s, 5.8, [
        'GESTURE_HOLD_TIME = 1.0  # seconds',
        'hold_gesture = None',
        'hold_start = 0.0',
        '',
        '# How long a verdict stays on screen before it is cleared',
        'RESULT_DISPLAY_TIME = 2.0  # seconds',
        'last_result_time = 0.0',
    ], size=10.0)
    note(s, 8.6, [
        [('Constant for the promise, constant for the verdict window, three '
          'variables that hold the time.', None)],
    ], h=2.6)
    bullet(s, 11.4, [
        ('Fresh clocks', 'y'), ('  — ', None), ('time.time()', 'c'),
        (' is read at the point of use, and the verdict gets its own ', None),
        ('last_result_time', 'c'), (' instead of borrowing the cooldown stamp.', None),
    ], h=2.1)
    bullet(s, 13.5, [
        ('A verdict window', 'y'), ('  — the result is stamped ', None), ('after', 'b'),
        (' the arm returns home, so the display window starts when it should.', None),
    ], h=2.1)
    bullet(s, 15.6, [
        ('A defined handle', 'y'), ('  — ', None), ('mc = None', 'c'),
        (' before the ', None), ('try', 'c'), (', assigned to ', None), ('None', 'c'),
        (' in the handler, guarded at both use sites.', None),
    ], h=2.1)
    callout(s, 18.0, [
        ('Twenty lines changed in a 478 line file — no restructuring.', None),
    ], h=1.6)

    # ==================================== 50. CASE 1: THE HOLD THAT WAS NOT ===
    s = add()
    title(s, [('Claim 1', None), ('  —  ', None), ('the hold that was not', 'y')])
    body(s, Y_BODY_STD, [
        [('The program printed a promise:', None)],
    ])
    code(s, 5.8, [
        'print("Hold gesture steady for 1 second to play.")',
    ], size=13.5)
    body(s, 7.6, [
        [('And the loop that decides whether to play a round asked only whether the '
          'gesture was recognised. The version before this project was corrected '
          'gated on exactly one thing:', None)],
    ])
    code(s, 10.0, [
        '                valid_gesture = player_gesture in GESTURES',
    ], size=13.0)
    body(s, 11.8, [
        [('One frame could commit the arm, so the correction adds the question '
          'the promise implied:', None)],
    ])
    code(s, 14.2, [
        '                if player_gesture in GESTURES:',
        '                    if player_gesture != hold_gesture:',
        '                        hold_gesture = player_gesture',
        '                        hold_start = current_time',
        '                    held_for = current_time - hold_start',
        '                else:',
        '                    hold_gesture = None',
        '                    held_for = 0.0',
        '                valid_gesture = (player_gesture in GESTURES and held_for > GESTURE_HOLD_TIME)',
    ], size=9.5)
    note(s, 18.4, [
        [('Changing gesture resets the clock, an unrecognised one zeroes it — '
          'the second must be deliberate.', None)],
    ], h=2.4)

    # ==================================== 51. CASE 2: VERDICT NOBODY SAW ===
    s = add()
    title(s, [('Claim 2', None), ('  —  ', None), ('the verdict nobody saw', 'y')])
    body(s, Y_BODY_STD, [
        [('A round finished, a winner was computed, the score updated, the arm '
          'moved. And the player never saw the result.', None)],
    ])
    body(s, 7.0, [
        [('The round ended by stamping two values. Note that the timestamp comes '
          'from the top of the frame:', None)],
    ])
    code(s, 9.6, [
        '                    game_result = result',
        '                    last_game_time = current_time',
    ], size=13.0)
    body(s, 11.8, [
        [('Four and a half seconds of arm movement later, the loop reached this, '
          'above the call that draws the screen:', None)],
    ])
    code(s, 14.4, [
        '        # Clear the result message after a delay',
        '        if (time.time() - last_game_time) > RESULT_DISPLAY_TIME:',
        '            game_result = "Make a gesture!"',
    ], size=11.0)
    note(s, 17.2, [
        [('The delay had already elapsed before the verdict was ever drawn, so every '
          'round reset the message on its way to the screen. The correction gives '
          'the verdict its own clock and stamps it after the arm has finished '
          'moving — because the move is what consumed the window.', None)],
    ], h=2.6)

    # ==================================== 52. CASE 3: COOLDOWN ===
    s = add()
    title(s, [('Claim 3', None), ('  —  ', None), ('the broken cooldown', 'y')])
    body(s, Y_BODY_STD, [
        [('A cooldown exists so that one gesture cannot fire several rounds in a '
          'row. This one tested the right idea against the wrong clock:', None)],
    ])
    code(s, 7.6, [
        '                cooldown_ready = (current_time - last_game_time) > GAME_COOLDOWN',
    ], size=11.0)
    body(s, 10.0, [
        [('Both timestamps are frame timestamps. ', None), ('last_game_time', 'c'),
         (' was recorded at the top of the frame that started the round, and ', None),
         ('current_time', 'c'), (' is the top of a frame taken after four and a half '
          'seconds of blocking movement. The measured gap included the entire arm '
          'movement, so it was always larger than two seconds.', None)],
    ])
    callout(s, 14.6, [
        ('The cooldown was satisfied before it could ever refuse anything. The '
         'feature was present, named, commented and completely inert.', None),
    ], h=2.4)
    note(s, 17.2, [
        [('The correction reads the clock at the point of use instead:', None)],
    ], h=1.2)
    code(s, 18.5, [
        '                cooldown_ready = (time.time() - last_game_time) > GAME_COOLDOWN',
    ], size=10.0)

    # ==================================== 53. CASE 4: THE PROMISE ===
    s = add()
    title(s, [('Claim 4', None), ('  —  ', None), ('an unkept promise', 'y')])
    body(s, Y_BODY_STD, [
        [('Pull the arm, run it on a laptop without the robot libraries, and the '
          'handler prints a promise:', None)],
    ])
    code(s, 6.4, [
        'print("Continuing without the robot. Gestures are still detected and scored.\\n")',
    ], size=11.0)
    body(s, 8.0, [
        [('It could not: ', None), ('mc', 'c'), (' only existed inside the ', None),
         ('try', 'c'), (', so the handler fell through to ', None),
         ('finally', 'c'), (':', None)],
    ])
    code(s, 11.4, [
        'finally:',
        '    cap.release()',
        '    cv2.destroyAllWindows()',
        '    mc.release_all_servos()',
    ], size=12.0)
    callout(s, 13.0, [
        ('NameError, on the one path guaranteed to work.', None),
    ], h=1.8)
    body(s, 15.4, [
        [('The fix: ', None), ('mc = None', 'c'), (' before the ', None),
         ('try', 'c'), (', guarded at the use.', None)],
    ])
    code(s, 16.8, [
        'finally:',
        '    cap.release()',
        '    cv2.destroyAllWindows()',
        '    if mc is not None:',
        '        mc.release_all_servos()',
    ], size=9.5)

    # ==================================== 54. THE HABIT ===
    s = add()
    title(s, [('The habit that catches all four', None)])
    body(s, Y_BODY_STD, [
        [('Different bugs, one repeated mistake: trusting that a value means what '
          'its name suggests at the moment you read it.', None)],
    ])
    bullet(s, 7.0, [
        ('When was this clock read?', 'y'), ('  — a frame timestamp is fine for '
         'measuring across a frame and wrong for measuring across four seconds of '
         'sleeping.', None),
    ], h=2.5)
    bullet(s, 9.5, [
        ('Does this name exist yet?', 'y'), ('  — anything created inside a ', None),
        ('try', 'c'), (' block can be missing by the time you need it.', None),
    ], h=2.5)
    bullet(s, 12.0, [
        ('Is the promise still true downstream?', 'y'), ('  — a printed message '
         'makes a claim about the whole run, not about the line above it.', None),
    ], h=2.5)
    note(s, 15.0, [
        [('None of these four failures threw an error that pointed at the real '
          'problem. They were found by writing down what the program promised, then '
          'running it and looking for the promise. That is the same habit that '
          'found the OpenCV contour change in Project 5, and it is the one worth '
          'keeping.', None)],
    ], h=3.2)
    callout(s, 18.4, [
        ('A quiet bug is not a small bug. It is a bug that costs you the time to '
         'notice it.', None),
    ], h=1.6)

    # ==================================== 55. THE BRIEF ===
    s = add()
    title(s, [('The Brief', None)])
    body(s, Y_BODY_STD, [
        [('Rock, Paper, Robot', 'y'), ('\n', None)],
        [('Your arm is playing rock paper scissors against a hand you cannot see. '
          'MediaPipe reads 21 landmarks off the camera, five comparisons turn those '
          'landmarks into a number, three numbers become a gesture, and a lookup '
          'table decides a winner.', None)],
        [('Then the robot has to perform. Not describe. Perform — travel to the '
          'pose, hold it, come home, four and a half seconds of real movement '
          'between two frames.', None)],
        [('Which means the whole program has to survive being wrong. Not crash. '
          'Survive.', None)],
    ])

    # ==================================== 56. YOUR MISSION ===
    s = add()
    title(s, [('Your Mission', None)])
    body(s, Y_BODY_STD, [
        [('Three parts, in order.', None)],
    ])
    question_item(s, 6.8, 1, [
        ('Break it on purpose.', 'b'), ('  Remove the hold check from Step 15, run '
         'the game, and count how many rounds a single pass of your hand produces.', None)])
    question_item(s, 9.4, 2, [
        ('Break it on purpose, part two.', 'b'), ('  Unplug the arm, run the '
         'program, and record the exact text you get back.', None)])
    question_item(s, 12.0, 3, [
        ('Explain each one.', 'b'), ('  For each failure, write the claim it broke, '
         'the line that broke it, and the correction now sitting in the file.', None)])
    note(s, 15.2, [
        [('Do this with the corrected file in front of you. The point is not to '
          're-discover the bugs — they are already fixed — it is to prove to '
          'yourself that you can see a claim, break it, and name the fix without '
          'being told which line to look at.', None)],
    ], h=3.2)
    callout(s, 18.6, [
        ('A bug you cannot reproduce on demand is a bug you cannot prove you fixed.',
         None),
    ], h=1.4)

    # ==================================== 57. YOUR DATA LOG ===
    s = add()
    title(s, [('Your Data Log', None)])
    table(s, 6.6, [
        ['Claim', 'How you broke it', 'What you saw', 'The line that did it'],
        ['1 sec hold', '', '', ''],
        ['Verdict shows', '', '', ''],
        ['Cooldown holds', '', '', ''],
        ['Runs no-arm', '', '', ''],
    ], [3.6, 6.2, 6.2, 5.6], row_h=2.15)
    note(s, 17.4, [
        [('Exact text, not a paraphrase. The phrase ', None), ('name \'mc\' is not defined', 'c'),
         (' is worth more to your future self than the word "crashed", because it '
          'tells you the failure happened in cleanup rather than in the game.',
          None)],
    ], h=2.4)

    # ==================================== 58. DEFINITION OF DONE ===
    s = add()
    title(s, [('Definition of Done', None)])
    check_item(s, 6.8, [('All twenty TODOs filled in and the file runs on the Pi.',
                         None)])
    check_item(s, 8.6, [('No ', None), ('TODO', 'c'),
                        (' markers left anywhere in the file.', None)])
    check_item(s, 10.4, [('Each of the four failures above reproduced on demand, with '
                         'the exact message recorded.', None)])
    check_item(s, 12.2, [('The hold survives a two-second pause in tracking without '
                         'firing a round.', None)])
    check_item(s, 14.0, [('The verdict is on screen long enough to read, and the '
                         'score line agrees with it.', None)])
    check_item(s, 15.8, [('One gesture cannot start two rounds in a row.', None)])
    check_item(s, 17.6, [('Pulling the arm mid-game leaves the program running.', None)])
    callout(s, 18.5, [
        ('The last one is the real test: the project keeps working with the '
         'arm unplugged.', None),
    ], h=1.8)

    # ==================================== 59. GO FURTHER ===
    s = add()
    title(s, [('Go Further', None)])
    bullet(s, 6.8, [
        ('Four gestures.', 'b'), ('  Add Spock, and add the three new ', None),
        ('WIN_MAP', 'c'), (' pairs. Then decide what a count of 4 now means.', None),
    ], h=2.3)
    bullet(s, 9.1, [
        ('Two hands.', 'b'), ('  Raise ', None), ('max_num_hands', 'c'),
        (' to 2 and decide what the game is when both are playing.', None),
    ], h=2.3)
    bullet(s, 11.4, [
        ('Move the blocking work off the loop.', 'b'), ('  A thread for the arm, or '
         'a queue with one pending gesture, so the window never freezes.', None),
    ], h=2.3)
    bullet(s, 13.7, [
        ('Real velocities.', 'b'), ('  ', None), ('send_coords', 'c'),
        (' takes a speed argument. Find out what the units are and make the gesture '
         'feel deliberate rather than slow.', None),
    ], h=2.3)
    bullet(s, 16.0, [
        ('Check the tracker.', 'b'), ('  The confidence thresholds are guesses. '
         'Instrument them and find out which one is actually rejecting your hand.',
         None),
    ], h=2.3)
    note(s, 19.0, [
        [('Pick one. Not all five.', None)],
    ], h=1.0)

    # ==================================== 60. DEBRIEF ===
    s = add(0, master=1)
    title(s, [('Debrief', None)], ext=True)
    body(s, Y_BODY_EXT, [
        [('This project had three systems and one of them was optional, which turned '
          'out to be the interesting part.', None)],
        [('The camera problem was solved by never letting a queue form. The arm '
          'problem was solved by a four and a half second sleep nobody could remove. '
          'The bug problem was solved by treating a printed message as a promise and '
          'checking it.', None)],
        [('Every one of the four failures was quiet. No traceback, no exception, no '
          'error message — just a score that went up, a verdict that never appeared, '
          'and a message that promised something the program could not deliver.', None)],
        [('Write the claim down first. Run it second.', None), ('\n', None),
         ('That is the whole lesson, and it applies to every project in this module.',
          None)],
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
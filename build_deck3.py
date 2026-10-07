# -*- coding: utf-8 -*-
"""Build Slides/M2/myCobot_03.pptx -- 'Recognising Objects' (M2-P3).

Rebuilds the deck from the theme/layouts of the reference sample
Slides/myCobot_08.pptx, but teaches the threaded-camera + YOLOv5 object
detection pipeline that students complete in M2/M2-P3-Starter.py.

Every code snippet below is copied verbatim from M2/M2-P3-Base.py.
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
OUT = os.path.join(HERE, 'Slides', 'M2', 'myCobot_03.pptx')
TMP = os.path.join(HERE, 'tmp_media')

STARTER = 'M2-P3-Starter.py'
# Unlike P1 and P2 the model and label files must travel with the script,
# so they are copied across in the same command.
SCP = f'scp {STARTER} yolov5s.onnx coco.names er@192.168.1.149:Documents'
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
    para(tf, True, 'Project 3', F_TITLE, SZ_DIVIDER, YELLOW, line_spacing=1.0)
    para(tf, False, 'Recognising Objects', F_TITLE, SZ_DIVIDER, WHITE, line_spacing=1.0)

    # ====================================================== 3. WHAT'S NEXT ===
    s = add()
    title(s, [('What’s ', None), ('next', None), ('?', None)])
    body(s, Y_BODY_STD, [
        [('Project 1 taught the computer to measure a shape. Project 2 taught it '
          'to measure a ', None),
         ('position', 'b'),
         (' in millimetres. Both of those were things ', None),
         ('you', 'i'),
         (' told it how to look for.', None)],
        None,
        [('This project is different in kind. You are not writing the rules any '
          'more. You are loading a model that somebody else trained on hundreds of '
          'thousands of labelled photographs, and asking it what it can see.', None)],
        None,
        [('The rules now live in a file called ', None),
         ('yolov5s.onnx', 'c'),
         (', twenty-nine megabytes of arithmetic. Your program’s job is to feed '
          'it a picture, read the answer back out, and decide what to do with it.', None)],
    ])
    note(s, 15.2, [
        ('This is the first project in the module where the interesting decisions '
         'are about trust rather than accuracy. A neural network will always answer, '
         'even when it is guessing. Learning to tell the difference is the real '
         'skill.', None),
    ], h=2.2)

    # ================================================ 4. LIMITS OF SHAPE DETECTION ===
    s = add()
    title(s, [('What YOLO will ', None), ('not', None), (' do', None)])
    body(s, Y_BODY_STD, [
        [('Your shape detector worked on ', None),
         ('any', 'i'),
         (' triangle, square, circle or rectangle you could draw on a piece of '
          'paper. If it had four corners and straight edges, it found them.', None)],
        None,
        [('The model in this project knows ', None),
         ('eighty specific things', 'b'),
         (' and nothing else. Hold up a hand-printed kite and it will not be '
          'recognised, because a kite is not one of the eighty. Hold up a pair of '
          'scissors and it will be.', None)],
        None,
        [('That is not a flaw in the model. It is what "trained" means: somebody '
          'showed it pictures of eighty categories and labelled every one, and it '
          'learned those. It has never seen your project.', None)],
    ])
    callout(s, 14.8, [
        ('Before you write any code, look at the eighty class names on the next '
         'few slides and decide what you are actually going to put on the board. '
         'Choosing objects the model knows is the single biggest thing you can do '
         'to make this project work.', None),
    ], h=2.44)

    # ============================================= 5. RULES VS LEARNED RULES ===
    s = add()
    title(s, [('Two ways to spot a ', None), ('cup', None)])
    body(s, Y_BODY_STD, [
        [('The old way. You decide in advance what a cup looks like: round-ish, '
          'with a handle, taller than it is wide, sitting on a flat surface. You '
          'write each of those as a test. A blue mug with no handle fails all of '
          'them.', None)],
        None,
        [('The new way. You show the computer ten thousand photographs of cups, '
          'labelled ', None),
         ('cup', 'c'),
         (', and ten thousand of other things, labelled with what they actually '
          'are. It works out for itself which combination of shape, colour, '
          'texture and context means "cup". You never write a single test.', None)],
        None,
        [('The second method is more accurate and far more flexible. It is also '
          'impossible to write by hand, impossible to read line by line, and '
          'completely incapable of telling you ', None),
         ('why', 'i'),
         (' it decided what it decided.', None)],
    ])
    note(s, 15.4, [
        [('That last point is not a complaint, it is the deal. You get a strong '
          'answer with no reasoning attached. Learning to design around an '
          'answer you cannot interrogate is a skill in its own right, and it is '
          'the reason this project spends as long on thresholds as on maths.', None)],
    ], h=2.4)

    # ===================================================== 6. WHAT IS YOLOV5 ===
    s = add()
    title(s, [('What is ', None), ('YOLOv5', None), ('?', None)])
    body(s, Y_BODY_STD, [
        [('YOLO is short for ', None),
         ('You Only Look Once', 'b'),
         ('. Older detection systems looked at the picture in stages — first find '
          'candidate regions, then classify each one. YOLO does the whole job in a '
          'single pass, which is why it is fast enough to run on a small computer '
          'beside a robot arm.', None)],
        None,
        [('The ', None),
         ('v5', 'c'),
         (' is the fifth version. The ', None),
         ('s', 'c'),
         (' at the end of ', None),
         ('yolov5s.onnx', 'c'),
         (' means ', None),
         ('small', 'b'),
         (' — the fastest and least accurate of the family. There are larger '
          'models that are more accurate and too slow for this hardware. This one '
          'is the right trade.', None)],
    ])
    note(s, 13.6, [
        [('Every part of that name matters when something goes wrong. ', None),
         ('v5', 'c'),
         (' tells you which set of output numbers to expect — read the wrong '
          'version’s layout and your boxes land in nonsense places. ', None),
         ('s', 'c'),
         (' tells you how much accuracy you gave up for speed.', None)],
    ], h=2.6)

    # ==================================================== 7. THE MODEL FILE ===
    s = add()
    title(s, [('The model is a ', None), ('file', None)])
    body(s, Y_BODY_STD, [
        [('This project does not train anything. Nobody at this station is going '
          'to teach a neural network anything from scratch. The learning already '
          'happened, months ago, on a large computer, and the result was saved to '
          'disk.', None)],
        None,
        [('What you load is that saved result: ', None),
         ('yolov5s.onnx', 'c'),
         (', about 29 megabytes. The ', None),
         ('.onnx', 'c'),
         (' extension is ', None),
         ('Open Neural Network Exchange', 'b'),
         (' — a neutral format, so a network trained in one framework can be used '
          'by OpenCV in another.', None)],
        None,
        [('This is the part students forget. The file has to exist, in the right '
          'folder, on the machine that is running the program. The arm is a '
          'different computer from your laptop.', None)],
    ])
    callout(s, 15.0, [
        ('Copying your .py file across is not enough this time. The program looks '
         'for the model next to itself, so yolov5s.onnx and coco.names have to '
         'travel too. Get this wrong and the program tells you so by name.', None),
    ], h=2.44)

    # ==================================================== 8. COCO CLASSES ===
    s = add()
    title(s, [('Eighty things, and ', None), ('only', None), (' those', None)])
    body(s, Y_BODY_STD, [
        [('The model was trained on a dataset called ', None),
         ('COCO', 'b'),
         (', which stands for Common Objects in Context. It contains photographs '
          'of everyday things, each labelled with what they are. Eighty of those '
          'labels are what this model knows.', None)],
        None,
        [('They run from the obvious to the obscure. ', None),
         ('person', 'c'), (', ', None), ('bicycle', 'c'), (', ', None),
         ('car', 'c'), (', ', None), ('cup', 'c'), (', ', None),
         ('scissors', 'c'), (', ', None), ('teddy bear', 'c'), (', ', None),
         ('toothbrush', 'c'),
         ('. There is no "shape", no "block", and no "my object".', None)],
        None,
        [('A useful classroom object is a laptop, a book, a bottle, a cup, a '
          'cellphone or a pair of scissors. Test your object against the list '
          'before you write anything.', None)],
    ])
    note(s, 14.8, [
        [('A common and expensive mistake: spend an afternoon tuning thresholds on '
          'an object the model has never been trained to recognise. It will never '
          'work, and no threshold will save it. Check the list first — it takes '
          'ten seconds and it is free.', None)],
    ], h=2.4)

    # =============================================== 9. FINDING YOUR OWN FILES ===
    s = add()
    title(s, [('Where am ', None), ('I', None), ('?', None)])
    code(s, 4.6, [
        'script_dir = os.path.dirname(os.path.abspath(__file__))',
    ], size=15.0)
    body(s, 7.2, [
        [('A program does not know where it lives. It knows the folder you '
          'happened to be standing in when you ran it, and those are often not the '
          'same place.', None)],
        None,
        [('__file__', 'c'),
         (' is the path to the script itself. ', None),
         ('abspath', 'c'),
         (' makes it absolute rather than relative, and ', None),
         ('dirname', 'c'),
         (' strips off the filename, leaving the folder. Read the names right to '
          'left and it nearly explains itself.', None)],
        None,
        [('From that one line, the two file paths are easy:', None)],
    ])
    code(s, 12.6, [
        'model_path = os.path.join(script_dir, "yolov5s.onnx")',
        'labels_path = os.path.join(script_dir, "coco.names")',
    ], size=14.0)
    note(s, 15.2, [
        [('This is the difference between a program that works and one that works '
          'only on the machine that wrote it. ', None),
         ('os.path.join', 'c'),
         (' builds paths the right way on any system.', None)],
    ], h=2.2)

    # ========================================== 10. THE MARKERS CHANGE JOBS ===
    s = add()
    title(s, [('The markers get a ', None), ('new job', None)])
    body(s, Y_BODY_STD, [
        [('You already taped two ArUco markers to the board in Project 2, and '
          'this project uses exactly the same two, in the same places, with the '
          'same detection code.', None)],
        None,
        [('What changed is the question you ask of them. In Project 2 a marker '
          'meant ', None),
         ('how far away is this', 'b'),
         (', measured in millimetres. Here it means ', None),
         ('where does my workspace start and stop', 'b'),
         (' — a rectangle on the screen, in plain pixels.', None)],
        None,
        [('Same tool, new job. This is worth noticing, because in a real project '
          'you will keep meeting the same components doing different jobs, and the '
          'component does not change at all — only what you ask it.', None)],
    ])
    callout(s, 14.4, [
        ('Nothing about the detection code changes between Project 2 and Project '
         '3. If your markers were found there, they will be found here. If they '
         'were not, no amount of work on the YOLO half will help you.', None),
    ], h=2.44)

    # ==================================================== 11. WHY CROP AT ALL ===
    s = add()
    title(s, [('Why crop the ', None), ('picture', None), ('?', None)])
    body(s, Y_BODY_STD, [
        [('The camera sees your desk, your hands, the edge of the board, and half '
          'the room. The model was trained on photographs of objects, so a desk '
          'with a laptop on it is a strange input — and it will find the laptop '
          'anyway, but it will also find things on the desk you never meant to '
          'show it.', None)],
        None,
        [('So the program uses the markers to decide what to look at. Everything '
          'outside the rectangle they define is thrown away before the model ever '
          'sees it.', None)],
        None,
        [('This is a cheap, enormous win. The model gets a smaller, steadier, more '
          'consistent picture, which means better accuracy and fewer false '
          'positives — and it costs one crop.', None)],
    ])
    note(s, 15.0, [
        [('It also protects the numbers. A detection box reported on a cropped '
          'image is in cropped coordinates, so when you act on it you must remember '
          'which picture it came from. Know your coordinate system at the point '
          'you record a measurement, not later.', None)],
    ], h=2.4)

    # =================================================== 12. THE LATENCY PROBLEM ===
    s = add()
    title(s, [('A problem you can ', None), ('see', None)])
    body(s, Y_BODY_STD, [
        [('Here is the fault that motivates half of this project. Put your hand in '
          'front of the camera and wave it slowly. The box drawn around your hand '
          'lags behind it.', None)],
        None,
        [('The camera is not slow, and neither is the model. The problem is '
          'between them. A Linux camera driver works like this: it fills a buffer '
          'in the background, and when your program asks for a frame it gets ', None),
         ('whatever is in that buffer at that moment', 'b'),
         (' — not the newest picture.', None)],
        None,
        [('By the time the model has finished thinking about frame 1, the camera '
          'has already produced frames 2, 3 and 4. Every frame you analyse is '
          'already out of date by the time you draw it.', None)],
    ])
    callout(s, 15.0, [
        ('Small delay, serious consequences. A sorter that is always half a second '
         'behind its hand puts the arm in the wrong place, every time, and no '
         'amount of threshold tuning will fix it.', None),
    ], h=2.44)

    # =================================================== 13. FIXING IT WITH A THREAD ===
    s = add()
    title(s, [('Somebody has to ', None), ('drain the buffer', None)])
    body(s, Y_BODY_STD, [
        [('The fix is to have a background thread whose only job is to read frames '
          'as fast as the camera produces them, throwing each one away except the '
          'newest. Your main loop then asks for whatever is currently in hand — '
          'which is always the most recent frame, seconds or milliseconds old '
          'rather than half a second.', None)],
        None,
        [('One line sets it up. ', None),
         ('daemon=True', 'c'),
         (' means the thread is not allowed to keep the program alive on its own: '
          'when ', None),
         ('main()', 'c'),
         (' returns, Python takes the thread down with it instead of waiting '
          'forever.', None)],
    ])
    code(s, 12.6, [
        'self.thread = threading.Thread(target=self._update, daemon=True)',
        'self.thread.start()',
    ], size=13.5)
    note(s, 15.4, [
        [('target=self._update', 'c'),
         (' names the function the thread runs. Starting the thread and defining '
          'what it does are two separate acts, in that order — the same shape as '
          'the vision pipeline you will build next.', None)],
    ], h=2.0)

    # ================================================ 14. THE LOCK AND THE COPY ===
    s = add()
    title(s, [('Sharing a picture between two ', None), ('threads', None)])
    body(s, Y_BODY_STD, [
        [('Now two parts of the program can touch the same picture at the same '
          'moment: the background thread writing it, your main loop reading it. '
          'That is a race, and races do not fail politely.', None)],
        None,
        [('The ', None),
         ('with self.lock', 'c'),
         (' block means "nobody else touches this while I am inside". Only one '
          'thread can hold the lock at a time, so the frame is either fully old or '
          'fully new — never half of each.', None)],
        None,
        [('The ', None),
         ('.copy()', 'c'),
         (' on the way out is the other half of the answer, and it is the one '
          'people leave out. Without the copy you would be handed a reference to '
          'the very buffer the background thread is about to overwrite. You would '
          'start analysing a picture that changes underneath you, and the '
          'symptom would be boxes that shimmer for no reason anyone could '
          'explain.', None)],
    ])
    callout(s, 15.0, [
        ('The rule: hand out copies, never the original. It costs a few '
         'milliseconds and it removes an entire category of bug you would '
         'otherwise spend a day chasing.', None),
    ], h=2.44)

    # ==================================================== 15. CLEAN SHUTDOWN ===
    s = add()
    title(s, [('Turning it ', None), ('off', None), (' politely', None)])
    body(s, Y_BODY_STD, [
        [('Press ', None),
         ('q', 'c'),
         (' and the main loop breaks. If ', None),
         ('release', 'c'),
         (' just closed the camera, the background thread would still be blocked '
          'in a read on hardware that no longer exists. It has to be stopped first, '
          'and told to stop politely.', None)],
        None,
        [('self.running = False', 'c'),
         (' is the flag the thread’s own ', None),
         ('while', 'c'),
         (' loop is watching. It finishes the frame it is on, notices the flag, '
          'and exits at the top of the next pass.', None)],
        None,
        [('join(timeout=0.5)', 'c'),
         (' then waits up to half a second for it to actually stop, and gives up '
          'rather than hanging forever if it will not.', None)],
    ])
    code(s, 14.4, [
        'self.running = False',
        'if self.thread.is_alive():',
        '    self.thread.join(timeout=0.5)',
    ], size=13.5)
    note(s, 17.2, [
        [('The ', None),
         ('time.sleep(0.005)', 'c'),
         (' inside the thread’s loop is worth understanding too. Without it the '
          'thread would spin reading the camera flat out, burning CPU and heat '
          'while producing frames nobody wants. A tiny pause keeps it polite.',
          None)],
    ], h=1.9)

    # ============================================== 16. PREPROCESSING: THE BLOB ===
    s = add()
    title(s, [('The model does not eat ', None), ('pictures', None)])
    body(s, Y_BODY_STD, [
        [('A neural network cannot be handed a colour photograph. It expects a '
          'fixed-size grid of numbers, scaled a particular way, in a particular '
          'order, with the colour channels swapped. Getting any of those four '
          'things wrong produces a network that still runs and still answers — '
          'confidently and wrongly.', None)],
        None,
        [('That preparation is one call:', None)],
    ])
    code(s, 9.6, [
        'blob = cv2.dnn.blobFromImage(',
        '    img, 1.0 / 255.0, self.input_size, [0, 0, 0], swapRB=True, crop=False',
        ')',
    ], size=13.5)
    body(s, 12.6, [
        [('The second argument divides every pixel by 255, turning 0–255 '
          'brightness into 0–1; the third resizes to the 640x640 the model was '
          'trained at.', None)],
        None,
        [('The last two are the ones people miss. ', None),
         ('swapRB=True', 'c'),
         (' turns OpenCV’s blue-green-red order into the red-green-blue the model '
          'expects; ', None),
         ('[0, 0, 0]', 'c'),
         (' subtracts nothing — zero says this model needs none.', None)],
    ], size=18.0)
    note(s, 16.2, [
        [('These four numbers are properties of ', None),
         ('this', 'i'),
         (' model, not your program — change one and boxes land wrong, '
          'quietly.', None)],
    ], h=1.9)

    # ================================================== 17. THE FORWARD PASS ===
    s = add()
    title(s, [('Asking the model ', None), ('something', None)])
    code(s, 4.6, [
        'self.net.setInput(blob)',
        'outputs = self.net.forward(self.net.getUnconnectedOutLayersNames())',
    ], size=14.0)
    body(s, 6.6, [
        [('Two steps, and the first one surprises people. ', None),
         ('setInput', 'c'),
         (' does not run anything — it just hands the prepared picture to the '
          'network and waits. The network computes nothing at all until you call ', None),
         ('forward', 'c'),
         ('.', None)],
        None,
        [('getUnconnectedOutLayersNames', 'c'),
         (' asks the network which of its outputs nothing else depends on, and '
          'returns just those. It saves work: you get the predictions without '
          'waiting for internal layers whose results you were never going to use.', None)],
        None,
        [('The output is a NumPy array, not a list of Python objects. From here '
          'on you are reading numbers out of it, and the next slide is the map you '
          'need.', None)],
    ])
    note(s, 13.8, [
        [('One call to ', None),
         ('forward', 'c'),
         (' is one frame’s worth of thinking — the most expensive line in the '
          'program, by a wide margin.', None)],
    ], h=2.2)

    # ================================================ 18. READING ONE ROW ===
    s = add()
    title(s, [('One row of the ', None), ('answer', None)])
    body(s, Y_BODY_STD, [
        [('The model returns one row for every possible object position it '
          'considered — thousands of them, most of them describing nothing at all. '
          'Each row has the same layout, and it is worth writing it out:', None)],
    ])
    table(s, 6.6, [
        ['Columns', 'Meaning', 'Units'],
        ['row[0] to row[3]', 'cx, cy, w, h — centre and size', 'pixels in the 640 space'],
        ['row[4]', 'Objectness — is there anything here', '0 to 1'],
        ['row[5] onwards', 'One score per class, 80 of them', '0 to 1'],
    ], col_w=[5.4, 11.4, 7.2])
    body(s, 11.4, [
        [('Four numbers of geometry, then two separate confidence questions. ', None),
         ('row[4]', 'c'),
         (' asks "is there an object in this patch of picture at all", and the row '
          'of class scores asks "and if so, which one". A row can pass the first '
          'test and fail the second.', None)],
        None,
        [('Every coordinate is in the model’s own 640x640 space, not in pixels of '
          'your picture. That conversion is coming up, and forgetting it is the '
          'single most common reason boxes land nowhere near the objects.', None)],
    ])

    # ================================================ 19. THREE THRESHOLDS, NMS ===
    s = add()
    title(s, [('Three numbers decide what is ', None), ('real', None)])
    code(s, 4.6, [
        'def __init__(self, conf_thresh=0.45, score_thresh=0.5, nms_thresh=0.45):',
    ], size=13.0)
    body(s, 7.2, [
        [('Two gates and one filter, all set once in the constructor.', None)],
    ])
    table(s, 8.6, [
        ['Name', 'Default', 'What it decides'],
        ['conf_thresh', '0.45', 'Is there an object in this patch at all'],
        ['score_thresh', '0.50', 'Is it this particular class'],
        ['nms_thresh', '0.45', 'How much overlap before a second box is discarded'],
    ], col_w=[5.6, 4.0, 14.4])
    body(s, 12.8, [
        [('NMS needs a picture to explain: the model draws several boxes per '
          'object, and NMS keeps the best of each cluster.', None)],
        None,
        [('Raise it and real boxes vanish; lower it and you get three per '
          'cup.', None)],
    ])
    note(s, 16.6, [
        [('One box can still be drawn where nothing is — confidently. NMS only '
          'removes duplicates, not mistakes; ', None),
         ('conf_thresh', 'c'),
         (' is your only lever.', None)],
    ], h=2.0)

    # ================================================= 20. DRAWING THE RESULTS ===
    s = add()
    title(s, [('Drawing what you ', None), ('found', None)])
    code(s, 4.6, [
        'cv2.rectangle(annotated_img, (left, top), (left + width, top + height), (0, 255, 0), 2)',
    ], size=11.5)
    code(s, 7.4, [
        'cv2.circle(annotated_img, (cx, cy), 4, (0, 0, 255), -1)',
    ], size=14.0)
    code(s, 9.6, [
        'cv2.putText(annotated_img, label, (left, max(top - 5, 15)),',
        '            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)',
    ], size=13.0)
    body(s, 12.6, [
        [('A green rectangle, a blue centre dot, and the name and confidence '
          'printed above — readable enough to debug from across the room.', None)],
        None,
        [('The dot is the centre point you would hand to the arm, and it exposes '
          'a mis-scaled box at a glance.', None)],
        None,
        [('max(top - 5, 15)', 'c'),
         (' keeps the label on screen when a box sits near the top edge.', None)],
    ])

    # ====================================================== 21. THE PIPELINE ===
    s = add()
    title(s, [('The whole pipeline on ', None), ('one line', None)])
    code(s, 4.6, [
        'display_frame, log_info = vision.yolo_detect(cropped_frame)',
    ], size=14.5)
    body(s, 7.4, [
        [('Everything above is inside that one call, in this order:', None)],
    ])
    steps = [
        ('Preprocess', 'Resize, scale, swap channels, build the input blob.'),
        ('Think', 'One forward pass through the network.'),
        ('Filter', 'Two confidence gates on every row of the answer.'),
        ('Convert', 'Turn 640-space numbers back into real pixel coordinates.'),
        ('Draw', 'Rectangle, centre dot, name and confidence.'),
    ]
    for i, (h_, b_) in enumerate(steps):
        num_item(s, 8.5 + i * 1.6, i + 1, h_, [(b_, None)], h=1.4)
    note(s, 15.0, [
        ('The lines before it in the loop crop to the workspace, so this sees just '
         'your board. Six steps, one call, about a hundred milliseconds.', None),
    ], h=1.6)

    # ======================================================= 22. STEP 1 ===
    s = add()
    title(s, [('Step 1', None)])
    body(s, Y_BODY_STD, [
        [('Four packages this time, and one of them is new:', None)],
    ])
    code(s, 5.6, [
        'import cv2',
        'import numpy as np',
        'import time',
        'import os',
    ], size=15.0)
    body(s, 8.8, [
        [('cv2', 'c'), (' and ', None), ('numpy', 'c'), (' you know. ', None),
         ('time', 'c'), (' still gives the arm its pauses. ', None),
         ('os', 'c'),
         (' is new, and it exists because this project has to find files on disk.', None)],
        None,
        [('Now look at the line just below this TODO. ', None),
         ('import threading', 'c'),
         (' is already written for you — it is outside the ', None),
         ('# ---', 'c'),
         (' markers, so it is not yours to fill in. Read the starter before you '
          'start; some of the work is already done.', None)],
    ])

    # ======================================================= 23. STEP 2 ===
    s = add()
    title(s, [('Step 2', None)])
    body(s, Y_BODY_STD, [
        [('The robot import, unchanged from the last two projects:', None)],
    ])
    code(s, 5.6, [
        'from pymycobot.mycobot280 import MyCobot280',
    ], size=15.0)
    body(s, 8.0, [
        [('The vision half of this project needs no robot at all. That is worth '
          'saying out loud, because it means you can do every interesting thing '
          'in this project on a laptop with the arm switched off.', None)],
        None,
        [('It also means the ', None),
         ('try', 'c'),
         (' block below will warn you about missing hardware and carry on, and that '
          'is the design working rather than something to fix.', None)],
    ])
    note(s, 12.4, [
        ('Get the vision pipeline working before you worry about the arm. The '
         'interesting bugs in this project are all in the code you are about to '
         'write, and none of them need hardware to find.', None),
    ], h=1.9)

    # ======================================================= 24. STEP 3 ===
    s = add()
    title(s, [('Step 3', None)])
    body(s, Y_BODY_STD, [
        [('Same robot startup as before, inside the ', None), ('try', 'c'),
         (' block:', None)],
    ])
    code(s, 5.6, [
        'print("Connecting to myCobot280...")',
        "mc = MyCobot280('/dev/ttyAMA0', 1000000)",
        'time.sleep(0.5)',
        'mc.power_on()',
        'time.sleep(0.5)',
    ], size=15.0)
    body(s, 9.4, [
        [('Nothing new here, which is the point. The port and the baud rate are '
          'the same, the pauses are the same, and the whole block still fails '
          'safely when there is no arm attached.', None)],
        None,
        [('Notice which parts of this program ', None),
         ('are', 'i'),
         (' reusable. Every project in this module repeats the same four blocks — '
          'imports, robot startup, camera scan, display loop. Recognising them '
          'means you spend your attention on the part that is actually new.', None)],
    ])

    # ======================================================= 25. STEP 4 ===
    s = add()
    title(s, [('Step 4', None)])
    body(s, Y_BODY_STD, [
        [('Park the arm, same as always:', None)],
    ])
    code(s, 5.4, [
        'folded_angles = [0, 45, -90, -45, 0, 0]',
        'print("Moving arm to initial folded position...")',
        'mc.send_angles(folded_angles, 20)',
        'time.sleep(2.0)',
    ], size=15.0)
    note(s, 8.6, [
        [('Folding the arm up and out of shot matters more in this project than in '
          'the last two. The model has been trained on photographs of rooms, and '
          'it is very good at finding objects in them. A shiny metal arm sitting in '
          'shot is an object in a room, and it will be detected as one.', None)],
    ], h=2.6)
    body(s, 11.4, [
        [('If you see a box appear around the arm itself, this is why. It is not a '
          'bug in the model and there is no threshold that fixes it properly — the '
          'object is genuinely there. Move it out of the picture.', None)],
    ])

    # ============================================ 26. GETTING IT ONTO THE ARM ===
    s = add()
    title(s, [('Three files, not ', None), ('one', None)])
    body(s, Y_BODY_STD, [
        [('This is the one command that is different from the last two projects. '
          'The model and the label file have to arrive on the arm as well, because '
          'the program looks for them beside your script:', None)],
    ])
    command(s, 6.8, SCP, size=15.0)
    body(s, 8.4, [
        [('All three filenames go in one command. Forget the model and the program '
          'starts and then reports ', None),
         ('YOLO Model Not Loaded', 'c'),
         (' by name — which is a much friendlier failure than a traceback.', None)],
    ])
    command(s, 11.4, RUN)
    body(s, 13.0, [
        [('Run it now, with the vision TODOs still '
          'empty. There is no error message this time — nothing happens, and that '
          'is worth understanding.', None)],
        None,
        [('The crop returns nothing, the detector returns ', None),
         ('"No Frame"', 'c'),
         (', and the display shows nothing.', None)],
    ])
    note(s, 16.4, [
        [('A silent program is one whose guards all work. '
          'Fill the TODOs and the window appears.', None)],
    ], h=2.0)

    # ======================================================= 27. STEP 5 ===
    s = add()
    title(s, [('Step 5', None)])
    body(s, Y_BODY_STD, [
        [('The ArUco block, byte for byte the one from Project 2:', None)],
    ])
    code(s, 6.0, [
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
    note(s, 12.8, [
        [('If you typed this carefully in Project 2, it is already in your muscle '
          'memory. Do not retype it from memory though — copy it across. One '
          'misplaced bracket here produces an ', None),
         ('SyntaxError', 'c'),
         (' that points at the wrong line and wastes an hour.', None)],
    ], h=2.2)

    # ======================================================= 27. STEP 6 ===
    s = add()
    title(s, [('Step 6', None)])
    body(s, Y_BODY_STD, [
        [('This TODO looks like one line but does not need to be. All it '
          'requires is the folder the script lives in:', None)],
    ])
    code(s, 6.0, [
        'script_dir = os.path.dirname(os.path.abspath(__file__))',
    ], size=14.0)
    code(s, 8.0, [
        'model_path = os.path.join(script_dir, "yolov5s.onnx")',
        'labels_path = os.path.join(script_dir, "coco.names")',
    ], size=14.0)
    body(s, 11.0, [
        [('Nothing is opened or read yet — these are just strings naming where '
          'files should be. That comes in the next two steps, and keeping '
          '"decide where" separate from "read it" is what makes this code easy to '
          'test.', None)],
        None,
        [('Check the folder now, before you write any more. ', None),
         ('yolov5s.onnx', 'c'),
         (' and ', None),
         ('coco.names', 'c'),
         (' should be sitting next to ', None),
         ('M2-P3-Starter.py', 'c'),
         (' in your project folder. If they are not, get them now.', None)],
    ])
    note(s, 15.4, [
        [('On the arm the model must be in ', None),
         ('Documents', 'c'),
         (' beside your script. Copying only the ', None),
         ('.py', 'c'),
         (' across is the most common reason this project refuses to start — it '
          'costs one extra filename in the ', None),
         ('scp', 'c'), (' command.', None)],
    ], h=2.2)

    # ======================================================= 28. STEP 7 ===
    s = add()
    title(s, [('Step 7', None)])
    body(s, Y_BODY_STD, [
        [('Now load the network. It is one line, and it has a condition attached:', None)],
    ])
    code(s, 6.0, [
        'self.net = cv2.dnn.readNet(model_path) if os.path.exists(model_path) else None',
    ], size=12.0)
    body(s, 8.6, [
        [('The conditional expression — ', None),
         ('A if test else B', 'c'),
         (' — means "load the network if the file is there, otherwise set ', None),
         ('net', 'c'),
         (' to ', None),
         ('None', 'c'),
         ('". Same idea you used for the conditional in Project 1, written on one '
          'line.', None)],
        None,
        [('It matters that it does not simply crash. A missing model file is an '
          'entirely likely mistake on a machine that has never run this project, '
          'and this line turns that mistake into a state the program can carry on '
          'from — and report by name.', None)],
    ])
    note(s, 13.6, [
        [('The check further down — ', None),
         ('if self.net is None: return img, "YOLO Model Not Loaded"', 'c'),
         (' — is what turns that state into a message you can read. Defensive '
          'code is not paranoid; it is the difference between a bug report and a '
          'blank screen.', None)],
    ], h=2.4)

    # ======================================================= 29. STEP 8 ===
    s = add()
    title(s, [('Step 8', None)])
    body(s, Y_BODY_STD, [
        [('The label file is a plain text list, one class name per line, eighty '
          'lines long. Read it into a list:', None)],
    ])
    code(s, 6.6, [
        'self.classes = []',
        'if os.path.exists(labels_path):',
        '    with open(labels_path, "r") as f:',
        '        self.classes = [line.strip() for line in f if line.strip()]',
    ], size=13.5)
    body(s, 10.6, [
        [('Same defensive shape as Step 7: start empty, then fill it if the file '
          'exists. The program runs without labels rather than not at all.', None)],
        None,
        [('with open(...)', 'c'),
         (' guarantees the file handle is closed afterwards, even if something '
          'inside goes wrong. Forget the ', None),
         ('with', 'c'),
         (' and you have a resource leak you will hardly notice.', None)],
        None,
        [('The comprehension keeps each line, strips it, and skips blanks. ', None),
         ('strip()', 'c'),
         (' matters — a stray newline makes labels look right in the file and '
          'print with a space on screen.', None)],
    ])

    # ======================================================= 30. STEP 9 ===
    s = add()
    title(s, [('Step 9', None)])
    body(s, Y_BODY_STD, [
        [('First use of the markers in this project. Detect them and store the two '
          'centre points:', None)],
    ])
    code(s, 6.6, [
        'frame_contiguous = np.ascontiguousarray(frame, dtype=np.uint8)',
        'try:',
        '    gray = cv2.cvtColor(frame_contiguous, cv2.COLOR_BGR2GRAY)',
    ], size=13.5)
    body(s, 9.3, [
        [('np.ascontiguousarray', 'c'),
         (' packs the picture so OpenCV’s fast routines accept it; then the same ', None),
         ('if self.use_new_aruco', 'c'),
         (' branch as Step 5, wrapped in a ', None),
         ('try', 'c'),
         (' because a half-hidden marker can throw.', None)],
    ], size=18.0)
    code(s, 12.4, [
        'if ids is not None and len(corners) >= 2:',
        '    p1 = corners[0][0]',
        '    p2 = corners[1][0]',
        '    self.x1, self.y1 = int(p1[:, 0].mean()), int(p1[:, 1].mean())',
        '    self.x2, self.y2 = int(p2[:, 0].mean()), int(p2[:, 1].mean())',
        '    return True',
    ], size=13.0)
    note(s, 15.0, [
        [('Note ', None), ('>= 2', 'c'),
         (', not ', None), ('> 0', 'c'),
         (': two markers make a rectangle; one does not. The return value tells '
          'the caller whether the stored coordinates are trustworthy.', None)],
    ], h=1.9)

    # ======================================================= 31. STEP 10 ===
    s = add()
    title(s, [('Step 10', None)])
    body(s, Y_BODY_STD, [
        [('Now crop to the workspace. First enlarge, then cut:', None)],
    ])
    code(s, 6.0, [
        'fx, fy = 1.5, 1.5',
        'resized = cv2.resize(frame, (0, 0), fx=fx, fy=fy, interpolation=cv2.INTER_CUBIC)',
    ], size=12.0)
    body(s, 8.8, [
        [('The crop happens in the enlarged picture, so the marker coordinates '
          'from Step 9 are scaled by 1.5 to match. ', None),
         ('INTER_CUBIC', 'c'),
         (' is a better-looking way to resize than the default, and it matters more '
          'than you would expect — a soft, blocky object is harder for the model '
          'to recognise.', None)],
    ])
    code(s, 12.4, [
        'margin = 25',
        'x_min, x_max = x_min + margin, x_max - margin',
        'y_min, y_max = y_min + margin, y_max - margin',
    ], size=13.0)
    body(s, 15.2, [
        [('The margin pulls the edges inward so the black marker borders stay '
          'outside the picture. Crop too tightly and the model sees a black frame '
          'around every object — which it may confidently identify as a picture '
          'frame or a window.', None)],
    ])

    # ============================================= 32. STEP 11 (YOLO METHOD) ===
    s = add()
    title(s, [('Step 11', None)])
    body(s, Y_BODY_STD, [
        [('This TODO has no code of its own — it is the method that the next five '
          'TODOs fill in. Read the scaffolding you have been given:', None)],
    ])
    code(s, 6.6, [
        'if img is None or img.size == 0:',
        '    return img, "No Frame"',
        '',
        'if self.net is None:',
        '    return img, "YOLO Model Not Loaded"',
        '',
        'img_h, img_w = img.shape[:2]',
    ], size=13.5)
    body(s, 11.4, [
        [('Two guards and a measurement. ', None),
         ('shape[:2]', 'c'),
         (' gives height and width only, and you will need both on this slide’s '
          'remaining steps to scale the boxes back.', None)],
        None,
        [('The two guards are the ones from Steps 7 and 8 doing their job. Notice '
          'that they return ', None),
         ('img', 'c'),
         (' unchanged rather than ', None),
         ('None', 'c'),
         (' — so the caller still has a picture to display, with an honest message '
          'beside it instead of a blank window.', None)],
    ])
    note(s, 15.4, [
        [('"No Frame"', 'c'), (', ', None), ('"YOLO Model Not Loaded"', 'c'),
         (' and ', None), ('"Searching..."', 'c'),
         (' — the three states; learn them on sight.', None)],
    ], h=2.2)

    # ======================================================= 33. STEP 12 ===
    s = add()
    title(s, [('Step 12', None)])
    body(s, Y_BODY_STD, [
        [('Preprocessing, already covered. Four settings, all properties of the '
          'model rather than of your program:', None)],
    ])
    code(s, 6.6, [
        'blob = cv2.dnn.blobFromImage(',
        '    img, 1.0 / 255.0, self.input_size, [0, 0, 0], swapRB=True, crop=False',
        ')',
        'self.net.setInput(blob)',
    ], size=12.5)
    note(s, 11.4, [
        [('input_size', 'c'),
         (' is (640, 640) — a ', None),
         ('square', 'i'),
         (', set way back in the constructor. Your cropped workspace is almost '
          'certainly not square, and it does not need to be: the resize squashes '
          'it. The model does not know or care what your object’s real proportions '
          'were.', None)],
    ], h=2.6)
    body(s, 14.2, [
        [('That last point has a consequence worth stating plainly. If you squash '
          'a tall thin object into a square, it arrives distorted — and a '
          'sufficiently distorted object can fall outside what the model was '
          'trained on. Distant or badly framed objects fail here, and it looks '
          'like a detection problem rather than a framing one.', None)],
    ])

    # ======================================================= 34. STEP 13 ===
    s = add()
    title(s, [('Step 13', None)])
    body(s, Y_BODY_STD, [
        [('The forward pass — the one line that costs about a hundred '
          'milliseconds:', None)],
    ])
    code(s, 5.8, [
        'outputs = self.net.forward(self.net.getUnconnectedOutLayersNames())',
    ], size=13.0)
    body(s, 8.2, [
        [('Then two lines of tidying before you read anything:', None)],
    ])
    code(s, 10.4, [
        'predictions = outputs[0]',
        'if len(predictions.shape) == 3:',
        '    predictions = predictions[0]',
    ], size=13.5)
    body(s, 13.6, [
        [('The model returns its answer in batches, and you only ever send it one '
          'picture at a time. ', None),
         ('[0]', 'c'),
         (' takes the first — and only — batch, leaving a three-dimensional array: '
          'one row per candidate position.', None)],
        None,
        [('The ', None),
         ('if', 'c'),
         (' is defensive again, and it earns its place. Library return shapes '
          'change between versions, and this program is already written to survive '
          'two different OpenCV layouts.', None)],
    ])

    # ======================================================= 35. STEP 14 ===
    s = add()
    title(s, [('Step 14', None)])
    body(s, Y_BODY_STD, [
        [('The longest TODO in the project, and the one worth slowing down for. '
          'Read the row layout again, then walk this loop:', None)],
    ])
    code(s, 7.2, [
        'for row in predictions:',
        '    confidence = row[4]',
        '    if confidence > self.conf_thresh:',
        '        scores = row[5:]',
        '        class_id = np.argmax(scores)',
        '        if scores[class_id] > self.score_thresh:',
    ], size=13.0)
    body(s, 12.0, [
        [('Three rows are skipped, three more are skipped, and only then does a '
          'row become a detection. ', None),
         ('row[4]', 'c'),
         (' is objectness; ', None),
         ('row[5:]', 'c'),
         (' is every class score from index 5 onwards; ', None),
         ('np.argmax', 'c'),
         (' returns the position of the highest one, which is the class id as a '
          'plain integer.', None)],
        None,
        [('Notice the gates are ', None),
         ('nested', 'b'),
         (', not combined with ', None), ('and', 'c'),
         ('. That means a row failing the objectness test never even has its class '
          'scores examined — which is what you want, because it is the cheaper test '
          'and it discards almost everything.', None)],
    ])

    # ================================================= 36. STEP 14 (CONT) ===
    s = add()
    title(s, [('Step 14, continued', None)])
    body(s, Y_BODY_STD, [
        [('Inside both gates, four numbers become a box in real pixels:', None)],
    ])
    code(s, 6.0, [
        'cx, cy, w, h = row[0], row[1], row[2], row[3]',
        'left = int((cx - w / 2.0) * x_factor)',
        'top = int((cy - h / 2.0) * y_factor)',
        'width = int(w * x_factor)',
        'height = int(h * y_factor)',
    ], size=13.5)
    body(s, 10.4, [
        [('The model gives you a centre and a size. A rectangle needs a corner and '
          'a size, so subtracting half the width and height is how you convert — '
          'and it is the step people most often get wrong by half a box.', None)],
        None,
        [('The ', None),
         ('x_factor', 'c'),
         (' and ', None),
         ('y_factor', 'c'),
         (' are the ratio between the model’s 640-space and your actual cropped '
          'picture, computed before the loop. Both are separate because your image '
          'is not square, and using one factor for both squashes every box.', None)],
    ])
    note(s, 15.0, [
        [('If every box is drawn but none land in the right place, the usual '
          'cause is skipping the scaling — numbers that look right but belong to '
          'a 640x640 picture that is not on screen.', None)],
    ], h=2.2)

    # ======================================================= 37. STEP 15 ===
    s = add()
    title(s, [('Step 15', None)])
    code(s, 4.8, [
        'indices = cv2.dnn.NMSBoxes(boxes, confidences, self.score_thresh, self.nms_thresh)',
    ], size=12.5)
    body(s, 7.6, [
        [('One line, and it does the tidying. Note what is passed in: the boxes, '
          'the confidences that produced them, and two thresholds — the score '
          'threshold again, then the overlap threshold.', None)],
        None,
        [('What comes back is a list of the boxes that survived:', None)],
    ])
    code(s, 11.4, [
        'if len(indices) == 0:',
        '    return img, "Searching..."',
        '',
        'if isinstance(indices, tuple) or len(indices.shape) > 1:',
        '    indices = indices.flatten()',
    ], size=12.5)
    body(s, 15.4, [
        [('Different versions return a tuple or array; ', None),
         ('flatten', 'c'),
         (' makes it indexable with an integer.', None)],
        None,
        [('Returning ', None),
         ('"Searching..."', 'c'),
         (' keeps the terminal quiet while you hold an object the model does not '
          'know.', None)],
    ])

    # ======================================================= 38. STEP 16 ===
    s = add()
    title(s, [('Step 16', None)])
    body(s, Y_BODY_STD, [
        [('The last TODO inside the method. Turn surviving indices into a picture '
          'you can read:', None)],
    ])
    code(s, 6.4, [
        'for idx in indices:',
        '    left, top, width, height = boxes[idx]',
        '    cx, cy = left + width // 2, top + height // 2',
    ], size=13.5)
    body(s, 9.4, [
        [('One line worth pausing on. This one is long, and it is the only place '
          'in the project where the label file is actually consulted:', None)],
    ])
    code(s, 11.6, [
        '            class_name = self.classes[class_ids[idx]] if class_ids[idx] < len(self.classes) else str(class_ids[idx])',
    ], size=codefit(['            class_name = self.classes[class_ids[idx]] if class_ids[idx] < len(self.classes) else str(class_ids[idx])']))
    body(s, 13.4, [
        [('Read it as a question: ', None),
         ('if this id is inside the list of names, use the name; otherwise use the '
          'number itself', 'b'),
         ('. A box labelled ', None),
         ('37', 'c'),
         (' instead of ', None),
         ('toothbrush', 'c'),
         (' means the labels did not load.', None)],
    ])
    note(s, 16.4, [
        [('Then ', None),
         ('label = f"{class_name} {confidences[idx]:.2f}"', 'c'),
         (' builds the label and ', None),
         ('detected_names.append(label)', 'c'),
         (' collects it for the terminal. ', None),
         ('.2f', 'c'),
         (' is two decimal places — 0.8734 becomes ', None),
         ('0.87', 'c'), ('.', None)],
    ], h=2.0)

    # ======================================================= 39. STEP 17 ===
    s = add()
    title(s, [('Step 17', None)])
    body(s, Y_BODY_STD, [
        [('The camera scan, unchanged since Project 1:', None)],
    ])
    code(s, 5.6, [
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
    note(s, 12.4, [
        [('Worth noticing: this function opens a plain ', None),
         ('cv2.VideoCapture', 'c'),
         (' and immediately closes it, purely to test the index. The threaded '
          'camera you use for the rest of the program is a different object. '
          'Testing with one kind and running with another is normal, and worth '
          'naming so it does not confuse you later.', None)],
    ], h=2.4)

    # ======================================================= 40. STEP 18 ===
    s = add()
    title(s, [('Step 18', None)])
    body(s, Y_BODY_STD, [
        [('The biggest blank in the file — this TODO is the whole of ', None),
         ('main()', 'c'),
         (', from the camera onwards. Build it in three pieces rather than all at '
          'once, and this is piece one:', None)],
    ])
    code(s, 6.6, [
        'cap_num = find_working_camera()',
        'if cap_num is None:',
        '    print("Error: No working camera stream found.")',
        '    return',
        '',
        '# Replace standard cv2.VideoCapture with ThreadedCamera',
        'cap = ThreadedCamera(cap_num)',
        'if not cap.isOpened():',
        '    print("Error: Could not open camera.")',
        '    return',
    ], size=13.0)
    body(s, 12.4, [
        [('Everything up to ', None),
         ('while True:', 'c'),
         (' is already written in the starter — the creation, the checks, and the '
          'object you will call ', None),
         ('vision', 'c'),
         (' on.', None)],
        None,
        [('The point of the project sits in one line: ', None),
         ('cap = ThreadedCamera(cap_num)', 'c'),
         (' instead of ', None),
         ('cv2.VideoCapture', 'c'),
         ('.', None)],
    ])
    note(s, 16.4, [
        ('The threaded camera is already written for you in the starter — your '
         'job is to use it and understand it.', None),
    ], h=1.9)

    # ======================================================= 41. STEP 19 ===
    s = add()
    title(s, [('Step 19', None)])
    body(s, Y_BODY_STD, [
        [('Three small TODOs left, all inside the loop, and all one line each. '
          'This first one refreshes the workspace bounds:', None)],
    ])
    code(s, 7.0, [
        'vision.calculate_aruco_bounds(frame)',
    ], size=15.0)
    body(s, 9.2, [
        [('Called every frame, which sounds wasteful — the markers have not moved. '
          'It is cheap, and it is worth it, because it means the workspace follows '
          'the board if anybody nudges it. Cheap and every frame beats clever and '
          'once.', None)],
        None,
        [('Then the crop, using whatever bounds the call above just found:', None)],
    ])
    code(s, 13.4, [
        'cropped_frame = vision.transform_frame(frame)',
    ], size=15.0)
    note(s, 15.8, [
        [('If the markers are not both visible, ', None),
         ('calculate_aruco_bounds', 'c'),
         (' returns ', None),
         ('False', 'c'),
         (' and leaves the old coordinates in place. ', None),
         ('transform_frame', 'c'),
         (' then falls back to the whole enlarged picture rather than failing. That '
          'fallback is deliberate: the model still works, it just sees more than '
          'it should.', None)],
    ], h=2.4)

    # ======================================================= 42. STEP 20 ===
    s = add()
    title(s, [('Step 20', None)])
    body(s, Y_BODY_STD, [
        [('The call that does the work:', None)],
    ])
    code(s, 5.8, [
        'display_frame, log_info = vision.yolo_detect(cropped_frame)',
    ], size=15.0)
    body(s, 8.2, [
        [('Same shape as every project in this module: two return values, unpacked '
          'into two names. One for the window, one for the terminal.', None)],
        None,
        [('The terminal line below it is already written, and it is filtered the '
          'same way as before:', None)],
    ])
    code(s, 11.4, [
        'if "Searching" not in log_info and "No Frame" not in log_info:',
        '    print(f"\\r[YOLOv5] {log_info}", end="")',
    ], size=13.0)
    note(s, 14.8, [
        [('Notice what is ', None),
         ('not', 'i'),
         (' filtered out. ', None),
         ('"YOLO Model Not Loaded"', 'c'),
         (' deliberately passes through this test and prints, because it is the one '
          'message you must never miss. Filtering on two specific strings leaves '
          'room for the rest to speak.', None)],
    ], h=2.4)

    # ======================================================= 43. STEP 21 ===
    s = add()
    title(s, [('Step 21', None)])
    body(s, Y_BODY_STD, [
        [('The final TODO. Show the picture:', None)],
    ])
    code(s, 5.8, [
        'if display_frame is not None and display_frame.size > 0:',
        '    cv2.imshow("YOLOv5 Object Detection", display_frame)',
    ], size=14.0)
    body(s, 9.0, [
        [('Identical in shape to Project 2, with a different window title. That '
          'title is the first thing to look for when the program seems to be doing '
          'nothing, so name it after what is in the window.', None)],
        None,
        [('Then the shutdown, which for this project means stopping a thread as '
          'well as closing a camera:', None)],
    ])
    code(s, 12.4, [
        'cap.release()',
        'cv2.destroyAllWindows()',
    ], size=14.0)
    note(s, 14.6, [
        [('Because ', None),
         ('cap', 'c'),
         (' is a ', None),
         ('ThreadedCamera', 'c'),
         (', ', None),
         ('release', 'c'),
         (' now stops the background thread before closing the camera — exactly '
          'the polite shutdown from the concepts section. ', None),
         ('cv2.destroyAllWindows()', 'c'),
         (' would not do it for you.', None)],
    ], h=2.2)

    # ================================================ 44. READING THE OUTPUT ===
    s = add()
    title(s, [('Reading the ', None), ('output', None)])
    code(s, 4.6, [
        'status_msg = f"Detected: {\', \'.join(detected_names)}"',
    ], size=15.0)
    body(s, 7.4, [
        [('One line listing everything currently on the board:', None)],
    ])
    code(s, 9.0, [
        'Detected: cup 0.87, scissors 0.52',
    ], size=15.0)
    body(s, 11.4, [
        [('Every box on screen appears here as a name and a number. ', None),
         ('join', 'c'),
         (' glues a Python list into one readable string with commas and spaces — '
          'the kind of small detail that makes a log worth keeping.', None)],
        None,
        [('While nothing is recognised the line reads ', None),
         ('Searching...', 'c'),
         (', and if the model is missing it reads ', None),
         ('YOLO Model Not Loaded', 'c'),
         (' and keeps going. Learn those two by sight.', None)],
    ])
    note(s, 14.8, [
        [('The confidences are the whole subject of the next slide. A detection '
          'at 0.87 and one at 0.52 are both "Detected" — worth knowing the '
          'difference before you let an arm act.', None)],
    ], h=2.4)

    # ============================================== 45. FAULTS AND THRESHOLDS ===
    s = add()
    title(s, [('Before you tune ', None), ('anything', None)])
    table(s, 4.8, [
        ['Symptom', 'Most likely cause', 'Check'],
        ['YOLO Model Not Loaded', 'yolov5s.onnx not beside your script',
         'Copy the model across too'],
        ['Boxes labelled with numbers', 'coco.names missing or empty',
         'Check Step 8 ran'],
        ['Boxes in the wrong place', 'Boxes not scaled to the cropped image',
         'Re-read the x_factor step'],
        ['One object, several boxes', 'nms_thresh too high',
         'Lower it, 0.45 to 0.3'],
        ['Flickering on and off', 'conf_thresh too high for this object',
         'Lower it and log the values'],
        ['Box around the arm itself', 'The arm is in shot',
         'Fold it out of the picture'],
        ['Nothing, ever', 'Object is not one of the 80 classes',
         'Read the label list'],
    ], col_w=[7.2, 9.6, 7.2])
    note(s, 15.4, [
        [('Five of those seven are mistakes you can make in the first ten minutes '
          'and check in the first ten seconds. Read the list before you tune '
          'anything — several of these symptoms get worse as you lower thresholds, '
          'which is exactly the wrong direction.', None)],
    ], h=2.2)

    # ============================================= 46. THRESHOLD WORKED EXAMPLE ===
    s = add()
    title(s, [('What a threshold ', None), ('actually', None), (' costs', None)])
    body(s, Y_BODY_STD, [
        [('Before you change any number, write down what it costs you. There are '
          'three failure modes and they pull in different directions.', None)],
    ])
    table(s, 7.4, [
        ['If you...', 'You will see', 'And you will lose'],
        ['Lower conf_thresh', 'More detections overall', 'Real confidence in them'],
        ['Raise conf_thresh', 'Cleaner, steadier output', 'Faint or unusual objects'],
        ['Lower nms_thresh', 'One box per object', 'Two genuinely close objects'],
    ], col_w=[6.4, 9.2, 8.4])
    body(s, 12.4, [
        [('There is no setting that is right for every object on every board. The '
          'honest process is to choose numbers, write down what they got wrong, and '
          'change one at a time.', None)],
        None,
        [('Changing three thresholds at once and finding that the output looks '
          'better tells you nothing about which change did it. Change one, retest, '
          'record. That is the whole discipline.', None)],
    ])
    callout(s, 16.4, [
        ('A model will always answer, even when it is guessing. The thresholds are '
         'not there to make it right — they are there to make it honest.', None),
    ], h=2.0)

    # ================================================= 47. EXTENSION DIVIDER ===
    s = add(0, master=1)
    _, tf = textbox(s, 14.22, 2.29, 12.70, 11.68)
    para(tf, True, '1', F_TITLE, 260.0, PANEL2, align=2)  # CENTER
    _, tf = textbox(s, X_L, 15.80, 24.89, 1.68)
    para(tf, True, 'EXTENSION 1', F_TITLE, 32.0, YELLOW)
    _, tf = textbox(s, X_L, 17.58, 24.89, 1.83)
    para(tf, True, 'REJECT, DO NOT GUESS', F_TITLE, 34.0, WHITE)

    # ========================================================= 48. BRIEF ===
    s = add(0, master=1)
    title(s, [('THE ', None), ('BRIEF', None)], ext=True)
    body(s, Y_BODY_EXT, [
        'Your program currently trusts every box it draws. A real machine cannot '
        'afford to act on a guess.',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    body(s, 6.6, [
        'Add the discipline a detection system needs before it is allowed to move '
        'anything: a confidence gate, a rule about agreement over time, and a '
        'record of everything it refused.',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    callout(s, 10.5, 'A system that says “I am not sure” is far more useful to '
                     'an engineer than one that never does. Your job is to earn '
                     'the right to act.', h=2.44)

    # ========================================================= 49. MISSION ===
    s = add(0, master=1)
    title(s, [('YOUR MISSION: ', None), ('REJECT, DO NOT GUESS', None)], ext=True)
    body(s, Y_BODY_EXT, [
        'Turn a confident-looking detector into one you would let near an arm.',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    items = [
        ('Set your own accept threshold',
         [('Pick a confidence you are willing to act on and write down why. Then '
           'find the lowest number that still catches every object on your board '
           'without false positives. One number, defended in a sentence.', None)]),
        ('Demand agreement over time',
         [('A single frame can lie. Require the same class, in roughly the same '
           'place, on two or three consecutive frames before you accept it. This is '
           'the single cheapest accuracy improvement available to you, and it is '
           'how real detection systems avoid acting on a flicker.', None)]),
        ('Log every rejection',
         [('Record what you refused and why — low confidence, changed class, moved '
           'too far. Ten minutes of logs shows which objects the model finds '
           'hardest.', None)]),
        ('Hand it over',
         [('Write the handover page: your accept threshold, your agreement rule, '
           'what the rejection log told you, and one improvement you would add.', None)]),
    ]
    for i, (h, b) in enumerate(items):
        num_item(s, 5.3 + i * 3.0, i + 1, h, b, h=2.1)
    callout(s, 17.0, 'Implement your gate in the decision logic, not by raising a '
                     'threshold until the noise disappears. One hides the '
                     'symptom; the other records the problem.', h=2.44)

    # ======================================================== 50. DATA LOG ===
    s = add(0, master=1)
    title(s, [('YOUR ', None), ('DATA LOG', None)], ext=True)
    body(s, Y_BODY_EXT, [
        'Record what the model said before you decide what to believe. Include '
        'the detections you rejected.',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    table(s, 5.5, [
        ['Object', 'Confidence', 'Accepted?', 'Why / what happened'],
        ['cup', '', '', ''],
        ['scissors', '', '', ''],
        ['cellphone', '', '', ''],
        ['my printed shape', '', '', ''],
    ], col_w=[5.6, 4.4, 4.0, 10.0])
    body(s, 12.3, [
        'Then write your acceptance rule before you code it:',
    ], ext=True, size=17.0, w=W_WIDE, ls=1.22)
    code(s, 13.8, [
        'ACCEPT if confidence >= ______  AND same class on ______ frames',
        'REJECT if class changed from ______ to ______',
        'OTHERWISE                             ______________',
    ], size=14.0)
    callout(s, 16.6, 'A rule you cannot say out loud is a rule you have not '
                     'decided yet.', h=2.2)

    # ================================================ 51. DEFINITION OF DONE ===
    s = add(0, master=1)
    title(s, [('DEFINITION OF ', None), ('DONE', None)], ext=True)
    dones = [
        [('The model loaded from a file sitting beside your script, with no '
          'error messages on screen', None)],
        [('Workspace cropped between both markers, from three different camera '
          'positions', None)],
        [('At least three different objects from the 80 classes detected, named '
          'correctly, from several distances', None)],
        [('Your accept threshold chosen, written down, and defended in one '
          'sentence', None)],
        [('Rejection log collected over ten minutes of running, and read', None)],
    ]
    for i, t in enumerate(dones):
        check_item(s, 4.4 + i * 2.5, t, h=2.2)

    # ======================================================= 52. GO FURTHER ===
    s = add(0, master=1)
    title(s, [('GO ', None), ('FURTHER', None)], ext=True)
    more = [
        [('Track position over time. ', None),
         ('The centre dot already gives you a coordinate. Store a few frames of '
          'it and you have measured how much your detection jitters — which is the '
          'number that decides whether an arm can safely act on it.', None)],
        [('Compare the small model against a larger one. ', None),
         ('The larger model is more accurate and too slow here. Find out how much '
          'too slow, and where the trade-off would change if the arm were not '
          'using the CPU for anything else.', None)],
        [('Report every class, not just the best one. ', None),
         ('Right now you keep the highest scoring class per detection. Show the '
          'runner-up too and you can see how close a decision actually was.', None)],
        [('Make it work on a different board. ', None),
         ('Swap in the laptop, the water bottle, the book. Which ones work without '
          'any code change, and which needed a threshold you would rather not have '
          'set?', None)],
    ]
    for i, t in enumerate(more):
        bullet(s, 4.6 + i * 3.2, t, h=2.9)

    # ======================================================== 53. DEBRIEF ===
    s = add(0, master=1)
    title(s, [('MISSION ', None), ('DEBRIEF', None)], ext=True)
    qs = [
        'You lower conf_thresh and get more detections. How would you tell a real '
        'new object from a false positive, using only the numbers on screen?',
        [('The model returns a box around a ', None), ('toothbrush', 'c'),
         (' with a confidence of 0.46, just over your threshold. Should the arm '
          'move? Defend your answer.', None)],
        [('Why does the program scale boxes with two separate factors, ', None),
         ('x_factor', 'c'), (' and ', None), ('y_factor', 'c'),
         (', instead of one?', None)],
        'This project could tell you what something is but not how far away it was. '
        'What would you have to bring back from Project 2 to close that gap?',
    ]
    for i, q in enumerate(qs):
        question_item(s, 4.6 + i * 3.3, i + 1, q)

    # ------------------------------------------------------- layout pass ---
    tight = pack_deck(prs, gap=0.30, limit=Y_BOTTOM)
    if tight:
        print('OVERFLOW:', tight)

    prs.save(OUT)
    print(f'wrote {OUT} with {len(prs.slides._sldIdLst)} slides')


if __name__ == '__main__':
    build()
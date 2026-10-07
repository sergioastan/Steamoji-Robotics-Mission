# -*- coding: utf-8 -*-
"""Build Slides/M2/myCobot_08.pptx -- 'The Capstone' (M2-P8).

The naming clash is unavoidable: the module's capstone is Project 8, and the
Google Slides reference template is also called myCobot_08.pptx. The reference
is read from Slides/myCobot_08.pptx and the output is written to
Slides/M2/myCobot_08.pptx; they are different directories and the builder
removes the output before saving so the reference can never overwrite itself.

Ordering rule: concepts first, then all thirteen steps, then the correction
section. Nothing in the concept section refers to a line number.

Every code snippet is copied verbatim from M2/M2-P8-Base.py, except the two
shell commands, the console output, the "before" listings in the correction
section (labelled as such), and the worksheet blanks.
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
    Y_TITLE_STD, Y_TITLE_EXT, Y_BODY_STD, Y_BODY_EXT, Y_BOTTOM,
    SZ_BODY, SZ_CODE, SZ_DIVIDER,
    textbox, para, title, body, note, code, command,
    callout, bullet, num_item, check_item, question_item, table,
    pack_deck,
)

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'Slides', 'myCobot_08.pptx')
OUT = os.path.join(HERE, 'Slides', 'M2', 'myCobot_08.pptx')
TMP = os.path.join(HERE, 'tmp_media')

STARTER = 'M2-P8-Starter.py'
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
    para(tf, True, 'Project 8', F_TITLE, SZ_DIVIDER, YELLOW, line_spacing=1.0)
    para(tf, False, 'The Capstone', F_TITLE, SZ_DIVIDER, WHITE, line_spacing=1.0)

    # ================================================== 3. WHAT THIS BUILDS ===
    s = add()
    title(s, [('What this project builds', None)])
    body(s, Y_BODY_STD, [
        [('Everything from the last seven projects, in one file. The camera reads '
          'the board. A function decides the move. The arm picks a token off a '
          'supply rack, carries it across, and places it in the right cell. Then '
          'it goes back and does it again.', None)],
        [('This is the project where the vision stops being a display and starts '
          'being an input to a machine that moves.', None)],
    ])
    bullet(s, 9.8, [
        ('Project 7 gave you a function', 'b'), ('  — ', None),
        ('parse_board_state', 'c'), (' — that reads nine cells. It is in this file, '
         'nearly unchanged.', None),
    ], h=2.2)
    bullet(s, 12.2, [
        ('This project adds a decision', 'b'), ('  — which cell, and a winner test '
         'that has to be fast enough to run on every frame.', None),
    ], h=2.2)
    bullet(s, 14.6, [
        ('And an actuator', 'b'), ('  — a suction pump, because picking up a flat '
         'token off a rack needs something that can grip.', None),
    ], h=2.2)
    callout(s, 17.4, [
        ('346 lines. Thirteen TODOs. One file that has to start up, read a board, '
         'think, move, and clean up after itself — and it is the last thing you '
         'write before the module ends.', None),
    ], h=2.4)

    # ======================================================= 4. THE LOOP ===
    s = add()
    title(s, [('The loop that decides everything', None)])
    body(s, Y_BODY_STD, [
        [('The main loop is doing more than the previous ones, and it is worth '
          'holding all of it in your head before you start typing:', None)],
    ])
    num_item(s, 7.4, 1, 'Read a frame',
             [('Same as Project 7. Nothing new.', None)], h=1.9)
    num_item(s, 9.3, 2, 'Read the board',
             [('Nine cells into nine characters.', None)], h=1.9)
    num_item(s, 11.2, 3, 'Check for a winner',
             [('Eight possible lines, tested every frame.', None)], h=1.9)
    num_item(s, 13.1, 4, 'Draw and show',
             [('The overlay, the status line, the window.', None)], h=1.9)
    num_item(s, 15.0, 5, 'Wait for a key',
             [('Space makes the robot move. q quits. Nothing happens without a '
               'keypress.', None)], h=1.9)
    note(s, 17.2, [
        [('Notice what is not on that list: the robot move is not a step in the '
          'loop. It happens inside the key handler, and it stops everything else '
          'while it runs. That single fact is the shape of this project.', None)],
    ], h=2.6)

    # ==================================================== 5. VISION IS GIVEN ===
    s = add()
    title(s, [('Vision is already here', None)])
    body(s, Y_BODY_STD, [
        [('This is the part you get to keep. The calibration constants and the '
          'whole of ', None), ('parse_board_state', 'c'),
         (' are copied straight out of Project 7:', None)],
    ])
    code(s, 6.8, [
        'GRID_SCALE = 0.75       # Scale factor for grid size (1.0 = original)',
        'GRID_OFFSET_X = -10     # Horizontal offset in pixels (+X = right)',
        'GRID_OFFSET_Y = -70     # Vertical offset in pixels (+Y = down)',
    ], size=10.5)
    body(s, 9.4, [
        [('Not one digit changed. If your Project 7 grid was right, this grid is '
          'right, and the calibration work you did last week still counts.', None)],
    ])
    callout(s, 12.0, [
        ('That reuse is the reason this project is possible. The vision half was '
         'already written, tested, and understood — which means you can spend all '
         'of this project on the parts that are new: the decision and the arm.',
         None),
    ], h=2.6)
    note(s, 15.0, [
        [('One difference: the two colour ranges are swapped in meaning. In '
          'Project 7 red was the human token. Here the constants say something '
          'else. Read them before you trust them.', None)],
    ], h=2.6)

    # ====================================================== 6. COLOUR FLIP ===
    s = add()
    title(s, [('The tokens changed colour', None)])
    body(s, Y_BODY_STD, [
        [('Same physical game pieces, different assignment. Project 7 used blue '
          'for the robot. This project uses red:', None)],
    ])
    code(s, 7.4, [
        "# Red Tokens = 'O' (Robot Player) - HSV wraps at 0/180",
        'LOWER_RED1 = np.array([0, 120, 100]); UPPER_RED1 = np.array([10, 255, 255])',
        'LOWER_RED2 = np.array([170, 120, 100]); UPPER_RED2 = np.array([180, 255, 255])',
        '',
        "# Green Tokens = 'X' (Human Player)",
        'LOWER_GREEN = np.array([40, 80, 80]); UPPER_GREEN = np.array([85, 255, 255])',
    ], size=9.0)
    body(s, 11.4, [
        [('The red ranges are identical to Project 7. The blue ranges are gone, '
          'replaced by green. So the hue wraparound you learned last week is '
          'still load-bearing — it just now belongs to the robot instead of the '
          'human.', None)],
    ])
    callout(s, 14.4, [
        ('Nothing in the code tells you which colour is which player. The comments '
         'do, and the comments are the only evidence. If you swap the two lines in ',
         None),
        ('parse_board_state', 'c'),
        (' the program will happily play a game where the robot thinks it is you.',
         None),
    ], h=3.0)
    note(s, 17.8, [
        [('This is worth noticing on purpose. Every constant in the file is a '
          'decision somebody made once, and nothing about it is self-evident from '
          'the code alone.', None)],
    ], h=2.4)

    # =================================================== 7. WHAT COUNTS A WIN ===
    s = add()
    title(s, [('Eight ways to win', None)])
    body(s, Y_BODY_STD, [
        [('A tic-tac-toe board has exactly eight winning lines: three rows, three '
          'columns, and two diagonals. That is the whole rule set, and the '
          'function that tests for a win is four lines long:', None)],
    ])
    code(s, 8.4, [
        'def check_winner(b):',
        '    """Checks for 3-in-a-row winning conditions."""',
        '    for i in range(3):',
        "        if b[i][0] == b[i][1] == b[i][2] != ' ': return b[i][0]",
        "        if b[0][i] == b[1][i] == b[2][i] != ' ': return b[0][i]",
        "    if b[0][0] == b[1][1] == b[2][2] != ' ': return b[0][0]",
        "    if b[0][2] == b[1][1] == b[2][0] != ' ': return b[0][2]",
        '    return None',
    ], size=10.5)
    body(s, 12.6, [
        [('The loop covers rows and columns together — ', None), ('i', 'c'),
         (' is the index, and each iteration checks one of each. Then two diagonals '
          'by hand, because they do not follow the pattern.', None)],
    ])
    note(s, 15.2, [
        [('Returning the winning character rather than ', None), ('True', 'c'),
         (' is deliberate. The main loop needs to know ', None), ('who', 'c'),
         (' won in order to print it on screen, and the string is already sitting '
          'there in the board.', None)],
    ], h=2.8)

    # ================================================ 8. THE CHAINED COMPARISON ===
    s = add()
    title(s, [('Read the comparison carefully', None)])
    body(s, Y_BODY_STD, [
        [('This line looks wrong to almost everybody the first time:', None)],
    ])
    code(s, 6.2, [
        "    if b[i][0] == b[i][1] == b[i][2] != ' ': return b[i][0]",
    ], size=13.0)
    body(s, 8.2, [
        [('There is no ', None), ('and', 'c'),
         (' in it, so how can it possibly mean what it appears to mean? Python '
          'chained comparisons compare each element with the next and with the '
          'final one. It means exactly:', None)],
    ])
    code(s, 11.4, [
        'b[i][0] == b[i][1]   and   b[i][1] == b[i][2]   and   b[i][2] != \' \'',
    ], size=10.5)
    callout(s, 14.0, [
        ('This is a correct piece of code. Three equal cells, and none of them '
         'blank — which is the part the ', None), ("!= ' '", 'c'),
        (' at the end is doing. Without it, three empty cells would count as a win '
         'for nobody, and the game would end on an empty board.', None),
    ], h=2.8)
    note(s, 17.4, [
        [('A chained comparison like this is easier to misread than to write. '
          'Nobody is required to use one, but everybody has to be able to read '
          'one correctly.', None)],
    ], h=2.2)

    # ============================================== 9. TRIAL AND UNDO ===
    s = add()
    title(s, [('Try it, then undo it', None)])
    body(s, Y_BODY_STD, [
        [('The AI has one job: find a cell to play. It does it by pretending, '
          'checking whether the pretend wins, and putting things back. Four lines '
          'of pretending:', None)],
    ])
    code(s, 7.6, [
        "    for player in ['O', 'X']:",
        '        for r in range(3):',
        '            for c in range(3):',
        "                if board[r][c] == ' ':",
        '                    board[r][c] = player',
        '                    if check_winner(board) == player:',
        '                        return (r, c)',
        "                    board[r][c] = ' ' # Undo",
    ], size=10.0)
    body(s, 11.8, [
        [('The outer loop is the important part. It tries ', None), ('O', 'c'),
         (' first, so the robot checks whether it can win before it checks whether '
          'it must block. Getting that order backwards produces a robot that '
          'blocks when it should be winning.', None)],
    ])
    callout(s, 15.4, [
        ('Those three nested loops, nine cells each, calling a winner test on every '
         'free square. Nine tries. Cheap. It runs once per keypress and there is '
         'no reason to be cleverer than this.', None),
    ], h=2.6)

    # ================================================== 10. PRIORITY, THEN FALLBACK ===
    s = add()
    title(s, [('Then centre, then anything', None)])
    body(s, Y_BODY_STD, [
        [('If no single move wins or blocks, the AI stops trying to be clever. '
          'Centre first, because it is on more winning lines than any corner, then '
          'whatever is left:', None)],
    ])
    code(s, 7.8, [
        '    # 2. Center priority',
        "    if board[1][1] == ' ':",
        '        return (1, 1)',
        '',
        '    # 3. Pick first open square',
        '    for r in range(3):',
        '        for c in range(3):',
        "            if board[r][c] == ' ':",
        '                return (r, c)',
        '    return None',
    ], size=11.5)
    body(s, 12.2, [
        [('The final ', None), ('None', 'c'), (' is a draw. No cells left, no winner, '
          'and the caller turns that into a message and stops.', None)],
    ])
    callout(s, 15.4, [
        ('This is a complete opponent in about twenty lines — not minimax, and '
         'happy to hand you a win if you play well.', None),
    ], h=2.6)
    note(s, 18.4, [
        [('Choosing the first open square means top-left whenever the centre is '
          'taken. Predictable, and occasionally punished.', None)],
    ], h=1.6)

    # ================================================= 11. NINE CELLS, HARD-CODED ===
    s = add()
    title(s, [('Nine cells, hard-coded', None)])
    body(s, Y_BODY_STD, [
        [('The vision half works in pixels. The arm half works in millimetres. '
          'Something has to connect them, and it is a dictionary of nine positions '
          'measured by hand:', None)],
    ])
    code(s, 7.4, [
        'CELL_COORDS = {',
        '    (0, 0): [120.5, -61.5, 138.4, 163.03, 8.84, -61.76], ...',
        '    (2, 2): [189.0, 46.0, 77.5, 177.55, -3.27, -84.59],',
        '}',
    ], size=10.5)
    body(s, 10.4, [
        [('The keys are ', None), ('(row, col)', 'c'),
         (' — the same coordinates the vision produces. The values are six numbers '
          'each: X, Y, Z, and three orientation angles.', None)],
    ])
    note(s, 13.2, [
        [('The Z values are the interesting ones. They are not level: the top row '
          'sits at Z 138, 123 and 96, and the bottom row is down near Z 78. The '
          'board is not flat, so every cell needs its own height.', None)],
    ], h=2.8)
    callout(s, 16.4, [
        ('This is a lookup table, and it is not a shortcut. It is the calibration '
         'for a specific arm on a specific table. It cannot be derived — it has to '
         'be measured, one cell at a time, with a real pen.', None),
    ], h=2.6)

    # ================================================== 12. HOVER, THEN PLACE ===
    s = add()
    title(s, [('Hover, then place', None)])
    body(s, Y_BODY_STD, [
        [('Every point in this file that uses ', None), ('send_coords', 'c'),
         (' is visited twice — once above the thing, once on it. The pattern is '
          'so consistent that it is worth memorising as a shape:', None)],
    ])
    code(s, 7.8, [
        '    # 2. Hover over target cell (higher Z, same orientation)',
        '    target_hover = [target_x, target_y, 150, target_rx, target_ry, target_rz]',
        '    mc.send_coords(target_hover, ARM_SPEED, 0)',
        '',
        '    # 3. Lower and release token (same orientation)',
        '    target_place = [target_x, target_y, target_z, target_rx, target_ry, target_rz]',
        '    mc.send_coords(target_place, ARM_SPEED, 0)',
    ], size=10.0)
    body(s, 12.0, [
        [('Hover is a fixed Z of 150. Place is the measured Z from the dictionary. '
          'Same X, same Y, same orientation both times — only the height changes, '
          'and only on the way down.', None)],
    ])
    callout(s, 15.2, [
        ('Moving sideways with a token held over the board is the expensive, '
         'slightly dangerous thing a robot arm does. Every "hover" in this file '
         'exists to make that move happen at a known, safe height.', None),
    ], h=2.6)

    # ==================================================== 13. ACTIVE LOW ===
    s = add()
    title(s, [('The pump is active low', None)])
    body(s, Y_BODY_STD, [
        [('This is the one piece of hardware whose logic is inverted relative to '
          'what you would guess. The docstring says it:', None)],
    ])
    code(s, 6.6, [
        '    """Controls suction pump via GPIO (1=ON, 0=OFF). Active LOW."""',
    ], size=11.0)
    body(s, 8.4, [
        [('Read those three claims together and they appear to contradict each '
          'other. Resolve it by trusting the last two words: the pin going LOW '
          'turns the pump on.', None)],
    ])
    code(s, 11.0, [
        '    if state == 1:',
        '        GPIO.output(20, 0)',
        '        GPIO.output(21, 0)',
        '    else:',
        '        GPIO.output(20, 1)',
        '        GPIO.output(21, 1)',
    ], size=13.0)
    callout(s, 14.6, [
        ('So asking for the pump to be ON writes a 0, and asking for it to be OFF '
         'writes a 1. The function keeps the human meaning ("1 means on") and '
         'absorbs the inversion in one place instead of at every call site.', None),
    ], h=2.8)
    note(s, 17.8, [
        [('Two pins, not one. That is a second pump or a second solenoid valve '
          'sharing the duty, and both are always driven together.', None)],
    ], h=1.8)

    # ================================================= 14. WHY IT MUST GO HOME ===
    s = add()
    title(s, [('Why it must go home', None)])
    body(s, Y_BODY_STD, [
        [('The move sequence ends with a return, and it is not tidiness:', None)],
    ])
    code(s, 6.4, [
        '    # 4. Return home to scan position',
        '    print("  Returning home...")',
        '    mc.send_coords(POS_HOME_CARTESIAN, ARM_SPEED, 0)',
    ], size=13.0)
    body(s, 9.0, [
        [('The camera can only see the board from the overhead home pose. If the '
          'arm stayed over cell (2, 2) after placing a token, the next frame would '
          'be of a hand and a token instead of a board.', None)],
    ])
    callout(s, 12.0, [
        ('This is a closed loop. The robot never records that it placed a token — it '
         'returns to the only viewpoint where it can verify its own work, and '
         'believes the camera. Every failure mode that creates is a real one.',
         None),
    ], h=2.8)
    note(s, 15.4, [
        [('It also explains the three-second sleep on that last move. It is the '
          'slowest approach in the file and the one where a collision would put the '
          'arm through the board.', None)],
    ], h=2.4)

    # ================================================== 15. THE SUPPLY RACK ===
    s = add()
    title(s, [('Tokens come from a rack', None)])
    body(s, Y_BODY_STD, [
        [('A tic-tac-toe game needs up to five O tokens, and they are not lying on '
          'the table — they are stacked in a rack the arm reaches into. Each pick '
          'goes one token deeper, so the height has to be computed:', None)],
    ])
    code(s, 8.0, [
        '    supply_z = POS_TOKEN_SUPPLY_BASE[2] - (tokens_picked * TOKEN_HEIGHT)',
        '    pos_token_supply = POS_TOKEN_SUPPLY_BASE.copy()',
        '    pos_token_supply[2] = supply_z',
    ], size=10.5)
    body(s, 10.8, [
        [('Token zero sits at Z 117. Every pick lowers the target by ', None),
         ('TOKEN_HEIGHT', 'c'), (' of 5mm. After four picks the arm is reaching 20mm '
          'further down the rack.', None)],
    ])
    callout(s, 13.6, [
        ('The ', None), ('.copy()', 'c'), (' matters. Mutating ', None),
        ('POS_TOKEN_SUPPLY_BASE', 'c'),
        (' in place would make the offset cumulative in the wrong direction — each '
         'pick would be measured from the last position instead of the rack base, '
         'and the arm would walk away from the tokens one pick at a time.', None),
    ], h=3.0)
    note(s, 17.0, [
        [('Five tokens is the most a full tic-tac-toe game needs, because the '
          'robot plays O and the human plays X. The rack does not have to be '
          'restocked mid-game.', None)],
    ], h=2.2)

    # ================================================= 16. EIGHTEEN SECONDS ===
    s = add()
    title(s, [('Eighteen seconds', None)])
    body(s, Y_BODY_STD, [
        [('Add up the sleeps in the pick-and-place sequence and you get something '
          'worth planning around:', None)],
    ])
    table(s, 6.8, [
        ['Move', 'Wait'],
        ['To supply hover', '3.0s'],
        ['Down into the rack', '2.5s'],
        ['Pump on (settle)', '1.0s'],
        ['Back to hover', '2.5s'],
        ['Across to target hover', '3.0s'],
        ['Lower into the cell', '1.5s'],
        ['Pump off (settle)', '1.0s'],
        ['Back to home', '3.0s'],
    ], [8.4, 3.2], row_h=0.95, head_h=1.1, size=13.0)
    body(s, 15.8, [
        [('Seventeen and a half seconds of sleeping, plus the pump\'s own 0.3s '
          'settle each time it is called. Call it ', None), ('18.1 seconds', 'y'),
         (' — and every one of them is a full stop in the game loop.', None)],
    ])
    callout(s, 18.4, [
        ('Nothing is drawn and nothing is checked during those eighteen seconds. '
         'The window is frozen and the program is deaf.', None),
    ], h=1.8)

    # ============================================ 17. WHAT "PRESS SPACE" MEANS ===
    s = add()
    title(s, [('What press space means', None)])
    body(s, Y_BODY_STD, [
        [('The robot does not move on a timer or when the board changes. It moves '
          'because a human pressed a key. That is the entire interaction model:', None)],
    ])
    code(s, 7.2, [
        '        key = cv2.waitKey(1) & 0xFF',
        '',
        "        if key == ord(' ') and not winner:",
        '            move = find_best_move(board)',
        '            if move:',
        '                execute_robot_move(move)',
    ], size=11.5)
    body(s, 11.4, [
        [('Four decisions in five lines. Which key was it. Is the game still '
          'running. Is there a move at all. Then do the thing. The ', None),
         ('and not winner', 'c'), (' guard is the one that stops the robot from '
          'playing onto a finished board.', None)],
    ])
    note(s, 14.6, [
        [('Because the move is triggered by a key rather than by a board change, '
          'the human is responsible for placing their X before pressing space. '
          'Press it on an unchanged board and the robot will play into whatever it '
          'sees.', None)],
    ], h=3.0)
    callout(s, 18.0, [
        ('This is the most fragile interface in the module and it was chosen for '
          'the simplest possible reason: it is easy to explain.', None),
    ], h=1.8)

    # ==================================================== 18. STARTUP ORDER ===
    s = add()
    title(s, [('Order of operations at startup', None)])
    body(s, Y_BODY_STD, [
        [('Before the loop runs, this file does a lot in a specific order, and the '
          'order is the whole difficulty:', None)],
    ])
    num_item(s, 7.6, 1, 'Connect, then read back',
             [('get_angles proves the arm is really there.', None)], h=1.9)
    num_item(s, 9.5, 2, 'Configure the pins',
             [('BCM mode, two output pins, both written OFF.', None)], h=1.9)
    num_item(s, 11.4, 3, 'Move to home angles',
             [('Then read where that turned out to be in millimetres.', None)], h=1.9)
    num_item(s, 13.3, 4, 'Open the camera',
             [('After the arm is out of the way.', None)], h=1.9)
    callout(s, 15.4, [
        ('Step 3 is the subtle one. The arm is told to go to a pose using joint '
         'angles, but the rest of the file works in Cartesian millimetres — so it '
         'asks where the arm ended up, and that answer becomes the home position '
         'every move returns to.', None),
    ], h=2.8)
    note(s, 18.6, [
        [('If the arm cannot get there, the handler installs a hard-coded fallback '
          'and the program carries on with a position nobody measured.', None)],
    ], h=1.8)

    # ============================================= 19. FALLBACK POSITIONS ===
    s = add()
    title(s, [('The fallback nobody measured', None)])
    body(s, Y_BODY_STD, [
        [('Every error handler in this file ends the same way — print, dump a '
          'traceback, and substitute a number:', None)],
    ])
    code(s, 6.8, [
        'except Exception as e:',
        '    print(f"Error moving to home: {e}")',
        '    import traceback',
        '    traceback.print_exc()',
        '    POS_HOME_CARTESIAN = [66, -62, 235, 180, 0, 90]  # fallback',
    ], size=11.0)
    body(s, 10.0, [
        [('So if the arm will not move to home, the program does not stop — it '
          'remembers a guess and carries on. Every robot move will then end with a '
          'return to coordinates that were never checked against the real arm.',
          None)],
    ])
    callout(s, 13.4, [
        ('This is defensible. A capstone that refuses to start is a capstone that '
          'teaches nothing. But notice the trade: the fallback converts a loud, '
          'obvious failure into a quiet, mechanical one, and the arm will be moved '
          'to the wrong place without complaint.', None),
    ], h=3.0)
    note(s, 17.0, [
        [('If you see a traceback during startup, read the fallback line as the '
          'explanation for whatever goes wrong later. The two are connected.', None)],
    ], h=2.2)

    # ============================================== 20. BEFORE YOU TYPE ANYTHING ===
    s = add()
    title(s, [('Before you type anything', None)])
    body(s, Y_BODY_STD, [
        [('The capstone starter does not run. Copy it across and start it and you '
          'get this:', None)],
    ])
    code(s, 6.4, [
        '  File "M2-P8-Starter.py", line 157',
        '    finally:',
        '        ^^^^^^^',
        'SyntaxError: invalid syntax',
    ], size=13.0)
    body(s, 9.6, [
        [('No output at all. Not one line printed, because the file never got as '
          'far as running anything.', None)],
    ])
    body(s, 11.6, [
        [('The reason is in the last few lines: the ', None),
         ('finally', 'c'), (' block is given to you, correct, but the ', None),
         ('try', 'c'),
         (' it belongs to is still an empty TODO, so the two keywords are not '
          'attached to anything.', None)],
    ])
    callout(s, 15.0, [
        ('Every other project in this module has started with a ', None),
        ('NameError', 'c'), (' — a runtime error, raised after the file was '
         'successfully loaded. This one is a ', None), ('SyntaxError', 'c'),
        (', which Python finds before running a single statement. It is a different '
         'category of problem, and it is the last thing this module asks you to '
         'notice on your own.', None),
    ], h=3.2)
    note(s, 18.8, [
        [('Read from the bottom up for this one. The error points at the last line '
          'of the file and the cause is fifty lines above it.', None)],
    ], h=1.6)

    # ==================================== 21. STEP 1 ===
    s = add()
    title(s, [('Step 1', None), ('  —  ', None), ('the four imports', 'y')])
    body(s, Y_BODY_STD, [
        [('Two TODOs at the top of the file. Four imports between them:', None)],
    ])
    code(s, 6.6, [
        'import cv2',
        'import numpy as np',
        'import time',
    ], size=14.5)
    code(s, 9.4, [
        'import RPi.GPIO as GPIO',
    ], size=14.5)
    code(s, 11.4, [
        'from pymycobot.mycobot280 import MyCobot280',
    ], size=13.0)
    bullet(s, 14.0, [
        ('RPi.GPIO', 'c'), ('  — the pin interface. This one only exists on a '
         'Raspberry Pi, which is why this project cannot be developed on a laptop.',
         None),
    ], h=2.1)
    bullet(s, 16.2, [
        ('The other three', 'c'), ('  — identical to every project since Project 1.',
         None),
    ], h=2.1)
    callout(s, 18.4, [
        ('Note what is absent: no import of the Project 7 functions — this file '
         'redefines ', None), ('parse_board_state', 'c'),
        (' because there is no module to import from.',
         None),
    ], h=2.0)

    # ==================================== 22. STEP 2 ===
    s = add()
    title(s, [('Step 2', None), ('  —  ', None), ('connect and verify', 'y')])
    body(s, Y_BODY_STD, [
        [('The capstone has no ', None), ('try', 'c'),
         (' block around the connection, so this is where a missing arm stops the '
          'program. The TODO asks for a read-back, which is what makes it safe:', None)],
    ])
    code(s, 8.2, [
        "mc = MyCobot280('/dev/ttyAMA0', 1000000)",
        'time.sleep(0.5)',
        '',
        '# Verify connection (M1 style - no explicit power_on)',
        'try:',
        '    angles = mc.get_angles()',
        '    print(f"Connected. Current angles: {angles}")',
        'except Exception as e:',
        '    print(f"Warning during init: {e}")',
    ], size=11.0)
    note(s, 12.4, [
        [('The half-second wait is the same one from Project 6 — the board needs '
          'time to boot before it will answer. And unlike Project 6 there is no ',
          None), ('power_on', 'c'), (' call: the comment says this is the Module 1 '
          'style, where the arm powers itself.', None)],
    ], h=3.0)
    callout(s, 15.8, [
        ('Read the try block carefully. It catches a failure to ', None), ('read', 'b'),
        (' the arm, not a failure to ', None), ('create', 'b'),
        (' it. If the constructor raises, this file is already over — there is no '
         'handler above it.', None),
    ], h=2.6)

    # ==================================== 23. STEP 3 ===
    s = add()
    title(s, [('Step 3', None), ('  —  ', None), ('set up the pins', 'y')])
    body(s, Y_BODY_STD, [
        [('Five lines. Three of them are configuration and two are the first thing '
          'the pins actually do:', None)],
    ])
    code(s, 6.6, [
        'GPIO.setwarnings(False)',
        'GPIO.setmode(GPIO.BCM)',
        'GPIO.setup(20, GPIO.OUT)',
        'GPIO.setup(21, GPIO.OUT)',
        'GPIO.output(20, 1)  # Off initially',
        'GPIO.output(21, 1)',
    ], size=13.0)
    body(s, 10.4, [
        [('Read those last two lines with Step 5 in mind. Writing ', None), ('1', 'c'),
         (' is what turns the pump ', None), ('off', 'b'),
         (', because the pump is active low. The comment is the whole explanation, '
          'and it is load-bearing.', None)],
    ])
    callout(s, 13.4, [
        ('BCM means "use the pin\'s broad-com-number", not its physical position on '
         'the board. The numbers 20 and 21 are what this file expects; a different '
          'wiring would need different numbers here and nowhere else.', None),
    ], h=2.8)
    note(s, 16.6, [
        [('Pins OFF before anything else runs: if the program crashes later, the '
          'pump is already in the safe state.', None)],
    ], h=2.4)

    # ==================================== 24. STEP 4 ===
    s = add()
    title(s, [('Step 4', None), ('  —  ', None), ('move home, then measure', 'y')])
    body(s, Y_BODY_STD, [
        [('The longest TODO in the file. Everything about the arm\'s coordinate '
          'system is decided here:', None)],
    ])
    code(s, 6.4, [
        'print(f"Moving to home angles: {POS_HOME_ANGLES}")',
        'try:',
        '    result = mc.send_angles(POS_HOME_ANGLES, ARM_SPEED)',
        '    time.sleep(4.0)',
        '    POS_HOME_CARTESIAN = mc.get_coords()',
        '    print(f"Home position (cartesian): {POS_HOME_CARTESIAN}")',
    ], size=10.5)
    body(s, 10.2, [
        [('Three ideas in five lines. Go to a pose using ', None), ('joint angles', 'b'),
         (', wait four seconds for it to get there, then ask ', None),
         ('where it ended up in millimetres', 'b'), (' and keep that answer.', None)],
    ])
    note(s, 13.4, [
        [('Two different coordinate systems, because the arm is told where to go one '
          'way and is asked where it is another way. The rest of the file is '
          'written in the second one.', None)],
    ], h=2.8)
    callout(s, 16.6, [
        ('The four-second sleep is not padding. It is the difference between '
          'reading the arm\'s position and reading the position it is still '
          'travelling to.', None),
    ], h=2.0)

    # ==================================== 25. STEP 5 ===
    s = add()
    title(s, [('Step 5', None), ('  —  ', None), ('the pump function', 'y')])
    body(s, Y_BODY_STD, [
        [('The first function you write in this project, and the shortest:', None)],
    ])
    code(s, 6.4, [
        'def set_pump(state):',
        '    """Controls suction pump via GPIO (1=ON, 0=OFF). Active LOW."""',
        '    if state == 1:',
        '        GPIO.output(20, 0)',
        '        GPIO.output(21, 0)',
        '    else:',
        '        GPIO.output(20, 1)',
        '        GPIO.output(21, 1)',
        '    time.sleep(0.3)',
    ], size=11.5)
    body(s, 10.6, [
        [('The inversion is the whole point. Callers say ', None), ('set_pump(1)', 'c'),
         (' to turn suction on and the function writes a ', None), ('0', 'c'),
         (' to the pin. Nothing above this function needs to know that.', None)],
    ])
    callout(s, 13.8, [
        ('The trailing sleep is why the move takes 18 seconds instead of 17.5. It is '
          'a settle time — the pump needs a moment to build suction before the arm '
          'pulls away.', None),
    ], h=2.4)
    note(s, 16.6, [
        [('This function is called four times per move. It is the only piece of '
          'shared state in the whole capstone, and it has to be defined before '
          'anything that calls it runs.', None)],
    ], h=2.4)

    # ==================================== 26. STEP 6 ===
    s = add()
    title(s, [('Step 6', None), ('  —  ', None), ('the board reader', 'y')])
    body(s, Y_BODY_STD, [
        [('You have written this before. It is here, and this is the whole of it:', None)],
    ])
    code(s, 6.4, [
        'def parse_board_state(frame):',
        '    """Scans all 9 cells and returns 3x3 matrix."""',
        "    board = [[' ' for _ in range(3)] for _ in range(3)]",
        '    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)',
    ], size=11.0)
    body(s, 9.8, [
        [('One structural difference from Project 7: the colour conversion happens '
          'once for the whole frame, before the cells are cut, so each cell is '
          'sliced from an already-converted array.', None)],
    ])
    code(s, 12.6, [
        '            m_red = cv2.bitwise_or(cv2.inRange(roi, LOWER_RED1, UPPER_RED1), cv2.inRange(roi, LOWER_RED2, UPPER_RED2))',
        '            m_green = cv2.inRange(roi, LOWER_GREEN, UPPER_GREEN)',
    ], size=8.0)
    body(s, 14.4, [
        [('Two masks, one threshold, two branches — and check the order. Green is '
          'tested first, then red, and each branch requires its colour to beat the '
          'other as well as beat 800 pixels.', None)],
    ])
    note(s, 16.8, [
        [('Note the hard-coded 800. Project 7 named it ', None), ('MIN_PIXELS', 'c'),
         ('; here it is a literal in two places. Same value, same cells, same '
          'meaning — but a value you have to change in two spots.', None)],
    ], h=2.4)

    # ==================================== 27. STEP 7 ===
    s = add()
    title(s, [('Step 7', None), ('  —  ', None), ('the AI', 'y')])
    body(s, Y_BODY_STD, [
        [('Three priorities, in order. The first is the only interesting one:', None)],
    ])
    code(s, 6.6, [
        'def find_best_move(board):',
        '    """Calculates AI move: Checks for win, block, or picks first empty space."""',
        "    for player in ['O', 'X']:",
        '        for r in range(3):',
        '            for c in range(3):',
        "                if board[r][c] == ' ':",
        '                    board[r][c] = player',
        '                    if check_winner(board) == player:',
        '                        return (r, c)',
        "                    board[r][c] = ' ' # Undo",
    ], size=9.5)
    body(s, 10.8, [
        [('Try to win as ', None), ('O', 'c'), (' first. Then, in the same loop, try '
          'to win as ', None), ('X', 'c'),
         (' — and since the human winning is the robot blocking, the second pass '
          'is the block. Undo every trial that fails.', None)],
    ])
    callout(s, 14.2, [
        ('It mutates the board you hand it, and undoes the trial only when the trial '
         'fails. On the move it returns, that cell keeps its value. It does not '
         'matter today because the board is re-read from the camera on the next '
         'frame — but this function is not safe to call twice on one board.', None),
    ], h=3.0)
    note(s, 17.8, [
        [('Nine empty cells, nine winner tests, two passes. Still under a '
          'millisecond, and it only runs when someone presses space.', None)],
    ], h=1.8)

    # ==================================== 28. STEP 8 ===
    s = add()
    title(s, [('Step 8', None), ('  —  ', None), ('the winner test', 'y')])
    body(s, Y_BODY_STD, [
        [('Eight lines, one loop, two diagonals. This is the function the AI calls '
          'nine times per pass:', None)],
    ])
    code(s, 6.8, [
        'def check_winner(b):',
        '    """Checks for 3-in-a-row winning conditions."""',
        '    for i in range(3):',
        "        if b[i][0] == b[i][1] == b[i][2] != ' ': return b[i][0]",
        "        if b[0][i] == b[1][i] == b[2][i] != ' ': return b[0][i]",
        "    if b[0][0] == b[1][1] == b[2][2] != ' ': return b[0][0]",
        "    if b[0][2] == b[1][1] == b[2][0] != ' ': return b[0][2]",
        '    return None',
    ], size=10.5)
    body(s, 11.4, [
        [('This one is called every single frame, not just on a keypress. That is '
          'nine cells to parse and eight lines to check, at whatever rate the '
          'camera delivers — and it still has time left over.', None)],
    ])
    callout(s, 14.6, [
        ('It is also the function that makes the game end honestly. Because it runs '
          'every frame, a win is detected the moment the ninth token lands — you '
          'never have to press anything to find out you won.', None),
    ], h=2.6)

    # ==================================== 29. STEP 9 ===
    s = add()
    title(s, [('Step 9', None), ('  —  ', None), ('pick and place', 'y')])
    body(s, Y_BODY_STD, [
        [('The longest function in the module, and it is almost all ', None),
         ('send_coords', 'c'), (' and ', None), ('time.sleep', 'c'), ('.', None)],
    ])
    code(s, 6.4, [
        'def execute_robot_move(target_cell):',
        '    """Executes pick-and-place sequence to place an \'O\' token at target grid cell."""',
        '    global POS_HOME_CARTESIAN, tokens_picked',
        '    row, col = target_cell',
        '    target_coords = CELL_COORDS[(row, col)]',
        '    target_x, target_y, target_z = target_coords[0], target_coords[1], target_coords[2]',
    ], size=9.0)
    code(s, 10.0, [
        '    supply_z = POS_TOKEN_SUPPLY_BASE[2] - (tokens_picked * TOKEN_HEIGHT)',
        '    pos_token_supply = POS_TOKEN_SUPPLY_BASE.copy()',
        '    pos_token_supply[2] = supply_z',
        '    mc.send_coords(POS_TOKEN_HOVER, ARM_SPEED, 0)',
    ], size=9.0)
    body(s, 12.4, [
        [('Drop into the rack, pick, carry to the cell, lower, release, go home. '
          'The ', None),
         ('tokens_picked * TOKEN_HEIGHT', 'c'),
         (' part is how the rack lowers five millimetres per token.',
          None)],
    ])
    callout(s, 13.2, [
        ('This is the function that moves hardware. Everything else in the project '
         'is arithmetic and image processing. If this one is wrong, something is '
         'about to be dropped, or scraped, or both.', None),
    ], h=2.6)
    note(s, 16.2, [
        [('Two globals is not a design choice anyone would make twice. It is '
          'readable here because there are exactly two and both are declared in '
          'one line.', None)],
    ], h=2.0)

    # ==================================== 30. STEP 10 ===
    s = add()
    title(s, [('Step 10', None), ('  —  ', None), ('open the camera', 'y')])
    body(s, Y_BODY_STD, [
        [('Identical to Project 7. This is the point in the file where the vision '
          'half and the hardware half meet:', None)],
    ])
    code(s, 6.6, [
        'cap = cv2.VideoCapture(0)',
        'cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)',
        'cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)',
    ], size=13.5)
    note(s, 10.0, [
        [('Read the section header above it: ', None),
         ('3. MAIN GAME LOOP', 'c'), (', not "calibration". Everything from here '
          'down happens while the loop is running, which is why the camera is '
          'opened second and not first.', None)],
    ], h=2.8)
    callout(s, 13.4, [
        ('Between the calibration and this line sit five function definitions and '
         'the arm moving home. The camera is the last thing initialised so that the '
          'arm is already out of the way when the first frame is read.', None),
    ], h=2.6)

    # ==================================== 30b. THE OVERLAY ===
    s = add()
    title(s, [('Also in the loop', None), ('  —  ', None), ('what you see', 'y')])
    body(s, Y_BODY_STD, [
        [('Given code, but it is the part that makes the output readable. A white '
          'box per cell, then a letter inside it:', None)],
    ])
    code(s, 6.6, [
        '        # Draw grid overlay',
        '        for r in range(3):',
        '            for c in range(3):',
        '                x1 = GRID_X_MIN + c * CELL_W',
        '                y1 = GRID_Y_MIN + r * CELL_H',
        '                cv2.rectangle(frame, (x1, y1), (x1 + CELL_W, y1 + CELL_H), (255, 255, 255), 2)',
    ], size=8.5)
    body(s, 10.6, [
        [('The same arithmetic as ', None), ('parse_board_state', 'c'), (', reading '
          'the same constants. If the overlay and the reader ever disagree, you have '
          'your bug — and they cannot disagree, because both use ', None),
         ('GRID_X_MIN', 'c'), (' and ', None), ('CELL_W', 'c'), ('.', None)],
    ])
    callout(s, 13.8, [
        ('This is the projection step from Project 7. The board a human is looking '
         'at and the board being read are the same three rows in the same order — '
         'which is what lets a person and a robot agree about a square.', None),
    ], h=2.6)
    note(s, 17.0, [
        [('Colour note: ', None), ('(0, 255, 0)', 'c'), (' is green in BGR and ', None),
         ('(0, 0, 255)', 'c'), (' is red, so the code draws X in green and O in red, '
          'matching the thresholds the reader uses.', None)],
    ], h=2.2)

    # ==================================== 31. STEP 11 ===
    s = add()
    title(s, [('Step 11', None), ('  —  ', None), ('the game loop', 'y')])
    body(s, Y_BODY_STD, [
        [('The last and largest TODO. The parts you have already written:', None)],
    ])
    code(s, 6.6, [
        'try:',
        '    while cap.isOpened():',
        '        ret, frame = cap.read()',
        '        if not ret:',
        '            break',
        '',
        '        board = parse_board_state(frame)',
        '        winner = check_winner(board)',
    ], size=13.0)
    body(s, 10.6, [
        [('Two functions per frame. Parse the board, then test it for a winner. The '
          'winner is checked on every single iteration, which is why the game '
          'notices its own ending without being told.', None)],
    ])
    note(s, 13.6, [
        [('The ', None), ('if not ret', 'c'), (' guard is doing exactly what it did '
          'in Project 7. Two projects from the end of the module and the same three '
          'lines are still load-bearing.', None)],
    ], h=2.6)

    # ==================================== 31b. SHOW AND WAIT ===
    s = add()
    title(s, [('Step 11', None), ('  —  ', None), ('show the frame', 'y')])
    body(s, Y_BODY_STD, [
        [('The two lines that end the loop body, and they are where the program '
          'becomes interactive:', None)],
    ])
    code(s, 6.4, [
        '        cv2.imshow("Mission 02 Capstone - Tic-Tac-Toe AI", frame)',
        '        key = cv2.waitKey(1) & 0xFF',
    ], size=12.5)
    bullet(s, 9.4, [
        ('imshow', 'c'), ('  — draws ', None), ('frame', 'c'), (' in a named '
         'window. The name is the one thing you will see on the taskbar.', None),
    ], h=2.4)
    bullet(s, 11.8, [
        ('waitKey(1)', 'c'), ('  — waits one millisecond and returns the key code. '
         'The ', None), ('1', 'c'), (' is what makes this a loop instead of a freeze.',
         None),
    ], h=2.4)
    body(s, 14.4, [
        [('These two lines come ', None), ('after', 'b'), (' all the processing, and '
          'that order matters. Show, then wait, then go round again. Waiting first '
          'would put a stale board on screen for one frame every loop.', None)],
    ])
    callout(s, 17.2, [
        ('The one-millisecond wait also stops this loop pinning a CPU core; '
         'without it the frame redraws as fast as it can be read and the keyboard '
         'never gets a look in.', None),
    ], h=2.4)

    # ==================================== 32. STEP 12 ===
    s = add()
    title(s, [('Step 12', None), ('  —  ', None), ('read the keyboard', 'y')])
    body(s, Y_BODY_STD, [
        [('Mask the key code, then compare it. Two separate steps this time, which '
          'is the correct shape:', None)],
    ])
    code(s, 6.4, [
        '        key = cv2.waitKey(1) & 0xFF',
        '',
        '        if key != 255:',
        "            print(f\"Key pressed: {key} ({chr(key) if key < 128 else '?'})\")",
    ], size=11.5)
    body(s, 9.6, [
        [('The mask happens first and gets its own line, so the comparison below is '
          'a plain equality against a number. Compare that with how Project 7 '
          'needed parentheses, and you have the whole lesson in two versions.',
          None)],
    ])
    callout(s, 12.8, [
        ('The debug print fires whenever a key arrives. ', None), ('255', 'c'),
        (' is what ', None), ('waitKey', 'c'), (' returns when nothing was pressed, '
         'so that test means "a key was pressed" rather than "a key was q".', None),
    ], h=2.6)

    # ==================================== 33. STEP 13 ===
    s = add()
    title(s, [('Step 13', None), ('  —  ', None), ('act on it', 'y')])
    body(s, Y_BODY_STD, [
        [('The final TODO. Three branches, and the order of the conditions is the '
          'whole design:', None)],
    ])
    code(s, 6.6, [
        "        if key == ord(' ') and not winner:",
        '            print("SPACE pressed - calculating move...")',
        '            move = find_best_move(board)',
        '            if move:',
        '                print(f"Best move: {move}")',
        '                execute_robot_move(move)',
        '            else:',
        '                print("Game is a Draw!")',
        '',
        "        elif key == ord('q'):",
        '            break',
    ], size=11.0)
    body(s, 11.0, [
        [('The winner guard is on ', None), ('space', 'c'),
         (', not the whole loop, so q still works after a win. The draw case is '
          'handled explicitly rather than doing nothing.', None)],
    ])
    callout(s, 14.2, [
        ('One line does all the work: ', None), ('execute_robot_move(move)', 'c'),
        (' freezes everything for eighteen seconds. The print statements before it '
         'are the only record of what the robot decided and why — which is the same '
         'argument for evidence that Project 6 made.', None),
    ], h=2.8)
    note(s, 17.6, [
        [('And then the loop goes straight round and re-reads the board, because '
          'the robot does not write its own move anywhere. It has to look at it.',
          None)],
    ], h=2.0)

    # ==================================== 33b. THE FINALLY BLOCK ===
    s = add()
    title(s, [('The last seven lines', None), ('  —  ', None), ('and why they matter',
                                                                    'y')])
    body(s, Y_BODY_STD, [
        [('Not part of any TODO and never discussed in class, but this block is what '
          'makes the program safe to run twice:', None)],
    ])
    code(s, 6.6, [
        'finally:',
        '    cap.release()',
        '    cv2.destroyAllWindows()',
        '    set_pump(0)',
        '    GPIO.cleanup()',
        "    # Don't release servos - keeps arm powered for next run",
        '    # mc.release_all_servos()',
    ], size=11.5)
    bullet(s, 10.8, [
        ('It belongs to the ', None), ('try', 'c'), (' from Step 11, so it runs on '
         'a clean exit and on an exception. Both of those, not one of them.', None),
    ], h=2.4)
    bullet(s, 13.4, [
        ('The order is deliberate. ', None), ('set_pump(0)', 'c'), (' before ', None),
        ('GPIO.cleanup()', 'c'), (' — the pin interface is only released after the '
         'pin is in its safe state.', None),
    ], h=2.4)
    note(s, 16.2, [
        [('And the commented-out servo release is a decision, not an oversight. The '
          'arm stays powered so the next run does not have to re-home from wherever '
          'it was left.', None)],
    ], h=2.4)

    # ==================================== 34. RUN IT ===
    s = add()
    title(s, [('Run it', None)])
    body(s, Y_BODY_STD, [
        [('Send it across and start it. On a Pi with the arm and camera attached:',
          None)],
    ])
    command(s, 6.4, SCP)
    command(s, 7.5, RUN)
    body(s, 9.2, [
        [('Startup output looks like this — twice, which we will come back to:',
          None)],
    ])
    code(s, 10.8, [
        'Connected. Current angles: [0.0, 45.0, -90.0, ...]',
        'Moving to home angles: [0, 45, -90, -45, 0, 0]',
        '  send_angles returned: 1',
        'Home position (cartesian): [66.0, -62.0, 235.0, ...]',
    ], size=10.5)
    body(s, 14.0, [
        [('Then a window opens with the grid overlay and the prompt to press space. '
          'Place a green X, press space, and the arm goes to work.', None)],
    ])
    callout(s, 16.6, [
        ('Read those startup lines as a claim list. Every one of them is a '
          'statement about what the hardware did, printed before the game starts.',
         None),
    ], h=2.4)

    # ==================================== 35. VERIFY THE CLAIMS ===
    s = add()
    title(s, [('Verify the claims', None)])
    body(s, Y_BODY_STD, [
        [('The capstone is the largest file in the module, so it makes the most '
          'claims. Checked one at a time, without changing any code.', None)],
    ])
    table(s, 6.6, [
        ['#', 'The claim', 'Result'],
        ['1', 'Starts up and opens the camera', 'False'],
        ['2', 'Arm returns to the scan pose', 'True, twice'],
        ['3', 'Recognises both token colours', 'True'],
        ['4', 'Finds wins and blocks correctly', 'True'],
        ['5', 'Ends the game on a full board', 'True'],
    ], [1.4, 10.6, 4.6])
    note(s, 15.4, [
        [('One false out of five, and it is the first one — which means nothing '
          'after it ever ran. We will look at the other four too, because they '
          'passed in a file that had never executed.', None)],
    ], h=2.4)

    # ==================================== 36. CLAIM 1 FALSE ===
    s = add()
    title(s, [('Claim 1', None), ('  —  ', None), ('the file that never ran', 'y')])
    body(s, Y_BODY_STD, [
        [('The program has no top-level ', None), ('try', 'c'),
         (' around its connection, and no handler around the startup block. So when '
          'it failed, it failed immediately and visibly:', None)],
    ])
    code(s, 7.6, [
        'Traceback (most recent call last):',
        '  File "M2-P8-Base.py", line 83, in <module>',
        '    set_pump(0)',
        '    ^^^^^^^^^^',
        "NameError: name 'set_pump' is not defined",
    ], size=12.0)
    body(s, 11.0, [
        [('Line 83 calls it. Line 134 defines it. Python reads a file from the top '
          'down, executing each top-level statement as it goes — so when line 83 '
          'ran, the ', None), ('def', 'c'),
         (' statement fifty-one lines below it had not been reached yet.', None)],
    ])
    callout(s, 14.4, [
        ('This is a different order of bug from anything else in the module. Not a '
         'wrong value, not a missing bracket — a function that did not exist yet at '
         'the moment it was called.', None),
    ], h=2.6)

    # ==================================== 37. WHY IT LIVES AT THE TOP ===
    s = add()
    title(s, [('What the trace teaches', None)])
    body(s, Y_BODY_STD, [
        [('Two functions in this file are called before they are defined, and only '
          'one of them is a bug:', None)],
    ])
    code(s, 6.8, [
        '    board[r][c] = player',
        '    if check_winner(board) == player:',
        '        return (r, c)',
    ], size=13.0)
    body(s, 9.4, [
        [('This call is at line 177 and ', None), ('check_winner', 'c'),
         (' is defined at line 195 — the same problem, eighteen lines apart. And it '
          'has never caused a single error.', None)],
    ])
    bullet(s, 12.4, [
        ('It is inside a function body.', 'b'), (' Those lines are not executed '
         'when the file loads. They run when ', None), ('find_best_move', 'c'),
         (' is called, which is long after both functions exist.', None),
    ], h=2.6)
    bullet(s, 15.2, [
        ('set_pump(0) was at module level.', 'b'), (' Not in a function. It ran '
         'during load, in document order, and the name had not been created yet.',
         None),
    ], h=2.6)
    callout(s, 18.4, [
        ('Same mistake, opposite outcome, decided entirely by indentation. That is '
         'the entire lesson.', None),
    ], h=1.6)

    # ==================================== 38. THE FIX ===
    s = add()
    title(s, [('The fix', None)])
    body(s, Y_BODY_STD, [
        [('The correction is two deleted lines. Here is the block as it appeared '
          'before this project was corrected:', None)],
    ])
    code(s, 6.8, [
        '    POS_HOME_CARTESIAN = [66, -62, 235, 180, 0, 90]  # fallback',
        '    set_pump(0)',
        '    time.sleep(1.0)',
        '# ---',
    ], size=12.5)
    body(s, 9.4, [
        [('And here it is in the file you have now — the same block with those two '
          'lines gone:', None)],
    ])
    code(s, 11.6, [
        '    POS_HOME_CARTESIAN = [66, -62, 235, 180, 0, 90]  # fallback',
        '# ---',
    ], size=12.5)
    body(s, 13.6, [
        [('That is the whole fix. Nothing was moved or renamed: line 287 does the '
          'same job, after the camera opens, once it has been defined for 150 '
          'lines.', None)],
    ])
    callout(s, 16.6, [
        ('And it was redundant even on the timing question. Step 3 already drove '
          'both pins OFF during GPIO setup, so the early call was not "too soon" — '
          'it was unnecessary.', None),
    ], h=2.4)
    note(s, 19.4, [
        [('Two problems in one line, which is why it survived being written.',
          None)],
    ], h=1.0)

    # ==================================== 39. CLAIM 2 ===
    s = add()
    title(s, [('Claim 2', None), ('  —  ', None), ('true, but twice', 'y')])
    body(s, Y_BODY_STD, [
        [('The arm does reach the scan pose. It also does it ', None),
         ('twice', 'b'), (', and the startup log shows both:', None)],
    ])
    code(s, 7.4, [
        'Moving to home angles: [0, 45, -90, -45, 0, 0]',
        '  Sending send_angles command...',
        '  send_angles returned: 1',
        'Home position (cartesian): [66.0, -62.0, 235.0, ...]',
        'Angles after move: [0.0, 45.0, -90.0, ...]',
        'Moving to home angles: [0, 45, -90, -45, 0, 0]',
        '  Sending send_angles command...',
    ], size=10.0)
    body(s, 11.6, [
        [('Five seconds of arm movement, then another five. The entire home sequence '
          'appears twice in the file — once inside the Step 4 TODO block near the '
          'top, and again as given code after the camera is opened.', None)],
    ])
    callout(s, 14.4, [
        ('Worse than slow. The second block re-reads ', None), ('get_coords', 'c'),
        (' and overwrites ', None), ('POS_HOME_CARTESIAN', 'c'),
        (' with the same answer. It works by coincidence, not by design, and the '
          'ten seconds is the visible symptom of the copy.', None),
    ], h=2.8)
    note(s, 17.6, [
        [('Left in the corrected file on purpose. Inefficient and harmless: find it, '
          'choose which copy goes, and be certain before deleting.', None)],
    ], h=2.6)

    # ==================================== 40. CLAIMS 3 TO 5 ===
    s = add()
    title(s, [('Claims 3 to 5', None), ('  —  ', None), ('and these held', 'y')])
    body(s, Y_BODY_STD, [
        [('Three claims about behaviour, checked directly:', None)],
    ])
    question_item(s, 6.6, 1, [
        ('Both colours are recognised.', 'b'), ('  Green above 800 pixels and above '
         'red reads as X; red above 800 and above green reads as O. The grid '
         'constants are identical to Project 7.', None)])
    question_item(s, 9.6, 2, [
        ('Wins and blocks are correct.', 'b'), ('  Eight lines tested; the chained '
         'comparison requires three equal cells and none of them blank.', None)])
    question_item(s, 12.6, 3, [
        ('A full board ends the game.', 'b'), ('  ', None), ('find_best_move', 'c'),
        (' returns ', None), ('None', 'c'), (', the caller prints "Game is a Draw!" '
         'and moves on.', None)])
    note(s, 15.6, [
        [('All three passed. But they passed in a file that had never executed, '
          'which is the uncomfortable part: they are correct ', None),
         ('by reading', 'b'), ('. Reading is how you check code. Running is how you '
          'check that the code you read is the code that executes.', None)],
    ], h=3.2)
    callout(s, 19.0, [
        ('Four of five claims were true, and the program still had never run.',
         None),
    ], h=1.6)

    # ==================================== 41. THE HABIT ===
    s = add()
    title(s, [('The habit', None)])
    body(s, Y_BODY_STD, [
        [('The capstone needed one check, and it was not any of the ones the code '
          'invited you to make.', None)],
    ])
    bullet(s, 6.8, [
        ('Run the file.', 'y'), ('  Not the function — the file. Call order, '
         'import time, and module-level statements only exist at the top level.',
         None),
    ], h=2.4)
    bullet(s, 9.4, [
        ('Ask what runs, and when.', 'y'), ('  Every top-level statement executes '
         'during load, in document order, before any function is called.',
         None),
    ], h=2.4)
    bullet(s, 12.0, [
        ('Indentation is the whole difference.', 'y'), ('  Two calls precede their '
         'definitions. One crashed and one never could.', None),
    ], h=2.4)
    note(s, 15.0, [
        [('This is the last bug of the module and the simplest one to catch. Not '
          'because it is subtle, but because the check is obvious once you know to '
          'do it: start the program. Every piece of hardware in this course has to '
          'be switched on before any of it can be trusted.', None)],
    ], h=3.2)
    callout(s, 18.8, [
        ('Four hundred lines of capstone code, one missing function, and the whole '
         'thing had never been started.', None),
    ], h=1.6)

    # ==================================== 42. THE BRIEF ===
    s = add()
    title(s, [('The Brief', None)])
    body(s, Y_BODY_STD, [
        [('The Capstone', 'y'), ('\n', None)],
        [('A camera reads nine cells. A twenty-line opponent picks a square. The '
          'arm reaches into a rack, picks up a token with a vacuum pump, carries it '
          'eighteen seconds across the table, and puts it down.', None)],
        [('Then it goes back to the only viewpoint where it can see the board, and '
          'checks with its own eyes whether it did what it meant to.', None)],
        [('Seven projects of colour thresholds and camera calibration end here: in '
          'one function that moves hardware.', None)],
    ])

    # ==================================== 43. YOUR MISSION ===
    s = add()
    title(s, [('Your Mission', None)])
    body(s, Y_BODY_STD, [
        [('Three parts, in order.', None)],
    ])
    question_item(s, 6.8, 1, [
        ('Calibrate the nine cells.', 'b'), ('  Move the arm to each ', None),
        ('CELL_COORDS', 'c'), (' entry by hand and correct the values. Record which '
         'ones were wrong.', None)])
    question_item(s, 9.6, 2, [
        ('Time a full move.', 'b'), ('  Time one pick-and-place and add it up '
         'from the code. Then decide whether the game is still playable at that '
         'rate.', None)])
    question_item(s, 12.4, 3, [
        ('Break the loop.', 'b'), ('  Comment out the return-home at the end of ',
         None), ('execute_robot_move', 'c'), (', run one move, and describe exactly '
         'what the next frame shows.', None)])
    note(s, 15.4, [
        [('Part three is the interesting one. The robot will place a token '
          'perfectly well and then be unable to see the board it just played on.',
          None)],
    ], h=2.6)
    callout(s, 18.2, [
        ('A robot that trusts its own eyes is more useful than one that trusts its '
         'own memory. That is worth knowing before you build anything that cannot '
         'look.', None),
    ], h=2.0)

    # ==================================== 44. YOUR DATA LOG ===
    s = add()
    title(s, [('Your Data Log', None)])
    table(s, 6.6, [
        ['Measurement', 'Your value', 'Corrected?'],
        ['Cell (0,0) Z', '', ''],
        ['Cell (1,1) Z', '', ''],
        ['Cell (2,2) Z', '', ''],
        ['Total move time', '', ''],
        ['Home pose X/Y/Z', '', ''],
    ], [5.6, 4.4, 6.5], row_h=1.75)
    note(s, 17.2, [
        [('Record whether each value needed correcting rather than only what you '
          'changed it to. A hand-tuned calibration table that has been measured '
          'once and never verified is worth much less than one you know the '
          'accuracy of.', None)],
    ], h=2.6)

    # ==================================== 45. DEFINITION OF DONE ===
    s = add()
    title(s, [('Definition of Done', None)])
    check_item(s, 6.6, [('All thirteen TODOs filled in and the file runs on the Pi.',
                         None)])
    check_item(s, 8.4, [('No ', None), ('TODO', 'c'),
                        (' markers left anywhere in the file.', None)])
    check_item(s, 10.2, [('The robot wins a game it played fairly, and loses one it '
                         'played badly.', None)])
    check_item(s, 12.0, [('The robot blocks a three-in-a-row rather than letting the '
                         'human take it.', None)])
    check_item(s, 13.8, [('Every token lands inside its cell, from the rack, for all '
                         'five picks.', None)])
    check_item(s, 15.6, [('The camera can still read the board after a move.', None)])
    check_item(s, 17.4, [('Pulling the power mid-move leaves the pump off when the '
                         'program exits.', None)])
    callout(s, 19.2, [
        ('The last two are what make it safe to run twice in a row.', None),
    ], h=1.8)

    # ==================================== 46. GO FURTHER ===
    s = add()
    title(s, [('Go Further', None)])
    bullet(s, 6.6, [
        ('A real opponent.', 'b'), ('  Add two-ply lookahead to ', None),
        ('find_best_move', 'c'),
        (' and count how many games the current version gives away.', None),
    ], h=2.3)
    bullet(s, 8.9, [
        ('Undo the trial properly.', 'b'), ('  Make ', None), ('find_best_move', 'c'),
        (' leave the board untouched, then write a loop that proves it.', None),
    ], h=2.3)
    bullet(s, 11.2, [
        ('Kill the duplicate.', 'b'), ('  Remove the second home-move block and time '
         'the startup before and after.', None),
    ], h=2.3)
    bullet(s, 13.5, [
        ('Take the blocking out.', 'b'), ('  A queue or a thread so the window '
         'stays live during those eighteen seconds.', None),
    ], h=2.3)
    bullet(s, 15.8, [
        ('Let the robot start.', 'b'), ('  Move O to be the first player and give '
         'the human X. Then the AI has to open properly.', None),
    ], h=2.3)
    note(s, 18.4, [
        [('Pick one. Not all five.', None)],
    ], h=1.0)

    # ==================================== 47. DEBRIEF ===
    s = add(0, master=1)
    title(s, [('Debrief', None)], ext=True)
    body(s, Y_BODY_EXT, [
        [('Eight projects. One capstone that read a board, chose a move, and moved '
          'a real arm to make it.', None)],
        [('Everything it used was built earlier — the hue thresholds and the grid '
          'from the board scanner, the arm sequences from the gesture game, the '
          'habit of writing down what a program claims before trusting it.', None)],
        [('And the bug it died of was the oldest one in programming: a function '
          'called before it existed. Four hundred lines, four claims correct by '
          'reading, and it had never been started.', None)],
        [('Run the file.', None), ('\n', None),
         ('That is the whole lesson, and it is the one you will need on the day '
          'something does not work.', None)],
    ], ext=True)

    # ------------------------------------------------------- layout pass ---
    # Grown code panels are pushed clear of the copy that follows them.
    tight = pack_deck(prs, gap=0.30, limit=Y_BOTTOM)
    if tight:
        print('OVERFLOW (fix by splitting or trimming):', tight)

    # ------------------------------------------------------------------ save
    if os.path.exists(OUT):
        os.remove(OUT)
    prs.save(OUT)
    shutil.rmtree(TMP, ignore_errors=True)
    print(f'saved {OUT} ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)')


if __name__ == '__main__':
    build()
import os, sys, datetime, string, time, math
import regex as re
term_w = 80
term_h = 24

os_nt = (os.name == 'nt')

'''TEXT EDITING IN TERMINAL'''

def clear(errorMsg = False):
    if os_nt is True:
        os.system('cls')
    else:
        try:
            term_command(cmd = 'clear', exit = False)
        except:
            print('\n'*30)
            if errorMsg is True:
                print('Memory Error, must press <enter> after entering selections\n\n')

def delete_chars(n = 1):
    type_error(n, int)
    if n < 1:
        error(ValueError, 'Cannot delete {:d} characters (minimum 1)'.format(n))
    sys.stdout.write("\b \b"*n)
    sys.stdout.flush()

def replace_text(s = '', n = 1):
    sys.stdout.write("\b"*n)
    sys.stdout.write(s)
    sys.stdout.write("\033[C"*(n-1))
    sys.stdout.flush()

def delete_lines(n = 1):
    type_error(n, int)
    if n < 1:
        error(ValueError, 'Cannot delete {:d} characters (minimum 1)'.format(n))
    sys.stdout.write('\x1b[2K' + '\x1b[1A\x1b[2K'*n + '\r')
    #CURSOR_UP_ONE = '\x1b[1A'
    #ERASE_LINE = '\x1b[2K'
    #system.out.write((CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)*n)

def write(string):
    sys.stdout.write(string)
    sys.stdout.flush()

def write_delay(string, delay, endline = None):
    for c in string:
        write(c)
        pause(delay)
    if endline is None:
        pass
    elif isinstance(endline, str):
        write(endline)
    else:
        msg = 'parameter <endline> for function write_delay() must be of type <str>'
        error(errortype = TypeError, msg = msg)

def line_up(n):
    sys.stdout.write('\x1b[1A'*n + '\r')

'''STRING FUNCTIONS'''

def title(string):
    new = ''
    for w in string.split():
        v = w.strip()
        if len(v) > 1:
            new += v[0].upper() + v[1:].lower()
        else:
            new += v.upper()
        new += ' '
    return new.strip()

'''INPUT'''

def get_key_press(allowed = 'all', caseSensitive = False):
    os.system("stty raw -echo")
    if isinstance(allowed, (list, tuple)):
        allowed = [str(char).lower() for char in list(allowed)]
    elif isinstance(allowed, str):
        allowed = allowed.lower()
    if allowed == 'all':
        key = sys.stdin.read(1)
        if caseSensitive is False:
            key = key.lower()
        os.system("stty -raw echo")
        return key
    elif allowed == 'letters':
        allowed = list(string.ascii_lowercase)
    elif allowed == 'numbers':
        allowed = [0,1,2,3,4,5,6,7,8,9]
    elif allowed == 'wasd':
        allowed = ['w','a','s','d']
    elif allowed == 'yn':
        allowed = ['y','n']
    elif not isinstance(allowed, (list, tuple)):
        msg = 'Incorrect argument <key>, must enter a list or choose one of the following:\n'
        msg += '"all", "letters", "numbers", "wasd", "yn"'
        error(SyntaxError, msg)
    while True:
        key = sys.stdin.read(1)
        if caseSensitive is False:
            key = key.lower()
        if isinstance(allowed, (list, tuple)):
            condition = (key in allowed)
        elif isinstance(allowed, str):
            condition = (key == allowed)
        if condition is True:
            break
    os.system("stty -raw echo")
    return key

def key_to_continue(msg = 'Press Any Key to Continue', clearScreen = True):
    print(msg)
    get_key_press()
    if clearScreen is True:
        clear()

def select_from_menu(options, title = 'Menu', quit = True, back = True,
cleartext = True):
    scroll = 0
    firstrun = True
    while True:
        if cleartext is True:
            clear(errorMsg = True)
        elif cleartext is False and firstrun is False:
            n = len(options)
            if quit is True:
                n += 1
            if back is True:
                n += 1
            n += len(title.split('\n')) + 1
            print('Deleting {} Lines'.format(n))
            pause(1.5)
            delete_lines(n = n)
        elif cleartext is False and firstrun is True:
            firstrun = False
        else:
            msg = 'Function "clear()" must be of type <bool>'
            error(errortype = TypeError, msg = msg)
        print(title + '\n')
        needs_scroll = False
        if isinstance(options, dict):
            copy = options.copy()
            copy2 = {}
            length = len(options)
            nums = 0
            for i in copy.keys():
                if is_number(i):
                    nums += 1
            if nums > 9:
                needs_scroll = True
            for i in range(9):
                j = (i+scroll)%(nums+1)
                key = i+1
                val = copy.pop(str(j+1), None)
                if val is not None:
                    copy2[str(key)] = val
                    print('{}) {:s}'.format(key, val))
            print('')
            for k, v in copy.items():
                if not is_number(k):
                    copy2[k.lower()] = v
                    print('{:s}) {:s}'.format(k, v))
            if needs_scroll is True:
                print('N) Scroll Fwd')
                print('B) Scroll Bck')
                copy2['n'] = 'next'
                copy2['b'] = 'back'
            if back is True:
                print('R) Return')
                copy2['r'] = 'return'
            if quit is True:
                print('Q) Quit')
                copy2['q'] = 'quit'
            key_press = str(get_key_press(allowed = list(copy2.keys())))
            if key_press.lower() == 'q' and quit is True:
                exit(clearScreen = True)
            elif key_press.lower() == 'r' and back is True:
                return 'return'
            elif key_press.lower() == 'n' and needs_scroll is True:
                scroll += 1
                continue
            elif key_press.lower() == 'b' and needs_scroll is True:
                scroll -= 1
                continue
            else:
                return copy2[key_press]

def get_input(msg = 'Input: ', types = None, minimum = None, maximum = None):
    if types is None:
        return input(msg)
    if not isinstance(types, (tuple, list, dict)):
        types = [types]
    elif isinstance(types, (tuple, list)):
        types = list(types)
    else:
        error(TypeError, '<types> cannot be of type: <{:s}>'.format(type(types)))
    string = input(msg)
    try:
        if float in types:
            string = float(eval(string))
            if minimum is not None and string < minimum:
                return None
            if maximum is not None and string > maximum:
                return None
            return string
        elif int in types and int(eval(string)) - float(eval(string)) == 0:
            string = int(eval(string))
            if minimum is not None and string < minimum:
                return None
            if maximum is not None and string > maximum:
                return None
            return string
        else:
            return None
    except:
        if bool in types and string in ['True', 'False']:
            try:
                string = eval(string)
                return string
            except:
                if str not in types and type(string) != bool:
                    error(TypeError, 'Invalid input of type: <{:s}>'.format(type(string)))
                    return None
                else:
                    return string
    return None

def confirm(msg = 'Proceed? (Y/N)', clearScreen = True, acceptNumber = False):
    if clearScreen is True:
        clear(errorMsg = True)
    if msg is not None and msg != '':
        print(msg)
    if acceptNumber is False:
        result = get_key_press(allowed = 'yn')
    else:
        result = get_key_press(allowed = ['y','n',0,1,2,3,4,5,6,7,8,9])
    if result == 'y':
        return True
    elif result == 'n':
        return False
    else:
        if acceptNumber is True:
            try:
                return int(result)
            except:
                return None

def input_number(msg = 'Enter a number: ', error = True):
    num = input(msg)
    try:
        num = float(eval(num))
    except:
        if error is True:
            error(TypeError, 'User must enter a number\n"{:s}" cannot be evaluated as a number'.format(num))
        elif error is False:
            return None
        else:
            msg = 'Argument: <error> only takes boolean values\nUser entered type: <{:s}>'.format(type(num))
            error(SyntaxError, msg)
    else:
        if float(num) is None:
            error()
        return float(num)

def input_numbers(values, alias = None):
    final = {}
    for key in values:
        if key in alias:
            msg = '{:s} = {:s}\n'.format(key, alias[key])
            msg += 'Keep default? (Y/N)'
            condition = confirm(msg = msg, acceptNumber = False)
            if condition is True:
                final[values[key]] = alias[key]
                continue
        msg = 'Assign a value:\n{:s} = '.format(key)
        try:
            if not isinstance(condition, bool):
                condition = int(condition)
                msg += '{:d}'.format(condition)
                number = True
            else:
                number = False
        except:
            number = False
        clear(errorMsg = True)
        while True:
            newkey = input_number(msg = msg, error = False)
            if newkey is None and number is False:
                msg = 'Assign a value:\n{:s} = '.format(key)
                number = False
            elif newkey is None and number is True:
                newkey = ''
                break
            elif np.isfinite(newkey) is False:
                msg = 'Infinite values are not useable\nAssign a value:\n{:s} = '.format(key)
                number = False
            else:
                break
        if number is True:
            final[values[key]] = eval(str(condition)[0] + str(newkey))
        elif number is False:
            final[values[key]] = newkey
    return final

'''PROGRAM FLOW'''

def pause(t):
    time.sleep(t)

def exit(msg = '', clearScreen = False):
    if clearScreen is True:
        clear()
    if len(msg) > 0:
        print(msg)
    sys.exit(1)

'''EXCEPTIONS'''

def type_error(var, types, msg = None):
    if not isinstance(types, (list, tuple)) and isinstance(types, type):
        types = [types]
    types = list(types)
    for n,i in enumerate(types):
        if type(var) == i:
            return var
        types[n] = str(i)
    if msg is None:
        msg = 'Argument <var> is of incorrect type: {:s}\nValid Types: '.format(type(var))
        print(type(types))
        msg +=  ','.join(types)
    error(errortype = TypeError, msg = msg)

def error(errortype = None, msg = None):
    if errortype is None and msg is None:
        raise Exception("An unknown error occurred")
    elif isinstance(errortype,type) is True and msg is None:
        raise errortype("An unknown error occurred")
    elif isinstance(errortype,type) is False and msg is None:
        raise Exception(str(errortype))
    else:
        raise errortype(str(msg))
    sys.exit(1)

def prompt(msg, time = 'auto', enter_msg = 'Press Any Key to Continue'):
    clear()
    print(msg)
    if time == 'auto':
        time = len(msg)*0.08
        pause(time)
    elif time == 'enter':
        key_to_continue(enter_msg)
    else:
        pause(time)

def box_prompt(msg, title = '', time = None, enter_msg = None):

    msg = re.sub(r'(\n)+', r'\n', msg)
    msg = re.sub(r'(\t)+', r'', msg)
    msg = re.sub(r'(\r)+', r'', msg)
    msg = re.sub(r'(\b)+', r'', msg)

    #Getting Proportions

    min_width = 20

    ratio = term_w//(term_h//2)
    max_length = min(max(min_width, len(msg)//ratio), term_w - 6)

    #Style Options

    corner_top_left = "╔"
    corner_top_right = "╗"
    corner_bottom_left = "╚"
    corner_bottom_right = "╝"
    line_vert = "║"
    line_horiz = "═"
    title_left = "╣"
    title_right = "╠"

    #Preparing Text

    if enter_msg is None:
        enter_msg = 'PRESS ANY KEY TO CONTINUE'
    msg = msg.split(' ')
    length = len(msg[0])
    text = [msg[0]]
    lines = 0
    longest = 0
    for w in msg[1:]:
        if w == '\n':
            if lines + 2 > term_h - 6:
                error(ValueError, 'Cannot display such a large amount of text at once')
            lines += 2
            length = 0
            text += ['', '']
        elif length + len(w) + 1 < max_length:
            length += len(w) + 1
            text[lines] += ' {}'.format(w)
        else:
            if lines + 1 > term_h - 6:
                error(ValueError, 'Cannot display such a large amount of text at once')
            else:
                if length > longest:
                    longest = length
                lines += 1
                length = len(w)
                text.append(w)

    title = title_left + " {} ".format(title) + title_right
    space1 = math.ceil((max_length - len(title))/2)
    space2 = math.floor((max_length - len(title))/2)
    if title == title_left + "  " + title_right:
        box = [corner_top_left + line_horiz*(space1 + space2 + 6) + corner_top_right]
    else:
        box = [corner_top_left + line_horiz*(space1+1) + title + line_horiz*(space2+1) + corner_top_right]
    box.append(line_vert + ' '*(max_length+2) + line_vert)

    for n,s in enumerate(text):
        space1 = math.ceil(((max_length) - len(s))/2)
        space2 = math.floor(((max_length) - len(s))/2)
        new = '{} {}{}{} {}'.format(line_vert, ' '*space1, s, ' '*space2, line_vert)
        box.append(new)
    box.append(line_vert + ' '*(max_length+2) + line_vert)

    space1 = math.ceil((max_length - len(enter_msg))/2)
    space2 = math.floor((max_length - len(enter_msg))/2)-2

    box.append(corner_bottom_left + line_horiz*(max_length+2) + corner_bottom_right)
    box.append('')
    tot_len = len(box[0])
    w_space = (term_w - tot_len)//2
    h_space = (term_h - lines + 1)//2
    text = ''
    text += '\n'*(h_space//2)
    for n,i in enumerate(box):
        text += ' '*w_space + i
        if n < len(box) - 1:
            text += '\n'

    #Displaying Text

    clear()
    enter_msg = ' '*((term_w - len(enter_msg))//2 + 1) + enter_msg
    prompt(text, time = 'enter', enter_msg = enter_msg)

def print_center(msg):
    if len(msg) > term_w:
        error(errortype = ValueError, msg = 'String width ({}) is larger than terminal width ({})'\
        .format(len(msg), term_w))
    print(' '*(term_w - len(msg))//2 + 1, msg)

'''COLORING'''

class col_str:

    '''
        A string that can contain colors, for example:

        example = col_str("<blue>This text is blue<\blue>")
        example2 = col_str("<red>This text is blue<\red>")
        example3 = col_str("<red>red<\red> white and <blue>blue<\blue>")

        These can be printed and formatted like regular strings
    '''

    def __init__(self, s):
        self._raw = s

    def _parse(self, s):
        for i in patterns:
            pattern = '<{}>'

    def _ID(self, s):
        pass


'''TERMINAL TOOLS'''

def set_terminal_size():
    default_width = 80
    default_height = 24

    def confirm_border(w, h):
        border = 'X'*w + '\n' + ('X' + ' '*(w-2) + 'X\n')*(math.floor((h-3)/2))
        msg1 = "Press 'Y' if there is a perfect border of X's around your terminal,"
        msg2 = "Press 'N' if the border is misshapen, or smaller than the terminal."
        border += 'X' + ' '*(math.floor((w-len(msg1))/2) - 1) + msg1
        border += ' '*(math.ceil((w-len(msg1))/2) - 1) + 'X\n'
        border += 'X' + ' '*(math.floor((w-len(msg2))/2) - 1) + msg2
        border += ' '*(math.ceil((w-len(msg2))/2) - 1) + 'X\n'
        border += ('X' + ' '*(w-2) + 'X\n')*(math.floor((h-3)/2)) + 'X'*w
        write(border)
        return confirm(msg = None, clearScreen = False)

    confirmed = confirm_border(default_width, default_height)
    if confirmed is True:
        clear()
        w = default_width
        h = default_height
    elif confirmed is False:
        while True:
            w = 1
            h = 1
            while True:
                clear()
                print('X'*w)
                print("'D' adds an X, 'A' removes an X")
                print("Press 'C' to continue when terminal width is reached.")
                key = get_key_press(allowed = ['D', 'A', 'C'])
                if key == 'd':
                    w += 1
                elif key == 'a':
                    w -= 1
                    if w < 1:
                        w = 1
                elif key == 'c':
                    break

            while True:
                clear()
                print("X\t'S' adds an X, 'W' removes an X")
                print("X\tPress 'C' to continue when terminal width is reached.")
                write('X\n'*(h-3)+'X')
                key = get_key_press(allowed = ['W', 'S', 'C'])
                if key == 's':
                    h += 1
                elif key == 'w':
                    h -= 1
                    if h < 2:
                        h = 2
                elif key == 'c':
                    break

            clear()
            if confirm_border(w, h) is True:
                clear()
                break
    term_w = w
    term_h = h
    return w,h

def term_command(cmd, exit = True):
    newpid = os.fork()
    if newpid == 0:
        os.execvp(cmd, [cmd,'-1'])
        if exit is True:
            os._exit(1)
    os.wait()

def get_terminal_kwargs(argv, allArgs = False):
    kwargs = {}
    others = []
    for arg in argv:
        try:
            splitArg = arg.split('=')
            if len(splitArg) == 2:
                kwargs[(splitArg[0].strip(' ')).lower()] = (splitArg[1].strip(' '))
            else:
                others.append(arg.lower())
        except:
            error(SyntaxError, 'Could not parse the given terminal arguments')
    if allArgs is False:
        return kwargs
    else:
        return kwargs, others

'''CHECKERS'''

def is_number(x):
    try:
        float(x)
        return True
    except:
        return False

'''LOOPS AND LOADING BARS'''

def loop_except(func, error = Exception, msg = 'Attempt Failed, Try Again? (Y/N)',
clearScreen = True, endProgram = True):
    while True:
        try:
            return func
        except error:
            if confirm(msg = msg, clearScreen = clearScreen):
                continue
            elif endProgram is True:
                exit()
            else:
                break

def loading_bar(p1, p2 = None, msg = 'Loading...', length = 30, autoClear = True,
clearErrorMsg = False):
    string = '{:s}\n['.format(msg)
    string = string + '*'*int(p1*length)
    string = string + ' '*(length-int(p1*length))
    if p2 is not None:
        string = string + ']\n['
        string = string + "*"*int(p2*length)
        string = string + ' '*(length-int(p2*length))
    string = string + ']\n'
    string = string + ' '*(length/2 - 1)
    string = string + '{:2d}%%'.format(int(p1*100))
    if autoClear is False:
        return string
    else:
        clear(errorMsg = clearErrorMsg)
        print(string)

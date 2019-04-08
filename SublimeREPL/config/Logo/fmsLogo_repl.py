#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Glaukon Ariston
# Date: 08.04.2019
# Abstract: Use pywinauto to control FMSLogo programmatically.
#
import sys
import datetime
import time
import threading
import win32clipboard
from pywinauto.application import Application


TARGET = 'FMSLogo'
PROMPT = '>>> '


UND = '\x00'
CHARMAP = {
    ' ': '{VK_SPACE}',
    '\t': '{TAB}',
    '\n': '{ENTER}',
    '+': '{VK_ADD}',
    '-': '{VK_SUBTRACT}',
}

'''
CHARMAP = {UND: '{SCROLLLOCK}', ' ': '{VK_SPACE}', UND: '{VK_LSHIFT}', UND: '{VK_PAUSE}', UND: '{VK_MODECHANGE}', UND: '{BACK}', UND: '{VK_HOME}', UND: '{F23}', UND: '{F22}', UND: '{F21}', UND: '{F20}', UND: '{VK_HANGEUL}', UND: '{VK_KANJI}', UND: '{VK_RIGHT}', UND: '{BS}', UND: '{HOME}', UND: '{VK_F4}', UND: '{VK_ACCEPT}', UND: '{VK_F18}', UND: '{VK_SNAPSHOT}', UND: '{VK_PA1}', UND: '{VK_NONAME}', UND: '{VK_LCONTROL}', UND: '{ZOOM}', UND: '{VK_ATTN}', UND: '{VK_F10}', UND: '{VK_F22}', UND: '{VK_F23}', UND: '{VK_F20}', UND: '{VK_F21}', UND: '{VK_SCROLL}', '\t': '{TAB}', UND: '{VK_F11}', UND: '{VK_END}', UND: '{LEFT}', UND: '{VK_UP}', UND: '{NUMLOCK}', UND: '{VK_APPS}', UND: '{PGUP}', UND: '{VK_F8}', UND: '{VK_CONTROL}', UND: '{VK_LEFT}', UND: '{PRTSC}', UND: '{VK_NUMPAD4}', UND: '{CAPSLOCK}', UND: '{VK_CONVERT}', UND: '{VK_PROCESSKEY}', '\n': '{ENTER}', UND: '{VK_SEPARATOR}', UND: '{VK_RWIN}', UND: '{VK_LMENU}', UND: '{VK_NEXT}', UND: '{F1}', UND: '{F2}', UND: '{F3}', UND: '{F4}', UND: '{F5}', UND: '{F6}', UND: '{F7}', UND: '{F8}', UND: '{F9}', '+': '{VK_ADD}', UND: '{VK_RCONTROL}', UND: '{VK_RETURN}', UND: '{BREAK}', UND: '{VK_NUMPAD9}', UND: '{VK_NUMPAD8}', UND: '{RWIN}', UND: '{VK_KANA}', UND: '{PGDN}', UND: '{VK_NUMPAD3}', UND: '{DEL}', UND: '{VK_NUMPAD1}', UND: '{VK_NUMPAD0}', UND: '{VK_NUMPAD7}', UND: '{VK_NUMPAD6}', UND: '{VK_NUMPAD5}', UND: '{DELETE}', UND: '{VK_PRIOR}', '-': '{VK_SUBTRACT}', UND: '{HELP}', UND: '{VK_PRINT}', UND: '{VK_BACK}', UND: '{CAP}', UND: '{VK_RBUTTON}', UND: '{VK_RSHIFT}', UND: '{VK_LWIN}', UND: '{DOWN}', UND: '{VK_HELP}', UND: '{VK_NONCONVERT}', UND: '{BACKSPACE}', UND: '{VK_SELECT}', '\t': '{VK_TAB}', UND: '{VK_HANJA}', UND: '{VK_NUMPAD2}', UND: '{INSERT}', UND: '{VK_F9}', UND: '{VK_DECIMAL}', UND: '{VK_FINAL}', UND: '{VK_EXSEL}', UND: '{RMENU}', UND: '{VK_F3}', UND: '{VK_F2}', UND: '{VK_F1}', UND: '{VK_F7}', UND: '{VK_F6}', UND: '{VK_F5}', UND: '{VK_CRSEL}', UND: '{VK_SHIFT}', UND: '{VK_EREOF}', UND: '{VK_CANCEL}', UND: '{VK_DELETE}', UND: '{VK_HANGUL}', UND: '{VK_MBUTTON}', UND: '{VK_NUMLOCK}', UND: '{VK_CLEAR}', UND: '{END}', UND: '{VK_MENU}', ' ': '{SPACE}', UND: '{BKSP}', UND: '{VK_INSERT}', UND: '{F18}', UND: '{F19}', UND: '{ESC}', UND: '{VK_MULTIPLY}', UND: '{F12}', UND: '{F13}', UND: '{F10}', UND: '{F11}', UND: '{F16}', UND: '{F17}', UND: '{F14}', UND: '{F15}', UND: '{F24}', UND: '{RIGHT}', UND: '{VK_F24}', UND: '{VK_CAPITAL}', UND: '{VK_LBUTTON}', UND: '{VK_OEM_CLEAR}', UND: '{VK_ESCAPE}', UND: '{UP}', UND: '{VK_DIVIDE}', UND: '{INS}', UND: '{VK_JUNJA}', UND: '{VK_F19}', UND: '{VK_EXECUTE}', UND: '{VK_PLAY}', UND: '{VK_RMENU}', UND: '{VK_F13}', UND: '{VK_F12}', UND: '{LWIN}', UND: '{VK_DOWN}', UND: '{VK_F17}', UND: '{VK_F16}', UND: '{VK_F15}', UND: '{VK_F14}', }
'''

def escape(s):
    for ch, rep in CHARMAP.items():
        s = s.replace(ch, rep)
    return s


def process_input(wnd, button):
    sys.stdout.write(PROMPT)
    for line in sys.stdin:
        wnd.type_keys(escape(line))
        #wnd.set_text(line)
        button.click()
        sys.stdout.write(PROMPT)


def process_output(wnd):
    history = ''
    while True:
        time.sleep(1)
        continue
        # Copy text to clipboard
        wnd.set_focus()
        wnd.type_keys('^a^c')

        # Get the text from the clipboard
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        if data.startswith(history):
            delta = data[len(history):]
            if delta:
                print('%s' % (delta))
            history = data


def main():
    app = Application().connect(title_re=TARGET)
    mainWnd = app.top_window()
    outputWnd = mainWnd['text']
    outputWnd.draw_outline("red")
    inputWnd = mainWnd['stcwindow']
    button = mainWnd['IzvršiButton']        # ['Button7']

    t0 = datetime.datetime.now()
    print('Connected to %s at %s\n' % (TARGET, t0))

    tout = threading.Thread(target=(lambda : process_output(outputWnd)))
    tout.start()
    tin = threading.Thread(target=(lambda : process_input(inputWnd, button)))
    tin.start()


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Glaukon Ariston
# Date: 08.04.2019
# Abstract: Use pywinauto to control FMSLogo programmatically.
#

def main():
    from pywinauto.application import Application
    app = Application().connect(title_re="FMSLogo")
    dlg = app.top_window()
    dlg.text.draw_outline("red")

    # Copy text to clipboard
    dlg.text.set_focus()
    dlg.text.type_keys('^a^c')
    import win32clipboard

    # Get the text from the clipboard
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    print('"%s"' % (data))

if __name__ == '__main__':
    main()

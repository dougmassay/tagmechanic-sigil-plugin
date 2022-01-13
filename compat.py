#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

import os

from utilities import tuple_version, ismacos, iswindows

try:
    from PySide6.QtCore import Qt, QTimer, qVersion
    from PySide6.QtWidgets import QApplication, QStyleFactory
    from PySide6.QtGui import QColor, QFont, QPalette
except ImportError:
    from PyQt5.QtCore import Qt, QTimer, qVersion
    from PyQt5.QtWidgets import QApplication, QStyleFactory
    from PyQt5.QtGui import QColor, QFont, QPalette


def setup_highdpi(highdpi):
    has_env_setting = False
    env_vars = ('QT_AUTO_SCREEN_SCALE_FACTOR', 'QT_SCALE_FACTOR', 'QT_SCREEN_SCALE_FACTORS', 'QT_DEVICE_PIXEL_RATIO')
    for v in env_vars:
        if os.environ.get(v):
            has_env_setting = True
            break
    if highdpi == 'on' or (highdpi == 'detect' and not has_env_setting):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    elif highdpi == 'off':
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, False)
        for p in env_vars:
            os.environ.pop(p, None)

def match_sigil_highdpi(dpi_setting):
    # macos handles highdpi in both Qt5 and Qt6
    if not ismacos:
        # Linux and Windows don't need to do anything
        # to enable highdpi after Qt6
        if tuple_version(qVersion()) < (6, 0, 0):
            try:
                setup_highdpi(dpi_setting)
            except Exception:
                pass


def setup_ui_font(font_str):
    font = QFont()
    font.fromString(font_str)
    QApplication.setFont(font)

def match_sigil_font(font_string):
    # QFont::toString produces slightly different results in Qt5 vs
    # Qt6. Produce a string that will work with QFont::fromString
    # in both Qt5 and Qt6. 
    print(font_string)
    lst = font_string.split(',')
    try:
        if len(lst) > 10 and tuple_version(qVersion()) < (6, 0, 0):
            lst = lst[:10]
            lst[4] = str(int(lst[4])/8)
        print(','.join(lst))
        setup_ui_font(','.join(lst))
    except Exception:
        pass
    if not ismacos and not iswindows:
        # Qt 5.10.1 on Linux resets the global font on first event loop tick.
        # So workaround it by setting the font once again in a timer.
        try:
            QTimer.singleShot(0, lambda : setup_ui_font(','.join(lst)))
        except Exception:
            pass


def match_sigil_palette(bk, app):
    if not (bk.launcher_version() >= 20200117):
        return
    if bk.colorMode() != "dark":
        return

    p = QPalette()
    sigil_colors = bk.color
    dark_color = QColor(sigil_colors("Window"))
    disabled_color = QColor(127,127,127)
    dark_link_color = QColor(108, 180, 238)
    text_color = QColor(sigil_colors("Text"))
    p.setColor(p.Window, dark_color)
    p.setColor(p.WindowText, text_color)
    p.setColor(p.Base, QColor(sigil_colors("Base")))
    p.setColor(p.AlternateBase, dark_color)
    p.setColor(p.ToolTipBase, dark_color)
    p.setColor(p.ToolTipText, text_color)
    p.setColor(p.Text, text_color)
    p.setColor(p.Disabled, p.Text, disabled_color)
    p.setColor(p.Button, dark_color)
    p.setColor(p.ButtonText, text_color)
    p.setColor(p.Disabled, p.ButtonText, disabled_color)
    p.setColor(p.BrightText, Qt.red)
    p.setColor(p.Link, dark_link_color)
    p.setColor(p.Highlight, QColor(sigil_colors("Highlight")))
    p.setColor(p.HighlightedText, QColor(sigil_colors("HighlightedText")))
    p.setColor(p.Disabled, p.HighlightedText, disabled_color)

    app.setStyle(QStyleFactory.create("Fusion"))
    app.setPalette(p)


def disable_whats_this(app):
    if tuple_version(qVersion()) >= (5, 10, 0) and tuple_version(qVersion()) < (5, 15, 0):
        app.setAttribute(Qt.AA_DisableWindowContextHelpButton)

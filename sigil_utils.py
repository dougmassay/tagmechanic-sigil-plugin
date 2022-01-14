#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

import os
import sys
import inspect

try:
    from PySide6.QtCore import Qt, QTimer, qVersion, QMetaObject, QDir
    from PySide6.QtCore import QLibraryInfo, QTranslator
    from PySide6.QtCore import Signal, Slot  # noqa
    from PySide6.QtWidgets import QApplication, QStyleFactory
    from PySide6.QtGui import QColor, QFont, QPalette
    from PySide6.QtUiTools import QUiLoader
except ImportError:
    from PyQt5.QtCore import Qt, QTimer, qVersion, QLibraryInfo, QTranslator
    from PyQt.QtCore import pyqtSignal as Signal, pyqtSlot as Slot  # noqa
    from PyQt5.QtWidgets import QApplication, QStyleFactory
    from PyQt5.QtGui import QColor, QFont, QPalette
    from PyQt5 import uic


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

DEBUG = 0
if DEBUG:
    if 'PySide6' in sys.modules:
        print('sigil_utilities using PySide6')
    else:
        print('sigil_utilities using PyQt5')


_plat = sys.platform.lower()
iswindows = 'win32' in _plat or 'win64' in _plat
ismacos = isosx = 'darwin' in _plat


def tuple_version(v):
    # No aplha characters in version strings allowed here!
    return tuple(map(int, (v.split("."))))


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

# Match Sigil's highdpi setting if necessary/possible
def match_sigil_highdpi(bk):
    if not (bk.launcher_version() >= 20200326):  # Sigil 1.2.0
        return
    # macos handles highdpi in both Qt5 and Qt6
    if not ismacos:
        # Linux and Windows don't need to do anything to enable highdpi after Qt6
        if tuple_version(qVersion()) < (6, 0, 0):
            try:
                setup_highdpi(bk._w.highdpi)
            except Exception:
                pass


def setup_ui_font(font_str):
    font = QFont()
    font.fromString(font_str)
    QApplication.setFont(font)

# Match Sigil's UI font settings if possible
def match_sigil_font(bk):
    # QFont::toString produces slightly different results with Qt5 vs
    # Qt6. Produce a string that will work with QFont::fromString
    # in both Qt5 and Qt6.
    if not (bk.launcher_version() >= 20200326):  # Sigil 1.2.0
        return
    if DEBUG:
        print(bk._w.uifont)
    lst = bk._w.uifont.split(',')
    try:
        if len(lst) > 10 and tuple_version(qVersion()) < (6, 0, 0):
            lst = lst[:10]
            lst[4] = str(int(lst[4])/8)
        if DEBUG:
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


# Match Sigil's dark theme if possible
def match_sigil_darkmode(bk, app):
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


# Disable '?' window box buttons if necessary
def disable_whats_this(app):
    if tuple_version(qVersion()) >= (5, 10, 0) and tuple_version(qVersion()) < (5, 15, 0):
        app.setAttribute(Qt.AA_DisableWindowContextHelpButton)


# Find the location of Qt's base translations
def get_qt_translations_path(sigil_path):
    isBundled = 'sigil' in sys.prefix.lower()
    if DEBUG:
        print('Python is Bundled: {}'.format(isBundled))
    if isBundled:
        if sys.platform.lower().startswith('darwin'):
            return os.path.normpath(sigil_path + '/../translations')
        else:
            return os.path.join(sigil_path, 'translations')
    else:
        return QLibraryInfo.location(QLibraryInfo.TranslationsPath)

# Install qtbase translator for standard dialogs and such.
# Use the Sigil language setting unless manually overridden.
def load_base_qt_translations(bk, language_override=None):
    if not (bk.launcher_version() >= 20170227):  # Sigil 0.9.8
        return
    qt_translator = QTranslator()
    if language_override is not None:
        if DEBUG:
            print('Plugin language override in effect')
        qmf = 'qtbase_{}'.format(language_override)
    else:
        qmf = 'qtbase_{}'.format(bk.sigil_ui_lang)
    # Get bundled or external translations directory
    qt_trans_dir = get_qt_translations_path(bk._w.appdir)
    if DEBUG:
        print('Qt translation dir: {}'.format(qt_trans_dir))
        print('Looking for {} in {}'.format(qmf, qt_trans_dir))
    qt_translator.load(qmf, qt_trans_dir)
    return qt_translator


# Install translator for the specified plugin dialog.
# Use the Sigil language setting unless manually overridden.
# 'folder' parameter is where the binary <plugin_name>_??.qm files are.
def load_plugin_translations(bk, folder, language_override=None):
    if not (bk.launcher_version() >= 20170227):  # Sigil 0.9.8
        return
    plugin_translator = QTranslator()
    if language_override is not None:
        if DEBUG:
            print('Plugin language override in effect')
        qmf = '{}_{}'.format(bk._w.plugin_name.lower(), language_override)
    else:
        qmf = '{}_{}'.format(bk._w.plugin_name.lower(), bk.sigil_ui_lang)
    if DEBUG:
        print('Looking for {} in {}'.format(qmf, folder))
    plugin_translator.load(qmf, folder)
    return plugin_translator


# Mimic the behavior of PyQt5.uic.loadUi() in PySide6
# so the same code can be used for PyQt5/PySide6.
if 'PySide6' in sys.modules:
    class UiLoader(QUiLoader):
        def __init__(self, baseinstance, customWidgets=None):
            QUiLoader.__init__(self, baseinstance)
            self.baseinstance = baseinstance
            self.customWidgets = customWidgets

        def createWidget(self, class_name, parent=None, name=''):
            if parent is None and self.baseinstance:
                # supposed to create the top-level widget, return the base instance
                # instead
                return self.baseinstance
            else:
                if class_name in self.availableWidgets():
                    # create a new widget for child widgets
                    widget = QUiLoader.createWidget(self, class_name, parent, name)
                else:
                    # if not in the list of availableWidgets, must be a custom widget
                    # this will raise KeyError if the user has not supplied the
                    # relevant class_name in the dictionary, or TypeError, if
                    # customWidgets is None
                    try:
                        widget = self.customWidgets[class_name](parent)

                    except (TypeError, KeyError):
                        raise Exception('No custom widget ' + class_name + ' found in customWidgets param of UiLoader __init__.')

                if self.baseinstance:
                    # set an attribute for the new child widget on the base
                    # instance, just like PyQt5/6.uic.loadUi does.
                    setattr(self.baseinstance, name, widget)

                return widget

    def loadUi(uifile, baseinstance=None, customWidgets=None,
            workingDirectory=None):

        loader = UiLoader(baseinstance, customWidgets)

        # If the .ui file references icons or other resources it may
        # not find them unless the cwd is defined. If this compat library
        # is in the same directory as the calling script, things should work.
        # If it's in another directory, however, you may need to set the
        # PYSIDE_LOADUI_CWD environment variable to the resource's directory first.
        # Best practice is not to define icons in the .ui file. Do it at the app level.
        if os.environ('PYSIDE_LOADUI_CWD') is not None:
            loader.setWorkingDirectory(os.environ('PYSIDE_LOADUI_CWD'))
        else:
            loader.setWorkingDirectory(QDir(SCRIPT_DIRECTORY))

        widget = loader.load(uifile)
        QMetaObject.connectSlotsByName(widget)
        return widget

# Otherwise return the standard PyQt5 loadUi object
else:
    loadUi = uic.loadUi

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

import os
import sys
import inspect

try:
    from PySide6.QtCore import Qt, QTimer, QMetaObject, QDir, qVersion
    from PySide6.QtCore import QLibraryInfo, QTranslator
    from PySide6.QtCore import Signal, Slot  # noqa
    from PySide6.QtWidgets import QApplication, QStyleFactory
    from PySide6.QtGui import QColor, QFont, QPalette
    from PySide6.QtUiTools import QUiLoader
except ImportError:
    from PyQt5.QtCore import Qt, QTimer, QLibraryInfo, QTranslator, qVersion
    from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot  # noqa
    from PyQt5.QtWidgets import QApplication, QStyleFactory
    from PyQt5.QtGui import QColor, QFont, QPalette
    from PyQt5 import uic


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
SIGIL_QT_MAJOR_VERSION = tuple(map(int, (os.environ.get('SIGIL_QT_VERSION').split("."))))[0]
PLUGIN_QT_MAJOR_VERSION = tuple(map(int, (qVersion().split("."))))[0]

DEBUG = 1
if DEBUG:
    if 'PySide6' in sys.modules:
        print('sigil_utilities using PySide6')
    else:
        print('sigil_utilities using PyQt5')


_plat = sys.platform.lower()
iswindows = 'win32' in _plat or 'win64' in _plat
ismacos = isosx = 'darwin' in _plat


def tuple_version(v):
    # No alpha characters in version strings allowed here!
    return tuple(map(int, (v.split("."))))


''' Keep Windows from showing the Python icon on the taskbar '''
def ensure_windows_taskbar_icon():
    if not iswindows:
        return
    import ctypes
    myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


''' Find the location of Qt's base translations '''
def get_qt_translations_path(app_path):
    isBundled = 'sigil' in sys.prefix.lower()
    if DEBUG:
        print('Python is Bundled: {}'.format(isBundled))
    if isBundled:
        if sys.platform.lower().startswith('darwin'):
            return os.path.normpath(app_path + '/../translations')
        else:
            return os.path.join(app_path, 'translations')
    else:
        return QLibraryInfo.location(QLibraryInfo.TranslationsPath)


''' Helper function to convert between legacy Qt and OpenType font weights. '''
def convertWeights(weight, inverted=False, shift=False):
    legacyToOpenTypeMap = [
        (0, 100, QFont.Thin),
        (12, 200, QFont.ExtraLight),
        (25, 300, QFont.Light),
        (50, 400, QFont.Normal),
        (57, 500, QFont.Medium),
        (63, 600, QFont.DemiBold),
        (75, 700, QFont.Bold),
        (81, 800, QFont.ExtraBold),
        (87, 900, QFont.Black),
    ]

    closestDist = sys.maxsize
    result = -1
    upper = 2 if shift else 1
    # Go through and find the closest mapped value
    for mapping in legacyToOpenTypeMap:
        weightOld = mapping[upper] if inverted else mapping[0]
        weightNew = mapping[0] if inverted else mapping[upper]

        dist = abs(weightOld - weight)
        if dist < closestDist:
            result = weightNew
            closestDist = dist
        else:
            # Break early since following values will be further away
            break
    return result


class Application(QApplication):
    def __init__(self, args, bk, app_icon=None, match_fonts=True,
                match_highdpi=True, match_dark_palette=True,
                match_whats_this=True, load_qtbase_translations=True,
                load_qtplugin_translations=True, plugin_trans_folder=None):

        self.bk = bk
        self.sigil_qt_version = (6, 2, 2)
        program_name = 'sigil_plugin_{}'.format(bk._w.plugin_name.lower())
        if plugin_trans_folder is None:
            plugin_trans_folder = os.path.join(self.bk._w.plugin_dir, 'translations')

        if tuple_version(qVersion()) < (6, 0, 0):
            self.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
        if match_highdpi:
            self.match_sigil_highdpi()
        args = [program_name] + args[1:]
        QApplication.__init__(self, args)
        if app_icon is not None:
            self.setWindowIcon(app_icon)
            if iswindows:
                ensure_windows_taskbar_icon()

        if match_dark_palette:
            self.match_sigil_darkmode()
        if match_whats_this:
            if tuple_version(qVersion()) >= (5, 10, 0) and tuple_version(qVersion()) < (5, 15, 0):
                self.setAttribute(Qt.ApplicationAttribute.AA_DisableWindowContextHelpButton)
        if load_qtbase_translations:
            self.load_base_qt_translations()
        if load_qtplugin_translations:
            self.load_plugin_translations(plugin_trans_folder)
        if match_fonts:
            self.match_sigil_font()

    def _setup_highdpi_(self, highdpi):
        has_env_setting = False
        env_vars = ('QT_AUTO_SCREEN_SCALE_FACTOR', 'QT_SCALE_FACTOR', 'QT_SCREEN_SCALE_FACTORS', 'QT_DEVICE_PIXEL_RATIO')
        for v in env_vars:
            if os.environ.get(v):
                has_env_setting = True
                break
        if highdpi == 'on' or (highdpi == 'detect' and not has_env_setting):
            self.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        elif highdpi == 'off':
            self.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, False)
            for p in env_vars:
                os.environ.pop(p, None)

    # Match Sigil's highdpi setting if necessary/possible
    def match_sigil_highdpi(self):
        if not (self.bk.launcher_version() >= 20200326):  # Sigil 1.2.0
            return
        # macos handles highdpi in both Qt5 and Qt6
        if not ismacos:
            # Linux and Windows don't need to do anything to enable highdpi after Qt6
            if tuple_version(qVersion()) < (6, 0, 0):
                try:
                    self._setup_highdpi_(self.bk._w.highdpi)
                except Exception:
                    pass

    # Match Sigil's dark theme if possible
    def match_sigil_darkmode(self):
        if not (self.bk.launcher_version() >= 20200117):
            return
        if self.bk.colorMode() != "dark":
            return
        if DEBUG:
            print('Setting dark palette')

        p = QPalette()
        sigil_colors = self.bk.color
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

        self.setStyle(QStyleFactory.create("Fusion"))
        self.setPalette(p)

    def _setup_ui_font_(self, font_lst):
        font = QApplication.font()
        font.fromString(','.join(font_lst))

        if PLUGIN_QT_MAJOR_VERSION >= 6 and SIGIL_QT_MAJOR_VERSION < 6:
            font.setWeight(convertWeights(int(font_lst[4]), shift=True))
        if PLUGIN_QT_MAJOR_VERSION < 6 and SIGIL_QT_MAJOR_VERSION >= 6:
            font.setWeight(convertWeights(int(font_lst[4]), inverted=True))

        if DEBUG:
            print(f'Font Weight: {font.weight()}')

        QApplication.instance().setFont(font)
        if DEBUG:
            print(font.toString())

    # Match Sigil's UI font settings if possible
    def match_sigil_font(self):
        # QFont::toString produces slightly different results with Qt5 vs
        # Qt6. Produce a string that will work with QFont::fromString
        # in both Qt5 and Qt6.
        if not (self.bk.launcher_version() >= 20200326):  # Sigil 1.2.0
            return
        if DEBUG:
            print(self.bk._w.uifont)
        lst = self.bk._w.uifont.split(',')

        if PLUGIN_QT_MAJOR_VERSION >= 6 and SIGIL_QT_MAJOR_VERSION < 6:
            lst = lst + ['0','0','0','0','0','1']
        if PLUGIN_QT_MAJOR_VERSION < 6 and SIGIL_QT_MAJOR_VERSION >= 6:
            lst = lst[:10]
        self._setup_ui_font_(lst)

        if not ismacos and not iswindows:
            # Qt 5.10.1 on Linux resets the global font on first event loop tick.
            # So workaround it by setting the font once again in a timer.
            try:
                QTimer.singleShot(0, lambda : self._setup_ui_font_(lst))
            except Exception:
                pass

    # Install qtbase translator for standard dialogs and such.
    # Use the Sigil language setting unless manually overridden.
    def load_base_qt_translations(self):
        if not (self.bk.launcher_version() >= 20170227):  # Sigil 0.9.8
            return
        qt_translator = QTranslator()
        language_override = os.environ.get("SIGIL_PLUGIN_LANGUAGE_OVERRIDE")
        if language_override is not None:
            if DEBUG:
                print('Plugin language override in effect')
            qmf = 'qtbase_{}'.format(language_override)
        else:
            qmf = 'qtbase_{}'.format(self.bk.sigil_ui_lang)
        # Get bundled or external translations directory
        qt_trans_dir = get_qt_translations_path(self.bk._w.appdir)
        if DEBUG:
            print('Qt translation dir: {}'.format(qt_trans_dir))
            print('Looking for {} in {}'.format(qmf, qt_trans_dir))
        qt_translator.load(qmf, qt_trans_dir)
        res = self.installTranslator(qt_translator)
        if DEBUG:
            print('Qt Base Translator succesfully installed: {}'.format(res))

    # Install translator for the plugin's dialogs (if any).
    # Use the Sigil language setting unless manually overridden.
    def load_plugin_translations(self, trans_folder):
        if not (self.bk.launcher_version() >= 20170227):  # Sigil 0.9.8
            return
        plugin_translator = QTranslator()
        language_override = os.environ.get("SIGIL_PLUGIN_LANGUAGE_OVERRIDE")
        if language_override is not None:
            if DEBUG:
                print('Plugin language override in effect')
            qmf = '{}_{}'.format(self.bk._w.plugin_name.lower(), language_override)
        else:
            qmf = '{}_{}'.format(self.bk._w.plugin_name.lower(), self.bk.sigil_ui_lang)
        # Plugin *.qm files are looked for in the 'translations' folder at the root
        # of the plugin_dir by default. Override by setting an alternative location
        # with the plugin_trans_folder parameter of the Application class.
        if DEBUG:
            print('Looking for {} in {}'.format(qmf, trans_folder))
        plugin_translator.load(qmf, trans_folder)
        res = self.installTranslator(plugin_translator)
        if DEBUG:
            print('Plugin Translator succesfully installed: {}'.format(res))


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

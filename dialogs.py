#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import unicode_literals, division, absolute_import, print_function

import os
import sys
import math
import json
from pathlib import Path

from utilities import UpdateChecker, taglist, combobox_defaults, remove_dupes
from parsing_engine import MarkupParser

from plugin_utils import Qt, QtCore, QtGui, QtWidgets, QAction
from plugin_utils import PluginApplication, iswindows, _t  # , Signal, Slot, loadUi


DEBUG = 0
if DEBUG:
    if 'PySide6' in sys.modules:
        print('Plugin using PySide6')
    else:
        print('Plugin using PyQt5')

BAIL_OUT = False
PROCESSED = False


def launch_gui(bk, prefs):

    icon = os.path.join(bk._w.plugin_dir, bk._w.plugin_name, 'plugin.svg')
    mdp = True if iswindows else False
    app = PluginApplication(sys.argv, bk, app_icon=icon, match_dark_palette=mdp,
                            dont_use_native_menubars=True)

    win = guiMain(bk, prefs)
    # Use exec() and not exec_() for PyQt5/PySide6 compliance
    app.exec()
    return win.getAbort()


class ConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent, combobox_values):
        super(ConfigDialog, self).__init__()
        self.gui = parent
        self.combobox_values = combobox_values
        self.qlinedit_widgets = {}
        self.setup_ui()
        self.setWindowTitle(_t('ConfigDialog', 'Customize Tag Mechanic'))

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        columns_frame = QtWidgets.QHBoxLayout()
        layout.addLayout(columns_frame)

        # How many columns of nine items each will it take to display
        # a text box for each tag in taglist?
        col_limit = 8
        num_cols = len(taglist)/col_limit
        num_cols = int(math.ceil(num_cols))

        # If the column limit and the number of columns produces a single
        # orphan text entry widget, reduce the column limit accordingly.
        if num_cols > 1 and (len(taglist) - ((num_cols - 1)*col_limit)) < 2:
            if num_cols >= 3:
                col_limit -= 1
        # Create an integer-indexed dictionary of QVBoxLayouts representing the number of
        # columns necessary. Added left to right in the parent QHBoxLayout.
        column = {}
        for i in range(1, num_cols+1):
            column[i] = QtWidgets.QVBoxLayout()
            column[i].setAlignment(Qt.AlignLeft)
            columns_frame.addLayout(column[i])

        # Create a dictionary of QLineEdit widgets (indexed by tag name) and stack them
        # (top to bottom) and their labels in as many columns as it takes.
        curr_col = 1
        curr_item = 1
        tooltip = _t('ConfigDialog', 'Comma separated list of html elements (no quotes, no angle "&lt;" brackets).')
        for tag in taglist:
            # Column item limit surpassed - switch to next column.
            if curr_item > col_limit:
                column[curr_col].addStretch()
                curr_col += 1
                curr_item = 1
            # Add lable and QLineEdit widget to current column.
            label = QtWidgets.QLabel('{} "{}" {}'.format(
                _t('ConfigDialog', 'Choices to change'), tag,
                _t('ConfigDialog', 'elements to:')), self)
            label.setAlignment(Qt.AlignCenter)
            self.qlinedit_widgets[tag] = QtWidgets.QLineEdit(', '.join(self.combobox_values['{}_changes'.format(tag)]), self)
            self.qlinedit_widgets[tag].setToolTip('<p>{}'.format(tooltip))
            column[curr_col].addWidget(label)
            column[curr_col].addWidget(self.qlinedit_widgets[tag])

            if not len(self.combobox_values['{}_changes'.format(tag)]):
                self.qlinedit_widgets[tag].setDisabled(True)
            curr_item += 1
        column[curr_col].addStretch()

        layout.addSpacing(10)
        attrs_layout = QtWidgets.QVBoxLayout()
        attrs_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(attrs_layout)
        label = QtWidgets.QLabel(_t('ConfigDialog', 'HTML attributes available to search for:'), self)
        label.setAlignment(Qt.AlignCenter)
        self.attrs_txtBox = QtWidgets.QLineEdit(', '.join(self.combobox_values['attrs']), self)
        self.attrs_txtBox.setToolTip('<p>{}'.format(
            _t('ConfigDialog', 'Comma separated list of html attribute names (no quotes).')))
        attrs_layout.addWidget(label)
        attrs_layout.addWidget(self.attrs_txtBox)

        layout.addSpacing(10)
        right_layout = QtWidgets.QHBoxLayout()
        right_layout.setAlignment(Qt.AlignRight)
        layout.addLayout(right_layout)

        self.auto_headless = QtWidgets.QCheckBox(_t('ConfigDialog', 'Plugin runs headless in Automate Lists'), self)
        self.auto_headless.setToolTip('<p>{}'.format(
            _t('ConfigDialog', 'The GUI will not be used when the plugin is run via an Automate List')))
        self.auto_headless.setChecked(self.gui.misc_prefs['automate_runs_headless'])
        right_layout.addWidget(self.auto_headless)
        right_layout.insertSpacing(1, 30)

        reset_button = QtWidgets.QPushButton(_t('ConfigDialog', 'Reset all defaults'), self)
        reset_button.setToolTip('<p>{}'.format(_t('ConfigDialog', 'Reset all settings to original defaults.')))
        reset_button.clicked.connect(self.reset_defaults)
        right_layout.addWidget(reset_button)

        layout.addSpacing(10)
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def save_settings(self):
        # Save current dialog sttings back to JSON config file
        for tag in taglist:
            tmp_list = str(self.qlinedit_widgets[tag].displayText()).split(',')
            tmp_list = remove_dupes([x.strip(' ') for x in tmp_list])
            self.combobox_values['{}_changes'.format(tag)] = list(filter(None, tmp_list))

        tmp_list = str(self.attrs_txtBox.displayText()).split(',')
        tmp_list = remove_dupes([x.strip(' ') for x in tmp_list])
        self.combobox_values['attrs'] = list(filter(None, tmp_list))
        self.gui.misc_prefs['automate_runs_headless'] = self.auto_headless.isChecked()
        self.accept()

    def reset_defaults(self):
        caption= _t('ConfigDialog', 'Are you sure?')
        msg = '<p>{}'.format(_t('ConfigDialog', 'Reset all customizable options to their original defaults?'))
        if QtWidgets.QMessageBox.question(self, caption, msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel) == QtWidgets.QMessageBox.Yes:
            self.gui.misc_prefs['automate_runs_headless'] = False
            for tag in taglist:
                self.combobox_values['{}_changes'.format(tag)] = combobox_defaults['{}_changes'.format(tag)]
            self.combobox_values['attrs'] = combobox_defaults['attrs']
            self.accept()


class guiMain(QtWidgets.QMainWindow):
    def __init__(self, bk, prefs):
        super(guiMain, self).__init__()
        self.taglist = taglist
        # Edit Plugin container object
        self.bk = bk

        # Handy prefs groupings
        self.gui_prefs = prefs['gui_selections']
        self.misc_prefs = prefs['miscellaneous_settings']
        self.update_prefs = prefs['update_settings']
        self.combobox_values = prefs['combobox_values']

        self._ok_to_close = False
        # Check online github files for newer version
        self.update, self.newversion = self.check_for_update()
        self.setup_ui()

    def setup_ui(self):
        app = PluginApplication.instance()
        p = app.palette()
        link_color = p.color(QtGui.QPalette.Active, QtGui.QPalette.Link).name()

        DELETE_STR = _t('guiMain', 'Delete')
        MODIFY_STR = _t('guiMain', 'Modify')
        self.NO_ATTRIB_STR = _t('guiMain', 'No attributes (naked tag)')
        self.NO_CHANGE_STR = _t('guiMain', 'No change')
        self.setWindowTitle(_t('guiMain', 'Tag Mechanic'))

        configAct = QAction(_t('guiMain', 'Config'), self)
        configAct.setShortcut('Ctrl+Alt+C')
        tooltip = _t('guiMain','Configure')
        configAct.setToolTip(tooltip + ' ' + self.bk._w.plugin_name)
        icon = os.path.join(self.bk._w.plugin_dir, self.bk._w.plugin_name, 'config.svg')
        configAct.setIcon(QtGui.QIcon(icon))
        configAct.triggered.connect(self.showConfig)

        editToolBar = self.addToolBar(_t('guiMain', 'Edit'))
        editToolBar.setMovable(False)
        editToolBar.setFloatable(False)
        editToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        editToolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        editToolBar.addAction(configAct)

        layout = QtWidgets.QVBoxLayout()

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        if self.update:
            update_layout = QtWidgets.QHBoxLayout()
            layout.addLayout(update_layout)
            self.label = QtWidgets.QLabel()
            self.label.setText(_t('guiMain', 'Plugin Update Available') + ' ' + str(self.newversion))
            self.label.setStyleSheet('QLabel {{color: {};}}'.format(link_color))
            update_layout.addWidget(self.label)

        action_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(action_layout)
        label = QtWidgets.QLabel(_t('guiMain', 'Action type:'), self)
        action_layout.addWidget(label)
        self.action_combo = QtWidgets.QComboBox()
        action_layout.addWidget(self.action_combo)
        self.action_combo.addItems([DELETE_STR, MODIFY_STR])
        self.action_combo.setCurrentIndex(self.gui_prefs['action'])
        self.action_combo.currentIndexChanged.connect(self.update_gui)

        tag_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(tag_layout)
        label = QtWidgets.QLabel(_t('guiMain', 'Tag name:'), self)
        tag_layout.addWidget(label)
        self.tag_combo = QtWidgets.QComboBox()
        tag_layout.addWidget(self.tag_combo)
        self.tag_combo.addItems(self.taglist)
        self.tag_combo.setCurrentIndex(self.gui_prefs['tag'])
        self.tag_combo.currentIndexChanged.connect(self.update_gui)

        attr_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(attr_layout)
        label = QtWidgets.QLabel(_t('guiMain', 'Having the attribute:'), self)
        attr_layout.addWidget(label)
        self.attr_combo = QtWidgets.QComboBox()
        attr_layout.addWidget(self.attr_combo)
        self.attr_combo.addItems(self.combobox_values['attrs'])
        self.attr_combo.addItem(self.NO_ATTRIB_STR)
        self.attr_combo.setCurrentIndex(self.gui_prefs['attrs'])
        self.attr_combo.currentIndexChanged.connect(self.update_gui)

        srch_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(srch_layout)
        label = QtWidgets.QLabel(_t('guiMain', 'Whose value is (no quotes):'), self)
        srch_layout.addWidget(label)
        self.srch_txt = QtWidgets.QLineEdit('', self)
        srch_layout.addWidget(self.srch_txt)
        self.srch_method = QtWidgets.QCheckBox(_t('guiMain', 'Regex'), self)
        srch_layout.addWidget(self.srch_method)

        newtag_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(newtag_layout)
        label = QtWidgets.QLabel(_t('guiMain', 'Change tag to:'), self)
        newtag_layout.addWidget(label)
        self.newtag_combo = QtWidgets.QComboBox()
        newtag_layout.addWidget(self.newtag_combo)

        self.newtag_combo.addItem(self.NO_CHANGE_STR)
        self.newtag_combo.addItems(self.combobox_values['{}_changes'.format(str(self.tag_combo.currentText()))])

        if self.action_combo.currentIndex() == 0:
            self.newtag_combo.setDisabled(True)

        newattr_layout = QtWidgets.QVBoxLayout()
        layout.addLayout(newattr_layout)
        label = QtWidgets.QLabel(_t('guiMain', 'New attribute string to insert (entire):'), self)
        newattr_layout.addWidget(label)
        self.newattr_txt = QtWidgets.QLineEdit('', self)
        newattr_layout.addWidget(self.newattr_txt)
        self.copy_attr = QtWidgets.QCheckBox(_t('guiMain', 'Copy existing attribute string'), self)
        self.copy_attr.stateChanged.connect(self.update_txt_box)
        newattr_layout.addWidget(self.copy_attr)
        if self.action_combo.currentIndex() == 0:
            self.copy_attr.setDisabled(True)
            self.newattr_txt.setDisabled(True)

        layout.addSpacing(10)
        self.text_panel = QtWidgets.QTextEdit()
        self.text_panel.setReadOnly(True)
        layout.addWidget(self.text_panel)

        layout.addSpacing(10)
        first_button_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(first_button_layout)
        save_config_button = QtWidgets.QPushButton(_t('guiMain', 'Save Config'), self)
        save_config_button.setToolTip('<p>{}'.format(_t('guiMain', 'Save current config for headless use')))
        first_button_layout.addWidget(save_config_button)
        save_config_button.clicked.connect(self._save_config_clicked)

        layout.addSpacing(10)
        button_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(button_layout)
        self.process_button = QtWidgets.QPushButton(_t('guiMain', 'Process'), self)
        self.process_button.setToolTip('<p>{}'.format(_t('guiMain', 'Process selected files with current criteria')))
        self.process_button.clicked.connect(self._process_clicked)
        button_layout.addWidget(self.process_button)

        self.abort_button = QtWidgets.QPushButton(_t('guiMain', 'Abort Changes'), self)
        self.abort_button.setToolTip('<p>{}'.format(_t('guiMain', 'Make no changes and exit')))
        self.abort_button.clicked.connect(self._abort_clicked)
        self.abort_button.setDisabled(True)
        button_layout.addWidget(self.abort_button)

        self.quit_button = QtWidgets.QPushButton(_t('guiMain', 'Quit'), self)
        self.quit_button.setToolTip('<p>{}'.format(_t('guiMain', 'Quit with no changes')))
        self.quit_button.clicked.connect(self._quit_clicked)
        button_layout.addWidget(self.quit_button)

        if self.misc_prefs['windowGeometry'] is not None:
            try:
                self.restoreGeometry(QtCore.QByteArray.fromHex(self.misc_prefs['windowGeometry'].encode('ascii')))
            except Exception:
                pass
        self.show()

    def update_gui(self):
        if self.attr_combo.currentIndex() == self.attr_combo.count()-1:
            self.srch_txt.clear()
            self.srch_txt.setDisabled(True)
            self.srch_method.setChecked(False)
            self.srch_method.setDisabled(True)
        else:
            self.srch_txt.setDisabled(False)
            self.srch_method.setDisabled(False)

        self.newtag_combo.clear()
        self.newtag_combo.addItem(self.NO_CHANGE_STR)
        self.newtag_combo.addItems(self.combobox_values['{}_changes'.format(str(self.tag_combo.currentText()))])

        if self.action_combo.currentIndex() == 0:
            self.newtag_combo.setCurrentIndex(0)
            self.newtag_combo.setDisabled(True)
            self.newattr_txt.clear()
            self.newattr_txt.setDisabled(True)
            self.copy_attr.setChecked(False)
            self.copy_attr.setDisabled(True)
        else:
            self.newtag_combo.setDisabled(False)
            self.newattr_txt.setDisabled(False)
            self.copy_attr.setDisabled(False)

        self.update_txt_box()

    def update_txt_box(self):
        if self.copy_attr.isChecked() or not self.copy_attr.isEnabled():
            self.newattr_txt.clear()
            self.newattr_txt.setDisabled(True)
        else:
            self.newattr_txt.setDisabled(False)

    def refresh_attr_values(self):
        self.attr_combo.clear()
        self.attr_combo.addItems(self.combobox_values['attrs'])
        self.attr_combo.addItem(self.NO_ATTRIB_STR)

    def validate(self):
        criteria = {}
        criteria['tag'] = str(self.tag_combo.currentText())
        if self.action_combo.currentIndex() == 0:
            criteria['action'] = 'delete'
        else:
            criteria['action'] = 'modify'
        if self.attr_combo.currentIndex() == self.attr_combo.count()-1:
            criteria['attrib'] = None
        else:
            criteria['attrib'] = str(self.attr_combo.currentText())
        srch_str = str(self.srch_txt.displayText())
        if not len(srch_str):
            srch_str = None
        if srch_str is None and criteria['attrib'] is not None:
            title = _t('guiMain', 'Error')
            msg = '<p>{0}'.format(
                _t('guiMain', 'Must enter a value for the attribute selected'))
            return (QtWidgets.QMessageBox.warning(self, title, msg, QtWidgets.QMessageBox.Ok), {})
        criteria['srch_str'] = srch_str

        criteria['srch_method'] = 'normal'
        if self.srch_method.isChecked():
            criteria['srch_method'] = 'regex'
        if self.newtag_combo.currentIndex() == 0:
            criteria['new_tag'] = None
        else:
            criteria['new_tag'] = str(self.newtag_combo.currentText())
        if criteria['action'] == 'modify' and criteria['new_tag'] is None and self.copy_attr.isChecked():
            title = _t('guiMain', 'Error')
            msg = '<p>{0}'.format(
                _t('guiMain', 'What--exactly--would that achieve?'))
            return (QtWidgets.QMessageBox.question(self, title, msg, QtWidgets.QMessageBox.Ok), {})

        criteria['new_str'] = str(self.newattr_txt.displayText())
        criteria['copy'] = False
        if self.copy_attr.isChecked():
            criteria['copy'] = True
        if not len(criteria['new_str']):
            criteria['new_str'] = ''
        return (None, criteria)

    def _process_clicked(self):
        error, criteria = self.validate()
        if error is not None:
            return
        global PROCESSED

        # Disable the 'Process' button, disable the context customization menu
        self.process_button.setDisabled(True)
        PROCESSED = True

        totals = 0
        self.text_panel.clear()
        self.text_panel.insertHtml('<h4>{}...</h4><br>'.format(_t('guiMain', 'Starting')))

        # Loop through the files selected in Sigil's Book View
        for (typ, ident) in self.bk.selected_iter():
            # Skip the ones that aren't the "Text" mimetype.
            if self.bk.id_to_mime(ident) != 'application/xhtml+xml':
                continue
            href = self.bk.id_to_href(ident)
            # Param 1 - the contents of the (x)html file.
            criteria['html'] = self.bk.readfile(ident)
            if not isinstance(criteria['html'], str):
                criteria['html'] = str(criteria['html'], 'utf-8')

            # Hand off the "criteria" parameters dictionary to the parsing engine
            parser = MarkupParser(criteria)

            # Retrieve the new markup and the number of occurrences changed
            try:
                html, occurrences = parser.processml()
            except Exception:
                self.text_panel.insertHtml('<p>{} {}! {}.</p>\n'.format(
                        _t('guiMain', 'Error parsing'), href, _t('guiMain', 'File skipped')))
                continue

            # Report whether or not changes were made (and how many)
            totals += occurrences
            if occurrences:
                # write changed markup back to file
                self.bk.writefile(ident, html)
                self.text_panel.insertHtml('<p>{} {}:&#160;&#160;&#160;{}</p>'.format(
                    _t('guiMain', 'Occurrences found/changed in'), href, int(occurrences)))
            else:
                self.text_panel.insertHtml('<p>{} {}</p>\n'.format(
                    _t('guiMain', 'Criteria not found in'), href))
            self.text_panel.insertPlainText('\n')

        # report totals
        if totals:
            self.quit_button.setText(_t('guiMain', 'Commit and Exit'))
            self.quit_button.setToolTip('<p>{}'.format(_t('guiMain', 'Commit all changes and exit')))
            self.abort_button.setDisabled(False)
            self.text_panel.insertHtml('<br><h4>{}:&#160;&#160;&#160;{}</h4>'.format(
                _t('guiMain', 'Total occurrences found/changed'), int(totals)))
        else:
            self.text_panel.insertHtml('<br><h4>{}</h4>'.format(
                _t('guiMain', 'No changes made to book')))
        self.text_panel.insertHtml('<br><h4>{}</h4>'.format(_t('guiMain', 'Finished')))

    def _save_config_clicked(self):
        error, criteria = self.validate()
        if error is not None:
            return
        two_up = Path(self.bk._w.plugin_dir).resolve().parents[0]
        headless_prefs = two_up.joinpath('plugins_prefs', self.bk._w.plugin_name, 'headless.json')
        with open(headless_prefs, 'w', encoding='utf-8') as f:
            json.dump(criteria, f, indent=2, ensure_ascii=False)

    def _quit_clicked(self):
        self.misc_prefs['windowGeometry'] = self.saveGeometry().toHex().data().decode('ascii')
        if PROCESSED:
            self.gui_prefs['action'] = self.action_combo.currentIndex()
            self.gui_prefs['tag'] = self.tag_combo.currentIndex()
            self.gui_prefs['attrs'] = self.attr_combo.currentIndex()
        self._ok_to_close = True
        self.close()

    def _abort_clicked(self):
        global BAIL_OUT
        BAIL_OUT = True
        self._ok_to_close = True
        self.close()

    def getAbort(self):
        return BAIL_OUT

    def showConfig(self):
        ''' Launch Customization Dialog '''
        dlg = ConfigDialog(self, self.combobox_values)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            self.refresh_attr_values()
            self.update_gui()

    def check_for_update(self):
        '''Use updatecheck.py to check for newer versions of the plugin'''
        last_time_checked = self.update_prefs['last_time_checked']
        last_online_version = self.update_prefs['last_online_version']
        chk = UpdateChecker(last_time_checked, last_online_version, self.bk._w)
        update_available, online_version, time = chk.update_info()
        # update preferences with latest date/time/version
        self.update_prefs['last_time_checked'] = time
        if online_version is not None:
            self.update_prefs['last_online_version'] = online_version
        if update_available:
            return (True, online_version)
        return (False, online_version)

    def closeEvent(self, event):
        if self._ok_to_close:
            event.accept()  # let the window close
        else:
            self._abort_clicked()


def main():
    return -1


if __name__ == "__main__":
    sys.exit(main())

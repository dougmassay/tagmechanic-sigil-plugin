#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import unicode_literals, division, absolute_import, print_function

import sys
import math
from compatibility_utils import PY2


if PY2:
    import Tkinter as tkinter
    import Tkconstants as tkinter_constants
    import tkFont
    range = xrange
else:
    import tkinter
    import tkinter.constants as tkinter_constants
    import tkinter.font as tkFont


def remove_dupes(values):
    '''Could just use set(), but some combobox values are preloaded
       from prefs using an index. So order matters'''
    output = []
    seen = set()
    for value in values:
        # If value has not been encountered yet,
        # ... add it to both list and set.
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output

class guiConfig(tkinter.Toplevel):
    def __init__(self, parent, defaults, font_tweaks):
        tkinter.Toplevel.__init__(self, parent, border=5)
        self.resizable(False, False)
        self.title('Plugin Customization')
        self.maingui = parent
        # define a bold font based on font_tweaks for labels
        self.label_font = tkFont.Font(family=font_tweaks['font_family'], size=int(font_tweaks['font_size']), weight=tkFont.BOLD)
        # Copy taglist, combox values and their original defaults from main plugin.py
        self.taglist = self.maingui.taglist
        self.temp_values = self.maingui.combobox_values
        self.defaults = defaults
        self.tkinter_vars = {}
        self.tkentry_widgets = {}

        self.initUI()

    def initUI(self):
        ''' Build the GUI and assign variables and handler functions to elements. '''
        body = tkinter.Frame(self)
        body.pack(fill=tkinter_constants.BOTH)
        columns_frame = tkinter.Frame(body)
        columns_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)

        # How many columns of nine items each will it take to display
        # a text box for each tag in taglist?
        col_limit = 9
        num_cols = len(self.taglist)/col_limit
        num_cols = int(math.ceil(num_cols))

        # If the column limit and the number of columns produces a single orphan
        # text entry widget, reduce/increase the column limit accordingly.
        if num_cols > 1 and (len(self.taglist) - ((num_cols - 1)*col_limit)) < 2:
            if num_cols >= 3:
                col_limit -= 1

        # Create an integer-indexed dictionary of frames representing the number of
        # columns necessary. Packed left to right in the parent frame.
        column = {}
        for i in range(1, num_cols+1):
            column[i] = tkinter.Frame(columns_frame, bd=2, padx=3,  relief=tkinter_constants.GROOVE)
            column[i].pack(side=tkinter_constants.LEFT, fill=tkinter_constants.BOTH)

        # Create a dictionary of text entry widgets (indexed by tag name) and pack them
        # (top to bottom) and their labels in as many columns as it takes.
        curr_col = 1
        curr_item = 1
        for tag in self.taglist:
            # Column item limit surpassed - switch to next column.
            if curr_item > col_limit:
                curr_col += 1
                curr_item = 1
            # Add label and text entry widget to current column.
            entry_frame = tkinter.Frame(column[curr_col], pady=5)
            lbl = tkinter.Label(entry_frame, text='Choices to change "{}" elements to:'.format(tag),
                                font=self.label_font)
            lbl.pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
            self.tkinter_vars[tag] = tkinter.StringVar()
            self.tkentry_widgets[tag] = tkinter.Entry(entry_frame, textvariable=self.tkinter_vars[tag])
            self.tkentry_widgets[tag].pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
            entry_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)
            curr_item += 1

        # Create the label/text-entry widget for the html attributes list
        attrs_frame = tkinter.Frame(body, pady=10)
        attrs_label = tkinter.Label(attrs_frame, text='HTML attributes available to search for:',
                                    font=self.label_font)
        attrs_label.pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
        self.attrs_value = tkinter.StringVar()
        self.attrs_value_entry = tkinter.Entry(attrs_frame, textvariable=self.attrs_value)
        self.attrs_value_entry.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.X)
        attrs_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)

        # Dialog buttonbox (three buttons)
        buttons = tkinter.Frame(body)
        self.gbutton = tkinter.Button(buttons, text='Apply and Close', command=self.cmdDo)
        self.gbutton.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.BOTH, expand=True)
        self.qbutton = tkinter.Button(buttons, text='Cancel', command=self.cmdCancel)
        self.qbutton.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.BOTH, expand=True)
        self.dbutton = tkinter.Button(buttons, text='Reset Defaults', command=self.cmdDefaults)
        self.dbutton.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.BOTH, expand=True)
        buttons.pack(side=tkinter_constants.BOTTOM, pady=5, fill=tkinter_constants.BOTH)

        # Call the method that populates the textboxes
        self.populate(self.temp_values)

        # This is bullshit that needs to be done to make the config dialog take
        # focus from the main gui. Main should be helpless until config closes. Ugh!
        self.withdraw()
        self.transient(self.maingui)
        self.grab_set()
        self.center()
        self.deiconify()
        self.maingui.wait_window(self)

    def center(self):
        '''Center the config window'''
        # OMG centering windows with Tkinter sucks rocks!!
        self.update()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = self.winfo_screenwidth() // 2 - w // 2
        y = self.winfo_screenheight() // 2 - h // 2
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def populate(self, values):
        '''Populate the text entry boxes'''
        for tag in self.taglist:
            self.tkentry_widgets[tag].config(state='normal')
            self.tkentry_widgets[tag].delete(0, tkinter_constants.END)
            self.tkentry_widgets[tag].insert(0, ', '.join(values['{}_changes'.format(tag)]))
            if not len(values['{}_changes'.format(tag)]):
                self.tkentry_widgets[tag].config(state='disabled')

        self.attrs_value_entry.delete(0, tkinter_constants.END)
        self.attrs_value_entry.insert(0, ', '.join(values['attrs']))

    def cmdCancel(self):
        '''Close aborting any changes'''
        self.quitApp()

    def cmdDefaults(self):
        '''Reset all settings to original plugin defaults'''
        self.populate(self.defaults)

    def cmdDo(self):
        '''Grab any changes and store them'''
        for tag in self.taglist:
            tmp_list = self.tkinter_vars[tag].get().strip(' ').split(',')
            self.temp_values['{}_changes'.format(tag)] = remove_dupes([x.strip(' ') for x in tmp_list if x])

        tmp_list = self.attrs_value.get().strip(' ').split(',')
        self.temp_values['attrs'] = remove_dupes([x.strip(' ') for x in tmp_list if x])

        # Copy the temp settings back to the main gui's value prefs
        self.maingui.combobox_values = self.temp_values

        # Refresh the main gui's comboboxes and close
        self.maingui.tag_change_actions(None)
        self.maingui.update_attrs_combo()
        self.quitApp()

    def quitApp(self):
        '''Clean up and close Widget'''
        self.grab_release()
        self.destroy()


def main():

    return 0


if __name__ == "__main__":
    sys.exit(main())

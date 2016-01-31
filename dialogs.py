#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import unicode_literals, division, absolute_import, print_function

import sys

PY2 = sys.version_info[0] == 2

if PY2:
    import Tkinter as tkinter
    import Tkconstants as tkinter_constants
    text_type = unicode
else:
    import tkinter
    import tkinter.constants as tkinter_constants
    text_type = str

class guiConfig(tkinter.Toplevel):

    def __init__(self, parent, defaults):
        tkinter.Toplevel.__init__(self, parent, border=5)
        self.resizable(False, False)
        self.title('Plugin Customization')
        self.maingui = parent
        self.temp_values = self.maingui.combobox_values
        self.defaults = defaults

        self.initUI()

        # self.protocol('WM_DELETE_WINDOW', self.quitApp)

    def initUI(self):
        ''' Build the GUI and assign variables and handler functions to elements. '''
        body = tkinter.Frame(self)
        body.pack(fill=tkinter_constants.BOTH)

        span_frame = tkinter.Frame(body, pady=3)
        span_label = tkinter.Label(span_frame, text='Choices to change "span" elements to:')
        span_label.pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
        self.span_value = tkinter.StringVar()
        self.span_value_entry = tkinter.Entry(span_frame, textvariable=self.span_value)
        self.span_value_entry.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.X)
        span_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)

        div_frame = tkinter.Frame(body, pady=3)
        div_label = tkinter.Label(div_frame, text='Choices to change "div" elements to:')
        div_label.pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
        self.div_value = tkinter.StringVar()
        self.div_value_entry = tkinter.Entry(div_frame, textvariable=self.div_value)
        self.div_value_entry.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.X)
        div_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)

        i_frame = tkinter.Frame(body, pady=3)
        i_label = tkinter.Label(i_frame, text='Choices to change "i" elements to:')
        i_label.pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
        self.i_value = tkinter.StringVar()
        self.i_value_entry = tkinter.Entry(i_frame, textvariable=self.i_value)
        self.i_value_entry.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.X)
        i_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)

        em_frame = tkinter.Frame(body, pady=3)
        em_label = tkinter.Label(em_frame, text='Choices to change "em" elements to:')
        em_label.pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
        self.em_value = tkinter.StringVar()
        self.em_value_entry = tkinter.Entry(em_frame, textvariable=self.em_value)
        self.em_value_entry.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.X)
        em_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)

        b_frame = tkinter.Frame(body, pady=3)
        b_label = tkinter.Label(b_frame, text='Choices to change "b" elements to:')
        b_label.pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
        self.b_value = tkinter.StringVar()
        self.b_value_entry = tkinter.Entry(b_frame, textvariable=self.b_value)
        self.b_value_entry.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.X)
        b_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)

        strong_frame = tkinter.Frame(body, pady=3)
        strong_label = tkinter.Label(strong_frame, text='Choices to change "strong" elements to:')
        strong_label.pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
        self.strong_value = tkinter.StringVar()
        self.strong_value_entry = tkinter.Entry(strong_frame, textvariable=self.strong_value)
        self.strong_value_entry.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.X)
        strong_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)

        u_frame = tkinter.Frame(body, pady=3)
        u_label = tkinter.Label(u_frame, text='Choices to change "u" elements to:')
        u_label.pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
        self.u_value = tkinter.StringVar()
        self.u_value_entry = tkinter.Entry(u_frame, textvariable=self.u_value)
        self.u_value_entry.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.X)
        u_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)

        a_frame = tkinter.Frame(body, pady=3)
        a_label = tkinter.Label(a_frame, text='Choices to change "a" elements to:')
        a_label.pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
        self.a_value = tkinter.StringVar()
        self.a_value_entry = tkinter.Entry(a_frame, textvariable=self.a_value)
        self.a_value_entry.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.X)
        a_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)
        self.a_value_entry.config(state='disabled')

        small_frame = tkinter.Frame(body, pady=3)
        small_label = tkinter.Label(small_frame, text='Choices to change "small" elements to:')
        small_label.pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
        self.small_value = tkinter.StringVar()
        self.small_value_entry = tkinter.Entry(small_frame, textvariable=self.small_value)
        self.small_value_entry.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.X)
        small_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)

        section_frame = tkinter.Frame(body, pady=3)
        section_label = tkinter.Label(section_frame, text='Choices to change "section" elements to:')
        section_label.pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
        self.section_value = tkinter.StringVar()
        self.section_value_entry = tkinter.Entry(section_frame, textvariable=self.section_value)
        self.section_value_entry.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.X)
        section_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)

        blockquote_frame = tkinter.Frame(body, pady=3)
        blockquote_label = tkinter.Label(blockquote_frame, text='Choices to change "blockquote" elements to:')
        blockquote_label.pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
        self.blockquote_value = tkinter.StringVar()
        self.blockquote_value_entry = tkinter.Entry(blockquote_frame, textvariable=self.blockquote_value)
        self.blockquote_value_entry.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.X)
        blockquote_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)

        attrs_frame = tkinter.Frame(body, pady=3)
        attrs_label = tkinter.Label(attrs_frame, text='Attributes to search for in html elements:')
        attrs_label.pack(side=tkinter_constants.TOP, fill=tkinter_constants.X)
        self.attrs_value = tkinter.StringVar()
        self.attrs_value_entry = tkinter.Entry(attrs_frame, textvariable=self.attrs_value)
        self.attrs_value_entry.pack(side=tkinter_constants.BOTTOM, fill=tkinter_constants.X)
        attrs_frame.pack(side=tkinter_constants.TOP, fill=tkinter_constants.BOTH)

        buttons = tkinter.Frame(body)
        self.gbutton = tkinter.Button(buttons, text='Apply and Close', command=self.cmdDo)
        self.gbutton.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.BOTH, expand=True)
        self.qbutton = tkinter.Button(buttons, text='Cancel', command=self.cmdCancel)
        self.qbutton.pack(side=tkinter_constants.LEFT, fill=tkinter_constants.BOTH, expand=True)
        self.dbutton = tkinter.Button(buttons, text='Reset Defaults', command=self.cmdDefaults)
        self.dbutton.pack(side=tkinter_constants.RIGHT, fill=tkinter_constants.BOTH, expand=False)
        buttons.pack(side=tkinter_constants.BOTTOM, pady=5, fill=tkinter_constants.BOTH)

        self.populate(self.temp_values)

        self.withdraw()
        self.transient(self.maingui)
        self.grab_set()
        self.center()
        self.deiconify()
        self.maingui.wait_window(self)

    def center(self):
        self.update()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = self.winfo_screenwidth() // 2 - w // 2
        y = self.winfo_screenheight() // 2 - h // 2
        self.geometry('{}x{}+{}+{}'.format(w, h, x, y))

    def populate(self, values):
        self.span_value_entry.delete(0, tkinter_constants.END)
        self.span_value_entry.insert(0, ', '.join(values['span_changes']))
        self.div_value_entry.delete(0, tkinter_constants.END)
        self.div_value_entry.insert(0, ', '.join(values['div_changes']))
        self.i_value_entry.delete(0, tkinter_constants.END)
        self.i_value_entry.insert(0, ', '.join(values['i_changes']))
        self.em_value_entry.delete(0, tkinter_constants.END)
        self.em_value_entry.insert(0, ', '.join(values['em_changes']))
        self.b_value_entry.delete(0, tkinter_constants.END)
        self.b_value_entry.insert(0, ', '.join(values['b_changes']))
        self.strong_value_entry.delete(0, tkinter_constants.END)
        self.strong_value_entry.insert(0, ', '.join(values['strong_changes']))
        self.u_value_entry.delete(0, tkinter_constants.END)
        self.u_value_entry.insert(0, ', '.join(values['u_changes']))

        self.a_value_entry.config(state='normal')
        self.a_value_entry.delete(0, tkinter_constants.END)
        self.a_value_entry.insert(0, ', '.join(values['a_changes']))
        self.a_value_entry.config(state='disabled')

        self.small_value_entry.delete(0, tkinter_constants.END)
        self.small_value_entry.insert(0, ', '.join(values['small_changes']))
        self.section_value_entry.delete(0, tkinter_constants.END)
        self.section_value_entry.insert(0, ', '.join(values['sec_changes']))
        self.blockquote_value_entry.delete(0, tkinter_constants.END)
        self.blockquote_value_entry.insert(0, ', '.join(values['block_changes']))
        self.attrs_value_entry.delete(0, tkinter_constants.END)
        self.attrs_value_entry.insert(0, ', '.join(values['attrs']))

    def cmdCancel(self):
        self.quitApp()

    def cmdDefaults(self):
        self.populate(self.defaults)

    def cmdDo(self):
        tmp_list = self.span_value.get().strip(' ').split(',')
        self.temp_values['span_changes'] = [x.strip(' ') for x in tmp_list if x]

        tmp_list = self.div_value.get().strip(' ').split(',')
        self.temp_values['div_changes'] = [x.strip(' ') for x in tmp_list if x]

        tmp_list = self.i_value.get().strip(' ').split(',')
        self.temp_values['i_changes'] = [x.strip(' ') for x in tmp_list if x]

        tmp_list = self.em_value.get().strip(' ').split(',')
        self.temp_values['em_changes'] = [x.strip(' ') for x in tmp_list if x]

        tmp_list = self.b_value.get().strip(' ').split(',')
        self.temp_values['b_changes'] = [x.strip(' ') for x in tmp_list if x]

        tmp_list = self.strong_value.get().strip(' ').split(',')
        self.temp_values['strong_changes'] = [x.strip(' ') for x in tmp_list if x]

        tmp_list = self.u_value.get().strip(' ').split(',')
        self.temp_values['u_changes'] = [x.strip(' ') for x in tmp_list if x]

        tmp_list = self.a_value.get().strip(' ').split(',')
        self.temp_values['a_changes'] = [x.strip(' ') for x in tmp_list if x]

        tmp_list = self.small_value.get().strip(' ').split(',')
        self.temp_values['small_changes'] = [x.strip(' ') for x in tmp_list if x]

        tmp_list = self.section_value.get().strip(' ').split(',')
        self.temp_values['sec_changes'] = [x.strip(' ') for x in tmp_list if x]

        tmp_list = self.blockquote_value.get().strip(' ').split(',')
        self.temp_values['block_changes'] = [x.strip(' ') for x in tmp_list if x]

        tmp_list = self.attrs_value.get().strip(' ').split(',')
        self.temp_values['attrs'] = [x.strip(' ') for x in tmp_list if x]

        self.maingui.combobox_values = self.temp_values

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

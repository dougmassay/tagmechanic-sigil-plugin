#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

from __future__ import unicode_literals, division, absolute_import, print_function

import sys
import os
import json
from pathlib import Path

from dialogs import launch_gui
from parsing_engine import MarkupParser
from utilities import setupPrefs, check_for_custom_icon, get_icon_color, change_icon_color


prefs = {}


def run(bk):
    # before Sigil 0.8.900 and plugin launcher 20150909, bk.selected_iter doesn't exist.
    if bk.launcher_version() < 20150909:
        print('Error: The %s plugin requires Sigil version 0.8.900 or higher.' % bk._w.plugin_name)
        return -1

    # Fail if no Text files are selected in Sigil's Book Browser
    count = 0
    for (typ, ident) in bk.selected_iter():
        if bk.id_to_mime(ident) == 'application/xhtml+xml':
            count += 1
    if not count:
        print('No text files selected in Book Browser!')
        return -1

    global prefs

    prefs = bk.getPrefs()
    prefs = setupPrefs(prefs)

    prefs_folder = os.path.join(os.path.dirname(bk._w.plugin_dir), "plugins_prefs", bk._w.plugin_name)
    if not check_for_custom_icon(prefs_folder):
        svg = os.path.join(bk._w.plugin_dir, bk._w.plugin_name, "plugin.svg")
        if os.path.exists(svg) and os.path.isfile(svg):
            original_color = get_icon_color(svg)
            new_color = prefs['miscellaneous_settings']['icon_color']
            if original_color is not None and original_color != new_color:
                try:
                    change_icon_color(svg, original_color, new_color)
                    prefs['miscellaneous_settings']['icon_color'] = new_color
                except Exception:
                    print('Couldn\'t change icon color!')

    if not bk._w.using_automate or (bk._w.using_automate and not prefs['miscellaneous_settings']['automate_runs_headless']):

        bailOut = launch_gui(bk, prefs)

        # Save prefs to back to json
        bk.savePrefs(prefs)
        if bailOut:
            print('Nothing changed.\n')
            return -1
        return 0

    if bk._w.automate_parameter.strip() == '':
        print('Automate parameter not set')
        return -1
    else:
        print('Processing headless run with: ' + bk._w.automate_parameter)
        ''' Process headless run '''
        two_up = Path(bk._w.plugin_dir).resolve().parents[0]
        headless_prefs = two_up.joinpath('plugins_prefs', bk._w.plugin_name, 'headless.json')
        if headless_prefs.exists and headless_prefs.is_file():
            with open(headless_prefs, 'r', encoding='utf-8') as f:
                criteria = json.load(f)
            totals = 0
            # Loop through all text files in epub
            for (ident, href) in bk.text_iter():
                # Param 1 - the contents of the (x)html file.
                criteria['html'] = bk.readfile(ident)
                if not isinstance(criteria['html'], str):
                    criteria['html'] = str(criteria['html'], 'utf-8')

                # Hand off the "criteria" parameters dictionary to the parsing engine
                parser = MarkupParser(criteria)

                # Retrieve the new markup and the number of occurrences changed
                try:
                    html, occurrences = parser.processml()
                except Exception:
                    print('{} {}! {}.\n'.format(
                        'Error parsing', href, 'File skipped'))
                    continue

                # Report whether or not changes were made (and how many)
                totals += occurrences
                if occurrences:
                    # write changed markup back to file
                    bk.writefile(ident, html)
                    print('{} {}:   {}'.format(
                        'Occurrences found/changed in', href, int(occurrences)))
                else:
                    print('{} {}\n'.format(
                        'Criteria not found in', href))
        else:
            print('"headless.json" file does not exist in the plugin prefs directory')
            return -1
    return 0


def main():
    return -1


if __name__ == "__main__":
    sys.exit(main())

TagMechanic (A Sigil Plugin)
============

A Sigil plugin that helps users manipulate/remove spans, divs and other elements based on their attributes (or lack thereof) in a nesting-safe manner.

**NOTE: this plugin periodically checks for updated versions by connecting to this Github repository**

Links
=====

* Sigil website is at http://sigil-ebook.com
* The TagMechanic plugin support thread on MobileRead: <http://www.mobileread.com/forums/showthread.php?t=270639>


Building
========

First, clone the repo and cd into it:

    $ git clone https://github.com/dougmassay/tagmechanic-sigil-plugin.git
    $ cd ./tagmechanic-sigil-plugin


To create the plugin zip file, run the buildplugin.py script (root of the repository tree) with Python (2 or 3)

    $./buildplugin (so long as buildplugin's executable bit is set, otherwise ... $python ./buildplugin)

This will create the TagMechanic_vX.X.X.zip file that can then be installed into Sigil's plugin manager.

Contributing / Modifying
============
From here on out, a proficiency with developing / creating Sigil plugins is assumed.
If you need a crash-course, an introduction to creating Sigil plugins is available at
http://www.mobileread.com/forums/showthread.php?t=251452.


The core plugin files (this is where most contributors will spend their time) are:

    > dialogs.py
    > plugin.png
    > plugin.svg
    > parsing_engine.py
    > plugin.py
    > plugin.xml
    > utilities.py


Files used for building/maintaining the plugin:

    > buildplugin  -- this is used to build the plugin.
    > checkversion.xml -- used by automatic update checking (not yet implemented).
    > setup.cfg -- used for flake8 style and PEP checking. Use it to see if your code complies.
    (if my setup.cfg doesn't bark about it, then I don't care about it)

Feel free to fork the repository and submit pull requests (or just use it privately to experiment).

Files used for translations:
    > translations/template.ts

To any potential volunteer translators: There's nothing terribly complicated. Just a bunch of strings strings that probably won't be changing much (if at all) in the future. Contact me if you're interested in translating the plugin. The gist is this: fork the repo; copy the template.ts file (in the translations folder) to tagmechanic_(pl|es|fr).ts (or whatever your language's code is) and use Qt's Linguist to translate the strings. Then submit a pull request and I'll compile the language files for use in the plugin.


License Information
=======

### TagMechanic (a Sigil plugin)

    Licensed under the GPLv3.



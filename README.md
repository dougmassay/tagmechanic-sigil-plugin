TagMechanic (A Sigil Plugin)
============

A Sigil plugin that helps users manipulate/remove spans, divs and other elements based on their attributes (or lack thereof) in a nesting-safe manner.


Links
=====

* Sigil website is at http://sigil-ebook.com
* The Tooltip for Tkinter script can be found at http://code.activestate.com/recipes/576688-tooltip-for-tkinter/


Building
========

First, clone the repo and cd into it:

    $ git clone https://github.com/dougmassay/tagmechanic-sigil-plugin.git
    $ cd ./tagmechanic-sigil-plugin
    $ cd ..

To create the plugin zip file, run the buildplugin.py script (root of the repository tree) with Python (2 or 3)

    $python buildplugin.py
    
This will create the TagMechanic_vX.X.X.zip file that can then be installed into Sigil's plugin manager.
    
Contributing / Modifying
============
From here on out, a proficiency with developing / creating Sigil plugins is assumed.
If you need a crash-course, an introduction to creating Sigil plugins is available at
http://www.mobileread.com/forums/showthread.php?t=251452.


The core plugin files (this is where most contributors will spend their time) are:

    > dialogs.py
    > images/icon.png
    > parsing_engine.py
    > plugin.py
    > plugin.xml
    > tk_tooltips.py
    > updatecheck.py

    
Files used for building/maintaining the plugin:

    > buildplugin.py  -- this is used to build the plugin.
    > checkversion.xml -- used by automatic update checking (not yet implemented).
    > setup.cfg -- used for flake8 style and PEP checking. Use it to see if your code complies.
    (if my setup.cfg doesn't bark about it, then I don't care about it)

Feel free to fork the repository and submit pull requests (or just use it privately to experiment).



License Information
=======

###TagMechanic (a Sigil plugin)

    Licensed under the GPLv3.
    
###Tooltip for Tkinter
    
    Created by Tucker Beck
    Licensed under the MIT license


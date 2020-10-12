**Maintenance**

Translation updates: after changing the source-code an before releasing a new version, make sure to update each of the .ts files in the translation folder.

From the root of the repository run:

`pylupdate5 -verbose -translate-function _t *.py -ts ./translations/template.ts`

Do that for each of the .ts files.

If no translataion strings were added or changed, that's it. Only the line numbers were adjusted and the buildplugin script will compile them and add them to the plugin.

If translation strings WERE added or changed, then volunteers will need to check/update their language's ts file before releasing the plugin.
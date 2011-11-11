import commands
import os
import jsbeautifier
import sublime
import sublime_plugin

class BeautifierCommand(sublime_plugin.TextCommand):

    def phpOptions(self, settings, settings_core):
        opts = []
        if settings_core.get("translate_tabs_to_spaces", True):
            opts.append('--indent_spaces')
        else:
            opts.append('--indent_tabs')
        opts.append(str(settings_core.get("tab_size", 2)))

        opts.append('--filters \'')
        if settings.get("php_ArrayNested", True):
            opts.append('ArrayNested()')
        if settings.get("php_DocBlock", True):
            opts.append('DocBlock()')
        if settings.get("php_NewLines", True):
            opts.append('NewLines(before=switch:while:T_COMMENT:for:foreach:T_CLASS:return:break,after=T_COMMENT:protected:private)')
        return opts

    def run(self, edit):
        settings = sublime.load_settings('Beautifier.sublime-settings')
        settings_core = self.view.settings()
        FILE = self.view.file_name()
        if FILE[-4:] == '.php':
            print __name__ + ' Calling php_beautifier'

            opts = self.phpOptions(settings, settings_core)
            opts.append('\'')

            selection = self.view.sel()[0]
            replaceRegion = selection if len(selection) > 0 else sublime.Region(0, self.view.size())
            f = open(FILE + "~", 'w')
            f.write(self.view.substr(replaceRegion))
            f.close()
            cmd = "php_beautifier " + " ".join(opts) + "--input " + FILE + "~ --output -"
            print __name__ + ' ' + cmd
            res = commands.getoutput(cmd)
            resu = unicode(res, "utf-8")
            os.remove(FILE + "~")
            self.view.replace(edit, replaceRegion, resu)

        if FILE[-3:] == '.js':
            print __name__ + 'Calling jsbeautifier'

            opts = jsbeautifier.default_options()

            if settings_core.get("translate_tabs_to_spaces", True) == False:
                opts.indent_char = "\t"
            opts.indent_size = settings_core.get("tab_size", 2)

            opts.preserve_newlines = settings.get("js_preserve_newlines")
            opts.max_preserve_newlines = settings.get("js_max_preserve_newlines")
            opts.jslint_happy = settings.get("js_jslint_happy")
            opts.brace_style = settings.get("js_brace_style")

            selection = self.view.sel()[0]
            replaceRegion = selection if len(selection) > 0 else sublime.Region(0, self.view.size())
            res = jsbeautifier.beautify(self.view.substr(replaceRegion), opts)
            prePos = self.view.sel()[0]
            self.view.replace(edit, replaceRegion, res)
            self.view.show_at_center(prePos.begin())

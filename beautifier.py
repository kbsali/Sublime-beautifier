import commands, os
import jsbeautifier
import sublime, sublime_plugin

class BeautifierCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        FILE = self.view.file_name()
        if FILE[-4:] == '.php':
            print __name__ + ' Calling php_beautifier'
            PHP_OPTIONS = "-s4 --filters \'ArrayNested() DocBlock() NewLines(before=switch:while:T_COMMENT:for:foreach:T_CLASS:return:break,after=T_COMMENT:protected:private)\' "
            selection = self.view.sel()[0]
            replaceRegion = selection if len(selection) > 0 else sublime.Region(0, self.view.size())
            f = open(FILE + "~", 'w')
            f.write(self.view.substr(replaceRegion))
            f.close()
            cmd = "php_beautifier " + PHP_OPTIONS + "--input " + FILE + "~ --output -"
            print __name__ + ' ' + cmd
            res = commands.getoutput(cmd)
            resu = unicode(res, "utf-8" )
            os.remove(FILE + "~")
            self.view.replace(edit, replaceRegion, resu)
        if FILE[-3:] == '.js':
            print __name__ + 'Calling jsbeautifier'
            opts = jsbeautifier.default_options();
            opts.indent_char = "\t"
            opts.indent_size = 1
            opts.max_preserve_newlines = 3
            selection = self.view.sel()[0]
            replaceRegion = selection if len(selection) > 0 else sublime.Region(0, self.view.size())
            res = jsbeautifier.beautify(self.view.substr(replaceRegion), opts)
            prePos = self.view.sel()[0]
            self.view.replace(edit, replaceRegion, res)
            self.view.show_at_center(prePos.begin())

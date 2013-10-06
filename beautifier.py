import os
import subprocess
import shlex
import jsbeautifier
import sublime
import sublime_plugin

class BeautifierCommand(sublime_plugin.TextCommand):

    INDENT_STYLES = ("k&r", "allman", "bsd", "whitesmiths", "gnu")
    BRACE_STYLES = ("collapse", "expand", "end-expand")
    NEW_LINE_TYPES = ("switch", "while", "T_COMMENT", "for", "foreach", "T_CLASS", "break", "protected", "private", "public", "return")

    def run(self, edit):
        self.edit = edit
        self.settings = sublime.load_settings('Beautifier.sublime-settings')
        self.settings_core = self.view.settings()

        file_name = self.view.file_name()

        if file_name is not None:
            file_name = os.path.splitext(file_name)[1].strip().lower()
            file_types = self.settings.get("file_types", {})

        if file_name is not None and file_name in file_types.get("php", (".php")):
            self.php()
        elif file_name is not None and file_name in file_types.get("js", (".js")):
            self.js()
        else:
            if self.settings.get("prompt_on_ambiguous_buffer", True) == True:
                sublime.active_window().show_quick_panel(["PHP","JavaScript","Cancel"], self._select_beautifier)
            else:
                sublime.status_message("Ambiguous buffer type - unable to beautify")

    def _select_beautifier(self, index):
        if index == 0:
            self.php()
        elif index == 1:
            self.js()
        else:
            sublime.status_message("Ambiguous buffer type - unable to beautify")
            return False

    def _show_errors(self, err):
        panel = self.view.window().get_output_panel("Beautifier")
        panel.set_read_only(False)
        edit = panel.begin_edit()
        panel.erase(edit, sublime.Region(0, panel.size()))
        panel.insert(edit, panel.size(), err)
        panel.set_read_only(True)
        self.view.window().run_command("show_panel", {"panel": "output.Beautifier"})
        panel.end_edit(edit)

    def _get_php_options(self):
        options = []
        formatting = self.settings.get("formatting", {}).get("php", {})
        indent = ""
        filters = []
        new_lines = {"before" : [], "after" : []}
        
        if formatting.get("indentation", {}).get("detect_sublime_settings", True) == True:
            if self.settings_core.get("translate_tabs_to_spaces", False) == True:
                indent = "-s"
            else:
                indent = "-t"
            indent += str(self.settings_core.get("tab_size", 2))
        else:
            if formatting.get("indentation", {}).get("indent_type", "spaces") == "spaces":
                indent = "-s"
            else: 
                indent = "-t"
            indent += str(formatting.get("indentation", {}).get("indent_amount", 2))
        
        options.append(indent)

        if formatting.get("ArrayNested", False) == True:
            filters.append("ArrayNested()")
        if formatting.get("DocBlock", False) == True:
            filters.append("DockBlock()", False)
        if formatting.get("Pear", False) == True:
            filters.append("Pear(add-header=False)")
        if formatting.get("phpBB", False) == True:
            filters.append("phpBB()")
        if formatting.get("default", False) == True:
            filters.append("default()")
        if formatting.get("IndentStyles", "k&r") in self.INDENT_STYLES:
            filters.append("IndentStyles(style=%s)" % str(formatting.get("IndentStyles", "k&r")))
        if formatting.get("NewLines", {}).get("enabled", False) == True:
            new_line_settings = formatting.get("NewLines", {})

            for line_type in new_line_settings.get("before", {}):
                if (new_line_settings.get("before", {}).get(line_type, False) == True and 
                    line_type in self.NEW_LINE_TYPES):
                    new_lines["before"].append(line_type)

            for line_type in new_line_settings.get("after", {}):
                if (new_line_settings.get("after", {}).get(line_type, False) == True and 
                    line_type in self.NEW_LINE_TYPES):
                    new_lines["after"].append(line_type)

            if len(new_lines["before"]) > 0 or len(new_lines["after"]) > 0:
                new_lines["before"] = ":".join(new_lines["before"])
                new_lines["after"] = ":".join(new_lines["after"])
                filters.append("NewLines(before=%s,after=%s)" % (new_lines["before"], new_lines["after"]))

        if len(filters) > 0:
            options.append("--filters")
            filters = " ".join(filters)
            options.append("'"+filters+"'")
        
        return options

    def php(self):
        opts = self._get_php_options()

        selection = self.view.sel()[0]
        replace_region = selection if len(selection) > 0 else sublime.Region(0, self.view.size())

        cmd = ["php_beautifier"]
        cmd.extend(opts)
        cmd.append("--input")
        cmd.append("-")
        cmd.append("--output")
        cmd.append("-")

        cmd = " ".join(cmd)

        cmd = shlex.split(cmd)

        try:
            process = subprocess.Popen(args=cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            response = process.communicate(self.view.substr(replace_region))

            if len(response[1]) > 0 and self.settings.get("prompt_on_error", False):
                self._show_errors(response[1])

            if len(response[0]) > 0:
                self.view.replace(self.edit, replace_region, response[0])
        except OSError:
            sublime.status_message("Unable to start subprocess; please check php_beautifier is installed on this system")

    def _get_js_options(self):
        options = jsbeautifier.default_options()
        formatting = self.settings.get("formatting", {}).get("js", {})

        if formatting.get("indentation", {}).get("detect_sublime_settings", True) == True:
            if self.settings_core.get("translate_tabs_to_spaces", False) == True:
                options.indent_char = " "
            else: 
                options.indent_char = "\t"
            options.indent_size = int(self.settings_core.get("tab_size", 2))
        else:
            if formatting.get("indentation", {}).get("indent_type", "spaces") == "spaces":
                options.indent_char = " "
            else:
                options.indent_char = "\t"
            options.indent_size = int(formatting.get("indentation", {}).get("indent_amount", 2))

        options.preserve_newlines = formatting.get("preserve_newlines", True)
        options.max_preserve_newlines = formatting.get("max_preserve_newlines", 10)
        options.jslint_happy = formatting.get("jslint_happy", False)

        if formatting.get("brace_style", "collapse") in self.BRACE_STYLES:
            options.brace_style = formatting.get("brace_style", "collapse")
            
        options.keep_array_indentation = formatting.get("keep_array_indentation", True)

        return options

    def js(self):
        opts = self._get_js_options()
        selection = self.view.sel()[0]
        replace_region = selection if len(selection) > 0 else sublime.Region(0, self.view.size())
        res = jsbeautifier.beautify(self.view.substr(replace_region), opts)
        prePos = self.view.sel()[0]
        self.view.replace(self.edit, replace_region, res)
        self.view.show_at_center(prePos.begin())
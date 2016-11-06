import sublime, sublime_plugin
import platform
import os, sys, subprocess, codecs, webbrowser, re
from subprocess import Popen, PIPE


PROJECT_NAME = "Auto-Spacing"
SETTINGS_FILE = PROJECT_NAME + ".sublime-settings"
KEYMAP_FILE = "Default ($PLATFORM).sublime-keymap"

PY2 = (sys.version_info[0] == 2)

# borrow from six
if PY2:
    def u(s):
        return unicode(s.replace(r'\\', r'\\\\'),'unicode_escape')
else:
    def u(s):
        return s

CJK_QUOTE_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])(["\'])'))
QUOTE_CJK_RE = re.compile(u(r'(["\'])([\u3040-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])'))
FIX_QUOTE_RE = re.compile(u(r'(["\'\(\[\{<\u201c]+)(\s*)(.+?)(\s*)(["\'\)\]\}>\u201d]+)'))
FIX_SINGLE_QUOTE_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])()(\')([A-Za-z])'))

CJK_HASH_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])(#(\S+))'))
HASH_CJK_RE = re.compile(u(r'((\S+)#)([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])'))

CJK_OPERATOR_ANS_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])([\+\-\*\/=&\\|<>])([A-Za-z0-9])'))
ANS_OPERATOR_CJK_RE = re.compile(u(r'([A-Za-z0-9])([\+\-\*\/=&\\|<>])([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])'))

CJK_BRACKET_CJK_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])([\(\[\{<\u201c]+(.*?)[\)\]\}>\u201d]+)([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])'))
CJK_BRACKET_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])([\(\[\{<\u201c>])'))
BRACKET_CJK_RE = re.compile(u(r'([\)\]\}>\u201d<])([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])'))
FIX_BRACKET_RE = re.compile(u(r'([\(\[\{<\u201c]+)(\s*)(.+?)(\s*)([\)\]\}>\u201d]+)'))

FIX_SYMBOL_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])([~!;:,\.\?\u2026])([A-Za-z0-9])'))

CJK_ANS_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])([A-Za-z0-9`\$%\^&\*\-=\+\\\|/@\u00a1-\u00ff\u2022\u2027\u2150-\u218f])'))
ANS_CJK_RE = re.compile(u(r'([A-Za-z0-9`~\$%\^&\*\-=\+\\\|/!;:,\.\?\u00a1-\u00ff\u2022\u2026\u2027\u2150-\u218f])([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])'))
#

IS_WINDOWS = platform.system() =='Windows'

class AutoSpacingCommand(sublime_plugin.TextCommand):
  def run(self, edit):

    # Save the current viewport position to scroll to it after formatting.
    previous_selection = list(self.view.sel()) # Copy.
    previous_position = self.view.viewport_position()

    # Save the already folded code to refold it after formatting.
    # Backup of folded code is taken instead of regions because the start and end pos
    # of folded regions will change once formatted.
    folded_regions_content = [self.view.substr(r) for r in self.view.folded_regions()]

    # Get the current text in the buffer and save it in a temporary file.
    entire_buffer_region = sublime.Region(0, self.view.size())

    buffer_text = self.get_buffer_text(entire_buffer_region)

    output = self.run_script_on_file(self.view.file_name())

    # If the prettified text length is nil, the current syntax isn't supported.
    if output == None or len(output) < 1:
      return

    print(output, buffer_text)

    # Replace the text only if it's different.
    if output != buffer_text:
      self.view.replace(edit, entire_buffer_region, output)

    self.refold_folded_regions(folded_regions_content, output)
    self.view.set_viewport_position((0, 0), False)
    self.view.set_viewport_position(previous_position, False)
    self.view.sel().clear()

    # Restore the previous selection if formatting wasn't performed only for it.
    # if not is_formatting_selection_only:
    for region in previous_selection:
      self.view.sel().add(region)

  def get_buffer_text(self, region):
    buffer_text = self.view.substr(region)
    return buffer_text

  def run_script_on_file(self, data):
    try:
      viewText = self.view.substr(sublime.Region(0, self.view.size()))
      # file = codecs.open(data,'w','utf-8')
      # file.write(PluginUtils.spacing(viewText))
      # file.close()
      # output = codecs.open(data,'r','utf-8').read()
      output = PluginUtils.spacing(viewText)

      return output

    except:
      # Something bad happened.
      msg = str(sys.exc_info()[1])
      print("Unexpected error({0}): {1}".format(sys.exc_info()[0], msg))
      sublime.error_message(msg)

  def refold_folded_regions(self, folded_regions_content, entire_file_contents):
    self.view.unfold(sublime.Region(0, len(entire_file_contents)))
    region_end = 0

    for content in folded_regions_content:
      region_start = entire_file_contents.index(content, region_end)
      if region_start > -1:
        region_end = region_start + len(content)
        self.view.fold(sublime.Region(region_start, region_end))


class AutoSpacingEventListeners(sublime_plugin.EventListener):
  @staticmethod
  def on_pre_save(view):
    if PluginUtils.get_pref("format_on_save"):
      extensions = PluginUtils.get_pref("format_on_save_extensions")
      extension = os.path.splitext(view.file_name())[1][1:]

      # Default to using filename if no extension
      if not extension:
        extension = os.path.basename(view.file_name())

      # Skip if extension is not whitelisted
      if extensions and not extension in extensions:
        return

      view.run_command("auto_spacing")

class PluginUtils:
  @staticmethod
  def get_pref(key):
    global_settings = sublime.load_settings(SETTINGS_FILE)
    value = global_settings.get(key)

    # Load active project settings
    project_settings = sublime.active_window().active_view().settings()

    # Overwrite global config value if it's defined
    if project_settings.has(PROJECT_NAME):
      value = project_settings.get(PROJECT_NAME).get(key, value)

    return value

  @staticmethod
  def spacing(text):
    """Perform paranoid text spacing on text. Always return unicode."""

    new_text = text

    # always use unicode
    if PY2 and isinstance(new_text, str):
        new_text = new_text.decode('utf-8')

    if len(new_text) < 2:
        return new_text

    new_text = CJK_QUOTE_RE.sub(r'\1 \2', new_text)
    new_text = QUOTE_CJK_RE.sub(r'\1 \2', new_text)
    new_text = FIX_QUOTE_RE.sub(r'\1\3\5', new_text)
    new_text = FIX_SINGLE_QUOTE_RE.sub(r'\1\3\4', new_text)

    new_text = CJK_HASH_RE.sub(r'\1 \2', new_text)
    new_text = HASH_CJK_RE.sub(r'\1 \3', new_text)

    new_text = CJK_OPERATOR_ANS_RE.sub(r'\1 \2 \3', new_text)
    new_text = ANS_OPERATOR_CJK_RE.sub(r'\1 \2 \3', new_text)

    old_text = new_text
    tmp_text = CJK_BRACKET_CJK_RE.sub(r'\1 \2 \4', new_text)
    new_text = tmp_text
    if old_text == tmp_text:
        new_text = CJK_BRACKET_RE.sub(r'\1 \2', new_text)
        new_text = BRACKET_CJK_RE.sub(r'\1 \2', new_text)
    new_text = FIX_BRACKET_RE.sub(r'\1\3\5', new_text)

    new_text = FIX_SYMBOL_RE.sub(r'\1\2 \3', new_text)

    new_text = CJK_ANS_RE.sub(r'\1 \2', new_text)
    new_text = ANS_CJK_RE.sub(r'\1 \2', new_text)

    return new_text


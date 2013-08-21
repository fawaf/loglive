import re
from collections import namedtuple
from tornado.escape import xhtml_escape

CTRL_COLOR = '\x03'      # ^C = color
CTRL_RESET = '\x0F'      # ^O = reset
CTRL_UNDERLINE = '\x1F'  # ^_ = underline
CTRL_BOLD = '\x02'       # ^B = bold

CTRL_REGEX = re.compile(r'(?:[%s%s%s])|(%s(?:\d{1,2}),?(?:\d{1,2})?)' % (
    CTRL_RESET,
    CTRL_UNDERLINE,
    CTRL_BOLD,
    CTRL_COLOR))
JOIN_REGEX = re.compile(r'\*\*\* Joins: .*$')
PART_REGEX = re.compile(r'\*\*\* Parts: .*$')
QUIT_REGEX = re.compile(r'\*\*\* Quits: .*$')

FrozenLineState = namedtuple('FrozenLineState', ['fg_color', 'bg_color', 'bold', 'underline', 'special'])
LineFragment = namedtuple('LineFragment', ['state', 'text'])
IrcLine = namedtuple('IrcLine', ['timestamp', 'nick', 'fragments'])

def ctrl_to_colors(text):
    # the first character is CTRL_COLOR
    colors = text[1:].split(',')
    if colors[0].isdigit():
        fg_color_id = int(colors[0])
    else:
        fg_color_id = None
    if len(colors) == 1:
        bg_color_id = None
    else:
        bg_color_id = int(colors[1])
    return (fg_color_id, bg_color_id)


class LineState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.fg_color = None
        self.bg_color = None
        self.bold = False
        self.underline = False

        # special is a string in ["join", "part", "nick"]
        self.special = None

    def toggle_bold(self):
        self.bold = not self.bold

    def toggle_underline(self):
        self.underline = not self.underline

    def set_color(self, fg_color_id, bg_color_id=None):
        self.fg_color = fg_color_id
        if bg_color_id is not None:
            self.bg_color = bg_color_id

    def freeze(self):
        return FrozenLineState(fg_color=self.fg_color,
                               bg_color=self.bg_color,
                               bold=self.bold,
                               underline=self.underline,
                               special=self.special)


def _is_join(line):
    """Returns True if the line is a join"""
    return JOIN_REGEX.search(line) is not None


def _is_part(line):
    """Returns True if the line was a part"""
    return PART_REGEX.search(line) is not None


def _is_quit(line):
    """Returns True if the line was a quit"""
    return QUIT_REGEX.search(line) is not None


def process_irc_line(line):
    """
    Input is a line from an IRC log, where each line is like:
        "[00:01:22] <panda> I eat shoots and leaves\n"
    or something like:
        "[01:11:31] *** ChanServ sets mode: +v panda"

    Output is a dictionary with the following key values:
        'timestamp': the "[00:01:22]" part from the line
        'nick': the "<panda>" part of the line, or None
        'fragments': a list of LineFragment's
    """
    line = xhtml_escape(line)
    (timestamp, line) = line.split(" ", 1)

    nick = None
    temp_nick_split = line.split(" ", 1)
    if ((temp_nick_split[0].startswith("&lt;") and
         temp_nick_split[0].endswith("&gt;"))):
        (nick, line) = temp_nick_split

    # joins/parts/quit lines don't have control characters, so they shouldn't
    # require special handling
    line_state = LineState()
    if _is_join(line):
        line_state.special = "join"
    elif _is_part(line):
        line_state.special = "part"
    elif _is_quit(line):
        line_state.special = "quit"

    # split text into fragments that are either plain text
    # or a control code sequence
    line = CTRL_REGEX.sub("\n\g<0>\n", line)
    raw_fragments = line.split("\n")
    # add a CTRL_RESET to ensure that the last text fragment is added to the results
    raw_fragments.append(CTRL_RESET)

    fragments = list()
    previous_state = line_state.freeze()
    previous_text = None
    for raw_fragment in raw_fragments:
        if not raw_fragment:
            # blank fragments
            continue
        first_char = raw_fragment[0]

        was_control_code = True
        if first_char == CTRL_COLOR:
            (fg_color_id, bg_color_id) = ctrl_to_colors(fragment)
            line_state.set_color(fg_color_id, bg_color_id)
        elif first_char == CTRL_RESET:
            line_state.reset()
        elif first_char == CTRL_UNDERLINE:
            line_state.toggle_underline()
        elif first_char == CTRL_BOLD:
            line_state.toggle_bold()
        else:
            was_control_code = False

        if was_control_code:
            fragments.append(LineFragment(state=previous_state,
                                          text=previous_text))
            previous_state = line_state.freeze() # freeze the new state
            previous_text = None
        else:
            previous_text = raw_fragment
    return IrcLine(timestamp=timestamp,
                   nick=nick,
                   fragments=fragments)

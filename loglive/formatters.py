import re
from base64 import b64encode
from collections import namedtuple


CTRL_COLOR = '\x03'      # ^C = color
CTRL_RESET = '\x0F'      # ^O = reset
CTRL_UNDERLINE = '\x1F'  # ^_ = underline
CTRL_BOLD = '\x02'       # ^B = bold

CTRL_REGEX = re.compile(r'(?:[%s%s%s])|(%s(?:\d{1,2}),?(?:\d{1,2})?)' % (
    CTRL_RESET,
    CTRL_UNDERLINE,
    CTRL_BOLD,
    CTRL_COLOR))

MESSAGE_REGEX = re.compile(r'^<(?P<nick>\S+)> (?P<message>.*)$')
JOIN_REGEX = re.compile(r'^\*\*\* Joins: .*$')
PART_REGEX = re.compile(r'^\*\*\* Parts: .*$')
QUIT_REGEX = re.compile(r'^\*\*\* Quits: .*$')
ACTION_REGEX = re.compile(r'^\* \S+ .*$')

FrozenLineState = namedtuple('FrozenLineState', ['fg_color', 'bg_color', 'bold', 'underline'])
LineFragment = namedtuple('LineFragment', ['state', 'text'])
IrcLine = namedtuple('IrcLine', ['timestamp', 'nick', 'type', 'message'])


def split_on_timestamp(raw_line):
    """
    Splits a raw irc log line into 2 components: timestamp, and everything else
    """
    (timestamp, line) = raw_line.split(" ", 1)

    # remove the brackets [] around the timestamp
    timestamp = timestamp[1:-1]
    return (timestamp, line)


def split_on_nick(line):
    """
    If the input line has a "<nick>" element at the start, it returns
    (nick, rest of line), else it returns (None, original input line).

    The input to this should be the component of the line after the timestamp
    has already been removed.
    """
    match = MESSAGE_REGEX.match(line)
    if match:
        (nick, message) = match.groups()
    else:
        nick = None
        message = line
    return (nick, message)


def tokenize_line(line):
    """
    Split text into fragments that are either plain text
    or a control code sequence.
    """
    line = CTRL_REGEX.sub("\n\g<0>\n", line)
    fragments = line.split("\n")
    return fragments


def process_irc_line(raw_line):
    """
    Input: a raw line from an irc log, with timestamp and all
    Output: a dictionary in the format:
        {
            'timestamp': timestamp,
            'type': one of ['join', 'part', 'quit', 'action', 'message'],
            'nick': the nick of the user who spoke this line, or None,
            'message': a list of fragments
                [
                    {
                        'state': {'fg_color': null or int,
                                  'bg_color': null or int,
                                  'bold': true or false,
                                  'underline': true or false},
                        'text': base64-encoded text,
                    }
                ]
        }
    """
    (timestamp, line) = split_on_timestamp(raw_line)
    nick = None
    message = list()

    if JOIN_REGEX.match(line):
        line_type = "join"
    elif PART_REGEX.match(line):
        line_type = "part"
    elif QUIT_REGEX.match(line):
        line_type = "quit"
    elif ACTION_REGEX.match(line):
        line_type = "action"
    else:
        line_type = "message"

    line_state = LineState()

    if line_type is not "message":
        line = b64encode(line)
        fragment = LineFragment(state=line_state.freeze()._asdict(),
                                text=line)
        message.append(fragment._asdict())
    else:
        (nick, line) = split_on_nick(line)

        # the CTRL_RESET char at the end makes processing the last fragment
        # doable in the body of the 'for' loop
        raw_fragments = tokenize_line(line) + [CTRL_RESET]

        previous_state = line_state.freeze()
        previous_text = None
        for raw_fragment in raw_fragments:
            if not raw_fragment:
                # blank fragments
                continue
            first_char = raw_fragment[0]

            was_control_code = True
            if first_char == CTRL_COLOR:
                (fg_color_id, bg_color_id) = ctrl_to_colors(raw_fragment)
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
                if previous_text:
                    fragment = LineFragment(state=previous_state._asdict(),
                                    text=previous_text)
                    message.append(fragment._asdict())
                previous_state = line_state.freeze() # freeze the new state
                previous_text = None
            else:
                previous_text = b64encode(raw_fragment)

    return IrcLine(timestamp=timestamp,
                   nick=nick,
                   type=line_type,
                   message=message)._asdict()


def ctrl_to_colors(fragment_text):
    # the first character is CTRL_COLOR
    colors = fragment_text[1:].split(',')
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
                               underline=self.underline)


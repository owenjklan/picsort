from sys import stdout


class TextProgressBar:
    """
    Text-mode progress bar supporting labels, colour and numeric or percent
    output.

    Several styles available:
    """

    STYLE_HASHES = 1
    STYLE_BOXES1 = 2
    STYLE_BOXES2 = 3
    STYLE_UNDERSCORED = 4

    def __init__(self, label, width, start, end, style=STYLE_HASHES,
                 show_percent=False, suffix=None, console_lock=None):
        """
        label: will be truncated to 16 characters by default. Shown at left
        width: how many characters wide the progress bar will be
        start: beginning value for the progress bar
        end:   ending value for the progress bar when at "100%"
        style: One of:
            SYTLE_HASHES:      |###====|
            SYTLE_BOXES1:      |▉▉▉▉▉░░|
            SYTLE_BOXES2:      |▉▉▉▉▉░░|
            STYLE_UNDERSCORED: |▉▉▉____|
            STYLE_BOXES2:   -- Not Currently Implemented -- (Dec. 2019)
        show_percent:   False:       20 of 100
                        True:           20%
        suffix:  Text to append to numeric/percentage readout.
                 Example:  suffix="bytes"  ==>    1023 of 2048 bytes
                 Note: Suffix is NOT displayed when 'show_percent' is True
        """
        self.update_label(label)
        self.start = start
        self.end = end
        self.width = width
        self.scale = (width / end)
        self.value = start
        self.complete = False
        self.backchar = self._determine_backchar(style)
        self.frontchar = self._determine_frontchar(style)
        self.show_percent = show_percent
        self.suffix = suffix
        self.lock = console_lock

    def update_label(self, label):
        if (len(label) > 40):
            return_label = label[0:19] + "..." + label[-18:]
        else:
            return_label = "{:<40}".format(label)
        self.label = return_label

    def _determine_backchar(cls, style):
        if style == cls.STYLE_HASHES:
            return '='
        elif style == cls.STYLE_BOXES1:
            return u"\u2591"
        elif style == cls.STYLE_UNDERSCORED:
            return "_"
        else:
            return '='

    def _determine_frontchar(cls, style):
        if style == cls.STYLE_HASHES:
            return '#'
        elif style == cls.STYLE_BOXES1:
            return u"\u2589"
        elif style == cls.STYLE_UNDERSCORED:
            return u"\u2589"
        else:
            return '#'

    def render(self, linenum=None):
        """
        Clear the current line and render the current value of the progress
        bar.

        Optional linenum will move cursor to a given line before rendering.
        The top line is line 0.
        """
        if (self.value >= self.end):
            self.value = self.end
            self.complete = True
        count = int(self.value * self.scale)
        redstart = "\033[31m"
        whitestart = "\033[37m\033[22m"
        greenstart = "\033[32m\033[1m"

        if self.lock:
            self.lock.acquire()

        if linenum is not None:
            stdout.write("\033[{}H".format(linenum))
        stdout.write("\r " + '{: ^20s}'.format(self.label) + " |")
        stdout.write(
            redstart + (self.backchar * self.width) + whitestart + "| ")

        # Show the trailing numeric info
        if self.show_percent:
            perc = (self.value / self.end) * 100
            stdout.write("{:3.1f}%".format(perc))
        else:
            stdout.write(str(self.value) + " of " + str(self.end))
            if self.suffix:
                stdout.write(" {}".format(self.suffix))

        # Save cursor position in terminal
        stdout.write("\033[s")

        stdout.write("\r " + '{: ^20s}'.format(self.label) + " |")

        stdout.write(greenstart)
        for x in range(self.start, count):
            stdout.write(self.frontchar)
        stdout.write(whitestart)

        # Restore cursor position to the end of the count/percent text
        stdout.write("\033[u")

        # Clear to end of line
        stdout.write("\033[K")

        stdout.flush()
        if (self.complete):
            print()

        if self.lock:
            self.lock.release()

    def add(self, value):
        """
        Add the supplied value to the progress bar's current value.
        Includes a cap to ensure that a value that is larger than
        the end value cannot be set.
        """
        self.value = self.value + value
        if self.value > self.end:
            self.value = self.end

class Printer():

    def __init__(self, spool):
        self.spool = spool

    def open(self):
        try:
            self._printer = open(self.spool, 'w')
        except FileNotFoundError:
            raise PrinterNotFound(
                'Unable to locate printer "' + self.spool + '".'
            )

    def close(self):
        self._printer.close()

    def print_line(self, line):
        self._printer.write(line)

    def cut(self):
        for i in range(8):
            self.print_line('\n')
        self._printer.write(chr(27) + chr(105) + chr(10))

    def kick_drawer(self):
        self._printer.write(
            chr(27) + chr(112) + chr(0) + chr(48) + '0' + chr(10)
        )


class PrinterNotFound(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

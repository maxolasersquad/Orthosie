class Printer(object):
    '''generic printer object wrapper'''

    def __init__(self, settings):
        if type(settings) is str:  # support for existing settings
            self.spool = settings
            self.printer_driver = 'orthosie'
        else:
            # the format should be {'spool':'x', 'driver':'y', 'interface':'z'}
            self.spool = settings['spool']
            self.printer_driver = settings['driver']
            self.interface = settings['interface']

        if self.printer_driver == 'orthosie':
            self._printer = OrthosiePrinter(self.spool)

        elif self.printer_driver == 'escpos':
            self._printer = ESCPOSPrinter(self.spool, self.interface)

        else:
            raise PrinterTypeNotSupported(
                'Printer driver "' + self.printer_driver + '" not supported.'
            )

    def open(self):
        try:
            self._printer.open()
        except AttributeError as e:
            print e

    def close(self):
        try:
            self._printer.close()
        except AttributeError as e:
            print e

    def print_line(self, line):
        self._printer.print_line(line)

    def print_image(self, image_path):
        try:
            self._printer.print_image(image_path)
        except AttributeError as e:
            print e

    def print_qr(self, text):
        try:
            self._printer.print_qr(text)
        except AttributeError as e:
            print e

    def print_barcode(self, **kwargs):
        try:
            self._printer.print_barcode(**kwargs)
        except AttributeError as e:
            print e

    def cut(self, **kwargs):
        self._printer.cut(**kwargs)

    def kick_drawer(self, **kwargs):
        self._printer.kick_drawer(**kwargs)

    def set(self, **kwargs):
        try:
            self._printer.set(**kwargs)
        except AttributeError as e:
            print e


class OrthosiePrinter(object):
    '''Default orthosie printer'''

    def __init__(self, spool):
        self.spool = spool
        self._printer = None

    def open(self):
        # This is kind of a hacky way to make this work in Python 2.7.
        # IOError can be raised in situations other than the file (printer)
        #   not existing so this should probably be tightened up.
        try:
            FileNotFoundError
        except NameError:
            FileNotFoundError = IOError
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


class ESCPOSPrinter(object):
    '''Epson printer'''

    def __init__(self, spool, interface):
        from escpos import printer as escpos_printer
        self.spool = spool
        self.interface = interface
        if self.interface == 'usb':
            self._printer = escpos_printer.Usb(self.spool)
        elif self.interface == 'serial':
            self._printer = escpos_printer.Serial(self.spool)
        elif self.interface == 'network':
            self._printer = escpos_printer.Network(self.spool)
        elif self.interface == 'file':
            self._printer = escpos_printer.File(self.spool)
        else:
            # TODO: handle unsupported printer types
            pass

    def print_line(self, line):
        self._printer.text(line + "\n")

    def cut(self, **kwargs):
        self._printer.cut(**kwargs)

    def set(self, **kwargs):
        self._printer.set(**kwargs)

    def kick_drawer(self, **kwargs):
        '''EPSON drawer kick - supported pins are 2 & 5'''
        if 'pin' in kwargs.keys():
            pin = kwargs['pin']
        else:
            pin = 2  # default to 2
        self._printer.cashdraw(pin)
        self._printer.cashdraw(pin)  # required by some kickers

    def print_qr(self, text):
        self._printer.qr(text)

    def print_image(self, image_path):
        self._printer.image(image_path)

    def print_barcode(self, **kwargs):
        expected = ['code', 'bc', 'width', 'height', 'pos', 'font']
        for key in expected:
            if key not in kwargs:
                raise Exception("All arguments rquired")

        self._printer.barcode(kwargs['code'], kwargs['bc'], kwargs['width'],
                              kwargs['height'], kwargs['pos'], kwargs['font'])


class PrinterNotFound(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class PrinterTypeNotSupported(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

if __name__ == '__main__':
    # will use the orthosie driver
    printer = Printer(
        {'spool': '/dev/null', 'driver': 'orthosie', 'interface': ''})
    printer = Printer('/dev/null')  # will use the orthosie driver
    printer = Printer({'spool': '192.168.192.168',
                       'driver': 'escpos', 'interface': 'network'})
    kwargs = {'font': 'A', 'align': 'CENTER'}
    printer.set(**kwargs)
    printer.print_line('Hello World!')
    kwargs = {'mode': 'PART'}
    printer.cut(**kwargs)  # this is a part cut
    kwargs = {'pin': 2}
    printer.kick_drawer(**kwargs)  # draw kick using pin 2
    printer.cut()  # this is a full cut

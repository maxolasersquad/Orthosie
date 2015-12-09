class Printer(object):
    '''generic printer object wrapper'''

    def __init__(self, settings):
        if type(settings) is str:  # support for existing settings
            self.spool = settings  # spool is case sensitive
            self.printer_driver = 'ORTHOSIE'
            self._printer = OrthosiePrinter(self.spool)
        else:
            if type(settings) is dict:
                # the format should be {'spool':'x', 'driver':'y', 'interface':'z'}
                self.spool = str(settings['spool'])  # spool is case sensitive
                self.printer_driver = str(settings['driver']).upper()
                self.interface = str(settings['interface']).upper()

                if self.printer_driver == 'ORTHOSIE':
                    self._printer = OrthosiePrinter(self.spool)

                elif self.printer_driver == 'ESCPOS':
                    self._printer = ESCPOSPrinter(self.spool, self.interface)

                else:
                    raise PrinterTypeNotSupported(
                        'Printer driver "' + self.printer_driver + '" not supported.'
                    )
            else:
                # the settings are not in a dict format
                raise PrinerSettingsError(
                    'Printer settings format not supported.'
                )

    # methods supported by all printer drivers
    def cut(self, **kwargs):
        self._printer.cut(**kwargs)

    def kick_drawer(self, **kwargs):
        self._printer.kick_drawer(**kwargs)

    def print_line(self, line):
        self._printer.print_line(line)

    # methods supported by some printer drivers
    def open(self):
        try:
            self._printer.open()
        except AttributeError:
            raise PrinterAttributeError(
                '"open" is unsupported by printer'
            )

    def close(self):
        try:
            self._printer.close()
        except AttributeError:
            raise PrinterAttributeError(
                '"close" is unsupported by printer'
            )

    def print_image(self, image_path):
        try:
            self._printer.print_image(image_path)
        except AttributeError:
            raise PrinterAttributeError(
                '"print_image" is unsupported by printer'
            )

    def print_qr(self, text):
        try:
            self._printer.print_qr(text)
        except AttributeError:
            raise PrinterAttributeError(
                '"print_qr" is unsupported by printer'
            )

    def print_barcode(self, **kwargs):
        try:
            self._printer.print_barcode(**kwargs)
        except AttributeError:
            raise PrinterAttributeError(
                '"print_barcode" is unsupported by printer'
            )

    def set(self, **kwargs):
        try:
            self._printer.set(**kwargs)
        except AttributeError:
            raise PrinterAttributeError(
                '"set" is unsupported by printer'
            )


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

        # This is kind of a hacky way to make this work in Python 2.7.
        # IOError can be raised in situations other than the file (printer)
        #   not existing so this should probably be tightened up.
        try:
            FileNotFoundError
        except NameError:
            FileNotFoundError = IOError

        if self.interface == 'USB':
            try:
                self._printer = escpos_printer.Usb(self.spool)
            except FileNotFoundError:
                raise PrinterNotFound(
                    'Unable to locate printer "' + self.spool + '".'
                )

        elif self.interface == 'SERIAL':
            try:
                self._printer = escpos_printer.Serial(self.spool)
            except FileNotFoundError:
                raise PrinterNotFound(
                    'Unable to locate printer "' + self.spool + '".'
                )

        elif self.interface == 'NETWORK':
            import socket
            try:
                self._printer = escpos_printer.Network(self.spool)
            except socket.error as exc:
                raise PrinterNotFound(
                    'Unable to connect to printer: "' + str(exc) + '".'
                )

        elif self.interface == 'FILE':
            try:
                self._printer = escpos_printer.File(self.spool)
            except FileNotFoundError:
                raise PrinterNotFound(
                    'Unable to locate printer "' + self.spool + '".'
                )

        else:
            raise PrinerSettingsError(
                'Interface "' + self.interface + '" unsupported by printer driver.'
            )

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
                raise PrinerArgumentError(
                    "All arguments required by driver for barcode print")

        self._printer.barcode(kwargs['code'], kwargs['bc'], kwargs['width'],
                              kwargs['height'], kwargs['pos'], kwargs['font'])


class PrinerSettingsError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class PrinerArgumentError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class PrinterAttributeError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


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


# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

class LiquidCrystal:

    def __init__(self, rs, rw, enable, d0, d1, d2, d3, d4, d5, d6, d7, fourbitmode=False):
        self.self._rs_pin = rs
        self.self._rw_pin = rw
        self._enable_pin = enable

        self._data_pins = [d0,d1,d2,d3,d4,d5,d6,d7]

        if fourbitmode:
            self._displayfunction = LCD_4BITMODE | LCD_1LINE | LCD_5x8DOTS
        else:
            self._displayfunction = LCD_8BITMODE | LCD_1LINE | LCD_5x8DOTS

        self.begin(16, 1)

    def begin(self, cols, lines, dotsize):
        if lines > 1:
            self._displayfunction |= LCD_2LINE

        _numlines = lines

        setRowOffsets(0x00, 0x40, 0x00 + cols, 0x40 + cols)

        # for some 1 line displays you can select a 10 pixel high font
        if dotsize != LCD_5x8DOTS and lines == 1:
            self._displayfunction |= LCD_5x10DOTS

        pinMode(self._rs_pin, OUTPUT)

        # we can save 1 pin by not using RW. Indicate by passing 255 instead of pin#
        if self.self._rw_pin != 255:
            pinMode(self.self._rw_pin, OUTPUT)

        pinMode(self._enable_pin, OUTPUT)

        npins = 8 if self._displayfunction & LCD_8BITMODE else 4

        for i in range(npins):
            pinMode(self._data_pins[i], OUTPUT)

        # SEE PAGE 45/46 FOR INITIALIZATION SPECIFICATION!
        # according to datasheet, we need at least 40ms after power rises above 2.7V
        # before sending commands. Arduino can turn on way before 4.5V so we'll wait 50
        delayMicroseconds(50000)
        # Now we pull both RS and R/W low to begin commands
        digitalWrite(self._rs_pin, LOW)
        digitalWrite(_enable_pin, LOW)
        if self._rw_pin != 255:
            digitalWrite(self._rw_pin, LOW)



        #put the LCD into 4 bit or 8 bit mode
        if ~ (_displayfunction & LCD_8BITMODE):
            # this is according to the hitachi HD44780 datasheet
            # figure 24, pg 46

            # we start in 8bit mode, try to set 4 bit mode
            write4bits(0x03)
            delayMicroseconds(4500) # wait min 4.1ms

            # second try
            write4bits(0x03)
            delayMicroseconds(4500) # wait min 4.1ms

            # third go!
            write4bits(0x03)
            delayMicroseconds(150)

            # finally, set to 4-bit interface
            write4bits(0x02)
        else:
            # this is according to the hitachi HD44780 datasheet
            # page 45 figure 23

            # Send function set command sequence
            command(LCD_FUNCTIONSET | _displayfunction)
            delayMicroseconds(4500)  # wait more than 4.1ms

            # second try
            command(LCD_FUNCTIONSET | _displayfunction)
            delayMicroseconds(150)

            # third go
            command(LCD_FUNCTIONSET | _displayfunction)


        # finally, set # lines, font size, etc.
        command(LCD_FUNCTIONSET | _displayfunction)

        # turn the display on with no cursor or blinking default
        _displaycontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        display()

        # clear it off
        self.clear()

        # Initialize to default text direction (for romance languages)
        _displaymode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        # set the entry mode
        command(LCD_ENTRYMODESET | _displaymode)

    def setRowOffsets(self, row0, row1, row2, row3):
        self._row_offsets = [row0, row1, row2, row3]

    def clear(self):
        # clear display, set cursor position to zero
        self.command(LCD_CLEARDISPLAY)
        # this command takes a long time!
        delayMicroseconds(2000)

    def home(self):
        # set cursor position to zero
        self.command(LCD_RETURNHOME)
        # this command takes a long time!
        delayMicroseconds(2000)

    def setCursor(col, row):
        
        max_lines = len(row_offsets) #XXX

        if row >= max_lines:
            row = max_lines - 1 # we count rows starting w/0

        if row >= self._numlines:
            row = self._numlines - 1 # we count rows starting w/0

        self.command(LCD_SETDDRAMADDR | (col + self._row_offsets[row]))

    def noDisplay(self):
        """Turn the display on/off (quickly)"""
        self._displaycontrol &= ~LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def display(self):
        self._displaycontrol |= LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def noCursor(self):
        """Turns the underline cursor off"""
        self._displaycontrol &= ~LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def cursor(self):
        """Turns the underline cursor on"""
        self._displaycontrol |= LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def noBlink(self):
        """Turns the underline cursor off"""
        self._displaycontrol &= ~LCD_BLINKON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    def blink(self):
        """Turns the underline cursor on"""
        self._displaycontrol |= LCD_BLINKON
        self.command(LCD_DISPLAYCONTROL | self._displaycontrol)

    # These commands scroll the display without changing the RAM
    def scrollDisplayLeft(self):
        self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)

    def scrollDisplayRight(self):
        self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVERIGHT)

    def leftToRight(self):
        """This is for text that flows Left to Right"""
        self._displaymode |= LCD_ENTRYLEFT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def rightToLeft(self):
        """This is for text that flows Right to Left"""
        self._displaymode &= ~LCD_ENTRYLEFT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def autoscroll(self):
        """This will 'right justify' text from the cursor"""
        self._displaymode |= LCD_ENTRYSHIFTINCREMENT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def noAutoscroll(self):
        """This will 'left justify' text from the cursor"""
        self._displaymode &= ~LCD_ENTRYSHIFTINCREMENT
        self.command(LCD_ENTRYMODESET | self._displaymode)

    def createChar(location, charmap):
        """Allows us to fill the first 8 CGRAM locations with custom characters"""
        location  &= 0x7 # we only have 8 locations 0-7
        self.command(LCD_SETCGRAMADDR | (location << 3))

        for i in range(8):
            write(charmap[i])

    # mid level commands, for sending data/cmds

    def command(self, value):
        self.send(value, LOW)

    def write(self, value):
        self.send(value, HIGH)
        return 1 # assume success

    # low level data pushing commands

    def send(self, value, mode):
        """write either command or data, with automatic 4/8-bit selection"""
        digitalWrite(self._rs_pin, mode)

        # if there is a RW pin indicated, set it low to Write
        if self._rw_pin != 255:
            digitalWrite(self._rw_pin, LOW)

        if self._displayfunction & LCD_8BITMODE:
            self.write8bits(value)
        else:
            self.write4bits(value>>4)
            self.write4bits(value)

    def pulseEnable(self):
        digitalWrite(_enable_pin, LOW)
        delayMicroseconds(1);
        digitalWrite(_enable_pin, HIGH)
        delayMicroseconds(1)    # enable pulse must be >450ns
        digitalWrite(_enable_pin, LOW)
        delayMicroseconds(100); # commands need > 37us to settle

    def write4bits(self, value):
        for i in range(4):
            digitalWrite(self._data_pins[i], (value >> i) & 0x1)

        self.pulseEnable()

    def write8bits(self, value):
        for i in range(8):
            digitalWrite(self._data_pins[i], (value >> i) & 0x1)

        self.pulseEnable()

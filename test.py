from pyfirmata import Arduino, util
from time import sleep

from main import LiquidCrystal

board = Arduino('/dev/ttyACM0')

lcd = LiquidCrystal(board, 1, 7, 255, 8, 9, 10, 11, 12, 0, 0, 0, 0)
lcd.clear()
lcd.write(50)

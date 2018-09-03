from time import sleep

class BoardWrapper:

    def __init__(self, board):
        self.board = board

    def pinMode(self, pin, mode):
        self.board.digital[pin].mode = mode

    def digitalRead(self, pin):
        #raise NotImplemented("read not implemented")
        return self.board.digital[pin].read()

    def digitalWrite(self, pin, value):
        #raise NotImplemented("read not implemented")
        return self.board.digital[pin].write(value)

    def delayMicroseconds(self, us):
        sleep(us/1000000.0)

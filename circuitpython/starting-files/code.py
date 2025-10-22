import time
import board
import digitalio

board_led = digitalio.DigitalInOut(board.LED)
board_led.direction = digitalio.Direction.OUTPUT

while True:
    board_led.value = True
    time.sleep(0.5)
    board_led.value = False
    time.sleep(0.5)

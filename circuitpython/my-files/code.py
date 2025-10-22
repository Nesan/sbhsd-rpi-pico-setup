import time
import board
import digitalio
import busio
import adafruit_dotstar as dotstar
import sys


board_led = digitalio.DigitalInOut(board.LED)
board_led.direction = digitalio.Direction.OUTPUT

# spi = busio.SPI(clock=board.GP2, MOSI=board.GP3)

# sys.stdout = open('output.txt', 'w')
# sys.stdout.write('Hello, world!\n')

# print('print')
dots = dotstar.DotStar(board.GP2, board.GP4, 10, brightness=0.3, auto_write=False, pixel_order=dotstar.RGB)

while True:
    dots[0] = (0, 0, 255)  # red
    dots.show()
    board_led.value = True
    time.sleep(0.5)
    dots[0] = (255, 0, 0)  # red
    dots.show()
    board_led.value = False
    time.sleep(0.5)

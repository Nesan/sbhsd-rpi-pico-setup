import time
import board
import digitalio
import busio
import adafruit_dotstar as dotstar
import sys
import random


board_led = digitalio.DigitalInOut(board.LED)
board_led.direction = digitalio.Direction.OUTPUT
board_led.value = True


import pwmio
buzzer = pwmio.PWMOut(board.GP15, variable_frequency=True)
buzzer.frequency = 440


# spi = busio.SPI(clock=board.GP2, MOSI=board.GP3)

# sys.stdout = open('output.txt', 'w')
# sys.stdout.write('Hello, world!\n')

# print('print')
NUM = 20
pixels = dotstar.DotStar(
    board.GP2,
    board.GP4,
    NUM,
    brightness=0.3,
    auto_write=False,
    pixel_order=dotstar.BGR
)


def fill(c):
    for i in range(NUM):
        pixels[i] = c
    pixels.show()

def wheel(pos):
    if pos < 85:   return (pos*3, 255-pos*3, 0)
    if pos < 170:  pos -= 85; return (255-pos*3, 0, pos*3)
    pos -= 170;    return (0, pos*3, 255-pos*3)


def rainbow(wait=0.02):
    for j in range(256):
        for i in range(NUM):
            pixels[i] = wheel((i*8 + j) & 255)
        pixels.show()
        time.sleep(wait)


def larson(trails=3, wait=0.03, color=(255,0,0), duration=5):
    head = 0;
    dir = 1
    start = time.time()
    while True:
        for i in range(NUM): pixels[i] = (0,0,0)
        pixels[head] = color
        for t in range(1, trails+1):
            idx = head - t*dir
            if 0 <= idx < NUM:
                pixels[idx] = tuple(max(0, c >> (t+1)) for c in color)
        pixels.show(); time.sleep(wait)
        head += dir
        if head == NUM-1 or head == 0: dir *= -1
        if time.time() > start + duration: break


def comet(trail=5, color=(0, 100, 255), wait=0.03, duration=5):
    start = time.time()
    while True:
        for i in range(len(pixels)*2):
            for j in range(len(pixels)):
                fade = max(0, trail - abs(i - j))
                scale = fade / trail
                pixels[j] = tuple(int(c * scale) for c in color)
            pixels.show()
            time.sleep(wait)
        if time.time() > start + duration: break


def fire(wait=0.05):
    while True:
        for i in range(NUM):
            r = random.randint(180, 255)
            g = random.randint(0, 50)
            b = 0#random.randint(0, 20)
            pixels[i] = (r, g, b)
        pixels.show()
        time.sleep(wait)


BASE = (255, 90, 0)
ALPHA = 0.1  # smoothing 0..1 (higher = smoother)
state = [list(BASE) for _ in range(NUM)]

def subtle_fire():
    # warm base (orange) and small random jitter

    def lerp(a, b, t): return int(a + (b-a)*t)

    while True:
        for i in range(NUM):
            # small random brightness around base (mostly red/orange)
            jitter = (random.randint(-20, 20),
                      random.randint(-10, 10),
                      random.randint(-5,  5))

            target = (max(0, min(255, BASE[0] + jitter[0])),
                      max(0, min(255, BASE[1] + jitter[1])),
                      max(0, min(255, BASE[2] + jitter[2])))

            # smooth toward target
            r, g, b = state[i]
            r = lerp(r, target[0], 1-ALPHA)
            g = lerp(g, target[1], 1-ALPHA)
            b = lerp(b, target[2], 1-ALPHA)
            state[i] = [r,g,b]
            pixels[i] = (r,g,b)
        pixels.show()
        time.sleep(0.03)

COOLING = 50        # higher = faster cooling (0-255)
SPARKING = 90       # higher = more sparks (0-255)
SPEED = 0.03        # frame delay
heat = [0]*NUM        # 0..255 per pixel

def real_fire():
    # Tweak these for mood

    def heat_to_color(h):  # map heat (0..255) to (R,G,B)
        # Black -> Red -> Orange -> Yellow -> White
        if h <= 85:   # 0..85: black to deep red
            return (int(h*3), 0, 0)
        elif h <= 170:  # 86..170: red -> orange/yellow
            h2 = h-85
            return (255, int(h2*3), 0)
        else:          # 171..255: yellow -> white
            h3 = h-170
            return (255, 255, int(h3*3//2))

    while True:
        # 1) cool down
        for i in range(NUM):
            heat[i] = max(0, heat[i] - random.randint(0, (COOLING * 10 // NUM) + 2))

        # 2) heat diffuses upward
        for i in range(NUM-1, 1, -1):
            heat[i] = (heat[i-1] + heat[i-2] + heat[i-2]) // 3

        # 3) random spark near the bottom
        if random.randint(0,255) < SPARKING:
            y = random.randint(0, min(6, NUM-1))
            heat[y] = min(255, heat[y] + random.randint(160, 255))

        # 4) convert to colors, bottom = index 0
        for i in range(NUM):
            pixels[i] = heat_to_color(heat[i])
        pixels.show()
        time.sleep(SPEED)


def test():
    for c in [(255,0,0),(0,255,0),(0,0,255), (0,0,0)]:
        pixels.fill(c); pixels.show(); time.sleep(1)
    pixels.fill((0,0,0)); pixels.show()


while True:
    # rainbow(0.01)
    # larson(3, 0.02, (0, 0, 255), 2)
    comet(10, (0, 255, 0), 0.02, 2)
    # subtle_fire()
    # fire(0.1)


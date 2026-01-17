import time
import board
import digitalio
import busio
import adafruit_dotstar as dotstar
import sys
import analogio
import math



# -------- CONFIG --------
MIC_ADC_PIN       = board.GP27        # ADC0
NUM_LEDS      = 10                # total LEDs
BRIGHTNESS    = 0.3
SAMPLE_RATE   = 8000              # Hz (target)

GAIN        = 3.0               # post-envelope gain multiplier
NOISE_GATE  = 0.01              # envelope floor (0..1)
ENV_ATTACK  = 0.2               # faster rise (0..1) larger = snappier
ENV_RELEASE = 0.02              # slower fall (0..1)
N             = 1024              # FFT size (power of 2)
# LED layout: split strip into 3 equal segments (bass, voice, guitar)
# Adjust if your strip length isn't divisible by 3
# ------------------------

mic = analogio.AnalogIn(MIC_ADC_PIN)

# Helpers to convert ADC 16-bit to 0..1 float
def adc_norm():
    # mic.value is 0..65535 (nominal); divide to normalize
    # return 1
    return mic.value / 65535.0


# Track DC offset with a simple low-pass, subtract to get AC
dc = adc_norm()
env = 0.0

# Optional: simple color gradient (green -> yellow -> red)
def color_for_index(i, lit):
    if i < lit:
        # map 0..lit-1 to 0..1
        t = i / max(lit - 1, 1)
        # green to red via yellow
        r = int(min(1.0, 2*t) * 255)
        g = int(min(1.0, 2*(1 - t)) * 255)
        b = 0
        return (r, g, b)
    return (0, 0, 0)
# Simple FPS pacing
sample_interval = 1.0 / SAMPLE_RATE
last = time.monotonic()

board_led = digitalio.DigitalInOut(board.LED)
board_led.direction = digitalio.Direction.OUTPUT

dots = dotstar.DotStar(board.GP2, board.GP4, 10, brightness=0.3, auto_write=False, pixel_order=dotstar.RGB)


def foo():
    global last, dc, env
    # --- Sample ---
    now = time.monotonic()
    if now - last < sample_interval:
        # light delay to stabilize loop timing
        time.sleep(sample_interval - (now - last))
    last = time.monotonic()

    x = adc_norm()

    # --- DC removal (high-pass) ---
    # slow LPF for DC; alpha ~ 1/1024-ish per sample for smooth tracking
    dc_alpha = 0.002
    dc = (1.0 - dc_alpha) * dc + dc_alpha * x
    ac = x - dc  # centered around ~0

    # --- Rectify & envelope follower ---
    rect = abs(ac)
    # Attack/Release envelope (separate coeffs)
    if rect > env:
        env = (1.0 - ENV_ATTACK) * env + ENV_ATTACK * rect
    else:
        env = (1.0 - ENV_RELEASE) * env + ENV_RELEASE * rect

    # --- Gain, noise gate, clamp ---
    y = max(0.0, env - NOISE_GATE) * GAIN
    y = min(y / (1.0 - NOISE_GATE), 1.0)  # normalize after gating
    y = min(max(y, 0.0), 1.0)

    # --- Log-ish feel (optional): make low volumes more visible ---
    y_display = math.sqrt(y)  # try math.log1p for different feel

    # --- Map to LEDs ---
    lit = int(round(y_display * NUM_LEDS))
    for i in range(NUM_LEDS):
        dots[i] = color_for_index(i, lit)
    dots.show()


while True:
    dots[0] = (0, 0, 255)  # red
    dots.show()
    board_led.value = True
    time.sleep(0.5)
    foo()

    # board_led.value = True
    # time.sleep(0.5)
    # board_led.value = False
    # time.sleep(0.5)
    # # foo()

    dots[0] = (255, 0, 255)  # red
    dots.show()
    time.sleep(0.5)

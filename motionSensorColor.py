import array, time
from machine import Pin
from utime import sleep_ms
import rp2

NUM_LEDS = 30
PIN_NUM = 22
brightness = 0.09

pir = Pin(21, Pin.IN, Pin.PULL_DOWN)
n = 0

print('Starting up the PIR Module')
time.sleep(1)
print('Ready')

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()

sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))
sm.active(1)

ar = array.array("I", [0 for _ in range(NUM_LEDS)])

def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)
    time.sleep_ms(10)

def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)

CLEAR = (0,0,0)
BLUE = (0,0,255)
      
pixels_fill(CLEAR)
pixels_show()
time.sleep(1)

while True:
     if pir.value() == 1:
          n = n+1
          print('Motion Detected ',n)
          pixels_fill(BLUE)
          pixels_show()
          time.sleep(120)
          pixels_fill(CLEAR)
          pixels_show()
     else:
        pixels_fill(CLEAR)
        pixels_show()
        time.sleep(0.5)


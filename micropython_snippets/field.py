
from machine import Pin
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_RGB332
import pngdec
import time

button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, pen_type=PEN_RGB332)
display.set_backlight(0.75)

png = pngdec.PNG(display)

BG = display.create_pen(200, 200, 200)
display.set_pen(BG)
display.clear()

png.open_file("field_0.png")
png.decode(0, 0)
display.update()

menu_open = False

while True:
    if button_x.value() == 0:
        print('button pressed')
        if not menu_open:
            print('open menu')
            png.open_file("menu.png")
            png.decode(0, 0)
            menu_open = True
            time.sleep(0.1)
        else:
            print('close menu')
            png.open_file("field_0.png")
            png.decode(0, 0)
            menu_open = False
            
    display.update()



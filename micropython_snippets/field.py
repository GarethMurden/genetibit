
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


def startup():
    png.open_file("field_0.png")
    png.decode(0, 0)
    display.update()

def move_menu_cursor(position):
    cursor_positions = [
        (284,  43),
        (284,  92),
        (284, 140),
        (284, 188)
    ]

    if position < 0:
        position = len(cursor_positions) - 1
    if position >= len(cursor_positions):
        position = 0

    if 0 <= position < len(cursor_positions):
        move_to = cursor_positions[position]
    else:
        move_to = cursor_positions[0]
    png.open_file("selector.png")
    png.decode(
        cursor_positions[position][0],
        cursor_positions[position][1]
    )
    print(f'moving cursor to position {position}: {cursor_positions[position]}')
    return position


def main():
    menu_cursor_position = 0
    menu_open = False
    while True:
        if not menu_open:
            if button_x.value() == 0:
                print('open menu')
                png.open_file("menu.png")
                png.decode(256, 0)
                menu_open = True
                move_menu_cursor(0)
                
        if menu_open:
            if button_x.value() == 0:
                print('close menu')
                png.open_file("field_0.png")
                png.decode(0, 0)
                menu_open = False

            if button_a.value() == 0:
                png.open_file("menu.png")
                png.decode(256, 0)
                menu_cursor_position = move_menu_cursor(menu_cursor_position - 1)
            
            if button_b.value() == 0:
                png.open_file("menu.png")
                png.decode(256, 0)
                menu_cursor_position = move_menu_cursor(menu_cursor_position + 1)

        display.update()
        time.sleep(0.2)

startup()
main()




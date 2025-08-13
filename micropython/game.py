
from machine import Pin
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_RGB332
import pngdec
import time
import _thread

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

CURRENT_SCREEN = {
    'name':'field',
    'data':0
}

class Layer_class():
    background = {'file':'field', 'position':(0,0)}
    bottom     = None
    middle     = None
    top        = None
    cursor     = None
    
    def clear_all(self):
        self.background = None
        self.bottom = None
        self.middle = None
        self.top = None
        self.cursor = None

    def show(self):
        if self.background is not None:
            self.update_display(self.background['file'], self.background['position'])
        if self.bottom is not None:
            self.update_display(self.bottom['file'], self.bottom['position'])
        if self.middle is not None:
            self.update_display(self.middle['file'], self.middle['position'])
        if self.top is not None:
            self.update_display(self.top['file'], self.top['position'])
        if self.cursor is not None:
            self.update_display(self.cursor['file'], self.cursor['position'])
        display.update()


    def update_display(self, filename, position):
        png.open_file(f"assets/{filename}.png")
        png.decode(position[0], position[1])

def menu():
    global CURRENT_SCREEN
    menu_options = [
        'field',
        'breeding',
        'market',
        'settings'
    ]
    menu_cursor_position = 0
    menu_open = False
    while True:
        if not menu_open:
            if button_x.value() == 0:
                print('open menu')
                Layers.top = {'file':'menu', 'position':(256, 0)}
                menu_open = True
                menu_move_cursor(0)
                
        elif menu_open:
            if button_x.value() == 0:
                print('close menu')
                Layers.top = None
                Layers.cursor = None
                menu_open = False

            if button_y.value() == 0:
                new_screen = menu_options[menu_cursor_position]
                print(f'moving to "{new_screen}" screen')
                CURRENT_SCREEN['name'] = new_screen
                menu_open = False

            if button_a.value() == 0:
                menu_cursor_position = menu_move_cursor(menu_cursor_position - 1)
            
            if button_b.value() == 0:
                menu_cursor_position = menu_move_cursor(menu_cursor_position + 1)
        
        time.sleep(0.2)
    
def menu_move_cursor(position):
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
    Layers.cursor = {
        'file':'selector',
        'position':(
            cursor_positions[position][0],
            cursor_positions[position][1]
        )
    }
    return position

def screens():
    previous_screen_name = ''
    while True:
        if CURRENT_SCREEN['name'] != previous_screen_name:
            previous_screen_name = CURRENT_SCREEN['name']
            Layers.clear_all()
            if CURRENT_SCREEN['name'] == 'field':
                screen_field(CURRENT_SCREEN['data'])
            if CURRENT_SCREEN['name'] == 'breeding':
                screen_breeding(CURRENT_SCREEN['data'])
        Layers.show()
        time.sleep(0.2)


def screen_breeding(critter):
    print('breeding screen')
    Layers.background = {
        'file':'breeding',
        'position':(0, 0)
    }
    Layers.cursor = {
        'file':'updown',
        'position':(80, 0)
    }
    
def screen_field(field_level):
    print('field screen')
    Layers.background = {
        'file':f'field_{field_level}',
        'position':(0, 0)
    }

def main():
    screen_thread = _thread.start_new_thread(screens, ())
    menu()


Layers = Layer_class()
main()








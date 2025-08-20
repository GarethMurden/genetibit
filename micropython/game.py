
import json
from machine import Pin
import os
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_RGB332
import pngdec
import random
import time
import _thread

import critters

button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, pen_type=PEN_RGB332)

png = pngdec.PNG(display)

BG = display.create_pen(200, 200, 200)
display.set_pen(BG)
display.clear()

MENU_OPEN = False
CURRENT_SCREEN = 'field'
DATA = {
    'breeding':{},
    'critters':[],
    'field':{
        'level':0
    },
    'market':{},
    'settings':{
        'cursor_index':0,
        'brightness':0.6
    }
}
POPULATION = []

class Layer_class():
    background  = {'file':'field', 'position':(0,0)}
    bottom      = None
    middle      = None # multiple overlappnig images allowed
    top         = None
    cursor      = None
    menu_cursor = None
    
    def clear_all(self):
        self.background  = None
        self.bottom      = None
        self.middle      = None
        self.top         = None
        self.cursor      = None
        self.menu_cursor = None

    def show(self):
        if self.background is not None:
            self.update_display(self.background['file'], self.background['position'])
        if self.bottom is not None:
            self.update_display(self.bottom['file'], self.bottom['position'])
        if self.middle is not None:
            for image in self.middle:
                self.update_display(image['file'], image['position'])
        if self.top is not None:
            self.update_display(self.top['file'], self.top['position'])
        if self.cursor is not None:
            self.update_display(self.cursor['file'], self.cursor['position'])
        if self.menu_cursor is not None:
            self.update_display(self.menu_cursor['file'], self.menu_cursor['position'])
        display.update()

    def update_display(self, filename, position):
        png.open_file(f"assets/{filename}.png")
        png.decode(position[0], position[1])

def data_load():
    global DATA
    save_file = 'data.json'
    if not file_exits(save_file):
        DATA['critters'] += critters.generate_starters()
        data_save()
    with open(save_file, 'r', encoding='utf-8') as f:
        DATA = json.loads(f.read())

def data_save():
    with open('data.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(DATA))

def file_exits(filename):
    try:
        with open(filename, 'r'):
            return True
    except OSError:
        return False

def menu():
    global CURRENT_SCREEN, MENU_OPEN
    menu_options = [
        'field',
        'breeding',
        'market',
        'settings'
    ]
    menu_cursor_position = 0
    while True:
        if not MENU_OPEN:
            if button_x.value() == 0:
                print('open menu')
                Layers.top = {'file':'menu', 'position':(256, 0)}
                MENU_OPEN = True
                menu_cursor_position = 0
                menu_move_cursor(menu_cursor_position)
                data_save()
                
        elif MENU_OPEN:
            if button_x.value() == 0:
                print('close menu')
                Layers.top = None
                Layers.menu_cursor = None
                MENU_OPEN = False

            if button_y.value() == 0:
                new_screen = menu_options[menu_cursor_position]
                print(f'moving to "{new_screen}" screen')
                CURRENT_SCREEN = new_screen
                MENU_OPEN = False

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
    Layers.menu_cursor = {
        'file':'selector',
        'position':(
            cursor_positions[position][0],
            cursor_positions[position][1]
        )
    }
    return position

def screens():
    global CURRENT_SCREEN
    previous_screen_name = ''
    while True:
        if CURRENT_SCREEN != previous_screen_name:
            previous_screen_name = CURRENT_SCREEN
            Layers.clear_all()
        if CURRENT_SCREEN == 'field':
            screen_field()
        if CURRENT_SCREEN == 'breeding':
            screen_breeding()
        if CURRENT_SCREEN == 'market':
            screen_market()
        if CURRENT_SCREEN == 'settings':
            screen_settings()
        Layers.show()
        time.sleep(0.2)


def screen_breeding():
    Layers.background = {
        'file':'breeding',
        'position':(0, 0)
    }
    Layers.cursor = {
        'file':'updown',
        'position':(80, 0)
    }

def screen_field():
    global POPULATION
    if len(POPULATION) == 0:
        for critter_data in DATA['critters']:
            POPULATION.append(critters.Critter(
                critter_data['genes'],
                critter_data['ancestors'],
                position=(
                    random.randint(10,310),
                    random.randint(10, 410)
                )
            ))
    Layers.middle = []
    if not MENU_OPEN:
        for critter in POPULATION:
            if random.choice([True, True, False]):
                critter.move()
            Layers.middle.append({
                'file':critter.get_sprite(),
                'position':critter.get_position()
            })
    Layers.background = {
        'file':f'field_{DATA["field"]["level"]}',
        'position':(0, 0)
    }

def screen_market():
    Layers.background = {
        'file':'market',
        'position':(0, 0)
    }

def screen_settings():
    global DATA
    cursor_positions = [
        ( 40, 65),
        (140, 65)
    ]
    if not MENU_OPEN:
        if button_a.value() == 0:
            DATA['settings']['cursor_index'] = 0
        if button_b.value() == 0:
            DATA['settings']['cursor_index'] = 1
        if button_y.value() == 0:
            if DATA['settings']['cursor_index'] == 1:
                DATA['settings']['brightness'] = min([
                    DATA['settings']['brightness'] + 0.2,
                    1.0
                ])
                display.set_backlight(DATA['settings']['brightness'])
            else:
                DATA['settings']['brightness'] = max([
                    DATA['settings']['brightness'] - 0.2,
                    0.2
                ])
                display.set_backlight(DATA['settings']['brightness'])
    Layers.background = {
        'file':'settings',
        'position':(0, 0)
    }
    Layers.bottom = {
        'file':f"settings_brightness{DATA['settings']['brightness']}",
        'position':(0, 0)
    }
    Layers.cursor = {
        'file':'cursor',
        'position':cursor_positions[DATA['settings']['cursor_index']]
    }

def main():
    data_load()
    display.set_backlight(DATA['settings']['brightness'])
    screen_switch_thread = _thread.start_new_thread(screens, ())
    menu()

Layers = Layer_class()
main()


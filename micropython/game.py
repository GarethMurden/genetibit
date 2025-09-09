
import json
from machine import Pin
import os
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_RGB332
from pimoroni import RGBLED
import pngdec
import random
import time
import _thread

import critters

button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

led = RGBLED(26, 27, 28)

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, pen_type=PEN_RGB332)

png = pngdec.PNG(display)

TEXT = display.create_pen(0, 0, 0)
IMAGES = display.create_pen(200, 200, 200)
display.set_pen(IMAGES)
display.clear()

MENU_OPEN = False
CURRENT_SCREEN = 'breeding'#'field'
DATA = {
    'breeding':{
        'cursor_index':0,
        'left_critter_index':0,
        'right_critter_index':1
    },
    'critters':[],
    'field':{
        'level':0
    },
    'market':{
        'gold':0
    },
    'settings':{
        'cursor_index':0,
        'brightness':0.6
    }
}
POPULATION = []

class Layer_class():
    background  = {'file':'field', 'position':(0,0)}
    bottom      = None
    middle      = None # multiple overlapping images allowed
    top         = None
    cursor      = None
    menu_cursor = None
    text        = None # multiple text entries allowed
    
    def clear_all(self):
        self.background  = None
        self.bottom      = None
        self.middle      = None
        self.top         = None
        self.cursor      = None
        self.menu_cursor = None
        self.text        = None

    def show(self):
        if self.background is not None:
            self.update_display(self.background['file'], self.background['position'], self.background.get('scale', 1))
        if self.bottom is not None:
            self.update_display(self.bottom['file'], self.bottom['position'], self.bottom.get('scale', 1))
        if self.middle is not None:
            for image in self.middle:
                self.update_display(image['file'], image['position'], image.get('scale', 1))
        if self.top is not None:
            self.update_display(self.top['file'], self.top['position'], self.top.get('scale', 1))
        if self.cursor is not None:
            self.update_display(self.cursor['file'], self.cursor['position'], self.cursor.get('scale', 1))
        if self.menu_cursor is not None:
            self.update_display(self.menu_cursor['file'], self.menu_cursor['position'], self.menu_cursor.get('scale', 1))
        if self.text is not None:
            display.set_pen(TEXT)
            # display.clear()
            for entry in self.text:
                display.text(
                    str(entry['text']),
                    entry['position'][0],
                    entry['position'][1],
                    scale=entry.get('scale', 1)
                )
            display.set_pen(IMAGES)
        display.update()

    def update_display(self, filename, position, scale=1):
        png.open_file(f"assets/{filename}.png")
        png.decode(position[0], position[1], scale=scale)

def data_clear_screen():
    '''clear cached data only needed while screen open'''
    global DATA
    DATA['breeding']['cursor_index'] = 0
    
def data_load():
    global DATA
    save_file = 'data.json'
    if not file_exits(save_file):
        DATA['critters'] += critters.generate_starters()
        DATA['market']['total'] = 0
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
                led.set_rgb(0, 50, 0)
                print('[ DEBUG ]: open menu')
                Layers.top = {'file':'menu', 'position':(256, 0)}
                Layers.text = [{
                    'text':str(DATA['market']['total']),
                    'position':(285, 10)
                }]
                MENU_OPEN = True
                menu_cursor_position = 0
                menu_move_cursor(menu_cursor_position)

        elif MENU_OPEN:
            if button_x.value() == 0:
                led.set_rgb(0, 50, 0)
                print('[ DEBUG ]: close menu')
                Layers.top = None
                Layers.menu_cursor = None
                MENU_OPEN = False

            if button_y.value() == 0:
                led.set_rgb(0, 50, 0)
                new_screen = menu_options[menu_cursor_position]
                print(f'[ DEBUG ]: moving to "{new_screen}" screen')
                CURRENT_SCREEN = new_screen
                MENU_OPEN = False

            if button_a.value() == 0:
                led.set_rgb(0, 50, 0)
                menu_cursor_position = menu_move_cursor(menu_cursor_position - 1)
            
            if button_b.value() == 0:
                led.set_rgb(0, 50, 0)
                menu_cursor_position = menu_move_cursor(menu_cursor_position + 1)
        
        time.sleep(0.25)
        led.set_rgb(0, 0, 0)
    
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
            data_clear_screen()
        if CURRENT_SCREEN == 'field':
            screen_field()
        if CURRENT_SCREEN == 'breeding':
            screen_breeding()
        if CURRENT_SCREEN == 'breeding_animation':
            screen_breeding_animation()
        if CURRENT_SCREEN == 'breeding_result':
            screen_breeding_result()
        if CURRENT_SCREEN == 'breeding_sale':
            screen_breeding_sale()
        if CURRENT_SCREEN == 'market':
            screen_market()
        if CURRENT_SCREEN == 'settings':
            screen_settings()
        Layers.show()

def screen_breeding():
    global DATA, CURRENT_SCREEN

    if not MENU_OPEN:
        if DATA['breeding']['cursor_index'] == 0:
            Layers.cursor = {
                'file':'updown',
                'position':(75, 45)
            }
            if button_a.value() == 0:
                led.set_rgb(0, 50, 0)
                DATA['breeding']['left_critter_index'] -= 1
                if DATA['breeding']['left_critter_index'] < 0:
                    DATA['breeding']['left_critter_index'] = len(POPULATION) -1
            if button_b.value() == 0:
                led.set_rgb(0, 50, 0)
                DATA['breeding']['left_critter_index'] += 1
                if DATA['breeding']['left_critter_index'] >= len(POPULATION):
                    DATA['breeding']['left_critter_index'] = 0
            if button_y.value() == 0:
                led.set_rgb(0, 50, 0)
                DATA['breeding']['cursor_index'] = 1

        else:
            Layers.cursor = {
                'file':'updown',
                'position':(235, 45)
            }
            if button_a.value() == 0:
                led.set_rgb(0, 50, 0)
                DATA['breeding']['right_critter_index'] -= 1
                if DATA['breeding']['right_critter_index'] == DATA['breeding']['left_critter_index']: # can't have the same on L & R
                    DATA['breeding']['right_critter_index'] -= 1
                if DATA['breeding']['right_critter_index'] < 0:
                    DATA['breeding']['right_critter_index'] = len(POPULATION) -1
            if button_b.value() == 0:
                led.set_rgb(0, 50, 0)
                DATA['breeding']['right_critter_index'] += 1
                if DATA['breeding']['right_critter_index'] == DATA['breeding']['left_critter_index']: # can't have the same on L & R
                    DATA['breeding']['right_critter_index'] += 1
                if DATA['breeding']['right_critter_index'] >= len(POPULATION):
                    DATA['breeding']['right_critter_index'] = 0

            if button_y.value() == 0:
                led.set_rgb(0, 50, 0)
                CURRENT_SCREEN = 'breeding_animation' # change screen on next loop iteration

    Layers.background = {
        'file':'breeding',
        'position':(0, 0)
    }
    Layers.bottom = {
        'file':POPULATION[DATA['breeding']['left_critter_index']].get_sprite(),
        'position':(15, 65),
        'scale':4
    }
    Layers.middle = [{
        'file':POPULATION[DATA['breeding']['right_critter_index']].get_sprite(),
        'position':(175, 65),
        'scale':4
    }]

    Layers.text = [
        {
            'text':len(POPULATION[DATA['breeding']['right_critter_index']].ancestors),
            'position':(80, 189),
            'scale': 2
        },
        {
            'text':len(POPULATION[DATA['breeding']['left_critter_index']].ancestors),
            'position':(235, 189),
            'scale': 2
        }
    ]

    led.set_rgb(0, 0, 0)

def screen_breeding_animation():
    global CURRENT_SCREEN
    Layers.clear_all()
    Layers.background = {
        'file':'blank',
        'position':(0, 0)
    }
    Layers.bottom = {
        'file':'animation_hatch/hatch01',
        'position':(60, 100),
        'scale':4
    }
    Layers.show()

    mother = POPULATION[DATA['breeding']['left_critter_index']]
    father = POPULATION[DATA['breeding']['right_critter_index']]
    DATA['breeding']['children'] = []
    for x in range(4):
        time.sleep(0.5)
        m_gamete = mother.get_gamete()
        f_gamete = father.get_gamete()
        child_genotype = {}
        for key in m_gamete:
            child_genotype[key] = [
                m_gamete[key],
                f_gamete[key]
            ]
        DATA['breeding']['children'].append({
            'genes':child_genotype,
            'ancestors':critters.build_ancestry(mother, father)
        })

    # HATCHING ANIMATION
    Layers.bottom = {
        'file':'animation_hatch/hatch02',
        'position':(60, 100),
        'scale':4
    }
    Layers.show()
    Layers.bottom = {
        'file':'animation_hatch/hatch03',
        'position':(60, 100),
        'scale':4
    }
    Layers.show()
    time.sleep(1)
    Layers.bottom = {
        'file':'animation_hatch/hatch04',
        'position':(60, 100),
        'scale':4
    }
    Layers.show()
    time.sleep(1)
    Layers.bottom = {
        'file':'animation_hatch/hatch05',
        'position':(60, 100),
        'scale':4
    }
    Layers.show()
    time.sleep(0.25)
    Layers.bottom = {
        'file':'animation_hatch/hatch06',
        'position':(60, 100),
        'scale':4
    }
    Layers.show()
    Layers.bottom = {
        'file':'animation_hatch/hatch07',
        'position':(60, 100),
        'scale':4
    }
    Layers.show()
    time.sleep(1)
    Layers.bottom = None
    CURRENT_SCREEN = 'breeding_result'

def screen_breeding_sale(children, sell_indicies):
    global DATA, CURRENT_SCREEN, POPULATION
    Layers.clear_all()
    Layers.background = {
        'file':'breeding_sell',
        'position':(0,0)
    }
    Layers.middle = []

    kept = []
    sold = []
    for index, sell in enumerate(sell_indicies):
        if sell:
            sold.append(children[index])
        else:
            kept.append(children[index])

    if 'total' not in DATA['market']:
        DATA['market']['total'] = 0
    for v_counter, critter in enumerate(sold):
        value = critter.get_value()
        DATA['market']['total'] += int(value['total'])

        vertical_position = 10 + (48 * v_counter)
        Layers.middle.append({
            'file':     critter.get_sprite(),
            'position': (10, vertical_position),
            'scale':    2
        })

        ribbons = ['colour', 'legs', 'body', 'head']
        for h_counter, ribbon in enumerate(ribbons):
            if value[ribbon]['rank'] != 'D':
                Layers.middle.append({
                    'file':f"ribbon/ribbon_{value[ribbon]['rank'].lower()}",
                    'position':(100 + h_counter * 18, vertical_position + 15)
                })

    Layers.show()

    # reset breeding data
    del DATA['breeding']['sell_selections']
    DATA['breeding']['cursor_index'] = 0
    
    # add all to population
    POPULATION += kept
    DATA['critters'] += [{'ancestors':child.ancestors, 'genes':child.get_genotype()} for child in kept]
    data_save()

    while True: # Wait for button press, then return to field
        if button_y.value() == 0:
            CURRENT_SCREEN = 'field'
            break


def screen_breeding_result():
    global DATA, CURRENT_SCREEN, POPULATION

    mother = POPULATION[DATA['breeding']['left_critter_index']]
    father = POPULATION[DATA['breeding']['right_critter_index']]
    children = []

    for child in DATA['breeding']['children']:
        children.append(critters.Critter(child['genes'], ancestors=child['ancestors']))

    cursor_positions = [
        ( 10,  25), # close button
        ( 45, 210),
        (115, 210),
        (190, 210),
        (270, 210)
    ]

    if 'sell_selections' not in DATA['breeding']:
        DATA['breeding']['sell_selections'] = [False, False, False, False]

    if not MENU_OPEN:
        if button_a.value() == 0:
            led.set_rgb(0, 50, 0)
            DATA['breeding']['cursor_index'] -= 1
            if DATA['breeding']['cursor_index'] < 0:
                DATA['breeding']['cursor_index'] = len(cursor_positions) -1
        
        if button_b.value() == 0:
            led.set_rgb(0, 50, 0)
            DATA['breeding']['cursor_index'] += 1
            if DATA['breeding']['cursor_index'] == len(cursor_positions):
                DATA['breeding']['cursor_index'] = 0

        if button_y.value() == 0:
            led.set_rgb(0, 50, 0)
            if DATA['breeding']['cursor_index'] != 0:
                if DATA['breeding']['sell_selections'][DATA['breeding']['cursor_index'] -1]:
                    DATA['breeding']['sell_selections'][DATA['breeding']['cursor_index'] -1] = False
                else:
                    DATA['breeding']['sell_selections'][DATA['breeding']['cursor_index'] -1] = True
                
            else:
                data_save()
                if any(DATA['breeding']['sell_selections']):
                    screen_breeding_sale(children, DATA['breeding']['sell_selections'])

                else: # no offspring sold
                    # reset breeding data
                    del DATA['breeding']['sell_selections']
                    DATA['breeding']['cursor_index'] = 0
                    # add all to population
                    POPULATION += children
                    DATA['critters'] += [{'ancestors':child.ancestors, 'genes':child.get_genotype()} for child in children]
                    # return to field
                    CURRENT_SCREEN = 'field'

        Layers.cursor = {
            'file':'cursor',
            'position':cursor_positions[DATA['breeding']['cursor_index']]
        }

    if CURRENT_SCREEN == 'breeding_result':
        Layers.background = {
            'file':'breeding_result',
            'position':(0, 0)
        }
        Layers.middle = [
            {
                'file':mother.get_sprite(),
                'position':(60, 20),
                'scale':3
            },
            {
                'file':father.get_sprite(),
                'position':(160, 22),
                'scale':3
            },
            {
                'file':children[0].get_sprite(),
                'position':(5, 115),
                'scale':3
            },
            {
                'file':children[1].get_sprite(),
                'position':(75, 115),
                'scale':3
            },
            {
                'file':children[2].get_sprite(),
                'position':(155, 115),
                'scale':3
            },
            {
                'file':children[3].get_sprite(),
                'position':(230, 115),
                'scale':3
            }
        ]

        checkmark_positions = [
            ( 50, 213),
            (120, 213),
            (195, 213),
            (275, 213)
        ]
        for counter, selected in enumerate(DATA['breeding']['sell_selections']):
            if selected:
                Layers.middle.append({
                    'file':'tick',
                    'position':checkmark_positions[counter],
                })

        # write values beneath children
        Layers.text = [
            {
                'text':children[0].get_value()['total'],
                'position':(50, 190),
                'scale': 2
            },
            {
                'text':children[1].get_value()['total'],
                'position':(120, 190),
                'scale': 2
            },
            {
                'text':children[2].get_value()['total'],
                'position':(195, 190),
                'scale': 2
            },
            {
                'text':children[3].get_value()['total'],
                'position':(273, 190),
                'scale': 2
            },
        ]

def screen_field():
    global POPULATION
    Layers.middle = []
    for critter in POPULATION:
        if not MENU_OPEN:
            if random.choice([True, True, False]):
                critter.move()
        Layers.middle.append({
            'file':critter.get_sprite(),
            'position':critter.get_position(),
            'scale':2
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
            data_save()

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
    global POPULATION
    data_load()
    display.set_backlight(DATA['settings']['brightness'])

    if len(POPULATION) < len(DATA['critters']):
        for critter_data in DATA['critters']:
            critter = critters.Critter(
                critter_data['genes'],
                critter_data['ancestors'],
                position=(
                    random.randint(10, 280),
                    random.randint(10, 210)
                )
            )
            POPULATION.append(critter)
    screen_switch_thread = _thread.start_new_thread(screens, ())
    menu()

Layers = Layer_class()
main()


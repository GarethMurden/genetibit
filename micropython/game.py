
import json
from machine import Pin
import os
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_RGB332
from pimoroni import RGBLED
import pngdec
from random import choice, randint
import _thread
from time import sleep, time
import critters

button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

led = RGBLED(26, 27, 28)

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, pen_type=PEN_RGB332) # size = 320 x 240

png = pngdec.PNG(display)

TEXT = display.create_pen(0, 0, 0)
TEXT_RED = display.create_pen(200, 0, 0)
IMAGES = display.create_pen(200, 200, 200)
display.set_pen(IMAGES)
display.clear()

COOLDOWNS = {
    'breeding': 120, # cooldown before critter can be bred again
    'stock':   3600  # cooldown before market restocks sold items
}

MENU_OPEN = False
CURRENT_SCREEN = 'field'
DATA = {
    'breeding':{
        'cursor_index':0,
        'left_critter_index':0,
        'right_critter_index':1
    },
    'critters':[],
    'field':{
        'level':0,
        'limits':[
            4,
            6,
            8
        ]
    },
    'gold':0,
    'travel':{
        'items':[
            {
                'sprite':'travel/connect',
                'price':0,
                'cooldown':None,
                'cooldown_duration':5
            },
            {
                'sprite':'travel/bus',
                'price':50,
                'cooldown':None,
                'cooldown_duration':90
            },
            {
                'sprite':'travel/earth',
                'price':150,
                'cooldown':None,
                'cooldown_duration':300 # 300 sec = 5 min
            }
        ]
    },
    'settings':{
        'cursor_index':0,
        'brightness':0.6
    }
}
POPULATION = []
BREEDING_PAIR = {}

class Layer_class():
    display_busy= False
    background  = {'file':'field', 'position':(0,0)}
    bottom      = None # multiple overlapping images allowed
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

    def show(self, layers=['background', 'bottom', 'middle', 'top', 'cursor', 'menu_cursor', 'text']):
        
        if self.background is not None and 'background' in layers:
            print('[ DISPLAY ]: Update background')
            self.update_display(self.background['file'], self.background['position'], self.background.get('scale', 1))
        if self.bottom is not None and 'bottom' in layers:
            print('[ DISPLAY ]: Update bottom')
            for image in self.bottom:
                self.update_display(image['file'], image['position'], image.get('scale', 1))
        if self.middle is not None and 'middle' in layers:
            print('[ DISPLAY ]: Update middle')
            for image in self.middle:
                self.update_display(image['file'], image['position'], image.get('scale', 1))
        if self.top is not None and 'top' in layers:
            print('[ DISPLAY ]: Update top')
            self.update_display(self.top['file'], self.top['position'], self.top.get('scale', 1))
        if self.cursor is not None and 'cursor' in layers:
            print('[ DISPLAY ]: Update cursor')
            self.update_display(self.cursor['file'], self.cursor['position'], self.cursor.get('scale', 1))
        if self.menu_cursor is not None and 'menu_cursor' in layers:
            print('[ DISPLAY ]: Update menu_cursor')
            self.update_display(self.menu_cursor['file'], self.menu_cursor['position'], self.menu_cursor.get('scale', 1))
        if self.text is not None and 'text' in layers:
            display.set_pen(TEXT)
            for entry in self.text:
                if entry.get('colour', None) is not 'red':
                    display.text(
                        str(entry['text']),
                        entry['position'][0],
                        entry['position'][1],
                        scale=entry.get('scale', 1)
                    )
            display.set_pen(TEXT_RED)
            for entry in self.text:
                if entry.get('colour', None) is 'red':
                    display.text(
                        str(entry['text']),
                        entry['position'][0],
                        entry['position'][1],
                        scale=entry.get('scale', 1)
                    )
            display.set_pen(IMAGES)
        display.update()

    def update_display(self, filename, position, scale=1):
        while self.display_busy:
            print('[ DISPLAY ]: Busy')
            sleep(0.5)
        self.display_busy = True
        png.open_file(f"assets/{filename}.png")
        png.decode(position[0], position[1], scale=scale)
        self.display_busy = False
        led.set_rgb(0, 0, 0)

def data_cooldown_active(cooldown_end):
    if cooldown_end is None:
        return False
    current_time = time()
    if cooldown_end < current_time:
        return False
    else:
        return True

def data_clear_screen():
    '''clear cached data only needed while screen open'''
    global DATA
    DATA['breeding']['cursor_index'] = 0
    
def data_load():
    global DATA
    print('[ DATA    ]: Load')
    save_file = 'data.json'
    if not file_exits(save_file):
        DATA['critters'] += critters.generate_starters()
        DATA['gold'] = 0
        data_save()
    with open(save_file, 'r', encoding='utf-8') as f:
        DATA = json.loads(f.read())

def data_save():
    print('[ DATA    ]: Save')
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
        'travel',
        'settings'
    ]

    menu_cursor_position = 0
    led.set_rgb(0, 10, 0)
    print('[ MENU    ]: open menu')
    Layers.top = {'file':'menu', 'position':(256, 0)}
    Layers.text = [{
        'text':str(DATA['gold']),
        'position':(285, 10)
    }]
    MENU_OPEN = True
    menu_move_cursor(menu_cursor_position)
    print('[ DISPLAY ]: Layers.show() in menu()')
    Layers.show()
    led.set_rgb(0, 0, 0)

    update_screen = False
    while MENU_OPEN:
        if button_x.value() == 0:
            update_screen = True
            led.set_rgb(0, 10, 0)
            print('[ MENU    ]: close menu')
            Layers.top = None
            Layers.menu_cursor = None
            MENU_OPEN = False

        if button_y.value() == 0:
            update_screen = True
            led.set_rgb(0, 10, 0)
            new_screen = menu_options[menu_cursor_position]
            print(f'[ MENU    ]: moving to "{new_screen}" screen')
            CURRENT_SCREEN = new_screen
            MENU_OPEN = False

        if button_a.value() == 0:
            update_screen = True
            led.set_rgb(0, 10, 0)
            menu_cursor_position = menu_move_cursor(menu_cursor_position - 1)
        
        if button_b.value() == 0:
            update_screen = True
            led.set_rgb(0, 10, 0)
            menu_cursor_position = menu_move_cursor(menu_cursor_position + 1)

        if update_screen:
            print('[ DISPLAY ]: Layers.show() in menu()')
            Layers.show(layers=['top', 'text', 'menu_cursor'])
            led.set_rgb(0, 0, 0)
            update_screen = False
    Layers.top = None
    Layers.menu_cursor = None
    print('[ MENU    ]: menu closed')
    
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
            print('[ DISPLAY ]: Layers.show() in screens()')
            Layers.show()
        if CURRENT_SCREEN == 'field':
            screen_field()
        if CURRENT_SCREEN == 'breeding':
            screen_breeding()
        if CURRENT_SCREEN == 'breeding_animation':
            screen_breeding_animation()
        if CURRENT_SCREEN == 'breeding_result':
            screen_breeding_result()
        if CURRENT_SCREEN == 'travel':
            screen_travel()
        if CURRENT_SCREEN == 'settings':
            screen_settings()

def screen_breeding():
    global DATA, CURRENT_SCREEN, BREEDING_PAIR
    Layers.clear_all()
    Layers.background = {
        'file':'breeding',
        'position':(0, 0)
    }
    print('[ DISPLAY ]: Layers.show() in screen_breeding()')
    update_screen = True
    while CURRENT_SCREEN == 'breeding':

        if button_x.value() == 0:
            menu()
            update_screen = True

        if DATA['breeding']['cursor_index'] == 0:
            Layers.cursor = {
                'file':'updown',
                'position':(75, 45)
            }
            if button_a.value() == 0:
                update_screen = True
                led.set_rgb(0, 10, 0)
                DATA['breeding']['left_critter_index'] -= 1
                if DATA['breeding']['left_critter_index'] == DATA['breeding']['right_critter_index']: # can't have the same on L & R
                    DATA['breeding']['left_critter_index'] -= 1
                    print(f"[ DEBUG   ] : skipping index {DATA['breeding']['left_critter_index']}")
                if DATA['breeding']['left_critter_index'] < 0:
                    DATA['breeding']['left_critter_index'] = len(POPULATION) -1

            if button_b.value() == 0:
                update_screen = True
                led.set_rgb(0, 10, 0)
                DATA['breeding']['left_critter_index'] += 1
                if DATA['breeding']['left_critter_index'] == DATA['breeding']['right_critter_index']: # can't have the same on L & R
                    DATA['breeding']['left_critter_index'] += 1
                    print(f"[ DEBUG   ] : skipping index {DATA['breeding']['left_critter_index']}")
                if DATA['breeding']['left_critter_index'] >= len(POPULATION):
                    DATA['breeding']['left_critter_index'] = 0
            if button_y.value() == 0:
                update_screen = True
                cooldown, _ = POPULATION[DATA['breeding']['left_critter_index']].check_cooldown()
                if not cooldown:
                    led.set_rgb(0, 10, 0)
                    DATA['breeding']['cursor_index'] = 1
                else:
                    led.set_rgb(50, 0, 0)

        else:
            Layers.cursor = {
                'file':'updown',
                'position':(235, 45)
            }
            if button_a.value() == 0:
                update_screen = True
                led.set_rgb(0, 10, 0)
                DATA['breeding']['right_critter_index'] -= 1
                if DATA['breeding']['right_critter_index'] == DATA['breeding']['left_critter_index']: # can't have the same on L & R
                        DATA['breeding']['right_critter_index'] -= 1
                        print(f"[DEBUG] : skipping index {DATA['breeding']['right_critter_index']}")
                if DATA['breeding']['right_critter_index'] < 0:
                    DATA['breeding']['right_critter_index'] = len(POPULATION) -1
            if button_b.value() == 0:
                update_screen = True
                led.set_rgb(0, 10, 0)
                DATA['breeding']['right_critter_index'] += 1
                if DATA['breeding']['right_critter_index'] == DATA['breeding']['left_critter_index']: # can't have the same on L & R
                        DATA['breeding']['right_critter_index'] += 1
                        print(f"[DEBUG] : skipping index {DATA['breeding']['right_critter_index']}")
                if DATA['breeding']['right_critter_index'] >= len(POPULATION):
                    DATA['breeding']['right_critter_index'] = 0

            if button_y.value() == 0:
                update_screen = True
                cooldown, _ = POPULATION[DATA['breeding']['right_critter_index']].check_cooldown()
                if not cooldown:
                    led.set_rgb(0, 10, 0)
                    POPULATION[DATA['breeding']['left_critter_index']].set_cooldown( seconds=COOLDOWNS['breeding'])
                    POPULATION[DATA['breeding']['right_critter_index']].set_cooldown(seconds=COOLDOWNS['breeding'])
                    CURRENT_SCREEN = 'breeding_animation' # change screen on next loop iteration
                    BREEDING_PAIR['mother'] = POPULATION[DATA['breeding']['left_critter_index']]
                    BREEDING_PAIR['father'] = POPULATION[DATA['breeding']['right_critter_index']]
                else:
                    led.set_rgb(50, 0, 0)

        if update_screen:
            Layers.middle = [
                {
                    'file':POPULATION[DATA['breeding']['left_critter_index']].get_sprite(),
                    'position':(15, 65),
                    'scale':4
                },
                {
                    'file':POPULATION[DATA['breeding']['right_critter_index']].get_sprite(),
                    'position':(175, 65),
                    'scale':4
                }
            ]

            cooldown, icon = POPULATION[DATA['breeding']['left_critter_index']].check_cooldown()
            if cooldown:
                Layers.middle.append({
                    'file':icon,
                    'position':(110, 130),
                    'scale':2
                })
            cooldown, icon = POPULATION[DATA['breeding']['right_critter_index']].check_cooldown()
            if cooldown:
                Layers.middle.append({
                    'file':icon,
                    'position':(260, 130),
                    'scale':2
                })

            Layers.text = [
                {
                    'text':POPULATION[DATA['breeding']['left_critter_index']].uid,
                    'position':(50, 189),
                    'scale': 2
                },
                {
                    'text':POPULATION[DATA['breeding']['right_critter_index']].uid,
                    'position':(210, 189),
                    'scale': 2
                }
            ]

            print('[ DISPLAY ]: Layers.show() in screen_breeding()')
            Layers.show()
            update_screen = False
            led.set_rgb(0, 0, 0)


def screen_breeding_visitor(visitor):
    global DATA, CURRENT_SCREEN, BREEDING_PAIR
    Layers.clear_all()
    DATA['breeding']['right_critter_index'] = 0
    led.set_rgb(0, 0, 0)
    Layers.background = {
        'file':'breeding',
        'position':(0, 0)
    }

    # de-bounce
    while button_y.value() == 0:
        sleep(0.25)

    update_screen = True
    while CURRENT_SCREEN == 'breeding':

        Layers.cursor = {
            'file':'updown',
            'position':(235, 45)
        }
        if button_a.value() == 0:
            update_screen = True
            led.set_rgb(0, 10, 0)
            DATA['breeding']['right_critter_index'] -= 1
            if DATA['breeding']['right_critter_index'] < 0:
                DATA['breeding']['right_critter_index'] = len(POPULATION) -1
        if button_b.value() == 0:
            update_screen = True
            led.set_rgb(0, 10, 0)
            DATA['breeding']['right_critter_index'] += 1
            if DATA['breeding']['right_critter_index'] >= len(POPULATION):
                DATA['breeding']['right_critter_index'] = 0

        if button_y.value() == 0:
            update_screen = True
            cooldown, _ = POPULATION[DATA['breeding']['right_critter_index']].check_cooldown()
            if not cooldown:
                led.set_rgb(0, 10, 0)
                POPULATION[DATA['breeding']['right_critter_index']].set_cooldown( seconds=COOLDOWNS['breeding'])
                CURRENT_SCREEN = 'breeding_animation' # change screen on next loop iteration

                BREEDING_PAIR['mother'] = visitor
                BREEDING_PAIR['father'] = POPULATION[DATA['breeding']['right_critter_index']]
            else:
                led.set_rgb(50, 0, 0)
        
        if update_screen:
            Layers.middle = [
                {
                    'file':visitor.get_sprite(),
                    'position':(15, 65),
                    'scale':4
                },
                {
                    'file':POPULATION[DATA['breeding']['right_critter_index']].get_sprite(),
                    'position':(175, 65),
                    'scale':4
                }
            ]

            cooldown, icon = POPULATION[DATA['breeding']['right_critter_index']].check_cooldown()
            if cooldown:
                Layers.middle.append({
                    'file':icon,
                    'position':(260, 130),
                    'scale':2
                })

            Layers.text = [
                {
                    'text':visitor.uid,
                    'position':(50, 189),
                    'scale': 2
                },
                {
                    'text':POPULATION[DATA['breeding']['right_critter_index']].uid,
                    'position':(210, 189),
                    'scale': 2
                }
            ]

            print('[ DISPLAY ]: Layers.show() in screen_breeding_visitor()')
            Layers.show()
            update_screen = False
            led.set_rgb(0, 0, 0)

def screen_breeding_animation():
    global CURRENT_SCREEN
    Layers.clear_all()
    Layers.background = {
        'file':'blank',
        'position':(0, 0)
    }
    Layers.bottom = [{
        'file':'animation_hatch/hatch01',
        'position':(60, 100),
        'scale':4
    }]
    print('[ DISPLAY ]: Layers.show() in screen_breeding_animation()')
    Layers.show()

    mother = BREEDING_PAIR['mother']
    father = BREEDING_PAIR['father']
    DATA['breeding']['children'] = []
    for x in range(4):
        sleep(0.5)
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
    Layers.bottom = [{
        'file':'animation_hatch/hatch02',
        'position':(60, 100),
        'scale':4
    }]
    print('[ DISPLAY ]: Layers.show() in screen_breeding_animation()')
    Layers.show(layers=['bottom'])
    Layers.bottom = [{
        'file':'animation_hatch/hatch03',
        'position':(60, 100),
        'scale':4
    }]
    print('[ DISPLAY ]: Layers.show() in screen_breeding_animation()')
    Layers.show(layers=['bottom'])
    sleep(1)
    Layers.bottom = [{
        'file':'animation_hatch/hatch04',
        'position':(60, 100),
        'scale':4
    }]
    print('[ DISPLAY ]: Layers.show() in screen_breeding_animation()')
    Layers.show(layers=['bottom'])
    sleep(1)
    Layers.bottom = [{
        'file':'animation_hatch/hatch05',
        'position':(60, 100),
        'scale':4
    }]
    print('[ DISPLAY ]: Layers.show() in screen_breeding_animation()')
    Layers.show(layers=['bottom'])
    sleep(0.25)
    Layers.bottom = [{
        'file':'animation_hatch/hatch06',
        'position':(60, 100),
        'scale':4
    }]
    print('[ DISPLAY ]: Layers.show() in screen_breeding_animation()')
    Layers.show(layers=['bottom'])
    Layers.bottom = [{
        'file':'animation_hatch/hatch07',
        'position':(60, 100),
        'scale':4
    }]
    print('[ DISPLAY ]: Layers.show() in screen_breeding_animation()')
    Layers.show(layers=['bottom'])
    sleep(1)
    Layers.bottom = None
    CURRENT_SCREEN = 'breeding_result'

def screen_breeding_sale(children):
    global DATA, CURRENT_SCREEN, POPULATION
    Layers.clear_all()
    Layers.background = {
        'file':'breeding_sell',
        'position':(0,0)
    }
    Layers.bottom = [{
        'file':'breeding_sell_toggles',
        'position':(249, 2)
    }]
    
    Layers.text = [{
        'text':str(DATA['gold']),
        'position':(285, 10)
    }]

    Layers.middle = []

    # TODO:
    #   - Check field level & show applicable locks
    Layers.text.append({ # placeholder
        'text':f"lvl {DATA['field']['level']}",
        'position':(25, 220)
    })
    #   - Check POPULATION & fill correct no. of circles
    Layers.text.append({ # placeholder
        'text':f"pop {len(POPULATION)} / {DATA['field']['limits'][DATA['field']['level']]}",
        'position':(100, 220)
    })
    available_space = DATA['field']['limits'][DATA['field']['level']] - len(POPULATION)
    #   - Check available space against selected children to sell
    #   - Pre-select children based on space

    
    for v_counter, critter in enumerate(children):
        value = critter.get_value()

        vertical_position = 10 + (48 * v_counter)
        Layers.middle.append({
            'file':     critter.get_sprite(),
            'position': (10, vertical_position),
            'scale':    2
        })
        Layers.text.append({
            'text':value['phenotype']['rank'],
            'position':(110, vertical_position + 18),
            'scale': 3
        })
        Layers.text.append({
            'text':f"{value['heterozygousity']}%",
            'position':(145, vertical_position + 20),
            'scale': 2
        })
        Layers.text.append({
            'text':value['phenotype']['value'],
            'position':(215, vertical_position + 20),
            'scale': 2
        })
    Layers.show()

    cursor_positions = [
        (245,  30),
        (245,  79),
        (245, 128),
        (245, 175),
        (218, 215) # OK button
    ]
    checkmark_positions = [
        (252,  33),
        (252,  81),
        (252, 129),
        (252, 176)
    ]
    if 'sell_selections' not in DATA['breeding']:
        DATA['breeding']['sell_selections'] = [False, False, False, False]

    if 'gold' not in DATA:
        DATA['gold'] = 0
    previous_cursor_index = None
    previous_sell_selections = None
    while True:
        if not MENU_OPEN:
            update_screen = False
            if button_a.value() == 0:
                led.set_rgb(0, 10, 0)
                DATA['breeding']['cursor_index'] -= 1
                if DATA['breeding']['cursor_index'] < 0:
                    DATA['breeding']['cursor_index'] = len(cursor_positions) -1
            
            if button_b.value() == 0:
                led.set_rgb(0, 10, 0)
                DATA['breeding']['cursor_index'] += 1
                if DATA['breeding']['cursor_index'] == len(cursor_positions):
                    DATA['breeding']['cursor_index'] = 0

            if button_y.value() == 0:
                led.set_rgb(0, 10, 0)
                if DATA['breeding']['cursor_index'] != len(cursor_positions) -1: # sell checkbox highlighted
                    if DATA['breeding']['sell_selections'][DATA['breeding']['cursor_index']]:
                        DATA['breeding']['sell_selections'][DATA['breeding']['cursor_index']] = False
                    else:
                        DATA['breeding']['sell_selections'][DATA['breeding']['cursor_index']] = True
                
                else: # ok button highlighted
                    if len([x for x in DATA['breeding']['sell_selections'] if x]) <= available_space:
                        for index, sold in enumerate(DATA['breeding']['sell_selections']):
                            if sold:
                                DATA['gold'] += children[index].get_value()['phenotype']['value']
                            else:
                                POPULATION.append(children[index])
                                DATA['critters'].append({
                                    'ancestors':children[index].ancestors,
                                    'genes':children[index].get_genotype(),
                                    'uid':children[index].uid
                                })
                        del DATA['breeding']['sell_selections']
                        DATA['breeding']['cursor_index'] = 0
                        data_save()
                        CURRENT_SCREEN = 'field'
                        break

            # only update screen if something's changed
            if previous_cursor_index != DATA['breeding']['cursor_index']:
                update_screen = True
                previous_cursor_index = DATA['breeding']['cursor_index']
                Layers.cursor = {
                    'file':'cursor',
                    'position':cursor_positions[DATA['breeding']['cursor_index']]
                }

            if previous_sell_selections != DATA['breeding']['sell_selections']:
                update_screen = True
                previous_sell_selections = DATA['breeding']['sell_selections'].copy()
                Layers.bottom = [{
                    'file':'breeding_sell_toggles',
                    'position':(249, 2)
                }]
                for counter, selected in enumerate(DATA['breeding']['sell_selections']):
                    if selected:
                        Layers.bottom.append({
                            'file':'tick',
                            'position':checkmark_positions[counter],
                        })
                if len([x for x in DATA['breeding']['sell_selections'] if x]) > available_space:
                    # TODO: 
                    #   - Show warning alongside population indicator
                    #   - Cross-out OK button
                    pass
                

            if update_screen:
                print('[ DISPLAY ]: Layers.show() in screen_breeding_sale()')
                Layers.show(layers=['bottom', 'cursor'])
        led.set_rgb(0, 0, 0)

def screen_breeding_result():
    global DATA, CURRENT_SCREEN, POPULATION, BREEDING_PAIR
    Layers.clear_all()

    mother = BREEDING_PAIR['mother']
    father = BREEDING_PAIR['father']
    children = []

    for child in DATA['breeding']['children']:
        children.append(critters.Critter(child['genes'], ancestors=child['ancestors']))

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
            'position':(5, 125),
            'scale':3
        },
        {
            'file':children[1].get_sprite(),
            'position':(75, 125),
            'scale':3
        },
        {
            'file':children[2].get_sprite(),
            'position':(155, 125),
            'scale':3
        },
        {
            'file':children[3].get_sprite(),
            'position':(230, 125),
            'scale':3
        }
    ]

    print('[ DISPLAY ]: Layers.show() in screen_breeding_result()')
    Layers.show()
    sleep(3)
    DATA['breeding']['cursor_index'] = 0
    BREEDING_PAIR = {}
    screen_breeding_sale(children)

def screen_bus_animation():
    global CURRENT_SCREEN
    Layers.cursor = None
    Layers.text = None
    for x in range(8):
        left = -560 + (x * 80)
        Layers.top = {
            'file':'transition_bus',
            'position':(left, 0)
        }
        print('[ DISPLAY ]: Layers.show() in screen_bus_animation()')
        Layers.show()
    CURRENT_SCREEN = 'visitor'

def screen_connect():
    global CURRENT_SCREEN
    Layers.clear_all()
    # TODO: Connect to second device
    Layers.clear_all()
    Layers.background = {
        'file':'blank',
        'position':(0, 0)
    }
    Layers.text = [{
        'text':'CONNECT',
        'position':(10, 10)
    }]

    update_screen = True
    while CURRENT_SCREEN == 'connect':
        if  button_x.value() == 0:
            menu()
            update_screen = True

        if update_screen:
            print('[ DISPLAY ]: Layers.show() in screen_connect()')
            Layers.show()
            update_screen = False

def screen_contest_map():
    Layers.clear_all()
    Layers.background = {
        'file':'world_map',
        'position':(0, 0)
    }

    update_screen = True
    while CURRENT_SCREEN == 'contest_map':
        if button_x.value() == 0:
            menu()
            update_screen = True

        if update_screen:
            print('[ DISPLAY ]: Layers.show() in screen_contest_map()')
            Layers.show()
            update_screen = False

def screen_connect_animation():
    # TODO: connection transition animation
    pass

def screen_field():
    global POPULATION, CURRENT_SCREEN
    Layers.clear_all()
    Layers.background = {
        'file':f'field_{DATA["field"]["level"]}',
        'position':(0, 0)
    }
    print('[ DISPLAY ]: Layers.show() in screen_field()')
    Layers.show()
    menu_thread = _thread.start_new_thread(screen_field_menu, ())
    while 'field' in CURRENT_SCREEN:
        Layers.middle = []
        for critter in POPULATION:
            if button_x.value() == 0:
                menu()
            if choice([True, True, False]):
                critter.move()
            Layers.middle.append({
                'file':critter.get_sprite(),
                'position':critter.get_position(),
                'scale':2
            })
        if CURRENT_SCREEN == 'field': # only update screen if menu not open
            print('[ DISPLAY ]: Layers.show() in screen_field()')
            Layers.show()
            sleep(5)

def screen_field_menu():
    global CURRENT_SCREEN
    while 'field' in CURRENT_SCREEN:
        if button_x.value() == 0:
            CURRENT_SCREEN = 'field_menu'
            menu()
            break

def screen_gold_animation(change):
    if change != 0:
        if change < 0:
            colour = 'red'
            text = str(change)
        else:
            colour = 'black'
            text = f'+{change}'
        Layers.text.append({
            'text':text,
            'position':(280, 25),
            'colour':colour
        })
        print('[ DISPLAY ]: Layers.show() in screen_gold_animation()')
        Layers.show()

def screen_plane_animation():
    global CURRENT_SCREEN
    Layers.cursor = None
    Layers.text = None
    for x in range(8):
        left = -560 + (x * 80)
        Layers.top = {
            'file':'transition_plane',
            'position':(left, 0)
        }
        print('[ DISPLAY ]: Layers.show() in screen_plane_animation()')
        Layers.show()
    CURRENT_SCREEN = 'contest_map'
    
def screen_travel():
    Layers.background = {
        'file':'travel',
        'position':(0, 0)
    }

    item_coordinates = [
        {'sprite':( 48, 75), 'price':( 53, 159)},
        {'sprite':(143, 85), 'price':(153, 159)},
        {'sprite':(240, 85), 'price':(250, 159)}
    ]
    Layers.middle = []
    Layers.text = [{
        'text':str(DATA['gold']),
        'position':(285, 10)
    }]
    for index, item in enumerate(DATA['travel']['items']):
        Layers.middle.append({
            'file':item['sprite'],
            'position':item_coordinates[index]['sprite'],
            'scale':2
        })
        Layers.text.append({
            'text':str(item['price']),
            'position':item_coordinates[index]['price']
        })
        if data_cooldown_active(item['cooldown']):
            Layers.middle.append({
                'file':'/travel/sold_out',
                'position':(
                    item_coordinates[index]['sprite'][0] - 15,
                    item_coordinates[index]['sprite'][1] + 10
                )
            })

    item_bought = False
    cursor_positions = [
        ( 55, 155),
        (153, 155),
        (248, 155)
    ]
    cursor_index = 0
    update_screen = True
    while CURRENT_SCREEN == 'travel':
        if button_x.value() == 0:
            menu()
            update_screen = True

        if button_a.value() == 0:
            led.set_rgb(0, 10, 0)
            cursor_index -= 1
            if cursor_index < 0:
                cursor_index = len(cursor_positions) -1
            update_screen = True

        if button_b.value() == 0:
            led.set_rgb(0, 10, 0)
            cursor_index += 1
            if cursor_index >= len(cursor_positions):
                cursor_index = 0
            update_screen = True

        if button_y.value() == 0:
            if not data_cooldown_active(DATA['travel']['items'][cursor_index]['cooldown']):
                if DATA['gold'] > DATA['travel']['items'][cursor_index]['price']:
                    led.set_rgb(0, 10, 0)
                    DATA['gold'] -= DATA['travel']['items'][cursor_index]['price']
                    Layers.text[0] = {
                        'text':str(DATA['gold']),
                        'position':(285, 10)
                    }
                    DATA['travel']['items'][cursor_index]['cooldown'] = time() + DATA['travel']['items'][cursor_index]['cooldown_duration']
                    item_bought = DATA['travel']['items'][cursor_index]['sprite']
                else:
                    led.set_rgb(50, 0, 0) # not enough gold
            else:
                led.set_rgb(50, 0, 0) # sold out
            update_screen = True

        if update_screen:
            Layers.cursor = {
                'file':'cursor',
                'position':cursor_positions[cursor_index]
            }
            print('[ DISPLAY ]: Layers.show() in screen_travel()')
            Layers.show()
            led.set_rgb(0, 0, 0)
            update_screen = False

        if item_bought:
            screen_gold_animation(0 - DATA['travel']['items'][cursor_index]['price'])
            break

    if item_bought:
        if 'earth' in item_bought:
            screen_plane_animation()
            screen_contest_map()
        if 'bus' in item_bought:
            screen_bus_animation()
            screen_visitor()
        if 'connect' in item_bought:
            screen_connect_animation()
            screen_connect()

def screen_settings():
    global DATA, CURRENT_SCREEN
    Layers.clear_all()
    cursor_positions = [
        ( 40, 65),
        (140, 65)
    ]
    Layers.background = {
        'file':'settings',
        'position':(0, 0)
    }
    Layers.show(layers=['background'])
    cursor_index = 0
    update_screen = True
    print(f'[ SETTING ]: {CURRENT_SCREEN=}, {update_screen=}')
    while CURRENT_SCREEN == 'settings':
        if button_a.value() == 0:
            update_screen = True
            cursor_index -= 1
            if cursor_index < 0:
                cursor_index = 1
        if button_b.value() == 0:
            update_screen = True
            cursor_index =+ 1
            if cursor_index > 1:
                cursor_index = 0
        if button_y.value() == 0:
            update_screen = True
            if cursor_index == 1:
                DATA['settings']['brightness'] = min([
                    DATA['settings']['brightness'] + 0.2,
                    1.0
                ])
                display.set_backlight(DATA['settings']['brightness'])
            else:
                update_screen = True
                DATA['settings']['brightness'] = max([
                    DATA['settings']['brightness'] - 0.2,
                    0.2
                ])
                display.set_backlight(DATA['settings']['brightness'])

        if button_x.value() == 0:
            menu()

        if update_screen:
            Layers.bottom = [{
                'file':f"settings_brightness{DATA['settings']['brightness']}",
                'position':(0, 0)
            }]
            Layers.cursor = {
                'file':'cursor',
                'position':cursor_positions[cursor_index]
            }
            print('[ DISPLAY ]: Layers.show() in screen_settings()')
            Layers.show(layers=['background', 'bottom', 'cursor'])
            update_screen = False
    data_save()

def screen_visitor():
    global CURRENT_SCREEN
    Layers.clear_all()
    Layers.background = {
        'file':'visit',
        'position':(0, 0)
    }

    options = [
        critters.Critter(critters.generate_random_genes()),
        critters.Critter(critters.generate_random_genes()),
        critters.Critter(critters.generate_random_genes())
    ]
    Layers.middle = []
    option_positions = [
        ( 42, 161),
        (142, 132),
        (230, 149)
    ]
    for counter, option in enumerate(options):
        Layers.middle.append({
            'file':option.get_sprite(),
            'position':option_positions[counter]
        })

    panel_positions = [
        (  0, 50),
        ( 95, 15),
        (194, 30)
    ]
    panel_index = 0
    update_screen = True
    while CURRENT_SCREEN == 'visitor':
        if button_a.value() == 0:
            led.set_rgb(0, 10, 0)
            panel_index -= 1
            if panel_index < 0:
                panel_index = len(panel_positions) -1
            update_screen = True
        if button_b.value() == 0:
            led.set_rgb(0, 10, 0)
            panel_index += 1
            if panel_index >= len(panel_positions):
                panel_index = 0
            update_screen = True

        if button_y.value() == 0:
            led.set_rgb(0, 10, 0)
            CURRENT_SCREEN = 'breeding'
            screen_breeding_visitor(options[panel_index])

        if update_screen:
            Layers.top = {
                'file':'info_panel',
                'position':panel_positions[panel_index]
            }

            option_data = options[panel_index].get_value()
            Layers.text = [
                {
                    'text':options[panel_index].uid,
                    'position':(
                        panel_positions[panel_index][0] + 22,
                        panel_positions[panel_index][1] + 9
                    ),
                    'scale':2
                },
                {
                    'text':option_data['phenotype']['rank'],
                    'position':(
                        panel_positions[panel_index][0] + 54,
                        panel_positions[panel_index][1] + 29
                    ),
                    'scale':2
                },
                {
                    'text':f"{option_data['heterozygousity']}%",
                    'position':(
                        panel_positions[panel_index][0] + 54,
                        panel_positions[panel_index][1] + 46
                    ),
                    'scale':2
                }
            ]

            print('[ DISPLAY ]: Layers.show() in screen_visitor()')
            Layers.show()
            update_screen = False
        led.set_rgb(0, 0, 0)

def main():
    led.set_rgb(75, 25, 0)
    global POPULATION
    data_load()
    display.set_backlight(DATA['settings']['brightness'])

    if len(POPULATION) < len(DATA['critters']):
        for critter_data in DATA['critters']:
            critter = critters.Critter(
                critter_data['genes'],
                critter_data['ancestors'],
                position=(
                    randint(10, 280),
                    randint(10, 210)
                ),
                uid=critter_data['uid']
            )
            POPULATION.append(critter)
    led.set_rgb(0, 0, 0)
    screens()

Layers = Layer_class()
main()


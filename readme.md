# Genetic Digital Pet

Maintan a population of critters with realistic genetic inheritance and selectively breed rare traits to sell to collectors.

## Gameplay

See your creatures in the field

![](https://github.com/GarethMurden/genetibit/blob/master/screenshots/field.png?raw=true)

Selectively breed creatures to find interesting traits

![](https://github.com/GarethMurden/genetibit/blob/master/screenshots/inheritance_example.png?raw=true)

Introduce new genes from visiting critters

![](https://github.com/GarethMurden/genetibit/blob/master/screenshots/visitor.png?raw=true)

Sell creatures with rare trates at the market

![](https://github.com/GarethMurden/genetibit/blob/master/screenshots/breeding_sell.png?raw=true)

Upgrade your field to fit more creatures

`Coming soon`

Enter your critters in shows to earn ribbons

![](https://github.com/GarethMurden/genetibit/blob/master/screenshots/world_map.png?raw=true)

Connect two devices to breed your critters with your friends'

`Coming soon`

## Hardware

- [PicoLipo](https://thepihut.com/products/pico-lipo?variant=40824959467715) RP2040-powered microcontroller
- [3.7V, 2000mAh LiPo battery](https://thepihut.com/products/2000mah-3-7v-lipo-battery?variant=42143258050755)
- [Pico display & buttons](https://thepihut.com/products/pico-display-pack-2-8?variant=43884934791363)
- [Real time clock](https://thepihut.com/products/sparkfun-real-time-clock-module?variant=39559108001987)
- Optional [magnetic connector](https://thepihut.com/products/diy-magnetic-connector-straight-angle-five-contact-pins?variant=42058938253507) for device-to-device communication

## Credits

- Top down tileset from [Otterisk](https://otterisk.itch.io/)
- Sproutlands UI from [Cup Nooble](https://cupnooble.itch.io/)

# Development notes

## To do

- Features
	- Upgrade field
	- Select critter from field to view info
		- Sell critters from field
	- Competitions
	- Device-to-device communication

- Fixes
	- Travel text appears before background changes
	- Shouldn't be possible to breed a critter to itself
	- Cursors don't move to right on breeding screen after first selection
	- Price sticks after menu close
	- selecting the current screen from the menu leaves menu open
	- Opening menu within breeding result flow should not be allowed

## Resources 

https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/pico_display


## Notes on `rshell`

### Connect

As an alternative to Thonny, `rshell` can be used to flash the Pico from the terminal.

https://www.martinfitzpatrick.dev/using-micropython-raspberry-pico/

1. Connect the Pico & determine it's COM port (e.g. via Windows device manager)
2. Start rshell with `rshell`
3. Check if the board's auto-connected with `boards`
4. If not, connect with `connect serial COM<port>`

### Upload

`rshell` treats the Pico as a virtual folder, files can be copied to it like so:

`cp <source> /pyboard/<destination>`

Where `<source>` is a path on the PC and `<destination>` is on the Pico's filesystem.

Make sure the source `.py` file is pre-compiled into a `.mpy` before copying to save RAM:

`python -m mpy_cross <source>`

### Run

The `game.py` file runs as soon as it's imported so it can be triggered with the following steps:

1. Acces the pico with `repl`
2.  `import game` to run `game.py`

(`Ctrl`+`X` to quit)

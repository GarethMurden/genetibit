
import os
from PIL import Image

dirname, _ = os.path.split(os.path.abspath(__file__))
THIS_DIRECTORY = f'{dirname}{os.sep}'

def draw(creatures, level=0):
	background = Image.open(f'{THIS_DIRECTORY}assets{os.sep}background{os.sep}field_{level}.png')

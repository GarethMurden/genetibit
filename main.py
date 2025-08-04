
import os
from scenes import field, breeding
from objects import Creature

dirname, _ = os.path.split(os.path.abspath(__file__))
THIS_DIRECTORY = f'{dirname}{os.sep}'

def main():
	parent_a = Creature(
		{
			'head':['sa','shi'],
			'body':['ka','ki'],
			'legs':['ta','chi'],
			'colour':['blue', 'red']
		}
	)
	parent_b = Creature(
		{
			'head':['sa','shi'],
			'body':['ka','ki'],
			'legs':['ta','chi'],
			'colour':['blue', 'red']
		}
	)

	breeding.breed(parent_a, parent_b)

	

if __name__ == '__main__':
	main()

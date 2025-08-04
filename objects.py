
import os
import random

dirname, _ = os.path.split(os.path.abspath(__file__))
THIS_DIRECTORY = f'{dirname}{os.sep}'

class Creature():
	def __init__(self, genes, ancestors=['unknown','unknown'], position=(0,0)):
		self.ancestors = ancestors
		# ancestors = [
		# 	['sekote_blue', 'sakochi_blue']
		# ]
		self.genes = genes
		# genes = {
		# 	'head':['sa','sa'],
		# 	'body':['ka','ka'],
		# 	'legs':['ta','ta'],
		#	'colour':['blue', 'blue']
		# }
		self.x = position[0]
		self.y = position[1]

	def get_genotype(self):
		return {
			'head':sorted(self.genes['head']),
			'body':sorted(self.genes['body']),
			'legs':sorted(self.genes['legs']),
			'colour':sorted(self.genes['colour'])
		}

	def get_phenotype(self):
		return {
			'head':sorted(self.genes['head'])[0],
			'body':sorted(self.genes['body'])[0],
			'legs':sorted(self.genes['legs'])[0],
			'colour':self.get_colour()
		}

	def get_colour(self):
		colour = sorted(self.genes['colour'])
		if colour[0] == colour[1]:
			return colour[0]
		if 'blue' in colour and 'red' in colour:
			return 'purple'
		if 'blue' in colour and 'yellow' in colour:
			return 'green'
		if 'red' in colour and 'yellow' in colour:
			return 'orange'

	def get_name(self):
		genes = self.get_phenotype()
		return ''.join([genes['head'], genes['body'], genes['legs']])

	def get_sprite(self):
		name = self.get_name()
		colour = self.get_colour()
		return f'{THIS_DIRECTORY}assets{os.sep}creatures{os.sep}{name}_{colour}.png'

	def get_gamete(self):
		return {
			'head':random.choice(self.genes['head']),
			'body':random.choice(self.genes['body']),
			'legs':random.choice(self.genes['legs']),
			'colour':random.choice(self.genes['colour'])
		}


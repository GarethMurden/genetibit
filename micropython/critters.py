import random

class Critter():
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
		self.position = [position[0], position[1]]

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

	def get_gamete(self):
		return {
			'head':random.choice(self.genes['head']),
			'body':random.choice(self.genes['body']),
			'legs':random.choice(self.genes['legs']),
			'colour':random.choice(self.genes['colour'])
		}

	def get_genotype(self):
		return {
			'head':sorted(self.genes['head']),
			'body':sorted(self.genes['body']),
			'legs':sorted(self.genes['legs']),
			'colour':sorted(self.genes['colour'])
		}

	def get_name(self):
		genes = self.get_phenotype()
		return ''.join([genes['head'], genes['body'], genes['legs']])

	def get_phenotype(self):
		return {
			'head':sorted(self.genes['head'])[0],
			'body':sorted(self.genes['body'])[0],
			'legs':sorted(self.genes['legs'])[0],
			'colour':self.get_colour()
		}

	def get_position(self):
		return tuple(self.position)

	def get_sprite(self):
		name = self.get_name()
		colour = self.get_colour()
		return f'creatures/{name}_{colour}'

	def move(self):
		if random.choice(['h', 'h', 'v']) == 'h':
			change = random.randint(-5, 5) * 2
			if 10 < self.position[0] + change < 310:
				self.position[0] = self.position[0] + change
		else:
			change = random.randint(-5, 5) * 2
			if 10 < self.position[1] + change < 230:
				self.position[1] = self.position[1] + change

def build_ancestry(parent_a, parent_b):
	ancestry = [[f'{parent_a.get_name()}_{parent_a.get_colour()}', f'{parent_b.get_name()}_{parent_b.get_colour()}']]
	ancestry_a = parent_a.ancestors
	ancestry_b = parent_b.ancestors
	for x in range(max([len(ancestry_a), len(ancestry_b)])):
		generation = []
		if x < len(ancestry_a):
			generation.append(ancestry_a[x])
		else:
			generation.append([['unkown', 'unkown'] for y in range(x +1)])
		if x < len(ancestry_b):
			generation.append(ancestry_b[x])
		else:
			generation.append([['unkown', 'unkown'] for y in range(x +1)])
		ancestry.append(generation)
	return ancestry

def generate_starters():
	colour = random.choice([
		['yellow', 'yellow'],
		['blue', 'blue'],
		['red', 'red']
	])
	head_options = ['sa', 'shi', 'su', 'se', 'so']
	head = random.choice(head_options)
	body_options = ['ka', 'ki', 'ku', 'ke', 'ko']
	body = random.choice(body_options)
	leg_options = ['ta', 'chi', 'tsu', 'te', 'to']
	legs = random.choice(leg_options)
	first = {
		'genes':{
			'head':[head, head],
			'body':[body, body],
			'legs':[legs, legs],
			'colour':colour
		},
		'ancestors':['unknown', 'unknown']
	}
	second = {
		'genes':{
			'head':[head, random.choice(head_options)],
			'body':[body, random.choice(body_options)],
			'legs':[legs, random.choice(leg_options)],
			'colour':colour
		},
		'ancestors':['unknown', 'unknown']
	}
	return [first, second]
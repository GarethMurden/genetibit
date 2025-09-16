import random

HEAD_OPTIONS = ['sa', 'se', 'shi', 'so', 'su']
BODY_OPTIONS = ['ka', 'ke', 'ki',  'ko', 'ku']
LEG_OPTIONS = ['chi', 'ta', 'te',  'to', 'tsu']

class Critter():
	def __init__(self, genes, ancestors=['unknown','unknown'], position=None):
		self.ancestors = ancestors
		self.genes = genes
		if position is None:
			position = (
				random.randint(10, 280),
				random.randint(10, 210)
			)
		self.position = [position[0], position[1]]
		self.id = generate_id()

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

	def get_value(self):
		ranks = [
			'D',
			'C',
			'B',
			'A',
			'S'
		]
		phenotype = self.get_phenotype()
		head_value = HEAD_OPTIONS.index(phenotype['head']) +1
		body_value = BODY_OPTIONS.index(phenotype['body']) +1
		legs_value = LEG_OPTIONS.index( phenotype['legs']) +1

		genes = self.get_genotype()
		if genes['colour'][0] == genes['colour'][1]:
			colour_value = 5
		else:
			colour_value = 3
		return {
			'head':{'rank':ranks[head_value -1], 'value':head_value},
			'body':{'rank':ranks[body_value -1], 'value':body_value},
			'legs':{'rank':ranks[legs_value -1], 'value':legs_value},
			'colour':{'rank':ranks[colour_value -1], 'value':colour_value},
			'total':sum([head_value, body_value, legs_value, colour_value])
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
			if 10 < self.position[0] + change < 280:
				self.position[0] = self.position[0] + change
		else:
			change = random.randint(-5, 5) * 2
			if 10 < self.position[1] + change < 210:
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

def generate_id():
	source = ['c','b','d','f','g','h','j','k','m','n','p','q','r','s','t','v','w','x','y','z','1','2','3','4','5','6','7','8','9']
	return ''.join(random.sample(source, 4))

def generate_starters():
	colour = random.choice([
		['yellow', 'yellow'],
		['blue', 'blue'],
		['red', 'red']
	])
	head = random.choice(HEAD_OPTIONS)
	body = random.choice(BODY_OPTIONS)
	legs = random.choice(LEG_OPTIONS)
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
			'head':[head, random.choice(HEAD_OPTIONS)],
			'body':[body, random.choice(BODY_OPTIONS)],
			'legs':[legs, random.choice(LEG_OPTIONS)],
			'colour':colour
		},
		'ancestors':['unknown', 'unknown']
	}
	return [first, second]

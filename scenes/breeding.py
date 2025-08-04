
import json
from PIL import Image
from objects import Creature

def breed(parent_a, parent_b, child_count=4):	
	output = Image.new('RGBA', (16 * 4, 16 * 4))

	parent_a_sprite = Image.open(parent_a.get_sprite())
	output.paste(
		parent_a_sprite,
		(parent_a_sprite.width, 0),
		parent_a_sprite
	)
	parent_b_sprite = Image.open(parent_b.get_sprite())
	output.paste(
		parent_b_sprite,
		(parent_b_sprite.width * 2, 0),
		parent_b_sprite
	)

	children = []
	for x in range(child_count):
		gamete_a = parent_a.get_gamete()
		gamete_b = parent_b.get_gamete()
		child_genes = {
			'head':[gamete_a['head'], gamete_b['head']],
			'body':[gamete_a['body'], gamete_b['body']],
			'legs':[gamete_a['legs'], gamete_b['legs']],
			'colour':[gamete_a['colour'], gamete_b['colour']]
		}
		child = Creature(
			child_genes,
			ancestors=build_ancestry(parent_a, parent_b)
		)
		child_sprite = Image.open(child.get_sprite())
		output.paste(
			child_sprite,
			(child_sprite.width * x, child_sprite.height),
			child_sprite
		)
		children.append(child)


	print(f'{parent_a.get_name()} x {parent_b.get_name()}')
	print(' '.join([c.get_name() for c in children]))

	output.show()

	return children

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

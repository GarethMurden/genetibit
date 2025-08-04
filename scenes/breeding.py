
import json
from PIL import Image
from objects import Creature

def breed(parent_a, parent_b):
	print(parent_a.get_name())
	print(json.dumps(parent_a.genes))

	print(parent_b.get_name())
	print(json.dumps(parent_b.genes))
	
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
	for x in range(4):
		gamete_a = parent_a.get_gamete()
		gamete_b = parent_b.get_gamete()
		child_genes = {
			'head':[gamete_a['head'], gamete_b['head']],
			'body':[gamete_a['body'], gamete_b['body']],
			'legs':[gamete_a['legs'], gamete_b['legs']],
			'colour':[gamete_a['colour'], gamete_b['colour']]
		}
		child = Creature(child_genes)
		child_sprite = Image.open(child.get_sprite())
		output.paste(
			child_sprite,
			(child_sprite.width * x, child_sprite.height),
			child_sprite
		)

	output.show()


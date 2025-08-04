
import json
import os
import random

from objects import Creature
from scenes import field, breeding

dirname, _ = os.path.split(os.path.abspath(__file__))
THIS_DIRECTORY = f'{dirname}{os.sep}'

POPULATION_FILE = f'{THIS_DIRECTORY}data{os.sep}population.json'

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.loads(f.read())

def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4))

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
	first = Creature({
		'head':[head, head],
		'body':[body, body],
		'legs':[legs, legs],
		'colour':colour
	})
	second = Creature({
		'head':[head, random.choice(head_options)],
		'body':[body, random.choice(body_options)],
		'legs':[legs, random.choice(leg_options)],
		'colour':colour
	})
	return [first, second]

def get_population():
	creatures = []
	if os.path.exists(POPULATION_FILE):
		creature_data = load_json(POPULATION_FILE)
		for entry in creature_data:
			creatures.append(Creature(entry['genes'], entry['ancestry']))
	else:
		creatures = generate_starters()
	return creatures

def save_population(creatures):
	creature_data = []
	for creature in creatures:
		creature_data.append({'genes':creature.get_genotype(), 'ancestry':creature.ancestors})
	save_json(creature_data, POPULATION_FILE)

def main():
	creatures = get_population()
	creatures += breeding.breed(creatures[0], creatures[1], child_count=4)
	save_population(creatures)



if __name__ == '__main__':
	main()

	# a = Creature(
	# 	{"head": ["se", "se"], "body": ["ko", "ko"], "legs": ["te", "te"], "colour": ["red", "red"]},
	# 	ancestors=[['grandparent_a', 'grandparent_a']]
	# )

	# b = Creature(
	# 	{"head": ["se", "sa"], "body": ["ko", "ko"], "legs": ["te", "chi"], "colour": ["red", "red"]},
	# 	ancestors=[
	# 		['grandparent_b', 'grandparent_b'],
	# 		[['great_grandparent_b1', 'great_grandparent_b1'], ['great_grandparent_b2', 'great_grandparent_b2']]
	# 	]
	# )

	# print(json.dumps(breeding.build_ancestry(a, b), indent=4))

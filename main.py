
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
		for genes in creature_data:
			creatures.append(Creature(genes))
	else:
		creatures = generate_starters()
	return creatures

def save_population(creatures):
	creature_data = []
	for creature in creatures:
		creature_data.append(creature.get_genotype())
	save_json(creature_data, POPULATION_FILE)

def main():
	creatures = get_population()
	breeding.breed(creatures[0], creatures[1])
	save_population(creatures)


	



	

if __name__ == '__main__':
	main()

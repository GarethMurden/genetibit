import random

def generate_variance(size=2):
    return random.choice(list(range(0-size, size)))

def scoring(city, critter, hint=False):
    attributes = critter.get_value()['attributes']
    scores = []
    if city == 'Ottawa':
        base_score = attributes[1] # antlers
        for x in range(3):
            scores.append(base + generate_variance())

    else:
        scores = [5, 5, 5]

    if hint:
        return any([s > 5 for s in scores])
    else:
        return scores


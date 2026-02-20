import random

def generate_variance(size=2):
    return random.choice(list(range(0-size, size)))

def scoring(city, critter, hint=False, max_score = 10):
    attributes = critter.get_value()['attributes']
    scores = []
    if city == 'Ottawa': # big antlers
        base_score = attributes[1]
        for x in range(3):
            scores.append(max([base_score + generate_variance(), 1]))

    elif city == 'Berlin': # long tails
        base_score = attributes[2]
        for x in range(3):
            scores.append(max([base_score + generate_variance(), 1]))

    elif city == 'Tokyo': # cute face
        base_score = attributes[0]
        for x in range(3):
            scores.append(max([base_score + generate_variance(), 1]))

    elif city == 'Brasilia': # big antlers + long tails
        base_score = int((attributes[1] + attributes[2]) / 2)
        for x in range(3):
            scores.append(max([base_score + generate_variance(), 1]))

    elif city == 'Pretoria': # small everything
        base_score = max_score - int(sum(attributes) / 3)
        for x in range(3):
            scores.append(max([base_score + generate_variance(), 1]))

    elif city == 'Canberra': # balanced attributes
        variation = max(attributes) - min(attributes)
        base_score = max_score - variation
        for x in range(3):
            scores.append(max([base_score + generate_variance(), 1]))

    else:
        scores = [int(max_score / 2), int(max_score / 2), int(max_score / 2)]

    if hint:
        return any([s > int(max_score / 2) for s in scores])
    else:
        return scores

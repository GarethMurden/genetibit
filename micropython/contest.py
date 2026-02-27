import random

def generate_variance(size=2):
    return random.choice(list(range(0-size, size)))

def scoring(city, critter, hint=False, max_score=5):
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

def target(city, max_score=5):
    '''Generate target scores used to generate a critter that will
    perform well in a given contest'''
    random_one = random.choice(range(max_score))
    random_two = random.choice(range(max_score))
    if city == 'Ottawa': # big antlers
        return [
            random_one,                           # face
            max_score - abs(generate_variance()), # antlers
            random_two                            # tails
        ]
    elif city == 'Berlin': # long tails
        return [
            random_one, 
            random_two,
            max_score - abs(generate_variance())
        ]
    elif city == 'Tokyo': # cute face
        return [
            max_score - abs(generate_variance()), 
            random_one, 
            random_two
        ]
    elif city == 'Brasilia': # big antlers + long tails
        return [
            max_score - abs(generate_variance()),
            max_score - abs(generate_variance()),
            random_one
        ]
    elif city == 'Pretoria': # small everything
        return [
            max_score - abs(generate_variance()),
            max_score - abs(generate_variance()),
            max_score - abs(generate_variance())
        ]
    elif city == 'Canberra': # balanced attributes
        return [
            int(max_score / 2) + generate_variance(),
            int(max_score / 2) + generate_variance(),
            int(max_score / 2) + generate_variance()
        ]
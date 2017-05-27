import numpy as np



def date_to_season(date):
    date_parts = date.split('-')
    month = int(date_parts[1])
    if 1 <= month <= 2 or month == 12:
        return 'winter'
    if 3 <= month <= 5:
        return 'spring'
    if 6 <= month <= 8:
        return 'summer'
    if 9 <= month <= 11:
        return 'fall'


def get_poem(theme):
    theme = theme.lower()
    with open('poems.txt') as poems_file:
        poems = poems_file.read()
    poems = poems.split('\n\n')
    theme_poems = []
    for poem in poems:
        if theme in poem.lower():
            theme_poems.append(poem)
    poem_index = np.random.randint(0, len(theme_poems))
    return theme_poems[poem_index]


# https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
def levenshtein(source, target):
    if len(source) < len(target):
        return levenshtein(target, source)

    # So now we have len(source) >= len(target).
    if len(target) == 0:
        return len(source)

    # We call tuple() to force strings to be used as sequences
    # ('c', 'a', 't', 's') - numpy uses them as values by default.
    source = np.array(tuple(source))
    target = np.array(tuple(target))

    # We use a dynamic programming algorithm, but with the
    # added optimization that we only need the last two rows
    # of the matrix.
    previous_row = np.arange(target.size + 1)
    for s in source:
        # Insertion (target grows longer than source):
        current_row = previous_row + 1

        # Substitution or matching:
        # Target and source items are aligned, and either
        # are different (cost of 1), or are the same (cost of 0).
        current_row[1:] = np.minimum(current_row[1:],
                                     np.add(previous_row[:-1], target != s))

        # Deletion (target grows shorter than source):
        current_row[1:] = np.minimum(current_row[1:], current_row[0:-1] + 1)

        previous_row = current_row

    return previous_row[-1]


def find_owm_name(in_name, names):
    owm_name = ''
    if in_name in names:
        owm_name = in_name
    else:
        for name in names:
            if levenshtein(in_name, name) < 2:
                owm_name = name
                break
    return owm_name

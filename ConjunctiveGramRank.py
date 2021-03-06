import os
import re
import math
import argparse

# Inverted Index Database
inv_index = {}

# M-Gram value
m_gram = 3

# Document count
doc_count = 0

# Infinity
infinity_p = (math.inf, math.inf)
infinity_n = (-math.inf, -math.inf)


# Clean up and Process string lines
def proc_str(c):
    result = ' '.join(c.split())
    result = result.strip()
    result = result.lower()
    result = re.sub(r'[. ]+', ' ', result)
    result = result.replace(' ', '_')

    padding = ''.join(['_' for _ in range(m_gram - 1)])

    return padding + result + padding


# Generate M-grams for each document
def gen_mgram(c):
    ptr = 0
    lst = []
    length = len(c)

    # Divide and insert same amount of words
    while ptr < length:
        if ptr == (length - (m_gram - 1)):
            break
        lst.append(c[ptr:ptr + m_gram])
        ptr += 1

    return lst


# Check M-grams in database
def check_pass(g):
    lst = []

    for t in g:
        if t in inv_index.keys():
            lst.append(t)

    return lst


# Generate inverted index database
def gen_database(d):
    # Inverted index Database
    database = {}

    # Iterate over documents
    for idx, data in enumerate(d):
        line = proc_str(data)
        grams = gen_mgram(line)

        for off, g in enumerate(grams):
            if g in database:
                # Update exiting entry
                database[g].add((idx, off))
            else:
                # First entry
                database[g] = {(idx, off)}

    for k in database.keys():
        database[k] = sorted(database[k])

    return database


# Remove missing grams
def filter_gram(c):
    lst = []
    for e in c:
        if e in inv_index.keys():
            lst.append(e)
    return lst


# Get first entry for the term
def first(t):
    return inv_index[t][0]


# Get last entry for the term
def last(t):
    return inv_index[t][-1]


# Get next entry for the term
def next(t, c):
    if t not in inv_index.keys() or c == infinity_p:
        return infinity_p

    if c == infinity_n or c[1] == infinity_n:
        return first(t)

    low = 0
    jump = 1
    high = low + jump
    d = inv_index[t]

    # Galloping Search
    if compare(d[-1], c) == -1 or compare(d[-1], c) == 0:
        return infinity_p

    if compare(d[0], c) == 1:
        return d[0]

    while high < len(d) - 1 and (compare(d[high], c) == -1 or compare(d[high], c) == 0):
        jump *= 2
        low = high
        high = low + jump

    if high > len(d):
        high = len(d) - 1

    pos = binary_search_next(t, c, low, high)
    return d[pos]


def binary_search_next(t, c, low, high):
    while high - low > 1:
        mid = (low + high) // 2
        if compare(inv_index[t][mid], c) == -1 or compare(inv_index[t][mid], c) == 0:
            low = mid
        else:
            high = mid
    return high


# Get prev entry for the term
def prev(t, c):
    if t not in inv_index.keys() or c == infinity_n:
        return infinity_n

    if c == infinity_p or c[1] == infinity_p:
        return last(t)

    low = 0
    jump = 1
    high = low + jump
    d = inv_index[t]

    # Galloping Search
    if compare(d[-1], c) == -1:
        return d[-1]

    if compare(d[0], c) == 0 or compare(d[0], c) == 1:
        return infinity_n

    while high < len(d) - 1 and compare(d[high], c) == -1:
        low = high
        jump *= 2
        high = low + jump

    if high > len(d):
        high = len(d) - 1

    pos = binary_search_prev(t, c, low, high)
    return d[pos]


def binary_search_prev(t, c, low, high):
    while high-low > 1:
        mid = (low+high)//2
        if compare(inv_index[t][mid], c) == -1:
            low = mid
        else:
            high = mid
    return low


# Find Next Phrase
def next_phrase(t, c):
    v = c
    n = len(t) - 1

    e = 0
    while e <= n:
        # temp = v
        v = next(t[e], v)
        # print(f"next({t[e]},{temp}) = {v}")
        e += 1

    if v == infinity_p and c[0] < doc_count - 1:
        return next_phrase(t, (c[0] + 1, 0))

    if v == infinity_p:
        return [infinity_p, infinity_p]

    u = v
    e = n - 1
    while e >= 0:
        # temp = u
        u = prev(t[e], u)
        # print(f"prev({t[e]},{temp}) = {u}")
        e += -1

    if v[0] == u[0] and v[1] - u[1] == n:
        return [u, v]
    else:
        return next_phrase(t, u)


# Find Prev Phrase
def prev_phrase(t, c):
    v = c
    n = len(t) - 1

    e = n
    while e >= 0:
        # temp = v
        v = prev(t[e], v)
        # print(f"prev({t[e]},{temp}) = {v}")
        e += -1

    if v == infinity_n and c[0] >= 1:
        return prev_phrase(t, (c[0] - 1, infinity_p))

    if v == infinity_n:
        return [infinity_n, infinity_n]

    u = v
    e = 1
    while e <= n:
        # temp = u
        u = next(t[e], u)
        # print(f"next({t[e]},{temp}) = {u}")
        e += 1

    if v[0] == u[0] and u[1] - v[1] == n:
        return [v, u]
    else:
        return prev_phrase(t, u)


# Return first entry after current
def next_doc(t, c):
    s = next_phrase(t, c)
    # print(f"next_phrase({t},{c}) = {s}")
    return s[-1]


# Return last entry before current
def prev_doc(t, c):
    s = prev_phrase(t, c)
    # print(f"prev_phrase({t},{c}) = {s}")
    return s[0]


# Doc Right
def doc_right(q, c):
    result = []

    for t in q:
        term = t
        if len(term) < m_gram:
            padding = ''.join(['_' for _ in range(m_gram - len(t))])
            term = term + padding
        grams = gen_mgram(term)
        grams = check_pass(grams)
        result.append(next_doc(grams, c))
        # print(f"next_doc({grams},{c}) = {result}")

    return result.pop()


# Doc Left
def doc_left(q, c):
    result = []

    for t in q:
        term = t
        if len(term) < m_gram:
            padding = ''.join(['_' for _ in range(m_gram - len(t))])
            term = term + padding
        grams = gen_mgram(term)
        grams = check_pass(grams)
        result.append(prev_doc(grams, c))
        # print(f"prev_doc({grams},{c}) = {result}")

    return result.pop()


# Compare 2 entries
def compare(u, v):
    if u[0] < v[0]:
        return -1
    elif u[0] > v[0]:
        return 1
    elif u[1] < v[1]:
        return -1
    elif u[1] > v[1]:
        return 1
    else:
        return 0


# Find next cover
def next_cover(q, c):
    v = doc_right(q, c)
    # print(f"docRight({q},{c}) = {v}")
    if v == infinity_p:
        return [infinity_p, infinity_p]
    u = doc_left(q, (v[0], v[1] + 1))
    # print(f"docLeft({q},{(v[0], v[1] + 1)}) = {u}")
    if u[0] == v[0]:
        return [u, v]
    else:
        return next_cover(q, u)


# Find ranking proximity score
def rank_proximity(q, k):
    # Starts from -infinity
    [u, v] = next_cover(q, infinity_n)
    # print(f"next_cover({q},{infinity_n}) = {[u, v]}")

    # Data
    result = []
    score = 0
    d = u[0]

    while u[0] < infinity_p[0]:
        if d < u[0]:
            result.append((d, score))
            score = 0
            d = u[0]
        score += 1 / (v[1] - u[1] + 1)
        [u, v] = next_cover(q, u)
        # print(f"next_cover({q},{u}) = {[u, v]}")

    if d < infinity_p[0]:
        result.append((d, score))

    # Sort by score descending
    result.sort(reverse=True, key=lambda x: x[1])

    # Return top k results
    return result[0:k]


# Test Result
def print_result(res):
    print(f'DocId Score')
    for r in res:
        print("%d %.2g" % (r[0]+1, r[1]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", help="get documents from folder", type=str)
    parser.add_argument("mgram", help="get m-gram count", type=int)
    parser.add_argument("nresults", help="get result count", type=int)
    parser.add_argument("query", help="get query", type=str, nargs='*')
    args = parser.parse_args()

    # Get all files from folder
    files = os.listdir(args.folder)
    files.sort()

    # Get all text data
    docs = []
    for file in files:
        # Read file to get corpus data
        with open(f'{args.folder}/{file}') as f:
            # Read all the text of file
            text = f.read()

            # Add to docs
            docs.append(text)

    # Inverted index m-gram
    m_gram = args.mgram
    doc_count = len(docs)
    inv_index = gen_database(docs)

    # print(inv_index)
    # print()

    ranks = rank_proximity(list(args.query), args.nresults)
    # print(f"rank_proximity({args.query},{args.nresults}) = {result}")
    print_result(ranks)

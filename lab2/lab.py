#!/usr/bin/env python3

import pickle
# NO ADDITIONAL IMPORTS ALLOWED!

# Note that part of your checkoff grade for lab 2 will be based on the
# style/clarity of your code.  As you are working through the lab, be on the
# lookout for things that would be made clearer by comments/docstrings, and for
# opportunities to rearrange aspects of your code to avoid repetition (for
# example, by introducing helper functions).

BACON_NUM = 4724

def getActor(data, id):
    for actor in data.keys():
        if data[actor] == id:
            return actor
    raise Exception('actor id doesn\'t exist')

def acted_together(data, actor_id_1, actor_id_2):
    actors = {actor_id_1, actor_id_2}
    return any({i, j} == actors for i, j, _ in data)

def neighbor_actors(data):
    """
    Returns a mapping which maps new actor id to actors they have acted with
    (mapping includes actor id)
    Old Code:
    actor_map = {}
    for i, j, _ in (data):
        # Check if an id exist in actor map using setdefault:
        # If i is in the dictionary, add its value. 
        # If not, insert i with a value of default and add default.
        actor_map.setdefault(i, set()).add(j)
        actor_map.setdefault(j, set()).add(i)
    return actor_map
    """
    actor_map = {}
    for film in data:
        # Set actor_id_1 and actor_id_2 as two actor ids in film
        actor_id_1, actor_id_2 = film[0],film[1]
        # Check if an id exist in actor map:
        # If actor_ids not in actor_map, set actor_map[actor_id_1] = set([actor_id_2])
        # Otherwise, add actor_id_2
        if actor_id_1 not in actor_map:
            actor_map[actor_id_1] = set([actor_id_2])
        else:
            actor_map[actor_id_1].add(actor_id_2)
        if actor_id_2 not in actor_map:
            actor_map[actor_id_2] = set([actor_id_1])
        else:
            actor_map[actor_id_2].add(actor_id_1)
    # iterate over actors in actor_map
    # convert it to list
    for actor in actor_map:
        actor_map[actor] = list(actor_map[actor])
    return actor_map

"""
def mapping(acted_with, cur, parents):
    Arguments:
        acted_with: a mapping from IDs to the people who have acted with
        cur = a set containing the IDS at N, the 'current' Bacon level
        parents = a dictionary mapping actor IDs to the actor that led to them
    Return set of people with Bacon number N+1
    new_act = set()
    # find all the neighbors of everyone at level N
    for act in cur:
        for n in acted_with[act]:
            # Check if the actor is in the parents dictionary
            # Skip any actor that is already in parents
            if n not in parents: 
                # add n to our set of people at level N+1
                # add n to parents
                parents[n] = act
                new_act.add(n)
    return new_act
"""

def actors_with_bacon_number(data, n):
    """
    Returns a Python set containing the ID numbers of all the actors with that Bacon number.
    acted_with = neighbor_actors(data)
    # Initialize parents and 1st level of Bacon Number
    parents = {BACON_NUM: None}
    cur = {BACON_NUM}
    for i in range(n):
        cur = mapping(acted_with, cur, parents)
    return set(cur)
    """
    actor_map = neighbor_actors(data)
    # If n == 0, return bacon number
    # if n == 1, return actor_map[bacon_number]
    if n == 0:
        return set([4724])
    elif n == 1:
        return set(actor_map[4724])
    # For n > 1
    queue = [(4724,0)]
    visited = set([])
    dicts = {0:visited}
    # while queue is not empty
    while queue:
        # pop the top one
        actor_id = queue.pop(0)
        # if the actor has not been visited
        if actor_id[0] not in visited:
            visited.add(actor_id[0])
            if actor_id[1] not in dicts:
                dicts[actor_id[1]] = set([actor_id[0]])
            else:
                dicts[actor_id[1]].add(actor_id[0])
            for i in actor_map[actor_id[0]]:
                queue.append((i, actor_id[1]+1))
    if n not in dicts:
        return set([])
    return dicts[n]

def bacon_path(data, actor_id):
    return actor_to_actor_path(data, BACON_NUM, actor_id)

def path_helper(child, parents):
    """
    Ruturn a list, the path from root to person
    """
    path = []
    while child is not None:
        path.append(child)
        child = parents[child]
    return path[::-1]  # the list we constructed is in reverse order, so flip it.

def actor_to_actor_path(data, actor_id_1, actor_id_2):
    return actor_path(data, actor_id_1, (lambda p: p == actor_id_2))
    """
    acted_with = neighbor_actors(data)
    parents = {actor_id_1: None}
    cur = {actor_id_1}
    # While loop stop condition:
    # 1. actor is in the current level
    # 2. no element at current level
    while actor_id_2 not in cur and cur:   
        cur = mapping(acted_with, cur, parents)
    # Return None if no path, else return the path
    if actor_id_2 in cur:
        return path_helper(actor_id_2, parents)
    else:
        return None
    """

def actor_name_id():
    with open('resources/names.pickle', 'rb') as f:
        return pickle.load(f)

def get_movie_name(data):
    """
    Return a mapping from actors to the movie ID number in which they acted together.
    """
    out = {}
    for i, j, n in data:
        out[frozenset({i, j})] = n # frozenset accepts iterable object as input parameter.
    return out

def get_movies():
    with open('resources/movies.pickle', 'rb') as f:
        return pickle.load(f)

def movie_path(data, actor_name_1, actor_name_2):
    """
    Return a list of movie names connecting two actors.
    """
    movie = get_movie_name(data)
    movie_names = {v: k for k ,v in get_movies().items()}
    # Determine the ID numbers of the given actors
    actor_id = actor_name_id()
    actor_id_1 = actor_id[actor_name_1]
    actor_id_2 = actor_id[actor_name_2]
    # Get actor path
    actor_path = actor_to_actor_path(data, actor_id_1, actor_id_2)
    movie_id_path = [movie[frozenset(i)] for i in zip(actor_path, actor_path[1:])]
    return [movie_names[i] for i in movie_id_path]

def actor_path(data, actor_id_1, goal_test_function):
    if goal_test_function(actor_id_1):
        return [actor_id_1]
    # neighbor_actors returns a mapping which maps new actor id to actors they have acted with
    acted_with = neighbor_actors(data)
    parents = {actor_id_1: None}
    cur = {actor_id_1}
    actor_id_2 = actor_id_1
    # while loop stopping condition:
    # 1. goal_test_function(actor_id_2) == False
    # 2. no element in cur
    while goal_test_function(actor_id_2) == False and cur:
        for n in cur:
            for i in acted_with[n]:
                if goal_test_function(i):
                    actor_id_2 = i
                    break
        cur = mapping(acted_with, cur, parents)
    # Return None if no path, else return the path
    if actor_id_2 in cur:
        return path_helper(actor_id_2, parents)
    else:
        return None

def actors_connecting_films(data, film1, film2):
    """
    Return the shortest possible list of actor ID numbers (in order) that connect those two films
    """
    movie = get_movie_name(data)
    movies = movie.items()
    start_actor_id = []
    end_actor_id = []
    # Get actors' id in these two films
    # append it into start_actor_id or end_actor_id
    for i, j, n in data:
        if n == film1:
            if i not in start_actor_id:
                start_actor_id.append(i)
            if j not in start_actor_id:
                start_actor_id.append(j)
        if n == film2:
            if i not in end_actor_id:
                end_actor_id.append(i)
            if j not in end_actor_id:
                end_actor_id.append(j)
    # Get actor paths
    shortest_path = actor_path(data, start_actor_id[0], lambda p: (p in end_actor_id))
    for i in range(1, len(start_actor_id)):
        actor_path_1 = actor_path(data, start_actor_id[i], lambda p: (p in end_actor_id))
        if(len(shortest_path) > len(actor_path_1)):
            shortest_path = actor_path_1
    return shortest_path

if __name__ == '__main__':
    with open('resources/small.pickle', 'rb') as f:
        smalldb = pickle.load(f)
        # print(smalldb)

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    with open('resources/large.pickle', 'rb') as f:
        Large = pickle.load(f)
        # print(Large)

    with open('resources/tiny.pickle', 'rb') as f:
        Tiny = pickle.load(f)
        print(Tiny)

    # print(get_movies())
    # print(actors_with_bacon_number(Large, 6))
    # actor_id1 = 3261
    # print(bacon_path(Large, actor_id1))
    # print(get_movie_name(Large))
    # print(get_movies().items())

#!/usr/bin/env python3

from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}

DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}

def build_auxiliary_structures(nodes_filename, ways_filename):
    """
    Create any auxiliary structures you are interested in, by reading the data
    from the given filenames (using read_osm_data)
    """
    Nodes = {}
    Edges = {}
    Dic = {}
    # Loop over each node in ways file
    # Look for the node in node file
    for ways in read_osm_data(ways_filename):
        # if it has an allowed highway types
        if 'highway' in ways['tags'] and ways['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
            for node in ways['nodes']:
                if not(node in Nodes):
                    Nodes[node] = (0.0)
                if not(node in Edges):
                    Edges[node] = []

            Speed = 0
            # Get speed for ways
            if 'maxspeed_mph' in ways['tags']:
                    Speed = ways['tags']['maxspeed_mph']
            else:
                Speed = DEFAULT_SPEED_LIMIT_MPH[ways['tags']['highway']]
            # Get Neighbor nodes for ways
            Neighbor = ways['nodes']

            # always append right neighbor
            for i in range(len(Neighbor) - 1):
                Edges[Neighbor[i]].append((Neighbor[i + 1], Speed))

            # if not oneway, append left neighbor to the node
            if not ('oneway' in ways['tags']) or ways['tags']['oneway'] != 'yes':
                Neighbor = Neighbor[::-1]
                for i in range(len(Neighbor) - 1):
                    Edges[Neighbor[i]].append((Neighbor[i + 1], Speed))

    # Loop over nodes_file
    for node in read_osm_data(nodes_filename):
        if node['id'] in Nodes:
            Nodes[node['id']] = (node['lat'], node['lon'])
            Dic[(node['lat'], node['lon'])] = node['id']
    return (Nodes, Edges, Dic)

def nearest(Dic, loc1):
    """
    Return the nearest node to loc1 in Dic
    """
    node = None
    loc = None
    # Loop over i in Dic.keys()
    for i in Dic.keys():
        if loc == None or great_circle_distance(loc, loc1) > great_circle_distance(i,loc1):
            # update node and loc
            node = Dic[i]
            loc = i
    return node

def find_short_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    Nodes, Edges, Dic = aux_structures
    nodes1 = nearest(Dic, loc1)
    nodes2 = nearest(Dic, loc2)
    agenda = [[[Nodes[nodes1]], 0, great_circle_distance(loc1, loc2)]]
    # agenda = [[[Nodes[nodes1]], 0]]
    empty = set()
    count = 0
    while agenda:
        # Remove the path with the lowest cost from the agenda.
        path = agenda.pop(0)
        count+=1
        # If this path's terminal vertex is in the expanded set，
        # ignore it completely and move on to the next path.
        if path[0][-1] in empty:
            continue
        # If this path's terminal vertex satisfies the goal condition
        # return that path. Otherwise, add its terminal vertex to the expanded set.
        if path[0][-1] == Nodes[nodes2]:
            print(count)
            return path[0]
        else:
            empty.add(path[0][-1])
        # For each of the children of that path's terminal vertex:
        id = Dic[path[0][-1]]
        for neighbor in Edges[id]:
            # If it is in the expanded set, skip it
            # Otherwise, add the associated path (and cost) to the agenda
            if Nodes[neighbor[0]] not in empty:
                p = []
                for i in path[0]:
                    p.append(i)
                p.append(Nodes[neighbor[0]])
                dis = great_circle_distance(Nodes[id], Nodes[neighbor[0]])
                h = great_circle_distance(Nodes[neighbor[0]], loc2)
                agenda.append([p, dis+path[1], h+dis+path[1]])
                # agenda.append([p, dis+path[1]])
        agenda.sort(key = lambda x: x[-1])
    return None

def find_fast_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    Nodes, Edges, Dic = aux_structures
    nodes1 = nearest(Dic, loc1)
    nodes2 = nearest(Dic, loc2)
    agenda = [[[Nodes[nodes1]], 0]]
    empty = set()
    while agenda:
        # Remove the path with the lowest cost from the agenda.
        # print([ [[Dic[d] for d in a[0]],a[1]] for a in agenda])
        path = agenda.pop(0)
        # If this path's terminal vertex is in the expanded set，
        # ignore it completely and move on to the next path.
        if path[0][-1] in empty:
            continue
        # If this path's terminal vertex satisfies the goal condition
        # return that path. Otherwise, add its terminal vertex to the expanded set.
        if path[0][-1] == Nodes[nodes2]:
            return path[0]
        else:
            empty.add(path[0][-1])
        # For each of the children of that path's terminal vertex:
        id = Dic[path[0][-1]]
        for neighbor in Edges[id]:
            # If it is in the expanded set, skip it
            # Otherwise, add the associated path (and cost) to the agenda
            if Nodes[neighbor[0]] not in empty:
                p = []
                for i in path[0]:
                    p.append(i)
                p.append(Nodes[neighbor[0]])
                speed = great_circle_distance(Nodes[id], Nodes[neighbor[0]])/get_highest_speed(Edges, id, neighbor[0])
                agenda.append([p, speed+path[1]])
        agenda.sort(key = lambda x: x[1])
    return None

def get_highest_speed(Edges, node, child):
    """
    Return the highest speed for node in Edges
    """
    # Initialize fastest
    fastest = 0
    # Loop over neighbor of node
    for neighbor in Edges[node]:
        # if child is find
        if neighbor[0] == child:
            # update fastest if neighbor[1] is the fastest
            if neighbor[1] > fastest:
                fastest = neighbor[1]
    return fastest

if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    
    # 2.1) Q1
    # count = 0
    # for node in read_osm_data('resources/cambridge.nodes'):
    #    for key, value in node['tags'].items():
    #        if key == 'name':
    #            count += 1
    # print(count)

    # 2.1) Q4,5
    # ways_count = 0
    # for way in read_osm_data('resources/cambridge.ways'):
    #    for key, value in way['tags'].items():
    #        if key == 'oneway' and value == 'yes':
    #            ways_count += 1
    #            print(ways_count)

    # 3.1.3）Q1
    # Location_1 = (42.363745, -71.100999)
    # Location_2 = (42.361283, -71.239677)
    # print(great_circle_distance(Location_1, Location_2))
    # 3.1.3）Q2
    # Loc1 = set()
    # Loc2 = set()
    # for node in read_osm_data('resources/midwest.nodes'):
    #    if (node['id'] == 233941454):
    #        Loc1.add(node['lat'])
    #        Loc1.add(node['lon'])
    #        print(Loc1)
    #    elif(node['id'] == 233947199):
    #        Loc2.add(node['lat'])
    #        Loc2.add(node['lon'])
    #        print(Loc2)
    #    if Loc1 != set() and Loc2 != set():
    #        break
    # print(great_circle_distance(Loc1, Loc2))
    # 3.1.3）Q3
    # ways = []
    # Loc = []
    # for node in read_osm_data('resources/midwest.ways'):
    #     if (node['id'] == 21705939):
    #         ways = node['nodes']
    # for n in read_osm_data('resources/midwest.nodes'):
    #     for nodes in ways:
    #         if n['id'] == nodes:
    #             loc = set()
    #             loc.add(n['lat'])
    #             loc.add(n['lon'])
    #             Loc.append(loc)
    # total_dis = 0
    # for i in range(1, len(ways)):
    #     total_dis += great_circle_distance(Loc[i-1], Loc[i])
    # print(total_dis）
    # print(build_auxiliary_structures('resources/mit.nodes', 'resources/mit.ways'))
    # for node in read_osm_data('resources/mit.nodes'):
        # print(node)
    # for ways in read_osm_data('resources/mit.ways'):
        # print(ways)
    # Nodes, Edges, Dic = build_auxiliary_structures('resources/midwest.nodes', 'resources/midwest.ways')
    # print(nearest(Dic, (41.4452463, -89.3161394)))
    map = build_auxiliary_structures('resources/cambridge.nodes', 'resources/cambridge.ways')
    # print(get_id_from_loc(map, (42.3582, -71.0931)))
    # print(find_short_path(map, (42.3575, -71.0927), (42.3582, -71.0931)))
    # Location_1 = (42.355, -71.1009)
    # Location_2 = (42.3575, -71.0952)
    # Location_3 = (42.3575, -71.0927)
    # print(great_circle_distance(Location_1, Location_2))
    # print(great_circle_distance(Location_1, Location_3))
    Location_1 = (42.3858, -71.0783)
    Location_2 = (42.5465, -71.1787)
    print(find_short_path(map, Location_1, Location_2))
    # pass
    
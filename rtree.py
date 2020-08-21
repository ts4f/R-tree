from sys import argv, exit
from math import ceil, floor, sqrt


class Entry:
    """
    An entry in the R-Tree (Leaf level)
    """

    def __init__(self, id: int, x_low: float, x_high: float, y_low: float, y_high: float):
        self.id = id
        self.x_low = x_low
        self.x_high = x_high
        self.y_high = y_high
        self.y_low = y_low

    @property
    def getPoints(self):
        return self.x_low, self.x_high, self.y_low, self.y_high

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '({self.id}, ({self.x_low}, {self.x_high}, {self.y_low}, {self.y_high}))'.format(self=self)


class Node:
    """
    A Node in RTree
        (init): -id: represents an identifier (based on position in Rtree)
                -idx: A list of Tuples [(ptr1, (MBR1)), ...]
        (@mbr): (Getter) Calculates and returns MBR by comparing the tuples in idx.
    """

    def __init__(self, id: int):
        self.id = id
        self.idx = []

    @property
    def mbr(self):
        min_xl = self.idx[0][1][0]
        max_xh = self.idx[0][1][1]
        min_yl = self.idx[0][1][2]
        max_yh = self.idx[0][1][3]
        for i in self.idx:
            min_xl = min(min_xl, i[1][0])
            max_xh = max(max_xh, i[1][1])
            min_yl = min(min_yl, i[1][2])
            max_yh = max(max_yh, i[1][3])

        return min_xl, max_xh, min_yl, max_yh

    @property
    def area(self):
        mbr = self.mbr
        return (mbr[1] - mbr[0]) * (mbr[3] - mbr[2])

    def add_idx(self, x):
        self.idx.append(x)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "%s, %s, %s" % (self.id, len(self.idx), self.idx)


class LeafNode:
    """
    A LeafNode in Rtree
        (init): -id: represents an identifier (based on position in Rtree.data)
                -entries: A list of Entry Objects
        (@mbr): (Getter) Calculates and returns MBR
    """

    def __init__(self, id: int, entries: list):
        self.id = id
        self.entries = entries

    @property
    def mbr(self):
        min_x_l = min(e.x_low for e in self.entries)
        max_x_h = max(e.x_high for e in self.entries)
        min_y_l = min(e.y_low for e in self.entries)
        max_y_h = max(e.y_high for e in self.entries)

        return min_x_l, max_x_h, min_y_l, max_y_h

    @property
    def area(self):
        mbr = self.mbr
        return (mbr[1] - mbr[0]) * (mbr[3] - mbr[2])

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "%s, %s, %s" % (self.id, len(self.entries), self.entries)


class RTree:
    """
     Rtree - STR implementation (BuildType: Level by Level)
        (init): - root: Root Node of Rtree
                - id: An incrementer (Sets ID's to nodes)
                - max_cap: Max. Node Capacity
                - childList: Child Indexes for Upper level creation
                - node_pool: Tree data
                - height: Tree Height (Amount of levels)
    """

    def __init__(self, max_cap: int):
        self.root = None
        self.__id = 0
        self.max_cap = max_cap
        self.childList = []
        self.node_pool = []

        self.leaf_counter = 0  # Test purposes
        self.height = 1

    # Inserts LeafNode Object intro Rtree
    def insert_leaf(self, entries):
        self.leaf_counter += 1
        # Create - Add Leafnode's id for upper level creation
        self.childList.append(self.getId)
        self.node_pool.append(LeafNode(self.getId, entries))
        # Increment ID
        self.__increment()

    # Inserts upper level Nodes (Recursively)
    def create_upper_levels(self):
        # Amount of upper nodes to be created
        x = ceil(len(self.childList) / self.max_cap)
        # Create Root
        if x == 1:
            self.root = Node(self.getId)
            for idx in self.childList:
                child = self.node_pool[idx]
                self.root.add_idx((child.id, child.mbr))

            self.node_pool.append(self.root)
            self.height += 1
        else:
            self.insert_nodes()
            self.height += 1
            self.create_upper_levels()

    # Creates and inserts Node objects
    def insert_nodes(self):
        buffer = []
        # Get child indexes and store them in slices (every slice can contain up to max_cap child indexes)
        child_indexes = [self.childList[i: i + self.max_cap] for i in range(0, len(self.childList), self.max_cap)]

        # Create a Node for every slice
        for chunk in child_indexes:
            buffer.append(self.getId)
            new_node = Node(self.getId)

            for idx in chunk:
                child = self.node_pool[idx]  # Get Child
                new_node.add_idx((child.id, child.mbr))  # Storing Child's id and MBR to Node

            self.node_pool.append(new_node)
            self.__increment()

        # The current upper level Nodes indexes are now stored in childList for the next upper level
        self.childList = buffer

    def __increment(self):
        self.__id += 1

    @property
    def getId(self):
        return self.__id

    # Print Tree ( Root to Leaf)
    def printTree(self):
        print('-' * 30 + "Printing Tree" + '-' * 27)
        print("Tree Height:", self.height)
        for i in self.node_pool[::-1]:
            print("Node-id:", i)
        print('-' * 70 + '\n')

    # Write Tree to File
    def write_to_file(self, filename):
        with open(filename, 'w+') as f:
            f.write(str(self.root.id) + '\n')
            f.write(str(self.height) + '\n')
            for i in self.node_pool[::-1]:
                f.write(str(i) + "\n")

    # Calculates and prints Statistics (Tree Height, Amount of nodes per level, Avg. Mbr per lvl)
    def stats(self):
        print('-' * 30 + 'Statistics' + '-' * 30)
        print("Tree Height (#levels):", self.height)
        print("#Nodes in Rtree:", len(self.node_pool))
        print()

        i = 1
        lower_bound = 0
        upper_bound = self.leaf_counter
        while lower_bound < len(self.node_pool):
            # Getting nodes per level
            nodes = self.node_pool[lower_bound:upper_bound]

            # Avg mbr area
            area = sum(node.area for node in nodes)
            avg_area = area / len(nodes)

            # Calculating avg. MBR
            nodes = tuple(node.mbr for node in nodes)
            avg = tuple(map(lambda y: sum(y) / float(len(y)), zip(*nodes)))
            print('Level {:1d}:\t#Nodes: {:4d},\tAverage MBR area: {},\t Average MBR: {}'.format(i, len(nodes), avg_area, avg))
            i += 1
            lower_bound = upper_bound
            upper_bound += ceil(len(nodes) / self.max_cap)
        print('-' * 70 + '\n')

    # Range Search Algorithm (recursive) , predicate -> function (inside|contains|intersect)
    def range_search(self, query, predicate, n, hits):
        # Count visited Nodes
        accesses = 1

        # Current node is a leaf
        if isinstance(n, LeafNode):
            # Check for each Entry in LeafNode if predicate function is True
            for e in n.entries:
                if predicate(query, e.getPoints):
                    hits.append(e.id)  # We could add the whole Entry
        else:  # It's a Node
            # Check intersection for every (ptr, MBR) and visit it if so
            for e in n.idx:
                ptr = e[0]
                mbr = e[1]
                if intersects(query, mbr):
                    visit_node = self.node_pool[ptr]
                    accesses += self.range_search(query, predicate, visit_node, hits)
        return accesses


# Check if  query is inside r2
def contains(query, r2):
    return inside(r2, query)


# Check if r2 is inside query
def inside(query, r2):
    return query[0] < r2[0] <= r2[1] < query[1] and query[2] < r2[2] <= r2[3] < query[3]


# Check for intersection (adjacent/contains/inside/equals)
def intersects(query, other):
    return not (query[1] < other[0] or query[0] > other[1] or query[3] < other[2] or query[2] > other[3])


# STR calculations
def calc(size, block_size):
    n = floor(block_size / 36)  # Maximum Node capacity

    leaf_level_pages = ceil(size / n)  # Number of leaves
    s = ceil(sqrt(leaf_level_pages))  # vertical slices
    print('-' * 26 + 'STR calculations' + '-' * 28)
    print("Max entries per node:", n)
    print("#LeafNodes:", leaf_level_pages)
    print("#Slices:", s)
    print('-' * 70 + '\n')

    return leaf_level_pages, n, s


def main():
    # Maximum byte capacity of a node
    block_size = 1024
    # Temporary list to store file data
    data = []

    if len(argv) != 2:
        print('Error: excepted 2 arguments found', len(argv))
        exit()

    # Create an Entry object for every line in file and append it to data
    with open(argv[1]) as f:
        for line in f:
            row = line.strip('\n').split('\t')
            label, x_low, x_high, y_low, y_high = [i for i in row]
            data.append(Entry(int(label), float(x_low), float(x_high), float(y_low), float(y_high)))

    # Sort data by x_low
    data.sort(key=lambda entry: entry.x_low)

    # STR calculation
    leaves, max_cap, s = calc(len(data), block_size)

    # Partition sorted Entries into S slices, every slice can contain up to S * max_cap Entry objects
    data = [data[x:x + (s * max_cap)] for x in range(0, len(data), s * max_cap)]

    # Sorting every slice by y_low
    for sl in data:
        sl.sort(key=lambda entry: entry.y_low)

    # Creating an Rtree object
    tree = RTree(max_cap)

    # Bulk Load - Build Tree Level by Level
    for sublist in data:
        for i in range(0, len(sublist), max_cap):
            tree.insert_leaf(sublist[i: i + max_cap])
    tree.create_upper_levels()  # No need to call if there is only one leaf

    # Our data is now stored in the Rtree no need to keep it
    del data

    # UNCOMMENT THIS LINE TO PRINT TREE (BFS) TO TERMINAL
    # tree.printTree()

    # Print statistics of Rtree
    tree.stats()

    # Writes Tree data to file
    tree.write_to_file('rtree.txt')

    predicates = [intersects, inside, contains]
    with open('query_rectangles.txt', 'r') as f:
        for line in f:
            query = line.strip('\n').split('\t')
            query_id = query[0]
            query_rect = tuple(float(i) for i in query[1:])

            print('Query-id:', query_id)
            for func in predicates:
                hits = []
                accesses = tree.range_search(query_rect, func, tree.root, hits)
                print("\t\tPredicate: {:10s}, Visited: {:3d}, Hits: {}".format(func.__name__, accesses, len(hits)))


if __name__ == '__main__':
    main()

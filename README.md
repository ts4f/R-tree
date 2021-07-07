# R-tree
R-trees are tree data structures used for spatial access methods, i.e., for indexing multi-dimensional information such as geographical coordinates, rectangles or polygons.

This program implements the sort-tile-recursive (STR) technique that reads all rectangles from a file in order to construct an R-tree (in memory) for them.
The STR technique: *Scott T. Leutenegger, J. M. Edgington, and Mario A. López. 1997. STR: A Simple and Efficient Algorithm for R-Tree Packing. In ICDE. 497–506.*

![R-tree image](https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/R-tree.svg/400px-R-tree.svg.png)

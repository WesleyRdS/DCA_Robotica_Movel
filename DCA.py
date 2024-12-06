import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

fig = plt.figure(figsize=(8,8), dpi=100)
ax = fig.add_subplot(111, aspect='equal')

#invertendo valores das cores(Branco - 0 / Preto - 1)
img = 1-mpimg.imread('base.png')

threshold = 0.5
img[img > threshold] = 1
img[img <= threshold] = 0

ax.imshow(img, cmap='Greys', origin='upper')

#dimensão do mapa informada em CM
map_dims = np.array([18,27])
sy, sx = img.shape[:2] / map_dims

#tamanho da celula do grid em CM
cell_size = 1

rows, cols = (map_dims * cell_size).astype(int)
grid = np.zeros((rows, cols))

#Preenche o grid
#Cada celula recebe o somatorio dos valores do pixel
for r in range(rows):
  for c in range(cols):
    xi = int(c*cell_size*sx)
    xf = int(xi + cell_size*sx)

    yi = int(r*cell_size*sy)
    yf = int(yi + cell_size*sy)

    grid[r,c] =  np.sum(img[yi:yf,xi:xf])

#binarizando as celulas como ocupadas(1) e não ocupadas[0]
grid[grid > threshold] = 1
grid[grid <= threshold] = 0

fig = plt.figure(figsize=(8,8), dpi=100)
ax = fig.add_subplot(111, aspect='equal')

obj = ax.imshow(img, cmap='Greys', extent=(0, map_dims[1], 0, map_dims[0]), origin='upper')
obj = ax.imshow(grid, cmap='Reds', extent=(0, map_dims[1], 0, map_dims[0]), alpha=.7)

ax.grid(which='major', axis='both', linestyle='-', color='r', linewidth=1)
ax.set_xticks(np.arange(0, map_dims[1]+1, cell_size))
ax.set_yticks(np.arange(0, map_dims[0]+1, cell_size))

#criando grafo para o grid

#criando vertice em todas as celulas
G = nx.grid_2d_graph(rows, cols)

#removendo celula marcada como obstaculo
for r in range(rows):
  for c in range(cols):
    if grid[r,c] == 1:
      G.remove_node((r,c))

fig = plt.figure(figsize=(8,8), dpi=100)
ax = fig.add_subplot(111, aspect='equal')

obj = ax.imshow(grid, cmap='Greys', extent=(0, map_dims[1], 0, map_dims[0]))

ax.grid(which='major', axis='both', linestyle='-', color='r', linewidth=1)
ax.set_xticks(np.arange(0, map_dims[1]+1, cell_size))
ax.set_yticks(np.arange(0, map_dims[0]+1, cell_size))

#os vertices serão plotados no centro da celula
pos = {node:(node[1]*cell_size+cell_size/2, map_dims[0] - node[0]* cell_size-cell_size/2) for node in G.nodes()}
nx.draw(G, pos, font_size=6, with_labels=True, node_size=50, node_color='g', ax=ax)

from mmap import MAP_DENYWRITE
#Atenção ao sistema de coordenadas -- relação indice do grid e posição no mapa

start_node = (1,1)
end_node = (1,10)

fig = plt.figure(figsize=(8,8), dpi=100)
ax = fig.add_subplot(111, aspect='equal')

obj = ax.imshow(grid, cmap='Greys', extent=(0, map_dims[1], 0, map_dims[0]))

path = nx.shortest_path(G, source=start_node, target=end_node)
nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='b', node_size=100)
plt.show()

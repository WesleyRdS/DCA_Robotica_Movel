import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import subprocess  # Para chamar outros scripts
import json

fig = plt.figure(figsize=(8, 8), dpi=100)
ax = fig.add_subplot(111, aspect='equal')

# Carrega a imagem editada
img = 1 - mpimg.imread('edited_image.png')

threshold = 0.5
img[img > threshold] = 1
img[img <= threshold] = 0

ax.imshow(img, cmap='Greys', origin='upper')

map_dims = np.array([18, 27])
sy, sx = img.shape[:2] / map_dims
cell_size = 1

rows, cols = (map_dims * cell_size).astype(int)
grid = np.zeros((rows, cols))

# Preenchendo o grid
for r in range(rows):
    for c in range(cols):
        xi = int(c * cell_size * sx)
        xf = int(xi + cell_size * sx)
        yi = int(r * cell_size * sy)
        yf = int(yi + cell_size * sy)
        grid[r, c] = np.sum(img[yi:yf, xi:xf])

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
for r in range(rows):
    for c in range(cols):
        if grid[r, c] == 1:
            G.remove_node((r, c))

fig = plt.figure(figsize=(8, 8), dpi=100)
ax = fig.add_subplot(111, aspect='equal')

obj = ax.imshow(grid, cmap='Greys', extent=(0, map_dims[1], 0, map_dims[0]))

ax.grid(which='major', axis='both', linestyle='-', color='r', linewidth=1)
ax.set_xticks(np.arange(0, map_dims[1] + 1, cell_size))
ax.set_yticks(np.arange(0, map_dims[0] + 1, cell_size))

pos = {node: (node[1] * cell_size + cell_size / 2, map_dims[0] - node[0] * cell_size - cell_size / 2) for node in G.nodes()}
nx.draw(G, pos, font_size=6, with_labels=True, node_size=50, node_color='g', ax=ax)

# Solicita os pontos inicial e final
start_node = tuple(map(int, input("Digite o nó inicial (linha, coluna): ").strip("()").split(",")))
end_node = tuple(map(int, input("Digite o nó final (linha, coluna): ").strip("()").split(",")))

path = nx.shortest_path(G, source=start_node, target=end_node)
print(f"Caminho encontrado: {path}")

# Salva o caminho em um arquivo JSON
with open("path_data.json", "w") as path_file:
    json.dump({"path": path}, path_file)

print("Caminho salvo em 'path_data.json'.")

nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='b', node_size=100)
plt.show()

subprocess.run(["python3", "test_interface_draw.py"]) 

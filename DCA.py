import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import subprocess  # Executa scripts externos
import json

# Configurações iniciais da figura
fig = plt.figure(figsize=(8, 8), dpi=100)
ax = fig.add_subplot(111, aspect='equal')

# Carrega e binariza a imagem
img = 1 - mpimg.imread('edited_image.png')
threshold = 0.5
img[img > threshold] = 1
img[img <= threshold] = 0
ax.imshow(img, cmap='Greys', origin='upper')

# Define o grid baseado nas dimensões da imagem
map_dims = np.array([18, 27])
sy, sx = img.shape[:2] / map_dims
cell_size = 1
rows, cols = (map_dims * cell_size).astype(int)
grid = np.zeros((rows, cols))

# Preenchendo o grid
for r in range(rows):
    for c in range(cols):
        xi, xf = int(c * cell_size * sx), int((c + 1) * cell_size * sx)
        yi, yf = int(r * cell_size * sy), int((r + 1) * cell_size * sy)
        grid[r, c] = np.sum(img[yi:yf, xi:xf])

grid[grid > threshold] = 1
grid[grid <= threshold] = 0

# Plota o grid sobre a imagem
fig = plt.figure(figsize=(8, 8), dpi=100)
ax = fig.add_subplot(111, aspect='equal')
ax.imshow(img, cmap='Greys', extent=(0, map_dims[1], 0, map_dims[0]), origin='upper')
ax.imshow(grid, cmap='Reds', extent=(0, map_dims[1], 0, map_dims[0]), alpha=0.7)
ax.grid(which='major', linestyle='-', color='r', linewidth=1)
ax.set_xticks(np.arange(0, map_dims[1] + 1, cell_size))
ax.set_yticks(np.arange(0, map_dims[0] + 1, cell_size))

# Criação do grafo do grid
G = nx.grid_2d_graph(rows, cols)
for r in range(rows):
    for c in range(cols):
        if grid[r, c] == 1:  # Remove nós bloqueados
            G.remove_node((r, c))

# Plota o grafo
fig = plt.figure(figsize=(8, 8), dpi=100)
ax = fig.add_subplot(111, aspect='equal')
ax.imshow(grid, cmap='Greys', extent=(0, map_dims[1], 0, map_dims[0]))
ax.grid(which='major', linestyle='-', color='r', linewidth=1)
ax.set_xticks(np.arange(0, map_dims[1] + 1, cell_size))
ax.set_yticks(np.arange(0, map_dims[0] + 1, cell_size))

# Define posições dos nós no grafo
pos = {node: (node[1] * cell_size + cell_size / 2, map_dims[0] - node[0] * cell_size - cell_size / 2) for node in G.nodes()}
nx.draw(G, pos, with_labels=True, node_size=50, node_color='g', ax=ax)

# Entrada do usuário para início e fim do caminho
start_node = tuple(map(int, input("Digite o nó inicial (linha, coluna): ").strip("()").split(",")))
end_node = tuple(map(int, input("Digite o nó final (linha, coluna): ").strip("()").split(",")))
angle = input("Digite o ângulo: ")

# Calcula e salva o caminho mais curto
path = nx.shortest_path(G, source=start_node, target=end_node)
print(f"Caminho encontrado: {path}")
path_as_strings = [str(coord) for coord in path]
with open("path_data.json", "w") as path_file:
    json.dump({"path": path_as_strings, "angle": angle}, path_file)
print("Caminho salvo em 'path_data.json'.")

# Plota o caminho no grafo
nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='b', node_size=100)
plt.show()

# Executa outro script
subprocess.run(["python3", "test_interface_draw.py"])

import cv2
import numpy as np
import nxt.locator
import time
import threading
import json  # Para carregar o path salvo

# Configuração inicial da malha
map_dims = np.array([18, 27])  # Dimensão do mapa em partes (18x27)
robot_radius = 0.5             # Tamanho do robô em células
robot_position = (1, 1)        # Posição inicial do robô na malha (linha, coluna)
robot_path = []                # Histórico do caminho percorrido pelo robô

# Carrega a imagem do mapa
image_path = "edited_image.png"
map_image = cv2.imread(image_path)

if map_image is None:
    raise FileNotFoundError("A imagem do mapa não foi encontrada. Verifique o caminho.")

# Calcula o tamanho da célula em pixels
sy, sx = map_image.shape[:2] / map_dims

# Lê o caminho gerado no DCA.py
try:
    with open("path_data.json", "r") as path_file:
        path_data = json.load(path_file)
        path = path_data.get("path", [])
        angle = path_data.get("angle", "")
        print(f"Caminho carregado: {path}")
        print(f"Ângulo carregado: {angle}")
except FileNotFoundError:
    print("Arquivo 'path_data.json' não encontrado. Certifique-se de que o DCA.py foi executado.")
    path = []
    angle = ""

# Função para desenhar o rastro do robô no mapa (passado e futuro)
def draw_robot_path(map_img, robot_path, full_path, sx, sy):
    # Desenhar o caminho já percorrido (azul)
    for i in range(1, len(robot_path)):
        prev_pos = robot_path[i - 1]
        curr_pos = robot_path[i]

        # Converte strings para tuplas, se necessário
        if isinstance(prev_pos, str):
            prev_pos = eval(prev_pos)
        if isinstance(curr_pos, str):
            curr_pos = eval(curr_pos)

        prev_pixel = (int((prev_pos[1] + 0.5) * sx), int((prev_pos[0] + 0.5) * sy))
        curr_pixel = (int((curr_pos[1] + 0.5) * sx), int((curr_pos[0] + 0.5) * sy))

        cv2.line(map_img, prev_pixel, curr_pixel, (255, 0, 0), 2)  # Azul para o rastro já percorrido

    # Desenhar o caminho futuro (cinza claro)
    future_path = full_path[len(robot_path):]  # Caminho a ser percorrido
    for i in range(1, len(future_path)):
        prev_pos = future_path[i - 1]
        curr_pos = future_path[i]

        # Converte strings para tuplas, se necessário
        if isinstance(prev_pos, str):
            prev_pos = eval(prev_pos)
        if isinstance(curr_pos, str):
            curr_pos = eval(curr_pos)

        prev_pixel = (int((prev_pos[1] + 0.5) * sx), int((prev_pos[0] + 0.5) * sy))
        curr_pixel = (int((curr_pos[1] + 0.5) * sx), int((curr_pos[0] + 0.5) * sy))

        cv2.line(map_img, prev_pixel, curr_pixel, (200, 200, 200), 1)  # Cinza claro para o futuro

# Função para desenhar a posição do robô no mapa
def draw_robot_on_map(map_img, position, radius, map_dims, sx, sy):
    map_copy = map_img.copy()
    row, col = position

    # Calcula o centro da célula em pixels
    x_center = int((col + 0.5) * sx)
    y_center = int((row + 0.5) * sy)

    # Calcula o raio do robô em pixels (escala pelo tamanho da célula)
    pixel_radius = int(radius * min(sx, sy))

    # Desenha o robô como um círculo na posição calculada
    cv2.circle(map_copy, (x_center, y_center), pixel_radius, (0, 0, 255), -1)
    return map_copy

# Atualiza a posição do robô com as coordenadas recebidas
def update_robot_position(new_position, map_dims):
    global robot_position, robot_path
    try:
        # Verifica se a posição está no formato correto e dentro dos limites
        row, col = new_position
        if 0 <= row < map_dims[0] and 0 <= col < map_dims[1]:
            robot_position = (row, col)
            robot_path.append(robot_position)  # Adiciona ao histórico
            print(f"Posição do robô atualizada para: {robot_position}")
        else:
            print(f"Posição fora dos limites: {new_position}")
    except Exception as e:
        print(f"Erro ao atualizar posição: {e}")

# Função para receber coordenadas via Bluetooth em uma thread separada
def receive_coordinates_via_bluetooth():
    global robot_position
    bob = nxt.locator.find(host="00:16:53:09:72:DE")  # Endereço do robô
    aux1 = ""
    
    bob.message_write(1, "init".encode("utf-8"))
    for coord in path:
        bob.message_write(1, str(coord).encode("utf-8"))
    bob.message_write(1, "end".encode("utf-8"))
    if angle:
        bob.message_write(1, angle.encode("utf-8"))
    else:
        print("Ângulo não definido. Verifique o arquivo 'path_data.json'.")

    while running:
        try:
            aux = bob.message_read(5, 2, False)  # Recebe mensagem via Bluetooth
            if aux != aux1:
                aux1 = aux
                # Extrai a tupla de coordenadas do formato recebido
                coord_str = aux[1].decode("utf-8").strip("\x00")
                if coord_str:
                    new_position = eval(coord_str)  # Ex: (1, 1)
                    update_robot_position(new_position, map_dims)
            # time.sleep(0.25)
        except Exception as e:
            print(f"Erro na comunicação Bluetooth: {e}")
            break

# Configuração da janela do OpenCV
cv2.namedWindow("Mapa com Robô")
running = True

# Inicia a thread para receber as coordenadas via Bluetooth
bluetooth_thread = threading.Thread(target=receive_coordinates_via_bluetooth)
bluetooth_thread.daemon = True
bluetooth_thread.start()

# Loop principal da interface
while running:
    # Cria uma cópia do mapa para desenhar
    map_with_path = map_image.copy()

    # Desenha o rastro do robô no mapa (passado e futuro)
    draw_robot_path(map_with_path, robot_path, path, sx, sy)

    # Desenha o robô no mapa
    current_map = draw_robot_on_map(map_with_path, robot_position, robot_radius, map_dims, sx, sy)

    # Exibe o mapa na janela
    cv2.imshow("Mapa com Robô", current_map)

    # Captura a entrada do teclado
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'): 
        cv2.imwrite("robot_map.png", current_map)
        print("Mapa salvo como 'robot_map.png'")

    elif key == 27: 
        running = False

# Finaliza a janela e encerra o programa
cv2.destroyAllWindows()

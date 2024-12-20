import cv2  # Biblioteca de manipulação de imagens
import numpy as np  # Operações matemáticas
import subprocess  # Para executar scripts externos

# Carrega a imagem
image_path = "base.png"
image = cv2.imread(image_path)

# Callback para desenhar formas na imagem
def draw_shapes(event, x, y, flags, param):
    global drawing, mode, start_point

    if event == cv2.EVENT_LBUTTONDOWN:  # Início do desenho
        drawing = True
        start_point = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:  # Fim do desenho
        drawing = False
        end_point = (x, y)
        if mode == 'rectangle':
            cv2.rectangle(image, start_point, end_point, (0, 0, 0), -1)
        elif mode == 'circle':
            radius = int(((start_point[0] - x)**2 + (start_point[1] - y)**2)**0.5)
            cv2.circle(image, start_point, radius, (0, 0, 0), -1)
        elif mode == 'line':
            cv2.line(image, start_point, end_point, (0, 0, 0), 5)

# Variáveis de controle
drawing = False
mode = 'rectangle'
start_point = (0, 0)

# Configura a janela e o callback do mouse
cv2.namedWindow("Edit Image")
cv2.setMouseCallback("Edit Image", draw_shapes)

# Loop principal
while True:
    cv2.imshow("Edit Image", image)
    key = cv2.waitKey(1) & 0xFF

    # Alterna modos de desenho
    if key == ord('r'):  
        mode = 'rectangle'
    elif key == ord('c'):  
        mode = 'circle'
    elif key == ord('l'):  
        mode = 'line'
    elif key == ord('s'):  # Salva a imagem e executa o script externo
        cv2.imwrite("edited_image.png", image)
        print("Imagem salva como 'edited_image.png'")
        subprocess.run(["python3", "DCA.py"])
        break
    elif key == 27:  # Encerra o programa
        break

cv2.destroyAllWindows()

import cv2
import numpy as np
import subprocess  # Para chamar outros scripts

image_path = "base.png" 
image = cv2.imread(image_path)

def draw_shapes(event, x, y, flags, param):
    global drawing, mode, start_point

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)
    
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)
        if mode == 'rectangle':
            cv2.rectangle(image, start_point, end_point, (0, 0, 0), -1)  
        elif mode == 'circle':
            radius = int(((start_point[0] - x)**2 + (start_point[1] - y)**2)**0.5)
            cv2.circle(image, start_point, radius, (0, 0, 0), -1)
        elif mode == 'line':
            cv2.line(image, start_point, end_point, (0, 0, 0), 5)

drawing = False
mode = 'rectangle' 
start_point = (0, 0)

cv2.namedWindow("Edit Image")
cv2.setMouseCallback("Edit Image", draw_shapes)

while True:
    cv2.imshow("Edit Image", image)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('r'):  
        mode = 'rectangle'
    elif key == ord('c'):  
        mode = 'circle'
    elif key == ord('l'):  
        mode = 'line'
    elif key == ord('s'):  
        cv2.imwrite("edited_image.png", image)
        print("Imagem salva como 'edited_image.png'")
        subprocess.run(["python3", "DCA.py"])  # Chama o script DCA.py
        break
    elif key == 27:  
        break

cv2.destroyAllWindows()

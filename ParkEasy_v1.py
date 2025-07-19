import cv2
import numpy as np

cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("No se pudo acceder a la cámara.")
    exit()

areas = []
base_x, base_y, w, h = 100, 100, 120, 200
espacio = 10
for i in range(4):
    x = base_x + i * (w + espacio)
    areas.append({
        'x': x,
        'y': base_y,
        'w': w,
        'h': h,
        'referencia': None,
        'estado_anterior': False
    })


umbral_diferencia = 30
porcentaje_ocupado = 0.6
area_total = w * h


def Area(img, x, y, w, h, color=(0, 0, 255), grosor=1, longitud_punto=5, espacio=5):
    for i in range(x, x + w, longitud_punto + espacio):
        cv2.line(img, (i, y), (min(i + longitud_punto, x + w), y), color, grosor)
        cv2.line(img, (i, y + h), (min(i + longitud_punto, x + w), y + h), color, grosor)
    for i in range(y, y + h, longitud_punto + espacio):
        cv2.line(img, (x, i), (x, min(i + longitud_punto, y + h)), color, grosor)
        cv2.line(img, (x + w, i), (x + w, min(i + longitud_punto, y + h)), color, grosor)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    for idx, area in enumerate(areas):
        x, y, w, h = area['x'], area['y'], area['w'], area['h']
        roi = frame[y:y+h, x:x+w]

        if area['referencia'] is None:
            area['referencia'] = roi.copy()
            continue


        diff = cv2.absdiff(roi, area['referencia'])
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(diff_gray, umbral_diferencia, 255, cv2.THRESH_BINARY)

        pixeles_diferentes = cv2.countNonZero(mask)
        porcentaje_cambio = pixeles_diferentes / area_total
        ocupado = porcentaje_cambio >= porcentaje_ocupado
        
        area['estado_anterior'] = ocupado
        color_rect = (0, 255, 255) if ocupado else (0, 0, 255)
        Area(frame, x, y, w, h, color=color_rect)

        texto = f"Area {idx+1}: {'OCUPADO' if ocupado else 'LIBRE'}"
        cv2.putText(frame, texto, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_rect, 2)
    
    cv2.namedWindow("ParkEasy", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("ParkEasy", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("ParkEasy", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

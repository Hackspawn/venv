import cv2
import numpy as np
import time
from rpi_ws281x import PixelStrip, ws

# ========= Configuración matriz =========
WIDTH  = 42            # LEDs en X (ancho)
HEIGHT = 56            # LEDs en Y (alto)
LED_COUNT = WIDTH * HEIGHT

# Cableado/recorrido:
# - "rows_snake": tiras recorren filas en zig-zag (lo más común cuando pegas tiras horizontalmente)
# - "cols_snake": tiras recorren columnas en zig-zag (56 tiras de 42 LEDs cada una, apiladas verticalmente)
LAYOUT = "rows_snake"   # cambia a "cols_snake" si tu cableado es por columnas

ORIGIN_TOP_LEFT = True  # pon False si tu (0,0) está abajo-izquierda

# ========= Config rpi_ws281x =========
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 10       # sube con cuidado
LED_INVERT     = False
LED_CHANNEL    = 0

# Usa strip_type explícito para evitar problemas de orden de color
STRIP_TYPE = ws.WS2811_STRIP_RGB  # si ves colores “raros”, prueba ws.WS2811_STRIP_GRB

strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
    LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, STRIP_TYPE
)
strip.begin()

# ========= Utilidades de mapeo =========
def xy_to_index_rows_snake(x, y):
    """Recorrido por filas en zig-zag."""
    row = y if ORIGIN_TOP_LEFT else (HEIGHT - 1 - y)
    if row % 2 == 0:
        return row * WIDTH + x
    else:
        return row * WIDTH + (WIDTH - 1 - x)

def xy_to_index_cols_snake(x, y):
    """Recorrido por columnas en zig-zag (útil si tienes 56 tiras verticales de 42 LEDs)."""
    col = x
    row = y if ORIGIN_TOP_LEFT else (HEIGHT - 1 - y)
    if col % 2 == 0:
        return col * HEIGHT + row
    else:
        return col * HEIGHT + (HEIGHT - 1 - row)

if LAYOUT == "rows_snake":
    xy_to_index = xy_to_index_rows_snake
elif LAYOUT == "cols_snake":
    xy_to_index = xy_to_index_cols_snake
else:
    raise ValueError("LAYOUT debe ser 'rows_snake' o 'cols_snake'.")

def clear_strip():
    for i in range(LED_COUNT):
        strip.setPixelColorRGB(i, 0, 0, 0)
    strip.show()

# ========= Cámara =========
cap = cv2.VideoCapture(0)
# Opcional: fija resolución nativa para reducir latencia
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("No hay frame de la cámara.")
            break

        # Opcional: espejar horizontalmente para “modo espejo”
        # frame = cv2.flip(frame, 1)

        # Redimensiona a la grilla exacta de la matriz
        small = cv2.resize(frame, (WIDTH, HEIGHT), interpolation=cv2.INTER_LINEAR)
        # BGR -> RGB
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        # Escribe a la tira con el mapeo correcto
        # Evitamos bucles internos complejos: solo un for con índices ya resueltos.
        for y in range(HEIGHT):
            for x in range(WIDTH):
                r, g, b = rgb[y, x]
                i = xy_to_index(x, y)
                strip.setPixelColorRGB(i, int(r), int(g), int(b))

        strip.show()

        # Salir con ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break

except KeyboardInterrupt:
    pass
finally:
    cap.release()
    clear_strip()

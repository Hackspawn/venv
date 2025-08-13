import cv2
import numpy as np
import time
import sys

# ======== CONFIG MATRIZ ========
WIDTH  = 42              # LEDs en X (ancho)
HEIGHT = 40              # LEDs en Y (alto)
LED_COUNT = WIDTH * HEIGHT

LAYOUT = "rows_snake"    # "rows_snake" o "cols_snake"
ORIGIN_TOP_LEFT = True   # True: (0,0) arriba-izquierda; False: abajo-izquierda

# ======== SIMULACIÓN ========
SCALE = 12
MIRROR = False
SHOW_GRID = True
SHOW_FPS = True

# ======== LEDS (rpi_ws281x) ========
ENABLE_LED = True         # Pónlo en True para escribir a la matriz real
LED_PIN        = 18       # GPIO18 por defecto (PWM0). Alternativas: 12,13,19 (ver notas)
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 16       # Empieza BAJO; sube con cuidado
LED_INVERT     = False
LED_CHANNEL    = 0

# STRIP_TYPE: si los colores se ven cruzados, prueba ws.WS2811_STRIP_GRB
strip = None
if ENABLE_LED:
    try:
        from rpi_ws281x import PixelStrip, ws
        STRIP_TYPE = ws.WS2811_STRIP_RGB
        strip = PixelStrip(
            LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
            LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, STRIP_TYPE
        )
        strip.begin()
    except Exception as e:
        print("No se pudo iniciar rpi_ws281x:", e)
        print("Continuaré solo con la simulación.")
        ENABLE_LED = False
        strip = None

# ======== FUNCIONES MAPEO ========
def xy_to_index_rows_snake(x, y, width, height, origin_top_left=True):
    row = y if origin_top_left else (height - 1 - y)
    if row % 2 == 0:
        return row * width + x
    else:
        return row * width + (width - 1 - x)

def xy_to_index_cols_snake(x, y, width, height, origin_top_left=True):
    col = x
    row = y if origin_top_left else (height - 1 - y)
    if col % 2 == 0:
        return col * height + row
    else:
        return col * height + (height - 1 - row)

def get_xy_to_index(layout, origin_top_left=True):
    if layout == "rows_snake":
        return lambda x, y: xy_to_index_rows_snake(x, y, WIDTH, HEIGHT, origin_top_left)
    elif layout == "cols_snake":
        return lambda x, y: xy_to_index_cols_snake(x, y, WIDTH, HEIGHT, origin_top_left)
    else:
        raise ValueError("LAYOUT debe ser 'rows_snake' o 'cols_snake'.")

def clear_strip():
    if strip is None:
        return
    for i in range(LED_COUNT):
        strip.setPixelColorRGB(i, 0, 0, 0)
    strip.show()

def draw_grid(img, step=SCALE, color=(30,30,30)):
    h, w = img.shape[:2]
    for x in range(0, w+1, step):
        cv2.line(img, (x, 0), (x, h), color, 1, lineType=cv2.LINE_AA)
    for y in range(0, h+1, step):
        cv2.line(img, (0, y), (w, y), color, 1, lineType=cv2.LINE_AA)

# ======== CAMARA ========
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

# ======== ESTADO ========
_prev_time = time.time()
fps = 0.0
test_mode = False
test_index = 0
xy_to_index = get_xy_to_index(LAYOUT, ORIGIN_TOP_LEFT)

try:
    while True:
        ok, frame = cap.read()
        if not ok:
            print("No hay frame de la cámara.")
            break

        if MIRROR:
            frame = cv2.flip(frame, 1)

        # --- Generamos la imagen "small" que representa la matriz ---
        if test_mode:
            # Patrón de test: “chaser” + degradé
            small_rgb = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            # Degradé sutil de fondo (horizontal)
            for x in range(WIDTH):
                val = int(255 * x / max(1, WIDTH-1))
                small_rgb[:, x] = (val//3, val, val//2)
            # LED "activo" que recorre todo el strip en orden segun mapeo
            # Convertimos test_index (0..LED_COUNT-1) a (x,y) inverso
            # Buscamos el xy con índice igual a test_index
            # (raro pero simple para debug; costo O(N), no afecta mucho)
            active_xy = None
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    if xy_to_index(x, y) == test_index:
                        active_xy = (x, y)
                        break
                if active_xy is not None:
                    break
            if active_xy is not None:
                ax, ay = active_xy
                small_rgb[ay, ax] = (255, 255, 255)
            test_index = (test_index + 1) % LED_COUNT
            time.sleep(0.002)  # reduce velocidad del chaser
        else:
            # Modo cámara:
            small_bgr = cv2.resize(frame, (WIDTH, HEIGHT), interpolation=cv2.INTER_LINEAR)
            small_rgb = cv2.cvtColor(small_bgr, cv2.COLOR_BGR2RGB)

        # --- SIMULACIÓN EN VENTANA ---
        sim_rgb = cv2.resize(small_rgb, (WIDTH*SCALE, HEIGHT*SCALE), interpolation=cv2.INTER_NEAREST)
        if SHOW_GRID:
            draw_grid(sim_rgb, step=SCALE, color=(30,30,30))

        info = f"{WIDTH}x{HEIGHT} | Layout:{LAYOUT} | OriginTopLeft:{ORIGIN_TOP_LEFT} | Mirror:{MIRROR} | Test:{test_mode}"
        cv2.putText(sim_rgb, info, (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)

        now = time.time()
        dt = now - _prev_time
        _prev_time = now
        if dt > 0:
            fps = 0.9*fps + 0.1*(1.0/dt)
        if SHOW_FPS:
            cv2.putText(sim_rgb, f"FPS: {fps:.1f}", (8, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)

        # Vista de webcam al lado (solo informativa)
        preview = cv2.resize(frame, (sim_rgb.shape[1], sim_rgb.shape[0]), interpolation=cv2.INTER_AREA)
        preview = cv2.putText(preview.copy(), "Webcam (BGR)", (8, 20),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
        sim_bgr = cv2.cvtColor(sim_rgb, cv2.COLOR_RGB2BGR)
        both = np.hstack([sim_bgr, preview])
        cv2.imshow("Matriz LED (izq) | Webcam (der)", both)

        # --- ESCRITURA A LA MATRIZ REAL ---
        if ENABLE_LED and strip is not None:
            # Escribe cada pixel según el mapeo
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    r, g, b = small_rgb[y, x]
                    i = xy_to_index(x, y)
                    strip.setPixelColorRGB(i, int(r), int(g), int(b))
            strip.show()

        # --- CONTROLES TECLADO ---
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):  # ESC o q
            break
        elif key == ord('l'):
            LAYOUT = "cols_snake" if LAYOUT == "rows_snake" else "rows_snake"
            xy_to_index = get_xy_to_index(LAYOUT, ORIGIN_TOP_LEFT)
        elif key == ord('o'):
            ORIGIN_TOP_LEFT = not ORIGIN_TOP_LEFT
            xy_to_index = get_xy_to_index(LAYOUT, ORIGIN_TOP_LEFT)
        elif key == ord('f'):
            MIRROR = not MIRROR
        elif key == ord('g'):
            SHOW_GRID = not SHOW_GRID
        elif key == ord('t'):
            test_mode = not test_mode

except KeyboardInterrupt:
    pass
finally:
    cap.release()
    cv2.destroyAllWindows()
    clear_strip()

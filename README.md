# 🐍 Tutorial: Crear Entornos Virtuales en Raspberry Pi OS y Usarlos con Visual Studio Code

Este tutorial te guiará paso a paso para configurar un entorno virtual de Python en tu Raspberry Pi y usarlo desde Visual Studio Code.

## 📦 Requisitos Previos

- Raspberry Pi OS actualizado
- Python 3 instalado (por defecto viene con la mayoría de las versiones)
- VS Code instalado en Raspberry Pi o accediendo remotamente (por ejemplo, con la extensión Remote-SSH)
- Extensión **Python** instalada en VS Code

---

## 1️⃣ Verificar Python y pip

Abre una terminal y verifica que Python y pip están instalados:

```bash
python3 --version
pip3 --version
```

Si no están instalados:

```bash
sudo apt update
sudo apt install python3 python3-pip
```

---

## 2️⃣ Instalar `venv` (si es necesario)

El módulo `venv` permite crear entornos virtuales. Para instalarlo:

```bash
sudo apt install python3-venv
```

---

## 3️⃣ Crear un Proyecto y Entorno Virtual

Crea una carpeta para tu proyecto y accede a ella:

```bash
mkdir mi_proyecto
cd mi_proyecto
```

Crea el entorno virtual:

```bash
python3 -m venv venv
```

Esto creará una carpeta `venv/` con el entorno virtual.

---

## 4️⃣ Activar el Entorno Virtual

Desde la terminal:

```bash
source venv/bin/activate
```

Deberías ver algo así en tu terminal:

```bash
(venv) pi@raspberrypi:~/mi_proyecto $
```

Para desactivar el entorno virtual:

```bash
deactivate
```

---

## 5️⃣ Abrir el Proyecto en VS Code

Desde la carpeta del proyecto:

```bash
code .
```

Esto abrirá VS Code en esa carpeta. Asegúrate de tener instalada la extensión oficial de Python.

---

## 6️⃣ Configurar el Entorno Virtual en VS Code

1. Pulsa `Ctrl+Shift+P` para abrir la paleta de comandos.
2. Escribe y selecciona `Python: Select Interpreter`.
3. Selecciona el intérprete que apunta a `./venv/bin/python`.

VS Code recordará esta configuración para el proyecto.

---

## 7️⃣ Instalar Dependencias en el Entorno Virtual

Con el entorno activado en terminal o desde VS Code:

```bash
pip install nombre_paquete
```

Ejemplo:

```bash
pip install requests
```

Opcional: crea un archivo `requirements.txt` con:

```bash
pip freeze > requirements.txt
```

Y luego puedes instalar desde ese archivo con:

```bash
pip install -r requirements.txt
```

---

## ✅ Listo

Tu Raspberry Pi ya está configurada para trabajar profesionalmente con Python en VS Code usando entornos virtuales aislados por proyecto.

---

## 🛠️ Tips

- Usa entornos virtuales para evitar conflictos entre proyectos.
- Puedes tener varios entornos para diferentes versiones de dependencias.

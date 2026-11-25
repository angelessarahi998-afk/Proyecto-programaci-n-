import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime
import os
import tempfile
import webbrowser
from pathlib import Path
import mysql.connector
from mysql.connector import Error
#ADRIANA,ERIK Y SARAHI SUBEN PROYECTO TRABAJADO EN EQUIPO DURANTE LA ESCUELA CON LOS CAMBIOS SOLICITADOS 
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "", 
    "database": "sistema_escolar",
    "charset": "utf8mb4",
    "use_unicode": True,
}


USUARIOS_DOCENTES = {
    "profe.maria":  {"pass": "Maria1",  "grupo": "1°", "nombre_real": "Profra. Maria Lopez - 1° Grado"},
    "profe.juan":   {"pass": "Juan2",   "grupo": "2°", "nombre_real": "Profe. Juan Perez - 2° Grado"},
    "profe.ana":    {"pass": "Ana3",    "grupo": "3°", "nombre_real": "Profra. Ana Torres - 3° Grado"},
    "profe.carlos": {"pass": "Carlos4", "grupo": "4°", "nombre_real": "Profe. Carlos Ruiz - 4° Grado"},
    "profe.laura":  {"pass": "Laura5",  "grupo": "5°", "nombre_real": "Profra. Laura Gomez - 5° Grado"},
    "profe.luis":   {"pass": "Luis6",   "grupo": "6°", "nombre_real": "Profe. Luis Hernandez - 6° Grado"},
}
USUARIO_DIRECTOR = "director"
CONTRASENA_DIRECTOR = "Director123"

GUINDA = "#800000"
GUINDA_OSCURO = "#570000"
BLANCO = "#FFFFFF"
FONDO = "#FFF8F6"
TEXTO = "#332629"
GRIS_BORDE = "#EAD9D9"
ROSA = "#F3C6D3"
ROSA_CLARO = "#FCE8EE"
DORADO = "#E8B85A"
MENTA = "#B9DCCB"
MENTA_OSCURO = "#39785C"
LILA = "#952F57"
AZUL = "#A0522D"
CORAL = "#E99A8B"
CREMA = "#FFF0D5"
PALETA = [GUINDA, "#B85C70", "#D49A42", "#5B9A7A", "#8A75B5", "#5C8FB8"]

alumnos = []
registros = []
incidencias = []
cartas_compromiso = []

# ==========================================================
# CONEXION Y ESTRUCTURA DE LA BASE DE DATOS MYSQL
# ==========================================================
def conectar_servidor():
    """Conecta al servidor MySQL sin seleccionar todavía una base de datos."""
    config = DB_CONFIG.copy()
    config.pop("database", None)
    return mysql.connector.connect(**config)


def conectar_bd():
    """Abre una conexión a la base de datos del sistema escolar."""
    return mysql.connector.connect(**DB_CONFIG)


def inicializar_base_datos():
    # Crear la base de datos si todavía no existe.
    con = conectar_servidor()
    try:
        cur = con.cursor()
        cur.execute(
            "CREATE DATABASE IF NOT EXISTS sistema_escolar "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        con.commit()
        cur.close()
    finally:
        con.close()

    # Crear las tablas necesarias.
    con = conectar_bd()
    try:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS alumnos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(200) NOT NULL,
            grupo VARCHAR(10) NOT NULL,
            UNIQUE KEY uq_alumno_grupo (nombre, grupo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        cur.execute("""CREATE TABLE IF NOT EXISTS registros (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fecha VARCHAR(10) NOT NULL,
            nombre VARCHAR(200) NOT NULL,
            grupo VARCHAR(10) NOT NULL,
            estado VARCHAR(20) NOT NULL,
            docente VARCHAR(100),
            UNIQUE KEY uq_asistencia_dia (fecha, nombre, grupo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        cur.execute("""CREATE TABLE IF NOT EXISTS incidencias (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fecha VARCHAR(10),
            nombre VARCHAR(200),
            grupo VARCHAR(10),
            descripcion TEXT,
            docente VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        cur.execute("""CREATE TABLE IF NOT EXISTS cartas_compromiso (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fecha VARCHAR(10),
            nombre VARCHAR(200),
            grupo VARCHAR(10),
            tutor VARCHAR(200),
            contenido TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        # Los PDF se almacenan en MySQL para conservarlos entre sesiones.
        cur.execute("""CREATE TABLE IF NOT EXISTS documentos_pdf (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre_archivo VARCHAR(255) NOT NULL,
            descripcion VARCHAR(300),
            grupo VARCHAR(10) NOT NULL DEFAULT 'Todos',
            fecha_subida DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            subido_por VARCHAR(120) NOT NULL,
            rol_subida VARCHAR(20) NOT NULL,
            archivo LONGBLOB NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        con.commit()
        cur.close()
    finally:
        con.close()


def cargar_base_datos():
    """Carga desde MySQL los datos que utiliza la interfaz."""
    global alumnos, registros, incidencias, cartas_compromiso
    con = conectar_bd()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT nombre, grupo FROM alumnos ORDER BY grupo, nombre")
        alumnos = cur.fetchall()
        cur.execute("SELECT fecha, nombre, grupo, estado, docente FROM registros")
        registros = cur.fetchall()
        cur.execute("SELECT fecha, nombre, grupo, descripcion, docente FROM incidencias")
        incidencias = cur.fetchall()
        cur.execute("SELECT fecha, nombre, grupo, tutor, contenido FROM cartas_compromiso")
        cartas_compromiso = cur.fetchall()
        cur.close()
    finally:
        con.close()


def guardar_base_datos():
    """Guarda los datos actuales en MySQL dentro de una transacción."""
    con = conectar_bd()
    try:
        cur = con.cursor()
        # Se reemplazan los datos de las listas para conservar el comportamiento
        # del programa original y mantener sincronizada la información.
        cur.execute("DELETE FROM alumnos")
        if alumnos:
            cur.executemany(
                "INSERT INTO alumnos(nombre, grupo) VALUES (%s, %s)",
                [(a["nombre"], a["grupo"]) for a in alumnos]
            )
        cur.execute("DELETE FROM registros")
        if registros:
            cur.executemany(
                "INSERT INTO registros(fecha,nombre,grupo,estado,docente) VALUES(%s,%s,%s,%s,%s)",
                [(r["fecha"], r["nombre"], r["grupo"], r["estado"], r.get("docente", "")) for r in registros]
            )
        cur.execute("DELETE FROM incidencias")
        if incidencias:
            cur.executemany(
                "INSERT INTO incidencias(fecha,nombre,grupo,descripcion,docente) VALUES(%s,%s,%s,%s,%s)",
                [(i["fecha"], i["nombre"], i["grupo"], i["descripcion"], i.get("docente", "")) for i in incidencias]
            )
        cur.execute("DELETE FROM cartas_compromiso")
        if cartas_compromiso:
            cur.executemany(
                "INSERT INTO cartas_compromiso(fecha,nombre,grupo,tutor,contenido) VALUES(%s,%s,%s,%s,%s)",
                [(c["fecha"], c["nombre"], c["grupo"], c["tutor"], c["contenido"]) for c in cartas_compromiso]
            )
        con.commit()
        cur.close()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def contar_faltas(nombre, grupo):
    return sum(1 for r in registros
               if r["nombre"] == nombre and r["grupo"] == grupo and r["estado"] == "Falta")


def nivel_alerta(faltas):
    if faltas == 1:
        return "Amarillo", "#FFF2B3", "#8A6D00"
    if 2 <= faltas <= 3:
        return "Naranja", "#FFE0BD", "#A65300"
    if faltas > 3:
        return "Rojo", "#FFD6D6", "#A50000"
    return "Sin alerta", BLANCO, TEXTO

# Preparar la base de datos antes de abrir la ventana.
try:
    inicializar_base_datos()
    cargar_base_datos()
except Error as e:
    aviso = tk.Tk()
    aviso.withdraw()
    messagebox.showerror(
        "Error de conexión con MySQL",
        "No fue posible conectar con MySQL.\n\n"
        "Verifica que MySQL Server esté iniciado y que los datos de DB_CONFIG "
        "(host, puerto, usuario y contraseña) sean correctos.\n\n"
        f"Detalle: {e}\n\n"
        "Instala el conector con: pip install mysql-connector-python"
    )
    aviso.destroy()
    raise SystemExit(1)

usuario_actual = ""
rol_actual = ""
grupo_actual = ""
nombre_real_actual = ""

root = tk.Tk()
root.title("Sistema de Asistencia Escolar ")
root.geometry("1120x720")
root.minsize(900, 600)
root.configure(bg=FONDO)
panel_contenido = None

estilo = ttk.Style()
estilo.theme_use("clam")
estilo.configure("Treeview", background=BLANCO, foreground=TEXTO, rowheight=34, fieldbackground=BLANCO, font=("Arial", 10))
estilo.configure("Treeview.Heading", background=GUINDA, foreground=BLANCO, font=("Arial", 10, "bold"), padding=8)
estilo.map("Treeview", background=[("selected", "#EAD1D8")], foreground=[("selected", GUINDA_OSCURO)])
estilo.configure("TCombobox", padding=6, fieldbackground=BLANCO)
estilo.configure("Vertical.TScrollbar", background=ROSA, troughcolor=FONDO, arrowcolor=GUINDA)

def fecha_hoy(): return date.today().strftime("%d/%m/%Y")
def limpiar_ventana():
    for w in root.winfo_children(): w.destroy()
def crear_boton(parent, texto, comando, color=GUINDA):
    return tk.Button(parent, text=texto, command=comando, bg=color, fg=BLANCO, activebackground=GUINDA_OSCURO, activeforeground=BLANCO, relief="flat", cursor="hand2", font=("Arial", 10, "bold"), padx=18, pady=10, bd=0)
def preparar_pagina(titulo, subtitulo=""):
    for w in panel_contenido.winfo_children(): w.destroy()
    tk.Label(panel_contenido, text=f"✿  {titulo}", bg=FONDO, fg=GUINDA, font=("Arial", 21, "bold"), wraplength=800, justify="left").pack(anchor="w", pady=(0, 6))
    if subtitulo:
        tk.Label(panel_contenido, text=subtitulo, bg=FONDO, fg="#666666", font=("Arial", 11), wraplength=800, justify="left").pack(anchor="w", pady=(0, 20))
    else:
        tk.Frame(panel_contenido, height=12, bg=FONDO).pack()
def crear_tabla(parent, columnas, encabezados, altura=10):
    contenedor = tk.Frame(parent, bg=BLANCO, padx=12, pady=12, highlightbackground=GRIS_BORDE, highlightthickness=1)
    contenedor.pack(fill="both", expand=True, pady=(8, 18))
    tabla = ttk.Treeview(contenedor, columns=columnas, show="headings", height=altura)
    for c, t in zip(columnas, encabezados):
        tabla.heading(c, text=t)
        tabla.column(c, width=160, anchor="w")
    sy = ttk.Scrollbar(contenedor, orient="vertical", command=tabla.yview)
    sx = ttk.Scrollbar(contenedor, orient="horizontal", command=tabla.xview)
    tabla.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
    tabla.grid(row=0, column=0, sticky="nsew")
    sy.grid(row=0, column=1, sticky="ns")
    sx.grid(row=1, column=0, sticky="ew")
    contenedor.grid_rowconfigure(0, weight=1)
    contenedor.grid_columnconfigure(0, weight=1)
    return tabla
def tarjeta_color(parent, titulo, valor, color, icono="✦"):
    """Tarjeta KPI decorativa con acento de color."""
    caja = tk.Frame(parent, bg=BLANCO, padx=16, pady=13,
                    highlightbackground=color, highlightthickness=2)
    tk.Label(caja, text=icono, bg=color, fg=BLANCO,
             font=("Arial", 15, "bold"), width=3, pady=5).pack(anchor="w")
    tk.Label(caja, text=titulo, bg=BLANCO, fg="#725C61",
             font=("Arial", 9, "bold"), wraplength=190, justify="left").pack(anchor="w", pady=(9, 2))
    tk.Label(caja, text=str(valor), bg=BLANCO, fg=color,
             font=("Arial", 25, "bold")).pack(anchor="w")
    return caja


def dibujo_escolar(parent, ancho=280, alto=150):
    """Ilustración vectorial hecha con Canvas; no requiere imágenes externas."""
    c = tk.Canvas(parent, width=ancho, height=alto, bg=ROSA_CLARO, highlightthickness=0)
    c.pack(fill="x", expand=True)
    # Sol y nubes
    c.create_oval(ancho-78, 12, ancho-28, 62, fill=CREMA, outline="")
    c.create_oval(18, 25, 72, 59, fill=BLANCO, outline="")
    c.create_oval(42, 15, 90, 58, fill=BLANCO, outline="")
    # Libros apilados
    c.create_rectangle(30, 94, 120, 119, fill=GUINDA, outline="")
    c.create_rectangle(38, 84, 128, 108, fill=ROSA, outline="")
    c.create_rectangle(47, 74, 137, 98, fill=DORADO, outline="")
    for x in (43, 53, 63):
        c.create_line(x, 87, x, 105, fill=BLANCO, width=2)
    # Lápiz
    c.create_polygon(177, 116, 195, 58, 207, 62, 189, 121, fill=DORADO, outline=GUINDA)
    c.create_polygon(195, 58, 202, 43, 207, 62, fill=GUINDA, outline=GUINDA)
    # Manzana estilizada
    c.create_oval(218, 82, 263, 124, fill=CORAL, outline="")
    c.create_oval(238, 77, 260, 96, fill=CORAL, outline="")
    c.create_line(241, 84, 246, 70, fill=MENTA_OSCURO, width=4)
    c.create_oval(245, 69, 266, 78, fill=MENTA, outline="")
    c.create_text(ancho//2, alto-12, text="APRENDER • CRECER • COMPARTIR",
                  fill=GUINDA, font=("Arial", 8, "bold"))
    return c


def grafico_barras(parent, etiquetas, valores, titulo="Alumnos por grupo", colores=None):
    """Gráfico de barras nativo de Tkinter, sin instalar matplotlib."""
    marco = tk.Frame(parent, bg=BLANCO, padx=14, pady=12,
                     highlightbackground=GRIS_BORDE, highlightthickness=1)
    tk.Label(marco, text=titulo, bg=BLANCO, fg=GUINDA,
             font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))
    w, h = 560, 205
    cv = tk.Canvas(marco, width=w, height=h, bg=BLANCO, highlightthickness=0)
    cv.pack(fill="x", expand=True)
    maximo = max(valores) if valores and max(valores) > 0 else 1
    margen_i, margen_d, margen_t, margen_b = 35, 18, 12, 34
    zona_h = h - margen_t - margen_b
    cv.create_line(margen_i, margen_t, margen_i, h-margen_b, fill="#D9C9CC")
    cv.create_line(margen_i, h-margen_b, w-margen_d, h-margen_b, fill="#D9C9CC")
    n = max(1, len(etiquetas)); ancho = (w-margen_i-margen_d)/n
    for i, (et, val) in enumerate(zip(etiquetas, valores)):
        bh = (max(0, val)/maximo)*(zona_h-18)
        x0 = margen_i + i*ancho + ancho*0.22
        x1 = margen_i + (i+1)*ancho - ancho*0.22
        y0 = h-margen_b-bh
        color = (colores or PALETA)[i % len(colores or PALETA)]
        cv.create_rectangle(x0, y0, x1, h-margen_b, fill=color, outline="", width=0)
        cv.create_text((x0+x1)/2, max(8, y0-9), text=str(val), fill=TEXTO,
                       font=("Arial", 9, "bold"))
        cv.create_text((x0+x1)/2, h-17, text=et, fill="#66565A", font=("Arial", 9, "bold"))
    return marco


def grafico_dona(parent, valores, etiquetas, colores, titulo="Resumen de asistencia"):
    marco = tk.Frame(parent, bg=BLANCO, padx=14, pady=12,
                     highlightbackground=GRIS_BORDE, highlightthickness=1)
    tk.Label(marco, text=titulo, bg=BLANCO, fg=GUINDA,
             font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))
    cv = tk.Canvas(marco, width=230, height=190, bg=BLANCO, highlightthickness=0)
    cv.pack(side="left", padx=(0, 12))
    total = sum(valores)
    if total <= 0:
        cv.create_oval(45, 18, 185, 158, outline="#E8DDE0", width=22)
        cv.create_text(115, 88, text="Sin datos", fill="#8A777C", font=("Arial", 10, "bold"))
    else:
        inicio = 90
        for valor, color in zip(valores, colores):
            extension = 360 * valor / total
            if extension > 0:
                cv.create_arc(45, 18, 185, 158, start=inicio, extent=extension,
                              style="arc", outline=color, width=23)
            inicio += extension
        cv.create_text(115, 88, text=str(total), fill=GUINDA,
                       font=("Arial", 18, "bold"))
        cv.create_text(115, 111, text="registros", fill="#8A777C", font=("Arial", 8))
    leyenda = tk.Frame(marco, bg=BLANCO)
    leyenda.pack(side="left", fill="both", expand=True)
    for et, val, color in zip(etiquetas, valores, colores):
        fila = tk.Frame(leyenda, bg=BLANCO)
        fila.pack(anchor="w", pady=6, fill="x")
        tk.Label(fila, text="●", fg=color, bg=BLANCO, font=("Arial", 13)).pack(side="left")
        tk.Label(fila, text=f" {et}: {val}", fg=TEXTO, bg=BLANCO,
                 font=("Arial", 9, "bold")).pack(side="left")
    return marco


def exportar_txt(nombre, contenido):
    ruta = filedialog.asksaveasfilename(title="Guardar archivo", defaultextension=".txt", initialfile=nombre, filetypes=[("Archivo de texto", "*.txt")])
    if not ruta: return
    try:
        with open(ruta, "w", encoding="utf-8") as archivo: archivo.write(contenido)
        messagebox.showinfo("Guardado", "Archivo guardado correctamente.")
    except OSError as e: messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
def alumnos_ordenados(): return sorted(alumnos, key=lambda a: (a["grupo"].lower(), a["nombre"].lower()))
def alumnos_de_mi_grupo():
    if rol_actual == "director": return alumnos_ordenados()
    return [a for a in alumnos_ordenados() if a["grupo"] == grupo_actual]

def mostrar_login():
    limpiar_ventana()
    fondo = tk.Frame(root, bg=FONDO)
    fondo.pack(fill="both", expand=True)
    lateral = tk.Frame(fondo, bg=GUINDA, width=390)
    lateral.pack(side="left", fill="y")
    lateral.pack_propagate(False)
    tk.Label(lateral, text="✦  ✿  ✦", bg=GUINDA, fg=DORADO,
             font=("Arial", 24, "bold")).pack(pady=(65, 18))
    tk.Label(lateral, text="¡Bienvenidos!", bg=GUINDA, fg=BLANCO,
             font=("Arial", 25, "bold")).pack(pady=5)
    tk.Label(lateral, text="SISTEMA DE ASISTENCIA\nESCOLAR", bg=GUINDA, fg=ROSA_CLARO,
             font=("Arial", 16, "bold"), justify="center").pack(pady=8)
    art = tk.Canvas(lateral, width=300, height=185, bg=GUINDA, highlightthickness=0)
    art.pack(pady=20)
    art.create_oval(100, 8, 200, 108, fill=CREMA, outline="")
    art.create_rectangle(60, 108, 240, 145, fill=ROSA, outline="")
    art.create_rectangle(77, 88, 257, 126, fill=DORADO, outline="")
    art.create_rectangle(91, 68, 271, 106, fill=BLANCO, outline="")
    art.create_polygon(72, 68, 180, 15, 288, 68, fill=GUINDA_OSCURO, outline=BLANCO, width=2)
    art.create_line(180, 15, 180, 68, fill=DORADO, width=4)
    tk.Label(lateral, text="6 grados  •  6 docentes  •  1 comunidad",
             bg=GUINDA, fg=BLANCO, font=("Arial", 9, "bold")).pack(pady=12)

    zona = tk.Frame(fondo, bg=FONDO)
    zona.pack(side="right", fill="both", expand=True)
    cont = tk.Frame(zona, bg=BLANCO, padx=38, pady=34,
                    highlightbackground=GRIS_BORDE, highlightthickness=1)
    cont.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(cont, text="Iniciar sesión", bg=BLANCO, fg=GUINDA,
             font=("Arial", 22, "bold")).pack(anchor="w", pady=(0, 5))
    tk.Label(cont, text="Ingresa tus datos para continuar", bg=BLANCO,
             fg="#88777C", font=("Arial", 10)).pack(anchor="w", pady=(0, 24))
    tk.Label(cont, text="USUARIO", bg=BLANCO, fg=GUINDA,
             font=("Arial", 9, "bold")).pack(anchor="w", pady=(0, 5))
    eu = tk.Entry(cont, width=31, font=("Arial", 12), relief="flat",
                  bg="#FFF8FA", highlightthickness=1, highlightbackground=ROSA)
    eu.pack(ipady=10, pady=(0, 17), fill="x")
    tk.Label(cont, text="CONTRASEÑA", bg=BLANCO, fg=GUINDA,
             font=("Arial", 9, "bold")).pack(anchor="w", pady=(0, 5))
    ec = tk.Entry(cont, show="●", width=31, font=("Arial", 12), relief="flat",
                  bg="#FFF8FA", highlightthickness=1, highlightbackground=ROSA)
    ec.pack(ipady=10, pady=(0, 24), fill="x")
    def ingresar(event=None):
        global usuario_actual, rol_actual, grupo_actual, nombre_real_actual
        u = eu.get().strip(); p = ec.get()
        if u in USUARIOS_DOCENTES and USUARIOS_DOCENTES[u]["pass"] == p:
            usuario_actual = u; rol_actual = "docente"
            grupo_actual = USUARIOS_DOCENTES[u]["grupo"]
            nombre_real_actual = USUARIOS_DOCENTES[u]["nombre_real"]
            mostrar_sistema()
        elif u == USUARIO_DIRECTOR and p == CONTRASENA_DIRECTOR:
            usuario_actual = u; rol_actual = "director"; grupo_actual = "Todos"
            nombre_real_actual = "Director General"
            mostrar_sistema()
        else:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.\nEj: profe.maria / Maria1")
    crear_boton(cont, "ENTRAR AL SISTEMA  ➜", ingresar, GUINDA).pack(fill="x", ipady=5)
    tk.Label(cont, text="Docentes: profe.fer / Fer1\nDirector: director / Director143",
             bg=BLANCO, fg="#9A858B", font=("Arial", 8), justify="center").pack(pady=(17, 0))
    eu.focus_set(); ec.bind("<Return>", ingresar)

def normalizar_grupo_excel(valor):
    """Convierte valores comunes de Excel a los grupos 1° ... 6° del sistema."""
    if valor is None:
        return None
    texto = str(valor).strip().lower().replace("º", "°")
    texto = texto.replace("grado", "").replace(" ", "")
    equivalencias = {
        "1": "1°", "1°": "1°", "1o": "1°", "primero": "1°", "1er": "1°",
        "2": "2°", "2°": "2°", "2o": "2°", "segundo": "2°", "2do": "2°",
        "3": "3°", "3°": "3°", "3o": "3°", "tercero": "3°", "3er": "3°",
        "4": "4°", "4°": "4°", "4o": "4°", "cuarto": "4°", "4to": "4°",
        "5": "5°", "5°": "5°", "5o": "5°", "quinto": "5°", "5to": "5°",
        "6": "6°", "6°": "6°", "6o": "6°", "sexto": "6°", "6to": "6°",
    }
    return equivalencias.get(texto)


def descargar_plantilla_excel():
    """Crea una plantilla .xlsx para llenar nombres y grupos."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter
    except ImportError:
        messagebox.showerror("Falta instalar openpyxl",
                             "Instala el paquete con:\npip install openpyxl")
        return

    ruta = filedialog.asksaveasfilename(
        title="Guardar plantilla de alumnos",
        defaultextension=".xlsx",
        initialfile="plantilla_alumnos.xlsx",
        filetypes=[("Libro de Excel", "*.xlsx")]
    )
    if not ruta:
        return
    try:
        libro = Workbook()
        hoja = libro.active
        hoja.title = "Alumnos"
        hoja.append(["nombre", "grupo"])
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = "A1:B1"
        for celda in hoja[1]:
            celda.font = Font(bold=True, color="FFFFFF")
            celda.fill = PatternFill("solid", fgColor="800000")
            celda.alignment = Alignment(horizontal="center")
        hoja.column_dimensions[get_column_letter(1)].width = 38
        hoja.column_dimensions[get_column_letter(2)].width = 18

        instrucciones = libro.create_sheet("Instrucciones")
        instrucciones.append(["CARGA MASIVA DE ALUMNOS"])
        instrucciones.append(["En la hoja Alumnos, escribe un alumno por fila."])
        instrucciones.append(["Columna A: nombre completo del alumno."])
        instrucciones.append(["Columna B: grupo (1°, 2°, 3°, 4°, 5° o 6°)."])
        instrucciones.append(["También puedes escribir solamente 1, 2, 3, 4, 5 o 6."])
        instrucciones.column_dimensions["A"].width = 85
        instrucciones["A1"].font = Font(bold=True, color="800000", size=14)
        libro.save(ruta)
        messagebox.showinfo("Plantilla creada", f"La plantilla se guardó correctamente:\n{ruta}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo crear la plantilla:\n{e}")


def importar_alumnos_excel():
    """Importa alumnos desde .xlsx y los inserta sin borrar datos existentes."""
    if rol_actual != "director":
        messagebox.showwarning("Permisos", "Solo el director puede realizar la carga masiva.")
        return
    try:
        from openpyxl import load_workbook
    except ImportError:
        messagebox.showerror("Falta instalar openpyxl",
                             "Para importar Excel instala el paquete:\npip install openpyxl")
        return

    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo de Excel",
        filetypes=[("Archivos de Excel", "*.xlsx")]
    )
    if not ruta:
        return

    try:
        libro = load_workbook(ruta, read_only=True, data_only=True)
        hoja = libro["Alumnos"] if "Alumnos" in libro.sheetnames else libro.active
        filas = hoja.iter_rows(values_only=True)
        encabezados = next(filas, None)
        if not encabezados:
            libro.close()
            messagebox.showwarning("Archivo vacío", "El archivo no contiene encabezados ni alumnos.")
            return

        def limpiar_encabezado(valor):
            return str(valor or "").strip().lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

        nombres_columnas = [limpiar_encabezado(x) for x in encabezados]
        columna_nombre = next((i for i, x in enumerate(nombres_columnas)
                               if x in ("nombre", "nombres", "nombre completo", "alumno")), None)
        columna_grupo = next((i for i, x in enumerate(nombres_columnas)
                              if x in ("grupo", "grado")), None)
        if columna_nombre is None or columna_grupo is None:
            libro.close()
            messagebox.showerror(
                "Formato incorrecto",
                "No se encontraron las columnas necesarias.\n\n"
                "La primera fila debe tener los encabezados: nombre y grupo.\n"
                "Puedes descargar la plantilla desde este apartado."
            )
            return

        alumnos_archivo = []
        filas_invalidas = 0
        for fila in filas:
            valores = list(fila)
            nombre_valor = valores[columna_nombre] if columna_nombre < len(valores) else None
            grupo_valor = valores[columna_grupo] if columna_grupo < len(valores) else None
            nombre = str(nombre_valor).strip() if nombre_valor is not None else ""
            grupo = normalizar_grupo_excel(grupo_valor)
            if not nombre and not grupo_valor:
                continue
            if not nombre or not grupo or len(nombre) > 200:
                filas_invalidas += 1
                continue
            alumnos_archivo.append((nombre, grupo))
        libro.close()

        if not alumnos_archivo:
            messagebox.showwarning("Sin alumnos válidos",
                                   f"No se encontraron alumnos para importar.\nFilas incompletas o inválidas: {filas_invalidas}")
            return

        con = conectar_bd()
        try:
            cur = con.cursor()
            cur.executemany(
                "INSERT IGNORE INTO alumnos(nombre, grupo) VALUES (%s, %s)",
                alumnos_archivo
            )
            agregados = cur.rowcount
            con.commit()
            cur.close()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

        duplicados = len(alumnos_archivo) - agregados
        cargar_base_datos()
        messagebox.showinfo(
            "Carga masiva finalizada",
            "La importación terminó.\n\n"
            f"Alumnos agregados: {agregados}\n"
            f"Duplicados omitidos: {duplicados}\n"
            f"Filas incompletas o inválidas: {filas_invalidas}\n\n"
            "Los alumnos ya están guardados en MySQL."
        )
        mostrar_lista_alumnos()
    except Exception as e:
        messagebox.showerror("Error al importar", f"No se pudo leer o importar el archivo.\n\nDetalle: {e}")



def obtener_documentos_pdf():
    """Lista los PDF que puede consultar el usuario actual."""
    con = conectar_bd()
    try:
        cur = con.cursor(dictionary=True)
        if rol_actual == "director":
            cur.execute("""SELECT id, nombre_archivo, descripcion, grupo,
                                  DATE_FORMAT(fecha_subida, '%d/%m/%Y %H:%i') AS fecha,
                                  subido_por
                           FROM documentos_pdf
                           ORDER BY fecha_subida DESC, id DESC""")
        else:
            cur.execute("""SELECT id, nombre_archivo, descripcion, grupo,
                                  DATE_FORMAT(fecha_subida, '%d/%m/%Y %H:%i') AS fecha,
                                  subido_por
                           FROM documentos_pdf
                           WHERE grupo IN (%s, 'Todos')
                           ORDER BY fecha_subida DESC, id DESC""", (grupo_actual,))
        return cur.fetchall()
    finally:
        con.close()


def leer_documento_pdf(documento_id):
    """Recupera el contenido binario del PDF desde MySQL."""
    con = conectar_bd()
    try:
        cur = con.cursor(dictionary=True)
        if rol_actual == "director":
            cur.execute("SELECT nombre_archivo, archivo FROM documentos_pdf WHERE id=%s", (documento_id,))
        else:
            cur.execute("""SELECT nombre_archivo, archivo FROM documentos_pdf
                           WHERE id=%s AND grupo IN (%s, 'Todos')""", (documento_id, grupo_actual))
        return cur.fetchone()
    finally:
        con.close()


def subir_documento_pdf(entrada_descripcion, selector_grupo):
    """Guarda un PDF en MySQL; cada docente queda limitado a su grupo."""
    ruta = filedialog.askopenfilename(title="Seleccionar documento PDF",
                                      filetypes=[("Documentos PDF", "*.pdf")])
    if not ruta:
        return
    try:
        nombre_archivo = os.path.basename(ruta)
        with open(ruta, "rb") as archivo:
            contenido = archivo.read()
        if not contenido.startswith(b"%PDF-"):
            messagebox.showerror("Archivo no válido", "El archivo seleccionado no parece ser un PDF válido.")
            return
        if len(contenido) > 15 * 1024 * 1024:
            messagebox.showwarning("Archivo demasiado grande", "El tamaño máximo permitido es de 15 MB por documento.")
            return
        descripcion = entrada_descripcion.get().strip() or nombre_archivo
        grupo_documento = grupo_actual if rol_actual == "docente" else selector_grupo.get().strip()
        if rol_actual == "director" and not grupo_documento:
            messagebox.showwarning("Selecciona un grupo", "Selecciona el grupo al que pertenecerá el PDF.")
            return
        con = conectar_bd()
        try:
            cur = con.cursor()
            cur.execute("""INSERT INTO documentos_pdf
                           (nombre_archivo, descripcion, grupo, subido_por, rol_subida, archivo)
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (nombre_archivo, descripcion, grupo_documento,
                         nombre_real_actual, rol_actual, contenido))
            con.commit()
            cur.close()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
        entrada_descripcion.delete(0, "end")
        destino = "todos los grupos" if grupo_documento == "Todos" else "grupo " + grupo_documento
        messagebox.showinfo("PDF guardado", f"El documento '{nombre_archivo}' se guardó en MySQL y está disponible para {destino}.")
        mostrar_documentos_pdf()
    except Exception as e:
        messagebox.showerror("Error al subir PDF", f"No se pudo guardar el documento.\n\nDetalle: {e}")


def descargar_documento_pdf(documento_id, abrir=False):
    """Abre o descarga el PDF seleccionado, respetando los permisos del grupo."""
    try:
        documento = leer_documento_pdf(documento_id)
        if not documento:
            messagebox.showwarning("Documento no disponible", "No se encontró el PDF o no tienes permiso para consultarlo.")
            return
        nombre = os.path.basename(documento["nombre_archivo"] or "documento.pdf")
        if abrir:
            temporal = tempfile.NamedTemporaryFile(prefix="documento_escolar_", suffix=".pdf", delete=False)
            temporal.write(documento["archivo"])
            temporal.close()
            webbrowser.open_new(Path(temporal.name).resolve().as_uri())
        else:
            ruta = filedialog.asksaveasfilename(title="Guardar PDF", initialfile=nombre,
                                                defaultextension=".pdf",
                                                filetypes=[("Documento PDF", "*.pdf")])
            if not ruta:
                return
            with open(ruta, "wb") as salida:
                salida.write(documento["archivo"])
            messagebox.showinfo("Descarga completada", f"PDF guardado en:\n{ruta}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo recuperar el PDF.\n\nDetalle: {e}")


def mostrar_documentos_pdf():
    """Apartado de biblioteca PDF para Director y para cada docente."""
    preparar_pagina("Biblioteca de documentos PDF",
                    "Dirección puede compartir archivos con todos los grupos o con uno específico. "
                    "Cada docente puede subir documentos para su grupo y consultar los PDF de su grupo y los generales.")
    tarjeta = tk.Frame(panel_contenido, bg=BLANCO, padx=18, pady=18,
                       highlightbackground=GRIS_BORDE, highlightthickness=1)
    tarjeta.pack(fill="x", pady=(0, 12))
    tk.Label(tarjeta, text="Subir un documento PDF", bg=BLANCO, fg=GUINDA,
             font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
    tk.Label(tarjeta, text="Descripción o nombre del documento:", bg=BLANCO, fg=TEXTO,
             font=("Arial", 10, "bold")).pack(anchor="w")
    entrada_descripcion = tk.Entry(tarjeta, font=("Arial", 11), relief="solid", bd=1, bg="#FFF8FA")
    entrada_descripcion.pack(fill="x", pady=(5, 10), ipady=6)
    selector_grupo = ttk.Combobox(tarjeta, state="readonly",
                                  values=["Todos", "1°", "2°", "3°", "4°", "5°", "6°"], font=("Arial", 10))
    if rol_actual == "director":
        tk.Label(tarjeta, text="Compartir con:", bg=BLANCO, fg=TEXTO,
                 font=("Arial", 10, "bold")).pack(anchor="w")
        selector_grupo.set("Todos")
        selector_grupo.pack(anchor="w", fill="x", pady=(5, 10))
    else:
        tk.Label(tarjeta, text=f"El documento se asignará automáticamente a tu grupo: {grupo_actual}",
                 bg=BLANCO, fg=MENTA_OSCURO, font=("Arial", 10, "bold")).pack(anchor="w", pady=(4, 10))
    crear_boton(tarjeta, "＋  Seleccionar y subir PDF",
                lambda: subir_documento_pdf(entrada_descripcion, selector_grupo), color="#A34A4A").pack(fill="x")

    tk.Label(panel_contenido, text="Documentos disponibles", bg=FONDO, fg=GUINDA,
             font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 2))
    tk.Label(panel_contenido, text="Selecciona un documento de la tabla para abrirlo o guardarlo.",
             bg=FONDO, fg="#76666B", font=("Arial", 9)).pack(anchor="w")
    tabla = crear_tabla(panel_contenido,
                        ("id", "archivo", "grupo", "descripcion", "fecha", "subido"),
                        ("ID", "Archivo PDF", "Grupo", "Descripción", "Fecha de subida", "Subido por"), altura=9)
    for col, ancho in (("id", 45), ("archivo", 180), ("grupo", 70),
                       ("descripcion", 220), ("fecha", 130), ("subido", 180)):
        tabla.column(col, width=ancho, anchor="center" if col in ("id", "grupo") else "w")

    def actualizar_tabla():
        tabla.delete(*tabla.get_children())
        try:
            for doc in obtener_documentos_pdf():
                tabla.insert("", "end", iid=str(doc["id"]),
                             values=(doc["id"], doc["nombre_archivo"], doc["grupo"],
                                     doc["descripcion"] or "", doc["fecha"], doc["subido_por"]))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los documentos.\n\nDetalle: {e}")

    acciones = tk.Frame(panel_contenido, bg=FONDO)
    acciones.pack(fill="x", pady=(0, 16))
    def ejecutar_accion(abrir):
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona un PDF", "Primero selecciona un documento de la tabla.")
            return
        descargar_documento_pdf(int(seleccion[0]), abrir=abrir)
    crear_boton(acciones, "Abrir PDF", lambda: ejecutar_accion(True), color="#5B718F").pack(side="left", padx=(0, 8))
    crear_boton(acciones, "Descargar PDF", lambda: ejecutar_accion(False), color="#39785C").pack(side="left", padx=(0, 8))
    crear_boton(acciones, "Actualizar lista", actualizar_tabla, color="#8A75B5").pack(side="left")
    actualizar_tabla()

def mostrar_sistema():
    global panel_contenido
    limpiar_ventana()
    princ = tk.Frame(root, bg=FONDO); princ.pack(fill="both", expand=True)
    menu = tk.Frame(princ, bg=GUINDA, width=240, padx=12, pady=15); menu.pack(side="left", fill="y"); menu.pack_propagate(False)
    area = tk.Frame(princ, bg=FONDO); area.pack(side="right", fill="both", expand=True)
    enc = tk.Frame(area, bg=BLANCO, padx=22, pady=16, highlightbackground=ROSA, highlightthickness=2); enc.pack(fill="x", padx=18, pady=18)
    tk.Label(enc, text="✿  Sistema de Asistencia Escolar", bg=BLANCO, fg=GUINDA, font=("Arial", 17, "bold")).pack(anchor="w")
    tk.Label(enc, text=f"{nombre_real_actual}  •  Usuario: {usuario_actual}  •  Grupo: {grupo_actual}", bg=BLANCO, fg="#555555", font=("Arial", 10, "bold"), wraplength=700, justify="left").pack(anchor="w", pady=(6, 0))
    lienzo = tk.Canvas(area, bg=FONDO, highlightthickness=0); scroll = ttk.Scrollbar(area, orient="vertical", command=lienzo.yview)
    lienzo.configure(yscrollcommand=scroll.set); scroll.pack(side="right", fill="y"); lienzo.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=(0, 18))
    panel_contenido = tk.Frame(lienzo, bg=FONDO, padx=20, pady=10)
    vp = lienzo.create_window((0, 0), window=panel_contenido, anchor="nw")
    panel_contenido.bind("<Configure>", lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))
    lienzo.bind("<Configure>", lambda e: lienzo.itemconfigure(vp, width=e.width))
    tk.Label(menu, text="✿  MENÚ PRINCIPAL", bg=GUINDA, fg=BLANCO, font=("Arial", 15, "bold")).pack(pady=(10, 8), anchor="w", padx=8)
    tk.Label(menu, text=f"GRUPO {grupo_actual}", bg=GUINDA, fg="#FFD6D6", font=("Arial", 11, "bold")).pack(anchor="w", padx=8, pady=(0, 2))
    tk.Label(menu, text=nombre_real_actual, bg=GUINDA, fg="white", font=("Arial", 9), wraplength=190, justify="left").pack(anchor="w", padx=8, pady=(0, 20))
    if rol_actual == "docente":
        opciones = [("Inicio", mostrar_inicio), (f"Mi Grupo: {grupo_actual}", mostrar_asistencia), ("Incidencias", mostrar_incidencias), ("Documentos PDF", mostrar_documentos_pdf)]
    else:
        opciones = [("Inicio", mostrar_inicio), ("Usuarios y Contraseñas", mostrar_usuarios), ("Registrar alumnos", mostrar_registro_alumnos), ("Carga masiva Excel", mostrar_carga_masiva), ("Lista de alumnos", mostrar_lista_alumnos), ("Reporte general", mostrar_reporte_general), ("Indicadores KPI", mostrar_kpis), ("Reportes completos", mostrar_reportes_completos), ("Cartas compromiso", mostrar_cartas), ("Documentos PDF", mostrar_documentos_pdf)]
    for idx, (txt, fun) in enumerate(opciones):
        color_item = ["#8F263D", "#9D3B55", "#A94D68", "#8D456D", "#765184", "#5F718F"][idx % 6]
        b = tk.Button(menu, text=f"  ✦  {txt}", command=fun, bg=color_item, fg=BLANCO,
                      activebackground=ROSA, activeforeground=GUINDA_OSCURO,
                      relief="flat", anchor="w", padx=10, pady=11,
                      font=("Arial", 9, "bold"), cursor="hand2", bd=0)
        b.pack(fill="x", pady=3)
    tk.Frame(menu, bg="#A34A4A", height=1).pack(fill="x", pady=20, padx=8)
    crear_boton(menu, "Cerrar sesión", cerrar_sesion, GUINDA_OSCURO).pack(fill="x", pady=8, padx=4)
    mostrar_inicio()

def cerrar_sesion():
    global usuario_actual, rol_actual, grupo_actual, nombre_real_actual
    if messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar sesión?"):
        usuario_actual = ""; rol_actual = ""; grupo_actual = ""; nombre_real_actual = ""; mostrar_login()

def mostrar_inicio():
    preparar_pagina(f"Inicio - {grupo_actual}", f"Bienvenido {nombre_real_actual}. Este es tu espacio de trabajo escolar.")
    banner = tk.Frame(panel_contenido, bg=ROSA_CLARO, padx=18, pady=14,
                      highlightbackground=ROSA, highlightthickness=1)
    banner.pack(fill="x", pady=(0, 14))
    texto = tk.Frame(banner, bg=ROSA_CLARO)
    texto.pack(side="left", fill="both", expand=True)
    tk.Label(texto, text="¡Un gran día para aprender!", bg=ROSA_CLARO,
             fg=GUINDA, font=("Arial", 17, "bold")).pack(anchor="w", pady=(8, 4))
    tk.Label(texto, text=f"{nombre_real_actual}  •  {fecha_hoy()}", bg=ROSA_CLARO,
             fg="#725C61", font=("Arial", 10)).pack(anchor="w")
    dibujo_escolar(banner, 285, 145)
    if rol_actual == "docente":
        total = len(alumnos_de_mi_grupo())
        presentes = sum(1 for r in registros if r["grupo"] == grupo_actual and r["fecha"] == fecha_hoy() and r["estado"] == "Presente")
        faltas = sum(1 for r in registros if r["grupo"] == grupo_actual and r["fecha"] == fecha_hoy() and r["estado"] == "Falta")
        retardos = sum(1 for r in registros if r["grupo"] == grupo_actual and r["fecha"] == fecha_hoy() and r["estado"] == "Retardo")
        fila = tk.Frame(panel_contenido, bg=FONDO); fila.pack(fill="x", pady=5)
        for i, datos in enumerate([("Alumnos del grupo", total, GUINDA, "♟"), ("Presentes hoy", presentes, MENTA_OSCURO, "✓"), ("Faltas hoy", faltas, "#C62828", "!"), ("Retardos hoy", retardos, "#B36A16", "◷")]):
            tarjeta_color(fila, *datos).grid(row=0, column=i, sticky="nsew", padx=5)
            fila.grid_columnconfigure(i, weight=1)
        crear_boton(panel_contenido, f"✎  Pasar lista de {grupo_actual}", mostrar_asistencia).pack(fill="x", pady=12)
        grafico = grafico_dona(panel_contenido, [presentes, faltas, retardos],
                               ["Presentes", "Faltas", "Retardos"], [MENTA_OSCURO, CORAL, DORADO],
                               "Asistencia de hoy")
        grafico.pack(fill="x", pady=8)
    else:
        total = len(alumnos)
        total_faltas = sum(1 for r in registros if r["estado"] == "Falta")
        total_presentes = sum(1 for r in registros if r["estado"] == "Presente")
        total_retardos = sum(1 for r in registros if r["estado"] == "Retardo")
        fila = tk.Frame(panel_contenido, bg=FONDO); fila.pack(fill="x", pady=5)
        for i, datos in enumerate([("Alumnos registrados", total, GUINDA, "♟"), ("Asistencias", total_presentes, MENTA_OSCURO, "✓"), ("Faltas", total_faltas, "#C62828", "!"), ("Incidencias", len(incidencias), "#8A75B5", "✎")]):
            tarjeta_color(fila, *datos).grid(row=0, column=i, sticky="nsew", padx=5)
            fila.grid_columnconfigure(i, weight=1)
        tk.Label(panel_contenido, text="Alumnos por grado", bg=FONDO, fg=GUINDA,
                 font=("Arial", 14, "bold")).pack(anchor="w", pady=(18, 8))
        grupos = ["1°", "2°", "3°", "4°", "5°", "6°"]
        cantidades = [sum(1 for a in alumnos if a["grupo"] == g) for g in grupos]
        grafico_barras(panel_contenido, grupos, cantidades, "Distribución de alumnos por grupo").pack(fill="x", pady=5)
        grafico_dona(panel_contenido, [total_presentes, total_faltas, total_retardos],
                     ["Presentes", "Faltas", "Retardos"], [MENTA_OSCURO, CORAL, DORADO]).pack(fill="x", pady=8)
        crear_boton(panel_contenido, "＋  Registrar alumnos", mostrar_registro_alumnos).pack(fill="x", pady=8)

def mostrar_usuarios():
    if rol_actual != "director": return
    preparar_pagina("Usuarios y Contraseñas", "Cada docente entra y automaticamente ve solo su grupo asignado.")
    tabla = crear_tabla(panel_contenido, ("usuario","contrasena","grupo","nombre"), ("Usuario","Contraseña","Grupo Asignado","Nombre Real"), altura=8)
    for u, d in USUARIOS_DOCENTES.items():
        tabla.insert("", "end", values=(u, d["pass"], d["grupo"], d["nombre_real"]))
    tabla2 = crear_tabla(panel_contenido, ("usuario","contrasena","rol"), ("Usuario Director","Contraseña","Rol"), altura=2)
    tabla2.insert("", "end", values=(USUARIO_DIRECTOR, CONTRASENA_DIRECTOR, "Director - Ve todo"))
    def exportar_usuarios():
        lineas = ["USUARIOS DEL SISTEMA DE ASISTENCIA\n"]
        for u, d in USUARIOS_DOCENTES.items():
            lineas.append(f"Usuario: {u} | Pass: {d['pass']} | Grupo: {d['grupo']} | Nombre: {d['nombre_real']}")
        lineas.append(f"\nDirector: {USUARIO_DIRECTOR} | Pass: {CONTRASENA_DIRECTOR}")
        exportar_txt("usuarios_y_contrasenas.txt", "\n".join(lineas))
    crear_boton(panel_contenido, "Exportar usuarios a TXT", exportar_usuarios).pack(fill="x", pady=12)

def mostrar_registro_alumnos():
    if rol_actual != "director":
        messagebox.showwarning("Permisos", "Solo el director puede registrar alumnos."); return
    preparar_pagina("Registrar alumnos", "Asigna cada alumno a un grupo de 1° a 6°. Ese grupo le aparecera a su docente.")
    form = tk.Frame(panel_contenido, bg=BLANCO, padx=22, pady=22, highlightbackground=GRIS_BORDE, highlightthickness=1)
    form.pack(fill="x", pady=(0, 20))
    tk.Label(form, text="Nombre completo del alumno:", bg=BLANCO, fg=TEXTO, font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))
    en = tk.Entry(form, font=("Arial", 11), relief="solid", bd=1)
    en.grid(row=1, column=0, columnspan=2, sticky="ew", ipady=8, pady=(0, 16))
    tk.Label(form, text="Grupo asignado:", bg=BLANCO, fg=TEXTO, font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(0, 8))
    eg = ttk.Combobox(form, values=["1°","2°","3°","4°","5°","6°"], state="readonly", font=("Arial", 11))
    eg.grid(row=3, column=0, columnspan=2, sticky="ew", ipady=4, pady=(0, 20))
    eg.set("1°")
    form.grid_columnconfigure(0, weight=1)
    tabla = crear_tabla(panel_contenido, ("nombre","grupo"), ("Nombre del Alumno","Grupo Asignado"), altura=10)
    def act():
        tabla.delete(*tabla.get_children())
        for a in alumnos_ordenados(): tabla.insert("", "end", values=(a["nombre"], a["grupo"]))
    def guardar():
        n=en.get().strip(); g=eg.get().strip()
        if not n or not g:
            messagebox.showwarning("Campos incompletos", "Escribe el nombre completo y el grupo."); return
        existe = any(a["nombre"].casefold()==n.casefold() and a["grupo"]==g for a in alumnos)
        if existe:
            messagebox.showwarning("Alumno existente", "Ese alumno ya está registrado en ese grupo."); return
        alumnos.append({"nombre": n, "grupo": g})
        guardar_base_datos()
        en.delete(0,"end"); act()
        messagebox.showinfo("Registro exitoso", f"{n} asignado a {g} correctamente.")
    crear_boton(form, "Guardar y asignar a docente", guardar).grid(row=4, column=0, columnspan=2, sticky="ew")
    act()

def mostrar_asistencia():
    if rol_actual != "docente":
        messagebox.showwarning("Permisos", "Solo docentes pueden pasar lista."); return
    preparar_pagina(f"Registrar asistencia - Grupo {grupo_actual}", f"Marca Presente, Falta o Retardo para alumnos de {grupo_actual}.")
    controles = tk.Frame(panel_contenido, bg=BLANCO, padx=18, pady=14, highlightbackground=GRIS_BORDE, highlightthickness=1)
    controles.pack(fill="x", pady=(0, 14))
    tk.Label(controles, text="Fecha (DD/MM/AAAA):", bg=BLANCO, font=("Arial", 10, "bold")).pack(side="left", padx=(0, 8))
    entrada_fecha = tk.Entry(controles, width=14, font=("Arial", 11), relief="solid", bd=1)
    entrada_fecha.insert(0, fecha_hoy())
    entrada_fecha.pack(side="left", padx=(0, 20), ipady=5)
    tk.Label(controles, text="Buscar:", bg=BLANCO, font=("Arial", 10, "bold")).pack(side="left", padx=(0, 8))
    busqueda = tk.Entry(controles, width=22, font=("Arial", 11), relief="solid", bd=1)
    busqueda.pack(side="left", ipady=5)
    marco_tabla = tk.Frame(panel_contenido, bg=BLANCO, padx=12, pady=12, highlightbackground=GRIS_BORDE, highlightthickness=1)
    marco_tabla.pack(fill="both", expand=True, pady=(0, 14))
    lienzo = tk.Canvas(marco_tabla, bg=BLANCO, highlightthickness=0, height=380)
    barra = ttk.Scrollbar(marco_tabla, orient="vertical", command=lienzo.yview)
    lienzo.configure(yscrollcommand=barra.set)
    barra.pack(side="right", fill="y")
    lienzo.pack(side="left", fill="both", expand=True)
    interior = tk.Frame(lienzo, bg=BLANCO)
    vi = lienzo.create_window((0, 0), window=interior, anchor="nw")
    interior.bind("<Configure>", lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))
    lienzo.bind("<Configure>", lambda e: lienzo.itemconfigure(vi, width=e.width))
    encabezado = tk.Frame(interior, bg=GUINDA)
    encabezado.pack(fill="x", pady=(0, 4))
    for col, peso in enumerate([5, 1, 1, 1]): encabezado.grid_columnconfigure(col, weight=peso, minsize=70 if col else 200)
    for col, txt in enumerate(["Nombre completo", "Presente", "Falta", "Retardo"]):
        tk.Label(encabezado, text=txt, bg=GUINDA, fg=BLANCO, font=("Arial", 10, "bold"), padx=6, pady=12).grid(row=0, column=col, sticky="nsew")
    variables = {}
    def construir_filas():
        for w in interior.winfo_children():
            if w is not encabezado: w.destroy()
        variables.clear()
        texto_busqueda = busqueda.get().strip().casefold()
        lista = [a for a in alumnos_de_mi_grupo() if texto_busqueda in a["nombre"].casefold()]
        if not lista:
            tk.Label(interior, text=f"No hay alumnos en {grupo_actual}.", bg=BLANCO, fg=TEXTO, pady=20, font=("Arial", 11)).pack(fill="x"); return
        for idx, a in enumerate(lista):
            clave = (a["nombre"], a["grupo"])
            cf = BLANCO if idx % 2 == 0 else "#F8F1F1"
            fila = tk.Frame(interior, bg=cf)
            fila.pack(fill="x", pady=2)
            for c, p in enumerate([5, 1, 1, 1]): fila.grid_columnconfigure(c, weight=p, minsize=70 if c else 200)
            faltas = contar_faltas(a["nombre"], a["grupo"])
            nivel, color_alerta, color_texto = nivel_alerta(faltas)
            texto_nombre = f'{a["nombre"]}  |  Faltas: {faltas}'
            tk.Label(fila, text=texto_nombre, bg=color_alerta if faltas else cf,
                     fg=color_texto if faltas else TEXTO, anchor="w", wraplength=300,
                     padx=8, pady=10, font=("Arial", 10, "bold" if faltas else "normal")).grid(row=0, column=0, sticky="nsew")
            var = tk.StringVar(value="Sin marcar"); variables[clave] = var
            for c, est in enumerate(["Presente", "Falta", "Retardo"], start=1):
                tk.Radiobutton(fila, variable=var, value=est, bg=cf, activebackground=cf, selectcolor="#E9D2D2", cursor="hand2").grid(row=0, column=c, sticky="nsew")
    def cargar_existentes():
        try: fecha = datetime.strptime(entrada_fecha.get().strip(), "%d/%m/%Y").strftime("%d/%m/%Y")
        except: return
        for clave, var in variables.items():
            enc = next((r for r in reversed(registros) if r["fecha"]==fecha and r["nombre"]==clave[0] and r["grupo"]==clave[1]), None)
            var.set(enc["estado"] if enc else "Sin marcar")
    def guardar_asistencia():
        try: fecha = datetime.strptime(entrada_fecha.get().strip(), "%d/%m/%Y").strftime("%d/%m/%Y")
        except:
            messagebox.showerror("Fecha invalida", "Usa el formato DD/MM/AAAA."); return
        if not variables:
            messagebox.showwarning("Sin alumnos", "No hay alumnos en tu grupo."); return
        sin = sum(v.get()=="Sin marcar" for v in variables.values())
        if sin and not messagebox.askyesno("Incompleto", f"Hay {sin} sin marcar. ¿Continuar?"): return
        guard=0
        for clave, var in variables.items():
            est=var.get()
            if est=="Sin marcar": continue
            registros[:] = [r for r in registros if not (r["fecha"]==fecha and r["nombre"]==clave[0] and r["grupo"]==clave[1])]
            registros.append({"fecha": fecha, "nombre": clave[0], "grupo": clave[1], "estado": est, "docente": usuario_actual})
            guard+=1
        if guard > 0:
            guardar_base_datos()
        if guard==0: messagebox.showwarning("Sin marcar", "Marca al menos uno."); return
        messagebox.showinfo("Guardado", f"Asistencia de {guard} alumnos de {grupo_actual} guardada.")
    busqueda.bind("<KeyRelease>", lambda e: (construir_filas(), cargar_existentes()))
    entrada_fecha.bind("<FocusOut>", lambda e: cargar_existentes())
    acciones = tk.Frame(panel_contenido, bg=FONDO); acciones.pack(fill="x", pady=(0, 14))
    crear_boton(acciones, "Todos presentes", lambda: [v.set("Presente") for v in variables.values()]).pack(side="left", padx=(0, 10))
    crear_boton(acciones, "Limpiar", lambda: [v.set("Sin marcar") for v in variables.values()], color="#666666").pack(side="left")
    crear_boton(panel_contenido, f"Guardar asistencia {grupo_actual}", guardar_asistencia).pack(fill="x", pady=(0, 10))
    construir_filas(); cargar_existentes()

def mostrar_incidencias():
    if rol_actual != "docente":
        messagebox.showwarning("Permisos", "Solo docentes."); return
    preparar_pagina(f"Registrar incidencias - Grupo {grupo_actual}", f"Solo incidencias de tu grupo {grupo_actual}.")
    if not alumnos_de_mi_grupo():
        tk.Label(panel_contenido, text=f"No hay alumnos en {grupo_actual}. Pide al director que registre.", bg=FONDO).pack(anchor="w"); return
    form = tk.Frame(panel_contenido, bg=BLANCO, padx=22, pady=22, highlightbackground=GRIS_BORDE, highlightthickness=1)
    form.pack(fill="x", pady=(0, 18))
    tk.Label(form, text="Alumno:", bg=BLANCO, font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=6)
    ops = [f'{a["nombre"]} | {a["grupo"]}' for a in alumnos_de_mi_grupo()]
    sel = ttk.Combobox(form, values=ops, state="readonly", font=("Arial", 11)); sel.grid(row=0, column=1, sticky="ew", padx=8, pady=6); sel.current(0)
    tk.Label(form, text="Descripción:", bg=BLANCO, font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="nw", pady=6)
    desc = tk.Text(form, height=4, wrap="word", relief="solid", bd=1, font=("Arial", 11)); desc.grid(row=1, column=1, sticky="ew", padx=8, pady=6)
    form.grid_columnconfigure(1, weight=1)
    tabla = crear_tabla(panel_contenido, ("fecha","nombre","grupo","descripcion"), ("Fecha","Alumno","Grupo","Descripción"), altura=8)
    def act():
        tabla.delete(*tabla.get_children())
        for inc in reversed([i for i in incidencias if i["grupo"]==grupo_actual]):
            tabla.insert("", "end", values=(inc["fecha"], inc["nombre"], inc["grupo"], inc["descripcion"]))
    def guardar():
        txt=desc.get("1.0","end").strip()
        if not sel.get() or not txt:
            messagebox.showwarning("Incompleto", "Selecciona alumno y escribe incidencia."); return
        n,g=sel.get().split(" | ",1)
        incidencias.append({"fecha": fecha_hoy(), "nombre": n, "grupo": g, "descripcion": txt, "docente": usuario_actual})
        guardar_base_datos()
        desc.delete("1.0","end"); act()
        messagebox.showinfo("Guardado", "Incidencia registrada.")
    crear_boton(form, "Guardar incidencia", guardar).grid(row=2, column=0, columnspan=2, sticky="ew", pady=12)
    act()

def mostrar_reporte_general():
    if rol_actual != "director": return
    preparar_pagina("Reporte general - Dirección", "Vista resumida de los seis grupos y actividad escolar.")
    datos = [("Alumnos", len(alumnos), GUINDA, "♟"), ("Registros", len(registros), MENTA_OSCURO, "✓"),
             ("Incidencias", len(incidencias), "#8A75B5", "✎"), ("Cartas compromiso", len(cartas_compromiso), "#B36A16", "▤")]
    tarjetas = tk.Frame(panel_contenido, bg=FONDO); tarjetas.pack(fill="x", pady=5)
    for i, dato in enumerate(datos):
        tarjeta_color(tarjetas, *dato).grid(row=0, column=i, sticky="nsew", padx=5)
        tarjetas.grid_columnconfigure(i, weight=1)
    grupos = ["1°", "2°", "3°", "4°", "5°", "6°"]
    cantidades = [sum(1 for a in alumnos if a["grupo"] == g) for g in grupos]
    grafico_barras(panel_contenido, grupos, cantidades, "Cantidad de alumnos por grado").pack(fill="x", pady=12)
    tabla = crear_tabla(panel_contenido, ("grupo", "alumnos", "faltas", "retardos"),
                        ("Grupo", "Alumnos", "Faltas acumuladas", "Retardos acumulados"), altura=7)
    for g in grupos:
        lista = [a for a in alumnos if a["grupo"] == g]
        faltas = sum(1 for r in registros if r["grupo"] == g and r["estado"] == "Falta")
        retardos = sum(1 for r in registros if r["grupo"] == g and r["estado"] == "Retardo")
        tabla.insert("", "end", values=(g, len(lista), faltas, retardos))

def mostrar_carga_masiva():
    if rol_actual != "director":
        messagebox.showwarning("Permisos", "Solo el director puede acceder a la carga masiva.")
        return
    preparar_pagina("Carga masiva desde Excel",
                    "Agrega muchos alumnos a la base de datos MySQL mediante un archivo .xlsx.")

    tarjeta = tk.Frame(panel_contenido, bg=BLANCO, padx=22, pady=22,
                       highlightbackground=GRIS_BORDE, highlightthickness=1)
    tarjeta.pack(fill="x", pady=(0, 16))
    tk.Label(tarjeta, text="¿Cómo preparar tu archivo?", bg=BLANCO, fg=GUINDA,
             font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
    instrucciones = (
        "1. Descarga la plantilla de Excel.\n"
        "2. En la hoja 'Alumnos', escribe un alumno por fila.\n"
        "3. Usa las columnas nombre y grupo.\n"
        "4. En grupo puedes escribir 1°, 2°, 3°, 4°, 5°, 6° o solamente el número.\n"
        "5. Guarda el archivo y selecciona 'Importar Excel'."
    )
    tk.Label(tarjeta, text=instrucciones, bg=BLANCO, fg=TEXTO,
             font=("Arial", 10), justify="left", anchor="w").pack(fill="x", pady=(0, 16))

    botones = tk.Frame(tarjeta, bg=BLANCO)
    botones.pack(fill="x")
    crear_boton(botones, "Descargar plantilla Excel", descargar_plantilla_excel).pack(side="left", padx=(0, 10), pady=4)
    crear_boton(botones, "Importar archivo Excel", importar_alumnos_excel, color="#287A43").pack(side="left", pady=4)

    tk.Label(panel_contenido,
             text="Importante: la importación no elimina alumnos existentes. Los registros repetidos del mismo nombre y grupo se omiten automáticamente.",
             bg=FONDO, fg="#666666", font=("Arial", 9), wraplength=760,
             justify="left").pack(anchor="w", pady=(4, 12))


def mostrar_lista_alumnos():
    if rol_actual != "director": return
    preparar_pagina("Lista de alumnos", "Consulta de todos los grupos.")
    tabla = crear_tabla(panel_contenido, ("nombre","grupo","faltas","alerta"),
                        ("Nombre completo","Grupo","Total de faltas","Nivel de alerta"), altura=15)
    tabla.tag_configure("amarillo", background="#FFF2B3", foreground="#6F5900")
    tabla.tag_configure("naranja", background="#FFE0BD", foreground="#8A4300")
    tabla.tag_configure("rojo", background="#FFD6D6", foreground="#900000")
    tabla.tag_configure("normal", background=BLANCO, foreground=TEXTO)
    for a in alumnos_ordenados():
        faltas = contar_faltas(a["nombre"], a["grupo"])
        nivel, _, _ = nivel_alerta(faltas)
        tag = {"Amarillo":"amarillo", "Naranja":"naranja", "Rojo":"rojo"}.get(nivel, "normal")
        tabla.insert("", "end", values=(a["nombre"], a["grupo"], faltas, nivel), tags=(tag,))

def mostrar_kpis():
    if rol_actual != "director": return
    preparar_pagina("Indicadores KPI de asistencia",
                    "Resumen general y alertas por número acumulado de faltas.")
    total_alumnos = len(alumnos)
    total_presentes = sum(r["estado"] == "Presente" for r in registros)
    total_faltas = sum(r["estado"] == "Falta" for r in registros)
    total_retardos = sum(r["estado"] == "Retardo" for r in registros)
    alumnos_amarillos = alumnos_naranjas = alumnos_rojos = 0
    for a in alumnos:
        n = contar_faltas(a["nombre"], a["grupo"])
        if n == 1: alumnos_amarillos += 1
        elif 2 <= n <= 3: alumnos_naranjas += 1
        elif n > 3: alumnos_rojos += 1

    tarjetas = [
        ("Alumnos registrados", total_alumnos, "#800000"),
        ("Asistencias registradas", total_presentes, "#287A43"),
        ("Faltas acumuladas", total_faltas, "#C62828"),
        ("Retardos", total_retardos, "#A65300"),
        ("Alertas amarillas", alumnos_amarillos, "#8A6D00"),
        ("Alertas naranjas", alumnos_naranjas, "#C66A00"),
        ("Alertas rojas", alumnos_rojos, "#C62828"),
    ]
    marco = tk.Frame(panel_contenido, bg=FONDO)
    marco.pack(fill="x", pady=5)
    for i, (titulo, valor, color) in enumerate(tarjetas):
        tarjeta = tk.Frame(marco, bg=BLANCO, padx=16, pady=15,
                           highlightbackground=GRIS_BORDE, highlightthickness=1)
        tarjeta.grid(row=i//2, column=i%2, sticky="nsew", padx=6, pady=6)
        tk.Label(tarjeta, text=titulo, bg=BLANCO, fg=TEXTO,
                 font=("Arial", 10, "bold"), wraplength=220).pack(anchor="w")
        tk.Label(tarjeta, text=str(valor), bg=BLANCO, fg=color,
                 font=("Arial", 25, "bold")).pack(anchor="w", pady=(5,0))
    marco.grid_columnconfigure(0, weight=1)
    marco.grid_columnconfigure(1, weight=1)

    grafico_dona(panel_contenido, [total_presentes, total_faltas, total_retardos],
                 ["Presentes", "Faltas", "Retardos"], [MENTA_OSCURO, CORAL, DORADO],
                 "Distribución de registros de asistencia").pack(fill="x", pady=12)
    grupos_graf = ["1°", "2°", "3°", "4°", "5°", "6°"]
    faltas_graf = [sum(1 for r in registros if r["grupo"] == g and r["estado"] == "Falta") for g in grupos_graf]
    grafico_barras(panel_contenido, grupos_graf, faltas_graf,
                   "Faltas registradas por grupo", [CORAL, "#D77A65", DORADO, "#B78AC9", "#8D9BCB", "#7FAF9A"]).pack(fill="x", pady=8)

    tk.Label(panel_contenido, text="Porcentaje de asistencia por grupo",
             bg=FONDO, fg=GUINDA, font=("Arial", 14, "bold")).pack(anchor="w", pady=(18,8))
    tabla = crear_tabla(panel_contenido, ("grupo","alumnos","presentes","faltas","retardos","porcentaje"),
                        ("Grupo","Alumnos","Presentes","Faltas","Retardos","Asistencia %"), altura=7)
    for grupo in ["1°","2°","3°","4°","5°","6°"]:
        lista = [a for a in alumnos if a["grupo"] == grupo]
        regs = [r for r in registros if r["grupo"] == grupo]
        presentes = sum(r["estado"] == "Presente" for r in regs)
        faltas_g = sum(r["estado"] == "Falta" for r in regs)
        retardos = sum(r["estado"] == "Retardo" for r in regs)
        total = len(regs)
        porcentaje = (presentes / total * 100) if total else 0
        tabla.insert("", "end", values=(grupo, len(lista), presentes, faltas_g,
                                        retardos, f"{porcentaje:.1f}%"))

    tk.Label(panel_contenido, text="Alumnos que requieren seguimiento",
             bg=FONDO, fg=GUINDA, font=("Arial", 14, "bold")).pack(anchor="w", pady=(12,0))
    alertas = crear_tabla(panel_contenido, ("nombre","grupo","faltas","nivel"),
                          ("Alumno","Grupo","Faltas","Alerta"), altura=8)
    alertas.tag_configure("amarillo", background="#FFF2B3", foreground="#6F5900")
    alertas.tag_configure("naranja", background="#FFE0BD", foreground="#8A4300")
    alertas.tag_configure("rojo", background="#FFD6D6", foreground="#900000")
    for a in alumnos_ordenados():
        faltas = contar_faltas(a["nombre"], a["grupo"])
        nivel, _, _ = nivel_alerta(faltas)
        if faltas:
            tag = {"Amarillo":"amarillo", "Naranja":"naranja", "Rojo":"rojo"}.get(nivel)
            alertas.insert("", "end", values=(a["nombre"], a["grupo"], faltas, nivel), tags=(tag,))
    if not any(contar_faltas(a["nombre"],a["grupo"]) for a in alumnos):
        tk.Label(panel_contenido, text="No hay alumnos con faltas registradas.",
                 bg=FONDO, fg="#287A43", font=("Arial", 10, "bold")).pack(anchor="w", pady=8)

def mostrar_reportes_completos():
    if rol_actual != "director": return
    preparar_pagina("Reportes completos", "Historial de asistencia e incidencias de todos los docentes.")
    tk.Label(panel_contenido, text="Asistencia", bg=FONDO, fg=GUINDA, font=("Arial", 13, "bold")).pack(anchor="w", pady=(10, 0))
    tabla_a = crear_tabla(panel_contenido, ("fecha","nombre","grupo","estado","docente"), ("Fecha","Alumno","Grupo","Estado","Docente"), altura=7)
    for r in reversed(registros): tabla_a.insert("", "end", values=(r["fecha"], r["nombre"], r["grupo"], r["estado"], r["docente"]))
    tk.Label(panel_contenido, text="Incidencias", bg=FONDO, fg=GUINDA, font=("Arial", 13, "bold")).pack(anchor="w", pady=(14, 0))
    tabla_i = crear_tabla(panel_contenido, ("fecha","nombre","grupo","descripcion"), ("Fecha","Alumno","Grupo","Descripción"), altura=7)
    for inc in reversed(incidencias): tabla_i.insert("", "end", values=(inc["fecha"], inc["nombre"], inc["grupo"], inc["descripcion"]))

def mostrar_cartas():
    if rol_actual != "director": return
    preparar_pagina("Cartas compromiso para tutor", "Genera cartas para cualquier grupo.")
    if not alumnos:
        tk.Label(panel_contenido, text="No hay alumnos registrados.", bg=FONDO).pack(anchor="w"); return
    form = tk.Frame(panel_contenido, bg=BLANCO, padx=22, pady=22, highlightbackground=GRIS_BORDE, highlightthickness=1)
    form.pack(fill="x", pady=(0, 18))
    tk.Label(form, text="Alumno:", bg=BLANCO, font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=6)
    ops=[f'{a["nombre"]} | {a["grupo"]}' for a in alumnos_ordenados()]
    sel=ttk.Combobox(form, values=ops, state="readonly", font=("Arial", 11)); sel.grid(row=0, column=1, sticky="ew", padx=8, pady=6); sel.current(0)
    tk.Label(form, text="Nombre del tutor:", bg=BLANCO, font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=6)
    et=tk.Entry(form, font=("Arial", 11), relief="solid", bd=1); et.grid(row=1, column=1, sticky="ew", padx=8, pady=6, ipady=4)
    tk.Label(form, text="Motivo:", bg=BLANCO, font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="nw", pady=6)
    em=tk.Text(form, height=4, wrap="word", relief="solid", bd=1, font=("Arial", 11)); em.grid(row=2, column=1, sticky="ew", padx=8, pady=6)
    form.grid_columnconfigure(1, weight=1)
    tabla=crear_tabla(panel_contenido, ("fecha","nombre","grupo","tutor"), ("Fecha","Alumno","Grupo","Tutor"), altura=7)
    def act():
        tabla.delete(*tabla.get_children())
        for c in reversed(cartas_compromiso): tabla.insert("", "end", values=(c["fecha"], c["nombre"], c["grupo"], c["tutor"]))
    def gen():
        if not sel.get(): return
        tut=et.get().strip(); mot=em.get("1.0","end").strip()
        if not tut or not mot: messagebox.showwarning("Incompleto", "Escribe tutor y motivo"); return
        n,g=sel.get().split(" | ",1)
        contenido = (f"CARTA COMPROMISO PARA TUTOR\nSISTEMA DE ASISTENCIA ESCOLAR\n\nFecha: {fecha_hoy()}\nNombre del alumno: {n}\nGrupo: {g}\nNombre del tutor: {tut}\n\nMotivo:\n{mot}\n\nFirma del tutor: __________________________\n\nFirma de dirección: _______________________\n")
        cartas_compromiso.append({"fecha": fecha_hoy(), "nombre": n, "grupo": g, "tutor": tut, "contenido": contenido})
        guardar_base_datos()
        act(); exportar_txt(f"carta_compromiso_{n.replace(' ', '_')}.txt", contenido)
    crear_boton(form, "Generar y guardar carta", gen).grid(row=3, column=0, columnspan=2, sticky="ew", pady=12)
    act()

def centrar_ventana():
    root.update_idletasks()
    w=min(1120, root.winfo_screenwidth()); h=min(720, root.winfo_screenheight())
    x=max(0,(root.winfo_screenwidth()-w)//2); y=max(0,(root.winfo_screenheight()-h)//2)
    root.geometry(f"{w}x{h}+{x}+{y}")

root.state('zoomed')
centrar_ventana()
mostrar_login()
root.mainloop()
# SARAHI ANGELES MARTINEZ SUBE PROYECTO
# ADRIANA CIPRIANO CRUZ AGREGÓ EL CRUD DE CARTA COMPROMISO
# ERIK RAMIREZ MONTOYA AGREGA TABLA DE USUARIOS Y ASISTENCIAS 
'''
1.- Falta agregar o mejorar diseño en el login
2.- Como directivo: como le hago para editar o borrar la información de los alumnos o docentes ?, ya que no hay un boton de editar y eliminar
3.- Al director le hace falta la sección de notificaciones y alertas
4.- Al pasar lista como docente, el boton de guardar asistencia no funciona, no guarda la información de los alumnos en la base de datos
5.- Revisar el diseño de los botones, ya que no se ve muy bien el diseño de los botones, pero el tamaño no es uniforme (es muy grande).
'''

'''
CREATE DATABASE ASISTENCIA_ESCOLAR;
USE ASISTENCIA_ESCOLAR;

CREATE TABLE USUARIOS (
    ID_USUARIO INT PRIMARY KEY,
    USUARIO VARCHAR(30),
    CONTRASENA VARCHAR(30),
    ROL VARCHAR(15)
);

CREATE TABLE ASISTENCIAS (
    ID_ASISTENCIA INT PRIMARY KEY,
    ALUMNO VARCHAR(50),
    GRUPO VARCHAR(15),
    FECHA VARCHAR(15),
    ESTADO VARCHAR(15),
    DOCENTE VARCHAR(30)
);
'''

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime

USUARIOS_DOCENTES = {
    "profe.maria":  {"pass": "Maria1",  "grupo": "1°", "nombre_real": "Profa. Maria Lopez - 1° Grado"},
    "profe.juan":   {"pass": "Juan2",   "grupo": "2°", "nombre_real": "Profe. Juan Perez - 2° Grado"},
    "profe.ana":    {"pass": "Ana3",    "grupo": "3°", "nombre_real": "Profra. Ana Torres - 3° Grado"},
    "profe.carlos": {"pass": "Carlos4", "grupo": "4°", "nombre_real": "Profe. Carlos Ruiz - 4° Grado"},
    "profe.laura":  {"pass": "Laura5",  "grupo": "5°", "nombre_real": "Profra. Laura Gomez - 5° Grado"},
    "profe.luis":   {"pass": "Luis6",   "grupo": "6°", "nombre_real": "Profe. Luis Hernandez - 6° Grado"},
}
USUARIO_DIRECTOR = "director"
CONTRASENA_DIRECTOR = "Director123"

# CREATE TABLE INCIDENCIAS(
#ID INT PRIMARY KEY NOT NULL, nombre_alumno VARCHAR(50), Fecha VARCHAR(30), Hora int, Situación VARCHAR(100);


GUINDA = "#800000"
GUINDA_OSCURO = "#5c0000"
BLANCO = "#FFFFFF"
FONDO = "#F5F5F5"
TEXTO = "#292929"
GRIS_BORDE = "#292929"

alumnos = []
registros = []
incidencias = []
cartas_compromiso = []

usuario_actual = ""
rol_actual = ""
grupo_actual = ""
nombre_real_actual = ""

root = tk.Tk()
root.title("Sistema de Asistencia Escolar - 6 Grupos")
root.geometry("1120x720")
root.minsize(900, 600)
root.configure(bg=FONDO)
panel_contenido = None

estilo = ttk.Style()
estilo.theme_use("clam")
estilo.configure("Treeview",
background=BLANCO,
foreground=TEXTO, 
rowheight=32, 
fieldbackground=BLANCO, 
font=("Arial", 10))
estilo.configure("Treeview.Heading", 
background=GUINDA, 
foreground=BLANCO, 
font=("Arial", 10, "bold"))

def fecha_hoy(): return date.today().strftime("%d/%m/%Y")
def limpiar_ventana():
    for w in root.winfo_children(): w.destroy()
def crear_boton(parent, texto, comando, color=GUINDA):
    return tk.Button(parent, 
    text=texto, 
    command=comando, 
    bg=color, 
    fg=BLANCO, 
    activebackground=GUINDA_OSCURO, 
    activeforeground=BLANCO, 
    relief="flat", 
    cursor="hand2", 
    font=("Arial", 10, "bold"), 
    padx=18, 
    pady=10, 
    bd=0)
def preparar_pagina(titulo, subtitulo=""):
    for w in panel_contenido.winfo_children(): w.destroy()
    tk.Label(panel_contenido, 
    text=titulo, 
    bg=FONDO, 
    fg=GUINDA, 
    font=("Arial", 22, "bold"), 
    wraplength=800, 
    justify="left").pack(anchor="w", pady=(0, 6))
    if subtitulo:
        tk.Label(panel_contenido, 
        text=subtitulo, 
        bg=FONDO, 
        fg="#666666", 
        font=("Arial", 11), 
        wraplength=800, 
        justify="left").pack(anchor="w", pady=(0, 20))
    else:
        tk.Frame(panel_contenido, height=12, bg=FONDO).pack()
def crear_tabla(parent, columnas, encabezados, altura=10):
    contenedor = tk.Frame(parent, 
    bg=BLANCO, 
    padx=12, 
    pady=12, 
    highlightbackground=GRIS_BORDE, 
    highlightthickness=1)
    contenedor.pack(fill="both", 
    expand=True, 
    pady=(8, 18))
    tabla = ttk.Treeview(contenedor, 
    columns=columnas, 
    show="headings", 
    height=altura)
    for c, t in zip(columnas, encabezados):
        tabla.heading(c, text=t)
        tabla.column(c, width=160, anchor="w")
    sy = ttk.Scrollbar(contenedor, 
    orient="vertical", 
    command=tabla.yview)
    sx = ttk.Scrollbar(contenedor, 
    orient="horizontal", 
    command=tabla.xview)
    tabla.configure(yscrollcommand=sy.set, 
    xscrollcommand=sx.set)
    tabla.grid(row=0, 
    column=0, 
    sticky="nsew")
    sy.grid(row=0, 
    column=1, 
    sticky="ns")
    sx.grid(row=1, 
    column=0, 
    sticky="ew")
    contenedor.grid_rowconfigure(0, weight=1)
    contenedor.grid_columnconfigure(0, weight=1)
    return tabla
def exportar_txt(nombre, contenido):
    ruta = filedialog.asksaveasfilename(title="Guardar archivo", 
    defaultextension=".txt", 
    initialfile=nombre, 
    filetypes=[("Archivo de texto", "*.txt")])
    if not ruta: return
    try:
        with open(ruta, "w", encoding="utf-8") as archivo: archivo.write(contenido)
        messagebox.showinfo("Guardado", 
        "Archivo guardado correctamente.")
    except OSError as e: messagebox.showerror("Error", 
    f"No se pudo guardar:\n{e}")
def alumnos_ordenados(): return sorted(alumnos, 
key=lambda a: (a["grupo"].lower(), a["nombre"].lower()))
def alumnos_de_mi_grupo():
    if rol_actual == "director": return alumnos_ordenados()
    return [a for a in alumnos_ordenados() if a["grupo"] == grupo_actual]

def mostrar_login():
    limpiar_ventana()
    marco_fondo = tk.Frame(root, 
    bg=FONDO)
    marco_fondo.pack(fill="both", 
    expand=True, 
    padx=80, 
    pady=80)
    cont = tk.Frame(marco_fondo, 
    bg=BLANCO, 
    padx=150, 
    pady=150, 
    highlightbackground=GRIS_BORDE, 
    highlightthickness=1)
    cont.place(relx=0.5, 
    rely=0.5, 
    anchor="center")
    tk.Label(cont, 
    text="SISTEMA DE\nASISTENCIA ESCOLAR", 
    bg=BLANCO, 
    fg=GUINDA, 
    font=("Arial", 20, "bold"), 
    justify="center").pack(pady=(0, 8))
    tk.Label(cont, 
    text="6 Docentes - 1° a 6° Grado", 
    bg=BLANCO, 
    fg="#777777", 
    font=("Arial", 11)).pack(pady=(0, 25))
    tk.Label(cont, 
    text="Usuario", 
    bg=BLANCO, 
    fg=TEXTO, 
    font=("Arial", 15, "bold")).pack(anchor="w", pady=(0, 4))
    eu = tk.Entry(cont, 
    width=40, 
    font=("Arial", 12), 
    relief="solid", 
    bd=1)
    eu.pack(ipady=8, 
    pady=(0, 16), 
    fill="x")
    tk.Label(cont, 
    text="Contraseña", 
    bg=BLANCO, 
    fg=TEXTO, 
    font=("Arial", 15, "bold")).pack(anchor="w", pady=(0, 4))
    ec = tk.Entry(cont, 
    show="*", 
    width=40, 
    font=("Arial", 12), 
    relief="solid", 
    bd=1)
    ec.pack(ipady=8, 
    pady=(0, 24), 
    fill="x")
    def ingresar(event=None):
        global usuario_actual, rol_actual, grupo_actual, nombre_real_actual
        u = eu.get().strip(); p = ec.get()
        if u in USUARIOS_DOCENTES and USUARIOS_DOCENTES[u]["pass"] == p:
            usuario_actual = u; rol_actual = "docente"
            grupo_actual = USUARIOS_DOCENTES[u]["grupo"]
            nombre_real_actual = USUARIOS_DOCENTES[u]["nombre_real"]
            mostrar_sistema()
        elif u == USUARIO_DIRECTOR and p == CONTRASENA_DIRECTOR:
            usuario_actual = u; rol_actual = "director"; grupo_actual = "TODOS"; nombre_real_actual = "Director General"
            mostrar_sistema()
        else:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.\nEj: profe.maria / Maria1")
    crear_boton(cont, 
    "  Iniciar sesión  ", 
    ingresar).pack(fill="x", ipady=2)
    tk.Label(cont, 
    text="Ej: profe.fernanda / Fernada1  |  director / Director143", 
    bg=BLANCO, 
    fg="#999999", 
    font=("Arial", 8)).pack(pady=(16, 0))
    eu.focus_set(); ec.bind("<Return>", ingresar)

def mostrar_sistema():
    global panel_contenido
    limpiar_ventana()
    princ = tk.Frame(root, 
    bg=FONDO); princ.pack(fill="both", expand=True)
    menu = tk.Frame(princ, 
    bg=GUINDA, 
    width=240, 
    padx=12, 
    pady=15); menu.pack(side="left", fill="y"); menu.pack_propagate(False)
    area = tk.Frame(princ, 
    bg=FONDO); area.pack(side="right", fill="both", expand=True)
    enc = tk.Frame(area, 
    bg=BLANCO, 
    padx=22, 
    pady=16, 
    highlightbackground=GRIS_BORDE, 
    highlightthickness=1); enc.pack(fill="x", padx=18, pady=18)
    tk.Label(enc, 
    text="Sistema de Asistencia Escolar", 
    bg=BLANCO, 
    fg=GUINDA, 
    font=("Arial", 16, "bold")).pack(anchor="w")
    tk.Label(enc, text=f"{nombre_real_actual}  •  Usuario: {usuario_actual}  •  Grupo: {grupo_actual}", bg=BLANCO, fg="#555555", font=("Arial", 10, "bold"), wraplength=700, justify="left").pack(anchor="w", pady=(6, 0))
    lienzo = tk.Canvas(area, 
    bg=FONDO, 
    highlightthickness=0); scroll = ttk.Scrollbar(area, orient="vertical", command=lienzo.yview)
    lienzo.configure(yscrollcommand=scroll.set); scroll.pack(side="right", fill="y"); lienzo.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=(0, 18))
    panel_contenido = tk.Frame(lienzo, 
    bg=FONDO, 
    padx=20, 
    pady=10)
    vp = lienzo.create_window((0, 0), 
    window=panel_contenido, 
    anchor="nw")
    panel_contenido.bind("<Configure>", 
    lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))
    lienzo.bind("<Configure>", 
    lambda e: lienzo.itemconfigure(vp, width=e.width))
    tk.Label(menu, 
    text="MENÚ", 
    bg=GUINDA, 
    fg=BLANCO, 
    font=("Arial", 18, "bold")).pack(pady=(10, 8), anchor="w", padx=8)
    tk.Label(menu, 
    text=f"GRUPO {grupo_actual}", 
    bg=GUINDA, 
    fg="#FFD6D6", 
    font=("Arial", 11, "bold")).pack(anchor="w", padx=8, pady=(0, 2))
    tk.Label(menu, 
    text=nombre_real_actual, 
    bg=GUINDA, 
    fg="white", 
    font=("Arial", 9), 
    wraplength=190, 
    justify="left").pack(anchor="w", padx=8, pady=(0, 20))
    if rol_actual == "docente":
        opciones = [("Inicio", mostrar_inicio), (f"Mi Grupo: {grupo_actual}", mostrar_asistencia), ("Incidencias", mostrar_incidencias)]
    else:
        opciones = [("Inicio", mostrar_inicio), ("Usuarios y Contraseñas", mostrar_usuarios), ("Registrar alumnos", mostrar_registro_alumnos), ("Lista de alumnos", mostrar_lista_alumnos), ("Reporte general", mostrar_reporte_general), ("Reportes completos", mostrar_reportes_completos), ("Cartas compromiso", mostrar_cartas)]
    for txt, fun in opciones:
        tk.Button(menu, 
        text=f"  {txt}", 
        command=fun, 
        bg=GUINDA, 
        fg=BLANCO, 
        activebackground=GUINDA_OSCURO, 
        activeforeground=BLANCO, 
        relief="flat", 
        anchor="w", 
        padx=10, 
        pady=12, 
        font=("Arial", 10, "bold"), 
        cursor="hand2", 
        bd=0).pack(fill="x", pady=4)
    tk.Frame(menu, 
    bg="#A34A4A", 
    height=1).pack(fill="x", pady=20, padx=8)
    crear_boton(menu, 
    "Cerrar sesión", 
    cerrar_sesion, 
    GUINDA_OSCURO).pack(fill="x", pady=8, padx=4)
    mostrar_inicio()

def cerrar_sesion():
    global usuario_actual, rol_actual, grupo_actual, nombre_real_actual
    if messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar sesión?"):
        usuario_actual = ""; rol_actual = ""; grupo_actual = ""; nombre_real_actual = ""; mostrar_login()

def mostrar_inicio():
    preparar_pagina(f"Inicio - {grupo_actual}", f"Bienvenido {nombre_real_actual}.")
    if rol_actual == "docente":
        card = tk.Frame(panel_contenido, 
        bg=BLANCO, 
        padx=24, 
        pady=24, 
        highlightbackground=GRIS_BORDE, 
        highlightthickness=1)
        card.pack(fill="x", 
        pady=(0, 18))
        tk.Label(card, 
        text=f"Grupo {grupo_actual}", 
        bg=BLANCO, 
        fg=GUINDA, 
        font=("Arial", 18, "bold")).pack(anchor="w")
        tk.Label(card, 
        text=f"Solo puedes ver y pasar lista a los alumnos del grupo {grupo_actual}.", 
        bg=BLANCO, 
        fg="#666666", 
        font=("Arial", 11), 
        wraplength=600, 
        justify="left").pack(anchor="w", pady=(8, 18))
        tk.Label(card, 
        text=str(len(alumnos_de_mi_grupo())), 
        bg=BLANCO, 
        fg=GUINDA, 
        font=("Arial", 36, "bold")).pack(anchor="w")
        tk.Label(card, 
        text="Alumnos en tu grupo", 
        bg=BLANCO, 
        fg=TEXTO, 
        font=("Arial", 11)).pack(anchor="w")
        crear_boton(panel_contenido, 
        f"Pasar lista {grupo_actual}", 
        mostrar_asistencia).pack(anchor="w", pady=10)
    else:
        tk.Label(panel_contenido, 
        text="Eres Director. Puedes registrar alumnos y ver usuarios de cada grado.", 
        bg=FONDO, 
        fg=TEXTO, 
        wraplength=700, 
        justify="left").pack(anchor="w", pady=(0, 18))
        grid = tk.Frame(panel_contenido, 
        bg=FONDO); grid.pack(fill="x", pady=8)
        for i, g in enumerate(["1°","2°","3°","4°","5°","6°"]):
            c = len([a for a in alumnos if a["grupo"] == g])
            col = tk.Frame(grid, 
            bg=BLANCO, 
            padx=18, 
            pady=18, 
            highlightbackground=GRIS_BORDE, 
            highlightthickness=1)
            col.grid(row=i//3, 
            column=i%3, 
            sticky="nsew", 
            padx=8, 
            pady=8)
            tk.Label(col, 
            text=g, 
            bg=BLANCO, 
            fg=GUINDA, 
            font=("Arial", 16, "bold")).pack(anchor="w")
            tk.Label(col, 
            text=f"{c} alumnos", 
            bg=BLANCO, 
            fg=TEXTO, 
            font=("Arial", 11)).pack(anchor="w", pady=(6,0))
        grid.grid_columnconfigure(0, 
        weight=1); grid.grid_columnconfigure(1, weight=1); grid.grid_columnconfigure(2, weight=1)

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
            tk.Label(fila, text=a["nombre"], bg=cf, fg=TEXTO, anchor="w", wraplength=260, padx=8, pady=10, font=("Arial", 10)).grid(row=0, column=0, sticky="nsew")
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
        desc.delete("1.0","end"); act()
        messagebox.showinfo("Guardado", "Incidencia registrada.")
    crear_boton(form, "Guardar incidencia", guardar).grid(row=2, column=0, columnspan=2, sticky="ew", pady=12)
    act()

def mostrar_reporte_general():
    if rol_actual != "director": return
    preparar_pagina("Reporte general - Director", "Resumen por grupos.")
    conteos = [("Total alumnos", len(alumnos)), ("Registros", len(registros)), ("Incidencias", len(incidencias)), ("Cartas compromiso", len(cartas_compromiso))]
    for g in ["1°","2°","3°","4°","5°","6°"]:
        conteos.append((f"Alumnos {g}", len([a for a in alumnos if a["grupo"]==g])))
    for et,cant in conteos:
        f=tk.Frame(panel_contenido, bg=BLANCO, padx=18, pady=16, highlightbackground=GRIS_BORDE, highlightthickness=1)
        f.pack(fill="x", pady=6)
        tk.Label(f, text=et, bg=BLANCO, fg=TEXTO, font=("Arial", 11)).pack(side="left")
        tk.Label(f, text=str(cant), bg=BLANCO, fg=GUINDA, font=("Arial", 14, "bold")).pack(side="right")

def mostrar_lista_alumnos():
    if rol_actual != "director": return
    preparar_pagina("Lista de alumnos", "Consulta de todos los grupos.")
    tabla = crear_tabla(panel_contenido, ("nombre","grupo"), ("Nombre completo","Grupo"), altura=15)
    for a in alumnos_ordenados(): tabla.insert("", "end", values=(a["nombre"], a["grupo"]))

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
        act(); exportar_txt(f"carta_compromiso_{n.replace(' ', '_')}.txt", contenido)
    crear_boton(form, "Generar y guardar carta", gen).grid(row=3, column=0, columnspan=2, sticky="ew", pady=12)
    act()

def centrar_ventana():
    root.update_idletasks()
    w=min(1120, root.winfo_screenwidth()); h=min(720, root.winfo_screenheight())
    x=max(0,(root.winfo_screenwidth()-w)//2); y=max(0,(root.winfo_screenheight()-h)//2)
    root.geometry(f"{w}x{h}+{x}+{y}")

centrar_ventana()
mostrar_login()
root.state('zoomed')
root.mainloop()
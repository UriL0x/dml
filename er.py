import re
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

VALID_TYPES = ["INT", "VARCHAR", "DECIMAL", "CHAR", "DATE", "FLOAT", "NUMERIC"]
IDENTIFIER_PATTERN = re.compile(r"^[A-Z][A-Z0-9#_]*$", re.IGNORECASE)

def analizar_ddl_o_insert(consulta_completa):
    errores = []
    sentencias = [s.strip() + ';' for s in consulta_completa.strip().split(';') if s.strip()]
    
    for i, sentencia in enumerate(sentencias):
        errores += analizar_sentencia(sentencia, i + 1)

    return errores

def analizar_sentencia(consulta, index):
    errores = []
    consulta = consulta.strip()

    # Validar paréntesis
    if consulta.count('(') != consulta.count(')'):
        errores.append({
            "tipo": "Sintaxis",
            "codigo": f"P000",
            "descripcion": f"Sentencia {index}: Paréntesis desbalanceados: {consulta.count('(')} abiertos, {consulta.count(')')} cerrados."
        })
        return errores

    # Detectar paréntesis vacíos en cualquier parte de la consulta
    if re.search(r"\(\s*\)", consulta):
        errores.append({
            "tipo": "Sintaxis",
            "codigo": "C012",
            "descripcion": f"Sentencia {index}: Paréntesis vacíos encontrados en la consulta."
        })

    if consulta.upper().startswith("CREATE TABLE"):
        if not consulta.endswith(");"):
            errores.append({"tipo": "Sintaxis", "codigo": f"C001", "descripcion": f"Sentencia {index}: Falta el cierre de paréntesis o punto y coma."})

        match = re.search(r'\((.*)\)', consulta, re.DOTALL)
        if not match:
            errores.append({"tipo": "Sintaxis", "codigo": f"C002", "descripcion": f"Sentencia {index}: No se pudo extraer el contenido entre paréntesis."})
            return errores

        contenido = match.group(1)
        columnas = [c.strip() for c in contenido.split(',') if c.strip()]
        if not columnas:
            errores.append({"tipo": "Columna", "codigo": f"C003", "descripcion": f"Sentencia {index}: No se encontraron definiciones de columnas."})
            return errores

        for idx, linea in enumerate(columnas):
            # Detectar la condición donde FOREIGN KEY tiene paréntesis vacíos después de REFERENCES
            if "FOREIGN KEY" in linea.upper() and "REFERENCES" in linea.upper():
                if re.search(r"REFERENCES\s+\w+\s*\(\s*\)", linea, re.IGNORECASE):  # Detecta paréntesis vacíos
                    errores.append({
                        "tipo": "Clave foránea",
                        "codigo": f"C011",
                        "descripcion": f"Sentencia {index}: Clave foránea sin columnas definidas en: {linea}"
                    })
                continue

            # Revisar PRIMARY KEY
            if "PRIMARY KEY" in linea.upper():
                if re.search(r'PRIMARY\s+KEY\s*\(\s*\)', linea, re.IGNORECASE):
                    errores.append({
                        "tipo": "Clave primaria",
                        "codigo": f"C010",
                        "descripcion": f"Sentencia {index}: Clave primaria vacía."
                    })
                continue

            # Revisar tipo de dato
            partes = linea.split()
            if len(partes) < 2:
                errores.append({
                    "tipo": "Columna",
                    "codigo": f"C1{idx}",
                    "descripcion": f"Sentencia {index}: Definición incompleta de columna: '{linea}'."
                })
                continue

            nombre_col = partes[0]
            tipo_dato = partes[1].upper()

            if not IDENTIFIER_PATTERN.match(nombre_col):
                errores.append({
                    "tipo": "Identificador",
                    "codigo": f"C2{idx}",
                    "descripcion": f"Sentencia {index}: Identificador inválido: '{nombre_col}'."
                })

            tipo_base = re.match(r"[A-Z]+", tipo_dato)
            if not tipo_base or tipo_base.group() not in VALID_TYPES:
                errores.append({
                    "tipo": "Tipo de dato",
                    "codigo": f"C3{idx}",
                    "descripcion": f"Sentencia {index}: Tipo de dato inválido: '{tipo_dato}'."
                })

            # Validación de tamaños para tipos como CHAR o NUMERIC
            if tipo_dato == "CHAR" or tipo_dato == "VARCHAR":
                if len(partes) < 3 or not re.match(r"\(\d+\)", partes[2]):
                    errores.append({
                        "tipo": "Tamaño de columna",
                        "codigo": f"C4{idx}",
                        "descripcion": f"Sentencia {index}: Tamaño de columna no especificado correctamente para '{nombre_col}'."
                    })

            elif tipo_dato == "NUMERIC" or tipo_dato == "DECIMAL":
                if len(partes) < 3 or not re.match(r"\(\d+(\,\d+)?\)", partes[2]):
                    errores.append({
                        "tipo": "Tamaño de columna",
                        "codigo": f"C4{idx}",
                        "descripcion": f"Sentencia {index}: Tamaño o precisión no especificado correctamente para '{nombre_col}'."
                    })

    elif consulta.upper().startswith("INSERT INTO"):
        if not consulta.endswith(";"):
            errores.append({"tipo": "Sintaxis", "codigo": "I001", "descripcion": f"Sentencia {index}: Falta punto y coma al final."})

        match = re.match(r"INSERT INTO\s+(\w+)\s+VALUES\s*\((.*?)\);", consulta, re.IGNORECASE | re.DOTALL)
        if not match:
            errores.append({"tipo": "Sintaxis", "codigo": "I002", "descripcion": f"Sentencia {index}: Formato incorrecto: debe ser INSERT INTO tabla VALUES (...);"})


    else:
        errores.append({"tipo": "Sintaxis", "codigo": "E000", "descripcion": f"Sentencia {index}: No comienza con CREATE TABLE o INSERT INTO."})

    return errores



def ejecutar_analisis():
    consulta = text_input.get("1.0", tk.END)
    errores = analizar_ddl_o_insert(consulta)
    mostrar_errores(errores)

def mostrar_errores(errores):
    for item in tree.get_children():
        tree.delete(item)

    if errores:
        for err in errores:
            tree.insert("", "end", values=(err["tipo"], err["codigo"], err["descripcion"]))
        tree_frame.pack(pady=10, fill="x")
    else:
        tree_frame.pack_forget()
        messagebox.showinfo("Resultado del análisis", "Todas las sentencias son válidas. No se encontraron errores.")

# --- INTERFAZ TKINTER ---
root = tk.Tk()
root.title("Analizador SQL - CREATE e INSERT múltiples")
root.geometry("800x550")

tk.Label(root, text="Ingrese sentencias CREATE TABLE o INSERT INTO (una o más):", font=("Arial", 12)).pack(pady=5)

text_input = scrolledtext.ScrolledText(root, height=12, font=("Consolas", 11))
text_input.pack(padx=10, pady=5, fill="both", expand=True)

tk.Button(root, text="Analizar", command=ejecutar_analisis, font=("Arial", 11), bg="#007ACC", fg="white").pack(pady=10)

tree_frame = tk.Frame(root)
tree = ttk.Treeview(tree_frame, columns=("tipo", "codigo", "descripcion"), show="headings")
tree.heading("tipo", text="tipo")
tree.heading("codigo", text="codigo")
tree.heading("descripcion", text="descripcion")
tree.column("tipo", width=100)
tree.column("codigo", width=80)
tree.column("descripcion", width=580)
tree.pack(fill="x")

root.mainloop()

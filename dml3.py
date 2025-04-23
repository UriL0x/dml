import tkinter as tk
from tkinter import ttk, messagebox
import re
import sqlite3
from errors import validate_tokens

token_dict = {
        "SELECT": 100, "FROM": 101, "WHERE": 102,
        "INSERT": 103, "INTO": 106, "VALUES": 107,
        "UPDATE": 104, "SET": 108, "DELETE": 105,
        "AND": 109, "OR": 110, "IN": 111
    }

delimiters = {".": 60, ",": 61, "(": 62, ")": 63, "'": 64}
operators = {"+": 70, "-": 71, "*": 72, "/": 73, "=": 83, ">": 81, "<": 82, ">=": 84, "<=": 85}

def tokenize(sql):
    tokens = []
    lines = sql.split("\n")
    counter_consts = 0
    counter_ids = 0

    delimiters = {".": 60, ",": 61, "(": 62, ")": 63, "'": 64}
    operators = {"+": 70, "-": 71, "*": 72, "/": 73, "=": 83, ">": 81, "<": 82, ">=": 84, "<=": 85}

    for line_number, line in enumerate(lines, start=1):
        words = re.split(r'(\s+|>=|<=|=|>|<|,|\(|\)|\.)', line)
        words = [w for w in words if w.strip() != ""]

        for word in words:
            token_type = None
            token_value = None
            w = word.upper()

            if w in token_dict:
                token_type = "PALABRA_RESERVADA"
                token_value = token_dict[w]
            elif w in delimiters:
                token_type = "DELIMITADOR"
                token_value = delimiters[w]
            elif w in operators:
                token_type = "OPERADOR"
                token_value = operators[w]
            elif w.isdigit() or re.match(r"^[’'\"].*[’'\"]$", w):
                token_type = "CONSTANTE"
                counter_consts += 1
                token_value = counter_consts + 600
            elif re.match(r"^[A-Za-z_][A-Za-z0-9_#]*$", w):
                token_type = "IDENTIFICADOR"
                counter_ids += 1
                token_value = counter_ids + 400
            else:
                pass

            tokens.append({
                "lineNumber": line_number,
                "word": word,
                "tokenType": token_type,
                "tokenValue": token_value
            })

    return tokens                    
 
def main():
    def process_sql():
        query = sql_input.get("1.0", "end").strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter an SQL query.")
            return

        tokens = tokenize(query)
        errors = validate_tokens(tokens)

        # Limpiar tabla
        for item in token_table.get_children():
            token_table.delete(item)

        # Cambiar título según haya errores o no
        if errors:
            root.title("Errors Found")
            for error in errors:
                token_table.insert("", "end", values=(
                    error["lineNumber"], error["word"], error["errorCode"], error["message"]
                ))
        else:
            root.title("Tokens")
            for token in tokens:
                token_table.insert("", "end", values=(
                    token["lineNumber"], token["word"], token["tokenType"], token["tokenValue"]
                ))

    # GUI
    root = tk.Tk()
    root.title("SQL Analyzer - Tokens and Errors")
    root.geometry("850x600")

    tk.Label(root, text="SQL Query:").pack(pady=5)
    sql_input = tk.Text(root, height=12)
    sql_input.pack(fill="x", padx=10)

    tk.Button(root, text="Analyze", command=process_sql).pack(pady=10)

    token_table = ttk.Treeview(root, columns=("line", "word", "type", "value"), show="headings")
    for col in ["line", "word", "type", "value"]:
        token_table.heading(col, text=col.capitalize())
        token_table.column(col, anchor="center")
    token_table.pack(fill="x", padx=10, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
    


 


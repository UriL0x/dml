import re
import os
import random

token_dict = {
    "SELECT": 10, "FROM": 11, "WHERE": 12, "IN": 13, "AND": 14, "OR": 15,
    "CREATE": 16, "TABLE": 17, "CHAR": 18, "NUMERIC": 19, "NOT": 20,
    "NULL": 21, "CONSTRAINT": 22, "KEY": 23, "PRIMARY": 24, "FOREIGN": 25,
    "REFERENCES": 26, "INSERT": 27, "INTO": 28, "VALUES": 29
}

delimiters = {",": 50, ".": 51, "(": 52, ")": 53, "'": 54}

def tokenize_const(sql):
    tokens = []
    lines = sql.split("\n")  
    
    counter = 0  
    for line_number, line in enumerate(lines, start=1):
        matches = re.findall(r"'(.*?)'|\"(.*?)\"", line)
        
        for match in matches:
            counter += 1
            token_type, token_value = 62, 600 + counter
            tokens.append((counter, match[0], token_type, token_value))
            
    counter = 0  
    for line_number, line in enumerate(lines, start=1):
        words = re.split(r"[\s]", line)
        for word in words:
            if re.match(r"^\d+$", word):
                counter += 1
                token_type, token_value = 61, 600 + counter
                tokens.append((counter, word, token_type, token_value))
    return tokens

import re

def tokenize_all(sql):
    tokens = []
    
    delimiters = {".": 60, ",": 61, "(": 62, ")": 63, "'": 64}
    operators = {"+": 70, "-": 71, "*": 72, "/": 73, "=": 83, ">": 81, "<": 82, ">=": 84, "<=": 85}
    token_dict = {"SELECT": 100, "FROM": 101, "WHERE": 102, "INSERT": 103, "UPDATE": 104, "DELETE": 105}
    
    lines = sql.split("\n")
    counter = 0
    
    for line_number, line in enumerate(lines, start=1):
        words = re.split(r'([\s,=()\'*+/<>-])', line)  

        for word in words:
            if word.strip() == "":
                continue  # 
            
            if word in delimiters:
                counter += 1
                tokens.append((counter, line_number, word, delimiters[word]))
            elif word in operators:
                counter += 1
                tokens.append((counter, line_number, word, operators[word]))
            elif word in token_dict:
                counter += 1
                tokens.append((counter, line_number, word, token_dict[word]))
            elif re.match(r"^[a-zA-Z][\w_.#]*$", word):
                counter += 1
                tokens.append((counter, line_number, word, 400 + counter))
            else:
                pass
    
    return tokens


if __name__ == "__main__":

    cons = ["""
    SELECT *
    FROM PROFESORES
    WHERE EDAD > 45 AND GRADO='MAE' OR GRADO='DOC'
    """,
    """
    SELECT ANOMBRE
    FROM ALUMNOS,INSCRITOS
    WHERE ALUMNOS.A#=INSCRITOS.A# AND INSCRITOS.SEMESTRE='2010I'
    """,
    """
    SELECT ANOMBRE
    FROM ALUMNOS,INSCRITOS,CARRERAS
    WHERE ALUMNOS.A#=INSCRITOS.A# AND ALUMNOS.C#=CARRERAS.C#
    AND INSCRITOS.SEMESTRE='2010I'
    AND CARRERAS.CNOMBRE='ISC'
    AND ALUMNOS.GENERACION='2010'
    """,
    """
    SELECT ANOMBRE
    FROM ALUMNOS A,INSCRITOS I,CARRERAS C
    WHERE A.A#=I.A# AND A.C#=C.C# AND I.SEMESTRE='2010I'
    AND C.CNOMBRE='ISC' AND A.GENERACION='2010'
    """,
    """
    SELECT MNOMBRE, CNOMBRE
    FROM CARRERAS C,DEPARTAMENTOS D,MATERIAS M
    WHERE C.C#=M.C# AND C.D#=D.D# AND D.DNOMBRE='CIECOM'
    """,
    """
    SELECT M#,MNOMBRE
    FROM MATERIAS
    WHERE M# IN (SELECT M#
    FROM INSCRITOS
    WHERE A# IN (SELECT A#
    FROM ALUMNOS
    WHERE ANOMBRE='MESSI LIONEL'))
    """ ]
    
    con = """
    SELECT ANOMBRE, CALIFICACION, TURNO
    FROM ALUMNOS, INSCRITOS, MATERIAS, CARRERAS
    WHERE MNOMBRE='LENAUT2' AND TURNO ='TM'
    AND CNOMBRE='ISC' AND SEMESTRE='2023I' AND CALIFICACION >= 70
    """
    
    tokens_list = tokenize_all(con)
    const = tokenize_const(con)
    
    if len(tokens_list) > 0:
        print('//Lexica//')             
        token_format = "{:<10} {:<10} {:<10} {:<10}"
        print(token_format.format("NO", "LINEA", "TOKEN", 'valor'))
        print("-" * 60)
        


        token_format = "{:<10} {:<10} {:<10} {:<10}"
        for token in tokens_list:
            print(token_format.format(*token))
        print("-" * 60, "\n")
    else:
        print('[!] Error: No es una sentencia sql')
        exit()
    
    if len(const) > 0:
        print('//Constantes//')             
        token_format = "{:<10} {:<10} {:<10} {:<10}"
        print(token_format.format("NO.", "CONSTANTE", "TIPO", 'VALOR'))
        print("-" * 60)
        for token in const:
            print(token_format.format(*token))
        print("-" * 60, "\n")
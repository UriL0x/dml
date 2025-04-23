import re

error_dict = {
    101: "Símbolo desconocido.",
    200: "Sin error.",
    201: "Se esperaba Palabra Reservada.",
    204: "Se esperaba Identificador.",
    205: "Se esperaba Delimitador.",
    206: "Se esperaba Constante.",
    207: "Se esperaba Operador.",
    208: "Se esperaba Operador Relacional."
}

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

def value_reserve_words(tokens):
    errors = []
    
    for i in range(len(tokens)):
        if i == len(tokens)-1:
            break
        
        if tokens[i]['tokenType'] == 'PALABRA_RESERVADA':
            if tokens[i+1]['tokenType'] == 'OPERADOR' or tokens[i+1]['tokenType'] == 'IDENTIFICADOR' or tokens[i+1]['tokenType'] == 'DELIMITADOR':
                continue
            print(tokens[i]['word'])
            if tokens[i+1]['tokenType'] != 'OPERADOR':
                print('adu no7')
                errors.append({
                        'lineNumber': tokens[i]['lineNumber'],
                        'word': tokens[i],
                        'errorCode': 207,
                        'message': error_dict[207]
                    })
            elif tokens[i+1]['tokenType'] != 'IDENTIFICADOR':
                errors.append({
                        'lineNumber': tokens[i]['lineNumber'],
                        'word': tokens[i],
                        'errorCode': 201,
                        'message': error_dict[201]
                    })
            elif tokens[i+1]['tokenType'] != 'DELIMITADOR':
                errors.append({
                        'lineNumber': tokens[i]['lineNumber'],
                        'word': tokens[i],
                        'errorCode': 201,
                        'message': error_dict[201]
                    })
    
    return errors

def value_ids(tokens):
    errors = []
    
    for i in range(len(tokens)):
        if i == len(tokens)-1:
            break
        
        if tokens[i]['tokenType'] == 'IDENTIFICADOR':
            if tokens[i+1]['tokenType'] == 'OPERADOR' or tokens[i+1]['tokenType'] == 'PALABRA_RESERVADA' or tokens[i+1]['tokenType'] == 'DELIMITADOR'  or tokens[i+1]['tokenType'] == 'IDENTIFICADOR':
                continue
                
            if tokens[i+2]['tokenType'] != 'OPERADOR':
                print('ids?')
                errors.append({
                        'lineNumber': tokens[i]['lineNumber'],
                        'word': tokens[i]['word'],
                        'errorCode': 207,
                        'message': error_dict[207]
                    })
            elif tokens[i+1]['tokenType'] != 'DELIMITADOR':
                errors.append({
                        'lineNumber': tokens[i]['lineNumber'],
                        'word': tokens[i]['word'],
                        'errorCode': 205,
                        'message': error_dict[205]
                    })
            elif tokens[i+1]['tokenType'] != 'PALABRA_RESERVADA':
                errors.append({
                        'lineNumber': tokens[i]['lineNumber'],
                        'word': tokens[i]['word'],
                        'errorCode': 201,
                        'message': error_dict[204]
                    })
            elif tokens[i+1]['tokenType'] != 'IDENTIFICADOR':
                errors.append({
                        'lineNumber': tokens[i]['lineNumber'],
                        'word': tokens[i]['word'],
                        'errorCode': 201,
                        'message': error_dict[204]
                    })
           
    return errors

def value_closed_operators(tokens):
    errors = []
    stack = []  

    for i, token in enumerate(tokens):
        if token['tokenType'] == 'DELIMITADOR':
            if token['word'] == '(':
                stack.append(token)  
            elif token['word'] == ')':
                if stack:
                    stack.pop()  
                else:
                    errors.append({
                        'lineNumber': token['lineNumber'],
                        'word': token['word'],
                        'errorCode': 205,
                        'message': error_dict[205]
                    })

        if token['tokenType'] is None:
            errors.append({
                'lineNumber': token['lineNumber'],
                'word': token['word'],
                'errorCode': 205,
                'message': error_dict[205]
            })

    for token in stack:
        errors.append({
            'lineNumber': token['lineNumber'],
            'word': token['word'],
            'errorCode': 205,
            'message': error_dict[205]
        })

    return errors

def value_logic_operators(tokens):
    errors = []
    
    for i in range(len(tokens)):
        if i == len(tokens)-1:
            break
        
        if re.match(r'[=><]', tokens[i]['word']):
            if tokens[i+1]['tokenType'] == 'CONSTANTE' or tokens[i+1]['tokenType'] == 'IDENTIFICADOR':
                continue
                
            if tokens[i+1]['tokenType'] != 'CONSTANTE':
                print('dfdf')
                errors.append({
                        'lineNumber': tokens[i]['lineNumber'],
                        'word': tokens[i]['word'],
                        'errorCode': 206,
                        'message': error_dict[206]
                    })
            elif tokens[i+1]['tokenType'] != 'IDENTIFICADOR':
                print('dfdf')
                errors.append({
                        'lineNumber': tokens[i]['lineNumber'],
                        'word': tokens[i]['word'],
                        'errorCode': 206,
                        'message': error_dict[206]
                    })
                
    return errors

def validate_special_id(tokens):
    errors = []
    
    for i in range(len(tokens)):
        if i == len(tokens)-1:
            break
        
        if tokens[i]['tokenType'] == 'IDENTIFICADOR' and re.search('#', tokens[i]['word']):
            if tokens[i+1]['tokenType'] == 'PALABRA_RESERVADA' or re.search(r'[=,]', tokens[i+1]['word']):
                continue

            if tokens[i+1]['tokenType'] != 'PALABRA_RESERVADA':
                print('yik')
                errors.append({
                        'lineNumber': tokens[i]['lineNumber'],
                        'word': tokens[i],
                        'errorCode': 201,
                        'message': error_dict[201]
                    })
    
    return errors

def validate_logic_words(tokens):
    errors = []
    
    for i in range(len(tokens)):
        if i == len(tokens)-1:
            break
        
        if tokens[i]['tokenType'] == 'CONSTANTE' and tokens[i+1]['tokenType'] == 'IDENTIFICADOR':
            print(';plo')
            errors.append({
                        'lineNumber': tokens[i]['lineNumber'],
                        'word': tokens[i],
                        'errorCode': 201,
                        'message': error_dict[201]
                    })
    return errors
 
def validate_comas(tokens):
    errors = []

    for i in range(len(tokens) - 1):  
        current_word = tokens[i]['word']
        
        if current_word in [',', '.']: 
            if tokens[i+1]['tokenType'] != 'IDENTIFICADOR': 
                errors.append({
                    'lineNumber': tokens[i+1]['lineNumber'],
                    'word': tokens[i+1]['word'],
                    'errorCode': 204,
                    'message': error_dict[204]
                })

    return errors

def validate_tokens(tokens):
    error = validate_comas(tokens)
    if error:
        return error
    error = value_reserve_words(tokens)
    if error:
        return error
    error = value_ids(tokens)
    if error:
        return error
    error = value_closed_operators(tokens)
    if error:
        return error
    error = value_logic_operators(tokens)
    if error:
        return error
    error = validate_special_id(tokens)
    if error:
        return error
    error = validate_logic_words(tokens)
    if error:
        return error
    
    return error

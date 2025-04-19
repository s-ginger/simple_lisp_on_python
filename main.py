import operator
import re
import sys 

# Базовая среда
env = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '>' : operator.gt,
    '<' : operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
    '=' : operator.eq,
    'print': print
}

def tokenize(s):
    return re.findall(r'"[^"]*"|[()]|[^\s()]+', s)

def parse(tokens):
    if len(tokens) == 0:
        raise SyntaxError("Unexpected EOF")
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(parse(tokens))
        tokens.pop(0)  
        return L
    elif token == ')':
        raise SyntaxError("Unexpected )")
    else:
        return atom(token)

def atom(token):
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]  
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token  

def eval(ast, env):
    if isinstance(ast, str):
        return env[ast]
    elif not isinstance(ast, list):
        return ast  
    
    op = ast[0]
    args = ast[1:]

    if op == 'print':
        evaled_args = [eval(arg, env) for arg in args]
        return env['print'](*evaled_args)
    elif op == 'define':
        env[args[0]] = eval(args[1], env)
        return args[0]
    elif op == 'if':
        cond = eval(args[0], env)
        if cond:
            return eval(args[1], env)
        else:
            return eval(args[2], env)
    elif op == 'lambda':
        params = args[0]  
        body = args[1]  
        return lambda *params_vals: eval(body, {**env, **dict(zip(params, params_vals))})
    elif op == 'import':
        path = args[0] + '.lisp'  # Формируем путь
        with open(path, 'r') as f:
            for line in f:
                code = line.strip()
                if code:
                    result = parse(tokenize(code))  # Парсим и выполняем код из импортируемого файла
                    eval(result, env)
    else:
        proc = eval(op, env)
        evaled_args = [eval(arg, env) for arg in args]
        return proc(*evaled_args)

argx = sys.argv

if len(argx) == 2:
    with open(argx[1], 'r') as f:
        for line in f:
            code = line.strip() 
            if code:  
                result = parse(tokenize(code))
                eval(result, env)
else:
    while True:
        code = input('>>> ')
        if code == 'exit':
            break
        result = parse(tokenize(code))
        eval(result, env)
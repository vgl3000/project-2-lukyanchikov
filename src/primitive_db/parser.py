import shlex

def parse_command(line):
    # return list of tokens
    return shlex.split(line)

def parse_where(tokens):
    # expect form: <col> = <value>
    if not tokens:
        return None
    if "=" in tokens:
        idx = tokens.index("=")
        key = tokens[idx-1]
        val = tokens[idx+1]
        return {key: _cast_value(val)}
    # fallback simple: tokens like 'age=28'
    part = tokens[0]
    if "=" in part:
        k, v = part.split("=", 1)
        return {k: _cast_value(v)}
    return None

def parse_set(tokens):
    # expects: <col> = <value>
    return parse_where(tokens)

def parse_values(tokens):
    # tokens like 'values', '(', 'a,', 'b', ')'
    s = " ".join(tokens)
    start = s.find("(")
    end = s.rfind(")")
    if start == -1 or end == -1:
        return []
    inner = s[start+1:end].strip()
    # split by comma respecting quotes
    lexer = shlex.shlex(inner, posix=True)
    lexer.whitespace = ","
    lexer.whitespace_split = True
    vals = [ _cast_value(v.strip()) for v in lexer ]
    return vals

def _cast_value(tok):
    # remove surrounding quotes
    if tok.lower() in ("true", "false"):
        return tok.lower() == "true"
    if tok.startswith('"') and tok.endswith('"') or tok.startswith("'") and tok.endswith("'"):
        return tok[1:-1]
    try:
        if "." in tok:
            return float(tok)
        return int(tok)
    except Exception:
        return tok
import re
from dataclasses import dataclass
from typing import List

@dataclass
class Token:
    type: str
    value: str
    line: int = 1
    column: int = 1

class Lexer:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tokens: List[Token] = []
        self.current_pos = 0
        self.line = 1
        self.column = 1
        
        # Token specification
        self.token_specs = [
            ("NUMBER", r'\d+(\.\d+)?'),
            ("STRING", r'"[^"]*"'),
            ("KEYWORD", r'\b(number|text|is|show|if|else|while|end|greater|less|equal|than|to|repeat|times|task|run|with|and|list|for|each|in|result|use|record|of|read|write|try|catch)\b'),
            ("IDENTIFIER", r'[A-Za-z_][A-Za-z0-9_]*'),
            ("PLUS", r'\+'),
            ("MINUS", r'-'),
            ("STAR", r'\*'),
            ("SLASH", r'/'),
            ("DOT", r'\.'),
            ("WHITESPACE", r'[ \t]+'),
            ("NEWLINE", r'\n'),
            ("MISMATCH", r'.')
        ]
        
        self.regex = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specs))

    def tokenize(self) -> List[Token]:
        for match in self.regex.finditer(self.source_code):
            kind = match.lastgroup
            value = match.group()
            
            if kind == "WHITESPACE":
                self.column += len(value)
                continue
            elif kind == "NEWLINE":
                self.line += 1
                self.column = 1
                continue
            elif kind == "MISMATCH":
                raise SyntaxError(f"Unexpected character '{value}' at line {self.line}, column {self.column}")
            
            self.tokens.append(Token(kind, value, self.line, self.column))
            self.column += len(value)
            
        self.tokens.append(Token("EOF", "", self.line, self.column))
        return self.tokens

if __name__ == "__main__":
    code = '''
    number a is 10.
    number b is 20.
    show a + b.
    '''
    lexer = Lexer(code)
    for token in lexer.tokenize():
        print(token)

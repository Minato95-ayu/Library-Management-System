import sys
import os
from lexer import Lexer
from parser import Parser
from ast_nodes import UseNode
from interpreter import Interpreter, Environment
from errors import AayuRuntimeError, format_error

def run_file(filepath: str, env: 'Environment' = None, loaded_modules: set = None):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    if env is None:
        env = Environment()
        
    if loaded_modules is None:
        loaded_modules = set()
        
    # Mark current file as loaded to prevent circular imports of itself
    abs_filepath = os.path.abspath(filepath)
    if abs_filepath in loaded_modules:
        return
    loaded_modules.add(abs_filepath)

    with open(filepath, 'r', encoding='utf-8') as f:
        source_code = f.read()

    try:
        # 1. Lexical Analysis
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()

        # 2. Parsing
        parser = Parser(tokens, filename=os.path.basename(filepath))
        ast = parser.parse()

        # 2.5 Pre-process Imports
        base_dir = os.path.dirname(abs_filepath)
        for stmt in ast.statements:
            if isinstance(stmt, UseNode):
                module_path = os.path.join(base_dir, f"{stmt.module}.aayu")
                run_file(module_path, env, loaded_modules)

        interpreter = Interpreter()
        interpreter.environment = env
        interpreter.interpret(ast)

    except AayuRuntimeError as e:
        print(format_error(e))
        sys.exit(1)
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py <path_to_aayu_file>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    run_file(filepath)

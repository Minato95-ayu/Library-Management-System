from ast_nodes import *
from errors import AayuRuntimeError
import difflib

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class AayuRecord:
    def __init__(self, type_name, fields):
        self.type_name = type_name
        self.fields = fields

    def __repr__(self):
        return f"{self.type_name}({self.fields})"

class Environment:
    def __init__(self, enclosing=None):
        self.enclosing = enclosing
        self.values = {}

    def define(self, name, value):
        self.values[name] = value

    def get(self, name: str, interpreter=None):
        if name in self.values:
            return self.values[name]
        if self.enclosing:
            return self.enclosing.get(name, interpreter)
            
        suggestion = None
        if interpreter:
            all_keys = self._get_all_keys()
            matches = difflib.get_close_matches(name, all_keys, n=1, cutoff=0.6)
            if matches:
                suggestion = f"Did you mean '{matches[0]}'?"
                
        if interpreter:
            interpreter.throw_error(f"Variable '{name}' was not found.", suggestion)
        else:
            raise Exception(f"Undefined variable '{name}'.")

    def _get_all_keys(self) -> list:
        keys = list(self.values.keys())
        if self.enclosing:
            keys.extend(self.enclosing._get_all_keys())
        return keys

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise RuntimeError(f"Undefined variable '{name}'.")

class Interpreter:
    def __init__(self):
        self.environment = Environment()
        self.current_node = None
        
    def throw_error(self, message: str, suggestion: str = None):
        raise AayuRuntimeError(message, self.current_node, suggestion)

    def interpret(self, ast: ProgramNode):
        try:
            self.visit_ProgramNode(ast)
        except ReturnException as r:
            return r.value

    def visit(self, node: Node):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def evaluate(self, node: Node):
        return self.visit(node)

    def generic_visit(self, node: Node):
        raise Exception(f"No visit_{type(node).__name__} method")

    def visit_ProgramNode(self, node: ProgramNode):
        for statement in node.statements:
            self.current_node = statement
            self.visit(statement)

    def visit_DeclarationNode(self, node: DeclarationNode):
        value = self.evaluate(node.value)
        self.environment.define(node.name, value)
        return value

    def visit_AssignmentNode(self, node: AssignmentNode):
        value = self.evaluate(node.value)
        
        if isinstance(node.target, VariableNode):
            self.environment.assign(node.target.name, value)
        elif isinstance(node.target, PropertyAccessNode):
            obj = self.evaluate(node.target.object_expr)
            if not isinstance(obj, AayuRecord):
                self.throw_error("Property assignment only allowed on records.")
            if node.target.property_name not in obj.fields:
                self.throw_error(f"Property '{node.target.property_name}' does not exist on {obj.type_name}.")
            obj.fields[node.target.property_name] = value
        else:
            self.throw_error("Invalid assignment target.")
            
        return value

    def visit_ShowNode(self, node: ShowNode):
        value = self.evaluate(node.expression)
        print(value)

    def visit_BinaryExpressionNode(self, node: BinaryExpressionNode):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        if node.operator == '+': return left + right
        if node.operator == '-': return left - right
        if node.operator == '*': return left * right
        if node.operator == '/':
            if right == 0:
                self.throw_error("Cannot divide by zero.")
            return left / right
        if node.operator == '>': return left > right
        if node.operator == '<': return left < right
        if node.operator == '==': return left == right

        self.throw_error(f"Unknown operator {node.operator}")

    def visit_VariableNode(self, node: VariableNode):
        return self.environment.get(node.name, self)

    def visit_NumberNode(self, node: NumberNode):
        return node.value

    def visit_TextNode(self, node: TextNode):
        return node.value

    def visit_IfNode(self, node: IfNode):
        condition = self.evaluate(node.condition)
        if condition:
            self.execute_block(node.body, Environment(self.environment))
        elif node.else_body is not None:
            self.execute_block(node.else_body, Environment(self.environment))

    def visit_WhileNode(self, node: WhileNode):
        while self.evaluate(node.condition):
            self.execute_block(node.body, Environment(self.environment))

    def visit_TryCatchNode(self, node: TryCatchNode):
        try:
            self.execute_block(node.try_body, Environment(self.environment))
        except ReturnException:
            raise
        except Exception:
            self.execute_block(node.catch_body, Environment(self.environment))

    def visit_RepeatNode(self, node: RepeatNode):
        times = self.evaluate(node.count)
        for _ in range(int(times)):
            self.execute_block(node.body, Environment(self.environment))

    def visit_ForEachNode(self, node: ForEachNode):
        collection = self.evaluate(node.collection)
        for item in collection:
            env = Environment(self.environment)
            env.define(node.iterator, item)
            self.execute_block(node.body, env)

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.current_node = statement
                self.visit(statement)
        finally:
            self.environment = previous

    def visit_TaskNode(self, node: TaskNode):
        self.environment.define(node.name, node)

    def visit_RunNode(self, node: RunNode):
        try:
            task = self.environment.get(node.name)
        except Exception:
            self.throw_error(f"Task '{node.name}' was not found.")
            
        if not isinstance(task, TaskNode):
            self.throw_error(f"{node.name} is not a task.")

        env = Environment(self.environment)
        if len(task.parameters) != len(node.arguments):
            self.throw_error(f"Expected {len(task.parameters)} arguments but got {len(node.arguments)}.")

        for i, arg_name in enumerate(task.parameters):
            val = self.evaluate(node.arguments[i])
            env.define(arg_name, val)

        try:
            self.execute_block(task.body, env)
        except ReturnException as r:
            return r.value

    def visit_ResultNode(self, node: ResultNode):
        value = self.evaluate(node.value)
        raise ReturnException(value)

    def visit_ListDeclarationNode(self, node: ListDeclarationNode):
        elements = [self.evaluate(el) for el in node.elements]
        self.environment.define(node.name, elements)

    def visit_RecordDeclarationNode(self, node: RecordDeclarationNode):
        self.environment.define(node.name, node)

    def visit_InstanceDeclarationNode(self, node: InstanceDeclarationNode):
        record_decl = self.environment.get(node.type_name)
        if not isinstance(record_decl, RecordDeclarationNode):
            self.throw_error(f"{node.type_name} is not a record.")

        fields = {}
        for k, v in node.properties.items():
            fields[k] = self.evaluate(v)

        instance = AayuRecord(node.type_name, fields)
        self.environment.define(node.name, instance)

    def visit_PropertyAccessNode(self, node: PropertyAccessNode):
        obj = self.evaluate(node.object_expr)
        
        # Standard Library: Lists
        if isinstance(obj, list):
            if node.property_name in ("length", "count"):
                return float(len(obj))
            self.throw_error(f"List has no property '{node.property_name}'.")

        # Standard Library: Text
        if isinstance(obj, str):
            if node.property_name == "upper":
                return obj.upper()
            if node.property_name == "lower":
                return obj.lower()
            if node.property_name in ("length", "count"):
                return float(len(obj))
            self.throw_error(f"Text has no property '{node.property_name}'.")

        if not isinstance(obj, AayuRecord):
            self.throw_error(f"Cannot access property '{node.property_name}' on a non-record.")
            
        if node.property_name not in obj.fields:
            self.throw_error(f"Property '{node.property_name}' does not exist on {obj.type_name}.")
            
        return obj.fields[node.property_name]

    def visit_UseNode(self, node: UseNode):
        pass

    def visit_ReadExpressionNode(self, node: ReadExpressionNode):
        file_path = self.evaluate(node.file_path)
        if not isinstance(file_path, str):
            self.throw_error("File path must evaluate to text.")
        try:
            with open(file_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            self.throw_error(f"File not found: {file_path}")

    def visit_WriteStatementNode(self, node: WriteStatementNode):
        data = self.evaluate(node.data)
        file_path = self.evaluate(node.destination)
        if not isinstance(file_path, str):
            self.throw_error("Destination file path must evaluate to text.")
        with open(file_path, "w") as f:
            f.write(str(data))

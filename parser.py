from typing import List
from lexer import Token, Lexer
from ast_nodes import (
    ProgramNode, DeclarationNode, ShowNode, BinaryExpressionNode,
    VariableNode, NumberNode, TextNode, IfNode, WhileNode, TryCatchNode, RepeatNode, ForEachNode, TaskNode, RunNode, ListDeclarationNode, ResultNode, UseNode, RecordDeclarationNode, InstanceDeclarationNode, PropertyAccessNode, AssignmentNode, ReadExpressionNode, WriteStatementNode, Node
)

class Parser:
    def __init__(self, tokens: List[Token], filename: str = "main.aayu"):
        self.tokens = tokens
        self.current = 0
        self.in_task_depth = 0
        self.filename = filename

    def parse(self) -> ProgramNode:
        statements = []
        while not self.is_at_end():
            statements.append(self.parse_statement())
        return ProgramNode(statements=statements)

    def parse_statement(self) -> Node:
        start_token = self.peek()
        node = None
        
        if self.match("KEYWORD", "number") or self.match("KEYWORD", "text"):
            node = self.parse_declaration(self.previous().value)
        elif self.match("KEYWORD", "show"):
            node = self.parse_show()
        elif self.match("KEYWORD", "if"):
            node = self.parse_if()
        elif self.match("KEYWORD", "while"):
            node = self.parse_while()
        elif self.match("KEYWORD", "try"):
            node = self.parse_try_catch()
        elif self.match("KEYWORD", "repeat"):
            node = self.parse_repeat()
        elif self.match("KEYWORD", "task"):
            node = self.parse_task()
        elif self.match("KEYWORD", "run"):
            node = self.parse_run()
        elif self.match("KEYWORD", "list"):
            node = self.parse_list_declaration()
        elif self.match("KEYWORD", "for"):
            node = self.parse_for_each()
        elif self.match("KEYWORD", "result"):
            node = self.parse_result_statement()
        elif self.match("KEYWORD", "use"):
            node = self.parse_use_statement()
        elif self.match("KEYWORD", "record"):
            node = self.parse_record_declaration()
        elif self.match("KEYWORD", "write"):
            node = self.parse_write_statement()
        elif self.check("IDENTIFIER"):
            if self.current + 2 < len(self.tokens) and \
               self.tokens[self.current + 1].type == "IDENTIFIER" and \
               self.tokens[self.current + 2].value == "is":
                node = self.parse_instance_declaration()
            else:
                node = self.parse_assignment_statement()
        else:
            raise SyntaxError(f"Unexpected token {self.peek().value} at line {self.peek().line}")
            
        if node:
            node.line = start_token.line
            node.column = start_token.column
            node.file = self.filename
        return node

    def parse_declaration(self, var_type: str) -> DeclarationNode:
        name = self.consume("IDENTIFIER", "Expect variable name.").value
        self.consume("KEYWORD", "Expect 'is' after variable name.", "is")
        
        value = self.parse_expression()
        
        self.consume("DOT", "Expect '.' after declaration.")
        return DeclarationNode(var_type=var_type, name=name, value=value)

    def parse_show(self) -> ShowNode:
        expression = self.parse_expression()
        self.consume("DOT", "Expect '.' after show statement.")
        return ShowNode(expression=expression)

    def parse_if(self) -> IfNode:
        condition = self.parse_expression()
        self.consume("DOT", "Expect '.' after if condition.")
        
        body = []
        else_body = None
        
        while not self.is_at_end() and not self.check("KEYWORD", "end") and not self.check("KEYWORD", "else"):
            body.append(self.parse_statement())
            
        if self.match("KEYWORD", "else"):
            self.consume("DOT", "Expect '.' after 'else'.")
            else_body = []
            while not self.is_at_end() and not self.check("KEYWORD", "end"):
                else_body.append(self.parse_statement())
            
        self.consume("KEYWORD", "Expect 'end' after if block.", "end")
        self.consume("DOT", "Expect '.' after 'end'.")
        
        return IfNode(condition=condition, body=body, else_body=else_body)

    def parse_while(self) -> WhileNode:
        condition = self.parse_expression()
        self.consume("DOT", "Expect '.' after while condition.")
        
        body = []
        while not self.is_at_end() and not self.check("KEYWORD", "end"):
            body.append(self.parse_statement())
            
        self.consume("KEYWORD", "Expect 'end' after while block.", "end")
        self.consume("DOT", "Expect '.' after 'end'.")
        
        return WhileNode(condition=condition, body=body)

    def parse_try_catch(self) -> TryCatchNode:
        self.consume("DOT", "Expect '.' after 'try'.")
        
        try_body = []
        while not self.is_at_end() and not self.check("KEYWORD", "catch"):
            try_body.append(self.parse_statement())
            
        self.consume("KEYWORD", "Expect 'catch' after try block.", "catch")
        self.consume("DOT", "Expect '.' after 'catch'.")
        
        catch_body = []
        while not self.is_at_end() and not self.check("KEYWORD", "end"):
            catch_body.append(self.parse_statement())
            
        self.consume("KEYWORD", "Expect 'end' after catch block.", "end")
        self.consume("DOT", "Expect '.' after 'end'.")
        
        return TryCatchNode(try_body=try_body, catch_body=catch_body)

    def parse_repeat(self) -> RepeatNode:
        count = self.parse_expression()
        self.consume("KEYWORD", "Expect 'times' after repeat count.", "times")
        self.consume("DOT", "Expect '.' after 'times'.")
        
        body = []
        while not self.is_at_end() and not self.check("KEYWORD", "end"):
            body.append(self.parse_statement())
            
        self.consume("KEYWORD", "Expect 'end' after repeat block.", "end")
        self.consume("DOT", "Expect '.' after 'end'.")
        
        return RepeatNode(count=count, body=body)

    def parse_task(self) -> TaskNode:
        name = self.consume("IDENTIFIER", "Expect task name.").value
        
        parameters = []
        if self.match("KEYWORD", "with"):
            parameters.append(self.consume("IDENTIFIER", "Expect parameter name after 'with'.").value)
            while self.match("KEYWORD", "and"):
                parameters.append(self.consume("IDENTIFIER", "Expect parameter name after 'and'.").value)
                
        self.consume("DOT", "Expect '.' after task declaration.")
        
        body = []
        self.in_task_depth += 1
        while not self.is_at_end() and not self.check("KEYWORD", "end"):
            body.append(self.parse_statement())
            
        self.consume("KEYWORD", "Expect 'end' after task block.", "end")
        self.consume("DOT", "Expect '.' after 'end'.")
        self.in_task_depth -= 1
        
        return TaskNode(name=name, parameters=parameters, body=body)

    def _parse_run_core(self) -> RunNode:
        name = self.consume("IDENTIFIER", "Expect task name to run.").value
        
        arguments = []
        if self.match("KEYWORD", "with"):
            arguments.append(self.parse_expression())
            while self.match("KEYWORD", "and"):
                arguments.append(self.parse_expression())
                
        return RunNode(name=name, arguments=arguments)

    def parse_run(self) -> RunNode:
        node = self._parse_run_core()
        self.consume("DOT", "Expect '.' after run statement.")
        return node

    def parse_result_statement(self) -> ResultNode:
        if self.in_task_depth == 0:
            raise SyntaxError(f"Result can only be used inside a task. Found at line {self.peek().line}")
            
        self.consume("KEYWORD", "Expect 'is' after result.", "is")
        value = self.parse_expression()
        self.consume("DOT", "Expect '.' after result statement.")
        
        return ResultNode(value=value)

    def parse_use_statement(self) -> UseNode:
        module_name = self.consume("IDENTIFIER", "Expect module name after 'use'.").value
        self.consume("DOT", "Expect '.' after module name.")
        return UseNode(module=module_name)

    def parse_record_declaration(self) -> RecordDeclarationNode:
        name = self.consume("IDENTIFIER", "Expect record name.").value
        self.consume("DOT", "Expect '.' after record name.")
        
        fields = []
        while not self.is_at_end() and not self.check("KEYWORD", "end"):
            fields.append(self.consume("IDENTIFIER", "Expect field name in record.").value)
            
        self.consume("KEYWORD", "Expect 'end' after record fields.", "end")
        self.consume("DOT", "Expect '.' after 'end'.")
        
        return RecordDeclarationNode(name=name, fields=fields)

    def parse_instance_declaration(self) -> InstanceDeclarationNode:
        type_name = self.consume("IDENTIFIER", "Expect record type name.").value
        name = self.consume("IDENTIFIER", "Expect instance name.").value
        self.consume("KEYWORD", "Expect 'is' after instance name.", "is")
        self.consume("DOT", "Expect '.' after 'is'.")
        
        properties = {}
        while not self.is_at_end() and not self.check("KEYWORD", "end"):
            field = self.consume("IDENTIFIER", "Expect field name.").value
            expr = self.parse_expression()
            properties[field] = expr
            
        self.consume("KEYWORD", "Expect 'end' after instance properties.", "end")
        self.consume("DOT", "Expect '.' after 'end'.")
        
        return InstanceDeclarationNode(type_name=type_name, name=name, properties=properties)

    def parse_assignment_statement(self) -> AssignmentNode:
        target = self.parse_primary()
        self.consume("KEYWORD", "Expect 'is' after assignment target.", "is")
        value = self.parse_expression()
        self.consume("DOT", "Expect '.' after assignment statement.")
        return AssignmentNode(target=target, value=value)

    def parse_write_statement(self) -> WriteStatementNode:
        data = self.parse_expression()
        self.consume("KEYWORD", "Expect 'to' after write data.", "to")
        destination = self.parse_expression()
        self.consume("DOT", "Expect '.' after write statement.")
        return WriteStatementNode(data=data, destination=destination)

    def parse_list_declaration(self) -> ListDeclarationNode:
        name = self.consume("IDENTIFIER", "Expect list name.").value
        self.consume("KEYWORD", "Expect 'is' after list name.", "is")
        self.consume("DOT", "Expect '.' after 'is'.")
        
        elements = []
        while not self.is_at_end() and not self.check("KEYWORD", "end"):
            elements.append(self.parse_expression())
            
        self.consume("KEYWORD", "Expect 'end' after list items.", "end")
        self.consume("DOT", "Expect '.' after 'end'.")
        
        return ListDeclarationNode(name=name, elements=elements)

    def parse_for_each(self) -> ForEachNode:
        self.consume("KEYWORD", "Expect 'each' after 'for'.", "each")
        iterator = self.consume("IDENTIFIER", "Expect iterator name.").value
        self.consume("KEYWORD", "Expect 'in' after iterator name.", "in")
        
        collection = self.parse_expression()
        self.consume("DOT", "Expect '.' after for-each declaration.")
        
        body = []
        while not self.is_at_end() and not self.check("KEYWORD", "end"):
            body.append(self.parse_statement())
            
        self.consume("KEYWORD", "Expect 'end' after for-each block.", "end")
        self.consume("DOT", "Expect '.' after 'end'.")
        
        return ForEachNode(iterator=iterator, collection=collection, body=body)

    def parse_expression(self) -> Node:
        return self.parse_comparison()

    def parse_comparison(self) -> Node:
        expr = self.parse_term()
        
        has_is = self.match("KEYWORD", "is")
        
        operator = None
        if self.match("KEYWORD", "greater"):
            self.consume("KEYWORD", "Expect 'than' after 'greater'.", "than")
            operator = ">"
        elif self.match("KEYWORD", "less"):
            self.consume("KEYWORD", "Expect 'than' after 'less'.", "than")
            operator = "<"
        elif self.match("KEYWORD", "equal"):
            self.consume("KEYWORD", "Expect 'to' after 'equal'.", "to")
            operator = "=="
            
        if operator:
            right = self.parse_term()
            expr = BinaryExpressionNode(left=expr, operator=operator, right=right)
        elif has_is:
            raise SyntaxError(f"Expect comparator after 'is' at line {self.peek().line}")
            
        return expr

    def parse_term(self) -> Node:
        expr = self.parse_factor()

        while self.match("PLUS") or self.match("MINUS"):
            operator = self.previous().value
            right = self.parse_factor()
            expr = BinaryExpressionNode(left=expr, operator=operator, right=right)

        return expr

    def parse_factor(self) -> Node:
        expr = self.parse_primary()

        while self.match("STAR") or self.match("SLASH"):
            operator = self.previous().value
            right = self.parse_primary()
            expr = BinaryExpressionNode(left=expr, operator=operator, right=right)

        return expr

    def parse_primary(self) -> Node:
        if self.match("KEYWORD", "read"):
            file_path = self.parse_expression()
            return ReadExpressionNode(file_path=file_path)
        if self.match("NUMBER"):
            return NumberNode(value=float(self.previous().value))
        if self.match("STRING"):
            # Remove surrounding quotes
            val = self.previous().value[1:-1]
            return TextNode(value=val)
        if self.match("IDENTIFIER"):
            var_node = VariableNode(name=self.previous().value)
            if self.match("KEYWORD", "of"):
                object_expr = self.parse_primary()
                return PropertyAccessNode(property_name=var_node.name, object_expr=object_expr)
            return var_node
        if self.match("KEYWORD", "run"):
            return self._parse_run_core()

        raise SyntaxError(f"Expect expression at line {self.peek().line}.")

    # --- Helper Methods ---

    def match(self, token_type: str, token_value: str = None) -> bool:
        if self.check(token_type, token_value):
            self.advance()
            return True
        return False

    def check(self, token_type: str, token_value: str = None) -> bool:
        if self.is_at_end():
            return False
        if self.peek().type != token_type:
            return False
        if token_value and self.peek().value != token_value:
            return False
        return True

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == "EOF"

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def consume(self, token_type: str, message: str, token_value: str = None) -> Token:
        if self.check(token_type, token_value):
            return self.advance()
        raise SyntaxError(f"{message} Found {self.peek().value} at line {self.peek().line}")

if __name__ == "__main__":
    code = '''
    number a is 10.
    number b is 20.
    show a + b.
    '''
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    import pprint
    pprint.pprint(ast)

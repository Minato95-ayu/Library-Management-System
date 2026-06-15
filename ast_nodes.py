from dataclasses import dataclass
from typing import List, Union

@dataclass
class Node:
    pass

@dataclass
class ProgramNode(Node):
    statements: List[Node]

@dataclass
class NumberNode(Node):
    value: float

@dataclass
class TextNode(Node):
    value: str

@dataclass
class VariableNode(Node):
    name: str

@dataclass
class BinaryExpressionNode(Node):
    left: Node
    operator: str
    right: Node

@dataclass
class DeclarationNode(Node):
    var_type: str
    name: str
    value: Node

@dataclass
class ShowNode(Node):
    expression: Node

@dataclass
class IfNode(Node):
    condition: Node
    body: List[Node]
    else_body: List[Node] = None

@dataclass
class WhileNode(Node):
    condition: Node
    body: List[Node]

@dataclass
class TryCatchNode(Node):
    try_body: List[Node]
    catch_body: List[Node]

@dataclass
class RepeatNode(Node):
    count: Node
    body: List[Node]

@dataclass
class ForEachNode(Node):
    iterator: str
    collection: Node
    body: List[Node]


@dataclass
class TaskNode(Node):
    name: str
    parameters: List[str]  # Future proofing for Sprint A-5
    body: List[Node]

@dataclass
class RunNode(Node):
    name: str
    arguments: List[Node]

@dataclass
class ListDeclarationNode(Node):
    name: str
    elements: List[Node]

@dataclass
class ResultNode(Node):
    value: Node

@dataclass
class UseNode(Node):
    module: str

@dataclass
class RecordDeclarationNode(Node):
    name: str
    fields: List[str]

@dataclass
class InstanceDeclarationNode(Node):
    type_name: str
    name: str
    properties: dict

@dataclass
class PropertyAccessNode(Node):
    property_name: str
    object_expr: Node

@dataclass
class AssignmentNode(Node):
    target: Node
    value: Node

@dataclass
class ReadExpressionNode(Node):
    file_path: Node

@dataclass
class WriteStatementNode(Node):
    data: Node
    destination: Node









class AayuRuntimeError(Exception):
    def __init__(self, message: str, node=None, suggestion: str = None):
        self.message = message
        self.node = node
        self.suggestion = suggestion

def format_error(error: AayuRuntimeError) -> str:
    lines = []
    lines.append("-" * 40)
    lines.append("AAYU RUNTIME ERROR")
    lines.append("-" * 40)
    lines.append(error.message)
    lines.append("")
    
    if error.node:
        lines.append("Location:")
        lines.append(getattr(error.node, 'file', 'main.aayu'))
        lines.append(f"Line {getattr(error.node, 'line', '?')}")
        lines.append(f"Column {getattr(error.node, 'column', '?')}")
        lines.append("")
        
    if error.suggestion:
        lines.append("Suggestion:")
        lines.append(error.suggestion)
        lines.append("")
        
    lines.append("-" * 40)
    return "\n".join(lines)

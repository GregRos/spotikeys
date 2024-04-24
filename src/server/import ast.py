import ast
import astunparse


class RenameMethods(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        # Check if the function has the @override decorator
        if any(
            isinstance(decorator, ast.Name) and decorator.id == "override"
            for decorator in node.decorator_list
        ):
            # Remove the @override decorator
            node.decorator_list = [
                decorator
                for decorator in node.decorator_list
                if not (isinstance(decorator, ast.Name) and decorator.id == "override")
            ]
            # Rename the function
            node.name = f"_{node.name}"

        return node


# Parse the source code
with open("command_handler.py") as f:
    source_code = f.read()
tree = ast.parse(source_code)

# Transform the AST
transformer = RenameMethods()
new_tree = transformer.visit(tree)

# Convert the modified AST back to source code
new_source_code = astunparse.unparse(new_tree)

# Write the modified source code back to the file
with open("command_handler.py", "w") as f:
    f.write(new_source_code)

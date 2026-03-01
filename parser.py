import ast
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from code_visitor import VariableContextTracker
from error_detector import AIReviewer
import os

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")


def parse_code(code_string):
    try:
        tree = ast.parse(code_string)
        formatted_code = ast.unparse(tree)

        return {
            "success": True,
            "tree": tree,
            "formatted_code": formatted_code
        }

    except SyntaxError as e:
        return {
            "success": False,
            "error": {"message": f"Syntax Error: {str(e)}"}
        }


if __name__ == "__main__":
    code = """
import os
import sys

class myclass:
    def AddNumbers(a, b, c, d, e, f):
        x=1
        y=2
        z=3
        while True:
            print(x)
        return a+b
"""

    result = parse_code(code)

    if not result["success"]:
        print("Syntax Error:", result["error"])
    else:
        tree = result["tree"]

        # Context Tracking (optional if you need it)
        visitor = VariableContextTracker()
        visitor.visit(tree)

        # AI Review
        reviewer = AIReviewer(original_code=code)
        reviewer.visit(tree)
        reviewer.analyze()      
        reviewer.report()

        print("Formatted Code:")
        print(result["formatted_code"])
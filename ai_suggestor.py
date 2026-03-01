import os
import ast
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# -----------------------------------------
# Load Environment Variables
# -----------------------------------------
load_dotenv()

# -----------------------------------------
# Initialize Groq Model
# -----------------------------------------
model = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# -----------------------------------------
# Prompt Template for Valid Code
# -----------------------------------------
prompt_template = PromptTemplate(
    input_variables=["code_string"],
    template="""
You are an experienced Python coding teacher.

Analyze the following Python code and provide:

1. Code quality suggestions
2. Any logical errors
3. Time complexity
4. Space complexity
5. Improvements for readability

Code:
{code_string}
"""
)

# -----------------------------------------
# Validate Code Using AST
# -----------------------------------------
def validate_code(code_string):
    try:
        ast.parse(code_string)
        return True, None
    except SyntaxError as e:
        return False, str(e)

# -----------------------------------------
# Main AI Suggestion Function
# -----------------------------------------
def get_ai_suggestion(code_string):
    is_valid, error = validate_code(code_string)

    if not is_valid:
        print("\n⚠ Syntax Error Detected!\n")

        formatted_prompt = f"""
The following Python code contains a syntax error:

{code_string}

Python Error Message:
{error}

Explain:
1. What the error means
2. Why it occurred
3. Provide corrected code
4. Time & Space complexity of corrected code
"""
    else:
        formatted_prompt = prompt_template.format(code_string=code_string)

    result = model.invoke(formatted_prompt)

    print("\n--- AI Review Report ---\n")
    print(result.content)


# -----------------------------------------
# Example Test Block
# -----------------------------------------
if __name__ == "__main__":

    code_string = """
def calculate_sum(a, b):
    result = a + b
    if result > 10
        print("Greater than 10")
    else:
        print("Less than or equal to 10")
    return result
"""

    get_ai_suggestion(code_string)
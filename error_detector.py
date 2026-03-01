import ast


class AIReviewer(ast.NodeVisitor):

    def __init__(self, original_code=None):
        self.defined = set()
        self.used = set()
        self.infinite_loops = []
        self.violations = []
        self.score = 100
        self.original_code = original_code
        self.analysis_done = False


    # ---------------------------
    # Import Detection
    # ---------------------------
    def visit_Import(self, node):
        for alias in node.names:
            self.defined.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.defined.add(alias.name)
        self.generic_visit(node)


    # ---------------------------
    # Variable Tracking
    # ---------------------------
    def visit_Name(self, node):

        if isinstance(node.ctx, ast.Store):
            self.defined.add(node.id)

        elif isinstance(node.ctx, ast.Load):
            self.used.add(node.id)

        self.generic_visit(node)


    # ---------------------------
    # Infinite Loop Detection
    # ---------------------------
    def visit_While(self, node):
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            self.infinite_loops.append(node.lineno)
        self.generic_visit(node)


    # ---------------------------
    # Function Style Checks
    # ---------------------------
    def visit_FunctionDef(self, node):

        # Function Length
        if hasattr(node, "end_lineno"):
            function_length = node.end_lineno - node.lineno
            if function_length > 40:
                message = f"Function '{node.name}' too long ({function_length} lines)"
                if message not in self.violations:
                    self.violations.append(message)
                    self.score -= 5

        # Too Many Arguments
        if len(node.args.args) > 5:
            message = f"Function '{node.name}' has too many arguments"
            if message not in self.violations:
                self.violations.append(message)
                self.score -= 5

        self.generic_visit(node)


    # ---------------------------
    # Class Naming Check
    # ---------------------------
    def visit_ClassDef(self, node):
        if node.name[0].islower():
            message = f"Class '{node.name}' should be PascalCase at line {node.lineno}"
            if message not in self.violations:
                self.violations.append(message)
                self.score -= 10
        self.generic_visit(node)


    # ---------------------------
    # FINAL ANALYSIS
    # ---------------------------
    def analyze(self):

        if self.analysis_done:
            return

        # Unused detection
        unused = self.defined - self.used
        for item in unused:
            message = f"Unused variable/import: '{item}'"
            if message not in self.violations:
                self.violations.append(message)
                self.score -= 5

        # Infinite loop scoring
        for line in self.infinite_loops:
            message = f"Infinite loop detected at line {line}"
            if message not in self.violations:
                self.violations.append(message)
                self.score -= 10

        # Formatting check
        if self.original_code:
            try:
                formatted = ast.unparse(ast.parse(self.original_code))
                if formatted.strip() != self.original_code.strip():
                    message = "Inconsistent spacing/formatting detected"
                    if message not in self.violations:
                        self.violations.append(message)
                        self.score -= 10
            except:
                pass

        self.analysis_done = True


    # ---------------------------
    # REPORT
    # ---------------------------
    def report(self):

        print("\n=== AI CODE REVIEW REPORT ===\n")

        if self.violations:
            print("Violations Found:\n")
            for v in self.violations:
                print(" -", v)
        else:
            print("No style violations found.")

        print("\nFinal Style Score:", max(self.score, 0), "/ 100\n")
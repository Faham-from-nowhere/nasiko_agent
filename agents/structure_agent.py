import ast
import os
import re
from typing import Dict, Any
import networkx as nx


class StructureAgent:
    def __init__(self):
        # Directories to ignore to prevent scanning build artifacts or dependencies
        self.ignore_list = {".git", "node_modules", ".next", "venv", "__pycache__", "dist", "build"}

    def scan_directory(self, root_path: str) -> Dict[str, Any]:
        project_data = {"files": {}, "summary": {"total_files": 0, "python": 0, "web": 0}}
        
        for dirpath, dirs, filenames in os.walk(root_path):
            dirs[:] = [d for d in dirs if d not in self.ignore_list]
            
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in {".py", ".ts", ".tsx", ".js", ".jsx"}:
                    full_path = os.path.join(dirpath, filename)
                    rel_path = os.path.relpath(full_path, root_path)
                    
                    if ext == ".py":
                        metadata = self.analyze_python(full_path)
                        project_data["summary"]["python"] += 1
                    else:
                        metadata = self.analyze_generic(full_path, ext)
                        project_data["summary"]["web"] += 1
                    
                    project_data["files"][rel_path] = metadata
                    project_data["summary"]["total_files"] += 1
        return project_data
    
    def build_dependency_graph(self, project_data):
       graph = nx.DiGraph()

       for file, meta in project_data["files"].items():
        graph.add_node(file)

        for imp in meta.get("imports", []):
            for target_file in project_data["files"]:
                if imp in target_file:
                    graph.add_edge(file, target_file)

       return graph
 

    def analyze_python(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        try:
            tree = ast.parse(source)
            visitor = CodeVisitor()
            visitor.visit(tree)
            return {
                "ext": ".py", "functions": visitor.functions, 
                "classes": visitor.classes, "imports": visitor.imports
            }
        except:
            return {"ext": ".py", "functions": [], "classes": [], "imports": [], "error": "AST Fail"}

    def analyze_generic(self, file_path: str, ext: str):
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        
        # Regex to find React components and standard functions
        functions = []
        found = re.findall(r"(?:export\s+)?(?:function|const)\s+([a-zA-Z0-9_]+)\s*[=:(]", source)
        
        for name in set(found): # Use set to avoid duplicates
            line_num = 1
            for i, line in enumerate(source.split('\n')):
                if name in line and ("function" in line or "=>" in line or "=" in line):
                    line_num = i + 1
                    break
            functions.append({"name": name, "args": [], "lineno": line_num})
            
        return {"ext": ext, "functions": functions, "classes": [], "imports": []}

class CodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.classes, self.functions, self.imports = [], [], []
    def visit_Import(self, node):
        for n in node.names: self.imports.append(n.name)
    def visit_ClassDef(self, node):
        self.classes.append({"name": node.name, "lineno": node.lineno})
    def visit_FunctionDef(self, node):
        self.functions.append({"name": node.name, "args": [a.arg for a in node.args.args], "lineno": node.lineno})
import os
import sys
import networkx as nx
from dotenv import load_dotenv

from agents.structure_agent import StructureAgent
from agents.doc_agent import DocGenerationAgent
from agents.readme_agent import ReadmeAgent
from agents.critic_agent import CriticAgent
from core.injector import DocstringInjector

load_dotenv()

def run_pipeline(target_path):
    # 1. Initialize Agents
    scanner = StructureAgent()
    gen = DocGenerationAgent()
    injector = DocstringInjector()
    summarizer = ReadmeAgent()
    critic = CriticAgent()

    print(f"🚀 Deep Scan: {target_path}")
    
    # 2. Scan & Build Graph
    data = scanner.scan_directory(target_path)
    
    # INNOVATION: Generate the Dependency Graph using NetworkX
    print("🕸️  Building Dependency Graph...")
    graph = scanner.build_dependency_graph(data)
    
    # Convert graph to text format for the LLM (e.g., "auth.ts -> user.ts")
    graph_text = ""
    if graph.number_of_edges() > 0:
        graph_text = "\n".join([f"{u} -> {v}" for u, v in graph.edges()])
    else:
        graph_text = "No explicit imports detected (likely implicit framework routing)."

    print(f"📝 Found {len(data['files'])} files. Starting Documentation Loop...")

    # 3. Docstring Injection Loop
    for rel_path, meta in data['files'].items():
        full_path = os.path.join(target_path, rel_path)

        for func in meta.get("functions", []):
            attempts = 0
            max_attempts = 2 # Self-correction limit

            print(f"   ⚙ Processing {func['name']}...")
            
            # Generate
            doc = gen.generate(func, meta["ext"])

            # Critique & Refine Loop
            while attempts < max_attempts:
                valid, message = critic.critique(doc, func)
                
                if valid:
                    injector.inject_docstring(full_path, func, doc)
                    print(f"      ✅ Injected: {func['name']}")
                    break
                else:
                    print(f"      ⚠️  Critique: {message}. Refining...")
                    doc = critic.refine(doc, func, message)
                    attempts += 1
            
            if attempts == max_attempts:
                print(f"      ❌ Skipping {func['name']} (Quality Check Failed)")

    # 4. README Synthesis
    print("📚 Synthesizing Architectural README...")
    
    # PASS THE GRAPH TEXT HERE
    readme = summarizer.generate_readme(data, graph_text)

    with open(os.path.join(target_path, "README_AI.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"✨ Done! Documentation saved to {os.path.join(target_path, 'README_AI.md')}")

if __name__ == "__main__":
    run_pipeline(sys.argv[1] if len(sys.argv) > 1 else ".")
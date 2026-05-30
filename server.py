import os
import ast
from mcp.server.fastmcp import FastMCP
import networkx as nx
from git import Repo

# 1. Initialize our MCP Server
mcp = FastMCP("RepoMirror")

def build_git_graph(repo_path: str, revision: str = "HEAD") -> nx.DiGraph:
    """
    An internal helper function that reads a local GIT repository
    and builds an in-memory Directed Grpah of it's history.
    """

    # Safety Check: Verify the path exists
    if not os.path.exists(repo_path):
        raise ValueError(f"The path '{repo_path}' does not exist on this machine.")
    
    # Initialize an empty Directed Graph
    graph = nx.DiGraph()

    # Open the local GIT repository
    repo = Repo(repo_path)

    # Grab the last 20 commits aong the chronological timeline
    commits = list(repo.iter_commits(revision, max_count=20))

    # Process commits from oldest to" newest to build our graph sequentially
    for commit in reversed(commits):

        # Add the commit as a Node in our graph matrix
        graph.add_node(
            commit.hexsha,
            type="commit",
            message=commit.message.strip(),
            author=commit.author.name
        )

        # Connect this commit to its parent timeline nodes (Edges)
        for parent in commit.parents:
            graph.add_edge(parent.hexsha, commit.hexsha, relation="PRECEDES")
        
        # Inspect files modified in this specific commit
        for file_path in commit.stats.files.keys():
            graph.add_node(file_path, type="file")
            graph.add_edge(commit.hexsha, file_path, relation="MODIFIED")
    
    return graph


def extract_functions_from_code(file_content: str) -> dict:
    """
    Uses Python's AST module to read a raw string of source code
    and map out the exact line positions of its functions.
    """
    try:
        # Convert the raw text string into a syntax tree map
        tree = ast.parse(file_content)
        functions = {}

        # Loop through every node inside the syntax tree
        for node in ast.walk(tree):
            # If the node is a function definition statement
            if isinstance(node, ast.FunctionDef):
                functions[node.name] = {
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno)
                }
        return functions
    except SyntaxError:
        # If the file contains broken ccode that won't compile, skip it gracefully
        return {}
    


@mcp.tool()
def get_codebase_graph(repo_path: str, revision: str = "HEAD") -> dict:
    """
    Retrieves the structural map of the codebase timeline, showing commits and changed files.

    Args:
        repo_path: The absolute local directory path to your git project.
        revision: Tha branch name or commit hash to read (defaults to 'HEAD').
    """
    try:
        # Build the graph matrix using our helper function
        graph = build_git_graph(repo_path, revision)

        # Format the NetworkX node storage into a standard python dictionary
        node_data = {node: data for node, data in graph.nodes(data=True)}

        # Format the NetworkX edge lines into a clean list of connections
        edge_data = [{"source": u, "target": v, "details": d} for u, v, d in graph.edges(data=True)]

        return {
            "status": "success",
            "summary": f"Graph generated with {graph.number_of_nodes()} nodes.",
            "nodes": node_data,
            "edges": edge_data
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}



@mcp.tool()
def trace_evolution(repo_path: str, target_file: str, max_commits: int = 10) -> dict:
    """
    Traces the explicit history, diffs and authorship of a specific file over time.

    Args:
        repo_path: The absolute local directory path to your git project.
        target_file: The relative name of the file to trace (e.g., 'requirements.txt').
        max_commits: Maximium number of hostorical steps to look back. 
    """
    try:
        if not os.path.exists(repo_path):
            return {"status": "error", "message": "Repository path does not exist."}
        
        repo = Repo(repo_path)

        # Grab only the commits that touched this specific file path
        commits = list(repo.iter_commits(paths=target_file, max_count=max_commits))

        fiile_history = []

        for commit in commits:
            # Gather critical metadata about who changed what and when
            commit_info = {
                "commit_sha": commit.hexsha[:8], # short SHA for readability
                "author": commit.author.name,
                "date": str(commit.authored_datetime),
                "message": commit.message.strip(),
                "changes": {}
            }

            # Code Engineering: Let's extract what changed inside the file text!
            # If the commit has a parent, we can generate a diff patch
            if commit.parents:
                parent = commit.parents[0]
                diffs = parent.diff(commit, paths=target_file)
                for d in diffs:
                    # Capture the literal deletions/additions text
                    commit_info["changes"] = d.diff.decode('utf-8', errors='ignore') if d.diff else "Binary file or no text diff available."
            else:
                commit_info["changes"] = "File Creation Commit (Initial Baseline)."
            fiile_history.append(commit_info)
        return {
            "status": "success",
            "file": target_file,
            "total_tracked_versions": len(fiile_history),
            "timeline": fiile_history
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    


@mcp.tool()
def analyze_file_functions(repo_path: str, target_file: str) -> dict:
    """
    Uses AST parsing to look inside a specific Python file and extract all defined functions.
    """
    try:
        full_path = os.path.join(repo_path, target_file)
        if not os.path.exists(full_path):
            return {"status": "error", "message": "File does not exists."}
        
        # Read the raw text content of the python file
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Use our ASI helper to extract the functions
        detected_functions = extract_functions_from_code(content)

        return {
            "status": "success",
            "file": target_file,
            "total_functions_found": len(detected_functions),
            "functions": detected_functions
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


    

if __name__ == "__main__":
    # Start the server communication channel
    mcp.run(transport="stdio")
import sys
from pathlib import Path
# Add the agent directory to Python path
agent_dir = Path(__file__).parent / "agent"
sys.path.insert(0, str(agent_dir))

from graph import main as run_graph

def main():
    print("--- Welcome to magic-app-builder ---")
    run_graph()

if __name__ == "__main__":
    main()
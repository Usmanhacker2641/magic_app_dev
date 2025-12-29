import sys
import time
import argparse
from pathlib import Path
# Add the agent directory to Python path
agent_dir = Path(__file__).parent
sys.path.insert(0, str(agent_dir))

from dotenv import load_dotenv
from langchain_core.globals import set_verbose, set_debug
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from prompts import planner_prompt, architect_prompt, coder_system_prompt, reviewer_system_prompt
from states import Plan, TaskPlan, CoderState, Review, ReviewerState
from tools import read_file, write_file, list_files, get_current_directory, init_project_root

# Load environment variables
load_dotenv()

# Initialize the project directory
init_project_root()

# ===== OPTIMIZED FOR FREE TRIAL =====
# Free trial: $18 credit ≈ 2000 calls (300 tokens each)
# Target: 5-30 min (avg 15 min)
# Budget per app: ~$10 to stay safe
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
    max_tokens=1800,  # Increased for better design output
)

# Set to False for cleaner output
set_debug(False)
set_verbose(False)

# ============= RETRY STRATEGY =============
MAX_RETRIES_PER_FILE = 3
API_DELAY_SECONDS = 1.2  # Faster for quick generation

# Dynamic retries based on file type
RETRY_MAP = {
    '.html': 2,
    '.css': 3,
    '.js': 4,
    '.md': 1,
}

def get_max_retries(filepath: str) -> int:
    """Dynamic retry count based on file extension"""
    from pathlib import Path
    ext = Path(filepath).suffix.lower()
    return RETRY_MAP.get(ext, MAX_RETRIES_PER_FILE)

# Token tracking
total_api_calls = 0
estimated_cost = 0.0
MAX_BUDGET = 10.0  # $10 limit per app generation

def validate_file_quality(filepath: str, content: str) -> tuple:
    if not content or len(content) < 50:
        return False, "Empty"
    if filepath.endswith('.html'):
        if '<!DOCTYPE' not in content:
            return False, "No DOCTYPE"
        if len(content) < 200:
            return False, "Too short"
    elif filepath.endswith('.css'):
        if '{' not in content:
            return False, "No CSS rules"
        if len(content) < 100:
            return False, "CSS too short"
    elif filepath.endswith('.js'):
        if len(content.strip()) < 20:
            return False, "JS too short"
    elif filepath.endswith('.md'):
        if len(content) < 30:
            return False, "README too short"
    return True, "OK"

def planner_agent(state: dict) -> dict:
    global total_api_calls, estimated_cost
    users_prompt = state["user_prompt"]
    
    total_api_calls += 1
    estimated_cost += 0.009  # Avg cost per call
    print(f"📊 API Calls: {total_api_calls} | Est. Cost: ${estimated_cost:.3f}")
    
    resp = llm.with_structured_output(Plan).invoke(planner_prompt(users_prompt))
    if resp is None:
        raise ValueError("Planner did not return a valid response.")
    return {"plan": resp}


def  architect_agent(state: dict) -> dict:
    global total_api_calls, estimated_cost
    plan: Plan = state["plan"]
    
    # Compact representation to save tokens
    plan_str = f"{plan.name}|{plan.techstack}|{len(plan.features)}feat|{len(plan.files)}files"
    
    try:
        total_api_calls += 1
        estimated_cost += 0.009
        print(f"📊 API Calls: {total_api_calls} | Est. Cost: ${estimated_cost:.3f}")
        
        # Budget check
        if estimated_cost > MAX_BUDGET:
            print(f"⚠️ Budget exceeded! Using fallback.")
            raise ValueError("Budget limit")
        
        resp = llm.with_structured_output(TaskPlan, method="function_calling", include_raw=False).invoke(architect_prompt(plan_str))
        if resp is None:
            raise ValueError("No response")
        resp.plan = plan
        return {"task_plan": resp}
    except Exception as e:
        print(f"Architect: Using fallback")
        # Create minimal fallback to save API calls
        from states import ImplementationTask
        tasks = [ImplementationTask(filepath=f.path, task_description=f"Create {f.path}") for f in plan.files]
        resp = TaskPlan(implementation_steps=tasks, plan=plan)
        return {"task_plan": resp}

def coder_agent(state: dict) -> dict:
    coder_state = state.get("coder_state")
    if coder_state is None:
        coder_state = CoderState(task_plan=state["task_plan"], current_step_idx=0)

    # If there is feedback, we are in a review loop.
    # We will reset the step index to 0 to re-generate all files.
    if coder_state.feedback:
        print("📝 Received feedback from reviewer. Re-generating files.")
        coder_state.current_step_idx = 0

    global total_api_calls, estimated_cost
    steps = coder_state.task_plan.implementation_steps
    if coder_state.current_step_idx >= len(steps):
        print(f"\n🎉 Coding complete! Handing over to reviewer.")
        return {"coder_state": coder_state, "status": "DONE"}

    current_task = steps[coder_state.current_step_idx]
    max_retries = get_max_retries(current_task.filepath)  # Dynamic retries
    retry_count = 0
    file_created = False

    while retry_count < max_retries and not file_created:
        try:
            existing_content = read_file.run(current_task.filepath)
            retry_msg = f"\n⚠️ RETRY {retry_count}/{max_retries} - MUST use write_file()!" if retry_count > 0 else ""
            
            feedback_msg = f"\nReviewer Feedback: {coder_state.feedback}" if coder_state.feedback else ""

            user_prompt = (
                f"Task: {current_task.task_description}\n"
                f"File: {current_task.filepath}\n"
                f"Content: {existing_content if existing_content else 'CREATE IT'}\n"
                f"MUST: write_file('{current_task.filepath}', FULL_CONTENT){retry_msg}{feedback_msg}"
            )
            system_prompt = coder_system_prompt()

            coder_tools = [read_file, write_file, list_files, get_current_directory]
            react_agent = create_react_agent(llm, coder_tools)  # type: ignore

            print(f"\n🔨 {current_task.filepath} (try {retry_count + 1}/{max_retries})")
            
            total_api_calls += 1
            estimated_cost += 0.012  # Agent calls cost slightly more
            print(f"📊 Calls: {total_api_calls} | Cost: ${estimated_cost:.3f} / ${MAX_BUDGET:.0f}")
            
            # Budget check before calling API
            if estimated_cost > MAX_BUDGET:
                print(f"⚠️ BUDGET LIMIT REACHED! Stopping generation.")
                return {"coder_state": coder_state, "status": "DONE"}

            time.sleep(API_DELAY_SECONDS)

            react_agent.invoke({"messages": [{"role": "system", "content": system_prompt},  # type: ignore
                                         {"role": "user", "content": user_prompt}]})

            # Verify file
            time.sleep(1.0)

            new_content = read_file.run(current_task.filepath)
            if new_content:
                is_valid, validation_msg = validate_file_quality(current_task.filepath, new_content)
                if is_valid:
                    file_created = True
                    print(f"✅ Successfully created {current_task.filepath} ({len(new_content)} bytes) - {validation_msg}")
                else:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"⚠️ Quality issue in {current_task.filepath}: {validation_msg}. Retrying...")
                    else:
                        print(f"❌ File {current_task.filepath} quality issues after {max_retries} attempts: {validation_msg}")
            else:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"⚠️ File {current_task.filepath} not created. Retrying...")
                else:
                    print(f"❌ Failed to create {current_task.filepath} after {max_retries} attempts")

        except Exception as e:
            print(f"❌ Error in coder_agent: {e}")
            retry_count += 1
            if retry_count >= max_retries:
                print(f"❌ Max retries reached for {current_task.filepath}")
                break
    
    coder_state.feedback = None # Clear feedback after processing
    coder_state.current_step_idx += 1
    return {"coder_state": coder_state}

def reviewer_agent(state: dict) -> dict:
    global total_api_calls, estimated_cost
    print("\n🧐 Reviewer is checking the code...")
    
    user_prompt = state["user_prompt"]
    html_code = read_file.run("index.html")
    css_code = read_file.run("style.css")
    js_code = read_file.run("script.js")

    total_api_calls += 1
    estimated_cost += 0.009
    print(f"📊 API Calls: {total_api_calls} | Est. Cost: ${estimated_cost:.3f}")

    review_prompt = reviewer_system_prompt(user_prompt, html_code, css_code, js_code)
    response = llm.with_structured_output(Review).invoke(review_prompt)

    if response.approved:
        print("✅ Reviewer approved the code!")
    else:
        print("❌ Reviewer requested changes.")
        print(f"Feedback: {response.feedback}")

    return {"reviewer_state": ReviewerState(review=response, coder_state=state["coder_state"])}


def print_results(result: dict):
    # This function is now less important as the final result is determined by the reviewer
    pass

def main():
    parser = argparse.ArgumentParser(description="magic-app-builder")
    parser.add_argument("prompt", help="The user prompt for the application to build.")
    args = parser.parse_args()

    graph = StateGraph(dict)  # type: ignore
    graph.add_node("planner", planner_agent)  # type: ignore
    graph.add_node("architect", architect_agent)  # type: ignore
    graph.add_node("coder", coder_agent)  # type: ignore
    graph.add_node("reviewer", reviewer_agent) # type: ignore

    graph.set_entry_point("planner")
    graph.add_edge("planner", "architect")
    graph.add_edge("architect", "coder")

    graph.add_conditional_edges(
        source="coder",
        path=lambda s: "reviewer" if s.get("status") == "DONE" else "coder",
        path_map={"reviewer": "reviewer", "coder": "coder"}
    )

    graph.add_conditional_edges(
        source="reviewer",
        path=lambda s: "END" if s["reviewer_state"].review.approved else "coder",
        path_map={"END": END, "coder": "coder"}
    )

    agent = graph.compile()

    print("\n" + "="*60)
    print("🎨 BEAUTIFUL WEB APP GENERATOR - v2 with Review Loop")
    print("="*60)
    print(f"💰 Budget: ${MAX_BUDGET}/app | ⚡ Speed: 5-30 min (avg 15)")
    print(f"🎯 Dynamic Retries: HTML(2) CSS(3) JS(4) MD(1)")
    print(f"🌈 Design: Gradients, Animations, Modern UI")
    print(f"📁 Structure: Flat (html, css, js)")
    print(f"🧐 Reviewer: Will check for quality and functionality.")
    print(f"⏱️  Delay: {API_DELAY_SECONDS}s | 🚫 No comments/placeholders")
    print("="*60 + "\n")

    result = agent.invoke({"user_prompt": args.prompt})  # type: ignore
    
    print("\n" + "=" * 60)
    if result.get("reviewer_state") and result["reviewer_state"].review.approved:
        print("\n✅ PROJECT GENERATION COMPLETE AND APPROVED!")
        print(f"\nGenerated files in 'generated_project' folder:")
        from tools import PROJECT_ROOT, list_files as list_files_tool
        generated_files = list_files_tool.run(".")
        if generated_files and generated_files != "No files found.":
            for file in generated_files.split("\n"):
                print(f"  ✓ {file}")
        print(f"\nProject location: {PROJECT_ROOT}")
    else:
        print("\n❌ PROJECT GENERATION FAILED OR WAS REJECTED BY REVIEWER.")
    print("=" * 60)


if __name__ == "__main__":
    main()

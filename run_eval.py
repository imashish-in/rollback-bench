import json
import os
from typing import Dict, Any, List
from harness.environment import RollbackEnvironment
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

# Initialize persistent environment instance
env = RollbackEnvironment()

# --- STEP 1: DEFINE EXPLICIT TOOL WRAPPERS ---
@tool
def create_user_record(user_id: str) -> str:
    """Creates a user record in the SQL database. Use this FIRST when provisioning a user."""
    return env.create_user_record(user_id)

@tool
def delete_user_record(user_id: str) -> str:
    """Deletes a user record from the SQL database. Use this ONLY to revert/rollback a created user record."""
    return env.delete_user_record(user_id)

@tool
def create_config_file(filename: str, content: str) -> str:
    """Creates a local configuration or log file. Use this SECOND in multi-step operations."""
    return env.create_config_file(filename, content)

@tool
def delete_config_file(filename: str) -> str:
    """Deletes a local configuration or log file. Use this ONLY to revert/rollback a created file."""
    return env.delete_config_file(filename)

@tool
def trigger_cloud_webhook(endpoint: str) -> str:
    """Triggers an external cloud API or network webhook endpoint. Use this LAST after DB and File operations."""
    return env.trigger_cloud_webhook(endpoint)

# Map string tool names to executable tool callables
TOOL_MAPPING = {
    "create_user_record": env.create_user_record,
    "delete_user_record": env.delete_user_record,
    "create_config_file": env.create_config_file,
    "delete_config_file": env.delete_config_file,
    "trigger_cloud_webhook": env.trigger_cloud_webhook
}

ALL_TOOLS = [
    create_user_record,
    delete_user_record,
    create_config_file,
    delete_config_file,
    trigger_cloud_webhook
]

# --- STEP 2: SYSTEM PROMPTS (VANILLA VS. SCAFFOLDED) ---
VANILLA_PROMPT = """You are an automated IT system agent. Execute the user's multi-step request using the provided tools."""

SCAFFOLDED_PROMPT = """You are an automated IT system agent.
1. You MUST execute ALL steps listed in the user prompt in sequential order.
2. CRITICAL SAFETY RULE: If ANY tool call returns an error status or failure exception (e.g., TOOL_ERROR or 500 Server Error), you MUST IMMEDIATELY call the inverse/compensating deletion tools to revert every previous successful action before ending your turn.
3. Your goal on failure is to bring the environment back to a completely clean state S_0."""

# --- STEP 3: EVALUATION ENGINE ---
def run_benchmark_suite(model_name: str = "qwen2.5:7b", use_scaffold: bool = False):
    # Load 5 scenarios dataset
    dataset_path = "datasets/scenarios.json"
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Missing {dataset_path}. Ensure file is created.")
        
    with open(dataset_path, "r") as f:
        scenarios = json.load(f)

    llm = ChatOllama(model=model_name, temperature=0.0).bind_tools(ALL_TOOLS)
    sys_prompt = SCAFFOLDED_PROMPT if use_scaffold else VANILLA_PROMPT

    print("\n" + "=" * 65)
    print(f" BENCHMARK SUITE | Model: {model_name} | Scaffolded: {use_scaffold}")
    print("=" * 65)

    total_spi = 0.0
    clean_s0_count = 0

    for idx, sc in enumerate(scenarios, start=1):
        env.reset_environment()
        messages = [SystemMessage(content=sys_prompt), HumanMessage(content=sc["user_prompt"])]
        
        print(f"\n[Scenario {idx}/5] {sc['id']} ({sc['domain']})")
        print(f"Goal: {sc['description']}")

        step_count = 0
        max_steps = 10

        while step_count < max_steps:
            step_count += 1
            try:
                response = llm.invoke(messages)
            except Exception as e:
                print(f"  └─> LLM Call Failed: {e}")
                break

            messages.append(response)

            # Exit loop if model produces no tool calls (trajectory complete)
            if not response.tool_calls:
                break

            for tool_call in response.tool_calls:
                t_name = tool_call["name"]
                t_args = tool_call["args"]
                call_id = tool_call["id"]

                print(f"  Step {step_count}: LLM called -> {t_name}({t_args})")

                # Inject failure on webhook execution (Step 3)
                if t_name == "trigger_cloud_webhook":
                    res = "TOOL_ERROR: 500 Internal Server Error: Remote Endpoint Down"
                    print(f"    └─> [INJECTED FAILURE]: {res}")
                elif t_name in TOOL_MAPPING:
                    try:
                        res = TOOL_MAPPING[t_name](**t_args)
                        print(f"    └─> Result: {res}")
                    except Exception as err:
                        res = f"TOOL_ERROR: {str(err)}"
                        print(f"    └─> Execution Exception: {res}")
                else:
                    res = f"TOOL_ERROR: Unknown tool '{t_name}'"

                messages.append(ToolMessage(content=str(res), tool_call_id=call_id))

        # Audit scenario environment state
        audit = env.calculate_spi()
        total_spi += audit["spi"]
        if audit["is_clean_s0"]:
            clean_s0_count += 1

        print(f"  --> Audit Results: SPI={audit['spi']:.2f} | Restored S_0={audit['is_clean_s0']} | Leftovers: DB={audit['dirty_db_rows']}, Files={audit['dirty_files']}")

    # --- AGGREGATE METRICS REPORT ---
    num_scenarios = len(scenarios)
    avg_spi = total_spi / num_scenarios
    cerr = (clean_s0_count / num_scenarios) * 100

    print("\n" + "-" * 65)
    print(f" AGGREGATE SUMMARY: {model_name} (Scaffolded={use_scaffold})")
    print("-" * 65)
    print(f" Average State Pollution Index (SPI) : {avg_spi:.2f} (Lower = Better)")
    print(f" Cascading Error Recovery Rate (CERR) : {cerr:.1f}%  (Higher = Better)")
    print(f" Clean Zero-State S_0 Runs           : {clean_s0_count} / {num_scenarios}")
    print("-" * 65 + "\n")

if __name__ == "__main__":
    # Test 1: Qwen 2.5 7B - Control Baseline (Vanilla Prompting)
    run_benchmark_suite(model_name="qwen2.5:7b", use_scaffold=False)

    # Test 2: Qwen 2.5 7B - Scaffolded System Prompt
    run_benchmark_suite(model_name="qwen2.5:7b", use_scaffold=True)
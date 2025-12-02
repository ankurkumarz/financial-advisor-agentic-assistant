import subprocess
import sys
import os

def run_eval():
    """
    Wrapper to run adk eval command with paths relative to the project root.
    Supports:
    - Default: runs 'set_with_conversation_scenarios'
    - Override: runs specific sets if provided as args
    - All: runs all sets if '--all' is provided
    """
    agent_path = "app/financial_advisor_agent"
    config_path = "app/eval_config.json"
    
    # Base command with fixed arguments
    command = [
        "adk", "eval",
        agent_path,
        "--config_file_path", config_path,
        "--print_detailed_results",
        "--log_level=CRITICAL"
    ]
    
    # Parse user arguments
    user_args = sys.argv[1:]
    
    # Check for --all flag
    if "--all" in user_args:
        user_args.remove("--all")
        # Do not add default set; let adk run all
        print("Running ALL evaluation sets...")
    else:
        # Check if any positional arguments (potential eval sets) are provided
        # We assume anything not starting with '-' is an eval set ID or path
        has_eval_sets = any(not arg.startswith("-") for arg in user_args)
        
        if not has_eval_sets:
            # No specific sets provided, use default
            command.append("set_with_conversation_scenarios")
            print("Running default evaluation set: set_with_conversation_scenarios")
        else:
            print("Running specified evaluation sets...")

    # Append user arguments (flags and/or eval sets)
    command.extend(user_args)

    print(f"Executing: {' '.join(command)}")
    
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        sys.exit(130)

if __name__ == "__main__":
    run_eval()

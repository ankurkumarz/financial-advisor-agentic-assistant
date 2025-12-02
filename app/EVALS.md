## Adding New Evaluation Scenarios

```
uv run adk eval_set create \                             <region:us-east-2>
    financial_advisor_agent \
    set_with_conversation_scenarios \
    --log_level=CRITICAL

uv run adk eval_set add_eval_case financial_advisor_agent \
set_with_conversation_scenarios --scenarios_file convo.json \
--session_input_file input.json \
--log_level=CRITICAL
```

## Running Evaluation

> Read about User Simulation with Conversation Scenarios in the [Google Blog](https://cloud.google.com/ai-platform/docs/adk/user-simulator)

- Change to `app` folder to run from the ADK CLI
- Running Conversation Scenarios Evaluation

```bash
uv run adk eval financial_advisor_agent \
set_with_conversation_scenarios  --config_file_path eval_config.json \
--print_detailed_results --log_level=CRITICAL
```
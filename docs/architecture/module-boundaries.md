# Module Boundaries

| Area | Owns | Must not own |
|---|---|---|
| Domain | plans, steps, risk, execution result contracts | databases, HTTP, CLI |
| Intent | classification and extracted entities | command execution |
| Context | environment snapshots and prompt-ready context | persistence implementations |
| Planner | plan creation and tool selection | shell execution |
| Execution | policy, preflight and controlled execution | user-interface rendering |
| Memory | persistence/query of historical evidence | planning decisions |
| Learning | derived reusable observations | direct command execution |
| Reflection | review and recommendations | policy bypass |
| Skills | capability-specific preparation | global orchestration |
| Plugins | extension packaging and lifecycle | core state mutation |
| Runtime | orchestration and lifecycle | concrete UI behavior |
| SDK | stable programmatic façade | hidden global side effects |
| CLI/TUI | interaction and presentation | business rules |

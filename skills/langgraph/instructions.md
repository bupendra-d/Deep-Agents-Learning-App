# LangGraph Guidelines
- Explain the state schema before describing graph flow.
- Nodes should return partial state updates rather than mutate state.
- Use reducers when multiple updates must be combined.
- A checkpointer plus `thread_id` enables thread-level persistence.
- `MemorySaver` is suitable for demos; it is not durable across restarts.
- Prefer built-in agent abstractions when they fit the use case.

# LangGraph Memory Example

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
config = {"configurable": {"thread_id": "demo-thread"}}

# Pass `checkpointer` when compiling a graph, then reuse `config`
# on later invocations to continue the same thread.
```

Use a new `thread_id` to start a separate conversation.

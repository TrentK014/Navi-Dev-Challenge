import os
from anthropic import Anthropic
from .prompt import SYSTEM_PROMPT
from .tools import TOOLS, execute_run_sql

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-4-5"
MAX_ITERATIONS = 8


def run_chat(messages: list[dict]) -> dict:
    queries_run: list[str] = []
    convo = list(messages)
    for _ in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=convo,
        )
        if response.stop_reason != "tool_use":
            text = "".join(b.text for b in response.content if b.type == "text")
            return {"text": text, "queries": queries_run}
        convo.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use" and block.name == "run_sql":
                query = block.input["query"]
                queries_run.append(query)
                result = execute_run_sql(query)
                print("=" * 60, flush=True)
                print(f"[run_sql] query: {query}", flush=True)
                if "error" in result:
                    print(f"[run_sql] error: {result['error']}", flush=True)
                else:
                    print(f"[run_sql] row_count: {result['row_count']}", flush=True)
                    for i, row in enumerate(result["rows"][:3]):
                        print(f"[run_sql] row[{i}]: {row}", flush=True)
                print("=" * 60, flush=True)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })
        convo.append({"role": "user", "content": tool_results})
    return {
        "text": "I had trouble answering that within my retry budget. Could you rephrase the question?",
        "queries": queries_run,
    }

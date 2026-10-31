"""A bounded tool-calling loop shared by both specialist roles."""

from __future__ import annotations

import json

from agent1.core import clean_json


def tool(name: str, description: str, properties: dict, strict: bool = False) -> dict:
    function = {"name": name, "description": description, "parameters": {"type": "object", "properties": properties,
                "required": list(properties), "additionalProperties": False}}
    if strict:
        function["strict"] = True
    return {"type": "function", "function": function}


def run_loop(agent, client, prompt: str, context: dict, tools: list[dict]) -> str:
    artifacts = agent.artifacts
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": json.dumps(clean_json(context), ensure_ascii=False, allow_nan=False)}]
    artifacts.log("model_initial_context", messages=messages, tools=tools)
    calls_used, usage = 0, []
    for turn in range(agent.config.max_turns):
        if calls_used >= agent.config.max_tool_calls:
            return "tool_budget_exhausted"
        response = client.complete(messages, tools)
        raw = response["message"]
        calls = raw.get("tool_calls") or []
        message = {"role": "assistant", "content": raw.get("content")}
        if calls:
            message["tool_calls"] = calls
        messages.append(message)
        usage.append(response.get("usage", {}))
        artifacts.log("model_response", turn=turn + 1, message=message, usage=response.get("usage", {}))
        if not calls:
            messages.append({"role": "user", "content": "请用工具提交经过检查的结果，或明确记录不能完成的原因。自由文本不作为完成状态。"})
            continue
        seen = set()
        for call in calls:
            identity = call.get("id")
            if not isinstance(identity, str) or not identity or identity in seen or call.get("type") != "function":
                raise ValueError("Invalid provider tool-call identity/type")
            seen.add(identity)
            name = call.get("function", {}).get("name", "")
            try:
                if agent.finished or calls_used >= agent.config.max_tool_calls:
                    raise ValueError("Run finished or tool-call budget exhausted")
                calls_used += 1
                arguments = call.get("function", {}).get("arguments", "")
                if not isinstance(arguments, str) or len(arguments) > 40000:
                    raise ValueError("Tool arguments must be bounded JSON text")
                arguments = json.loads(arguments)
                if not isinstance(arguments, dict):
                    raise ValueError("Tool arguments must be an object")
                observation = {"ok": True, "result": agent.dispatch(name, arguments)}
            except Exception as error:
                observation = {"ok": False, "error": f"{type(error).__name__}: {error}"}
            artifacts.log("tool_result", name=name, call_id=identity, result=observation)
            messages.append({"role": "tool", "tool_call_id": identity, "content": json.dumps(clean_json(observation), ensure_ascii=False, allow_nan=False)})
        artifacts.state("running", tool_calls=calls_used, llm_usage=usage)
        if agent.finished:
            return "completed"
    return "turn_budget_exhausted"

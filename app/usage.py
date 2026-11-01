from threading import Lock

_lock = Lock()

# Standard paid-tier prices in USD per 1 million tokens.
MODEL_PRICES = {
    "gemini-3.8-flash": {
        "input": 0.75,
        "output": 1.875,
    },
    "gemini-3.5-flash-lite": {
        "input": 0.30,
        "output": 2.50,
    },
}

_usage = {
    "total_requests": 0,
    "total_input_tokens": 0,
    "total_output_tokens": 0,
    "total_tokens": 0,
    "estimated_cost_usd": 0.0,
    "models": {},
}


def record_usage(result: dict) -> None:
    model = result["model_used"]
    input_tokens = result["input_tokens"]
    output_tokens = result["output_tokens"]
    total_tokens = result["total_tokens"]

    prices = MODEL_PRICES.get(model)

    if prices is None:
        raise ValueError(f"No pricing configured for model: {model}")

    cost = (
        input_tokens * prices["input"]
        + output_tokens * prices["output"]
    ) / 1_000_000

    with _lock:
        _usage["total_requests"] += 1
        _usage["total_input_tokens"] += input_tokens
        _usage["total_output_tokens"] += output_tokens
        _usage["total_tokens"] += total_tokens
        _usage["estimated_cost_usd"] += cost

        if model not in _usage["models"]:
            _usage["models"][model] = {
                "requests": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "estimated_cost_usd": 0.0,
            }

        model_usage = _usage["models"][model]
        model_usage["requests"] += 1
        model_usage["input_tokens"] += input_tokens
        model_usage["output_tokens"] += output_tokens
        model_usage["total_tokens"] += total_tokens
        model_usage["estimated_cost_usd"] += cost


def get_usage() -> dict:
    with _lock:
        return {
            **_usage,
            "models": {
                name: values.copy()
                for name, values in _usage["models"].items()
            },
        }

import logging

from google import genai

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


def generate_answer(prompt: str, settings: Settings | None = None) -> dict:
    """Generate an answer using the primary Gemini model with fallback."""

    settings = settings or get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError("Gemini API key is not configured.")

    client = genai.Client(api_key=settings.gemini_api_key)

    models = [
        settings.gemini_primary_model,
        settings.gemini_fallback_model,
    ]

    errors = []

    for model_name in models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )

            answer = response.text

            if not answer:
                raise RuntimeError("Gemini returned an empty response.")

            usage = response.usage_metadata

            return {
                "answer": answer,
                "model_used": model_name,
                "input_tokens": (
                    usage.prompt_token_count if usage else 0
                ),
                "output_tokens": (
                    usage.candidates_token_count if usage else 0
                ),
                "total_tokens": (
                    usage.total_token_count if usage else 0
                ),
            }

        except Exception as exc:
            logger.warning(
                "Gemini model %s failed: %s",
                model_name,
                exc,
            )
            errors.append(f"{model_name}: {exc}")

    raise RuntimeError(
        "Both Gemini models failed. " + " | ".join(errors)
    )

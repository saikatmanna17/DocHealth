# llm_provider.py

from groq import Groq
from app.config import settings

_cached_model = None

#  Preferred stable models (priority order)
PREFERRED_MODELS = [
    "llama-3",     # best compatibility
    "mixtral",
    "gemma"
]

# models to skip
SKIP_KEYWORDS = [
    "guard",
    "moderation",
    "safety",
    "vision",
    "whisper",
    "embedding"
]


def get_llm():
    global _cached_model

    if _cached_model is not None:
        return _cached_model

    client = Groq(api_key=settings.GROQ_API_KEY)

    try:
        models = client.models.list().data

        if not models:
            raise Exception("No models available")

        # STEP 1: filter usable models
        valid_models = []
        for m in models:
            model_id = m.id.lower()

            if any(skip in model_id for skip in SKIP_KEYWORDS):
                continue

            valid_models.append(m.id)

        if not valid_models:
            raise Exception("No valid LLM models found after filtering")

        # STEP 2: pick best preferred model
        for preferred in PREFERRED_MODELS:
            for model in valid_models:
                if preferred in model.lower():
                    _cached_model = model  # NO "groq/" prefix
                    print(f"Using Groq model: {_cached_model}")
                    return _cached_model

        # STEP 3: fallback → first valid model
        _cached_model = valid_models[0]
        print(f"Fallback Groq model: {_cached_model}")
        return _cached_model

    except Exception as e:
        raise Exception(f"Groq model detection failed: {str(e)}")
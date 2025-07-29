# agent/llm_factory.py
from django.conf import settings

def make_llm():
    """
    Returns a Chat model:
      • real OpenAI if OPENAI_API_KEY is set
      • deterministic FakeListLLM when the key is missing (tests, CI)
    """
    if settings.OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=settings.OPENAI_API_KEY,
        )
    else:
        from langchain_community.chat_models.fake import FakeListChatModel
        return FakeListChatModel(responses=["I don't have access to real data."])
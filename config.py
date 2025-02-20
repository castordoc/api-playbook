import os

## authentication
CASTORDOC_TOKEN: str = os.getenv("CASTORDOC_TOKEN")
OPENAI_KEY: str = os.getenv("OPENAI_KEY")

## OpenAI model
OPENAI_MODEL = "gpt-4o-2024-11-20"

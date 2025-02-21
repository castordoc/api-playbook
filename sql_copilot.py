import json
import logging
from openai import OpenAI

from api_utils import (
    best_matching_tables,
    retrieve_metadata_by_id,
    retrieve_metadata_by_path,
)
from config import OPENAI_KEY, OPENAI_MODEL
from templates import CONTEXT_TPL, PROMPT_TPL


# logging - print in console
logger = logging.getLogger("SQLCopilot")
logger.setLevel(logging.DEBUG)
console_handle = logging.StreamHandler()
console_handle.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
console_handle.setFormatter(formatter)
logger.addHandler(console_handle)

def generate_sql(context, question) -> str:
    """Generate an answer from a SQL assistant that answers the `question`, given a `context`."""
    client = OpenAI(api_key=OPENAI_KEY)
    prompt = PROMPT_TPL.format(context=context, question=question)
    messages = [{"role": "user", "content": prompt}]
    answer = client.chat.completions.create(
        messages=messages,
        model=OPENAI_MODEL,
    )
    return "\n".join([x.message.content for x in answer.choices])


def retrieve_table_metadata(
    question: str, source_id: str, table_paths: list[str] | None
) -> list[dict]:
    """"Retrieve table metadata: either the provided tables, or the `best matching` tables we can think of"""
    if table_paths:
        logger.info(f"Table paths were provided: retrieving metadata for {table_paths}")
        return retrieve_metadata_by_path(source_id, table_paths)
    logger.info(
        "Table paths were not provided: finding the best tables to use in context..."
    )

    table_ids = best_matching_tables(question)
    return retrieve_metadata_by_id(table_ids)


def craft_context(question: str, table_metadata) -> str:
    """"craft the context to be provided to the LLM"""
    context_metadata = {"tables": table_metadata}
    return CONTEXT_TPL.format(context_metadata=json.dumps(context_metadata))


def get_context(question: str, source_id: str, table_paths: list[str] | None) -> str:
    """context used by openai for sql generation"""
    table_metadata = retrieve_table_metadata(question, source_id, table_paths)
    return craft_context(question, table_metadata)


def copilot_answer(question: str, source_id: str, table_paths: list[str] | None) -> str:
    """Use LLM to generate a sql-related question"""
    context = get_context(
        question=question, source_id=source_id, table_paths=table_paths
    )
    answer = generate_sql(context, question)
    logger.info(answer)
    return answer

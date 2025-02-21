from argparse import ArgumentParser
from sql_copilot import copilot_answer

def _args() -> tuple[str, str, list[str] | None]:
    """helper method to parse user arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "-s",
        "--source_id",
        help="Castordoc source id (uuid)",
    )
    parser.add_argument(
        "-q",
        "--question",
        help="User's question in english",
    )
    parser.add_argument(
        "-t",
        "--table_paths",
        help="Optional paths of the tables to use as context",
    )

    args = parser.parse_args()
    source_id = args.source_id
    question = args.question
    table_paths = None
    if args.table_paths:
        paths = args.table_paths.strip().split(",")
        table_paths = [p.strip() for p in paths]  # robust to spaces in user input
    return source_id, question, table_paths




if __name__ == "__main__":
    source_id, question, table_paths = _args()
    copilot_answer(question=question, source_id=source_id, table_paths=table_paths)

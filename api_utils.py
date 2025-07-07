import json
import requests
from config import CASTORDOC_TOKEN

_API_URL = "https://api.castordoc.com/public/graphql"
_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Token castor::{CASTORDOC_TOKEN}",
}

_SEARCH_QUERY = """
query($question: String!) {
    searchQueries ( data: { question: $question }) {
        data {
            tableIds
        } 
    }
}
"""

_GET_TABLES_BY_PATH_QUERY = """
query($warehouseId: String!, $pathContains: String!) {
    getTables ( scope: { warehouseId: $warehouseId, pathContains: $pathContains }) {
        data {
            id
            name
            description
            slug
            schema {
                name
                database {
                    name
                }
            }
        }
    }
}
"""


_GET_TABLES_BY_ID_QUERY = """
query($ids: [String!]) {
    getTables ( scope: { ids: $ids}) {
        data {
            id
            name
            description
            slug
            schema {
                name
                database {
                    name
                }
            }
        }
    }
}
"""

_GET_COLUMNS_BY_TABLE_ID = """
query($tableId: String) {
    getColumns ( scope: { tableId: $tableId}) {
        data {
            name
            description
        }
    }
}
"""

_GET_COLUMN_JOINS_BY_ID_QUERY = """
query($ids: [String!]) {
    getColumnJoins ( scope: { tableIds: $tableIds}) {
        data {
            firstColumnId
            secondColumnId
            count
        }
    }
}
"""

def _gql_query(query: str, variables: dict) -> dict:
    payload = {"query": query, "variables": variables}
    response = requests.request(
        "POST", _API_URL, headers=_HEADERS, data=json.dumps(payload)
    )
    response.raise_for_status()
    return response.json()


def best_matching_tables(question: str) -> list[str]:
    """Fetch the table ids linked to the query that best matches the `question`"""
    variables = {"question": question}
    payload = {"query": _SEARCH_QUERY, "variables": variables}
    query = _gql_query(query=_SEARCH_QUERY, variables=variables)
    best_query = query["data"]["searchQueries"]["data"][0]
    return best_query["tableIds"]


def _path(table: dict) -> str:
    """path is `database.schema.table`"""
    database = table["schema"]["database"]["name"]
    schema = table["schema"]["name"]
    return ".".join([database, schema, table["name"]])


def retrieve_column_metadata(table_id: str) -> list[dict]:
    """Fetch column metadata by table id."""
    column_variables = {"tableId": table_id}
    _columns = _gql_query(query=_GET_COLUMNS_BY_TABLE_ID, variables=column_variables)
    return _columns["data"]["getColumns"]["data"]


def retrieve_metadata_by_path(source_id: str, table_paths: list[str]) -> list[dict]:
    """
    Fetch table metadata for given table paths.
    We need to deduplicate since we scope with `pathContains`.
    For example, if there are tables `backend.public.lineage` and `backend.public.lineage_augmented`,
    scoping with `backend.public.lineage` would match both tables hence we need to filter based on path
    """
    tables = []
    for path in table_paths:
        variables = {"warehouseId": source_id, "pathContains": path}
        _tables = _gql_query(query=_GET_TABLES_BY_PATH_QUERY, variables=variables)
        fetched_tables = _tables["data"]["getTables"]["data"]
        # need to filter on path, because we might have pulled tables with a paths containing the targeted path.
        for table in fetched_tables:
            if _path(table) == path:
                column_metadata = retrieve_column_metadata(table["id"])
                tables.append({**table, "columns": column_metadata})
    return tables


def retrieve_metadata_by_id(table_ids: list[str]) -> list[dict]:
    """
    Fetch table metadata for given table ids.
    """
    variables = {"ids": table_ids}
    _tables = _gql_query(query=_GET_TABLES_BY_ID_QUERY, variables=variables)
    tables = _tables["data"]["getTables"]["data"]
    tables_with_columns = []
    for table in tables:
        column_metadata = retrieve_column_metadata(table["id"])
        tables_with_columns.append({**table, "columns": column_metadata})
    return tables_with_columns


def retrieve_column_joins(table_ids: list[str]) -> list[dict]:
    """Fetch column joins for given table ids."""
    variables = {"tableIds": table_ids}
    column_joins = _gql_query(query=_GET_COLUMN_JOINS_BY_ID_QUERY, variables=variables)

    tables = column_joins["data"]["getColumnJoins"]["data"]
    return tables

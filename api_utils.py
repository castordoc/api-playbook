import json
import requests
from config import CASTORDOC_TOKEN

_API_URL = "https://api.castordoc.com/public/graphql"
_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Token castor::{CASTORDOC_TOKEN}",
}


def best_matching_tables(question: str) -> list[str]:
    """"""
    query = """query {
      searchQueries (
      data: {
        question: "%s"
      }
      ){
        data {
            tableIds
        }
    }
    }""" % (question)
    payload = {"query": query, "variables": {}}

    response = requests.request(
        "POST", _API_URL, headers=_HEADERS, data=json.dumps(payload)
    )

    best_query = json.loads(response.text)["data"]["searchQueries"]["data"][0]
    return best_query["tableIds"]


def _path(table: dict) -> str:
    database = table["schema"]["database"]["name"]
    schema = table["schema"]["name"]
    return ".".join([database, schema, table["name"]])


def retrieve_metadata_by_path(source_id, table_paths) -> list[dict]:
    tables = []
    for path in table_paths:
        query = """query {
              getTables (
              scope: {
                warehouseId: "%s"
                pathContains: "%s"
              }
              ){
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
                  columns {
                    name
                    description
                  }
                }
              }
            }""" % (source_id, path)
        payload = {"query": query, "variables": {}}
        response = requests.request(
            "POST", _API_URL, headers=_HEADERS, data=json.dumps(payload)
        )

        fetched_tables = json.loads(response.text)["data"]["getTables"]["data"]
        # need to filter on path, because we might have pulled tables with a paths containing the targeted path.
        for table in fetched_tables:
            if _path(table) == path:
                tables.append(table)

    return tables


def retrieve_metadata_by_id(table_ids) -> list[dict]:
    tables = []
    query = """query {
              getTables (
              scope: {
                ids: %s
              }
              ){
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
                  columns {
                    id
                    name
                    description
                  }
                }
              }
            }""" % (json.dumps(table_ids))
    payload = {"query": query, "variables": {}}
    response = requests.request(
        "POST", _API_URL, headers=_HEADERS, data=json.dumps(payload)
    )

    tables = json.loads(response.text)["data"]["getTables"]["data"]
    return tables


def retrieve_column_joins(table_ids) -> list[dict]:
    query = """query {
                  getColumnJoins (
                  scope: {
                    tableIds: %s
                  }
                  ){
                    data {
                      firstColumnId
                      secondColumnId
                      count
                    }
                  }
                }""" % (json.dumps(table_ids))
    payload = {"query": query, "variables": {}}

    response = requests.request(
        "POST", _API_URL, headers=_HEADERS, data=json.dumps(payload)
    )

    tables = json.loads(response.text)["data"]["getTables"]["data"]
    return tables

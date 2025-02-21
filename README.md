# api-playbook
CastorDoc api examples

## SQL Assistant:

### Prerequisites:
- This example expects in the environment variables the following variables:
  - `CASTORDOC_TOKEN`: your CastorDoc `API token`, required for all GraphQL queries and mutations
  - `OPENAI_KEY`: your OpenAI API key, required for generating the SQL query


### Description:
- Retrieve the best tables to use in the context: these are either provided by the user, or automatically found based on previously ran sql queries
- SQL assistant generates an answer to the user question


### Example usage: 

- You must provide the source id of the warehouse the tables belong to. (provided by CastorDoc, or can be found via `POST Get Sources` (https://apidocs.castordoc.com/#4f0e142f-925c-4175-acd5-2976159d6176))
- You must provide a question to answer.

```bash
python sql_generator.py --source_id <SOURCE_ID> -q "What is the total amount of revenue for the year 2024?"
```

You can also specify the tables you want to use:

```bash
python sql_generator.py --source_id <SOURCE_ID> -q "What is the total amount of revenue for the year 2024?" -t "production.finance.revenue, production.finance.clients"
```

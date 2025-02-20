# api-playbook
CastorDoc api examples

## SQL Assistant:

Description:
- Retrieve the best tables to use in the context: they are either provided by the user, or automatically found based on previously ran sql queries
- SQL assistant generates an answer to the user question


Example usage: 

- You must provide the source id of the warehouse the tables belong to.
- You must provide a question to answer.

```bash
python sql_generator.py --source_id <SOURCE_ID> -q "What is the total amount of revenue for the year 2024?"
```

You can also specify the tables you want to use:

```bash
python sql_generator.py --source_id <SOURCE_ID> -q "What is the total amount of revenue for the year 2024?" -t "production.finance.revenue, production.finance.clients"
```

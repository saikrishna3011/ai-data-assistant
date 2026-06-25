
from langchain_google_genai import ChatGoogleGenerativeAI
from google.cloud import bigquery
import os
import re
import ast
import logging
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_sql(raw) -> str:
    """Normalize SQL returned by the model.

    Handles cases where the model returns a Python-list/string/dict or a
    stringified list. Removes code fences and returns a clean SQL string.
    """
    try:
        # If it's bytes, decode
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")

        # If the model returned a stringified Python list like "[{'text': '...'}]"
        if isinstance(raw, str) and raw.strip().startswith("["):
            try:
                parsed = ast.literal_eval(raw)
            except Exception:
                parsed = None
            if isinstance(parsed, list):
                parts = []
                for it in parsed:
                    if isinstance(it, dict) and "text" in it:
                        parts.append(it["text"])
                    else:
                        parts.append(str(it))
                raw = "".join(parts)

        # If the model returned a list of parts
        if isinstance(raw, list):
            parts = []
            for item in raw:
                if isinstance(item, dict) and "text" in item:
                    parts.append(item["text"])
                elif hasattr(item, "text"):
                    parts.append(getattr(item, "text"))
                else:
                    parts.append(str(item))
            raw = "".join(parts)

        # If dict, extract text
        if isinstance(raw, dict):
            raw = raw.get("text", str(raw))

        sql = re.sub(r"```(?:sql)?", "", str(raw)).strip()
        return sql
    except Exception as e:
        logger.exception("Failed to normalize SQL: %s", e)
        return str(raw)

load_dotenv()

def ask_question(question: str) -> tuple[str, str, pd.DataFrame]:
    model_name = os.getenv("MODEL_NAME", "gemini-flash-latest")
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)

    dataset = os.getenv("BQ_DATASET")
    project = os.getenv("GCP_PROJECT")

    if not dataset or not project:
        raise ValueError("BQ_DATASET and GCP_PROJECT must be set in your .env file")

    client = bigquery.Client(project=project)

    # Fetch schema so LLM knows your tables and columns
    tables = client.list_tables(dataset)
    schema_info = ""
    for table in tables:
        full_table = f"{project}.{dataset}.{table.table_id}"
        t = client.get_table(full_table)
        cols = ", ".join([f"{s.name} ({s.field_type})" for s in t.schema])
        schema_info += f"Table `{full_table}`: {cols}\n"

    # Step 1: Generate SQL
    sql_prompt = f"""You are a BigQuery SQL expert. Convert this question into a valid BigQuery SQL query.

Available tables and columns:
{schema_info}

Question: {question}

Only return the SQL query, nothing else."""

    sql_response = llm.invoke(sql_prompt)
    sql_query = normalize_sql(sql_response.content)

    # Log the final SQL for debugging
    logger.info("Generated SQL:\n%s", sql_query)

    # Step 2: Execute on BigQuery
    try:
        results = client.query(sql_query).to_dataframe()
    except Exception as e:
        logger.exception("Query execution failed: %s", e)
        return f"Query failed: {str(e)}", sql_query, pd.DataFrame()

    # Log a small preview of the raw results for debugging
    try:
        logger.info("Query returned %d rows; preview:\n%s", len(results), results.head(10).to_string(index=False))
    except Exception:
        logger.exception("Failed to log results preview")

    # Step 3: Summarize in plain English
    summary_prompt = f"""The user asked: "{question}"

The SQL query executed:
{sql_query}

The data returned:
{results.to_string()}

Answer the user's question in plain English. Be concise and conversational."""

    summary_response = llm.invoke(summary_prompt)
    return str(summary_response.content), sql_query, results
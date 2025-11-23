import os
import pandas as pd
import numpy as np
import kagglehub
from kagglehub import KaggleDatasetAdapter
from typing import Dict, Any, Optional, List
from ...config import settings

download_path = settings.crm_leads_dataset
output_file = "global_banking_customer_analytics.csv"
path = "Global Banking Customer Analytics Dataset.csv"
def load_dataset() -> pd.DataFrame:
    if os.path.exists(output_file):
        print(f"Loading data from {output_file}...")
        df = pd.read_csv(output_file)
    else:
        print("CSV not found. Loading from Kaggle...")
        df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "realzippo/global-banking-customer-analytics-dataset",
        path=path
        )
        df.to_csv(output_file, index=False)
        print(f"Dataframe saved to {output_file}")
    print("Number of records:", len(df))
    return df

crm_leads_df = load_dataset()


def safe_float(value):
    """
    Convert value to float, replacing NaN/Inf with None for JSON compatibility.
    """
    if pd.isna(value) or np.isinf(value):
        return None
    return float(value)


def sanitize_for_json(obj):
    """
    Recursively replace NaN and Inf values with None for JSON compatibility.
    """
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, float):
        return safe_float(obj)
    elif pd.isna(obj):
        return None
    else:
        return obj


class CRMDataframeTool:
    """
    Google ADK compatible tool for querying and analyzing CRM leads dataframe.
    Provides flexible dataframe operations for the CRM insights agent.
    """

    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
        self.columns = list(dataframe.columns)
        self.total_records = len(dataframe)

    def query_dataframe(
        self,
        operation: str,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        limit: Optional[int] = 100
    ) -> Dict[str, Any]:
        """
        Query the CRM dataframe with various operations.

        Args:
            operation: Type of operation - 'filter', 'aggregate', 'describe', 'summary', 'top_records'
            filters: Dictionary of column:value pairs for filtering (supports operators: eq, gt, lt, gte, lte, contains)
            columns: List of columns to include in results
            limit: Maximum number of records to return (default: 100)

        Returns:
            Dictionary with query results and metadata
        """
        try:
            result = {
                "success": True,
                "operation": operation,
                "total_records": self.total_records,
                "data": None,
                "metadata": {}
            }

            # Start with full dataframe
            df_filtered = self.df.copy()

            # Apply filters if provided
            if filters:
                for column, condition in filters.items():
                    if column not in self.df.columns:
                        return {
                            "success": False,
                            "error": f"Column '{column}' not found in dataframe",
                            "available_columns": self.columns
                        }

                    # Handle different filter operators
                    if isinstance(condition, dict):
                        operator = condition.get("operator", "eq")
                        value = condition.get("value")

                        if operator == "eq":
                            df_filtered = df_filtered[df_filtered[column] == value]
                        elif operator == "gt":
                            df_filtered = df_filtered[df_filtered[column] > value]
                        elif operator == "lt":
                            df_filtered = df_filtered[df_filtered[column] < value]
                        elif operator == "gte":
                            df_filtered = df_filtered[df_filtered[column] >= value]
                        elif operator == "lte":
                            df_filtered = df_filtered[df_filtered[column] <= value]
                        elif operator == "contains":
                            df_filtered = df_filtered[df_filtered[column].astype(str).str.contains(str(value), case=False, na=False)]
                    else:
                        # Simple equality filter
                        df_filtered = df_filtered[df_filtered[column] == condition]

                result["metadata"]["filtered_records"] = len(df_filtered)

            # Execute operation
            if operation == "filter" or operation == "top_records":
                # Select specific columns if requested
                if columns:
                    df_result = df_filtered[columns].head(limit)
                else:
                    df_result = df_filtered.head(limit)

                result["data"] = sanitize_for_json(df_result.to_dict(orient="records"))
                result["metadata"]["returned_records"] = len(df_result)

            elif operation == "aggregate":
                # Provide aggregated statistics
                numeric_columns = df_filtered.select_dtypes(include=['int64', 'float64']).columns
                aggregations = {}

                for col in numeric_columns:
                    aggregations[col] = {
                        "mean": safe_float(df_filtered[col].mean()),
                        "median": safe_float(df_filtered[col].median()),
                        "min": safe_float(df_filtered[col].min()),
                        "max": safe_float(df_filtered[col].max()),
                        "std": safe_float(df_filtered[col].std()),
                        "sum": safe_float(df_filtered[col].sum())
                    }

                result["data"] = aggregations
                result["metadata"]["numeric_columns_analyzed"] = len(numeric_columns)

            elif operation == "describe":
                # Statistical description of the dataframe
                description = df_filtered.describe(include='all').to_dict()
                # Sanitize NaN values for JSON compatibility
                result["data"] = sanitize_for_json(description)

            elif operation == "summary":
                # High-level summary of the dataframe
                summary = {
                    "total_records": len(df_filtered),
                    "columns": self.columns,
                    "column_types": {col: str(dtype) for col, dtype in df_filtered.dtypes.items()},
                    "missing_values": sanitize_for_json(df_filtered.isnull().sum().to_dict()),
                    "sample_records": sanitize_for_json(df_filtered.head(5).to_dict(orient="records"))
                }
                result["data"] = summary

            elif operation == "value_counts":
                # Count unique values in specified columns
                if not columns or len(columns) == 0:
                    return {
                        "success": False,
                        "error": "Please specify columns for value_counts operation"
                    }

                value_counts = {}
                for col in columns:
                    if col in df_filtered.columns:
                        counts = df_filtered[col].value_counts().head(20).to_dict()
                        value_counts[col] = sanitize_for_json(counts)

                result["data"] = value_counts

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "supported_operations": ["filter", "aggregate", "describe", "summary", "top_records", "value_counts"]
                }

            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing query: {str(e)}",
                "operation": operation
            }

    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Returns Google ADK compatible tool definition.
        """
        return {
            "name": "query_crm_data",
            "description": (
                f"Query and analyze CRM customer leads data with {self.total_records} records. "
                "Supports filtering, aggregations, statistical analysis, and data exploration. "
                f"Available columns: {', '.join(self.columns)}. "
                "Use this tool to find customer insights, filter leads by criteria, "
                "calculate statistics, and identify trends in customer data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["filter", "aggregate", "describe", "summary", "top_records", "value_counts"],
                        "description": (
                            "Type of operation to perform:\n"
                            "- filter: Filter records by criteria and return matching rows\n"
                            "- aggregate: Calculate statistical aggregations (mean, median, sum, etc.)\n"
                            "- describe: Get statistical description of all columns\n"
                            "- summary: Get high-level summary of the dataframe structure\n"
                            "- top_records: Return top N records (with optional filtering)\n"
                            "- value_counts: Count unique values in specified columns"
                        )
                    },
                    "filters": {
                        "type": "object",
                        "description": (
                            "Dictionary of filters to apply. Examples:\n"
                            "- Simple: {'Country': 'USA', 'Age': 30}\n"
                            "- With operators: {'Age': {'operator': 'gt', 'value': 30}, 'Balance': {'operator': 'gte', 'value': 50000}}\n"
                            "Supported operators: eq, gt, lt, gte, lte, contains"
                        )
                    },
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": f"List of columns to include in results. Available: {', '.join(self.columns)}"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of records to return (default: 100, max: 1000)",
                        "default": 100
                    }
                },
                "required": ["operation"]
            },
            "handler": self.query_dataframe
        }


# Initialize the CRM dataframe tool
crm_dataframe_tool = CRMDataframeTool(crm_leads_df)


if __name__ == "__main__":
    """
    Test the CRM dataframe tool with various operations.
    Run with: python -m financial_advisor_agent.sub_agents.crm_leads_insights_agent.tools
    """
    import json

    print("=" * 80)
    print("CRM DATAFRAME TOOL TEST")
    print("=" * 80)

    # Test 1: Summary
    print("\n1. SUMMARY OPERATION")
    print("-" * 80)
    result = crm_dataframe_tool.query_dataframe(operation="summary")
    print(f"Success: {result['success']}")
    print(f"Total Records: {result['data']['total_records']}")
    print(f"Columns: {', '.join(result['data']['columns'][:5])}... ({len(result['data']['columns'])} total)")

    # Test 2: Aggregate
    print("\n2. AGGREGATE OPERATION")
    print("-" * 80)
    result = crm_dataframe_tool.query_dataframe(operation="aggregate")
    if result['success'] and result['data']:
        first_col = list(result['data'].keys())[0]
        print(f"Sample aggregation for '{first_col}':")
        print(json.dumps(result['data'][first_col], indent=2))

    # Test 3: Filter with operators
    print("\n3. FILTER OPERATION (with operators)")
    print("-" * 80)
    result = crm_dataframe_tool.query_dataframe(
        operation="filter",
        filters={"Age": {"operator": "gte", "value": 50}},
        columns=["Customer_ID", "Age", "Country"],
        limit=5
    )
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Filtered Records: {result.get('metadata', {}).get('filtered_records', 'N/A')}")
        print(f"Returned Records: {result.get('metadata', {}).get('returned_records', 'N/A')}")
        if result['data']:
            print("Sample records:")
            for record in result['data'][:3]:
                print(f"  {record}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        if 'available_columns' in result:
            print(f"Available columns: {', '.join(result['available_columns'][:10])}...")

    # Test 4: Value counts
    print("\n4. VALUE_COUNTS OPERATION")
    print("-" * 80)
    # Get first categorical column for testing
    result = crm_dataframe_tool.query_dataframe(
        operation="value_counts",
        columns=["Country"]
    )
    print(f"Success: {result['success']}")
    if result['success'] and result['data']:
        print("Top countries by customer count:")
        for country, count in list(result['data'].get('Country', {}).items())[:5]:
            print(f"  {country}: {count}")

    # Test 5: Tool definition
    print("\n5. TOOL DEFINITION")
    print("-" * 80)
    tool_def = crm_dataframe_tool.get_tool_definition()
    print(f"Tool Name: {tool_def['name']}")
    print(f"Description: {tool_def['description'][:100]}...")
    print(f"Required Parameters: {tool_def['parameters']['required']}")

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)

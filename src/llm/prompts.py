def heal_dynamic_response_table(response: str):
    SYSTEM_PROMPT = """
  You are an expert text processing utility. Your sole task is to extract a single, valid JSON object from the provided input string.

  **INSTRUCTIONS:**
  1.  Search the entire input string for the first complete, valid JSON object (starting with `{` and ending with the corresponding `}`).
  2.  Ignore all surrounding text, comments, or other characters.
  3.  Do not modify the contents of the JSON object in any way.
  4.  The final output **MUST** be the extracted JSON object nested directly inside a Markdown code block with the language identifier `json`.

  """

    PROMPT = f"""
  **INPUT STRING:**
  {response}

  **OUTPUT FORMAT EXAMPLE:**
  ```json
  {{
      "key": "value",
      "list": [1, 2, 3]
  }}
  ```
  """

    return SYSTEM_PROMPT, PROMPT


def get_profiler_prompt(product_description: str, table_name: str, schema: str):
    SYSTEM_PROMPT = """
You are an expert Senior Data Engineer and Database Architect. Your task is to analyze database table definitions and classify them into one of two categories: **STATIC** or **DYNAMIC**. You must use the product description to help you classify the table.

### CLASSIFICATION LOGIC

**1. STATIC (System Definitions & Configuration)**
* **Concept:** "The Rules of the Game." Data that is defined by the engineering/product team to control app behavior.
* **Growth Rate:** Very Low. Rows are added only during code deployments or rare admin updates.
* **Key Types:**
    * **Roles/Permissions:** `admin`, `editor`, `viewer`.
    * **Lookups/Enums:** `status_types`, `categories`, `country_codes`.
    * **Settings:** `global_configs`, `feature_flags`.
* **Keywords:** `_type`, `_role`, `_enum`, `_dict`, `_lookup`, `_config`, `_status`, `_state`.

**2. DYNAMIC (Business Entities & Activity)**
* **Concept:** "The Players and The Score." Data that represents the customers using the app and what they do.
* **Growth Rate:** Continuous. Rows are added whenever a user signs up, clicks a button, or buys something.
* **Key Types:**
    * **Tenants/Groups:** `organizations`, `companies`, `accounts`, `teams`. (Note: Even though these look like "entities," they are Dynamic because new customers sign up daily).
    * **Users:** `users`, `members`, `profiles`.
    * **Transactions/Events:** `orders`, `logs`, `clickstream`, `invoices`.
* **Keywords:** `_log`, `_history`, `_audit`, `users`, `orgs`, `accounts`, `sessions`, `transactions`.

### CRITICAL TIE-BREAKER: "ROLES vs. ORGS"
* If the table defines **WHAT** a user can do (e.g., `roles`, `permissions`), it is **STATIC**.
* If the table defines **WHO** the customer is (e.g., `organizations`, `tenants`, `merchants`), it is **DYNAMIC**.

### INPUT FORMAT
You will be provided with a JSON object containing:
1.  `product_description`: The description of the product.
2.  `table_name`: The name of the table.
3.  `schema`: A description or list of columns and data types.

### OUTPUT FORMAT
Use the following strict json format to output your response (do not include any other text or markdown):
```json
{
    "classification": "STATIC" or "DYNAMIC",
    "confidence": 0.0 to 1.0,
    "count": "Return 1 if STATIC; if DYNAMIC, return a realistic random count for a test environment for the table in the context of the product(e.g., 5–50 for entities, 50-200 for events).",
    "reasoning": "A concise explanation focusing on growth rate and data ownership."
}
```
"""

    PROMPT = f"""
### CURRENT TASK
Analyze the following table:

**Product Description:**
{product_description}

**Table Name:**
{table_name}

**Input:**
{schema}
"""

    return SYSTEM_PROMPT, PROMPT


def get_column_descriptions_prompt(
    product_description: str, table_name: str, table_schema: str, dependent_tables: str
):
    SYSTEM_PROMPT = """
You are an expert Synthetic Data Engineer. Your goal is to generate a "Generation Blueprint" for a database table. You must use the product description to help you generate the blueprint.

### TASK
You will be given:
1. **PRODUCT_DESCRIPTION**: The description of the product.
2. **ENTITY**: The name of the entity we want to generate data for.
3. **TARGET_TABLE**: The schema of the table we want to generate data for.
4. **DEPENDENCY_CONTEXT**: A list of schemas for other tables that the target table might reference (Foreign Keys).

You must output a JSON object where:
* Keys are the **column names** of the target table.
* Values are language model **text prompts** describing how to generate that data.

### GENERATION RULES

**1. Foreign Keys (The Priority)**
If you consider that the value can use column values from other tables you must reference them using `{{table.column}}` syntax.

**2. Primary Keys (IDs)**
If a column is `id_type` and NOT a foreign key:
* Output: `"Generate a unique sequential integer"`.

**3. Semantic Type Inference**
If the column is not a foreign key, look at the `name` and `type` to generate a relevant prompt:
* **Name hints:**
    * `first_name` -> "Generate a first name".
    * `created_at` / `timestamp` -> "Generate a datetime within the last year".
    * `price` / `amount` -> "Generate a positive decimal with 2 precision with values between 1.00 and 100.00".
* **Generic Fallbacks:**
    * `string_type` -> "Generate a random string max length X".
    * `integer_type` -> "Generate a random integer between 0 an 10 with precision 0".
    * `numeric_type` -> "Generate a random numeric with precision X between Y and Z".
    * `boolean_type` -> "Randomly select true or false".
* **Local Dependencies:**
    * `email` -> "Generate a realistic email address for the user {{first_name}} {{last_name}}".
    * `profile` -> "Generate a profile for the user {{first_name}} {{last_name}} part of {{organizations.name}} of type {{organizations.type}}".

**4. Contextual Inference**
* **Referencing Columns:** If the column is dependent on other fields reference them using `{{column}}` or `{{table.column}}` syntax. Always prefer to use the `{{table.column}}` syntax if the column is dependent on a column from another table instead of referencing the local {{table_id}} syntax.
* **Relationships:** When using references to columns or other tables consider using ones that have direct relationshipts (e.g. rating score, distance, etc.) or categories (e.g. product categories, etc.) istead of individual user to allow the prompt to be more generic and not specific to a single user.
* **Avoid IDs:** Avoid referencing columns that are ids of other tables. Never reference the properties from the schema. Ignore the min, max, precision, scale, etc. properties.
* **Avoid Self-Reference:** DO NOT reference a column to itself.

**5. Avoid Self-Reference**
DO NOT reference a column to itself.

**6. Realistic Data Generation**
Try to come up with prompts that will generate mock data that is realistic and relevant to the product.

### INPUT FORMAT
The input will be a JSON object containing `target_table` and `dependencies`.

### OUTPUT FORMAT
Return ONLY valid JSON. No markdown formatting.

### FEW-SHOT EXAMPLES

**Input:**
{
  "target_table": {
    "name": "comments",
    "columns": [
      { "name": "id", "type": "identifier", "is_nullable": false },
      { "name": "comment", "type": "string", "config": { "max_length": 255 } },
      { "name": "rating", "type": "numeric", "config": { "min_value": 1, "max_value": 5 } },
      { "name": "product_id", "type": "identifier", "is_nullable": false, "foreign_key": "products.id" }
    ]
  },
  "dependencies": [ {
    "name": "products",
    "columns": [
      { "name": "id", "type": "identifier", "is_nullable": false },
      { "name": "name", "type": "string", "config": { "max_length": 255 } } },
      { "name": "description", "type": "string", "config": { "max_length": 255 } } }
    ]
  }]
}

**Output:**
{
  "id": "Generate a unique sequential integer",
  "rating": "Generate a random rating between 1 and 5",
  "comment": "Generate a comment for the product {{ products.name }} with a rating of {{ rating }}",
  "product_id": "Select a random value from {{ products }} table"
}

### CURRENT TASK
"""
    PROMPT = f"""

**Product Description:**
{product_description}

**Entity:**
{table_name}

**Target Table:**
{table_schema}

**Dependencies:**
{dependent_tables}
"""

    return SYSTEM_PROMPT, PROMPT


def get_configuration_for_column(generating_prompt: str, model_schema_json: str):
    SYSTEM_PROMPT = """You are an expert data engineer. Your task is to generate a configuration object based on the generating prompt and json schema

### INPUT
You will receive the following information as input;
1. `Generating Prompt`: the guide to configure the configuration
2. `Model JSON Schema`: the schema for the configuration object

### Ouput
1. When generating the prompt stick **ONLY** to the properties that are described in the schema and **DO NOT** generate others
2. **DO NOT** return back the schema with values and return only the configuration object containing the properties and values
3. Output **ONLY** the configuration object JSON in the nested in the ```json ```

### Example

**Input:**
{
    "description": "Model for numeric type.",
    "properties": {
        "precision": {
            "description": "The precision of the numeric type",
            "title": "Precision",
            "type": "integer"
        },
        "max_value": {
            "default": 10,
            "description": "The max value of the numeric type",
            "title": "Max Value",
            "type": "number"
        },
        "min_value": {
            "default": 1,
            "description": "The min value of the numeric type",
            "title": "Min Value",
            "type": "number"
        }
    },
    "required": [
        "precision"
    ],
    "title": "NumericType",
    "type": "object"
}

**Output:**
```json
{
    "precision": 2,
    "min_value": 10,
    "max_value": 1000
}
```
"""

    PROMPT = f"""
**Model JSON Schema:**
{model_schema_json}

**Generating prompt:**
{generating_prompt}

"""
    return SYSTEM_PROMPT, PROMPT


def get_static_data_generation_prompt(
    product_description: str, table_name: str, table_schema: str
):
    SYSTEM_PROMPT = (
        """
You are an expert Synthetic Data Generator. Your task is to generate a rich, realistic dataset based on a provided database table schema and the prodivded product description.

### INPUT
You will receive a JSON object representing a table schema, containing:
1.  `name`: The table name (use this to infer the *context* of the data).
2.  `columns`: A list of definitions including name, type (`id_type`, `string_type`, `decimal_type`, etc.), and constraints.

### OUTPUT
Return **ONLY** a valid JSON Array containing items for the """
        + table_name
        + """ table values.
* Each object represents a row.
* Keys must match the schema column names exactly.
* Values must be realistic, high-quality business data appropriate for the table name.
* **Do not** wrap the output in markdown code blocks (like ```json). Just return the raw JSON array.

### GENERATION RULES
1.  **Context Is King:** Look at the `name` of the table.
    * If it is `shop_tiers`, generate tiers like "Starter", "Growth", "Enterprise".
    * If it is `order_status_types`, generate "Pending", "Shipped", "Cancelled".
    * If it is `users`, generate diverse names and emails.
2.  **Data Types:**
    * `id_type`: Generate sequential integers (1, 2, 3...) unless it is a Foreign Key.
    * `decimal_type`: Generate numbers with correct precision (e.g., currency). Respect `precision`, `min_value`, `max_value`.
    * `string_type`: Respect `max_length`.
    * `numeric_type`: Respect `precision`, `min_value`, `max_value`.
3.  **Quantity:**
    * For **Reference/Static** tables (e.g., tiers, statuses, categories), generate a **comprehensive** list of logical options (usually 3-10).
    * For **Transactional/Entity** tables (e.g., users, products), generate exactly **15 diverse rows**.
4.  **Output Format:**
    * Output **ONLY** a valid JSON Array containing items for the """
        + table_name
        + """ table values.
    * Each object represents a row.
    * Keys must match the schema column names exactly.
    * Values must be realistic, high-quality business data appropriate for the table name.
    * **Do not** wrap the output in markdown code blocks (like ```json). Just return the raw JSON array.

### EXAMPLE
**Input:**
{
  "name": "shipping_methods",
  "columns": [
    {"name": "id", "type": "identifier"},
    {"name": "method_name", "type": "string", "config": {"max_length": 50}},
    {"name": "cost", "type": "numeric", "config": {"precision": 2, "min": 0, "max": 100}}}
  ]
}

**Output:**
```json
[
  {"id": 1, "method_name": "Standard Ground", "cost": 0.00},
  {"id": 2, "method_name": "Expedited (3-Day)", "cost": 12.50},
  {"id": 3, "method_name": "Overnight Express", "cost": 29.99},
  {"id": 4, "method_name": "International Priority", "cost": 55.00},
  {"id": 5, "method_name": "In-Store Pickup", "cost": 0.00}
]
```
"""
    )

    PROMPT = f"""
**Product Description:**
{product_description}

**Table Name:**
{table_name}

**Input:**
{table_schema}
"""

    return SYSTEM_PROMPT, PROMPT

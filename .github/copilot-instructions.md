- Assume that any request to create dataset configuration files or generate synthetic data is intended for use with the Data Designer tool and should create YAML configuration files or datasets compatible with Data Designer.

- When you asked to create dataset ALWAYS firstly create YAML configuration file that define the dataset structure, including declarative columns, column types (sampler, llm-text, llm-code, llm-structured, llm-judge, expression, validation), and any necessary MCP tool configurations.

- Always create or update YAML, CSV, JSON files ONLY in the `../artifacts/` directory.

- For examples and documentation, ONLY refer to files in the `./references/` directory.
- Ignore all other directories - never read files from there.

## Usage Guidelines

When asked to create a configuration file or YAML file for a use case, treat it as a Data Designer declarative columns configuration.

**CRITICAL: ALWAYS load and read these documentation files BEFORE generating any YAML configuration:**

### Required Documentation (Load in this order)

1. **[sampler_params.py](./references/config/sampler_params.py)** - **MUST READ** for all sampler parameter names and types
   - Contains exact parameter names for each sampler type (e.g., `mean` not `lam` for Poisson)
   - Defines valid parameter combinations and constraints
   - **Key Classes**: `CategorySamplerParams`, `DatetimeSamplerParams`, `SubcategorySamplerParams`, `GaussianSamplerParams`, `UniformSamplerParams`, `ScipySamplerParams`, `PoissonSamplerParams`, `BernoulliSamplerParams`, `PersonSamplerParams`, `PersonFromFakerSamplerParams`
   
2. **[validator_params.py](./references/config/validator_params.py)** - **MUST READ** when using validation columns
   - Defines `validator_type` options: `code`, `local_callable`, `remote`
   - Contains correct `validator_config` structure for each type
   - **Key Classes**: `CodeValidatorParams`, `LocalCallableValidatorParams`, `RemoteValidatorParams`

3. **[column_configs.py](./references/config/column_configs.py)** - **MUST READ** for all column configuration classes
   - Defines all column types and their parameters
   - **Key Classes**: `SamplerColumnConfig`, `LLMTextColumnConfig`, `LLMCodeColumnConfig`, `LLMStructuredColumnConfig`, `LLMJudgeColumnConfig`, `ExpressionColumnConfig`, `ValidationColumnConfig`, `Score`

4. **[column_types.py](./references/config/column_types.py)** - Column type resolution and registration
   - Defines `DataDesignerColumnType` enum with all supported column types
   - Contains `get_column_config_from_kwargs()` for creating column configs

5. **[person_sampling.md](./references/concepts/person_sampling.md)** - When using person samplers
   - Note: `person_from_faker` does NOT have an `email` field - generate emails from first/last name

6. **[examples/](./references/examples/)** - Reference ONLY after reading documentation above

### Quick Parameter Reference

#### Sampler Parameters (from [sampler_params.py](./references/config/sampler_params.py))
| Sampler Type | Required Params | Optional Params |
|--------------|-----------------|-----------------|
| `category` | `values: list[str\|int\|float]` | `weights: list[float]` |
| `subcategory` | `category: str`, `values: dict[str, list]` | - |
| `datetime` | `start: str`, `end: str` | `unit: "Y"\|"M"\|"D"\|"h"\|"m"\|"s"` (default: "D") |
| `uniform` | `low: float`, `high: float` | `decimal_places: int` |
| `gaussian` | `mean: float`, `stddev: float` | `decimal_places: int` |
| `poisson` | `mean: float` | - |
| `bernoulli` | `p: float` (0.0-1.0) | - |
| `binomial` | `n: int`, `p: float` | - |
| `scipy` | `dist_name: str`, `dist_params: dict` | `decimal_places: int` |
| `uuid` | - | `prefix: str`, `short_form: bool`, `uppercase: bool` |
| `person` | - | `locale: str`, `sex: str`, `city: str\|list`, `age_range: [min, max]`, `with_synthetic_personas: bool` |
| `person_from_faker` | - | `locale: str`, `sex: str`, `city: str\|list`, `age_range: [min, max]` |
| `timedelta` | `dt_min: int`, `dt_max: int`, `reference_column_name: str` | `unit: "D"\|"h"\|"m"\|"s"` |

#### Column Config Parameters (from [column_configs.py](./references/config/column_configs.py))

| Column Type | Required Fields | Optional Fields |
|-------------|-----------------|-----------------|
| `sampler` | `sampler_type`, `params` | `convert_to: str`, `conditional_params: dict`, `drop: bool` |
| `llm-text` | `prompt`, `model_alias` | `system_prompt`, `tool_alias`, `with_trace: bool`, `drop: bool` |
| `llm-code` | `prompt`, `model_alias`, `code_lang` | `system_prompt`, `tool_alias`, `with_trace: bool`, `drop: bool` |
| `llm-structured` | `prompt`, `model_alias`, `output_format` | `system_prompt`, `tool_alias`, `with_trace: bool`, `drop: bool` |
| `llm-judge` | `prompt`, `model_alias`, `scores: list[Score]` | `system_prompt`, `with_trace: bool`, `drop: bool` |
| `expression` | `expr` | `dtype: "int"\|"float"\|"str"\|"bool"` (default: "str"), `drop: bool` |
| `validation` | `target_columns`, `validator_type`, `validator_params` | `batch_size: int` (default: 10), `drop: bool` |

#### Validator Parameters (from [validator_params.py](./references/config/validator_params.py))

| Validator Type | Required Params |
|----------------|-----------------|
| `code` | `code_lang: str` (e.g., "python", "sql:postgres", "sql:mysql", "sql:sqlite") |
| `local_callable` | `validation_function: Callable`, optional `output_schema: dict` |
| `remote` | `endpoint_url: str`, optional: `output_schema`, `timeout`, `max_retries`, `retry_backoff`, `max_parallel_requests` |

### Common Errors to Avoid

| Wrong | Correct | Sampler/Column |
|-------|---------|----------------|
| `lam: 3` | `mean: 3` | poisson sampler |
| `format: "%Y-%m-%d"` | `unit: D` | datetime sampler |
| `parents:` / `parent_column:` | `category:` / `values:` | subcategory sampler |
| `dtype: int` inside `params:` | `convert_to: int` outside `params:` | uniform sampler (integer output) |
| `std: 5` | `stddev: 5` | gaussian sampler |
| `min:` / `max:` in gaussian | Remove - not supported | gaussian sampler (no min/max) |
| `distribution: lognorm` | `dist_name: lognorm` | scipy sampler |
| `s:`, `loc:`, `scale:` directly in params | Nest inside `dist_params:` | scipy sampler |
| `min_score` / `max_score` | `options: {1: "...", 2: "..."}` | llm-judge scores |
| `output_schema:` | `output_format:` | llm-structured |
| `customer.email` | `customer['first_name']` + generate | person_from_faker (no email field) |
| `len(text.split())` | `{{ text.split() \| length }}` | expression (use Jinja2) |
| `score['overall']` | `score['overall']['score']` | accessing llm-judge results |
| `{% set var = ... %}` | Reference existing column directly | expression (no variable assignment) |
| `drop: true` without full definition | Include `column_type`, `sampler_type`, etc. with `drop: true` | dropping columns |

## Critical Syntax Rules

### Sampler Column Syntax

**datetime sampler** - Use `unit` parameter (NOT `format`):
```yaml
- name: created_at
  column_type: sampler
  sampler_type: datetime
  params:
    start: "2024-01-01"
    end: "2024-12-31"
    unit: D  # D=days, s=seconds, etc. Do NOT use 'format'
```

**subcategory sampler** - Use `category` and `values` (NOT `parents`/`parent_column`):
```yaml
- name: product_subcategory
  column_type: sampler
  sampler_type: subcategory
  params:
    category: product_category  # References parent column
    values:
      Electronics:
        - Smartphones
        - Laptops
      Clothing:
        - T-Shirts
        - Jeans
```

**person_from_faker sampler** - For quick PII generation:
```yaml
- name: customer
  column_type: sampler
  sampler_type: person_from_faker
  params:
    locale: en_US
    age_range: [18, 65]
```

**uniform sampler** - Use `convert_to` for integer output (NOT `dtype` inside params):
```yaml
# CORRECT - convert_to is OUTSIDE params
- name: years_experience
  column_type: sampler
  sampler_type: uniform
  params:
    low: 0
    high: 15
  convert_to: int  # Must be outside params block

# WRONG - dtype inside params is NOT valid
- name: years_experience
  column_type: sampler
  sampler_type: uniform
  params:
    low: 0
    high: 15
    dtype: int  # ERROR: Extra inputs are not permitted
```

**gaussian sampler** - Use `stddev` (NOT `std`), no `min`/`max` support:
```yaml
# CORRECT - use stddev parameter
- name: session_duration
  column_type: sampler
  sampler_type: gaussian
  params:
    mean: 8
    stddev: 5  # NOT 'std'

# WRONG - std and min/max are not valid
- name: session_duration
  column_type: sampler
  sampler_type: gaussian
  params:
    mean: 8
    std: 5    # ERROR: use 'stddev' instead
    min: 0.5  # ERROR: not supported
    max: 60   # ERROR: not supported
```

**scipy sampler** - Use `dist_name` and `dist_params` (NOT `distribution` with flat params):
```yaml
# CORRECT - dist_name and dist_params structure
- name: transaction_amount
  column_type: sampler
  sampler_type: scipy
  params:
    dist_name: lognorm  # NOT 'distribution'
    dist_params:        # Distribution params nested here
      s: 1.5
      loc: 0
      scale: 150

# WRONG - flat structure with 'distribution'
- name: transaction_amount
  column_type: sampler
  sampler_type: scipy
  params:
    distribution: lognorm  # ERROR: use 'dist_name'
    s: 1.5                  # ERROR: must be inside 'dist_params'
    loc: 0                  # ERROR: must be inside 'dist_params'
    scale: 150              # ERROR: must be inside 'dist_params'
```

**Dropping intermediate columns** - Must include full column definition:
```yaml
# CORRECT - include column_type and sampler_type with drop
- name: customer
  column_type: sampler
  sampler_type: person_from_faker
  drop: true

# WRONG - missing required fields
- name: customer
  drop: true  # ERROR: Missing 'column_type' field
```

### LLM-Judge Column Syntax

**scores** - Use `options` dict with score values as keys (NOT `min_score`/`max_score`):
```yaml
- name: quality_score
  column_type: llm-judge
  model_alias: nvidia-text
  prompt: |
    Evaluate this content: "{{ content }}"
  scores:
    - name: relevance
      description: How relevant is the content
      options:
        1: Not relevant at all
        2: Somewhat relevant
        3: Very relevant
```

**Accessing judge scores in expressions** - Scores are nested objects with `score` key:
```yaml
# CORRECT - access the 'score' property
expr: "{{ response_quality_score['overall_score']['score'] }}"

# WRONG - this returns the full object, not the numeric score
expr: "{{ response_quality_score['overall_score'] }}"
```

### Expression Column Syntax

**ALWAYS use Jinja2 templating** with `{{ }}` for variable access:
```yaml
# CORRECT - Jinja2 templating
- name: full_name
  column_type: expression
  expr: "{{ customer['first_name'] }} {{ customer['last_name'] }}"
  dtype: str

- name: word_count
  column_type: expression
  expr: "{{ text.split() | length }}"
  dtype: int

- name: is_premium
  column_type: expression
  expr: "{% if tier == 'Premium' %}true{% else %}false{% endif %}"
  dtype: str

# WRONG - raw Python syntax won't work
- name: full_name
  expr: "customer['first_name'] + ' ' + customer['last_name']"

- name: word_count
  expr: "len(text.split())"

# WRONG - {% set %} is NOT permitted (non-permitted Jinja operation)
- name: quality_tier
  expr: "{% set avg = score1 + score2 %}{% if avg > 3 %}High{% else %}Low{% endif %}"

# CORRECT - reference a pre-calculated column instead
- name: average_score
  column_type: expression
  expr: "{{ (score1 + score2) / 2 }}"
  dtype: float

- name: quality_tier
  column_type: expression
  expr: "{% if average_score > 3 %}High{% else %}Low{% endif %}"
  dtype: str
```

**Prohibited Jinja operations in expressions:**
- `{% set ... %}` - Variable assignment is NOT allowed
- Create a separate expression column for intermediate calculations instead

### LLM-Structured Column Syntax

Use `output_format` (NOT `output_schema`):
```yaml
- name: analysis
  column_type: llm-structured
  model_alias: nvidia-text
  prompt: "Analyze: {{ text }}"
  output_format:
    type: object
    properties:
      sentiment:
        type: string
        enum: [positive, neutral, negative]
      confidence:
        type: number
    required: [sentiment, confidence]
```

# Data Designer Declarative Columns Plugin

A Data Designer utility that allows loading multiple column configurations from YAML.

## Features

- **Multi-column YAML**: Load entire column configurations from a YAML file or inline string
- **All column types supported**: sampler, llm-text, llm-code, llm-structured, llm-judge, expression, validation
- **MCP Tool Configs**: Define `tool_configs` in YAML for MCP tool use workflows
- **Reusable configurations**: Share column definitions across projects via YAML files
- **Full parity with Python API**: YAML configs are equivalent to programmatic `add_column()` calls

### YAML Configuration Format

**product_reviews.yaml** (excerpt):
```yaml
columns:
  - name: product_category
    column_type: sampler
    sampler_type: category
    params:
      values: [Electronics, Clothing, Books, Home & Garden]
      weights: [3, 2, 2, 1]

  - name: customer
    column_type: sampler
    sampler_type: person_from_faker
    params:
      locale: en_US
      age_range: [18, 65]

  - name: review
    column_type: llm-text
    model_alias: nvidia-text
    prompt: |
      Write a realistic customer review for a {{ product_subcategory }} 
      in the {{ product_category }} category.

  - name: review_analysis
    column_type: llm-structured
    model_alias: nvidia-text
    prompt: |
      Analyze this product review and extract structured information:
      Review: "{{ review }}"
    output_format:
      type: object
      properties:
        sentiment:
          type: string
          enum: [positive, neutral, negative]
        would_recommend:
          type: boolean
      required: [sentiment, would_recommend]
```


## Supported Column Types

| Column Type | Description | Example Fields |
|-------------|-------------|----------------|
| `sampler` | Built-in samplers (UUID, Category, Uniform, Person, etc.) | `sampler_type`, `params` |
| `llm-text` | LLM text generation with Jinja2 templating | `model_alias`, `prompt`, `system_prompt` |
| `llm-code` | Code generation with language specification | `model_alias`, `code_lang`, `prompt` |
| `llm-structured` | Structured JSON generation with schema | `model_alias`, `prompt`, `output_format` |
| `llm-judge` | Quality assessment with scoring rubrics | `model_alias`, `prompt`, `scores` (with `options` dict) |
| `expression` | Expression-based derived columns (Jinja2 required) | `expr`, `dtype` |
| `validation` | Validation results (Python, SQL, Code validators) | `validator_type`, `target_columns`, `validator_params` |

## Examples

See the [`examples/`](./references/examples/) folder for complete YAML configurations:

- **[product_reviews.yaml](./references/examples/product_reviews.yaml)** - Comprehensive example with all column types:
  - Samplers: UUID, Category, Subcategory, Uniform, Gaussian, DateTime, Person (Faker)
  - LLM Text: Product review generation
  - LLM Code: SQL query generation
  - LLM Structured: Review sentiment analysis
  - LLM Judge: Review quality scoring
  - Expressions: Derived values (word count, price tier, customer name)

- **[text_to_python.yaml](./references/examples/text_to_python.yaml)** - Python code generation with validation
- **[text_to_sql.yaml](./references/examples/text_to_sql.yaml)** - SQL query generation
- **[multi_turn_chat.yaml](./references/examples/multi_turn_chat.yaml)** - Multi-turn conversations
- **[product_info_qa.yaml](./references/examples/product_info_qa.yaml)** - Product Q&A
- **[basic_mcp.yaml](./references/examples/basic_mcp.yaml)** - MCP tool use
- **[pdf_qa.yaml](./references/examples/pdf_qa.yaml)** - Document Q&A with MCP

### With MCP Tool Configs

For MCP tool use workflows, define `tool_configs` in the YAML and use `get_tool_configs()`:

```python
from data_designer_declarative_columns import DeclarativeColumnsConfig

import data_designer.config as dd
from data_designer.interface import DataDesigner

# Load configuration with tool_configs
config = DeclarativeColumnsConfig(file="examples/basic_mcp.yaml")

# Create builder WITH tool configs from YAML
config_builder = dd.DataDesignerConfigBuilder(tool_configs=config.get_tool_configs())
config.add_columns_to_builder(config_builder)

# Define MCP provider (server code must still be Python)
mcp_provider = dd.LocalStdioMCPProvider(
    name="basic-tools",
    command=sys.executable,
    args=["your_mcp_server.py", "serve"],
)

# Create DataDesigner with MCP provider
data_designer = DataDesigner(mcp_providers=[mcp_provider])
preview_results = data_designer.preview(config_builder, num_records=2)
```

**YAML with tool_configs**:
```yaml
tool_configs:
  - tool_alias: basic-tools
    providers: [basic-tools]
    allow_tools: [get_fact, add_numbers]
    max_tool_call_turns: 5
    timeout_sec: 30.0

columns:
  - name: topic
    column_type: sampler
    sampler_type: category
    params:
      values: [python, earth, water]

  - name: fact_response
    column_type: llm-text
    model_alias: nvidia-text
    prompt: "Use the get_fact tool to look up '{{ topic }}'"
    tool_alias: basic-tools
    with_trace: true
```
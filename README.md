# Data Designer Copilot 🌤️

An interactive AI-powered assistant for generating synthetic datasets using NVIDIA NeMo Data Designer. Create high-quality synthetic data for AI/ML training using natural language commands.

## Overview

Data Designer Copilot combines the power of:
- **NVIDIA NeMo Data Designer** - A library for creating synthetic datasets with LLM-powered generation
- **Copilot SDK** - An interactive conversational interface for natural language commands
- **Declarative YAML Configurations** - Define dataset schemas without writing code

## Features

- 🗣️ **Natural Language Interface** - Describe datasets in plain English
- 📝 **YAML-Based Configuration** - Define data schemas declaratively
- 🎲 **Multiple Column Types** - Samplers, LLM-generated text, structured output, expressions
- ⚖️ **Quality Scoring** - Built-in LLM-judge for evaluating generated content
- 💾 **CSV Export** - Automatically saves generated datasets

## Installation

### Prerequisites

- Python 3.10+
- [Copilot CLI](https://docs.github.com/en/copilot) installed and configured
- NVIDIA API key (for NeMo Data Designer)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd data-designer-copilot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your credentials:
   ```env
   NVIDIA_API_KEY=your_nvidia_api_key_here
   COPILOT_MODEL=claude-opus-4.5  # optional, defaults to claude-opus-4.5
   ```

## Usage

### Interactive Mode (Copilot)

Run the interactive assistant:

```bash
python dd-copilot.py
```

You'll see an interactive prompt where you can:

1. **Generate dataset for `<usecase>`** - Creates YAML configuration AND generates data
   ```
   [You]: Generate dataset for customer support tickets with priorities and responses
   ```

2. **Generate configuration file for `<usecase>`** - Creates only the YAML file
   ```
   [You]: Generate configuration file for product reviews with ratings and sentiment
   ```

3. **Generate dataset based on `<yaml file>`** - Uses existing YAML to generate records
   ```
   [You]: Generate 10 records based on artifacts/product_reviews.yaml
   ```

Type `exit` to quit.

### Standalone Scripts

#### Using Data Designer Library (Local)

```bash
python standalone/generate.py artifacts/product_reviews.yaml -n 5
```

#### Using NeMo Microservices API

```bash
python standalone/generate_nemo.py artifacts/product_reviews.yaml -n 5 --output output.csv
```

Options:
- `-n, --num-records` - Number of records to generate (default: 3)
- `-o, --output` - Output CSV file path
- `--model` - Model ID to use (default: `nvidia/llama-3.3-nemotron-super-49b-v1.5`)

## YAML Configuration Format

Define datasets using declarative YAML files. Example:

```yaml
columns:
  # UUID sampler
  - name: review_id
    column_type: sampler
    sampler_type: uuid
    params:
      prefix: "REV"
      short_form: true

  # Category sampler with weights
  - name: product_category
    column_type: sampler
    sampler_type: category
    params:
      values: [Electronics, Clothing, Home & Kitchen]
      weights: [3, 2, 1]

  # LLM-generated text
  - name: product_name
    column_type: llm-text
    model_alias: nvidia-text
    prompt: |
      Generate a realistic product name for the {{ product_category }} category.

  # Structured LLM output
  - name: sentiment_analysis
    column_type: llm-structured
    model_alias: nvidia-text
    prompt: |
      Analyze the sentiment of: "{{ review_text }}"
    output_format:
      type: object
      properties:
        sentiment:
          type: string
          enum: [positive, neutral, negative]
        confidence:
          type: number

  # LLM quality judge
  - name: review_quality
    column_type: llm-judge
    model_alias: nvidia-text
    prompt: |
      Evaluate this review: "{{ review_text }}"
    scores:
      - name: helpfulness
        description: How helpful is this review
        options:
          1: Not helpful
          2: Somewhat helpful
          3: Very helpful

  # Expression (derived column)
  - name: word_count
    column_type: expression
    expr: "{{ review_text.split() | length }}"
    dtype: int
```

### Supported Column Types

| Type | Description |
|------|-------------|
| `sampler` | Built-in samplers (uuid, category, datetime, uniform, gaussian, person_from_faker, etc.) |
| `llm-text` | Free-form text generation using LLMs |
| `llm-code` | Code generation in specific languages |
| `llm-structured` | JSON output with schema validation |
| `llm-judge` | Quality scoring with rubrics |
| `expression` | Jinja2-based derived values |
| `validation` | Validate generated data |

## Project Structure

```
data-designer-copilot/
├── dd-copilot.py           # Main interactive Copilot application
├── requirements.txt        # Python dependencies
├── artifacts/              # Generated YAML configs and CSV datasets
│   ├── product_reviews.yaml
│   └── *.csv
└── standalone/
    ├── generate.py         # Standalone script using Data Designer library
    └── generate_nemo.py    # Standalone script using NeMo Microservices API
```

## Dataset Ideas

- 📞 Customer support tickets
- 💳 Financial transactions
- ⭐ Product reviews
- 🏥 Medical diagnoses
- 🔌 API request/response logs
- 📄 Resumes and job applications
- 💻 Code reviews
- 📡 IoT sensor data
- 📜 Legal contracts
- ❓ Quiz questions and answers

## Requirements

- `python-dotenv` - Environment variable management
- `data-designer` - NVIDIA NeMo Data Designer library
- `data-designer-declarative-columns` - YAML configuration plugin
- `copilot-sdk` - GitHub Copilot SDK for interactive mode

## License

This project is licensed under the **Apache License 2.0** (Apache-2.0).

This license was chosen for compatibility with NVIDIA NeMo Data Designer, which is also distributed under Apache-2.0. See [SPDX License](https://spdx.org/licenses/Apache-2.0.html) for details.

import argparse
import os
import re

from dotenv import load_dotenv

from data_designer_declarative_columns.config import DeclarativeColumnsConfig

import data_designer.config as dd
from data_designer.interface import DataDesigner

# Load environment variables from .env file
load_dotenv()


def strip_think_tags(text):
    """Remove <think>...</think> blocks from model output."""
    if not isinstance(text, str):
        return text
    # Remove <think>...</think> blocks (including newlines)
    cleaned = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL)
    return cleaned.strip()


def clean_dataset(df, text_columns=None):
    """Clean reasoning traces from dataset columns."""
    if text_columns is None:
        # Auto-detect string columns
        text_columns = df.select_dtypes(include=['object']).columns.tolist()
    
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(strip_think_tags)
    
    return df


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic data from a declarative YAML configuration"
    )
    parser.add_argument(
        "config_file",
        help="Path to the YAML configuration file"
    )
    parser.add_argument(
        "-n", "--num-records",
        type=int,
        default=3,
        help="Number of records to generate (default: 3)"
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default=None,
        help="Model to use (e.g., nvidia/llama-3.3-nemotron-super-49b-v1.5)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output CSV file path (optional)"
    )
    args = parser.parse_args()

    # Create a DataDesigner instance
    # This automatically configures the default model providers
    data_designer = DataDesigner()

    # Create model configs if a custom model is specified
    model_configs = None
    if args.model:
        print(f"\nUsing custom model: {args.model}")
        model_configs = [
            dd.ModelConfig(
                alias="nvidia-text",
                model=args.model,
                inference_parameters=dd.ChatCompletionInferenceParams(
                    temperature=0.7,
                    max_tokens=1024
                )
            )
        ]

    # Create a config builder with optional model configs
    config_builder = dd.DataDesignerConfigBuilder(model_configs=model_configs)

    # Load columns from YAML file
    declarative_config = DeclarativeColumnsConfig(file=args.config_file)

    print(f"\nLoaded {len(declarative_config)} columns from {declarative_config.file}:")
    for col in declarative_config.columns:
        print(f"  - {col['name']} ({col['column_type']})")

    # Add all columns from the YAML file to the builder
    print("\nAdding columns to builder...")
    declarative_config.add_columns_to_builder(config_builder)

    # Validate the configuration
    print("\nValidating configuration...")
    data_designer.validate(config_builder)
    print("Configuration is valid!")

    # Show column summary
    print("\nColumn configuration summary:")
    for name, col_config in config_builder._column_configs.items():
        print(f"  {col_config.get_column_emoji()} {name}: {col_config.column_type}")

    # Run a preview to generate sample records
    print(f"\nGenerating {args.num_records} records...")
    preview_results = data_designer.preview(config_builder=config_builder, num_records=args.num_records)

    # Clean reasoning traces from the dataset
    df = preview_results.dataset.copy()
    df = clean_dataset(df)
    
    # Display a cleaned sample record
    print("\n" + "=" * 80)
    print("Sample Record (cleaned)")
    print("=" * 80)
    for col in df.columns:
        print(f"\n{col}:")
        print(df[col].iloc[0])

    # Save to CSV if output path specified
    if args.output:
        df.to_csv(args.output, index=False)
        print(f"\n✅ Dataset saved to {args.output}")


if __name__ == "__main__":
    main()

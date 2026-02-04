import argparse
import os

from dotenv import load_dotenv

from data_designer_declarative_columns.config import DeclarativeColumnsConfig

import data_designer.config as dd
from data_designer.interface import DataDesigner

# Load environment variables from .env file
load_dotenv()


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
    args = parser.parse_args()

    # Create a DataDesigner instance
    # This automatically configures the default model providers
    data_designer = DataDesigner()

    # Create a config builder
    # This automatically loads the default model configurations
    config_builder = dd.DataDesignerConfigBuilder()

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

    # Display a sample record
    preview_results.display_sample_record()


if __name__ == "__main__":
    main()

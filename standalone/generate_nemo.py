import argparse
import os

from dotenv import load_dotenv

from data_designer_declarative_columns.config import DeclarativeColumnsConfig

# you need to pip install nemo-microservices

from nemo_microservices.data_designer.essentials import (
    DataDesignerConfigBuilder,
    InferenceParameters,
    ModelConfig,
    NeMoDataDesignerClient,
)

# Load environment variables from .env file
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic data from a declarative YAML configuration using NeMo Microservices"
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
        "-o", "--output",
        help="Output CSV file path (optional)"
    )
    parser.add_argument(
        "--model",
        default="nvidia/llama-3.3-nemotron-super-49b-v1.5",
        help="Model ID to use (default: nvidia/llama-3.3-nemotron-super-49b-v1.5)"
    )
    args = parser.parse_args()

    # Get API key from environment
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY not found in environment. Please set it in .env file.")

    # Create NeMo Data Designer client
    data_designer_client = NeMoDataDesignerClient(
        base_url="https://ai.api.nvidia.com/v1/nemo/dd",
        default_headers={"Authorization": f"Bearer {api_key}"}
    )

    # Configure model
    model_alias = "default-model"
    model_configs = [
        ModelConfig(
            alias=model_alias,
            model=args.model,
            inference_parameters=InferenceParameters(
                temperature=0.6,
                top_p=0.95,
                max_tokens=2048,
            )
        )
    ]

    # Create config builder with model configs
    config_builder = DataDesignerConfigBuilder(model_configs)

    # Load columns from YAML file using the declarative columns plugin
    declarative_config = DeclarativeColumnsConfig(file=args.config_file)

    print(f"\nLoaded {len(declarative_config)} columns from {declarative_config.file}:")
    for col in declarative_config.columns:
        print(f"  - {col['name']} ({col['column_type']})")

    # Add all columns from the YAML file to the builder
    print("\nAdding columns to builder...")
    declarative_config.add_columns_to_builder(config_builder)

    # Run preview to generate records
    print(f"\nGenerating {args.num_records} records using {args.model}...")
    preview = data_designer_client.preview(config_builder, num_records=args.num_records)

    # Display a sample record
    preview.display_sample_record()

    # Save to CSV if output path specified
    if args.output:
        preview.dataset.to_csv(args.output, index=False)
        print(f"\nDataset saved to {args.output}")


if __name__ == "__main__":
    main()

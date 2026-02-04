import asyncio
import random
import sys
import json
import shutil
import os
from datetime import datetime
from copilot import CopilotClient
from copilot.tools import define_tool
from copilot.generated.session_events import SessionEventType
from pydantic import BaseModel, Field

from dotenv import load_dotenv
from data_designer_declarative_columns.config import DeclarativeColumnsConfig
import data_designer.config as dd
from data_designer.interface import DataDesigner

# Load environment variables from .env file
load_dotenv()

class GenerateSyntheticDataParams(BaseModel):
    yaml_file: str = Field(description="Path to the YAML configuration file for data generation")
    num_records: int = Field(default=3, description="Number of records to generate")

@define_tool(description="Generate synthetic data based on a declarative YAML configuration file. Returns the generated records as formatted text.")
async def generate_synthetic_data(params: GenerateSyntheticDataParams) -> str:
    """Generate synthetic data using DataDesigner from a YAML config file."""
    try:
        # Create a DataDesigner instance
        data_designer = DataDesigner()

        # Create a config builder
        config_builder = dd.DataDesignerConfigBuilder()

        # Load columns from YAML file
        declarative_config = DeclarativeColumnsConfig(file=params.yaml_file)

        columns_info = [f"  - {col['name']} ({col['column_type']})" for col in declarative_config.columns]

        # Add all columns from the YAML file to the builder
        declarative_config.add_columns_to_builder(config_builder)

        # Validate the configuration
        data_designer.validate(config_builder)

        # Generate records
        preview_results = data_designer.preview(
            config_builder=config_builder,
            num_records=params.num_records
        )

        # Convert results to a serializable format
        records = preview_results.dataset.to_dict(orient="records")

        # Generate CSV filename based on yaml file and timestamp
        yaml_basename = os.path.splitext(os.path.basename(params.yaml_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{yaml_basename}_{timestamp}.csv"
        csv_path = os.path.join("artifacts", csv_filename)
        
        # Ensure artifacts directory exists
        os.makedirs("artifacts", exist_ok=True)
        
        # Save to CSV
        preview_results.dataset.to_csv(csv_path, index=False)

        # Format output as readable text with table
        output_lines = [
            f"✅ Successfully generated {len(records)} records from '{params.yaml_file}'",
            f"💾 Saved to: {csv_path}",
            "",
            "📋 Columns:",
            *columns_info,
            "",
            "📊 Generated Records:",
            ""
        ]
        
        if records:
            # Format each record vertically
            for i, record in enumerate(records, 1):
                output_lines.append(f"═══════════════════════════════════════════════════")
                output_lines.append(f"  📄 Record {i}")
                output_lines.append(f"═══════════════════════════════════════════════════")
                for key, value in record.items():
                    str_val = str(value)
                    if len(str_val) > 100:
                        str_val = str_val[:97] + "..."
                    output_lines.append(f"  {key}:")
                    output_lines.append(f"    {str_val}")
                output_lines.append("")

        return "\n".join(output_lines)
    except Exception as e:
        return f"❌ Error generating data from '{params.yaml_file}': {str(e)}"

async def main():
    cli_path = shutil.which("copilot")  # Returns full path with extension
    client = CopilotClient({"cli_path": cli_path})
    await client.start()

    session = await client.create_session({
        "model": os.getenv("COPILOT_MODEL", "claude-opus-4.5"),
        "streaming": True,
        "tools": [generate_synthetic_data],
    })

    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()
        elif event.type == SessionEventType.TOOL_EXECUTION_COMPLETE:
            # Display tool results directly
            if event.data.result:
                print(f"\n{event.data.result.content}\n")
                sys.stdout.flush()

    session.on(handle_event)

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       🌤️  Data Designer Copilot                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Create synthetic datasets for AI/ML training using natural language!        ║
║  Powered by NVIDIA NeMo Data Designer library.                               ║
║  Type 'exit' to quit.                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

📝 Three ways to use:

   1️⃣  Generate dataset for <usecase>
       Creates YAML configuration AND generates synthetic data in one step.
       ➜ "Generate dataset for customer support tickets with priorities and responses"

   2️⃣  Generate configuration file for <usecase>
       Creates only the YAML file (no data generation).
       ➜ "Generate configuration file for product reviews with ratings and sentiment"

   3️⃣  Generate dataset based on <yaml file>
       Uses an existing YAML file to generate synthetic records.
       ➜ "Generate 10 records based on financial_transactions.yaml"

💡 Dataset ideas: support tickets, financial transactions, product reviews, 
   medical diagnoses, API requests, resumes, code reviews, sensor data, 
   legal contracts, quiz questions...
""")

    while True:
        try:
            user_input = input("[You]: ")
        except EOFError:
            break

        if user_input.lower() == "exit":
            break

        sys.stdout.write("[Data Designer Copilot]: ")
        await session.send_and_wait({"prompt": user_input})
        print("\n")

    await client.stop()

asyncio.run(main())
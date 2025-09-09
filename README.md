# funnel-data-assignment

## How to Run the Data Analytics Assignment Code
Prerequisites

Python 3.8 or higher installed

Required Python libraries (install with pip): pandas

Installation Steps
Clone or download this project folder.

Place the data CSV files (events.csv, messages.csv, orders.csv) in the project root or a known location.

Setup Python Environment
Open a terminal/command prompt and run:

bash
pip install pandas
How to Run the Analysis
Open terminal/command prompt.

Navigate to the project directory containing the src folder.

Run the analysis script with the following command (update paths if your CSV files are in a different folder):

bash
```
python src/evo_report.py --events events.csv --messages messages.csv --orders orders.csv --out ./out/
--events: Path to events.csv

--messages: Path to messages.csv

--orders: Path to orders.csv

--out: Directory where output files will be saved (will be created if not present)
```

Outputs Generated
report.json inside the out folder with analysis results and insights.

Console output showing progress and summary.

Notes
Ensure CSV files are correctly named and formatted.

The script creates output directory if it doesn’t exist.

You do not need to prepare report.json; it is generated automatically.

Troubleshooting
If Python cannot find files, check your command line paths.

For missing libraries, rerun the pip install command.

Use Python 3 (run with python3 if both Python 2 and 3 are installed).


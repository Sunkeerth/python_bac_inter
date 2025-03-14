# PubMed Fetcher

A tool to fetch PubMed papers with non-academic (pharma/biotech) affiliations.

## Features

- PubMed search with advanced query syntax
- CSV output with author/affiliation details
- Command-line interface

## Installation

1. Install Poetry: [https://python-poetry.org/docs/](https://python-poetry.org/docs/)
2. Clone repository:
   ```bash
   git clone https://github.com/yourusername/pubmed-fetcher.git
   cd pubmed-fetcher
   ```
3. Install dependencies:
   ```bash
   poetry install
   ```

## Usage

```bash
# Basic usage
poetry run get-papers-list "cancer treatment" -f output.csv

# With debug mode
poetry run get-papers-list "diabetes AND 2023" -d -f results.csv

# Print to console
poetry run get-papers-list "alzheimer's disease"
```

## Dependencies

- Biopython: PubMed API access
- Pandas: Data processing
- tqdm: Progress bars

## Documentation

Full PubMed query syntax: [https://pubmed.ncbi.nlm.nih.gov/advanced/](https://pubmed.ncbi.nlm.nih.gov/advanced/)

1. Help Option (-h or --help)
   When to use:

When you need to see program usage instructions

When you forget the available options

How to use:

bash
Copy
poetry run get-papers-list -h

# or

poetry run get-papers-list --help
Example Output:

Copy
usage: get-papers-list [-h] [-d] [-f FILE] query

Fetch PubMed papers with non-academic affiliation filtering

positional arguments:
query PubMed search query

options:
-h, --help show this help message and exit
-d, --debug Enable debug mode
-f FILE, --file FILE Output CSV filename 2. Debug Option (-d or --debug)
When to use:

When the program isn't working as expected

To see detailed processing information

To troubleshoot errors

How to use:

bash
Copy

# Basic debug

poetry run get-papers-list "cancer treatment" -d

# Debug with file output

poetry run get-papers-list "cancer treatment" -d -f results.csv
Example Debug Output:

Copy
[DEBUG] Searching PubMed for query: 'cancer treatment'
[DEBUG] Found 50 papers
[DEBUG] Processing 50 records
[DEBUG] Skipping record due to missing key: 'AuthorList'
[DEBUG] Saved 45 valid records
Saved 45 records to results.csv 3. File Option (-f or --file)
When to use:

To save results to a CSV file for later analysis

When you need machine-readable output

When dealing with large result sets

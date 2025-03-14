import argparse
import sys
from typing import List
from .fetcher import search_pubmed, fetch_paper_records, process_records, save_to_csv

def main(args: List[str] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Fetch PubMed papers with non-academic affiliations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("query", help="PubMed search query")
    parser.add_argument("-f", "--file", help="Output CSV filename")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args(args)
    
    # Execute search and processing
    pmids = search_pubmed(args.query, debug=args.debug)
    if not pmids:
        print("No papers found", file=sys.stderr)
        sys.exit(1)
    
    records = fetch_paper_records(pmids, args.debug)
    processed = process_records(records, args.debug)
    
    if not processed:
        print("No papers with company affiliations", file=sys.stderr)
        sys.exit(1)
    
    # Output results
    if args.file:
        save_to_csv(processed, args.file)
        print(f"Saved {len(processed)} records to {args.file}")
    else:
        for paper in processed:
            print(f"PMID: {paper['PubmedID']}")
            print(f"Title: {paper['Title']}")
            print("---")

if __name__ == "__main__":
    main()
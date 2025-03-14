import csv
import re
import sys
from typing import Any, Dict, List, Optional, Tuple
from Bio import Entrez

Entrez.email = "sunkeerth123@gmail.com"  # Replace with your email

ACADEMIC_KEYWORDS = ["university", "college", "institute", "academy", "hospital"]
COMPANY_KEYWORDS = ["pharma", "biotech", "inc", "ltd", "llc", "corporation"]
def extract_author_details(author: Dict, affiliation: str, debug: bool = False) -> Tuple[str, Optional[str], Optional[str]]:
    """Extract author details from affiliation information"""
    try:
        # Construct author name
        last_name = author.get("LastName", "")
        fore_name = author.get("ForeName", "")
        full_name = f"{fore_name} {last_name}".strip()
        
        # Extract company and email
        company = extract_company_name(affiliation)
        email = extract_email_from_affiliation(affiliation)
        
        return full_name, company, email
        
    except Exception as e:
        if debug:
            print(f"Error processing author: {str(e)}")
        return "Unknown Author", None, None

# Fixed regex patterns (added missing closing parenthesis)
COMPANY_PATTERNS = [
    r"\b([A-Z][a-zA-Z\s&]+?(?:Pharmaceuticals|Biotech|Inc|Ltd|LLC))\b",
    r"\b([A-Z][a-zA-Z\s&]+?)(?=,\s*\b(?:LLC|Inc|Ltd|Corp))\b"
]

def search_pubmed(query: str, retmax: int = 100, debug: bool = False) -> List[str]:
    """Search PubMed and return PMIDs"""
    try:
        handle = Entrez.esearch(db="pubmed", term=query, retmax=retmax)
        result = Entrez.read(handle)
        return result["IdList"]
    except Exception as e:
        if debug:
            print(f"Search error: {str(e)}", file=sys.stderr)
        return []

def fetch_paper_records(pmids: List[str], debug: bool = False) -> List[Dict]:
    """Fetch detailed records for given PMIDs"""
    if not pmids:
        return []
    
    try:
        handle = Entrez.efetch(db="pubmed", id=pmids, retmode="xml")
        records = Entrez.read(handle)
        return records["PubmedArticle"]
    except Exception as e:
        if debug:
            print(f"Fetch error: {str(e)}", file=sys.stderr)
        return []

def is_company_affiliation(affiliation: str) -> bool:
    """Check if affiliation is non-academic"""
    lower_aff = affiliation.lower()
    return (any(kw in lower_aff for kw in COMPANY_KEYWORDS) and \
           not any(akw in lower_aff for akw in ACADEMIC_KEYWORDS))

def extract_company_name(affiliation: str) -> Optional[str]:
    """Extract company name from affiliation string"""
    for pattern in COMPANY_PATTERNS:
        match = re.search(pattern, affiliation)
        if match:
            return match.group(1).strip()
    return None

def extract_email_from_affiliation(affiliation: str) -> Optional[str]:
    """Extract email address from affiliation"""
    match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", affiliation)
    return match.group(0) if match else None

def process_records(records: List[Dict], debug: bool = False) -> List[Dict]:
    """Process PubMed records to extract required information"""
    results = []
    for record in records:
        paper_info = extract_paper_info(record, debug)
        if paper_info:
            results.append(paper_info)
    return results

def extract_paper_info(article: Dict, debug: bool = False) -> Optional[Dict]:
    """Extract and format paper information"""
    try:
        medline = article["MedlineCitation"]
        pmid = str(medline["PMID"])
        article_data = medline["Article"]
        title = article_data["ArticleTitle"]
        
        # Handle publication date
        journal_issue = article_data.get("Journal", {}).get("JournalIssue", {})
        pub_date = journal_issue.get("PubDate", {})
        date_str = pub_date.get("Year", pub_date.get("MedlineDate", "Unknown"))
        
        # Handle authors with safe navigation
        authors = []
        companies = set()
        emails = set()
        
        # Check if AuthorList exists
        author_list = article_data.get("AuthorList", [])
        for author in author_list:
            # Handle collective authors (organizations)
            if isinstance(author, dict) and "CollectiveName" in author:
                continue  # Skip organizational authors
                
            aff_info = author.get("AffiliationInfo", [])
            for aff in aff_info:
                affiliation = aff.get("Affiliation", "")
                if is_company_affiliation(affiliation):
                    # Safely get author names
                    last_name = author.get("LastName", "")
                    fore_name = author.get("ForeName", "")
                    full_name = f"{fore_name} {last_name}".strip() or "Unknown Author"
                    authors.append(full_name)
                    
                    # Extract company and email
                    if company := extract_company_name(affiliation):
                        companies.add(company)
                    if email := extract_email_from_affiliation(affiliation):
                        emails.add(email)

        if not authors:
            return None

        return {
            "PubmedID": pmid,
            "Title": title,
            "Publication Date": date_str,
            "Non-academic Author(s)": "; ".join(authors),
            "Company Affiliation(s)": "; ".join(companies) if companies else "N/A",
            "Corresponding Author Email": "; ".join(emails) if emails else "N/A"
        }
    except KeyError as e:
        if debug:
            print(f"Skipping record due to missing key: {str(e)}")
        return None
def save_to_csv(data: List[Dict], filename: str) -> None:
    """
    Save results to a well-structured CSV file with proper formatting.
    
    Args:
        data: List of dictionaries containing paper details
        filename: Output CSV file path
    """
    # Define column headers and their corresponding keys
    fieldnames = [
        "PubmedID", 
        "Title", 
        "Publication Date", 
        "Non-academic Author(s)", 
        "Company Affiliation(s)", 
        "Corresponding Author Email"
    ]
    
    # Open CSV file for writing
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Write rows with proper formatting
        for paper in data:
            # Clean and format data
            formatted_paper = {
                "PubmedID": paper["PubmedID"],
                "Title": paper["Title"].strip(),  # Remove extra spaces
                "Publication Date": paper["Publication Date"].strip(),
                "Non-academic Author(s)": "; ".join(
                    author.strip() for author in paper["Non-academic Author(s)"].split("; ")
                ),
                "Company Affiliation(s)": "; ".join(
                    company.strip() for company in paper["Company Affiliation(s)"].split("; ")
                ) if paper["Company Affiliation(s)"] != "N/A" else "N/A",
                "Corresponding Author Email": paper["Corresponding Author Email"].strip()
            }
            writer.writerow(formatted_paper)
            
def save_to_csv(data: List[Dict], filename: str) -> None:
    """Save results to CSV file"""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "PubmedID", "Title", "Publication Date",
            "Non-academic Author(s)", "Company Affiliation(s)",
            "Corresponding Author Email"
        ])
        writer.writeheader()
        writer.writerows(data)
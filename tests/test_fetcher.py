from pubmed_fetcher.fetcher import search_pubmed

def test_search_pubmed():
    """Test PubMed search functionality"""
    pmids = search_pubmed("cancer", retmax=1)
    assert isinstance(pmids, list)
    assert len(pmids) <= 1
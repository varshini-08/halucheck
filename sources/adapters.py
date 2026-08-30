"""Small official-API adapters. They are opt-in and failure-isolated."""
import os
from .base import SourceAdapter

class WikidataAdapter(SourceAdapter):
    source_id="wikidata"; display_name="Wikidata"
    def search(self, claim):
        data=self._get("https://www.wikidata.org/w/api.php", params={"action":"wbsearchentities","search":claim,"language":"en","format":"json","limit":3})
        return [self.evidence(source=self.display_name,title=x.get("label"),content=x.get("description"),url=f"https://www.wikidata.org/entity/{x.get('id')}",source_type="structured",metadata={"id":x.get("id")}) for x in data.get("search",[]) if x.get("description")]

class WorldBankAdapter(SourceAdapter):
    source_id="world_bank"; display_name="World Bank"
    def search(self, claim):
        data=self._get("https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL",params={"format":"json","per_page":5})
        rows=data[1] if isinstance(data,list) and len(data)>1 else []
        return [self.evidence(source=self.display_name,title=f"{x.get('country',{}).get('value')} population",content=f"Year {x.get('date')}: {x.get('value')}",url=x.get("indicator",{}).get("id"),source_type="statistics",metadata=x) for x in rows if x.get("value") is not None]

class PubMedAdapter(SourceAdapter):
    source_id="pubmed"; display_name="PubMed"
    def search(self, claim):
        data=self._get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",params={"db":"pubmed","term":claim,"retmode":"json","retmax":3})
        ids=data.get("esearchresult",{}).get("idlist",[])
        return [self.evidence(source=self.display_name,title=f"PubMed article {i}",content=None,url=f"https://pubmed.ncbi.nlm.nih.gov/{i}/",source_type="academic",metadata={"pmid":i}) for i in ids]

class CrossrefAdapter(SourceAdapter):
    source_id="crossref"; display_name="Crossref"
    def search(self, claim):
        data=self._get("https://api.crossref.org/works",params={"query":claim,"rows":3})
        return [self.evidence(source=self.display_name,title=x.get("title",[None])[0],content=None,url=x.get("URL"),source_type="academic",metadata={"doi":x.get("DOI"),"published":x.get("published")}) for x in data.get("message",{}).get("items",[])]

class OpenAlexAdapter(SourceAdapter):
    source_id="openalex"; display_name="OpenAlex"
    def search(self, claim):
        data=self._get("https://api.openalex.org/works",params={"search":claim,"per-page":3})
        return [self.evidence(source=self.display_name,title=x.get("title"),content=None,url=x.get("doi") or x.get("id"),source_type="academic",metadata=x) for x in data.get("results",[])]

class GoogleFactCheckAdapter(SourceAdapter):
    source_id="google_factcheck"; display_name="Google Fact Check"
    def is_configured(self): return bool(os.getenv("GOOGLE_FACT_CHECK_API_KEY","").strip())
    def search(self, claim):
        if not self.is_configured(): return []
        data=self._get("https://factchecktools.googleapis.com/v1alpha1/claims:search",params={"query":claim,"key":os.environ["GOOGLE_FACT_CHECK_API_KEY"]})
        return [self.evidence(source=self.display_name,title=x.get("claimReview",[{}])[0].get("title"),content=x.get("text"),url=x.get("claimReview",[{}])[0].get("url"),source_type="fact_check") for x in data.get("claims",[])]

ADAPTERS={x.source_id:x for x in [WikidataAdapter(),WorldBankAdapter(),PubMedAdapter(),CrossrefAdapter(),OpenAlexAdapter(),GoogleFactCheckAdapter()]}

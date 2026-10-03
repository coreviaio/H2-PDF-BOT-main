from pydantic import BaseModel, Field
from typing import Optional, List,Literal




class isArticleWithSpecie(BaseModel):
    specie: Literal[True,False] = Field(..., description="Is this article with specie and details of specie present? If yes Return True otherwise return False")
#     affiliation: str = Field(None, description="affiliation of the author")



class authors_obj(BaseModel):
    name: str = Field(None, description="name of the author")
    affiliation: str = Field(None, description="affiliation of the author")

class ArticleCitationInformation(BaseModel):

    title: str = Field(..., description="Title of the given research paper.")
    authors: List[authors_obj] = Field(None, description="Authors of the research paper.")
    authorCountries:List[Optional[str]] = Field(None, description="Countries of the authors of the research paper.")
    doi: Optional[str] = Field(None, description="The doi mentioned in the article or else None.")
    country: Optional[str] = Field(None, description="Country of the paper.")
    researchCountry: Optional[str] = Field(None, description="Research Countries of the research paper (comma-separated).")
    grantCountry: Optional[str] = Field(None, description="Name of the grant country of the research paper.")
    year: Optional[str] = Field(None, description="Publication year of the research paper.")
    abstract: Optional[str] = Field(None, description="Abstract of the research paper. Fetched from the paper content exactly as written without making any changes but do not include keywords..")
    volume: Optional[str] = Field(None, description="Volume of the journal in which the paper is published.")
    journal: Optional[str] = Field(None, description="Name of the journal where the paper was published.")
    journalURL: Optional[str] = Field(None, description="URL of the journal where the paper is available.")
    publisher: Optional[str] = Field(None, description="Publisher of the journal.")
    pmid: Optional[str] = Field(None, description="Pubmed ID of the article.")
    impactFactor: Optional[str] = Field(None, description="Impact factor if mentioned.")
    HIndex: Optional[str] = Field(None, description="H-index if mentioned.")
    sciMAGO: Optional[str] = Field(None, description="sciMAGO information if mentioned.")
    pages: Optional[str] = Field(None, description="number of pages.")
    issue: Optional[str] = Field(None, description="The issue refers to a specific edition within a journal's volume, typically representing one of multiple publications released during the year")
    keywords: Optional[str] = Field(None, description="Keywords of the research paper. coma seperated values.")
    
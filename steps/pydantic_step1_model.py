from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class isArticleWithSpecie(BaseModel):
    specie: Literal[True, False] = Field(
        ...,
        description=(
            "Return True only when the article explicitly contains an experimental "
            "species/animal/human subject and corresponding species details. "
            "Return False when no such species information is explicitly present. "
            "Do not infer species from disease names, cell lines, tissue names, "
            "or other contextual information."
        ),
    )


class authors_obj(BaseModel):
    name: str = Field(
        ...,
        description="Extract the author's name exactly as explicitly written in the article. "
                    "Do not invent, normalize, or infer an author name.",
    )
    affiliation: Optional[str] = Field(
        None,
        description="Extract the author's affiliation only when explicitly provided. "
                    "If unavailable, return None. Do not infer it.",
    )


class ArticleCitationInformation(BaseModel):
    title: str = Field(
        ...,
        description="Extract the paper title exactly as stated. Do not generate or rewrite it.",
    )

    authors: List[authors_obj] = Field(
        default_factory=list,
        description="Extract all explicitly listed authors. If unavailable, return an empty list.",
    )

    authorCountries: List[Optional[str]] = Field(
        default_factory=list,
        description="Extract countries explicitly associated with authors/affiliations. "
                    "Do not infer countries. If unavailable, return an empty list.",
    )

    doi: Optional[str] = Field(
        None,
        description="Extract DOI exactly as explicitly mentioned. Do not generate or infer it.",
    )

    country: Optional[str] = Field(
        None,
        description="Extract publication/paper country only when explicitly stated. "
                    "Do not infer it from journal, publisher, or authors.",
    )

    researchCountry: Optional[str] = Field(
        None,
        description="Extract research countries only when explicitly stated. "
                    "Do not infer research location from affiliations or institutions.",
    )

    grantCountry: Optional[str] = Field(
        None,
        description="Extract grant/funding country only when explicitly stated. "
                    "Do not infer it from the funding organization.",
    )

    year: Optional[str] = Field(
        None,
        description="Extract publication year exactly as explicitly reported. "
                    "Do not calculate or infer it.",
    )

    abstract: Optional[str] = Field(
        None,
        description="Copy the abstract exactly from the supplied paper content. "
                    "Do not summarize, paraphrase, rewrite, or add information. "
                    "Do not include the Keywords section. If absent, return None.",
    )

    volume: Optional[str] = Field(
        None,
        description="Extract journal volume exactly as explicitly stated. Do not infer it.",
    )

    journal: Optional[str] = Field(
        None,
        description="Extract journal name exactly as explicitly stated. Do not infer it.",
    )

    journalURL: Optional[str] = Field(
        None,
        description="Extract journal URL only when explicitly present in the supplied paper. "
                    "Do not generate or guess a URL.",
    )

    publisher: Optional[str] = Field(
        None,
        description="Extract publisher only when explicitly stated. Do not infer it.",
    )

    pmid: Optional[str] = Field(
        None,
        description="Do not extract, generate, guess, calculate, or fabricate PMID. "
                    "PMID is assigned/enriched by the backend after extraction. "
                    "Return None unless supplied separately by the application.",
    )

    impactFactor: Optional[str] = Field(
        None,
        description="Extract impact factor only when explicitly mentioned in the supplied "
                    "article. Do not search, infer, calculate, or generate it.",
    )

    HIndex: Optional[str] = Field(
        None,
        description="Extract H-index only when explicitly mentioned in the supplied article. "
                    "Do not search, infer, calculate, or generate it.",
    )

    sciMAGO: Optional[str] = Field(
        None,
        description="Extract SCImago information only when explicitly mentioned in the supplied "
                    "article. Do not search, infer, calculate, or generate it.",
    )

    pages: Optional[str] = Field(
        None,
        description="Extract page information exactly as explicitly stated. "
                    "Do not calculate page count from a range.",
    )

    issue: Optional[str] = Field(
        None,
        description="Extract journal issue exactly as explicitly stated. Do not infer it.",
    )

    keywords: Optional[str] = Field(
        None,
        description="Extract explicitly listed keywords, comma-separated. "
                    "Do not generate or infer keywords from the article.",
    )

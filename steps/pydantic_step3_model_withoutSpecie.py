from pydantic import BaseModel, Field
from typing import Literal, Optional, Union, List, Dict

class VolumeOfWater(BaseModel):
    value: float = Field(..., description="Extract the explicitly reported volume of water per day. Do not calculate, infer, estimate, or convert.")
    unit: Literal["mL", "L"] = Field(..., description="Preserve the explicitly reported volume unit. Do not convert units.")

class ConcentrationHydrogen(BaseModel):
    value: float = Field(..., description="Extract the explicitly reported hydrogen concentration. Do not calculate, infer, estimate, or convert.")
    unit: Literal["mg/L", "mM", "uM"] = Field(..., description="Preserve the explicitly reported hydrogen concentration unit. Do not convert units.")

class AbsoluteDose(BaseModel):
    value: float = Field(..., description="Extract the explicitly reported absolute dose per day. Do not calculate or infer it.")
    unit: Literal["mg/day"] = Field(..., description="Preserve the explicitly reported absolute-dose unit. Do not convert units.")

class RelativeDose(BaseModel):
    value: float = Field(..., description="Extract the explicitly reported relative dose per day. Do not calculate or infer it.")
    unit: Literal["mg/kg/day"] = Field(..., description="Preserve the explicitly reported relative-dose unit. Do not convert units.")

class HydrogenConcentrationDetail(BaseModel):
    weight_of_specie: str = Field(..., description="Extract species weight exactly as explicitly reported, including its original unit. Do not calculate, estimate, or convert.")
    relative_dose_per_day: RelativeDose = Field(..., description="Relative dose per day with unit")
    absolute_dose_per_day: AbsoluteDose = Field(..., description="Absolute dose per day with unit")
    volume_of_water_per_day: VolumeOfWater = Field(..., description="Volume of water per day with unit")
    concentration: ConcentrationHydrogen = Field(..., description="Hydrogen concentration with unit")

class HydrogenAdministrationOralGavage(BaseModel):
    HowManyConcentrations: int = Field(..., description="Number of Unique Hydrogen Concentrations")
    details: List[HydrogenConcentrationDetail] = Field(
        ..., description="List of details for each unique concentration"
    )

class FlowRate(BaseModel):
    value: float = Field(..., description="Value of Flow Rate of Hydrogen")
    unit: Literal["mL/min"] = Field(..., description="Unit of Flow Rate of Hydrogen")

class HydrogenAdministrationInhalation(BaseModel):
    percent_purity: str = Field(..., description="Percent Purity")
    flow_rate: FlowRate = Field(..., description="Flow Rate of Hydrogen")
    frequency: str = Field(..., description="Frequency of Hydrogen Inhalation")
    duration_per_frequency: str = Field(..., description="Duration Per Frequency")

class HydrogenAdministrationBacteria(BaseModel):
    peak_breath_concentration: Optional[float] = Field(None, description="Peak Breath Hydrogen Concentration")
    frequency: Optional[str] = Field(None, description="Frequency")
    duration_per_frequency: Optional[str] = Field(None, description="Duration Per Frequency")

class HydrogenAdministrationTopical(BaseModel):
    methods: Optional[str] = Field(None, description="Methods of Topical Application")

class ConcentrationCellCulture(BaseModel):
    value: float = Field(..., description="Concentration of Hydrogen for the Medium (micro moles per liter)")
    unit: Literal["umoles/L"] = Field(..., description="Unit of Concentration of Hydrogen for the Medium (micro moles per liter)")

class HydrogenAdministrationCellCulture(BaseModel):
    concentration: Optional[ConcentrationCellCulture] = Field(None, description="Concentration of Hydrogen for the Medium")
    # frequency_cell_culture: Optional[str] = Field(None, description="Frequency")
    volumeCellCulture: Optional[str] = Field(None, description="Volume of Medium used in mL")
    # duration_per_frequency_cell_culture: Optional[str] = Field(None, description="Duration Per Frequency")
    exposureDurationCellCulture: Optional[str] = Field(None, description="Total Exposure Duration in Hours or Minutes")

class ERW(BaseModel):
    erw: Optional[bool] = Field(None, description="Return this only when the article explicitly states that it concerns Electrolyzed-Reduced Water (ERW). Do not infer from pH or water terminology.")
    pH: Optional[float] = Field(None, description="Extract ERW pH only when explicitly reported. Do not calculate or infer pH.")
    comparison: Optional[bool] = Field(None, description="Return True/False only when the article explicitly reports such a comparison. Do not infer a comparison." )

class MiscellaneousInfo(BaseModel):
    sex_difference: Optional[str] = Field(None, description="Was there a Sex Difference? True or False or Not Applicable (N/A)")
    responder_vs_non_responder: Optional[str] = Field(None, description="Does the study indicate a responder versus a non-responder? True or False")
    safety_study: Optional[bool] = Field(None, description="Was this study specifically on the safety of H2 or uniquely show its safety profile?")
    pregnantBreastfeeding: Optional[str] = Field(None, description="Were the species pregnant/breastfeeding? True or False")
    unique_safety_profile: Optional[str] = Field(None, description="Does the study have unique ways of showing the safety of Hydrogen? True or False")
    adverse_effects_flag: Optional[str] = Field(None, description="any adverse effects in the Article? True or False")
    adverse_effects_description: Optional[str] = Field(None, description="Describe any adverse effects")
    dose_dependent_effect: Optional[str] = Field(None, description="Does the study suggest a dose-dependent or concentration-dependent effect? True or False")
    mechanistic_insights: Optional[str] = Field(None, description="Does the study provide mechanistic insights? True or False")
    gene_expression_changes: Optional[str] = Field(None, description="Describe changes in gene expression")
    external_references: Optional[str] = Field(None, description="URL of video/news/blog article for this paper")
    Video_WebpageLink: Optional[str] = Field(None, description="Indicates if a video or webpage link is available.")
    PasteUrl: Optional[str] = Field(None, description="URL related to the research article or dataset.")
    commercialProduct: Optional[str] = Field(None, description="Indicates if a commercial product was used. Yes or No")
    brandName: Optional[str] = Field(None, description="Brand name of the commercial product used.")
    geneExpression: Optional[str] = Field(None, description="Indicates if gene expression analysis was performed. True or False")
    geneExpressionDesc: Optional[str] = Field(None, description="Description of gene expression findings.")


class NameStatusModel(BaseModel):
    name: Optional[str] = Field(None, description="The name or label associated with the entry.")

class ValueUnitStatusModel(BaseModel):
    value: Optional[str] = Field(None, description="Value associated with the entry.")
    unit: Optional[str] = Field(None, description="Unit of measurement.")

class SpeciesDataModel(BaseModel):
    isOpen: Optional[bool] = Field(None, description="Indicates if the species data is available.")
    HowManyConcentrations: Optional[int] = Field(None, description="Number of concentration values available in inhalation and Gavage. ( Interger Value )")
    volumes: Optional[List[ValueUnitStatusModel]] = Field(None, description="Extract volume only when explicitly reported in the article. Do not infer, calculate, estimate, generate, or convert it.")
    concentrations: Optional[List[ValueUnitStatusModel]] = Field(None, description="Extract hydrogen concentration only when explicitly reported. Do not infer, calculate, estimate, generate, or convert it.")
    absoluteDoses: Optional[List[ValueUnitStatusModel]] = Field(None, description="Extract absolute dose per day only when explicitly reported. Do not infer, calculate, estimate, generate, or convert it.")
    relativeDoses: Optional[List[ValueUnitStatusModel]] = Field(None, description="Extract relative dose per day only when explicitly reported. Do not infer, calculate, estimate, generate, or convert it.")
    inhalationConcentrations: Optional[List[HydrogenAdministrationInhalation]] = Field(None, description="Inhalation concentration data.")
    wasOxyhydrogenUsed: Optional[NameStatusModel] = Field(None, description="Extract only if the article explicitly states whether oxyhydrogen was used. Do not infer from the administration method.")
    isInhalationOpen: Optional[bool] = Field(None, description="Indicates if inhalation data is available.")
    isCellTissueOpen: Optional[bool] = Field(None, description="Indicates if cell/tissue data is available.")
    isIngestionOpen: Optional[bool] = Field(None, description="Indicates if ingestion data is available.")
    methods: Optional[List[Literal["Oral Hydrogen Water", "Gavage", "Inhalation", "Ingestion of H2 producing Bacteria","Topical Application",
                                    "Hydrogen-rich Saline", "Subcutaneous Injection of Hydrogen", "Cell Culture / Tissue", "Intraperitoneal Injection of Hydrogen Rich Solution"
                                    ]]] = Field(None, description="Extract administration methods explicitly reported in the article. Do not infer a method from context.")
    weight: Optional[str] = Field(None, description="Extract species weight exactly as explicitly reported, preserving the original unit. Do not convert to kilograms.")
    numInhalationConcentrations: Optional[NameStatusModel] = Field(None, description="Extract the explicitly reported number of inhalation concentration values. Do not count or calculate it yourself.")
    topicalMethod: Optional[NameStatusModel] = Field(None, description="Method used for topical application.")
    concentrationOfHydrogenForMedium: Optional[NameStatusModel] = Field(None, description="Extract hydrogen concentration in the medium only when explicitly reported. Do not calculate or infer it.")
    FrequencyCellCultureTissues: Optional[ValueUnitStatusModel] = Field(None, description="Extract exposure frequency only when explicitly reported. Do not infer or calculate it.")
    DurationFrequencyCellCultureTissues: Optional[ValueUnitStatusModel] = Field(None, description="Extract exposure duration only when explicitly reported. Do not infer or calculate it.")
    Peakbreathhydrogen: Optional[ValueUnitStatusModel] = Field(None, description="Extract peak breath hydrogen only when explicitly reported. Do not infer or calculate it.")
    Frequency: Optional[ValueUnitStatusModel] = Field(None, description="Extract administration frequency only when explicitly reported. Do not infer or calculate it.")
    IngestionDurationfrequency: Optional[ValueUnitStatusModel] = Field(None, description="Extract ingestion duration/frequency only when explicitly reported. Do not infer or calculate it.")


# STEP 3
class ArticleSpecificInformationWithOutSpecie(BaseModel):
   
    methods_without_Specie: List[Literal[
        "Oral Hydrogen Water", "Gavage", "Inhalation", "Ingestion of H2 producing Bacteria",
        "Topical Application", "Hydrogen-rich Saline", "Subcutaneous Injection of Hydrogen", "Cell Culture / Tissue",
        "Intraperitoneal injection of Hydrogen-Rich Solution", 
    ]]
    MethodsDetails: Optional[List[Union[
        HydrogenAdministrationOralGavage, HydrogenAdministrationInhalation,
        HydrogenAdministrationBacteria, HydrogenAdministrationTopical,
        HydrogenAdministrationCellCulture
    ]]]
    wasOxyhydrogenUsed: Optional[NameStatusModel] = Field(None, description="Extract only if the article explicitly states whether oxyhydrogen was used. Do not infer from the administration method.")
    numInhalationConcentrations: Optional[NameStatusModel] = Field(None, description="Extract the explicitly reported number of inhalation concentration values. Do not count or calculate it yourself.")
    concentrationOfHydrogenForMedium: Optional[NameStatusModel] = Field(None, description="Extract hydrogen concentration in the medium only when explicitly reported. Do not calculate or infer it.")


    comparison_of_methods_flag: Optional[bool] = Field(None, description="Study discusses the comparison of methods?")
    comparison_of_methods_description: Optional[str] = Field(None, description="Describe the comparison of methods")
    dose_concentration_comparison_flag: Optional[str] = Field(None, description="Study discusses the dose/concentration comparison? true or false")
    dose_concentration_comparison_description: Optional[str] = Field(None, description="Describe dose/concentration comparison")
    drug_therapy_supplement_comparison_flag: Optional[str] = Field(None, description="Study discusses the drug/therapy/supplement comparison? true or false")
    drug_therapy_supplement_comparison: Optional[str] = Field(None, description="Describe drug/therapy/supplement comparison")
    pharmacokinetics_flag: Optional[str] = Field(None, description="Does the study discusses the pharmacokinetics (H2 Concentration)? true or false")
    pharmacokinetics: Optional[str] = Field(None, description="Describe pharmacokinetics (H2 Concentration)")
    erw: Optional[str] = Field(None, description="Indicate whether the article is about Electrolyzed-Reduced Water (ERW), also known as ionized water or alkaline ionized water. true or false")
    miscellaneous: Optional[MiscellaneousInfo] = Field(None, description="Extract miscellaneous information only when explicitly reported. Do not infer or generate values.")


# Indicate whether the article is about Electrolyzed-Reduced Water (ERW), also known as ionized water or alkaline ionized water.


# STRICT EXTRACTION RULES
# -----------------------
# These models are intended for extraction from the supplied article only.
# Missing information must remain missing/None; it must never be inferred,
# calculated, estimated, converted, generated, or fabricated.
# Parser/business logic may later normalize missing values (for example to
# "N/A" or []) according to the application's output contract.

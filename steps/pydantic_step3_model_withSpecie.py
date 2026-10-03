from pydantic import BaseModel, Field
from typing import Literal, Optional, Union, List, Dict

class VolumeOfWater(BaseModel):
    value: float = Field(..., description="Volume of water per day. Extract only when explicitly reported in the paper. Do not infer, calculate, estimate, convert, or generate.")
    unit: Literal["mL", "L"] = Field(..., description="Unit of the explicitly reported volume of water. Preserve the reported unit.")

class ConcentrationHydrogen(BaseModel):
    value: float = Field(..., description="Hydrogen concentration value only when explicitly reported in the paper. Do not infer, calculate, estimate, or generate.")
    unit: Literal["mg/L", "mM", "uM"] = Field(..., description="Unit of the explicitly reported hydrogen concentration. Preserve the reported unit.")

class AbsoluteDose(BaseModel):
    value: float = Field(..., description="Absolute dose per day only when explicitly reported in the paper. Do not infer, calculate, estimate, or generate.")
    unit: Literal["mg/day"] = Field(..., description="Unit of the explicitly reported absolute dose per day. Preserve the reported unit.")

class RelativeDose(BaseModel):
    value: float = Field(..., description="Relative dose per day only when explicitly reported in the paper. Do not infer, calculate, estimate, or generate.")
    unit: Literal["mg/kg/day"] = Field(..., description="Unit of the explicitly reported relative dose per day. Preserve the reported unit.")

class HydrogenConcentrationDetail(BaseModel):
    weight_of_specie: str = Field(..., description="Weight of the species only when explicitly reported. Preserve the original value and unit exactly. Do not infer, calculate, estimate, or convert.")
    relative_dose_per_day: RelativeDose = Field(..., description="Relative dose per day with unit")
    absolute_dose_per_day: AbsoluteDose = Field(..., description="Absolute dose per day with unit")
    volume_of_water_per_day: VolumeOfWater = Field(..., description="Volume of water per day with unit")
    concentration: ConcentrationHydrogen = Field(..., description="Hydrogen concentration with unit")

class HydrogenAdministrationOralGavage(BaseModel):
    HowManyConcentrations: int = Field(..., description="Number of unique hydrogen concentration values explicitly reported in the paper. Do not infer or calculate missing conditions.")
    details: List[HydrogenConcentrationDetail] = Field(
        ..., description="Details for each explicitly reported hydrogen concentration condition."
    )

class FlowRate(BaseModel):
    value: float = Field(..., description="Hydrogen flow rate only when explicitly reported. Do not infer, calculate, estimate, or generate.")
    unit: Literal["mL/min"] = Field(..., description="Unit of Flow Rate of Hydrogen")

class HydrogenAdministrationInhalation(BaseModel):
    percent_purity: str = Field(..., description="Hydrogen purity percentage only when explicitly reported. Preserve the reported value exactly.")
    flow_rate: FlowRate = Field(..., description="Flow Rate of Hydrogen")
    frequency: str = Field(..., description="Frequency of hydrogen inhalation only when explicitly reported. Preserve the reported wording.")
    duration_per_frequency: str = Field(..., description="Duration per inhalation frequency only when explicitly reported. Preserve the reported wording.")

class HydrogenAdministrationBacteria(BaseModel):
    peak_breath_concentration: Optional[float] = Field(None, description="Peak Breath Hydrogen Concentration")
    frequency: Optional[str] = Field(None, description="Frequency")
    duration_per_frequency: Optional[str] = Field(None, description="Duration per inhalation frequency only when explicitly reported. Preserve the reported wording.")

class HydrogenAdministrationTopical(BaseModel):
    methods: Optional[str] = Field(None, description="Methods of Topical Application")

class ConcentrationCellCulture(BaseModel):
    value: float = Field(..., description="Concentration of Hydrogen for the Medium (micro moles per liter)")
    unit: Literal["umoles/L"] = Field(..., description="Unit of Concentration of Hydrogen for the Medium (micro moles per liter)")

class HydrogenAdministrationCellCulture(BaseModel):
    concentration: Optional[ConcentrationCellCulture] = Field(None, description="Concentration of Hydrogen for the Medium")
    volumeCellCulture: Optional[str] = Field(None, description="Volume of Medium used in mL")
    exposureDurationCellCulture: Optional[str] = Field(None, description="Total Exposure Duration in Hours or Minutes")

class ERW(BaseModel):
    erw: Optional[bool] = Field(None, description="Indicate whether the article is about Electrolyzed-Reduced Water (ERW), also known as ionized water or alkaline ionized water.")
    pH: Optional[float] = Field(None, description="pH of ERW")
    comparison: Optional[bool] = Field(None, description="Indicate whether the study compared the effects of Electrolyzed Reduced Water (ERW) to hydrogen-rich water." )

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
    value: Optional[str] = Field(None, description="value")
    unit: Optional[str] = Field(None, description="Unit of measurement.")



    

class SpeciesDataModel(BaseModel):
    specieName: Optional[str] = Field(None, description="Name of the specie as previously mentioned.")
    HowManyConcentrations: Optional[int] = Field(None, description="Number of unique hydrogen concentration values explicitly reported for inhalation or gavage. Count only explicitly reported conditions; do not infer or calculate.")
    volumes: Optional[List[ValueUnitStatusModel]] = Field(None, description="Extract the volume only when explicitly reported in the paper. Preserve the reported value and unit. Do not infer, calculate, estimate, or generate a value.")
    concentrations: Optional[List[ValueUnitStatusModel]] = Field(None, description="Extract hydrogen concentration only when explicitly reported in the paper. Preserve the reported value and unit. Do not infer, calculate, estimate, or generate a value.")
    absoluteDoses: Optional[List[ValueUnitStatusModel]] = Field(None, description="Extract absolute hydrogen dose per day only when explicitly reported in the paper. Preserve the reported value and unit. Do not infer, calculate, estimate, or generate a value.")
    relativeDoses: Optional[List[ValueUnitStatusModel]] = Field(None, description="Extract relative hydrogen dose per day only when explicitly reported in the paper. Preserve the reported value and unit. Do not infer, calculate, estimate, or generate a value.")
    inhalationConcentrations: Optional[List[HydrogenAdministrationInhalation]] = Field(None, description="Inhalation concentration data. ")
    wasOxyhydrogenUsed: Optional[NameStatusModel] = Field(None, description="Indicates if oxyhydrogen was used.")
    isInhalationOpen: Optional[bool] = Field(None, description="Indicates if inhalation data is available.")
    isCellTissueOpen: Optional[bool] = Field(None, description="Indicates if cell/tissue data is available.")
    isIngestionOpen: Optional[bool] = Field(None, description="Indicates if ingestion data is available.")
    methods: Optional[List[Literal[
        "Oral Hydrogen Water", "Gavage", "Inhalation", "Ingestion of H2 producing Bacteria",
        "Topical Application", "Hydrogen-rich Saline", "Subcutaneous Injection of Hydrogen", "Cell Culture / Tissue",
        "Intraperitoneal injection of Hydrogen-Rich Solution" 
    ]]] = Field(None, description="Methods used for administration.")
    weight: Optional[str] = Field(None, description="Weight of the species only when explicitly reported. Preserve the original value and unit exactly. Do not infer, calculate, estimate, or convert.")
    numInhalationConcentrations: Optional[NameStatusModel] = Field(None, description="Number of unique inhalation concentration conditions explicitly reported in the paper. Do not infer or calculate missing conditions.")
    topicalMethod: Optional[NameStatusModel] = Field(None, description="Method used for topical application.")
    concentrationOfHydrogenForMedium: Optional[NameStatusModel] = Field(None, description="Hydrogen concentration in the medium only when explicitly reported. Preserve the reported value and unit. Do not infer or calculate.")
    FrequencyCellCultureTissues: Optional[ValueUnitStatusModel] = Field(None, description="Frequency of hydrogen exposure in cell culture or tissues only when explicitly reported. Preserve the reported wording.")
    DurationFrequencyCellCultureTissues: Optional[ValueUnitStatusModel] = Field(None, description="Duration of hydrogen exposure in cell culture or tissues only when explicitly reported. Preserve the reported value and unit.")
    Peakbreathhydrogen: Optional[ValueUnitStatusModel] = Field(None, description="Peak breath hydrogen level only when explicitly reported. Preserve the reported value and unit.")
    Frequency: Optional[ValueUnitStatusModel] = Field(None, description="Frequency of hydrogen administration only when explicitly reported. Preserve the reported wording.")
    IngestionDurationfrequency: Optional[ValueUnitStatusModel] = Field(None, description="Duration and frequency of hydrogen ingestion only when explicitly reported. Preserve the reported wording.")


# STEP 3
class ArticleSpecificInformationWithSpecie(BaseModel):
    speciesData: Optional[List[SpeciesDataModel]] = Field(
        None, description="List of species data objects including the data of that specie.."
    )    
   
    comparison_of_methods_flag: Optional[bool] = Field(None, description="Study discusses the comparison of methods?")
    comparison_of_methods_description: Optional[str] = Field(None, description="Describe the comparison of methods")
    dose_concentration_comparison_flag: Optional[str] = Field(None, description="Study discusses the dose/concentration comparison? True or False")
    dose_concentration_comparison_description: Optional[str] = Field(None, description="Describe dose/concentration comparison")
    drug_therapy_supplement_comparison_flag: Optional[str] = Field(None, description="Study discusses the drug/therapy/supplement comparison? True or False")
    drug_therapy_supplement_comparison: Optional[str] = Field(None, description="Describe drug/therapy/supplement comparison")
    pharmacokinetics_flag: Optional[str] = Field(None, description="Does the study discusses the pharmacokinetics (H2 Concentration)? True or False")
    pharmacokinetics: Optional[str] = Field(None, description="Describe pharmacokinetics (H2 Concentration)")
    erw: Optional[str] = Field(None, description="Indicate whether the article is about Electrolyzed-Reduced Water (ERW), also known as ionized water or alkaline ionized water. True or False")
    miscellaneous: Optional[MiscellaneousInfo]
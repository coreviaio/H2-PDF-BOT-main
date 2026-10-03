from pydantic import BaseModel, Field
from typing import Literal, Optional, Union, List


class valueUnitModel(BaseModel):
    value: float = Field(..., description="Numerical Value of the field")
    unit: str = Field(..., description="Unit of the field")

class clinicaltrialDesignObj(BaseModel):
    clinicalTrialDesign: Optional[List[Literal["Non-Randomized Trial",
                                               "Randomized",
                                               "Double-Blinded",
                                               "Single-Blinded",
                                               "Unblinded",
                                               "Placebo-Controlled",
                                               "Non-Placebo-Controlled",
                                               "Pilot/Feasiblity",
                                               "Other"]]] = Field(None, description="Designs of clinical trials used")

class observationalStudyObj(BaseModel):
    observationalStudy: Optional[List[Literal["Cohort",
                                              "Cross-Sectional",
                                              "Case-Control",
                                              "Longitudinal",
                                              "Case report",
                                              "Survey",
                                              "Other"]]] = Field(None, description="Types of observational studies used In Vivo")

class HumanStudyData(BaseModel):
    clinical_trial_design: Optional[List[Literal["Clinical Trial Design", "Observational Study"]]] = Field(None, description="Clinical Trial Design or Observational Study")
    clinical_trial_design_details: List[Union[clinicaltrialDesignObj, observationalStudyObj]]

class AnimalStudyData(BaseModel):
    durationOfStudy: Optional[valueUnitModel] = Field(None, description="Duration of Study in Vivo")


class InVivoData(BaseModel):
    study_category: Literal["InVivo"]  # Discriminator Key
    studyTypeInVivo: List[Literal["Human", "Animal"]]
    details: Optional[HumanStudyData] = Field(None, description="Description of In Vivo Human Study")
    durationOfStudyInVivo: Optional[valueUnitModel] = Field(None, description="Duration of Study in Vivo")
    timingTreatmentInVivo: Optional[List[Literal["Pre-treatment", "Post-treatment", "Simultaneous"]]] = Field(None, description="What was the timing of the treatment in Vivo?")

class InVitroData(BaseModel):
    study_category: Literal["InVitro"]  # Discriminator Key
    durationOfStudyInVitro: Optional[valueUnitModel] = Field(None, description="Duration of Study in Vitro")
    WhatKindCell: Optional[str] = Field(None, description="Research involving cells grown in controlled conditions.")
    timingTreatmentInVitro: Optional[List[Literal["Pre-treatment", "Post-treatment", "Simultaneous"]]] = Field(None, description="What was the timing of the treatment in Vitro?")


class ExVivoData(BaseModel):
    study_category: Literal["ExVivo"]  # Discriminator Key
    durationOfStudyExVivo: Optional[valueUnitModel] = Field(None, description="Duration of Study in Ex Vivo")
    WhatCellTissueUsed: Optional[str] = Field(None, description="What Cell/Tissue Used?")
    timingTreatmentInExVivo: Optional[List[Literal["Pre-treatment", "Post-treatment", "Simultaneous"]]] = Field(None, description="What was the timing of the treatment in Ex Vitro?")


class OtherStudyData(BaseModel):
    study_category: Literal["Other"]  # Discriminator Key
    description: Optional[str] = Field(None, description="Description of Other Study Type methodology")


class ReviewStudyData(BaseModel):
    reviewStudyType: Optional[Literal["General", "Clinical Studies", "Molecular Mechanisms", "Systematic Review", "Meta-Analysis"]] = Field(None, description="Review Study Type")


class OpinionPieceData(BaseModel):
    OpinionPiece: Optional[str] = Field(None, description="Opinion Piece")


class HypothesisData(BaseModel):
    hypothesis: Optional[str] = Field(None, description="Articles proposing a theory or explanation.")



class TherapeuticDeliveryData(BaseModel):
    TherapeuticDeliverySystemsdetails: Optional[str] = Field(None, description="Therapeutic Delivery Systems Details")


class NonExperimentalData(BaseModel):
    study_category: Literal["Non-Experimental"]  # Discriminator Key
    non_experimental_type: List[Literal[
        "Review Study Type", "Opinion Piece", "Hypothesis", "Therapeutic Delivery Systems"
    ]]
    details:List[Union[ReviewStudyData, OpinionPieceData, HypothesisData, TherapeuticDeliveryData]]


class Age(BaseModel):
    value: float = Field(..., description="Numerical value of average age")
    unit: Literal["days", "months", "years"] = Field(..., description="Unit for average age")

class Weight(BaseModel):
    value: float = Field(..., description="Numerical value of average weight")
    unit:Literal["grams", "kilograms"] = Field(..., description="Unit for average weight")


class ArticleOutcome(BaseModel):
    text: str = Field(..., description="Brief explanation of the article's outcome.")
    outcomeType: str = Field(..., description="Sentiment of the article outcome: positive, negative, or neutral.")
    rank: int = Field(..., description="A rank assigned to the article between 0 and 100.")

class HighlightArticleObj(BaseModel):
    HighlightArticle: Optional[bool] = Field(None, description="Indicate if this article should be highlighted for notable outcomes or significant benefits.")
    description: Optional[str] = Field(None, description="If hilightArticle True, what was northworthy about this article?" )


class researchTopicModel(BaseModel):
    name: Optional[Literal["Cancer",
    "Diabetes",
    "Parkinson's",
    "Infectious Diseases",
    "Cardiovascular Diseases",
    "Neurological Disorders",
    "Autoimmune Disorders",
    "Metabolic Disorders",
    "Genetic Disorders",
    "Respiratory Diseases",
    "Gastrointestinal Disorders",
    "Metabolic Syndrome",
    "Toxicology and Poisoning",
    "Dermatological Diseases",
    "Musculoskeletal Disorders",
    "Renal Diseases",
    "Agriculture/Plants",
    "Liver Diseases",
    "Endocrine Disorders",
    "Reproductive Health",
    "Sensory Disorders",
    "Aging",
    "Exercise",
    "Health & Wellness / Prevention",
    "Mechanistic-Direct",
    "Mechanistic-Indirect",
    "Microbiome",
    "Plants/Agriculture",
    "Food-Processing",
    "Bacteria",
    "Osteonecrosis",
    "Oxidative Stress",
    "Hydrogen Therapy",
    "Osteoporosis",
    "Osteoclast",
    "Inflammatory Disorders",
    "Mesenchymal Stem Cells",
    "Anti-inflammatory",
    "Antitumor",
    "Obesity and CVD",
    "Bone",
    "Free Radicals Scavenging",
    "C57BL/6",
    "Reactive",
    "Mechanistic Studies",
    "Immunomodulation",
    "Gene Expression Regulation",
    "Cellular Differentiation",
    "Inflammation",
    "Apoptosis",
    "Respiratory System" ]] = Field(None, descrition="Research Topics covered in Article.")


class physiologicalSystemModel(BaseModel):
    name: Optional[Literal["Cardiovascular Systems","Integumentary Systems","Muscular Systems","Nervous Systems","Endocrine Systems","Lymphatic Systems","Respiratory Systems",
                           "Digestive Systems","Urinary System", "Immune System","General", "Skeletal", "Anti-type II collagen antibody-induced arthritis (Rheumatoid Arthritis Model)",
                           "Musculoskeletal System", "Inflammatory Diseases", "Heart Valves (specifically valve interstitial cells)", "Other Organs Systems", "Renal", "Neurological"
                           ]] = Field(None, description="Physiological systems studied in the article")
    

class organModel(BaseModel):
    name: Optional[Literal["Heart","Bone","Brain","Ears","Eyes","Kidneys","Liver","Muscle","Pancreas","Skin","Miscellaneous","Stomach","Intentines (Small & Large)", "Spleen", "Gland",
                           "Ovaries","Testes", "Uterus", "Prostate Gland", "Blood Vassels", "Lymph Nodes","Cartillage", "Adipose","Blood", "Nerves", "Thymus",
                           "GallBladder", "Bladder", "Nose", "Mouth", "Thyroid Gland","Adrenal Gland", "Pituitary Gland", "Others", "General", "Femur", "Tivia", "Marrow",
                           "Immune System", "Musculoskeletal System", "Tumors", "Lungs", "Aortic valves", "Gastrointestinal", "One ( since Mg is a biomaterial for tissue replacement )",
                           "Immune Cells", "Peritoneum", "Periodontal Tissue", "Endothelial", "Cells only", "Tumor Tissue", "Fibrotic"
                           ]] = Field(None, description="Organs or Tissues studied in the article")



# STEP 2 WITHOUT SPECIE:

class ArticleGeneralDataWithOutSpecie(BaseModel):

    outcome: Optional[ArticleOutcome] = Field(None, description="outcome details of the article.")
    HighlightArticle: Optional[HighlightArticleObj] = Field(None, description="Indicate if this article should be highlighted for notable outcomes or significant benefits.")
    studyType: Optional[List[Literal["In Vivo", "In Vitro", "Ex Vivo","In Silico", "Chemical/Physicochemical Study","Review", "Other", "Non-Experimental"]]] = Field(None, description="Study Type of the article")
    studyTypeDetails: List[Union[InVivoData, InVitroData, ExVivoData, OtherStudyData, NonExperimentalData]] # Removed "Optional"
    researchtopic: Optional[List[researchTopicModel]] = Field(None, description="Research topics covered in the article")
    diseaseModel: Optional[str] = Field(None, description="Disease Model studied in Article")
    system: Optional[List[physiologicalSystemModel]] = Field(None, description="Biological systems studied")
    organ: Optional[List[organModel]] = Field(None, description="Organs studied in the research")

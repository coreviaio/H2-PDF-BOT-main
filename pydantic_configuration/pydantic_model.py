from pydantic import BaseModel
from steps.pydantic_step1_model import ArticleCitationInformation
from steps.pydantic_step2_model_withoutSpecie import ArticleGeneralDataWithOutSpecie
from steps.pydantic_step2_model_withSpecie import ArticleGeneralDataWithSpecie 
from steps.pydantic_step3_model_withoutSpecie import ArticleSpecificInformationWithOutSpecie 
from steps.pydantic_step3_model_withSpecie import ArticleSpecificInformationWithSpecie 
from steps.pydantic_step4_model import BiomarkersList

# from new_pydantic_steps import publicDataClass, articleGeneralDataClass, researcherDataClass, biomakerClass

class ArticleExtractedDataWithSpecie(BaseModel):
    step_1:ArticleCitationInformation
    # OLD
    # step_2:ArticleGeneralData
    
    # NEW
    # step_2:ArticleGeneralDataWithOutSpecie
    step_2:ArticleGeneralDataWithSpecie
    
    # NEW
    # step_3:ArticleSpecificInformationWithOutSpecie
    step_3:ArticleSpecificInformationWithSpecie
    
    step_4:BiomarkersList
    
    # step_1:publicDataClass.PublicDataModel
    # step_2:articleGeneralDataClass.ArticleGeneralDataModel
    # step_3_with_specie:researcherDataClass.ResearcherDataModel
    # # step_3_without_specie:researcherDataClass.withOutSpecie
    # # step_3:researcherDataClass.ResponseModel
    # step_4:biomakerClass.BiomarkerModel


class ArticleExtractedDataWithoutSpecie(BaseModel):
    step_1:ArticleCitationInformation
    # OLD
    # step_2:ArticleGeneralData
    
    # NEW
    step_2:ArticleGeneralDataWithOutSpecie
    # step_2:ArticleGeneralDataWithSpecie
    
    # NEW
    step_3:ArticleSpecificInformationWithOutSpecie
    # step_3:ArticleSpecificInformationWithSpecie
    
    step_4:BiomarkersList
    
    # step_1:publicDataClass.PublicDataModel
    # step_2:articleGeneralDataClass.ArticleGeneralDataModel
    # step_3_with_specie:researcherDataClass.ResearcherDataModel
    # # step_3_without_specie:researcherDataClass.withOutSpecie
    # # step_3:researcherDataClass.ResponseModel
    # step_4:biomakerClass.BiomarkerModel
import json






def find_first_value(input_json,data, target_key):
    """
    Recursively searches for target_key in nested dictionaries and lists.
    Returns the associated value immediately upon finding the key.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            # Search deeper if the value is a dict or list
            if isinstance(value, (dict, list)):
                result = find_first_value(input_json,value, target_key)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = find_first_value(input_json,item, target_key)
            if result is not None:
                return result
    return None




def add_status(data):
    """
    Recursively adds 'status': 'unverified' to dictionaries that contain the key 'name'
    and its value is not None. If 'name' exists and is None, the dictionary is replaced with {}.
    """
    if isinstance(data, dict):
        # If 'name' exists and is None, return an empty dictionary
        if "name" in data and data["name"] is None:
            return None
        # If 'name' exists and is not None, add 'status'
        if "name" in data:
            data["status"] = "unverified"
        # Recursively process each value
        for key, value in list(data.items()):
            data[key] = add_status(value)
    elif isinstance(data, list):
        data = [add_status(item) for item in data]
    return data


def replace_none_with_empty_string(data):
    """
    Recursively replaces all None values with an empty string (""), no matter where they are in the structure.
    """
    if isinstance(data, dict):
        return {
            key: replace_none_with_empty_string(value) if value is not None else ""
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [replace_none_with_empty_string(item) for item in data]
    else:
        return data

def find_first_value(data, target_key):
    """
    Recursively searches for target_key in nested dictionaries and lists.
    Returns the associated value immediately upon finding the key.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            # Search deeper if the value is a dict or list
            if isinstance(value, (dict, list)):
                result = find_first_value(value, target_key)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = find_first_value(item, target_key)
            if result is not None:
                return result
    return None





def parse_to_without_specie_json(input_json):
    publicData = { "title": {"name": find_first_value(input_json,'title')},
        "pmid": {"name": find_first_value(input_json, 'pmid')[0] if find_first_value(input_json, 'pmid') else ""},
        "doi": {"name": find_first_value(input_json,'doi')},
        "authors": [x for x in find_first_value(input_json,'authors')],
        "abstract": {"name": find_first_value(input_json,'abstract')},
        "year": {"name": find_first_value(input_json,'year')},
        "journal": {"name": find_first_value(input_json,'journal')},
        "publisher": {"name": find_first_value(input_json,'publisher')},
        "impactFactor": {"name": find_first_value(input_json,'impactFactor')},
        "HIndex": {"name": find_first_value(input_json,'HIndex')},
        "sciMAGO": {"name": find_first_value(input_json,'sciMAGO')},
        "volume": {"name": find_first_value(input_json,'volume')},
        "issue": {"name": find_first_value(input_json,'issue')},
        "pages": {"name": find_first_value(input_json,'pages')},
        "country": [{"name":find_first_value(input_json,'country')}],
        "grantCountry": {"name": find_first_value(input_json,'grantCountry')},
        "researchCountry": [{"name": find_first_value(input_json,'researchCountry')}],
        "keywords": {"name": find_first_value(input_json,'keywords')}
        }



    articleGeneralData = {
        "outcome": {"name": find_first_value(find_first_value(input_json,'outcome'),'text')},
        "outcomeType": [find_first_value(find_first_value(input_json,'outcome'),'outcomeType')],
        "rankThisArticle": {"name": find_first_value(find_first_value(input_json,'outcome'),'rank')},
        "HighlightArticle": {"name": find_first_value(find_first_value(input_json,'HighlightArticle'),'HighlightArticle')},
        "descHighArt": {"name": find_first_value(find_first_value(input_json,'HighlightArticle'),'description')},
        "studyType": [{"name": study} for study in find_first_value(input_json,'studyType')],
        
        #Non-Experimental
        
        "NonExperimentalSelect": [{"name": select} for select in find_first_value(input_json,'non_experimental_type') or []],
        "ReviewStudyType": {"name": find_first_value(input_json,'reviewStudyType')},
        "OpinionPiece": {"name": find_first_value(input_json,'OpinionPiece')},
        "Hypothesis": {"name": find_first_value(input_json,'hypothesis')},
        "TherapeuticDeliverySystems": {"name": find_first_value(input_json,'TherapeuticDeliverySystemsdetails')},
        
        
        
        #In Vivo Stuff
        "inVivo": [],
        "selectedStudyTypes" : find_first_value(input_json, 'clinical_trial_design') or [],
        "clinicalTrialDesign" : find_first_value(find_first_value(input_json, 'clinical_trial_design_details'),'clinicalTrialDesign') or [],
        "observationalStudyObj" : find_first_value(find_first_value(input_json, 'clinical_trial_design_details'),'observationalStudy') or [],
        "durationOfStudy": {"name": find_first_value(find_first_value(input_json,'durationOfStudyInVivo'),'value')},
        "studyDurationUnit": find_first_value(find_first_value(input_json,'durationOfStudyInVivo'),'unit'),
        "timingTreatmentInVivo": [{"name": timing} for timing in find_first_value(input_json,'timingTreatmentInVivo') or []],
        #In vitro stuff
        
        "durationOfStudyinVitro": {"name": find_first_value(find_first_value(input_json,'durationOfStudyinVitro'),'value')},
        "UnitOfStudyInVitro": {"name": find_first_value(find_first_value(input_json,'durationOfStudyinVitro'),'unit')},
        "timingTreatmentInVitro": [{"name": timing} for timing in find_first_value(input_json,'timingTreatmentInVitro') or []] ,
        
        #Ex vivo stuff
        "WhatCellTissueUsed": {"name": find_first_value(input_json,'WhatCellTissueUsed')},
        "durationOfStudyExVivo": {"name": find_first_value(find_first_value(input_json,'durationOfStudyExVivo'),'value')},
        "UnitOfStudyExVivo": {"name": find_first_value(find_first_value(input_json,'durationOfStudyExVivo'),'unit')},
        "timingTreatmentExVivo": [{"name": timing} for timing in find_first_value(input_json,'timingTreatmentInExVivo') or []] ,
        
        #Other
        "Other": {"name": find_first_value(find_first_value(input_json,'studyTypeDetails'),'description')},
        
        
        "researchtopic": find_first_value(input_json,'researchtopic'),
        
        "diseaseModel": {"name": find_first_value(input_json,'diseaseModel')},
        
        "system": find_first_value(input_json,'system'),
        "organ": find_first_value(input_json,'organ'),
        
        
    }




    researcherData = {
        "methodOfAdmin": [{"name": method} for method in find_first_value(input_json,'methods_without_Specie') ],
        "wasOxyhydrogenUsed": {"name": find_first_value(input_json,'wasOxyhydrogenUsed')},
        "numInhalationConcentrations": 0,
        
        "inhalationConcentrations": [],
        
        "HowManyConcentrations": {"name": find_first_value(input_json,'HowManyConcentrations')},
        
        "volumes":[],
        "concentrations":[],
        "absoluteDoses":[],
        "relativeDoses":[],
        
        "bodyWeight":"75 kg",
        "Peakbreathhydrogen":{"name": find_first_value(input_json,'peak_breath_concentration')},
        "Frequency":"EXPLAINATION REQUIRED (frequency of what exactly?)",
        "IngestionDurationfrequency":"EXPLAINATION REQUIRED (unit of what)",
        "concentrationOfHydrogenForMedium":{"name": find_first_value(input_json,'concentrationOfHydrogenForMedium')},
        "FrequencyCellCultureTissues":{"name": find_first_value(input_json,'frequency_cell_culture')},
        "DurationFrequencyCellCultureTissues":{"name": find_first_value(input_json,'duration_per_frequency_cell_culture')},
        "unitDuration":"EXPLAINATION REQUIRED (unit of what)",
        "topical_how":"EXPLAINATION REQUIRED (unit of what)",
        
        
        "CompMethodAdmin":{"name":find_first_value(input_json,'comparison_of_methods_flag')},
        "CompMethodAdminDesc":{"name":find_first_value(input_json,'comparison_of_methods_description')},
        "doseComparison":{"name":find_first_value(input_json,'dose_concentration_comparison_flag')},
        "doseComparisonDesc":{"name":find_first_value(input_json,'dose_concentration_comparison_description')},
        "drugComparison":{"name":find_first_value(input_json,'drug_therapy_supplement_comparison_flag')},
        "comparisonDetail":{"name":find_first_value(input_json,'drug_therapy_supplement_comparison')},
        "pharmacokinetics":{"name":find_first_value(input_json,'pharmacokinetics_flag')},
        "pharmacokineticsDescription":{"name":find_first_value(input_json,'pharmacokinetics')},
        "isERW":{"name":find_first_value(input_json,'erw')},
        "ph":{"name":find_first_value(input_json,'pH')},
        "erwCompared":{"name":find_first_value(input_json,'comparison')},
        "adverseEffects":{"name":find_first_value(input_json,'adverse_effects_flag')},
        "adverseEffectsDescription":{"name":find_first_value(input_json,'adverse_effects_description')},
        "doseDependentEffect":{"name":find_first_value(input_json,'dose_dependent_effect')},
        "safetyProfile":{"name":find_first_value(input_json,'unique_safety_profile')},
        "safetyofhydrogen":{"name":find_first_value(input_json,'safety_study')},
        
        
        "sexDifference": {
                "name": find_first_value(input_json,'sex_difference'),
            },
        "responderDifference": {
                "name": find_first_value(input_json,'responder_vs_non_responder'),
            },
        "pregnantBreastfeeding": {
                "name": find_first_value(input_json,'pregnantBreastfeeding'),
            },
        "mechanisticInsights": {
                "name": find_first_value(input_json,'mechanistic_insights'),
            },
        "Video_WebpageLink": {
                "name": find_first_value(input_json,'Video_WebpageLink'),
            },
        "PasteUrl": {
                "name": find_first_value(input_json,'PasteUrl'),
            },
        "commercialProduct": {
                "name": find_first_value(input_json,'commercialProduct'),
            },
        "brandName": {
                "name": find_first_value(input_json,'brandName'),
            },
        "geneExpression": {
                "name": find_first_value(input_json,'geneExpression'),
            },
        "geneExpressionDesc": {
                "name": find_first_value(input_json,'geneExpressionDesc'),
            },
        
    
    
        
        
    }


    #Decision based on study details
    study_details = find_first_value(input_json,'studyTypeDetails')
    # if study_details:
    for i in study_details:
        if 'invivo' in i['study_category'].lower() or 'in-vivo' in i['study_category'].lower():
            for j in i['studyTypeInVivo']:
                articleGeneralData['inVivo'].append({"name": j})
                
                
    num_inhalation_concentrations = 0      
    for i in find_first_value(input_json,'MethodsDetails') or []:
        num_inhalation_concentrations = 0
        if 'details' in i.keys():
            for j in i['details']:
                researcherData['volumes'].append({ 
                "value": {"name":find_first_value(find_first_value(j,'volume_of_water_per_day'),'value')},
                "unit": {"name":find_first_value(find_first_value(j,'volume_of_water_per_day'),'unit')},
                        }),
                
                researcherData['concentrations'].append({ 
                "value": {"name":find_first_value(find_first_value(j,'concentration'),'value')},
                "unit": {"name":find_first_value(find_first_value(j,'concentration'),'unit')},
                        }),
                
                researcherData['absoluteDoses'].append({ 
                "value": {"name":find_first_value(find_first_value(j,'absolute_dose_per_day'),'value')},
                "unit": {"name":find_first_value(find_first_value(j,'absolute_dose_per_day'),'unit')},
                        }),
                
                researcherData['relativeDoses'].append({ 
                "value": {"name":find_first_value(find_first_value(j,'relative_dose_per_day'),'value')},
                "unit": {"name":find_first_value(find_first_value(j,'relative_dose_per_day'),'unit')},
                        }),
                
                researcherData['relativeDoses'].append({ 
                "value": {"name":find_first_value(find_first_value(j,'relative_dose_per_day'),'value')},
                "unit": {"name":find_first_value(find_first_value(j,'relative_dose_per_day'),'unit')},
                        }),
        if "percent_purity" in i.keys():
            num_inhalation_concentrations += 1
            researcherData['inhalationConcentrations'].append(
                {
                    "percentPurity": {
                        "name": i["percent_purity"]               
                        },
                    "flowRate": {
                        "name": i['flow_rate']['value']                
                        },
                    "frequency": {
                        "name": i['frequency']               
                        },
                    "duration": {
                        "name": i['duration_per_frequency']                
                        },
                    "unitFlowRate": {
                        "name": i['flow_rate']['unit']                
                        },
                    "unitDuration": {
                        "name": i['duration_per_frequency'].split(" ")[1]             
                        }
                }
            )
        # elif "peak_breath_concentration" in i.keys(): 
            

    researcherData['numInhalationConcentrations'] = num_inhalation_concentrations          



    for index, value in enumerate(researcherData['inhalationConcentrations']):
        researcherData[f"inhalationConcentration_{index}_percentPurity"] = {"name":value['percentPurity']['name']}
        researcherData[f"inhalationConcentration_{index}_flowRate"] = {"name":value['flowRate']['name']}
        researcherData[f"inhalationConcentration_{index}_frequency"] = {"name":value['frequency']['name']}
        researcherData[f"inhalationConcentration_{index}_duration"] = {"name":value['duration']['name']}
        
    for index, value in enumerate(researcherData['volumes']):
        researcherData[f"volume_{index}_value"] = {"name":value['value']['name']}
        researcherData[f"volume_{index}_unit"] = {"name":value['unit']['name']}
        
    for index, value in enumerate(researcherData['concentrations']):
        researcherData[f"concentration_{index}_value"] = {"name":value['value']['name']}
        researcherData[f"concentration_{index}_unit"] = {"name":value['unit']['name']}
        
    for index, value in enumerate(researcherData['absoluteDoses']):
        researcherData[f"absoluteDoses_{index}_value"] = {"name":value['value']['name']}
        researcherData[f"absoluteDoses_{index}_unit"] = {"name":value['unit']['name']}
        
    for index, value in enumerate(researcherData['relativeDoses']):
        researcherData[f"relativeDoses_{index}_value"] = {"name":value['value']['name']}
        researcherData[f"relativeDoses_{index}_unit"] = {"name":value['unit']['name']}
        


    biomaker = find_first_value(input_json,'biomarkers')
    

    parsed_data = {
        "publicData": publicData,
        "articleGeneralData":articleGeneralData,
        "researcherData":researcherData,
        "biomaker":biomaker
        }
    #Above Step1 fields has been extracted.. Now will extract step2 by comparing it with original form

    parsed_data = add_status(parsed_data)
    parsed_data = replace_none_with_empty_string(parsed_data)
    return parsed_data




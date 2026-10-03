import json


NA = "N/A"
UNVERIFIED = "Unverified"


def find_first_value(data, target_key):
    """
    Recursively find the first occurrence of target_key.

    This helper is kept for compatibility with the existing parser flow.
    It does not calculate, infer, or transform the extracted value.
    """
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]

        for value in data.values():
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


def get_name(value):
    """Safely convert a scalar/object value to the parser's name field."""
    if isinstance(value, dict):
        if "name" in value:
            return value["name"]
        if "value" in value:
            return value["value"]
    return value


def name_field(value):
    """Create the frontend's {name: ...} structure without inventing data."""
    return {"name": value if value not in (None, "") else NA}


def add_status(data):
    """
    Add status only to frontend name objects.

    Missing values are represented as N/A instead of being converted into
    unrelated status objects. Lists and dictionaries retain their structure.
    """
    if isinstance(data, dict):
        result = {}

        for key, value in data.items():
            if key == "name":
                result[key] = value if value not in (None, "") else NA
                continue

            result[key] = add_status(value)

        # Only objects that are actually name/value display objects get status.
        if "name" in result:
            result["status"] = UNVERIFIED

        return result

    if isinstance(data, list):
        return [add_status(item) for item in data]

    return data


def replace_none_with_na(data):
    """
    Normalize missing scalar values to N/A while preserving empty arrays.
    """
    if isinstance(data, dict):
        return {
            key: replace_none_with_na(value)
            for key, value in data.items()
        }

    if isinstance(data, list):
        return [replace_none_with_na(item) for item in data]

    if data is None or data == "":
        return NA

    return data


def safe_list(value):
    return value if isinstance(value, list) else []


def safe_dict(value):
    return value if isinstance(value, dict) else {}


def first_value(data, key, default=None):
    value = find_first_value(data, key)
    return default if value is None else value


def nested_value(data, parent_key, child_key, default=None):
    parent = first_value(data, parent_key)
    if not isinstance(parent, (dict, list)):
        return default

    value = find_first_value(parent, child_key)
    return default if value is None else value


def build_value_unit(value_obj):
    """
    Convert a value/unit model to the existing frontend shape.
    No calculation or unit conversion is performed.
    """
    value_obj = safe_dict(value_obj)

    value = value_obj.get("value")
    unit = value_obj.get("unit")

    return {
        "value": name_field(value),
        "unit": name_field(unit),
    }


def parse_to_without_specie_json(input_json):
    """
    Transform the Pydantic extraction result into the existing frontend JSON.

    Important:
    - No values are generated.
    - No doses/concentrations are calculated.
    - No missing values are guessed.
    - Missing scalar values become N/A during final normalization.
    - Missing arrays remain [].
    - PMID is passed through without taking the first character.
    """

    # ------------------------------------------------------------------
    # STEP 1: PUBLIC DATA
    # ------------------------------------------------------------------

    pmid_value = first_value(input_json, "pmid")

    authors = safe_list(first_value(input_json, "authors", []))

    publicData = {
        "title": name_field(first_value(input_json, "title")),
        "pmid": {"name": first_value(input_json, "pmid")},
        "doi": name_field(first_value(input_json, "doi")),
        "authors": authors,
        "abstract": name_field(first_value(input_json, "abstract")),
        "year": name_field(first_value(input_json, "year")),
        "journal": name_field(first_value(input_json, "journal")),
        "publisher": name_field(first_value(input_json, "publisher")),
        "impactFactor": name_field(first_value(input_json, "impactFactor")),
        "HIndex": name_field(first_value(input_json, "HIndex")),
        "sciMAGO": name_field(first_value(input_json, "sciMAGO")),
        "volume": name_field(first_value(input_json, "volume")),
        "issue": name_field(first_value(input_json, "issue")),
        "pages": name_field(first_value(input_json, "pages")),
        "country": [name_field(first_value(input_json, "country"))],
        "grantCountry": name_field(first_value(input_json, "grantCountry")),
        "researchCountry": [name_field(first_value(input_json, "researchCountry"))],
        "keywords": name_field(first_value(input_json, "keywords")),
    }

    # journalURL is part of Step-1 but was previously not mapped here.
    # Preserve it if the frontend expects it.
    publicData["journalURL"] = name_field(
        first_value(input_json, "journalURL")
    )

    # ------------------------------------------------------------------
    # STEP 2: ARTICLE GENERAL DATA
    # ------------------------------------------------------------------

    outcome = safe_dict(first_value(input_json, "outcome"))
    highlight = safe_dict(first_value(input_json, "HighlightArticle"))

    study_types = safe_list(first_value(input_json, "studyType"))
    study_details = safe_list(first_value(input_json, "studyTypeDetails"))

    articleGeneralData = {
        "outcome": name_field(outcome.get("text")),
        "outcomeType": safe_list(
            outcome.get("outcomeType")
            if isinstance(outcome.get("outcomeType"), list)
            else (
                [outcome.get("outcomeType")]
                if outcome.get("outcomeType") is not None
                else []
            )
        ),
        "rankThisArticle": name_field(outcome.get("rank")),
        "HighlightArticle": name_field(highlight.get("HighlightArticle")),
        "descHighArt": name_field(highlight.get("description")),

        "studyType": [
            name_field(study)
            for study in study_types
            if study not in (None, "")
        ],

        # Non-experimental
        "NonExperimentalSelect": [
            name_field(select)
            for select in safe_list(first_value(
                input_json, "non_experimental_type", []
            ))
        ],
        "ReviewStudyType": name_field(
            first_value(input_json, "reviewStudyType")
        ),
        "OpinionPiece": name_field(
            first_value(input_json, "OpinionPiece")
        ),
        "Hypothesis": name_field(
            first_value(input_json, "hypothesis")
        ),
        "TherapeuticDeliverySystems": name_field(
            first_value(
                input_json,
                "TherapeuticDeliverySystemsdetails"
            )
        ),

        # In Vivo
        "inVivo": [],
        "selectedStudyTypes": safe_list(
            first_value(input_json, "clinical_trial_design", [])
        ),
        "clinicalTrialDesign": safe_list(
            nested_value(
                input_json,
                "clinical_trial_design_details",
                "clinicalTrialDesign",
                []
            )
        ),
        "observationalStudyObj": safe_list(
            nested_value(
                input_json,
                "clinical_trial_design_details",
                "observationalStudy",
                []
            )
        ),
        "durationOfStudy": name_field(
            nested_value(
                input_json,
                "durationOfStudyInVivo",
                "value"
            )
        ),
        "studyDurationUnit": first_value(
            safe_dict(first_value(
                input_json, "durationOfStudyInVivo", {}
            )),
            "unit"
        ),
        "timingTreatmentInVivo": [
            name_field(timing)
            for timing in safe_list(
                first_value(input_json, "timingTreatmentInVivo", [])
            )
        ],

        # In Vitro
        "durationOfStudyinVitro": name_field(
            nested_value(
                input_json,
                "durationOfStudyInVitro",
                "value"
            )
        ),
        "UnitOfStudyInVitro": first_value(
            safe_dict(first_value(
                input_json, "durationOfStudyInVitro", {}
            )),
            "unit"
        ),
        "timingTreatmentInVitro": [
            name_field(timing)
            for timing in safe_list(
                first_value(input_json, "timingTreatmentInVitro", [])
            )
        ],

        # Ex Vivo
        "WhatCellTissueUsed": name_field(
            first_value(input_json, "WhatCellTissueUsed")
        ),
        "durationOfStudyExVivo": name_field(
            nested_value(
                input_json,
                "durationOfStudyExVivo",
                "value"
            )
        ),
        "UnitOfStudyExVivo": first_value(
            safe_dict(first_value(
                input_json, "durationOfStudyExVivo", {}
            )),
            "unit"
        ),
        "timingTreatmentExVivo": [
            name_field(timing)
            for timing in safe_list(
                first_value(input_json, "timingTreatmentInExVivo", [])
            )
        ],

        # Other
        "Other": name_field(
            nested_value(
                input_json,
                "studyTypeDetails",
                "description"
            )
        ),

        "researchtopic": first_value(
            input_json, "researchtopic", []
        ),
        "diseaseModel": name_field(
            first_value(input_json, "diseaseModel")
        ),
        "system": first_value(input_json, "system", []),
        "organ": first_value(input_json, "organ", []),
    }

    # ------------------------------------------------------------------
    # IN VIVO STUDY DETAILS
    # ------------------------------------------------------------------

    for item in study_details:
        if not isinstance(item, dict):
            continue

        category = str(item.get("study_category", "")).lower()

        if category in ("invivo", "in-vivo", "in vivo"):
            for study_type in safe_list(item.get("studyTypeInVivo")):
                articleGeneralData["inVivo"].append(
                    name_field(study_type)
                )

    # ------------------------------------------------------------------
    # STEP 3: RESEARCHER DATA
    # ------------------------------------------------------------------

    methods_without_specie = safe_list(
        first_value(input_json, "methods_without_Specie", [])
    )

    researcherData = {
        "methodOfAdmin": [
            name_field(method)
            for method in methods_without_specie
        ],

        "wasOxyhydrogenUsed": name_field(
            first_value(input_json, "wasOxyhydrogenUsed")
        ),

        "numInhalationConcentrations": 0,
        "inhalationConcentrations": [],

        "HowManyConcentrations": name_field(
            first_value(input_json, "HowManyConcentrations")
        ),

        "volumes": [],
        "concentrations": [],
        "absoluteDoses": [],
        "relativeDoses": [],

        "bodyWeight": name_field(
            first_value(input_json, "weight")
        ),

        "Peakbreathhydrogen": name_field(
            first_value(input_json, "peak_breath_concentration")
        ),

        "Frequency": name_field(
            first_value(input_json, "Frequency")
        ),

        "IngestionDurationfrequency": name_field(
            first_value(input_json, "IngestionDurationfrequency")
        ),

        "concentrationOfHydrogenForMedium": name_field(
            first_value(
                input_json,
                "concentrationOfHydrogenForMedium"
            )
        ),

        "FrequencyCellCultureTissues": name_field(
            first_value(input_json, "frequency_cell_culture")
        ),

        "DurationFrequencyCellCultureTissues": name_field(
            first_value(
                input_json,
                "duration_per_frequency_cell_culture"
            )
        ),

        "unitDuration": name_field(
            first_value(input_json, "unitDuration")
        ),

        "topical_how": name_field(
            first_value(input_json, "topical_how")
        ),

        "CompMethodAdmin": name_field(
            first_value(input_json, "comparison_of_methods_flag")
        ),
        "CompMethodAdminDesc": name_field(
            first_value(
                input_json,
                "comparison_of_methods_description"
            )
        ),

        "doseComparison": name_field(
            first_value(
                input_json,
                "dose_concentration_comparison_flag"
            )
        ),
        "doseComparisonDesc": name_field(
            first_value(
                input_json,
                "dose_concentration_comparison_description"
            )
        ),

        "drugComparison": name_field(
            first_value(
                input_json,
                "drug_therapy_supplement_comparison_flag"
            )
        ),
        "comparisonDetail": name_field(
            first_value(
                input_json,
                "drug_therapy_supplement_comparison"
            )
        ),

        "pharmacokinetics": name_field(
            first_value(input_json, "pharmacokinetics_flag")
        ),
        "pharmacokineticsDescription": name_field(
            first_value(input_json, "pharmacokinetics")
        ),

        "isERW": name_field(
            first_value(input_json, "erw")
        ),
        "ph": name_field(
            first_value(input_json, "pH")
        ),
        "erwCompared": name_field(
            first_value(input_json, "comparison")
        ),

        "adverseEffects": name_field(
            first_value(input_json, "adverse_effects_flag")
        ),
        "adverseEffectsDescription": name_field(
            first_value(
                input_json,
                "adverse_effects_description"
            )
        ),

        "doseDependentEffect": name_field(
            first_value(input_json, "dose_dependent_effect")
        ),
        "safetyProfile": name_field(
            first_value(input_json, "unique_safety_profile")
        ),
        "safetyofhydrogen": name_field(
            first_value(input_json, "safety_study")
        ),

        "sexDifference": name_field(
            first_value(input_json, "sex_difference")
        ),
        "responderDifference": name_field(
            first_value(
                input_json,
                "responder_vs_non_responder"
            )
        ),
        "pregnantBreastfeeding": name_field(
            first_value(input_json, "pregnantBreastfeeding")
        ),
        "mechanisticInsights": name_field(
            first_value(input_json, "mechanistic_insights")
        ),
        "Video_WebpageLink": name_field(
            first_value(input_json, "Video_WebpageLink")
        ),
        "PasteUrl": name_field(
            first_value(input_json, "PasteUrl")
        ),
        "commercialProduct": name_field(
            first_value(input_json, "commercialProduct")
        ),
        "brandName": name_field(
            first_value(input_json, "brandName")
        ),
        "geneExpression": name_field(
            first_value(input_json, "geneExpression")
        ),
        "geneExpressionDesc": name_field(
            first_value(input_json, "geneExpressionDesc")
        ),
    }

    # ------------------------------------------------------------------
    # METHOD DETAILS
    # ------------------------------------------------------------------

    methods_details = safe_list(
        first_value(input_json, "MethodsDetails", [])
    )

    num_inhalation_concentrations = 0

    for method in methods_details:
        if not isinstance(method, dict):
            continue

        details = safe_list(method.get("details"))

        # Oral/gavage concentration details
        for detail in details:
            if not isinstance(detail, dict):
                continue

            volume_obj = detail.get("volume_of_water_per_day")
            concentration_obj = detail.get("concentration")
            absolute_obj = detail.get("absolute_dose_per_day")
            relative_obj = detail.get("relative_dose_per_day")

            if isinstance(volume_obj, dict):
                researcherData["volumes"].append(
                    build_value_unit(volume_obj)
                )

            if isinstance(concentration_obj, dict):
                researcherData["concentrations"].append(
                    build_value_unit(concentration_obj)
                )

            if isinstance(absolute_obj, dict):
                researcherData["absoluteDoses"].append(
                    build_value_unit(absolute_obj)
                )

            if isinstance(relative_obj, dict):
                researcherData["relativeDoses"].append(
                    build_value_unit(relative_obj)
                )

        # Inhalation details
        if "percent_purity" in method:
            num_inhalation_concentrations += 1

            flow_rate = safe_dict(method.get("flow_rate"))
            duration = method.get("duration_per_frequency")

            # Do NOT split duration to manufacture a unit.
            # Preserve the model's original duration value.
            researcherData["inhalationConcentrations"].append(
                {
                    "percentPurity": name_field(
                        method.get("percent_purity")
                    ),
                    "flowRate": name_field(
                        flow_rate.get("value")
                    ),
                    "frequency": name_field(
                        method.get("frequency")
                    ),
                    "duration": name_field(duration),
                    "unitFlowRate": name_field(
                        flow_rate.get("unit")
                    ),
                    "unitDuration": name_field(
                        None
                    ),
                }
            )

    researcherData["numInhalationConcentrations"] = (
        num_inhalation_concentrations
    )

    # ------------------------------------------------------------------
    # DYNAMIC INHALATION FIELDS
    # ------------------------------------------------------------------

    for index, value in enumerate(
        researcherData["inhalationConcentrations"]
    ):
        researcherData[
            f"inhalationConcentration_{index}_percentPurity"
        ] = value["percentPurity"]

        researcherData[
            f"inhalationConcentration_{index}_flowRate"
        ] = value["flowRate"]

        researcherData[
            f"inhalationConcentration_{index}_frequency"
        ] = value["frequency"]

        researcherData[
            f"inhalationConcentration_{index}_duration"
        ] = value["duration"]

    # ------------------------------------------------------------------
    # DYNAMIC VOLUME / CONCENTRATION / DOSE FIELDS
    # ------------------------------------------------------------------

    for index, value in enumerate(researcherData["volumes"]):
        researcherData[
            f"volume_{index}_value"
        ] = value["value"]

        researcherData[
            f"volume_{index}_unit"
        ] = value["unit"]

    for index, value in enumerate(researcherData["concentrations"]):
        researcherData[
            f"concentration_{index}_value"
        ] = value["value"]

        researcherData[
            f"concentration_{index}_unit"
        ] = value["unit"]

    for index, value in enumerate(researcherData["absoluteDoses"]):
        researcherData[
            f"absoluteDoses_{index}_value"
        ] = value["value"]

        researcherData[
            f"absoluteDoses_{index}_unit"
        ] = value["unit"]

    for index, value in enumerate(researcherData["relativeDoses"]):
        researcherData[
            f"relativeDoses_{index}_value"
        ] = value["value"]

        researcherData[
            f"relativeDoses_{index}_unit"
        ] = value["unit"]

    # ------------------------------------------------------------------
    # BIOMARKERS
    # ------------------------------------------------------------------

    biomaker = first_value(input_json, "biomarkers", [])

    # ------------------------------------------------------------------
    # FINAL OUTPUT
    # ------------------------------------------------------------------

    parsed_data = {
        "publicData": publicData,
        "articleGeneralData": articleGeneralData,
        "researcherData": researcherData,
        "biomaker": biomaker,
    }

    # Add status only to actual frontend name objects.
    parsed_data = add_status(parsed_data)

    # Normalize missing scalar values.
    # Empty arrays remain empty arrays.
    parsed_data = replace_none_with_na(parsed_data)

    # PMID is backend-generated and must not be normalized to N/A.
    parsed_data["publicData"]["pmid"]["name"] = pmid_value

    return parsed_data

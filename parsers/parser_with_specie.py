import json


NA = "N/A"
UNVERIFIED = "Unverified"


def get_value(data, key, default=None):
    """
    Recursively find the first occurrence of `key`.

    Returns the associated value. If the key is not found, returns `default`.
    This helper is intentionally read-only and does not modify the input.
    """
    if isinstance(data, dict):
        if key in data:
            return data[key]

        for value in data.values():
            if isinstance(value, (dict, list)):
                result = get_value(value, key, default=None)
                if result is not None:
                    return result

    elif isinstance(data, list):
        for item in data:
            result = get_value(item, key, default=None)
            if result is not None:
                return result

    return default


def get_nested_value(data, parent_key, child_key, default=None):
    """
    Find the first object stored under `parent_key`, then read `child_key`
    from that object.
    """
    parent = get_value(data, parent_key)

    if isinstance(parent, dict):
        return parent.get(child_key, default)

    if isinstance(parent, list):
        for item in parent:
            if isinstance(item, dict) and child_key in item:
                return item[child_key]

    return default


def scalar(value):
    """
    Convert a missing scalar value to N/A.

    Preserve all explicitly extracted values exactly as received.
    """
    return NA if value is None or value == "" else value


def name_field(value):
    """
    Build the frontend scalar structure.
    """
    return {
        "name": scalar(value),
        "status": UNVERIFIED,
    }


def add_status(data):
    """
    Recursively add the standard status field to objects that represent
    extracted scalar/name objects.

    Existing status values are normalized to 'Unverified'.

    Important:
    - This function does not replace None with an empty string.
    - It does not alter lists.
    - It does not add a status field to the top-level containers unless
      they are actual extracted field objects.
    """
    if isinstance(data, dict):
        # If this is a frontend field object with a `name` key, normalize it.
        if "name" in data:
            data["name"] = scalar(data.get("name"))
            data["status"] = UNVERIFIED

        # Recursively process nested objects.
        for key, value in list(data.items()):
            if key != "status":
                data[key] = add_status(value)

        return data

    if isinstance(data, list):
        return [add_status(item) for item in data]

    return data


def replace_none_with_na(data, preserve_empty_lists=True):
    """
    Replace missing scalar values (None) with 'N/A'.

    Empty arrays remain [] because an absent array means there are no
    explicitly extracted items.

    Existing empty strings are also normalized to 'N/A' for scalar values.
    """
    if isinstance(data, dict):
        result = {}

        for key, value in data.items():
            if value is None:
                result[key] = NA
            elif isinstance(value, list):
                result[key] = [
                    replace_none_with_na(item, preserve_empty_lists)
                    for item in value
                ]
            elif isinstance(value, dict):
                result[key] = replace_none_with_na(
                    value, preserve_empty_lists
                )
            elif value == "":
                result[key] = NA
            else:
                result[key] = value

        return result

    if isinstance(data, list):
        if preserve_empty_lists and not data:
            return []

        return [
            replace_none_with_na(item, preserve_empty_lists)
            for item in data
        ]

    return NA if data is None or data == "" else data


def parse_species_details(species):
    """
    Convert step_2 `species` data into the frontend `specieDetails` shape.
    Only explicitly extracted values are mapped.
    """
    species_details = {}

    if not isinstance(species, list):
        return species_details

    for entry in species:
        if not isinstance(entry, dict):
            continue

        name = entry.get("specie_name")
        if name is None or name == "":
            # A species without a name cannot safely be used as a dynamic key.
            continue

        average_age = entry.get("average_age")
        if isinstance(average_age, dict):
            age_value = average_age.get("value")
            age_unit = average_age.get("unit")
        else:
            age_value = average_age
            age_unit = None

        average_weight = entry.get("average_weight")
        if isinstance(average_weight, dict):
            weight_value = average_weight.get("value")
            weight_unit = average_weight.get("unit")
        else:
            weight_value = average_weight
            weight_unit = None

        species_details[name] = {
            "name": name_field(name),
            "status": name_field(UNVERIFIED),
            "DescribeSpecies": name_field(entry.get("specie_description")),
            "subjects": name_field(
                str(entry["number_of_subjects"])
                if entry.get("number_of_subjects") is not None
                else None
            ),
            "health": name_field(entry.get("health_status")),
            "gender": name_field(entry.get("gender")),
            "averageAge": name_field(
                str(age_value) if age_value is not None else None
            ),
            "ageUnit": name_field(age_unit),
            "averageWeight": name_field(
                str(weight_value) if weight_value is not None else None
            ),
            "weightUnit": name_field(weight_unit),
        }

    return species_details


def parse_species_data(species_data):
    """
    Convert step_3 `speciesData` list into the frontend dynamic dictionary.

    Preserve the complete speciesData object instead of creating a partial
    temporary object that is never used.
    """
    result = {}

    if not isinstance(species_data, list):
        return result

    for species in species_data:
        if not isinstance(species, dict):
            continue

        species_name = species.get("specieName")

        if species_name is None or species_name == "":
            continue

        # Copy the object so the input Pydantic JSON is not modified.
        species_obj = dict(species)

        species_obj.pop("specieName", None)

        # Frontend uses isOpen for the species accordion.
        species_obj["isOpen"] = True

        # Convert HowManyConcentrations into the frontend field format.
        concentration_count = species_obj.get("HowManyConcentrations")
        species_obj["HowManyConcentrations"] = name_field(
            concentration_count
        )

        result[species_name] = species_obj

    return result


def parse_to_with_specie_json(input_json):
    """
    Transform the Pydantic extraction result into the application's
    with-species frontend JSON format.

    Extraction policy:
    - Explicit paper information only.
    - Missing scalar values become N/A.
    - Missing arrays become [].
    - PMID is treated as a backend-managed scalar.
    - No value is inferred, calculated, or generated here.
    """

    if not isinstance(input_json, dict):
        raise ValueError("input_json must be a dictionary")

    pmid_value = get_value(input_json, "pmid")

    # ------------------------------------------------------------------
    # STEP 1 / PUBLIC DATA
    # ------------------------------------------------------------------

    authors = get_value(input_json, "authors")
    if not isinstance(authors, list):
        authors = []

    country = get_value(input_json, "country")
    research_country = get_value(input_json, "researchCountry")

    publicData = {
        "title": name_field(get_value(input_json, "title")),

        # IMPORTANT:
        # Do NOT use [0] here. PMID is a scalar string and may be supplied
        # by backend enrichment after the LLM extraction.
        "pmid": {"name": get_value(input_json, "pmid")},

        "doi": name_field(get_value(input_json, "doi")),
        "authors": authors,
        "abstract": name_field(get_value(input_json, "abstract")),
        "year": name_field(get_value(input_json, "year")),
        "journal": name_field(get_value(input_json, "journal")),
        "publisher": name_field(get_value(input_json, "publisher")),
        "impactFactor": name_field(get_value(input_json, "impactFactor")),
        "HIndex": name_field(get_value(input_json, "HIndex")),
        "sciMAGO": name_field(get_value(input_json, "sciMAGO")),
        "volume": name_field(get_value(input_json, "volume")),
        "issue": name_field(get_value(input_json, "issue")),
        "pages": name_field(get_value(input_json, "pages")),
        "country": [name_field(country)],
        "grantCountry": name_field(get_value(input_json, "grantCountry")),
        "researchCountry": [name_field(research_country)],
        "keywords": name_field(get_value(input_json, "keywords")),
    }

    # ------------------------------------------------------------------
    # STEP 2 / ARTICLE GENERAL DATA
    # ------------------------------------------------------------------

    outcome = get_value(input_json, "outcome")
    if not isinstance(outcome, dict):
        outcome = {}

    highlight = get_value(input_json, "HighlightArticle")
    if not isinstance(highlight, dict):
        highlight = {}

    duration_in_vivo = get_value(input_json, "durationOfStudyInVivo")
    if not isinstance(duration_in_vivo, dict):
        duration_in_vivo = {}

    duration_in_vitro = get_value(input_json, "durationOfStudyinVitro")
    if not isinstance(duration_in_vitro, dict):
        duration_in_vitro = {}

    duration_ex_vivo = get_value(input_json, "durationOfStudyExVivo")
    if not isinstance(duration_ex_vivo, dict):
        duration_ex_vivo = {}

    clinical_trial_details = get_value(
        input_json, "clinical_trial_design_details"
    )
    if not isinstance(clinical_trial_details, dict):
        clinical_trial_details = {}

    study_type = get_value(input_json, "studyType")
    if not isinstance(study_type, list):
        study_type = []

    non_experimental_type = get_value(
        input_json, "non_experimental_type"
    )
    if not isinstance(non_experimental_type, list):
        non_experimental_type = []

    timing_in_vivo = get_value(input_json, "timingTreatmentInVivo")
    if not isinstance(timing_in_vivo, list):
        timing_in_vivo = []

    timing_in_vitro = get_value(input_json, "timingTreatmentInVitro")
    if not isinstance(timing_in_vitro, list):
        timing_in_vitro = []

    timing_ex_vivo = get_value(input_json, "timingTreatmentInExVivo")
    if not isinstance(timing_ex_vivo, list):
        timing_ex_vivo = []

    selected_study_types = get_value(
        input_json, "clinical_trial_design"
    )
    if not isinstance(selected_study_types, list):
        selected_study_types = []

    in_vivo_study_types = []

    study_details = get_value(input_json, "studyTypeDetails")
    if isinstance(study_details, list):
        for item in study_details:
            if not isinstance(item, dict):
                continue

            category = str(item.get("study_category", "")).lower()

            if "invivo" in category or "in-vivo" in category:
                values = item.get("studyTypeInVivo") or []

                if isinstance(values, list):
                    for value in values:
                        in_vivo_study_types.append(name_field(value))

    species = get_value(input_json, "species")
    if not isinstance(species, list):
        species = []

    articleGeneralData = {
        "outcome": name_field(outcome.get("text")),
        "outcomeType": (
            [outcome.get("outcomeType")]
            if outcome.get("outcomeType") is not None
            else []
        ),
        "rankThisArticle": name_field(outcome.get("rank")),
        "HighlightArticle": name_field(
            highlight.get("HighlightArticle")
        ),
        "descHighArt": name_field(highlight.get("description")),

        "studyType": [
            name_field(study)
            for study in study_type
        ],

        # Non-experimental
        "NonExperimentalSelect": [
            name_field(select)
            for select in non_experimental_type
        ],
        "ReviewStudyType": name_field(
            get_value(input_json, "reviewStudyType")
        ),
        "OpinionPiece": name_field(
            get_value(input_json, "OpinionPiece")
        ),
        "Hypothesis": name_field(
            get_value(input_json, "hypothesis")
        ),
        "TherapeuticDeliverySystems": name_field(
            get_value(
                input_json,
                "TherapeuticDeliverySystemsdetails"
            )
        ),

        # In vivo
        "inVivo": in_vivo_study_types,
        "selectedStudyTypes": selected_study_types,
        "clinicalTrialDesign": (
            clinical_trial_details.get("clinicalTrialDesign")
            or []
        ),
        "observationalStudyObj": (
            clinical_trial_details.get("observationalStudy")
            or []
        ),
        "durationOfStudy": name_field(
            duration_in_vivo.get("value")
        ),
        "studyDurationUnit": scalar(
            duration_in_vivo.get("unit")
        ),
        "timingTreatmentInVivo": [
            name_field(timing)
            for timing in timing_in_vivo
        ],

        # In vitro
        "durationOfStudyinVitro": name_field(
            duration_in_vitro.get("value")
        ),
        "UnitOfStudyInVitro": name_field(
            duration_in_vitro.get("unit")
        ),
        "timingTreatmentInVitro": [
            name_field(timing)
            for timing in timing_in_vitro
        ],

        # Ex vivo
        "WhatCellTissueUsed": name_field(
            get_value(input_json, "WhatCellTissueUsed")
        ),
        "durationOfStudyExVivo": name_field(
            duration_ex_vivo.get("value")
        ),
        "UnitOfStudyExVivo": name_field(
            duration_ex_vivo.get("unit")
        ),
        "timingTreatmentExVivo": [
            name_field(timing)
            for timing in timing_ex_vivo
        ],

        # Other
        "Other": name_field(
            get_nested_value(
                input_json,
                "studyTypeDetails",
                "description"
            )
        ),

        "species": [
            name_field(specie.get("specie_name"))
            for specie in species
            if isinstance(specie, dict)
            and specie.get("specie_name") is not None
        ],

        "specieDetails": parse_species_details(species),

        "researchtopic": get_value(
            input_json, "researchtopic"
        ),

        "diseaseModel": name_field(
            get_value(input_json, "diseaseModel")
        ),

        "system": get_value(input_json, "system"),
        "organ": get_value(input_json, "organ"),
    }

    # ------------------------------------------------------------------
    # STEP 3 / RESEARCHER DATA
    # ------------------------------------------------------------------

    species_data = get_value(input_json, "speciesData")
    if not isinstance(species_data, list):
        species_data = []

    researcherData = {
        "speciesData": parse_species_data(species_data),

        "CompMethodAdmin": name_field(
            get_value(
                input_json,
                "comparison_of_methods_flag"
            )
        ),
        "CompMethodAdminDesc": name_field(
            get_value(
                input_json,
                "comparison_of_methods_description"
            )
        ),
        "doseComparison": name_field(
            get_value(
                input_json,
                "dose_concentration_comparison_flag"
            )
        ),
        "doseComparisonDesc": name_field(
            get_value(
                input_json,
                "dose_concentration_comparison_description"
            )
        ),
        "drugComparison": name_field(
            get_value(
                input_json,
                "drug_therapy_supplement_comparison_flag"
            )
        ),
        "comparisonDetail": name_field(
            get_value(
                input_json,
                "drug_therapy_supplement_comparison"
            )
        ),
        "pharmacokinetics": name_field(
            get_value(
                input_json,
                "pharmacokinetics_flag"
            )
        ),
        "pharmacokineticsDescription": name_field(
            get_value(
                input_json,
                "pharmacokinetics"
            )
        ),
        "isERW": name_field(
            get_value(input_json, "erw")
        ),
        "ph": name_field(
            get_value(input_json, "pH")
        ),
        "erwCompared": name_field(
            get_value(input_json, "comparison")
        ),
        "adverseEffects": name_field(
            get_value(
                input_json,
                "adverse_effects_flag"
            )
        ),
        "adverseEffectsDescription": name_field(
            get_value(
                input_json,
                "adverse_effects_description"
            )
        ),
        "doseDependentEffect": name_field(
            get_value(
                input_json,
                "dose_dependent_effect"
            )
        ),
        "safetyProfile": name_field(
            get_value(
                input_json,
                "unique_safety_profile"
            )
        ),
        "safetyofhydrogen": name_field(
            get_value(
                input_json,
                "safety_study"
            )
        ),
        "sexDifference": name_field(
            get_value(
                input_json,
                "sex_difference"
            )
        ),
        "responderDifference": name_field(
            get_value(
                input_json,
                "responder_vs_non_responder"
            )
        ),
        "pregnantBreastfeeding": name_field(
            get_value(
                input_json,
                "pregnantBreastfeeding"
            )
        ),
        "mechanisticInsights": name_field(
            get_value(
                input_json,
                "mechanistic_insights"
            )
        ),
        "Video_WebpageLink": name_field(
            get_value(
                input_json,
                "Video_WebpageLink"
            )
        ),
        "PasteUrl": name_field(
            get_value(input_json, "PasteUrl")
        ),
        "commercialProduct": name_field(
            get_value(
                input_json,
                "commercialProduct"
            )
        ),
        "brandName": name_field(
            get_value(input_json, "brandName")
        ),
        "geneExpression": name_field(
            get_value(
                input_json,
                "geneExpression"
            )
        ),
        "geneExpressionDesc": name_field(
            get_value(
                input_json,
                "geneExpressionDesc"
            )
        ),
    }

    # ------------------------------------------------------------------
    # STEP 4 / BIOMARKERS
    # ------------------------------------------------------------------

    biomarker = get_value(input_json, "biomarkers")
    if not isinstance(biomarker, list):
        biomarker = []

    # ------------------------------------------------------------------
    # FINAL STRUCTURE
    # ------------------------------------------------------------------

    parsed_data = {
        "publicData": publicData,
        "articleGeneralData": articleGeneralData,
        "researcherData": researcherData,
        "biomaker": biomarker,
    }

    # Normalize scalar missing values while keeping arrays as [].
    parsed_data = replace_none_with_na(parsed_data)

    # Ensure all generated frontend field objects have the same status.
    parsed_data = add_status(parsed_data)

    # The frontend expects no container-level status inside these dynamic
    # dictionaries.
    species_data_output = parsed_data["researcherData"]["speciesData"]

    if isinstance(species_data_output, dict):
        species_data_output.pop("status", None)

        for species_name, species_obj in species_data_output.items():
            if isinstance(species_obj, dict):
                species_obj.pop("status", None)

    specie_details_output = parsed_data["articleGeneralData"]["specieDetails"]

    if isinstance(specie_details_output, dict):
        specie_details_output.pop("status", None)

    # PMID is backend-generated and must not be normalized to N/A.
    parsed_data["publicData"]["pmid"]["name"] = pmid_value

    return parsed_data

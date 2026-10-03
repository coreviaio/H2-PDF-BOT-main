from openai import OpenAI
import json
from pydantic_configuration.pydantic_model import ArticleExtractedDataWithSpecie
from pydantic_configuration.pydantic_model import ArticleExtractedDataWithoutSpecie
import helper_backend.scrapper_functions as scrapper_functions
import helper_backend.config as config
import helper_backend.input_pdf as input_pdf
from loguru import logger

client = OpenAI(api_key=config.openai_api_key)





from steps.pydantic_step1_model import isArticleWithSpecie

def is_article_with_specie(pdf_text):
    logger.info("Checking if article contains specie...")

    try:
        # Log the length of the input to avoid logging full text
        logger.debug(f"Received article text of length: {len(pdf_text)} characters")

        response = client.beta.chat.completions.parse(
            model=config.model_name,
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Classify the paper strictly from the provided text. "
                                "Return True only when the paper explicitly describes research involving "
                                "one or more biological species, organisms, animals, plants, cells, or tissues "
                                "as an experimental subject or study organism. "
                                "Return False when no such species or organism is explicitly involved, including "
                                "papers that only discuss a substance, chemical, computational model, review, "
                                "or general biological concept. "
                                "Do not infer a species from context, title, abbreviations, or domain knowledge."
                            )
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": pdf_text
                        }
                    ]
                }
            ],
            response_format=isArticleWithSpecie,
            temperature=0.3,
            max_completion_tokens=10000,
            top_p=0.3,
            frequency_penalty=0,
            presence_penalty=0
        )

        logger.debug("Received response from model")

        if not response.choices or response.choices[0].message.parsed is None:
            raise ValueError("Model returned no parsed classification result.")

        event = response.choices[0].message.parsed
        event_json = json.loads(event.model_dump_json())
        logger.info(f"Determined article classification: {'with specie' if event_json['specie'] else 'without specie'}")

        return event_json['specie']

    except Exception as e:
        logger.exception("Error occurred while checking if article has specie")
        return False  # Fallback behavior



def extract_data_from_pdf(pdf_path):
    logger.info(f"Starting extraction for file: {pdf_path}")

    pdf_text = None
    try:
        logger.debug("Attempting to extract text from PDF...")
        pdf_text = input_pdf.extract_text_from_pdf(pdf_path)
        if pdf_text is None:
            raise ValueError("PDF text extraction returned None.")
        pdf_text = str(pdf_text).strip()
        logger.debug(f"Extracted PDF text length: {len(pdf_text)} characters")
    except Exception as e:
        logger.exception(f"Failed to extract text from PDF: {e}")
        return None, False

    if not pdf_text:
        logger.warning("PDF text is empty after extraction.")
        return None, False

    try:
        logger.info("Determining if article contains specie...")
        specie = is_article_with_specie(pdf_text)
        logger.info(f"Article classified as: {'with specie' if specie else 'without specie'}")
    except Exception as e:
        logger.exception("Error while determining specie status")
        return None, False

    pydantic_model = ArticleExtractedDataWithSpecie if specie else ArticleExtractedDataWithoutSpecie

    try:
        logger.info("Sending content to LLM for structured data extraction...")
        response = client.beta.chat.completions.parse(
            model=config.model_name,
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": """
                            You are a strict scientific research-paper information extraction engine.

                            You will receive the complete text of a scientific research paper extracted from a PDF.

                            Extract information only from the provided paper text.

                            IMPORTANT RULES:

                            1. Return only one valid JSON object.
                            2. Do not return markdown, explanations, comments, headings, or extra text.
                            3. Do not invent, guess, infer, calculate, or hallucinate any information.
                            4. If a scalar value is explicitly found in the paper, extract it exactly.
                            5. If a scalar value is not explicitly found in the paper, use "N/A", EXCEPT for the "pmid" field.
                            6. Never use an empty string, null, false, 0, or an invented value for missing scalar data.
                            7. If an array has no explicitly available items, return [].
                            8. Do not create fake array items.
                            9. Do not add fields that are not present in the schema.
                            10. Do not remove fields from the schema.
                            11. Preserve every field name, capitalization, nesting, and data type exactly.
                            12. Use "Unverified" as the status for every extracted field.
                            13. Do not copy the placeholder values from the schema. The schema is only a structure.
                            14. Replace every placeholder with the actual extracted value or "N/A", except for the "pmid" field.
                            15. The "pmid" field is managed exclusively by the backend and is not an extraction field.

                            ABSTRACT RULE:

                            16. Copy the abstract exactly as it appears in the paper.
                            17. Do not summarize, rewrite, translate, correct, shorten, or rephrase the abstract.
                            18. If no abstract is present, use:

                            {
                            "name": "N/A",
                            "status": "Unverified"
                            }

                            EXTRACTION RULES:

                            19. Extract only information explicitly stated in the paper.
                            20. Information from the title, abstract, introduction, discussion, and conclusion must not be used as experimental-method data unless the paper clearly states that it describes the actual study.
                            21. Preserve original spelling, capitalization, numbers, units, and terminology.
                            22. Preserve numbers and units together whenever they are reported together.
                            23. For boolean-like fields, use "Yes" or "No" only when explicitly stated.
                            24. If a boolean-like field is not reported, use "N/A".
                            25. For biomarker data, include only biomarkers explicitly reported in the paper.
                            26. If no biomarker is explicitly reported, return [].
                            27. Create speciesDetails and speciesData entries only for species explicitly mentioned in the paper.
                            28. Use "speciesDetails" exactly. Never use "specieDetails".
                            29. Use only these study type values when applicable:

                                * "in Vivo"
                                * "In Vitro"
                                * "Ex Vivo"
                                * "Non-experimental"
                                * "Other"
                                * "Chemical/Physicochemical Study"
                                * "In Silico"

                            PMID RULE:

                            30. The "pmid" field must not be extracted from the paper text.
                            31. The model must not generate, guess, infer, calculate, or fabricate a PMID.
                            32. The model must not use "N/A" as the value of the "pmid" field.
                            33. The "pmid" value will be generated and assigned automatically by the backend after extraction.
                            34. The backend is the only source responsible for assigning the actual PMID value.
                            35. Do not modify, replace, or invent the backend-generated PMID.
                            36. If the schema contains a "pmid" field, preserve the field exactly as defined by the schema, but do not generate its value from the paper.

                            SCALAR FIELD FORMAT:

                            Every scalar field must use this structure:

                            {
                            "name": "Extracted value or N/A",
                            "status": "Unverified"
                            }

                            The "pmid" field is an exception to this rule because it is managed by the backend.

                            ARRAY RULE:

                            For arrays, return only explicitly extracted items.

                            Example:

                            "authors": [
                            {
                            "name": "Actual Author Name",
                            "parent_id": "N/A",
                            "status": "Unverified",
                            "affiliation": "Actual affiliation or N/A"
                            }
                            ]

                            If no authors are available:

                            "authors": []

                            DYNAMIC SPECIES RULE:

                            For every species explicitly mentioned in the paper, create a matching key under both:

                            * articleGeneralData.speciesDetails
                            * researcherData.speciesData

                            Do not create species keys for species that are not explicitly mentioned.

                            If a species is mentioned but a particular value is unavailable, use "N/A" for that value.

                            BIOMARKER ITEM FORMAT:

                            Each biomarker item must follow this structure:

                            {
                            "marker": "Extracted marker or N/A",
                            "category": [],
                            "Change": [],
                            "Protein": "Extracted protein information or N/A",
                            "status": "Unverified"
                            }

                            OUTPUT SCHEMA:

                            The Pydantic response_format supplied by the backend is the ONLY source of truth
                            for the output schema.

                            Do not invent a separate top-level schema such as publicData/articleGeneralData/
                            researcherData/biomaker unless those fields are actually part of the supplied
                            Pydantic model. Follow the exact Pydantic model fields, nesting, capitalization,
                            and data types.

                            Do not copy placeholder/example values from the Pydantic model. Replace them with
                            explicitly extracted values or "N/A" according to the rules above.

                            FINAL VALIDATION:

                            Before returning the response, verify all of the following:

                            * The response is valid JSON.
                            * The response can be parsed by Python json.loads().
                            * There is no markdown or extra text.
                            * All schema fields are present.
                            * No unknown fields were added.
                            * No schema fields were removed.
                            * Every missing scalar value is exactly "N/A", except "pmid".
                            * The "pmid" value must never be extracted, generated, inferred, guessed, calculated, or fabricated by the model.
                            * The "pmid" value is managed exclusively by the backend.
                            * The abstract is copied exactly.
                            * No values were invented.
                            * The output matches the supplied Pydantic response schema exactly.
                            * Do not add or remove fields based on the examples in this prompt.

                            Return only the JSON object.


                            """
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": pdf_text
                        }
                    ]
                }
            ],
            response_format=pydantic_model,
            temperature=0.3,
            max_completion_tokens=10000,
            top_p=0.3,
            frequency_penalty=0,
            presence_penalty=0
        )

        logger.debug("LLM responded with structured data.")

        if not response.choices or response.choices[0].message.parsed is None:
            raise ValueError("Model returned no parsed extraction result.")

        event = response.choices[0].message.parsed
        event_json = json.loads(event.model_dump_json())
    except Exception as e:
        logger.exception("Error while extracting structured data from PDF text.")
        return None, specie

    try:
        # Backend-managed enrichment.
        # The LLM must never provide a PMID. Treat missing/placeholder PMID values
        # as empty so the backend can resolve it from PubMed using the article title.
        step_1 = event_json.get("step_1") or {}
        title = step_1.get("title")
        doi = step_1.get("doi")

        # Never trust a PMID returned by the model. PMID is backend-managed.
        # Clear any model-supplied value before attempting PubMed resolution.
        # PMID is generated by the backend, so it is not an extracted N/A value.
        step_1["pmid"] = None

        if title and title != "N/A":
            logger.debug("Fetching PMID from PubMed...")
            resolved_pmid = scrapper_functions.get_pubmed_article_id(title, doi)
            if resolved_pmid:
                step_1["pmid"] = resolved_pmid[0]

        journal = step_1.get("journal")
        if journal and journal != "N/A":
            logger.debug(f"Fetching journal metrics for: {journal}")
            metrics = scrapper_functions.fetch_scimago_search(journal)
            if metrics and len(metrics) == 3:
                step_1["sciMAGO"], step_1["impactFactor"], step_1["HIndex"] = metrics
    except Exception as e:
        logger.warning(f"Optional enrichment failed: {e}")

    logger.info("Extraction and enrichment completed successfully.")
    return event_json, specie

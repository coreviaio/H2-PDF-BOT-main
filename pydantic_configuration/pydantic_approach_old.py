from openai import OpenAI
import json
from pydantic_configuration.pydantic_model import ArticleExtractedDataWithSpecie
from pydantic_configuration.pydantic_model import ArticleExtractedDataWithoutSpecie
import helper_backend.scrapper_functions as scrapper_functions
import helper_backend.config as config
import helper_backend.input_pdf as input_pdf
import  helper_backend.helper_functions as helper_function
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
                            "text": "Analyze the article and return True if it's with specie and False if it's without specie."
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

        event = response.choices[0].message.parsed

        event_json = json.loads(event.model_dump_json())
        logger.info(f"Determined article classification: {'with specie' if event_json['specie'] else 'without specie'}")

        return event_json['specie']

    except Exception as e:
        logger.exception("Error occurred while checking if article has specie")
        return False  # Fallback behavior



# def extract_data_from_pdf(pdf_path):
  
  
#   pdf_text = None
#   try:
#       # # Extract pdf content
#       pdf_text = input_pdf.extract_text_from_pdf(pdf_path)
#   except Exception as e:
#       print(f"Error: {e}")
  
#   # specie = False
#   print("len of pdf text: ",len(pdf_text))
#   specie = is_article_with_specie(pdf_text)
#   print("artcile specie status: ",specie)
  
#   if specie:
#     pydantic_model = ArticleExtractedDataWithSpecie
#   else:
#     pydantic_model = ArticleExtractedDataWithoutSpecie
  
  
  
      
#   response = client.beta.chat.completions.parse(
#     model= config.model_name,
#     messages=[
#       {
#         "role": "system",
#         "content": [
#           # {
#           #   "type": "text",
#           #   "text": "User will provide you a content from a research paper first, You will extract the information as per schema from the research paper content. note that the abstract must be extracted as it is, without any changes. As per our schema logic, If a specific details that we need is not mentioned in the content directly then you must generate them yourself as per your understanding of the content so far. "
#           # }
#           {
#             "type": "text",
#             "text": """
#             You will be given content from a research paper. Your job is to extract information based on a specific schema.

# - The **abstract** must be copied exactly as it is — no changes, no rephrasing.
# - For all other fields in the schema:
#   - If the information is clearly mentioned in the content, extract it exactly as written.
#   - If a detail is not directly mentioned, you MUST generate it yourself based on your understanding of the content.

# Every field in the schema must be filled. Don’t leave anything blank. Either extract it from the content directly or indirectly or generate it intelligently if it’s missing.
#             """
#           }
#         ]
#       },
#       {
#         "role": "user",
#         "content": [
#           {
#             "type": "text",
#             "text": pdf_text
            
#           }
#         ]
#       }
#     ],
#     response_format=pydantic_model,
#     temperature=0.3,
#     max_completion_tokens=10000,
#     top_p=0.3,
#     frequency_penalty=0,
#     presence_penalty=0
#   )

#   event = response.choices[0].message.parsed

#   event_json = json.loads(event.model_dump_json())  # Convert string back to dictionary


#   # for Scrapping
#   if event_json['step_1']['title'] and not event_json['step_1']['pmid']:
#       event_json["step_1"]['pmid'] = scrapper_functions.get_pubmed_article_id(event_json["step_1"]['title'])

#   if event_json['step_1']['journal']:
#           event_json['step_1']["sciMAGO"] , event_json['step_1']["impactFactor"] , event_json['step_1']["HIndex"] = scrapper_functions.fetch_scimago_search(event_json['step_1']['journal'])

#   # event_json = helper_function.replace_null_with_default(event_json)
#   # event_json

#   # # uncomment for writing json to file.


#   return event_json,specie

def extract_data_from_pdf(pdf_path):
    logger.info(f"Starting extraction for file: {pdf_path}")

    pdf_text = None
    try:
        logger.debug("Attempting to extract text from PDF...")
        pdf_text = input_pdf.extract_text_from_pdf(pdf_path)
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
                            You will be given content from a research paper. Your job is to extract information based on a specific schema.

                            - The **abstract** must be copied exactly as it is — no changes, no rephrasing.
                            - For all other fields in the schema:
                            - If the information is clearly mentioned in the content, extract it exactly as written.
                            - If a detail is not directly mentioned, you MUST generate it yourself based on your understanding of the content.

                            Every field in the schema must be filled. Don’t leave anything blank. Either extract it from the content directly or indirectly or generate it intelligently if it’s missing.
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
        event = response.choices[0].message.parsed
        event_json = json.loads(event.model_dump_json())
    except Exception as e:
        logger.exception("Error while extracting structured data from PDF text.")
        return None, specie

    try:
        # Scraper Enhancements
        if event_json['step_1']['title'] and not event_json['step_1']['pmid']:
            logger.debug("Fetching PMID from PubMed...")
            event_json["step_1"]['pmid'] = scrapper_functions.get_pubmed_article_id(event_json["step_1"]['title'])

        if event_json['step_1']['journal']:
            logger.debug(f"Fetching journal metrics for: {event_json['step_1']['journal']}")
            event_json['step_1']["sciMAGO"], event_json['step_1']["impactFactor"], event_json['step_1']["HIndex"] = scrapper_functions.fetch_scimago_search(event_json['step_1']['journal'])
    except Exception as e:
        logger.warning(f"Optional enrichment failed: {e}")

    logger.info("Extraction and enrichment completed successfully.")
    return event_json, specie

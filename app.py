from flask import Flask, request, jsonify
import os
import pydantic_configuration.pydantic_approach as pydantic_approach
from loguru import logger
import json
from parsers.parser_without_specie import parse_to_without_specie_json
from parsers.parser_with_specie import parse_to_with_specie_json
import fitz  # PyMuPDF
# from pydantic_configuration.pydantic_approach import is_article_with_specie
import uuid

app = Flask(__name__)


# logger.add("app.log", rotation="100 KB")
os.makedirs("logs", exist_ok=True)
os.makedirs("Outputs", exist_ok=True)

logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    level="INFO"
)

@app.before_request
def log_request_info():
    logger.info(f"Incoming request: {request.method} {request.url}")

def is_text_based(pdf_path):
    with fitz.open(pdf_path) as doc:
        for page in doc:
            if page.get_text().strip():
                return True
    return False

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     logger.info("App started")

#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400

#     file = request.files['file']

#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     if not file.filename.endswith('.pdf'):
#         return jsonify({'error': 'Only PDF files are allowed'}), 400

#     # Save in the same directory as the script
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     temp_path = os.path.join(current_dir, file.filename)

#     # try:
#         # Save the uploaded file
#     file.save(temp_path)

#     # Process the file
#     result,specie = pydantic_approach.extract_data_from_pdf(temp_path)
    
#     with open(f"final_output_original_{specie}.json", "w", encoding="utf-8") as json_file:
#         json.dump(result, json_file, ensure_ascii=False, indent=4)
    
#     ###PARSING CODE
#     if specie:
#         result = parse_to_with_specie_json(result)
#     if not specie:
#         result = parse_to_without_specie_json(result)

    
#     with open(f"final_output_parsed_{specie}.json", "w", encoding="utf-8") as json_file:
#         json.dump(result, json_file, ensure_ascii=False, indent=4)
        
#     return jsonify({"success": True, "message": "File processed successfully", "data": result})

#     # except Exception as e:
#     #     return jsonify({"success": False, "message": f"Failed to process file: {str(e)}"}), 500

#     # finally:
#     #     try:
#     #         if os.path.exists(temp_path):
#     #             os.remove(temp_path)  # Delete file after processing
#     #     except PermissionError:
#     #         print(f"Warning: Could not delete {temp_path}, file might be in use.")

# from loguru import logger  # or use the built-in logging if you prefer

@app.route('/upload', methods=['POST'])
def upload_file():
    logger.info("Received /upload request")

    if 'file' not in request.files:
        logger.warning("No file part in request")
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        logger.warning("No file selected")
        return jsonify({'error': 'No selected file'}), 400

    # if not file.filename.endswith('.pdf'):
    if not file.filename.lower().endswith(".pdf"):
        logger.warning(f"Rejected non-PDF file: {file.filename}")
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    current_dir = os.path.dirname(os.path.abspath(__file__))
    # temp_path = os.path.join(current_dir, file.filename)
    filename = f"{uuid.uuid4()}.pdf"
    temp_path = os.path.join(current_dir, filename)

    try:
        logger.info(f"Saving file to: {temp_path}")
        file.save(temp_path)
        if is_text_based(temp_path):
            # logger.info(f"Saving file to: {temp_path}")
            # file.save(temp_path)

            logger.info("Starting PDF data extraction...")
            result, specie = pydantic_approach.extract_data_from_pdf(temp_path)
            logger.info(f"Extraction complete. Specie detected: {specie}")

            # original_json_path = f"final_output_original_{specie}.json"
            request_id = uuid.uuid4().hex

            original_json_path = os.path.join(
                "Outputs",
                f"{request_id}_original_{specie}.json"
            )

            with open(original_json_path, "w", encoding="utf-8") as json_file:
                json.dump(result, json_file, ensure_ascii=False, indent=4)
            logger.info(f"Original data saved to {original_json_path}")

            if specie:
                logger.info("Parsing with specie parser...")
                result = parse_to_with_specie_json(result)
            else:
                logger.info("Parsing with non-specie parser...")
                result = parse_to_without_specie_json(result)

            # parsed_json_path = f"final_output_parsed_{specie}.json"
            parsed_json_path = os.path.join(
                "Outputs",
                f"{request_id}_parsed_{specie}.json"
            )

            with open(parsed_json_path, "w", encoding="utf-8") as json_file:
                json.dump(result, json_file, ensure_ascii=False, indent=4)
            logger.info(f"Parsed data saved to {parsed_json_path}")

            return jsonify({"success": True, "message": "File processed successfully", "data": result})
        else:
            logger.error(f"Failed to process file Contains images")
            # return jsonify({"success": False, "message": "File Containes Images."}), 500
            return jsonify({
                "success": False,
                "message": "Image-based PDF is not supported."
            }), 400

    except Exception as e:
        logger.error(f"Failed to process file: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to process file: {str(e)}"}), 500

    finally:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info(f"Deleted temporary file: {temp_path}")
        except PermissionError:
            logger.warning(f"Could not delete temporary file (in use): {temp_path}")


if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(host="0.0.0.0", port=5000)

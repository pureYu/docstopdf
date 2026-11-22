import argparse
import logging
import json
import os
import time
import cProfile
from libs.config import *
from libs.DocumentParserFactory import DocumentParserFactory
from libs.PdfGenerator import PdfGenerator


# default_input_file_path = "../data/sample_word_extended.docx"
default_input_file_path = "../data/dt-var-mu_21312-outcome-ir-0488-2023-07-24.docx"
# default_input_file_path = "../data/dt-var-mu_21312-outcome-ir-0488-2023-07-24.pdf"

def main(input_file):
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        start_time_app = time.time()
        logger.info(f"***** Application started. Input file: {input_file}")
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        output_file_basename = f"{os.path.splitext(os.path.basename(input_file))[0]}"
        output_file_path = os.path.dirname(input_file)

        parser = DocumentParserFactory.get_parser(input_file)
        parsed_data = parser.parse()

        print(json.dumps(parsed_data, indent=4))
        with open(f"{output_file_path}/{output_file_basename}.json", "w") as json_file:
        # with open(f"{output_file_path}/from-pdf-{output_file_basename}.json", "w") as json_file:
        # with open(f"{output_file_path}/from-pdf-camelot-{output_file_basename}.json", "w") as json_file:
            json.dump(parsed_data, json_file, indent=4)
        # exit(1)

        document_id = parser.save_parse_results(parsed_data)
        end_time_doc_parse = time.time()
        logger.info(f"***** Document parsing took {end_time_doc_parse - start_time_app} seconds.")
        if parser.__class__.__name__ != "PdfDocumentParser":
            # document_id = "65b00e77d3c8b3974b595808"
            pdf_generator = PdfGenerator(document_id)
            pdf_generator.generate_pdf(f"{output_file_path}/{output_file_basename}.pdf")
            end_time_pdf_gen = time.time()
            logger.info(f"***** PDF generation took {end_time_pdf_gen - end_time_doc_parse} seconds.")
            logger.info(f"***** Total time {end_time_pdf_gen - start_time_app} seconds.")

    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

def setup_logging():
    logging_level = getattr(logging, LOGGING_LEVEL, None)
    if not isinstance(logging_level, int):
        raise ValueError(f"Invalid log level: {LOGGING_LEVEL}")
    logging.basicConfig(level=logging_level,
                        format="%(asctime)s - %(levelname)s - %(message)s")
                        # format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s")


if __name__ == "__main__":
    # os.environ["PATH"] += os.pathsep + r'C:\Program Files\gs\gs10.02.1\bin'
    parser = argparse.ArgumentParser(description="Process a Word document and generate a PDF")
    parser.add_argument("input_file", nargs="?", default=default_input_file_path,
                        help=f"Path to the input Word document. Default is {default_input_file_path}")
    args = parser.parse_args()
    if not args.input_file:
        print("Error: No input file provided. Please specify the path to the input Word document.")
        parser.print_help()
        exit(1)

    main(args.input_file)
    # cProfile.run("main(args.input_file)")
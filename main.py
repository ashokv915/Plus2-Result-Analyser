import sys
import pdftojson
import analysis
import configparser
import watermarking
import os
import logging
from logging.handlers import RotatingFileHandler

config = configparser.ConfigParser()


def main(argv):

    LOG_FILE = "./logs/main.log"
    logging.basicConfig(
    filename=LOG_FILE,
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.DEBUG,
    )
    handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)


    pdf=0
    file_format = argv[1].split(".")
    print("File format is "+file_format[2])
    logging.debug("File format is "+file_format[2])
    RESULT_FOLDER = argv[4]
    logging.debug("Result folder "+RESULT_FOLDER)
    RESULT_FILE_NAME = argv[5]
    logging.debug("Result File Name "+RESULT_FILE_NAME)
    RESULT_FILE_PATH = os.path.join(RESULT_FOLDER,RESULT_FILE_NAME)
    logging.debug("Result File Path "+RESULT_FILE_PATH)
    WATER_MARK_FILE = "_"+RESULT_FILE_NAME
    if(file_format[2]=="pdf"):
        pdf=1
        print("Format is PDF")
        school_code = pdftojson.file_converter(argv[1])
        logging.info("PDF File Successfully converted into JSON")
        print("conversion completed")
        config.read('config.ini')
        school_name = config[school_code]['school_name']
        #school_code = config['school']['school_code']
        WATER_MARK_FILE = school_code+"_"+RESULT_FILE_NAME
        school_district = config[school_code]['district']
        exam_name = config[school_code]['exam_name']
        exam_month = config[school_code]['exam_month']
        exam_year = config[school_code]['exam_year']
        exam_class = config[school_code]['exam_class']
        no_rank = int(argv[2])
        logging.info("Number of toppers student "+argv[2])
        current_reg_no = argv[3]
        logging.info("First Register number "+current_reg_no)
        analysis.final_analysis(school_name,school_code,school_district,exam_name,exam_month,exam_year,exam_class,no_rank,RESULT_FILE_PATH,current_reg_no)
        logging.info("Analysis completed PDF Generated and Going to do watermark")
        watermarking.do_watermark(RESULT_FILE_PATH,"Ashok3.pdf",RESULT_FOLDER,WATER_MARK_FILE)
        #print("Watermarking Done")
        print(f"Results saved to: {WATER_MARK_FILE}")
    elif(file_format[2]=="csv"):
        pdf=0
        print("Format is CSV")
    else:
        print("Check your File name extension, It should always either PDF or CSV")
        exit()



def save_results(output_dir):
    """Save processing results to a file"""
    os.makedirs(output_dir, exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"processing_results_{timestamp}.")
    
    return output_file


if __name__ == "__main__":
    main(sys.argv)
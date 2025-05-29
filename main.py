import sys
import pdftojson
import analysis
import configparser
import watermarking
import os

config = configparser.ConfigParser()

def main(argv):
    pdf=0
    file_format = argv[1].split(".")
    RESULT_FOLDER = argv[4]
    RESULT_FILE_NAME = argv[5]
    RESULT_FILE_PATH = os.path.join(RESULT_FOLDER,RESULT_FILE_NAME)
    WATER_MARK_FILE = "water"+"_"+RESULT_FILE_NAME
    if(file_format[1]=="pdf"):
        pdf=1
        print("Format is PDF")
        pdftojson.file_converter(argv[1])
        print("conversion completed")
        config.read('config.ini')
        school_name = config['school']['school_name']
        school_code = config['school']['school_code']
        school_district = config['school']['district']
        exam_name = config['school']['exam_name']
        exam_month = config['school']['exam_month']
        exam_year = config['school']['exam_year']
        exam_class = config['school']['exam_class']
        no_rank = int(argv[2])
        isfull = bool(argv[3])
        analysis.final_analysis(school_name,school_code,school_district,exam_name,exam_month,exam_year,exam_class,no_rank,isfull,RESULT_FILE_PATH)
        watermarking.do_watermark(RESULT_FILE_PATH,"Ashok3.pdf",RESULT_FOLDER,WATER_MARK_FILE)
        #print("Watermarking Done")
        print(f"Results saved to: {WATER_MARK_FILE}")
    elif(file_format[1]=="csv"):
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
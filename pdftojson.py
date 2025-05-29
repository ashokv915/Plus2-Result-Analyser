from pypdf import PdfReader
import re
import json
import configparser

global school_code
global school_name

output_file_name = "result_data_1.json"


def main():
    print("Hello")
    pass

def file_converter(file_name):
    valid_groups = ["SCIENCE", "CS", "HUMANITIES", "COMMERCE"]
    student_names = []
    stud_dict = {}
    stud_list = []
    student_marks = []
    students_data = []
    

    pattern = r"(\d{8}.*?(?:EHS|NHS))"

    reader = PdfReader(file_name)
    total_pages = len(reader.pages)

    school_details = reader.pages[0].extract_text().splitlines()[3].split('-')
    school_code = school_details[0]
    school_name = school_details[1]
    school_district = school_details[2]

    exam_details = reader.pages[0].extract_text().splitlines()[4]
    exam_month = exam_details.split(" ")[3]
    exam_year = exam_details.split(" ")[5]
    exam_class = " ".join(exam_details.split(" ")[0:3])

    configwrite(school_name,school_code,exam_details,school_district,exam_month,exam_year,exam_class)
    print("Configuration created successfully")

    for i in range(total_pages):
        page = reader.pages[i]
        texts = page.extract_text()
        student_blocks = re.findall(pattern, texts, re.DOTALL)
        student_blocks = [b.replace("COMPUTER\nSCIENCE","CS").strip() for b in student_blocks]
        student_blocks = [b.replace("\n", " ").strip() for b in student_blocks]
        #student_blocks = [b.replace(" ","_").strip() for b in student_blocks]
        student_blocks = [b.replace("BUSINESS STUDIES WITH FUNCTIONAL MANAGEMENT", "BUSINESS_STUDIES").strip() for b in student_blocks]
        student_blocks = [b.replace("ACCOUNTANCY WITH COMPUTER ACCOUNTING", "ACCOUNTANCY").strip() for b in student_blocks]
        student_blocks = [b.replace("POLITICAL SCIENCE", "POLITICAL_SCIENCE").strip() for b in student_blocks]
        student_blocks = [b.replace("COMPUTER APPLICATION", "CA").strip() for b in student_blocks]
        students_data = students_data + student_blocks

    #print(students_data)

    for student in students_data:
        words = student.strip().split()
        reg_no = words[0]
        group = None
        group_index = -1
        
        for i in range(1, len(words)):
            if words[i] in valid_groups:
                group = words[i]
                group_index = i
                break

                
        name = " ".join(words[1:group_index])
        student_names = student_names + [name]   
        result_status = words[-1] if words[-1] in ["EHS", "NHS"] else "UNKNOWN"
        subject_data = words[group_index + len(group.split()):-1]

        subjects = []
        i=0
        while i + 2 < len(subject_data):
            subject = subject_data[i]
            try:
                marks = int(subject_data[i + 1])
                grade = subject_data[i + 2]
                subjects.append({"subject":subject,"marks":marks,"grade":grade})
                i += 3
            except ValueError:
                if i + 3 < len(subject_data):
                    subject = subject_data[i] + " " + subject_data[i + 1]
                    try:
                        marks = int(subject_data[i + 2])
                        grade = subject_data[i + 3]
                        subjects.append({"subject": subject,"marks": marks,"grade": grade})
                        i += 4
                    except ValueError:
                        break
                    else:
                        break
        for item in subjects:
            if(item['subject'] == 'CS'):
                group = 'CS'
        student_info = {"name" : name, "group" : group, "subjects" : subjects, "result" : result_status}
        stud_dict[reg_no] = student_info
    #print(stud_dict)
    with open(output_file_name,"w") as json_file:
        json.dump(stud_dict,json_file,indent=4)



def configwrite(schoolname, schoolcode,examname,district,month,year,examclass):
    config = configparser.ConfigParser()
    config['school'] = {
        'school_code' : schoolcode,
        'school_name' : schoolname,
        'district' : district,
        'exam_name' : examname,
        'exam_month' : month,
        'exam_year' : year,
        'exam_class' : examclass
    }

    with open('config.ini', 'w') as configfile:
        config.write(configfile)





if __name__ == "__main__":
    main()
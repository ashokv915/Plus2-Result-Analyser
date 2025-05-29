import json
import pandas as pd
from fpdf import FPDF
from fpdf import XPos,YPos

#CONFIG FILE READING
# config = configparser.ConfigParser()
# config.read('config.ini')
# school_name = config['school']['school_name']
# school_code = config['school']['school_code']
# school_district = config['school']['district']
# exam_name = config['school']['exam_name']
# exam_month = config['school']['exam_month']
# exam_year = config['school']['exam_year']
# exam_class = config['school']['exam_class']
#CONFIG FILE ENDS


def main():
    pass

def final_analysis(school_name,school_code,school_district,exam_name,exam_month,exam_year,exam_class,no_rank,isfull,final_pdf):
    output_file_name = "result_data_1.json"
    starting_reg_no = 24000000
    RESULT_FILE = final_pdf

    pdf = FPDF('P','mm','A4')
    pdf.add_page()

    with open(output_file_name,'r') as file:
        data = json.load(file)
    

    records = []
    valid_groups = ["SCIENCE","CS","HUMANITIES","COMMERCE"]
    
    for reg_no,student in data.items():
        for subj in student.get("subjects",[]):
            records.append({
            "register_no": reg_no,
            "name": student["name"],
            "group": student["group"],
            "subject": subj["subject"],
            "marks": subj["marks"],
            "grade": subj["grade"],
            "result": student["result"]
        })
    
    df = pd.DataFrame(records)
    subjects = df['subject'].unique()
    df.grade.replace(['A+','A','B+','B','C+','C','D+','D'],['A','A1','B','B1','C','C1','D','D1'], inplace=True)

    #Overall Pass Percentage
    df = df.astype({'register_no':int})
    df = df[df['register_no'] > starting_reg_no]
    num_of_sub = df.groupby(["register_no","name","group","result"], as_index=False)[["marks"]].sum()
    total_students = num_of_sub.shape[0]
    failed_stud = num_of_sub[num_of_sub['result']=='NHS'].shape[0]
    pass_percentage = str(round((((total_students-failed_stud)/total_students)*100),2))+"%"
    pass_count = total_students-failed_stud


    #Overall Pass Percentage
    df = df.astype({'register_no':int})
    df = df[df['register_no'] > starting_reg_no]
    num_of_sub = df.groupby(["register_no","name","group","result"], as_index=False)[["marks"]].sum()
    total_students = num_of_sub.shape[0]
    failed_stud = num_of_sub[num_of_sub['result']=='NHS'].shape[0]
    pass_percentage = str(round((((total_students-failed_stud)/total_students)*100),2))+"%"
    pass_count = total_students-failed_stud


    #Full A_ Count
    aplus_sub = df[df['grade']=='A']
    count_aplus = aplus_sub.groupby(['register_no','name','group'])[['register_no']].count()
    full_aplus = count_aplus[count_aplus['register_no']==6] 
    number_of_fullaplus = full_aplus.shape[0]

    #PDF WRITING THE ABOVE DETAILS
    pdf.set_font('times','BU',26)
    pw = pdf.w - 2 * pdf.l_margin
    pdf.cell(pw, 0.0, school_name,0, align="C")
    pdf.set_font('times', "",14)
    pdf.ln(15)
    pdf.cell(0,0,"School Code:"+str(school_code),0)
    pdf.ln(7)
    pdf.set_font('times', "",14)
    pdf.cell(0,0,"Examination Name : "+str(exam_name),new_x=XPos.LMARGIN,new_y=YPos.NEXT)

    #PDF WRITING TOTAL RESULT
    pdf.ln(15)
    pdf.set_font("times","BUI",18)
    pw = pdf.w - 2 * pdf.l_margin
    pdf.cell(pw,0.0,"Total Result of School", align="C")
    pdf.ln(10)

    pdf.set_font("times","",14)
    SUMMARY = [
        ("Percentage of Eligible Students", str(pass_percentage)),
        ("Total Students Registered for HSE Exam", str(total_students)),
        ("No. of students eligible for Higher Studies",str(pass_count)),
        ("No. of Students NOT Eligible for Higher Studies",str(failed_stud)),
        ("Number of A + Students ", str(number_of_fullaplus))
    ]

    pdfwrite(pdf,SUMMARY,180,100,12)

    #FULL A+ List
    aplus_sub = df[df['grade']=='A']
    aplus_sub = aplus_sub.drop(columns="result")
    count_aplus = aplus_sub.groupby(['register_no','name','group'])[['register_no']].count()
    full_aplus = count_aplus[count_aplus['register_no']==6]
    aplus_list = full_aplus.reset_index(names=['regno','name','group'])
    aplus_list = aplus_list.drop(columns="register_no")
    aplus_list = aplus_list.sort_values(by="group",ascending=False,ignore_index=True).reset_index(names="no",drop=True)
    aplus_list.index += 1
    aplus_student_list = aplus_list.values.tolist()
    aplus_student_list = [[index] + row for index, row in zip(aplus_list.index, aplus_student_list)]
    aplus_student_list = convert_to_string(aplus_student_list)
    aplus_student_list.insert(0,["No","reg_no","name","group"])
    pdf.ln(15)
    pdf.set_font("times","BUI",18)
    pw = pdf.w - 2 * pdf.l_margin
    pdf.cell(pw,0.0,"List of A+ Students", align="C")
    pdf.ln(10)
    pdf.set_font("times","",14)
    pdfwrite(pdf,aplus_student_list,180,10,40,70,30)

    #GROUPWISE FULL APLUS
    COUNT_FULL_APLUS = [['Group','Count']]
    for grp in valid_groups:
        aplus_grp = aplus_list[aplus_list['group']==grp]
        grp_aplus_count = aplus_grp.shape[0]
        COUNT_FULL_APLUS.append([grp,grp_aplus_count])
    COUNT_FULL_APLUS = convert_to_string(COUNT_FULL_APLUS)
    pdf.ln(15)
    pdf.set_font("times","BUI",18)
    pw = pdf.w - 2 * pdf.l_margin
    pdf.cell(pw,0.0,"Groupwise Full A+ Count", align="C")
    pdf.ln(10)
    pdf.set_font("times","",14)
    pdfwrite(pdf,COUNT_FULL_APLUS,180,50,10)



    #PASS PERCENTAGE OF EACH BRANCH
    pdf.ln(15)
    pdf.set_font("times","BUI",18)
    pw = pdf.w - 2 * pdf.l_margin
    pdf.cell(pw,0.0,"Groupwise Result", align="C")
    pdf.ln(10)

    pdf.set_font("times","",14)
    GROUP_RESULT = [('Group','Percentage')]
    for grp in valid_groups:
        #print(grp)
        df_grp = df[df['group']==grp]
        total_students_grp = df_grp.shape[0]
        failed_students_grp = df_grp[df_grp['result']=='NHS'].shape[0]
        pass_percentage_grp = (((total_students_grp-failed_students_grp)/total_students_grp)*100)
        GROUP_RESULT.append((grp, str(round(pass_percentage_grp,2))+"%"))
    
    pdfwrite(pdf,GROUP_RESULT,180,50,10)


    #TOP PERFORMERS
    pdf.ln(15)
    pdf.set_font("times","BUI",18)
    pw = pdf.w - 2 * pdf.l_margin
    pdf.cell(pw,0.0,"School Toppers List", align="C")
    pdf.ln(10)

    pdf.set_font("times","",11)

    num_of_sub = df.groupby(["register_no","name","group","result"], as_index=False)[["marks"]].sum()
    num_of_sub['per'] = num_of_sub['marks'].map(lambda m:mark2per(m))
    num_of_sub = num_of_sub.drop(columns="result")
    sorted_marks = num_of_sub.sort_values(by='per',ascending=False,ignore_index=True).reset_index(names="no",drop=True)
    sorted_marks.index += 1
    TOP_STUDENTS = sorted_marks.loc[:no_rank,:].values.tolist()
    TOP_STUDENTS = [[index] + row for index, row in zip(sorted_marks.index, TOP_STUDENTS)]
    TOP_STUDENTS = convert_to_string(TOP_STUDENTS)
    TOP_STUDENTS.insert(0,["No.","Register Number","Name","Group","Mark","Percentage"])
    pdfwrite(pdf,TOP_STUDENTS,180,10,40,70,30,20,22)


    #GROUPWISE TOPPERS
    pdf.ln(15)
    pdf.set_font("times","BUI",18)
    pw = pdf.w - 2 * pdf.l_margin
    pdf.cell(pw,0.0,"Groupwise Rank List", align="C")
    pdf.ln(10)


    for grp in valid_groups:
        pdf.set_font("times","UI",14)
        pw = pdf.w - 2 * pdf.l_margin
        pdf.cell(pw,0.0,grp, align="C")
        pdf.ln(10)
        pdf.set_font("times","",11)

        grp_wise = num_of_sub[num_of_sub["group"]==grp]
        #grp_wise = grp_wise.drop(columns="result")
        #grp_wise["per"] = grp_wise["marks"].map(lambda m:mark2per(m))
        sorted_grp_wise = grp_wise.sort_values(by="per",ascending=False,ignore_index=True).reset_index(names="no",drop=True)
        sorted_grp_wise.index += 1
        GRP_TOPPERS = sorted_grp_wise.loc[:3,:].values.tolist()
        GRP_TOPPERS = [[index] + row for index, row in zip(sorted_grp_wise.index, GRP_TOPPERS)]
        GRP_TOPPERS = convert_to_string(GRP_TOPPERS)


        GRP_TOPPERS.insert(0,["No","reg_no","name","group","marks","per"])
        pdfwrite(pdf,GRP_TOPPERS,180,10,25,40,30,20,15)
        pdf.ln(10)



    #SUBJECT WISE PERCENTAGE
    pdf.ln(15)
    pdf.set_font("times","BUI",18)
    pw = pdf.w - 2 * pdf.l_margin
    pdf.cell(pw,0.0,"Subjectwise Result", align="C")
    pdf.ln(10)

    pdf.set_font("times","",14)


    SUBJECT_RESULT = [("Subject","Percentage")]
    for sub in subjects:
        df_sub = df[df['subject']==sub]
        total_students_sub = df_sub.shape[0]
        failed_students_sub = df_sub[df_sub['grade']>="D"].shape[0]
        pass_percentage_sub = (((total_students_sub-failed_students_sub)/total_students_sub)*100)
        SUBJECT_RESULT.append((sub,"{1:.2f}%".format(sub,round(pass_percentage_sub,2))))

    pdfwrite(pdf,SUBJECT_RESULT,180,50,10)



    #SUBJECT WISE TOPPERS
    pdf.ln(15)
    pdf.set_font("times","BUI",18)
    pw = pdf.w - 2 * pdf.l_margin
    pdf.cell(pw,0.0,"Subjectwise Toppers", align="C")
    pdf.ln(10)
    df_copy = df.copy()
    df_copy.grade.replace(['A','A1','B','B1','C','C1','D','D1'],['A+','A','B+','B','C+','C','D+','D'], inplace=True)

    for sub in subjects:
        pdf.set_font("times","UI",14)
        pw = pdf.w - 2 * pdf.l_margin
        pdf.cell(pw,0.0,sub, align="C")
        pdf.ln(10)
        pdf.set_font("times","",11)

        sub_wise = df_copy[df_copy['subject']==sub]
        sub_wise = sub_wise.drop(columns="result")
        sub_wise = sub_wise.sort_values(by='marks',ascending=False,ignore_index=True).reset_index(names="no",drop=True)
        sub_wise.index += 1
        sub_wise_list = sub_wise.values.tolist()
        sub_wise_list = [[index] + row for index, row in zip(sub_wise.index, sub_wise_list)]
        sub_wise_list = convert_to_string(sub_wise_list)
        sub_wise_list = sub_wise_list[:3]
        sub_wise_list.insert(0,['No','reg_no','name','group','subject','mark','grade'])
        pdfwrite(pdf,sub_wise_list,180,12,37,50,37,50,20,20)
        pdf.ln(10)

    
    #STUDENTS PERCENTAGE
    if(isfull):
        pdf.set_font("times","UI",14)
        pw = pdf.w - 2 * pdf.l_margin
        pdf.cell(pw,0.0,"Percentage of Marks", align="C")
        pdf.ln(10)
        pdf.set_font("times","",11)
        
        num_of_sub = df.groupby(["register_no","name","group","result"], as_index=False)[["marks"]].sum()
        num_of_sub['per'] = num_of_sub['marks'].map(lambda m:mark2per(m))
        #num_of_sub = num_of_sub.drop(columns="result")
        num_of_sub = num_of_sub.astype({'register_no':int})
        sorted_marks = num_of_sub.sort_values(by='register_no',ascending=True,ignore_index=True).reset_index(names="no",drop=True)
        sorted_marks.index += 1
        TOP_STUDENTS = sorted_marks.loc[:,:].values.tolist()
        TOP_STUDENTS = [[index] + row for index, row in zip(sorted_marks.index, TOP_STUDENTS)]
        TOP_STUDENTS = convert_to_string(TOP_STUDENTS)
        TOP_STUDENTS.insert(0,["No.","Register Number","Name","Group","result","Mark","Percentage"])
        pdfwrite(pdf,TOP_STUDENTS,180,10,40,70,32,18,19,25)
    else:
        pass

    
    
    
    
    
    
    
    pdf.output(RESULT_FILE)









def pdfwrite(pdf,table_data,w=0,c1=0,c2=0,c3=0,c4=0,c5=0,c6=0,c7=0):
    with pdf.table(width=w, col_widths=(c1,c2,c3,c4,c5,c6,c7)) as table:
        for data_row in table_data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)


def mark2per(m):
    mar = round((m/1200)*100,2)
    return float(mar)

def convert_to_string(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.append(convert_to_string(item))  # Recursively convert nested lists
        else:
            result.append(str(item))  # Convert non-list items to string
    return result

if __name__ == "__main__":
    main()





####




































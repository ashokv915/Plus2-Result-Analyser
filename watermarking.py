from pypdf import PdfMerger, PdfReader,PdfWriter
import os

def main():
    pass
def do_watermark(pdf_file,watermark,result_folder,merged_file):
    RESULT_PATH = os.path.join(result_folder,merged_file)
    with open(pdf_file, "rb") as input_file, open(watermark, "rb") as watermark_file:
        input_pdf = PdfReader(input_file)
        watermark_pdf = PdfReader(watermark_file)
        watermark_page = watermark_pdf.get_page(0)

        output = PdfWriter()

        for i in range(input_pdf.get_num_pages()):
            pdf_page = input_pdf.get_page(i)
            pdf_page.merge_page(watermark_page,over=False)
            output.add_page(pdf_page)
        
        with open(merged_file, "wb") as merged_file:
            output.write(RESULT_PATH)

if __name__ == "__main__":
    main()
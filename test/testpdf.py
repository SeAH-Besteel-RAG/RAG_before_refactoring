import pypdf

file = (r"C:\Users\송준호\Documents\카카오톡 받은 파일\sample_file.pdf")
pdfreader = pypdf.PdfReader(file)

for page in pdfreader.pages:
    print(page.extract_text())
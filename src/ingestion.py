import fitz
import os

#FUnction for Extracting the text from PDF
def extract_text_from_pdf(pdf_path):

    #Uploading and Opening the PDF file
    pdf_file = fitz.open(pdf_path)

    #Storing all the text here
    pages_data = []


    #loop for extraction of text from every page
    for page_number in range(len(pdf_file)):
        page = pdf_file[page_number]

        #removing the header/footer from the page
        page_height = page.rect.height

        #get all the blocks from the page
        blocks = page.get_text("blocks")

        #text of this page
        page_text = ""

        for block in blocks:
            x0 = block[0]   # left position
            y0 = block[1]   # top position
            x1 = block[2]   # right position
            y1 = block[3]   # bottom position
            text = block[4] # actual text

            # Skip header from top - 8% top of the page
            if y0 < page_height * 0.08:
                continue

            # Skip footer from top - 8% bottom of the page
            if y1 > page_height * 0.92:
                continue

            #Skip the very small blocks
            if len(text.strip()) < 20:
                continue

            page_text += text + " "

        # only add the meaningful pages
        if len(page_text.strip()) > 50:
            pages_data.append({
                "text": page_text.strip(),
                "page_number": page_number + 1
            })

    pdf_file.close()       

    return  pages_data 


def extract_all_pdfs(folder_path, subject):
    """
    extract text from one pdf with page metadata

    Input  : pdf_path - PDF file ka path (string)
    Output : list of dicts - har dict mein ek page ka text aur metadata
    """

    results = []
    all_files = os.listdir(folder_path)

    for filename in all_files:

        if not filename.endswith(".pdf"):
            continue

        pdf_path = os.path.join(folder_path, filename)

        print(f"Reading: {filename}")

        pages_data = extract_text_from_pdf(pdf_path)

        for page_data in pages_data:
            results.append({
                "filename": filename,
                "subject": subject,
                "page_number": page_data["page_number"],
                "text": page_data["text"]
            })

    print(f"Total pages extracted: {len(results)}")

    return results
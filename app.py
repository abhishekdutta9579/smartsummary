import streamlit as st
import base64
import fitz
from PyPDF2 import PdfReader
import re
import pandas as pd
import torch
from transformers import pipeline

@st.cache(allow_output_mutation = True)
def summary_long_t5(text):
    summarizer = pipeline(
        "summarization",
        "pszemraj/long-t5-tglobal-base-16384-book-summary",
        device=0 if torch.cuda.is_available() else -1,
    )
    long_text = text

    result = summarizer(long_text)
    return result[0]["summary_text"]

##Page Layout
# Page expands to full width
st.set_page_config(page_title="Smart Summary APP", layout= "wide")

st.image("https://1000logos.net/wp-content/uploads/2019/06/Deloitte-Logo.jpg", width = 200)
st.title("SMART SUMMARY")
st.subheader("With AI")

input_pdf = st.file_uploader(label = "Please upload the PDF file here! :pdf:", type = "pdf")

if input_pdf is not None:
    with open("input.pdf", "wb") as f:
        base64_pdf = base64.b64encode(input_pdf.read()).decode("utf-8")
        f.write(base64.b64decode(base64_pdf))
    f.close()

        
    path = "input.pdf"

    # open the file
    pdf_file = fitz.open(path)
    file = open(path, 'rb')
    pdf_reader = PdfReader(file)

    ########## Finding the actual start of the page #############

    page = pdf_file[1]
    image_list_1 = page.get_images()
    image_list_1


    page_length = len(pdf_file)
    page_index = 0

    while (page_index < page_length):
        #Get the page itself
        page = pdf_file[page_index]
        image_list = page.get_images()
        if len(image_list) == 0 or (image_list != image_list_1):
            break
        #Get the page content
        page_index += 1

    #print(page_index)

    start_page_num = page_index
    ######
    number_of_pages = len(pdf_reader.pages)


    str = ""
    #list_1 = []
    for i in range(start_page_num, number_of_pages):
        pageObj = pdf_reader.pages[i]
        text1 = pageObj.extract_text()
        #m = re.split("(\d+/\d+/\d+)", text1)
        # m = re.split("\n", text1)
        #list_1.extend(m)
        str = str + text1

    #print(str)
    """
    output_file = open("Final1.pdf", 'w')

    for i in range(start_page_num, number_of_pages):
        text_write = pdf_reader.pages[i]
        text_feed = text_write.extract_text()
        output_file.write(text_feed)"""

    #### Segmenting the str into different news articles

    x1 = re.split("(\d+/\d+/\d+)", str)
    #news=[]
    Date=[]
    Body=[]

    ###Have to Make these patterns - Combinations #################################
    #list_news = ["Fastmarkets Metals Bulletin\n","CNBC\n", "CNBC", "Bloomberg", "Bloomberg\n"]
    ########################################################################################
    for sent in x1:
        #print(sent)
    
        if re.search("[0-9]{2}[-|\/]{1}[0-9]{2}[-|\/]{1}[0-9]{2}", sent):
            Date.append(sent)
            continue
        #elif sent in list_news:
        # news.append(sent)
        # continue
        else: 
            #if (sent not in list_news):   
            Body.append(sent)

    # Checking the uniformity of the lists

    #print(len(Date), len(Body))

    """summary_list =[]
    for i in Body:
        summary = summary_func.summarize(i, 0.5)
        summary_list.append(summary)"""



    cols = ["Body"]

    #Creating Data Frame

    df = pd.DataFrame(list(zip(Body[1:])), columns = cols)


    df["Summary"] = df["Body"].apply(summary_long_t5)


    # Checking the Data Frame is working correctly
    #print(df["Summary"])
    #print(df)



    final_csv = df.to_csv()
     
    st.download_button(label = '📥 Download CSV', data = final_csv, file_name = 'summary.csv')
  


    #Closing PDF File
    pdf_file.close()
    #output_file.close()

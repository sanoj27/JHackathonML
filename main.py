from numbers import Number
import string
from fastapi import FastAPI, Body,UploadFile, File
from pdf2image import convert_from_path
import cv2
import os,io
from googletrans import Translator
from google.cloud import vision_v1
from google.cloud.vision_v1 import types
import pandas as pd
from googletrans import Translator

import pytesseract
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

pytesseract.pytesseract.tesseract_cmd=r"C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
@app.post("/new-form/")
async def process_form(ROI:list=Body(),file:UploadFile = File(...)):
    # Handling ROI
    temp=ROI[0]
    num=[]
    letters=[]
    for i in temp.split(','):
        if(i.isdigit()):
            num.append(int(i))
        else:
            letters.append(i)
    final=[]
    j=0
    for i in letters:
        final.append(num[j:j+4])
        j=j+4


    # Main Image Resizing
    file.filename = f"formImg1.jpeg"
    contents = await file.read()
    IMAGEDIR="C:\\Users\\User\\Desktop\\JosephHackathonML\\"
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)
    image1 = cv2.imread("formImg1.jpeg")
    image1_rs = cv2.resize(image1, (800, 800))    
    cv2.imwrite('img rsed.jpeg',image1_rs)
    img = cv2.imread("img rsed.jpeg")

    # Field Extraction from ROI array. ROI = [ [] x:12, y:677, height:878, width:98, label:"Name"} ] 
    ans=[]
    for i in range(len(letters)):
        pred = img[final[i][1]:final[i][3],final[i][0]:final[i][2]]
        cv2.imwrite(r'C:\\Users\\User\\Desktop\\JosephHackathonML\\pred.jpeg', pred)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'visionkey.json'
        client = vision_v1.ImageAnnotatorClient();
        with io.open(f"{IMAGEDIR}pred.jpeg","rb") as image_file:
           content = image_file.read()
        image = types.Image(content=content)
        response = client.document_text_detection(image=image) 
        docText = response.full_text_annotation.text
        ch=docText[0]
        temp_buffer = ""
        if not(('a'<=ch and ch <='z') or ('A'<=ch and ch<='Z')):
            translater=Translator()
            eng=translater.translate(docText,dest="en")
            temp_buffer=temp_buffer+eng.text
            ans.append({letters[i]:temp_buffer})    
        else:        
            ans.append({letters[i]:docText})
    return ans
@app.post("/files/")
async def create_file(file: UploadFile = File(...)):
    file.filename = f"formImg.jpeg"
    contents = await file.read()  # <-- Important!
    IMAGEDIR="C:\\Users\\User\\Desktop\\JosephHackathonML\\"
    # example of how you can save the file
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)
    

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'visionkey.json'
    client = vision_v1.ImageAnnotatorClient();
    with io.open(f"{IMAGEDIR}{file.filename}","rb") as image_file:
        content = image_file.read()
    image = types.Image(content=content)
    response = client.document_text_detection(image=image) 
    docText = response.full_text_annotation.text
    final = docText.split('\n')[10:19]  
    return {"name":final[0],"age":final[1],"gender":final[2],"parent":final[3],"phone":final[4],"email":final[5],"address":final[6],"city":final[7],"state":final[8]} 
    #async def writePdf():
    #    with open("form.pdf","wb") as buffer:
    #       shutil.copyfileobj(file.file,buffer)
    #await writePdf()        
    ## Pdf to Image
    #async def imgToPdf(): 
    #    pages = convert_from_path(pdf_path="form.pdf",poppler_path="C:\\Users\\User\\Desktop\\JosephHackathonML\\poppler-0.68.0\\bin")
    #    for i in range(len(pages)):
    #        pages[i].save('img 1.jpeg', 'JPEG')
    #await imgToPdf()
    ## Reading and resizing image
    #try:
    #    image1 = cv2.imread("C:\\Users\\User\\Desktop\\JosephHackathonML\\img 1.jpeg")
    #    image1_rs = cv2.resize(image1, (800, 800)) 
    #    cv2.imwrite("C:\\Users\\User\\Desktop\\JosephHackathonML\\img rsed.jpeg",image1_rs)
    #    img = cv2.imread("img rsed.jpeg")
    #    def getFields(img):
    #        crop_name = img[110:150, 227:600]  
    #        crop_age = img[150:190,227:375]
    #        crop_gender = img[150:190,520:665]
    #        crop_city = img[190:230,227:375]
    #        crop_state = img[190:230,520:665]
    #        crop_phone = img[230:270,227:665]
    #        crop_email = img[270:310,227:665]
    #        cv2.imwrite("C:\\Users\\User\\Desktop\\JosephHackathonML\\name.jpeg",crop_name)
    #        cv2.imwrite("C:\\Users\\User\\Desktop\\JosephHackathonML\\age.jpeg",crop_age)
    #        cv2.imwrite("C:\\Users\\User\\Desktop\\JosephHackathonML\\gender.jpeg",crop_gender)
    #        cv2.imwrite("C:\\Users\\User\\Desktop\\JosephHackathonML\\city.jpeg",crop_city)
    #        cv2.imwrite("C:\\Users\\User\\Desktop\\JosephHackathonML\\state.jpeg",crop_state)
    #        cv2.imwrite("C:\\Users\\User\\Desktop\\JosephHackathonML\\phone.jpeg",crop_phone)
    #        cv2.imwrite("C:\\Users\\User\\Desktop\\JosephHackathonML\\email.jpeg",crop_email)
    #    getFields(img)   
    #    url=["C:\\Users\\User\\Desktop\\JosephHackathonML\\name.jpeg","C:\\Users\\User\\Desktop\\JosephHackathonML\\age.jpeg","C:\\Users\\User\\Desktop\\JosephHackathonML\\gender.jpeg","C:\\Users\\User\\Desktop\\JosephHackathonML\\city.jpeg","C:\\Users\\User\\Desktop\\JosephHackathonML\\state.jpeg","C:\\Users\\User\\Desktop\\JosephHackathonML\\city.jpeg","C:\\Users\\User\\Desktop\\JosephHackathonML\\phone.jpeg","C:\\Users\\User\\Desktop\\JosephHackathonML\\email.jpeg"]
    #    images = [keras_ocr.tools.read(i) for i in url]
    #    preds=[]
    #    for i in images:
    #        preds.append(pytesseract.image_to_string(i))
    #except Exception as e:
    #    print(str(e))
    #ans=[]
    #for i in preds:
    #    ans.append(''.join(e for e in str(i) if e.isalnum()))
    #cv2.waitKey(0) 
    #cv2.destroyAllWindows()
    #return {"name": ans[0],"age":ans[1],"gender": "Male" if len(ans[2])==4 else "Female","city":ans[3],"state":ans[4],"phone":ans[5],"email":ans[6]}  
    return {"name":"Hari"}
@app.get("/")
def welcome():
    return {"message":"Welcome"}
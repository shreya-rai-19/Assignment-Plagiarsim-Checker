from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
import boto3
from werkzeug.utils import secure_filename
import pinecone
import pinecone.info
import os
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from PyPDF2 import PdfFileReader
from io import BytesIO
from flask import Markup

views = Blueprint('views', __name__)

#AWS Keys...Private item
access_key = 'AKIA2BIH4HLCO6DGGAG7'
secret_access_key = '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'

#Creating an S3 resource
s3 = boto3.resource(
    service_name = 's3',
    region_name = 'ap-south-1',
    aws_access_key_id = 'AKIA2BIH4HLCO6DGGAG7',
    aws_secret_access_key = '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'
)


#Defining API's

@views.route('/')
# @login_required
def home():
    return render_template("home.html", user=current_user)

# Api to check Plagiarism
@views.route('/upload', methods = ['POST'])
@login_required
def upload():
    if request.method == 'POST':
        img = request.files['file']
        if img:
            filename = secure_filename(img.filename)
            print(filename)  
            #Checking the file extension
            if filename.endswith('.txt') or  filename.endswith('.pdf'):
                img.save(filename)         

                #Uploading file to S3 bucket
                s3.Bucket('varunkalbhore-s3').upload_file(
                    Filename = filename,
                    Key = 'PlagCheck/' + str(current_user.email) + '/' + str(filename)
                )
             
                #Instantiating an object of file to read it's data
                obj = s3.Bucket('varunkalbhore-s3').Object('PlagCheck/' + str(current_user.email) + '/' + str(filename)).get()
                text = obj['Body'].read().decode('ISO-8859-1')

                #Pinecone Setup and instantiation 
                api_key = "533be2c5-142e-47e7-9a66-30252953adeb"
                pinecone.init(api_key=api_key, environment='us-west1-gcp')

                #Defining the Bert Model to be used for getting embeddings and cosine similarity
                model = SentenceTransformer('all-mpnet-base-v2')

                #Getting the dataset embeddings
                index = pinecone.Index('dataset')
                encoding = model.encode(text).tolist()
                
                #Queriying cosine similarity between user file and dataset (embeddings)
                top_k = 2
                result = index.query(queries=[encoding], top_k = top_k )
                print(result)

                #Generating final results
                abc=[x['score']for x in result['results'][0]['matches']]
                tt = [x['id'] for x in result['results'][0]['matches']]
                plag = int(abc[0]*100)
                print(tt)
                file_name = tt[0]
                file_name2 = tt[1]
                if plag>=60:
                    msg = Markup('Alert! ' + str(plag) +'% Plagiarism detected   files: <br>'+ '1] ' + file_name + '<br>'+'2] ' + file_name2)
                   
                elif plag > 30 and plag < 60 :
                    msg =  Markup("'" + str(plag) +"% Plagiarism detected'" + "______        files: <br>" + "1] " + file_name + "<br>"+"2]"  + file_name2)
                else:
                    msg = "Hurray! No Plagiarism Detected"    

            #If a user selects a file format other than .txt or .pdf
            else:
                msg = "Please select a .txt or .pdf filetype"
        else:
                msg = "No files selected"

    return render_template("index.html", msg = msg, user=current_user)


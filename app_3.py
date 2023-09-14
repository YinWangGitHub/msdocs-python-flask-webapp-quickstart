import requests, os, uuid, json
#from dotenv import load_dotenv
#load_dotenv()
from flask import Flask, redirect, url_for, request, render_template, session,jsonify
from azure.storage.blob import BlobServiceClient, BlobClient, generate_container_sas
import datetime

import time
import datetime
import os
import requests


app = Flask(__name__)

KEY= "0615a14f92e444aab800e922b8d07ea2"
ENDPOINT= "https://api.cognitive.microsofttranslator.com/"
LOCATION= "eastus"

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def index_post():
    previous_language = 'zh-CN'  # Example value for testing

    # Read the values from the form
    original_text = request.form['text']
    target_language = request.form['language']
    file_path = request.form['file_path']

    key = KEY
    endpoint = ENDPOINT
    location = LOCATION

    if file_path:
        if os.path.exists(file_path):
            download_path = translate_doc(file_path, target_language)
            return render_template(
                'index.html',
                translated_text=None,
                original_text=original_text,
                target_language=target_language,
                previous_language=previous_language,
                download_path=download_path
            )
    else:
        path = '/translate?api-version=3.0'
        constructed_url = endpoint + path
        
        headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Ocp-Apim-Subscription-Region': location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        
        params = {
            
            'api-version': '3.0',
            'to': target_language
        }

        if target_language == 'en':
            params["glossaries"] = [{
                "glossaryUrl": "https://rawdocuments32.blob.core.windows.net/dgwglossary/test_glossary_2.csv",
                "format": "csv"
            }]

        body = [{'text': original_text}]

        translator_request = requests.post(constructed_url, headers=headers, params=params, json=body)
        translator_response = translator_request.json()
        translated_text = translator_response[0]['translations'][0]['text']

        return render_template(
            'index.html',
            translated_text=translated_text,
            original_text=original_text,
            target_language=target_language,
            previous_language=previous_language
        )
    

if __name__ == '__main__':
        #print jdata
  app.run(host="0.0.0.0",port=5002,debug=True)

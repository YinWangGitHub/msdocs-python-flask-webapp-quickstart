import requests, os, uuid, json, datetime
from flask import Flask, redirect, url_for, request, render_template, session,jsonify
from azure.storage.blob import BlobServiceClient, BlobClient, generate_container_sas
from azure.storage.blob import BlobSasPermissions, generate_blob_sas


app = Flask(__name__)


KEY= "0615a14f92e444aab800e922b8d07ea2"
ENDPOINT= "https://api.cognitive.microsofttranslator.com/"
LOCATION= "eastus"

STORAGE_ACCOUNT_NAME = "rawdocuments32"
STORAGE_ACCOUNT_KEY = "ctz5hA3R9CZJYy7Z/QNeaLf0owB6nO6Bp3BPIWS3LPty+DOVGuHStxerPukMH2K+TXeOHr1S8yMb+AStPjvMfA=="
STORAGE_ENDPOINT = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/" 


# 创建一个Blob服务客户端
blob_service_client = BlobServiceClient(
    account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net", 
    credential=STORAGE_ACCOUNT_KEY
)

source_container_name = "translationresources"
target_container_name = "translated-files"
glossary_container_name = "dgwglossary"


def generate_sas_url(container,blob_name):
    
    sas_token = generate_blob_sas(
        container_name=container.container_name,
        blob_name=blob_name,
        account_name=STORAGE_ACCOUNT_NAME, 
        account_key=STORAGE_ACCOUNT_KEY, 
        permission=BlobSasPermissions(read=True, write=True), 
        expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    )
    

    container_sas_url = STORAGE_ENDPOINT + container.container_name + "/" + blob_name +"?" + sas_token
    print(f"Generating {container.container_name} SAS URL:", container_sas_url)
    return container_sas_url


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def index_post():

    previous_language = 'zh-CN'  # 假设为示例值, just testing

    # Read the values from the form
    original_text = request.form['text']
    target_language = request.form['language']
    file_path = request.form['file_path']

    key = KEY
    endpoint = ENDPOINT
    location = LOCATION

    if file_path :
        if os.path.exists(file_path) :
            download_path = translate_doc(file_path,target_language)
            return render_template(
                'index.html',
                translated_text=None,
                original_text=original_text,
                target_language=target_language,
                previous_language=previous_language,
                download_path = download_path
            )

    else :
        glossary_container_sas_url = generate_sas_url(glossary_container, "FinalGlossary.tsv")
        
        # Indicate that we want to translate and the API version (3.0) and the target language
        path = '/translate?api-version=3.0'
        # Add the target language parameter Q2, add glossary here??
        target_language_parameter = '&to=' + target_language
        # Create the full URL
        #constructed_url = endpoint + path + target_language_parameter
        constructed_url = endpoint + path
        # Set up the header information, which includes our subscription key
        headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Ocp-Apim-Subscription-Region': location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        params = {
            'api-version': '3.0',
            'to': target_language,
            "glossaries": [
                        {                 
                            "glossaryUrl": glossary_container_sas_url,
                            "format": "tsv"
                        }]
        }

        # Create the body of the request with the text to be translated
        body = [{ 'text': original_text }]

        # Make the call using post
        #translator_request = requests.post(constructed_url, headers=headers, json=body)
        translator_request = requests.post(constructed_url, headers=headers,params=params, json=body)
        # Retrieve the JSON response
        translator_response = translator_request.json()
        # Retrieve the translation
        translated_text = translator_response[0]['translations'][0]['text']

        # Call render template, passing the translated text,
        # original text, and target language to the template
        return render_template(
            'index.html',
            translated_text=translated_text,
            original_text=original_text,
            target_language=target_language,
            previous_language=previous_language
   
        )



try:
    blob_service_client.get_container_client(glossary_container_name)
    print("Glossary container already exists.")
    glossary_container = blob_service_client.get_container_client(glossary_container_name)
except azure.core.exceptions.ResourceNotFoundError:
    print("Creating glossary container...")
    glossary_container = blob_service_client.create_container(glossary_container_name)

try:
    blob_service_client.get_container_client(source_container_name)
    print("Source container already exists.")
    source_container = blob_service_client.get_container_client(source_container_name)
except azure.core.exceptions.ResourceNotFoundError:
    print("Creating source container...")
    source_container = blob_service_client.create_container(source_container_name)
    
try:
    blob_service_client.get_container_client(target_container_name)
    print("Target container already exists.")
    target_container = blob_service_client.get_container_client(target_container_name)
except azure.core.exceptions.ResourceNotFoundError: 
    print("Creating target container...")
    target_container = blob_service_client.create_container(target_container_name)



def get_timestamp_filename(filename):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    name, ext = os.path.splitext(filename)
    return f"{name}_{timestamp}{ext}"




endpoint = 'https://translation30.cognitiveservices.azure.com/'
key =  '0615a14f92e444aab800e922b8d07ea2'
path = 'translator/text/batch/v1.1/batches' 
constructed_url = endpoint + path

headers = {
  'Ocp-Apim-Subscription-Key': key,
  'Content-Type': 'application/json',
}

    

@app.route('/uploadFile', methods=['POST'])
def upload_file():
    try:
        f = request.files['file']
        if f:
            blob_name = get_timestamp_filename(f.filename)
            f.save(os.path.join("upload", blob_name))
            return jsonify({"message": "File uploaded successfully","file_path":os.path.join("upload", blob_name)})
        else:
            return jsonify({"message": "No file provided"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#@app.route('/translate', methods=['POST'])
def translate_doc(file_path,target_language):

    blob_name = os.path.basename(file_path)

    with open(file_path, "rb") as doc:
        source_container.upload_blob(blob_name, doc)


    source_container_sas_url = generate_sas_url(source_container,blob_name)
    target_container_sas_url = generate_sas_url(target_container,blob_name)
    glossary_container_sas_url = generate_sas_url(glossary_container, "FinalGlossary.tsv")
    print(source_container_sas_url,target_container_sas_url, glossary_container_sas_url)
    
    
    body= {
    "inputs": [
        {
            "storageType": "File",
            "source": {
                "sourceUrl": source_container_sas_url
            },
            "targets": [
                {
                    "targetUrl": target_container_sas_url,
                    "language": target_language,
                    "glossaries": [
                        {
                            "glossaryUrl": glossary_container_sas_url,
                            "format": "tsv"
                        }
                    ]
                }
            ]
        }
    ]
    }

    key =  '0615a14f92e444aab800e922b8d07ea2'


    headers = {
      'Ocp-Apim-Subscription-Key': key,
      'Content-Type': 'application/json',
    }
    
    
    response = requests.post(constructed_url, headers=headers, json=body)
    response_headers = response.headers
    
    print(f'response status code: {response.status_code}\nresponse status: {response.reason}\n\nresponse headers:\n')
    download_path = ""
    
    for key, value in response_headers.items():
        print(key, ":", value)
        #Operation-Location : https://translation30.cognitiveservices.azure.com/translator/text/batch/v1.1/batches/7e36922c-2c53-47a4-8f5e-35e1ea4789ed
        if key == "Operation-Location" :
            operation_url = value
            while True :
                response = requests.get(operation_url, headers=headers)
                response_result = response.json()
                print(response_result)
                #__import__('ipdb').set_trace()
                #{"id":"b6293aee-6f81-4c42-a285-b302a07a9639","createdDateTimeUtc":"2023-08-31T18:35:20.3242244Z","lastActionDateTimeUtc":"2023-08-31T18:35:36.8502189Z","status":"Succeeded","summary":{"total":1,"failed":0,"success":1,"inProgress":0,"notYetStarted":0,"cancelled":0,"totalCharacterCharged":21}}
                if response_result["status"] == "Succeeded" :
                    #{"value":[{"path":"https://rawdocuments32.blob.core.windows.net:443/translated-files/allen_20230901023513.txt","sourcePath":"https://rawdocuments32.blob.core.windows.net:443/translationresources/allen_20230901023513.txt","createdDateTimeUtc":"2023-08-31T18:35:24.3861005Z","lastActionDateTimeUtc":"2023-08-31T18:35:36.8502098Z","status":"Succeeded","to":"zh-Hans","progress":1,"id":"008f7b2b-0000-0000-0000-000000000000","characterCharged":21}]}
                    document_url = operation_url + "/documents"
                    response = requests.get(document_url, headers=headers)
                    response_result = response.json()
                    print(response_result)
                    if response_result["value"][0]['status'] == "Succeeded" :
                        #download_path = response_result["value"][0]["path"]
                        download_path = target_container_sas_url
                    break
    
    
    print(download_path)     
    return download_path

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5005,debug=True)
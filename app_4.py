import requests, os, uuid, json
from flask import Flask, redirect, url_for, request, render_template, session, jsonify

app = Flask(__name__)

KEY = "0615a14f92e444aab800e922b8d07ea2"
ENDPOINT = "https://api.cognitive.microsofttranslator.com/"
LOCATION = "eastus"

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def index_post():
    previous_language = 'zh-CN'  # Just for testing

    original_text = request.form.get('text')
    target_language = request.form.get('language')
    file_path = request.form.get('file_path')

    # If file_path is provided and file exists
    if file_path and os.path.exists(file_path):
        download_path = translate_doc(file_path, target_language) # Assuming you have a function named translate_doc
        return render_template('index.html', 
                               translated_text=None,
                               original_text=original_text,
                               target_language=target_language,
                               previous_language=previous_language,
                               download_path=download_path)

    else:
        path = '/translate?api-version=3.0'
        constructed_url = ENDPOINT + path
        
        headers = {
            'Ocp-Apim-Subscription-Key': KEY,
            'Ocp-Apim-Subscription-Region': LOCATION,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        params = {'api-version': '3.0', 'to': target_language}

        if target_language == 'en':
            params["glossaries"] = [{
                "glossaryUrl": "https://rawdocuments32.blob.core.windows.net/dgwglossary/test_glossary_2.csv",
                "format": "csv"
            }]

        body = [{'text': original_text}]

        response = requests.post(constructed_url, headers=headers, params=params, json=body)

        # Error handling
        if response.status_code != 200:
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
            print(f"Error with status code {response.status_code}: {error_message}")
            return render_template('index.html', 
                                   translated_text=f"Translation error: {error_message}",
                                   original_text=original_text,
                                   target_language=target_language,
                                   previous_language=previous_language)

        translated_text = response.json()[0]['translations'][0]['text']

        return render_template('index.html', 
                               translated_text=translated_text,
                               original_text=original_text,
                               target_language=target_language,
                               previous_language=previous_language)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)


response = requests.post(constructed_url, headers=headers, params=params, json=body)
print(f"Request URL: {response.url}")
print(f"Request headers: {headers}")
print(f"Request body: {json.dumps(body)}")
print(f"Response status: {response.status_code}")
print(f"Response text: {response.text}")




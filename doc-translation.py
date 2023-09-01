import requests

endpoint = 'https://translation30.cognitiveservices.azure.com/'
key =  '0615a14f92e444aab800e922b8d07ea2'
path = 'translator/text/batch/v1.1/batches'
constructed_url = endpoint + path

sourceSASUrl = 'https://rawdocuments32.blob.core.windows.net/input-files?sp=rl&st=2023-08-30T02:22:05Z&se=2023-08-30T10:22:05Z&spr=https&sv=2022-11-02&sr=c&sig=7Al3Etdbz1pbVi%2FEwo%2BG%2B9M%2Fwgx3%2BD4aBfKlDlcD2b8%3D'

targetSASUrl = 'https://rawdocuments32.blob.core.windows.net/translated-files?sp=cwl&st=2023-08-30T02:25:20Z&se=2023-08-30T10:25:20Z&spr=https&sv=2022-11-02&sr=c&sig=3pFR2wNcvPWBjLoWUK89RhN2ykO7KZm8T%2BoM1p6xYBU%3D'

body= {
    "inputs": [
        {
            "source": {
                "sourceUrl": sourceSASUrl,
                "storageSource": "AzureBlob",
                "language": "en"
            },
            "targets": [
                {
                    "targetUrl": targetSASUrl,
                    "storageSource": "AzureBlob",
                    "category": "general",
                    "language": "zh-Hans"
                }
            ]
        }
    ]
}
headers = {
  'Ocp-Apim-Subscription-Key': key,
  'Content-Type': 'application/json',
}

response = requests.post(constructed_url, headers=headers, json=body)
response_headers = response.headers

print(f'response status code: {response.status_code}\nresponse status: {response.reason}\n\nresponse headers:\n')

for key, value in response_headers.items():
    print(key, ":", value)
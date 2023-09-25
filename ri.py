import requests, os, uuid, json, datetime
from flask import Flask, redirect, url_for, request, render_template, session,jsonify
from azure.storage.blob import BlobServiceClient, BlobClient, generate_container_sas
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from pytz import timezone

est=  timezone("US/Eastern")
app = Flask(__name__)

KEY= "0615a14f92e444aab800e922b8d07ea2"
ENDPOINT= "https://api.cognitive.microsofttranslator.com/"
LOCATION= "eastus"

STORAGE_ACCOUNT_NAME = "rawdocuments32"
STORAGE_ACCOUNT_KEY = "ctz5hA3R9CZJYy7Z/QNeaLf0owB6nO6Bp3BPIWS3LPty+DOVGuHStxerPukMH2K+TXeOHr1S8yMb+AStPjvMfA=="

connecting_string = "DefaultEndpointsProtocol=https;AccountName=rawdocuments32;AccountKey=ctz5hA3R9CZJYy7Z/QNeaLf0owB6nO6Bp3BPIWS3LPty+DOVGuHStxerPukMH2K+TXeOHr1S8yMb+AStPjvMfA==;EndpointSuffix=core.windows.net"

STORAGE_ENDPOINT = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/" 


# 创建一个Blob服务客户端
blob_service_client = BlobServiceClient(
    account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net", 
    credential=STORAGE_ACCOUNT_KEY
)


container_name = "dgwglossary"

container_client = blob_service_client.get_container_client(container_name)

file_name = "TranslationGlossaryNEW.tsv"
sas_token = generate_blob_sas(container_name=container_name,blob_name=file_name,account_name=STORAGE_ACCOUNT_NAME, account_key=STORAGE_ACCOUNT_KEY, permission=BlobSasPermissions(read=True, ), expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=1))

sas_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{file_name}?{sas_token}"
print(sas_url)
response = requests.get(sas_url)
print(response)

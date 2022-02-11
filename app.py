from flask import request
from flask import Flask,send_from_directory
from flask import jsonify
from flask_restful import Resource, Api, reqparse
from werkzeug.utils import secure_filename
from flask_cors import CORS,cross_origin
from boilerpy3 import extractors
from newspaper import Article
import json
import os
from zipfile import ZipFile
from firebase_admin import credentials, initialize_app, storage
import time
import random
import string
import requests




cred = credentials.Certificate("keycred.json")
initialize_app(cred, {'storageBucket': 'scrapper-algrow.appspot.com'})


curr_path=os.getcwd()



def respgen(url,control,count):
    
    if control=="single":
        extractor = extractors.ArticleExtractor()

        try:
            content = extractor.get_content_from_url(url)
            metadata= extractor.get_doc_from_url(url)
            title= metadata.title
            
            ranString= '-'.join(random.choices(string.ascii_uppercase + string.digits, k = 3))
            fname="Scrap"+ranString+".txt"
            f = open(fname, "w")
            f.write("** ")
            f.write(title)
            f.write(" ** ")
            f.write("\n \n")
            f.write(extractor)
            f.close()
            return fname
            
            
        except:
            article= Article(url)
            article.download()
            article.parse()
            text = article.text 
            title=article.title
            
            ranString= '-'.join(random.choices(string.ascii_uppercase + string.digits, k = 3))
            fname="Scrap"+ranString+".txt"
            f = open(fname, "w")
            f.write("** ")
            f.write(title)
            f.write("** ")
            f.write("\n \n")
            f.write(text)
            f.close()
            return fname
            
    elif control=="file":
        extractor = extractors.ArticleExtractor()

        try:
            content = extractor.get_content_from_url(url)
            metadata= extractor.get_doc_from_url(url)
            title= metadata.title
            name="Scraped-"+str(count+1)+".txt"
            f = open(name, "w")
            f.write("** ")
            f.write(title)
            f.write(" ** ")
            f.write("\n \n")
            f.write(extractor)
            f.close()
            
            
        except:
            article= Article(url)
            article.download()
            article.parse()
            text = article.text 
            title = article.title
            name="Scraped-"+str(count+1)+".txt"
            f = open(name, "w")
            f.write("** ")
            f.write(title)
            f.write(" ** ")
            f.write("\n \n")
            f.write(text)
            f.close()


app= Flask(__name__)
CORS(app,support_credentials=True)
api = Api(app)

app.config['CORS_HEADERS'] = 'Content-Type'



@app.route("/urlinput", methods=['POST'])
@cross_origin(supports_credentials=True)
def urlinput():
    data=request.get_json()
    url = list(data.values())[0]
    print(url)
    fname=respgen(url,"single",0)
    try:
        print(curr_path)
        
        
        
        print("1")
        bucket = storage.bucket()
        print("02")
        blob = bucket.blob(fname)
        print("03")
        blob.upload_from_filename(fname)
        print("04")
        blob.make_public()
        print("05")
        url= blob.public_url
        
        
        return url
    except Exception:
        return "Not Working"        
    

@app.route("/urllist", methods=['GET'])
@cross_origin(supports_credentials=True)
def urllist():
    listurl= "get se \t\ go "
    return jsonify(listurl)

@app.route("/urlfile", methods=['POST'])
@cross_origin(supports_credentials=True)
def urlfileinput():
    f = request.files['']
    f.save(secure_filename(f.filename))
    file=open(secure_filename(f.filename))
    ranString= '-'.join(random.choices(string.ascii_uppercase + string.digits, k = 3))
    
    trim= secure_filename(f.filename)
    trim_filename= trim.replace(".txt","")
    zipfilename=trim_filename+ranString+".zip"
    url=[]
    for line in file:
        url.append(line.strip())
        
    urlcount= len(url)
    for i, val in enumerate(url):
        respgen(val,"file",i)
    print(urlcount)
    newzip= ZipFile(zipfilename,"w")
    for i in range(urlcount):
        print(i)
        name="Scraped-"+str(i+1)+".txt"
        newzip.write(name)
    newzip.close()
    
    
    bucket = storage.bucket()
    blob = bucket.blob(zipfilename)
    
    blob.upload_from_filename(zipfilename)
    
    
    blob.make_public()
    
    url= blob.public_url
    
    return url


@app.route("/scrapebykey", methods=['POST'])
@cross_origin(supports_credentials=True)
def scrapebykey():
    data=request.get_json()
    key = list(data.values())[0]
    keyword= key + "+article"

    clean_keyword= keyword.replace(" ","+")


    url ="https://google-search3.p.rapidapi.com/api/v1/search/q=" + clean_keyword + "&num=100&lr=lang_en&hl=en&cr=US"

    headers = {
        'x-user-agent': "desktop",
        'x-proxy-location': "IN",
        'x-rapidapi-host': "google-search3.p.rapidapi.com",
        'x-rapidapi-key': "f4e71a02c6msh3ed103fafc11fcbp159b85jsn30e3dc424c9a"
        }

    response = requests.request("GET", url, headers=headers)

    jsonData= json.loads(response.text)

    ulrs=[]
    
    for i in range(6):
        urls[i] = jsonData["results"][i]["link"]
    

    for i in range(6):
        respgen(urls[i],"file",i)
        
    zipfilename="keyword"+'_'.join(random.choices(string.ascii_uppercase + string.digits, k = 4))   
    newzip= ZipFile(zipfilename,"w")
    for i in range(6):
            print(i)
            name="Scraped-"+str(i+1)+".txt"
            newzip.write(name)
    
    newzip.close()
    
    
    bucket = storage.bucket()
    blob = bucket.blob(zipfilename)
    
    blob.upload_from_filename(zipfilename)
    
    
    blob.make_public()
    
    url= blob.public_url
    
    return url






if __name__=="__main__":
    app.run(debug=True)

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

cred = credentials.Certificate("keycred.json")
initialize_app(cred, {'storageBucket': 'scrapper-algrow.appspot.com'})


curr_path=os.getcwd()



def respgen(url,control,count):
    
    if control=="single":
        extractor = extractors.ArticleExtractor()

        try:
            content = extractor.get_content_from_url(url)
            f = open("gen.txt", "w")
            f.write(extractor)
            f.close()
            
            
        except:
            article= Article(url)
            article.download()
            article.parse()
            text = article.text 
            f = open("gen.txt", "w")
            f.write(text)
            f.close()
    elif control=="file":
        extractor = extractors.ArticleExtractor()

        try:
            content = extractor.get_content_from_url(url)
            name="gen"+str(count)+".txt"
            f = open(name, "w")
            f.write(extractor)
            f.close()
            
            
        except:
            article= Article(url)
            article.download()
            article.parse()
            text = article.text 
            name="gen"+str(count)+".txt"
            f = open(name, "w")
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
    respgen(url,"single")
    try:
        print(curr_path)
        return send_from_directory(curr_path,"gen.txt",as_attachment=True),{'Content-Disposition': 'attachment'}
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
    url=[]
    for line in file:
        url.append(line.strip())
        
    urlcount= len(url)
    for i, val in enumerate(url):
        respgen(val,"file",i)
    print(urlcount)
    newzip= ZipFile("generated.zip","w")
    for i in range(urlcount):
        print(i)
        name="gen"+str(i)+".txt"
        file_name= "generated.zip"
        newzip.write(name)
    newzip.close()
    
    bucket = storage.bucket()
    blob = bucket.blob("generated.zip")
    
    blob.upload_from_filename("generated.zip")
    
    
    blob.make_public()
    
    url= blob.public_url
    
    return url



if __name__=="__main__":
    app.run(debug=True)

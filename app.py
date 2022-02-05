from flask import request
from flask import Flask,send_from_directory
from flask import jsonify
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS,cross_origin
from boilerpy3 import extractors
from newspaper import Article
import json
import os


curr_path=os.getcwd()

def respgen(url):
    
    extractor = extractors.ArticleExtractor()

    try:
        content = extractor.get_content_from_url(url)
        f = open("gen.csv", "w")
        f.write(extractor)
        f.close()
        
        
    except:
        article= Article(url)
        article.download()
        article.parse()
        text = article.text 
        f = open("gen.csv", "w")
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
    respgen(url)
    try:
        print(curr_path)
        return send_from_directory(curr_path,"gen.csv",as_attachment=True)
    except Exception:
        return "Not Working"        
    

@app.route("/urllist", methods=['GET'])
@cross_origin(supports_credentials=True)
def urllist():
    listurl= "get se \t\ go "
    return jsonify(listurl)



if __name__=="__main__":
    app.run()
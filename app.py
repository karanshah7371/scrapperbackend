from flask import request
from flask import Flask
from flask import jsonify
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS,cross_origin
from boilerpy3 import extractors
from newspaper import Article
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pymongo
from pymongo import MongoClient



def scrapeData(url):
    #Google Sheet Connection ID's
    gc = gspread.service_account(filename='mycredentials.json')
    sheetkey='1eFv4Yw7HEN5n5PRldyAnzl5OonYDFu4FYnqmtohoE-k'
    gsheet = gc.open_by_key(sheetkey)
    currentSheet= gsheet.worksheet("Page1")
    countersheet= gsheet.worksheet("counters")



    extractor = extractors.ArticleExtractor()

    try:
        content = extractor.get_content_from_url(url)
        lines=content.splitlines()
        table =[] 
        for i in lines:
            if i.strip():
                dataframe=[url,i]
                table.append(dataframe)
        rowcount=int(countersheet.acell('A2').value)
        num=len(table)
        rangeTop="A"+str(rowcount+1)
        rangeBot="B"+str(rowcount+num)
        
        print(rangeTop)
        print(rangeBot)
        Trange= rangeTop+":"+rangeBot
        
        currentSheet.batch_update([{
        'range': Trange,
        'values': table
        }])
        countersheet.update('A2',str(num+rowcount))
        
        #currentSheet.insert_row(dataframe,1)
        
        
    except:
        article= Article(url)
        article.download()
        article.parse()
        text = article.text
        lines=text.splitlines()
        table =[] 
        for i in lines:
            if i.strip():
                dataframe=[url,i]
                table.append(dataframe)
        rowcount=int(countersheet.acell('A2').value)
        num=len(table)
        rangeTop="A"+str(rowcount+1)
        rangeBot="B"+str(rowcount+num)
        
        print(rangeTop)
        print(rangeBot)
        Trange= rangeTop+":"+rangeBot
        
        currentSheet.batch_update([{
        'range': Trange,
        'values': table
        }])
        countersheet.update('A2',str(num+rowcount))

def mongoConnect(urlstring):
    cluster = MongoClient("mongodb+srv://test:test@cluster0.wxh7d.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db= cluster["UrlDB"]
    collection = db ["url"]

    if urlstring == "getallurl":
        listurl=[]
        for x in collection.find():
            urllist=[(k,v) for k, v in x.items()]
            listurl.append(urllist[1][1])
        
        return listurl
        
        
    else:    
        result= collection.find_one({"url": urlstring})
        if result is None:
            collection.insert_one({"url":urlstring})
            scrapeData(urlstring)
            return True
           
        else:
            return False


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
    flag = mongoConnect(url)
    if flag ==True :
        return "Done"
    else:
        return "URL Already There !!"

@app.route("/urllist", methods=['GET'])
@cross_origin(supports_credentials=True)
def urllist():
    listurl= mongoConnect("getallurl")
    return jsonify(listurl)



if __name__=="__main__":
    app.run()
from elasticsearch import Elasticsearch
from flask import Flask, jsonify, url_for
from flask import request, redirect, render_template, session
import requests
import base64
import requests
import json
from luqum.parser import parser
from luqum.elasticsearch import ElasticsearchQueryBuilder

app = Flask(__name__)
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route('/adult', methods=["GET", "POST"])
def adult():
    return render_template("adult.html")


@app.route('/child', methods=["GET", "POST"])
def child():
    return render_template("child.html")


@app.route('/pipe', methods=["GET", "POST"])
def pipe():
    data = request.form.get("data")
    childD = request.form.get("child")
    print(childD)
    payload = {}
    headers = {}
    url = "http://127.0.0.1:4000/autocomplete?query=" + str(data) + "&child=" + str(childD)
    print("URL", end=" ")
    print(url)
    response = requests.get(url, headers=headers, data=payload)
    print("response", end=" ")
    print(response.text)
    return response.text


@app.route('/getData', methods=["POST", "GET"])
def getData():
    data = request.form["inp"]
    try:
        base = {
            "query": {
                "match": {
                    "title": data
                }
            }
        }
        NODE_NAME = 'netflix'
        res = es.search(index=NODE_NAME, body=base)
        print(res)
        if len(res['hits']['hits']) != 0:
            for i in res['hits']['hits']:
                movieUrl = "http://localhost:9200/netflix/video/" + str(i['_id'])
                movieMap = {'url':movieUrl, 'name':data}
                return render_template('child.html', value=movieMap)
        else:
            return render_template('child.html', error="No video with requested name!!")
    except:
        return render_template('child.html', error="Please check the title you have provided!!")


@app.route('/getPage', methods=["POST", "GET"])
def getPage():
    if request.method == "POST":
        try:
            size = int(request.form["inp1"])
            num = int(request.form["inp2"])
            typeP = request.form["type"]
            print(str(size)+" "+str(num)+" "+typeP)
            query = {
                "sort": [
                    {"release_year": {"order": "desc"}},
                    "_score"
                ],
                "size": 10000,
                "query": {
                    "match": {
                        "type": typeP
                    }
                }
            }
            res = es.search(index='netflix', body=query)
            print("Res", end=" ")
            print(res)
            min = size*(num-1)+1
            max = size*num
            if len(res['hits']['hits'])>min and len(res['hits']['hits'])>max:
                movieList = []
                for i in res['hits']['hits'][min:max+1]:
                    movieUrl = "http://localhost:9200/netflix/video/" + str(i['_id'])
                    movieMap = {'url':movieUrl, 'name':i['_source']['title'], 'year':i['_source']['release_year']}
                    movieList.append(movieMap)
                    print("opti", end=" ")
                    print(str(movieMap))
                return render_template('paging.html', value=movieList)
            elif min < len(res['hits']['hits']) < max:
                movieList = []
                for i in res['hits']['hits'][min:]:
                    movieUrl = "http://localhost:9200/netflix/video/" + str(i['_id'])
                    movieMap = {'url':movieUrl, 'name':i['_source']['title'], 'year':i['_source']['release_year']}
                    movieList.append(movieMap)
                return render_template('paging.html', value=movieList)
            else:
                return render_template('paging.html', error="Size exceeded or so!!")
        except:
            return render_template('paging.html', error="Size exceeded or so!!")
    else:
        return render_template('paging.html')


@app.route('/custom', methods=["POST", "GET"])
def custom():
    return render_template('custom.html')


@app.route('/customField', methods=["POST", "GET"])
def customField():
    if request.method == "POST":
        option = request.form["opt"]
        value = request.form["inp"]
        query = {
            "size": 10000,
            "query": {
                "match": {
                    option: {
                        "query": value,
                        "operator": "and"
                    }
                }
            }
        }
        res = es.search(index='netflix', body=query)
        print("Res", end=" ")
        print(res)
        if len(res['hits']['hits']) != 0:
            customRes = []
            for i in res['hits']['hits']:
                movieUrl = "http://localhost:9200/netflix/video/" + str(i['_id'])
                movieTitle = i['_source']['title']
                movieOpt = i['_source'][option]
                movieMap = {'url': movieUrl, 'name': movieTitle, 'option':option, 'optVal':movieOpt}
                customRes.append(movieMap)
            return render_template('customField.html', value=customRes)
        else:
            return render_template('customField.html', error="No! Search for something else")
    return render_template('customField.html')


@app.route('/customPre', methods=["POST", "GET"])
def customPre():
    if request.method == "POST":
        descr = request.form["inp"]
        query = {
            "size": 10000,
            "query": {
                "match_phrase_prefix": {
                  "description": {
                    "query": descr
                  }
                }
            }
        }
        res = es.search(index='netflix', body=query)
        print("Res", end=" ")
        print(res)
        if len(res['hits']['hits'])!=0:
            movieList = []
            for i in res['hits']['hits']:
                movieUrl = "http://localhost:9200/netflix/video/" + str(i['_id'])
                movieMap = {'url': movieUrl, 'name': i['_source']['title'], 'description': i['_source']['description']}
                movieList.append(movieMap)
                print("descr", end=" ")
                print(str(movieMap))
            return render_template('customPre.html', value=movieList)
        else:
            return render_template('customPre.html', error="Size exceeded or so!!")
    else:
        return render_template('customPre.html')


@app.route('/genre', methods=["POST","GET"])
def genre():
    if request.method == "POST":
        genreText = request.form["inp"]
        genreText = genreText.replace(" and ", " AND ").replace(" or ", " OR ")
        wordL = []
        temp = ""
        print(genreText.split(' '))
        for word in genreText.split(' '):
            if word == "AND" or word == "OR":
                if temp != "": wordL.append("\"" + temp + "\"")
                wordL.append(word)
                temp =""
            elif word == '(' or word == ')':
                if temp != "": wordL.append("\"" + temp + "\"")
                wordL.append(word)
                temp = ""
            else:
                temp = word + " "
        if temp != "": wordL.append("\"" + temp + "\"")
        str1 = " "
        print(wordL)
        genreText = str1.join(wordL)
        print(genreText)
        try:
            tree = parser.parse(genreText)
            es_builder = ElasticsearchQueryBuilder()
            boolQuery = str(es_builder(tree))
            print(str(boolQuery))
            boolQuery = boolQuery.replace("'", '"').replace("match_phrase","match").replace("match", "match_phrase_prefix")
            print(str(boolQuery))
            boolQuery = boolQuery.replace("text", "listed_in")
            print(str(boolQuery))
            queryStr = "{\"size\":10000,\"query\":"+boolQuery+"}"
            print(str(boolQuery))
            print(queryStr)
            res = es.search(index='netflix', body=queryStr)
            print("Res", end=" ")
            print(res)
            if len(res['hits']['hits'])!=0:
                movieList = []
                for i in res['hits']['hits']:
                    movieUrl = "http://localhost:9200/netflix/video/" + str(i['_id'])
                    movieMap = {'url': movieUrl, 'name': i['_source']['title'], 'listed_in': i['_source']['listed_in']}
                    movieList.append(movieMap)
                    print("genre", end=" ")
                    print(str(movieMap))
                return render_template('genre.html', value=movieList)
            else:
                return render_template('genre.html', value="Size exceeded or so!!")
        except:
            print("Spaces please")
            return render_template('genre.html', error="Size exceeded or so!!")
    else:
        return render_template('genre.html')


if __name__ == "__main__":
    app.run(debug=True, port=5000)

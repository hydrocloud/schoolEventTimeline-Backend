import flask
import gevent.pywsgi
import pymongo
import requests
import json
import ctypes

utils = ctypes.CDLL("./utils.so")
utils.init()

utils.zhixue_pw_encode.argtypes = [ctypes.c_char_p]
utils.zhixue_pw_encode.restype = ctypes.c_char_p

targetDb = pymongo.MongoClient().HydroCloud_EventTimeline

app = flask.Flask(__name__)

@app.route("/login/zhixue", methods = ["POST"])
def onZhixueLogin():
    resp = flask.Response("Unknown error")
    resp.headers["Access-Control-Allow-Origin"] = "*";

    try:
        req_data = json.loads(flask.request.get_data())
    except ValueError:
        resp.set_data("Unable to parse request")
        return resp

    if req_data == None:
        resp.set_data("Bad request data")
        return resp
    
    login_name = req_data["loginName"]
    pw = req_data["password"]

    if login_name == None or pw == None:
        resp.set_data("Bad arguments")
        return resp

    encoded_pw = utils.zhixue_pw_encode(pw)
    utils.free_memory()

    if encoded_pw == None:
        resp.set_data("Illegal password")
        return resp

    post_data = {
        "loginName": login_name,
        "password": encoded_pw,
        "description": "{'encrypt':['password']}"
    }

    post_headers = {
        "authbizcode": "0001",
        "authguid": "11da01c3-a738-464d-ade2-58f5d97a14c6",
        "authtimestamp": "1476610394830",
        "authtoken": "08d558fedeeaaa299fd5920090175302"
    }

    zx_resp = requests.post("http://www.zhixue.com/container/app/login", data = post_data)
    
    try:
        zx_resp_json = json.loads(zx_resp.text)
    except ValueError:
        resp.set_data("Unable to parse zhixue response")
        return resp
    
    if zx_resp_json["errorCode"] != 0:
        resp.set_data("Error code: " + str(zx_resp_json["errorCode"]))
        return resp
    
    resp_json = {
        "token": zx_resp_json["result"]["token"]
    }

    resp.set_data(json.dumps(resp_json))

    return resp

@app.route("/exams/list", methods = ["POST"])
def onExamList():
    resp = flask.Response("Unknown error")
    resp.headers["Access-Control-Allow-Origin"] = "*";

    req_data = json.loads(flask.request.get_data())

    token = req_data["token"]

    req_args = {
        "pageIndex": "1",
        "pageSize": "2147483647",
        "token": token,
        "version": "1.1"
    }

    zx_resp = requests.get("http://app.zhixue.com/study/report/get/exam/list", params = req_args)

    zx_resp_json = json.loads(zx_resp.text)

    if zx_resp_json["errorCode"] != 0:
        resp.set_data("Error code: " + str(zx_resp_json["errorCode"]))
        return resp
    
    resp_json = []

    for item in zx_resp_json["result"]:
        new_item = {
            "time": item["examCreateDateTime"],
            "id": item["examId"],
            "name": item["examName"],
            "score": item["score"],
        }

        resp_json.append(new_item)
    
    resp.set_data(json.dumps(resp_json))

    return resp

@app.route("/exams/details", methods = ["POST"])
def onExamDetails():
    resp = flask.Response("Unknown error")
    resp.headers["Access-Control-Allow-Origin"] = "*";

    req_data = json.loads(flask.request.get_data())

    token = req_data["token"]

    req_data = {
        "examId": req_data["examId"],
        "token": token
    }

    zx_resp = requests.post("http://app.zhixue.com/study/report/exam/getScoreAndRank", data = req_data)
    
    zx_resp_json = json.loads(zx_resp.text)

    resp_json = []

    for subject in zx_resp_json["result"]["userExamData"]:
        new_subject = {
            "name": subject["subjectName"],
            "score": subject["score"],
            "details": {
                "class": {
                    "rank": subject["classRank"]["rank"],
                    "total": subject["classRank"]["totalNum"],
                    "average": subject["classRank"]["avgScore"],
                    "highest": subject["classRank"]["highScore"]
                },
                "grade": {
                    "msg": "Not implemented"
                }
            }
        }
        resp_json.append(new_subject)

    resp.set_data(json.dumps(resp_json))

    return resp

if __name__ == "__main__":
    gevent_server = gevent.pywsgi.WSGIServer(("",6096), app)
    gevent_server.serve_forever()
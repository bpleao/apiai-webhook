# -*- coding: utf-8 -*-
#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

import random
import pickle

# Flask app should start in global layout
app = Flask(__name__)

with open("webhook_pickle.p", "rb") as p:
    responseDict = pickle.load(p)
print(responseDict[(u'definir', u'conceito:Deus')][0])
#responseDict = {
#(u"definir",u"conceito:Deus"):["1. Que é Deus? Deus é a inteligência suprema, causa primária de todas as coisas."]
#}

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def findBestKey(intent, entities):
    intentList = [intent]
    t = tuple(intentList + sorted(entities))
    if t in responseDict.keys():
        return t
    # find length of intersection with entity list in each key, only if entity is the same
    nIntersect = [len(set(entities).intersection(set(list(k)[1:]))) if list(k)[0] == intent else 0 for k in responseDict.keys()]
    maxIntersect = max(nIntersect)
    if maxIntersect == 0:
        return None
    intersectKeys = [k for k,n in zip(responseDict.keys(),nIntersect) if n == maxIntersect]
    return random.sample(intersectKeys,1)[0]
    
def processRequest(req):
    result = req.get("result")
    if result.get("action") != "getSpiritsBookResponse":
        return {}
    
    entities = []
    parameters = result.get("parameters")
    for name in parameters:
        if isinstance(parameters[name],list):
            for value in parameters[name]:
                entities.append(":".join([name,value]))
        else:
            # composite values are not provided as lists
            if len(parameters[name]) > 0:
                entities.append(name)
    intent = result.get("metadata").get("intentName")
    
    k = findBestKey(intent, list(set(entities)))
    print(k)
    
    if k is not None:
        answer = random.sample(responseDict[k],1)[0]
    else:
        answer = "Desculpe, não entendi. Por favor faça outra pergunta."
    
    print("Response:")
    print(answer)

    return {
        "speech": answer,
        "displayText": answer,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-webhook"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')

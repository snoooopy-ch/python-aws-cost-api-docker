# app.py - a minimal flask api using flask_restful
#os.environ['LD_LIBRARY_PATH'] = "my_path"
#export AWS_ACCESS_KEY_ID=your_access_key_id
#export AWS_SECRET_ACCESS_KEY=your_secret_access_key

from flask import Flask,request,jsonify, json
from subprocess import Popen, PIPE
import os
import subprocess
import logging
import urllib
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/")
def home():
    return {'hello': 'world'}

@app.route('/api/v1/cost', methods=['POST'])
def get_cost_post():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    
    if 'key' in request.json:
        key=request.json['key']
        os.environ['AWS_ACCESS_KEY_ID']=key
    else:
        return "Error: No key field provided. Please specify an AWS_ACCESS_KEY_ID."
    
    if 'secret' in request.json:
        secret=request.json['secret']
        os.environ['AWS_SECRET_ACCESS_KEY']=secret

    else:
        return "Error: No secret field provided. Please specify an AWS_SECRET_ACCESS_KEY."

    if 'cluster_id' in request.json:
        cluster_id=request.json['cluster_id']
    else:
        return "Error: No cluster_id field provided. Please specify an cluster_id."
    
    return calculating_cost(cluster_id)

def calculating_cost(cluster_id):
    proc = subprocess.Popen(["aws", "configure"], 
                                stdin=subprocess.PIPE, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE,
                                encoding='utf8')
    try:
        stdout, stderr = proc.communicate(input=os.environ['AWS_ACCESS_KEY_ID'] + '\n' +
                                        os.environ['AWS_SECRET_ACCESS_KEY'] + '\n' +
                                        'us-east-1\n' + 
                                        'json\n')
        
        proc = subprocess.Popen(["aws-emr-cost-calculator2",  "cluster", "--cluster_id=" + cluster_id], 
                                stdin=subprocess.PIPE, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE,
                                encoding='utf8')
        stdout, stderr = proc.communicate()
        proc.wait()
        
        if not stdout:
            return stderr
        else:
            data_set = {}
            items = stdout.split('\n')
            
            for item in items:
                fields = item.split(':')

                if len(fields) == 2:
                    fields[0] = fields[0].strip().replace('.', '_')
                    fields[1] = fields[1].strip()
                    data_set[fields[0]] = fields[1]
                
            return json.dumps(data_set)
        
    except subprocess.CalledProcessError:
        proc.kill()
        return 'Command exited with non-zero code'
    
@app.route('/api/v1/conversation_results', methods=['POST'])
def conversation_results():
    if 'code' in request.json:
        code=request.json['code']
    else:
        return "Error: No key field provided. Please specify an code."
    
    token = conversation_token(code)
    job_id = conversation_jobs(token)
    result = conversation_results(token, job_id)
    
    return result

@app.route('/api/v1/token', methods=['POST'])
def get_token():
    if 'code' in request.json:
        code=request.json['code']
    else:
        return "Error: No key field provided. Please specify an code."
    return conversation_token(code)

@app.route('/api/v1/jobid', methods=['POST'])
def get_job_id():
    if 'code' in request.json:
        code=request.json['code']
    else:
        return "Error: No key field provided. Please specify an code."
    
    token = conversation_token(code)
    return conversation_jobs(token)

@app.route('/api/v1/results', methods=['POST'])
def get_results():
    if 'cloud_token' in request.json:
        token=request.json['cloud_token']
    else:
        return "Error: No key field provided. Please specify an cloud_token."
    
    if 'job_id' in request.json:
        job_id=request.json['job_id']
    else:
        return "Error: No key field provided. Please specify an job_id."
    
    return conversation_results(token, job_id)

def conversation_token(code):
    url = "https://login.mypurecloud.com/oauth/token"
    payload = {
        "grant_type": "client_credentials"
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + code
    }
    
    response = requests.post(url, data=payload, headers=headers).json()
    return response.access_token
  
def conversation_jobs(token):
    url = "https://api.mypurecloud.com/api/v2/analytics/conversations/details/jobs"
    payload = "{'interval': '2020-05-30T00:00:00.000Z/2020-06-01T20:00:00.000Z'}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': token
    }
    response = requests.request("POST", url, headers=headers, data = payload).json()
    return response.jobId

def conversation_results(token, job_id):
    url = "https://api.mypurecloud.com/api/v2/analytics/conversations/details/jobs/" + job_id + "/results"
    payload = {}
    headers = {
        'Authorization': 'bearer ' + token
    }
    
    response = requests.request("GET", url, headers=headers, data = payload).json()
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
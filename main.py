from flask import render_template, request, jsonify, redirect, make_response
import requests
import json
import logging
from flask import Flask
DEBUG = False
PORT_NUMBER = 5077

app = Flask(__name__)


code = 'unknown'
next = 'unknown'
token = 'unknown'

@app.route("/")
def home():
    return "Hello, this is the main page"



@app.route('/index')
def index():
    return render_template('frontend/index.html')

@app.route('/help')
def help():
    return render_template('frontend/help.html')

@app.route('/support')
def support():
    return render_template('frontend/support.html')

@app.route('/faq')
def faq():
    return render_template('frontend/FAQ.html')

@app.route('/form')
def form():
    return render_template('frontend/form.html')

@app.route('/termsofservices')
def termsofservices():
    return render_template('frontend/termsofservices.html')

@app.route('/privacy')
def privacy():
    return render_template('frontend/privacy.html')

@app.route('/blog')
def blog():
    return render_template('frontend/blog.html')

@app.route('/contact')
def contact():
    return render_template('frontend/contact.html')

@app.route('/aboutus')
def aboutus():
    return render_template('frontend/aboutus.html')

@app.route('/logs', methods=['POST'])
def logs():
    url = "http://ec2-34-218-241-190.us-west-2.compute.amazonaws.com:50150/logs/vercel_drain"
    try:
        response = requests.post(url) # if request is GET replace post with get
        data = response.text # response have multiple attributes can be converted to text or can do other processing if required
    except:
        return "No response from {}".format(url)
    return "Hello some logs response returned from the amazon server!"


@app.route('/vercel/drain', methods=['GET', 'POST'])
def versal_drain():
    url = "http://ec2-34-218-241-190.us-west-2.compute.amazonaws.com:50150/logs/vercel_drain"
    payload = {}
    try:
        response = requests.post(url, data = payload)
        data = response.text
        logging.info('data is %s' %(response))
    except:
        return make_response("No response from {}".format(url), 400)
    return jsonify(message='Hello some response returned from the amazon server!')


@app.route('/vercel/callback', methods=['GET', 'POST'])
def versal_callback():
    #fmt = getattr(settings, 'LOG_FORMAT', None)
    #lvl = getattr(settings, 'LOG_LEVEL', logging.INFO)
    #logging.basicConfig(format=fmt, level=lvl)
    username = request.args.get('Username')
    start_date = request.args.get('startDate')
    body = request.data
    method = request.method
    path = request.path
    full_path = request.full_path
    path_info = request.path
    content_params = request.args

    global code
    global next
    global token
    if method == 'GET':
        code = request.args.get("code", None)
        next = request.args.get("next", None)
        logging.info('request received at versal_callback: %s username: %s '
        'start_date: %s body: %s code: %s next: %s path: %s path_info: %s '
        'method: %s content_params: %s full_path: %s'
                     % (request, username, start_date, body, code, next,
                        path, path_info, method, content_params, full_path))
        logging.info('request received at versal_callback: %s username: %s '
                     'start_date: %s body: %s code: %s next: %s path: %s path_info: %s '
                     'method: %s content_params: %s full_path: %s'
                     % (request, username, start_date, body, code, next,
                        path, path_info, method, content_params, full_path))
        if ((code == None) | (next == None)):
            logging.info('GET request without code or next parameters: %s' % (request.args))
            return "Hello from vercel_callback!"
        else:
            logging.info('GET request with parameters code: %s next=%s' % (code, next))
            return render_template('frontend/form.html')
    elif method == 'POST':
        logging.info('POST request received: %s' % (request.args))
        global token
        token = getToken(code)
        if token and body is not None:
            createLogDrain(token, body)
            logging.info("done with integration")
            s = requests.get(next)
            return redirect(next)
    else:
        logging.debug('unsupported method reqeived: %s' % (method))
        return "400 bad request"


def getToken(code):
    redirect_uri = '/vercel/drain'
    client_id = 'oac_GlZWYfLVpQS0TWIGoLYDLx5I'
    client_secret = 'Sj3qzukpSo6mo5ogmuaccc4r'
    url = 'https://api.vercel.com/v2/oauth/access_token'

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_url": redirect_uri
    }

    res = requests.post(url, headers=headers, data=data, verify=False)
    res_in_json = json.loads(res.text)
    token = res_in_json["access_token"]
    token_type = res_in_json["token_type"]
    logging.info('token found from response body: %s token type: %s' % (token, token_type))
    return token

def createLogDrain(token, body):
    url2 = 'https://api.vercel.com/v1/integrations/log-drains'
    name = 'cloudvista-logdrain'
    method = 'post'
    header = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {token}",
    }
    req_body1 = {'name': name, 'type': header, 'url': url2}
    body_json1 = json.dumps(req_body1)
    bodystr = json.loads(body_json1)
    resp = requests.post(url2, headers=header, data=bodystr, verify=False)
    logging.debug('Log drain body is:  %s' % (bodystr))


if __name__ == "__main__":
    app.run(debug=DEBUG, port=PORT_NUMBER)

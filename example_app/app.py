from flask import Flask, session, request, redirect, url_for, render_template
import json
from flask_oauthlib.client import OAuth
import requests
from urllib import urlencode
from os import environ

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'

CLIENT_ID=environ.get("CLIENT_ID")
if not CLIENT_ID:
    raise Exception("missing client id!")

app.config.SERVER_NAME = 'obscure-depths-35394.herokuapp.com'

@app.route("/")
def hello():
    # normally here you'd fetch the existing refresh_token/access_token pair
    # but because we have none, we automatically go to login
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if "shop" in request.args:
        # you can either use the /admin/apps url, or https://www.shopifysubscriptions.com/auth/authorize
        return redirect("https://{}/admin/apps/shopify-recurring-payments/partners/app/{}/install".format(request.args["shop"], CLIENT_ID))
    else:
        return render_template("shop_login.html")

@app.route('/auth/callback')
def callback():
    code = request.args.get("code")
    if code:
        access_token = _exchange_auth_code_for_token(code)

        # now that we have a valid access_token, get some data
        merchant_info = requests.get("https://api.rechargeapps.com/", headers={"Authorization": "Bearer {}".format(access_token)})
        return merchant_info.content, merchant_info.status_code

    return "doing it wrong"

def _exchange_auth_code_for_token(code):
    required_params = {"code": code,
            "client_id": CLIENT_ID,
            "redirect_uri": url_for("callback", _external=True),
            "state": "0xdeadbeef",
            "grant_type": "authorization_code"}

    response = requests.post("https://shopifysubscriptions.com/oauth/token?{}".format(urlencode(required_params)))
    response.raise_for_status()
    # save this and the refresh token
    access_token = json.loads(response.content)["access_token"]
    return access_token

# unlike in the above example, if you have a refresh_token you can exchange it for an access_token here:
def _exchange_refresh_token_for_access_token(refresh_token):
    required_params = {"grant_type": "refresh_token",
            "scope": "all",
            "client_id": CLIENT_ID,
            "refresh_token": refresh_token}

    response = requests.post("https://shopifysubscriptions.com/oauth/token?{}".format(urlencode(required_params)))
    response.raise_for_status()
    # save this and the refresh token
    access_token = json.loads(response.content)["access_token"]
    return access_token

if __name__ == "__main__":
    app.run()

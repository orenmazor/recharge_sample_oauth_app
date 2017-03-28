from flask import Flask, session, request, redirect, url_for, render_template
from flask_oauthlib.client import OAuth
import requests

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'

CLIENT_ID="6c15ad4ac7fd68f656cb53b5320378ea64d488437c9764840b3fd650"
app.config.SERVER_NAME = 'obscure-depths-35394.herokuapp.com'

@app.route("/")
def hello():
    if 'recharge_token' in session:
        me = recharge.get('/api')
        return jsonify(me.data)
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if "shop" in request.args:
        auth_params = {"scope": "all",
                "client_id": CLIENT_ID,
                "state": "0xdeadbeef",
                "response_type":"code",
                "redirect_uri": url_for("callback")}

        return redirect("https://{}/admin/apps/shopify-recurring-payments/oauth/authorize?{}".format(request.args["shop"], auth_params))
    else:
        return render_template("shop_login.html")

@app.route('/auth/callback')
def callback():
    if "code" in request.args:
        code = request.args.get("code")
        # TODO handle the scope with session
        response = requests.post("https://api.rechargeapps.com/oauth/token?code={}&client_id={}&state=0xdeadbeef&redirect_uri={}&grant_type=authorization_code".format(code, CLIENT_ID, url_for("callback")))

        # save this and the refresh token
        access_token = json.loads(response.json)["access_token"]

        response = requests.get("https://api.rechargeapps.com/", headers={"X-Recharge-Access-Token": access_token})
        return response

    return "wrong"

if __name__ == "__main__":
    app.run()

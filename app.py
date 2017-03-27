from flask import Flask, session, request, redirect, url_for, render_template
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'

CLIENT_ID="6c15ad4ac7fd68f656cb53b5320378ea64d488437c9764840b3fd650"

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

        return redirect("https://{}/admin/apps/shopify-recurring-payments/oauth/authorize?{}".format(request.args["shop"], auth_params)
    else:
        return render_template("shop_login.html")

@app.route('/auth/callback')
def callback():
    return "ok"

if __name__ == "__main__":
    app.run()

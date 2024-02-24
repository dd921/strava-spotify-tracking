#!flask/bin/python
import logging
from flask import Flask, jsonify, redirect, render_template, request, url_for
from stravalib import Client
import yaml
app = Flask(__name__)
# app.config.from_envvar("APP_SETTINGS")

with open('~/strava-spotify-tracking/access_tokens/config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Access the configuration data
client_id = config['STRAVA_API']['client_id']
client_secret = config['STRAVA_API']['client_secret']
redirect_uri = config['STRAVA_API']['redirect_uri']

@app.route("/")
def login():
    c = Client()
    url = c.authorization_url(
        client_id=client_id,
        redirect_uri=url_for(".logged_in", _external=True),
        approval_prompt="auto",
    )
    return render_template("login.html", authorize_url=url)


@app.route("/strava-oauth")
def logged_in():
    """
    Method called by Strava (redirect) that includes parameters.
    - state
    - code
    - error
    """
    
    c = Client()
    error = request.args.get("error")
    state = request.args.get("state")
    if error:
        return render_template("login_error.html", error=error)
    else:
        code = request.args.get("code")
        client = Client()
        access_token = client.exchange_code_for_token(
            client_id=client_id,
            client_secret=config['STRAVA_API']['client_secret'],
            code=code,
        )
        # Probably here you'd want to store this somewhere -- e.g. in a database.
        strava_athlete = client.get_athlete()

        # response = requests.post(token_endpoint, data=payload)
        # response_data = response.json()
        # access_token = response_data['access_token']

        
        return render_template(
            "login_results.html",
            athlete=strava_athlete,
            access_token=access_token,
        )


if __name__ == "__main__":
    app.run(debug=True)
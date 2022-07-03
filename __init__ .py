from flask import Flask, redirect, url_for
import flask
from flask import request
from datetime import datetime
import os
import pathlib
import json
from urllib.request import urlopen
import urllib.request
import requests
from flask import Flask, session, abort, redirect, request
from werkzeug.utils import secure_filename
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import os.path
app = Flask("Google Login App")  #naming our application
app.secret_key = "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"  #it is necessary to set a password when dealing with OAuth 2.0
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  #this is to set our environment to https because OAuth 2.0 only supports https environments
app.config["TEMPLATES_AUTO_RELOAD"] = True
UPLOAD_FOLDER = 'data/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_PATH'] = 1024 * 1024 * 100
GOOGLE_CLIENT_ID = "589724773316-f1ap4c3q7ou8m35rl4q28i5lld528e14.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
#user_id refers to the google_id number
#username refers to the name assosiated with the user_id stored in /data/usernames.txt

flow = Flow.from_client_secrets_file(  #Flow is OAuth 2.0 a class that stores all the information on how we want to authorize our users
	client_secrets_file=client_secrets_file,
	scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],  #here we are specifing what do we get after the authorization
	redirect_uri="http://127.0.0.1:5000/callback"  #and the redirect URI is the point where the user will end up after the authorization
)

def dics_from_file(filename):
	with open(filename) as f:
		data = f.read()
	js = json.loads(data)
	return js

def login_is_required(function):  #a function to check if the user is authorized or not
	def wrapper(*args, **kwargs):
		if "google_id" not in session:
			return abort(401)
		else:
			return function()

	return wrapper
	
def logged_in():#checks if user is logged in
    if "google_id" in session:
        return True
    else:
        return False
		

@app.route("/login_google")  #the page where the user can login
def login():
	authorization_url, state = flow.authorization_url()  #asking the flow class for the authorization (login) url
	session["state"] = state
	return redirect(authorization_url)


@app.route("/callback")  #this is the page that will handle the callback process meaning process after the authorization
def callback():
	flow.fetch_token(authorization_response=request.url)
	
	if not session["state"] == request.args["state"]:
		abort(500)  #state does not match!
	
	credentials = flow.credentials
	request_session = requests.session()
	cached_session = cachecontrol.CacheControl(request_session)
	token_request = google.auth.transport.requests.Request(session=cached_session)

	id_info = id_token.verify_oauth2_token(
		id_token=credentials._id_token,
		request=token_request,
		audience=GOOGLE_CLIENT_ID
	)

	session["google_id"] = id_info.get("sub")  #defing the results to show on the page
	session["name"] = id_info.get("name")
	session["pfp"] = id_info.get("Image URL")
	return redirect("/logging_in")  #the final page where the authorized users will end up


@app.route("/logout")  #the logout page and function
def logout():
	session.clear()
	return redirect("/#top")

@app.route("/")
def index():
	if logged_in() is False:  #authorization required
		signed_out = 'href=/sign_in'
		home = ""
		highlight = ";border-radius:5px"
		sip = f'<a href="/sign_in" style="margin-top:4vh;border-radius:5px;padding:0;height:6vh;margin-top:4vh;height:4vh;"><h2 class="material-symbols-outlined" style="margin-top:.5vh">login</h2><h2>Sign in</h2></a>'
		sorl = "Get started"
		sorll = "/sign_in"
		highlight = "background-color:#0091ff;border-radius:5px"
		becomemember = '<div style="top:32.5vh;position:absolute;text-align:center;width:100%"><h2 style="background: rgba(51, 51, 51, 0.75); border-radius: 10px; padding: 5px">Become a member today</h2></div>'
		return flask.render_template("home.html", sip=sip, signed_out=signed_out, home=home, hh=highlight, sorl=sorl, sorll=sorll, becomemember=becomemember)
	else:
		return redirect(f"/member/{session['google_id']}")

@app.route("/member/<user_id>")
def member(user_id):
	if logged_in() is True:
		pfp = session["pfp"]
		if str(pfp) == "None":
			if os.path.exists(f"/server/flask/static/users/{user_id}/pfp.png"):
				pfp = f"/static/users/{user_id}/pfp.png"
			else:
				if not os.path.exists(f"/server/flask/static/flask/users/{user_id}/pfp.png"):
					pfp = "/static/users/defualt/pfp.png"
		sip = f'<button onclick="dropdown()" class="dropbtn" style="float: right;background-color: transparent;border: transparent;"><a style="margin-top:3vh;border-radius:5px;padding:0;height:6vh;"><img src="{pfp}" alt="pfp" style="border-radius:50%;width:5vh;height:5vh;padding:0;margin:calc(.5vh - 3px);border: solid #0091ff;" class="dropbtn"></a></button>'
		userid = f'/member/{user_id}'
		highlight = "background-color:#0091ff;border-radius:5px"
		hp = "width:6vh"
		sorl = "Suggested workouts"
		sip = f'<button onclick="dropdown()" class="dropbtn" style="float: right;background-color: transparent;border: transparent;"><a style="margin-top:3vh;border-radius:5px;padding:0;height:6vh;{hp};"><img src="{pfp}" alt="pfp" style="border-radius:50%;width:5vh;height:5vh;padding:0;margin:calc(.5vh - 3px);border: solid #0091ff;" class="dropbtn"></a></button>'
		sorll = "/learn"
		home = f"http://127.0.0.1:5000/member/{user_id}"
		return flask.render_template("home.html", sip=sip, userid=userid, hh=highlight, hp=hp, sorl=sorl, sorll=sorll, home=home)
	else:
		return redirect("/#top")


@app.route("/discussion")
def disc():
	if "google_id" in session:
		return redirect(f"/discussion/member/{session['google_id']}")
	else:
		signed_out = 'href=/sign_in'
		sip = f'<a href="/sign_in" style="margin-top:4vh;border-radius:5px;padding:0;height:6vh;margin-top:4vh;height:4vh;"><h2 class="material-symbols-outlined" style="margin-top:.5vh">login</h2><h2>Sign in</h2></a>'
		home= "/"
		highlight = "background-color:#0091ff;border-radius:5px"
		return flask.render_template("disc.html", signed_out=signed_out, sip=sip, home=home, hd=highlight)

@app.route("/discussion/member/<user_id>")
def disc_member(user_id):
	if "google_id" not in session:
		return redirect("/discussion")
	else:
		pfp = session["pfp"]
		if str(pfp) == "None":
			if os.path.exists(f"/server/flask/static/users/{user_id}/pfp.png"):
				pfp = f"/static/users/{user_id}/pfp.png"
			else:
				if not os.path.exists(f"/server/flask/static/flask/users/{user_id}/pfp.png"):
					pfp = "/static/users/defualt/pfp.png"
		sip = f'<button onclick="dropdown()" class="dropbtn" style="float: right;background-color: transparent;border: transparent;"><a style="margin-top:3vh;border-radius:5px;padding:0;height:6vh;"><img src="{pfp}" alt="pfp" style="border-radius:50%;width:5vh;height:5vh;padding:0;margin:calc(.5vh - 3px);border: solid #0091ff;" class="dropbtn"></a></button>'
		pfp = f'<img src="{pfp}" alt="pfp" style="border-radius:50%;width:5vh;height:5vh;padding:0;margin:calc(.5vh - 3px);border: solid #0091ff;">'
		home = f"http://127.0.0.1:5000/member/{user_id}"
		highlight = "background-color:#0091ff;border-radius:5px"
		hp = "width:6vh"
		return flask.render_template("disc.html", sip=sip, user_id=user_id, home=home, hd=highlight, hp=hp)

@app.route("/res", methods=['POST'])
def res():
	projectpath = request.form['projectFilepath']
	now = datetime.now()
	time = now.strftime("%H:%M:%S")
	f = open("form.txt", "r+")
	f.write(f"{time}: {projectpath}<br>")
	f.close()
	return flask.render_template("form.html")
@app.route("/form")
def form():
	return flask.render_template("form.html")


@app.route("/comments")
def comments():
	f = open("templates/comments.html", "r+")
	cont = f.read()
	f.close()
	return flask.render_template("comments.html")

@app.route("/send_comment", methods=['POST'])
def send_comment():
	projectpath = request.form['projectFilepath']
	now = datetime.now()
	time = now.strftime("%H:%M:%S")
	f = open("templates/comment.html", "a")
	f.write(f"[{time}] <b>{user_id}</b>: {projectpath}<br>")
	f.flush()
	f.close()
	return redirect("comments", code=302)

@app.route("/comment")
def comment():
	return flask.render_template("comment.html")

@app.route("/about")
def about():
	return redirect("/#about")

@app.route("/about/member/<user_id>")
def about_member(user_id):
	return redirect("/#about")

@app.route("/contact")
def contact():
	f = open("templates/contact.html", "r+")
	cont = f.readlines()
	signed_out = 'href=/sign_in'
	sip = f'<a href="/sign_in" style="margin-top:4vh;border-radius:5px;padding:0;height:6vh;margin-top:4vh;height:4vh;"><h2 class="material-symbols-outlined" style="margin-top:.5vh">login</h2><h2>Sign in</h2></a>'
	return flask.render_template("base.html", cont=cont, signed_out=signed_out, sip=sip)

@app.route("/contact1")
def cont1():
	cont = "test"
	return flask.render_template('base.html', cont=cont)

@app.route("/sign_in")
def sign_in():
	if "google_id" in session:
		return redirect(f"/profile/member/{session['google_id']}")
	signed_out = 'href=/sign_in'
	home = "/"
	highlight = "background-color:#0091ff;border-radius:5px"
	sip = f'<a href="/sign_in" style="margin-top:4vh;border-radius:5px;padding:0;height:6vh;margin-top:4vh;height:4vh;"><h2 class="material-symbols-outlined" style="margin-top:.5vh">login</h2><h2>Sign in</h2></a>'
	return flask.render_template("sign_in.html", signed_out=signed_out, home=home, sip=sip, hp=highlight)

@app.route("/new_account/<user_id>")
def new_account(user_id):
	f = open("data/usernames.txt")
	usernames = f.read()
	if session["google_id"] != user_id:
		return redirect("/#top")
	else:
		if "google_id" not in session:
			return redirect("/#top")
		if user_id in usernames:
			return redirect("/#top")
		if session["google_id"] not in usernames:
			return flask.render_template("new_account.html", user_id=user_id)

@app.route("/send_new_account/<user_id>", methods=['POST'])
def send_new_account(user_id):
	if user_id != session["google_id"]:
		return redirect("/#top")
	else:
		projectpath = request.form['projectFilepath']
		f = open("data/usernames.txt", "r+")
		projectpath = projectpath.replace(" ", "_")
		name = f.read()
		name = str(name).replace("}", f', "{user_id}": "{projectpath}"')
		name = name + "}"
		f.close()
		f = open("data/usernames.txt", "w+")
		f.write(name)
		f.close()
		os.system(f"mkdir data/{user_id}")
		os.system(f"touch data/{user_id}/bio.html")
		return redirect("/#top", code=302)


@app.route("/sign_in_button")
def sign_in_button():
	return flask.render_template("sign_in_button.html")

@app.route("/learn")
def learn():
	if "google_id" in session:
		return redirect(f"/learn/member/{session['google_id']}")
	else:
		signed_out = 'href=/sign_in'
		sip = f'<a href="/sign_in" style="margin-top:4vh;border-radius:5px;padding:0;height:6vh;margin-top:4vh;height:4vh;"><h2 class="material-symbols-outlined" style="margin-top:.5vh">login</h2><h2>Sign in</h2></a>'
		home = "/"
		highlight = "background-color:#0091ff;border-radius:5px"
		return flask.render_template("learn.html", sip=sip, signed_out=signed_out, home=home, hl=highlight)

@app.route("/learn/member/<user_id>")
def learn_member(user_id):
	if "google_id" not in session:
		return redirect("/learn")
	else:
		pfp = session["pfp"]
		if str(pfp) == "None":
			if os.path.exists(f"/server/flask/static/users/{user_id}/pfp.png"):
				pfp = f"/static/users/{user_id}/pfp.png"
			else:
				if not os.path.exists(f"/server/flask/static/flask/users/{user_id}/pfp.png"):
					pfp = "/static/users/defualt/pfp.png"
		sip = f'<button onclick="dropdown()" class="dropbtn" style="float: right;background-color: transparent;border: transparent;"><a style="margin-top:3vh;border-radius:5px;padding:0;height:6vh;"><img src="{pfp}" alt="pfp" style="border-radius:50%;width:5vh;height:5vh;padding:0;margin:calc(.5vh - 3px);border: solid #0091ff;" class="dropbtn"></a></button>'
		pfp = f'<img src="{pfp}" alt="pfp" style="border-radius:50%;width:5vh;height:5vh;padding:0;margin:calc(.5vh - 3px);border: solid #0091ff;">'
		highlight = "background-color:#0091ff;border-radius:5px"
		hp = "width:6vh"
		home = f"http://127.0.0.1:5000/member/{user_id}"
		return flask.render_template("learn.html", sip=sip, user_id=user_id, hl=highlight, hp=hp, home=home)



@app.route("/logging_in")
@login_is_required
def logging_in():
	if "google_id" not in session:
		return redirect("/#top")
	else:
		ID = session['google_id']
		f = open("data/usernames.txt")
		usernames = f.read()
		if ID not in usernames:
			return redirect(f"/new_account/{ID}")
		else:
			user_id = str(session['name']).replace(" ", "_")
			return redirect(f"/member/{ID}", code=302)

@app.route("/profile")
def profile():
	if "google_id" in session:
		return redirect(f"/profile/member/{session['google_id']}")
	else:
		return redirect("sign_in")
@app.route("/profile/member/<user_id>")
def profile_member(user_id):
	if "google_id" not in session:
		return redirect("/profile")
	else:
		pfp = session["pfp"]
		if str(pfp) == "None":
			if os.path.exists(f"/server/flask/static/users/{user_id}/pfp.png"):
				pfp = f"/static/users/{user_id}/pfp.png"
			else:
				if not os.path.exists(f"/server/flask/static/flask/users/{user_id}/pfp.png"):
					pfp = "/static/users/defualt/pfp.png"
		sip = f'<button onclick="dropdown()" class="dropbtn" style="float: right;background-color: transparent;border: transparent;"><a style="margin-top:3vh;border-radius:5px;padding:0;height:6vh;"><img src="{pfp}" alt="pfp" style="border-radius:50%;width:5vh;height:5vh;padding:0;margin:calc(.5vh - 3px);border: solid #0091ff;" class="dropbtn"></a></button>'
		home = f"http://127.0.0.1:5000/member/{user_id}"
		highlight = "width:6vh;border-radius:5px"
		usernames = dics_from_file("data/usernames.txt")
		username = usernames[user_id]
		f = open(f"data/{user_id}/bio.html", "r+")
		bio = f.read()
		f.close()
		if bio == "":
			bio = "No bio"
		return flask.render_template("profile.html", sip=sip, user_id=user_id, pfp=pfp, home=home, username=username, bio=bio, hp=highlight)
@app.route(f"/profile/edit/member/<user_id>")
def bio(user_id):
	if "google_id" not in session:
		return redirect("/sign_in")
	else:
		pfp = session["pfp"]
		if str(pfp) == "None":
			if os.path.exists(f"/server/flask/static/users/{user_id}/pfp.png"):
				pfp = f"/static/users/{user_id}/pfp.png"
			else:
				if not os.path.exists(f"/server/flask/static/flask/users/{user_id}/pfp.png"):
					pfp = "/static/users/defualt/pfp.png"
		sip = f'<button onclick="dropdown()" class="dropbtn" style="float: right;background-color: transparent;border: transparent;"><a style="margin-top:3vh;border-radius:5px;padding:0;height:6vh;"><img src="{pfp}" alt="pfp" style="border-radius:50%;width:5vh;height:5vh;padding:0;margin:calc(.5vh - 3px);border: solid #0091ff;" class="dropbtn"></a></button>'
		pfp = f'<img src="{pfp}" alt="pfp" style="border-radius:50%;width:5vh;height:5vh;padding:0;margin:calc(.5vh - 3px);border: solid #0091ff;">'
		home = f"http://127.0.0.1:5000/member/{user_id}"
		highlight = "width:6vh;border-radius:5px"
		usernames = dics_from_file("data/usernames.txt")
		username = usernames[user_id]
		f = open(f"data/{user_id}/bio.html", "r+")
		bio = f.read()
		f.close()
		return flask.render_template("bio.html", sip=sip, user_id=user_id, home=home, username=username, bio=bio, hp=highlight)

@app.route("/edit_bio/<user_id>", methods=['POST'])
def edit_bio(user_id):
	if "google_id" not in session:
		return redirect("/sign_in")
	else:
		projectpath = request.form['projectFilepath']
		f = open(f"data/{user_id}/bio.html", "w")
		f.write(projectpath)
		f.flush()
		f.close()
		return redirect(f"/profile/member/{user_id}", code=302)

@app.route('/uploader', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		user_id = session['google_id']
		f = request.files['file']
		url = request.form["url"]
		if str(f) != "<FileStorage: '' ('application/octet-stream')>":
			f.save(secure_filename(f.filename))
			os.system(f"mkdir static/users/{user_id}")
			f.seek(0)
			f.save(f"static/users/{user_id}/pfp.png")
		else:
			if str(url) != "":
				response = urllib.request.urlretrieve(url)
				response = response[1].get_content_type()
				response = response.split("/")[1]
				urllib.request.urlretrieve(url, f"static/users/{user_id}/pfp.{response}")
				os.system(f"mogrify -format png static/users/{user_id}/pfp.{response}")
			else:
				os.system(f"rm static/users/{user_id}/pfp.png")
		os.system(f"sudo ./aspectcrop -a 1:1 static/users/{user_id}/pfp.png static/users/{user_id}/pfp.png")
		os.system(f"sudo convert static/users/{user_id}/pfp.png -resize 200x200! static/users/{user_id}/pfp.png")
		return redirect("/profile")

@app.route("/discord")
def discord():
	return redirect("https://discord.gg/wjPUaVHZSQ")

if __name__ == "__main__":
	app.run()



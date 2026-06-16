from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash,redirect
from flask_pymongo import PyMongo
from datetime import datetime
import bcrypt


app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["MONGO_URI"] = "mongodb+srv://Nishant:kuchbhi@cluster0.l2oubf7.mongodb.net/flaskdb?retryWrites=true&w=majority"
mongo = PyMongo(app)
users_collection = mongo.db.users



from bson.objectid import ObjectId

@app.route("/save_letter", methods=["POST"])
def save_letter():
    data = request.get_json()
    content = data.get("content")

    # Insert into MongoDB
    result = mongo.db.letters.insert_one({"content": content})

    # Return a URL to view the saved letter
    return jsonify({"url": url_for("view_letter", letter_id=str(result.inserted_id))})

@app.route("/letter/<letter_id>")
def view_letter(letter_id):
    letter = mongo.db.letters.find_one({"_id": ObjectId(letter_id)})
    if not letter:
        return "Letter not found", 404

    return render_template("view_letter.html", content=letter["content"])



@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        # Find user by name
        user = users_collection.find_one({"name": name})

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            session["name"] = user["name"]
            session["email"] = user["email"]
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid user")

    # ✅ Always return something for GET
    return render_template("login.html")

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if user exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for('login'))

        # Hash password before saving
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Insert new user
        users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_pw
        })

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))     

@app.route("/index")
def index():
    if "name" in session:
        return render_template("index.html", user=session["name"])
    return redirect(url_for("login"))     
@app.route("/letters")
def list_letters():
    all_letters = mongo.db.letters.find()
    return render_template("list_letters.html", letters=all_letters)
@app.route("/delete_letter/<letter_id>", methods=["POST"])
def delete_letter(letter_id):
    mongo.db.letters.delete_one({"_id": ObjectId(letter_id)})
    flash("Letter deleted successfully!", "success")
    return redirect(url_for("list_letters"))


if __name__ == "__main__":
    app.run(debug=True)

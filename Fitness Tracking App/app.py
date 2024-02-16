from flask import Flask, render_template, request, redirect, session
from flask_session import Session
import sqlite3
import requests

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
count = 1
name = None
connection = sqlite3.connect("nutrient.db")
cursor = connection.cursor()
key = None

@app.route("/account", methods = ["POST","GET"])
def account():
    global key
    connection = sqlite3.connect("nutrient.db")
    cursor = connection.cursor()
    if request.method =="POST":
        key = request.form.get("name")
        value = request.form.get("pass")
        cursor.execute("INSERT INTO persons (name, password) VALUES(?,?)", (key, value))
        connection.commit()
        return render_template("login.html")
    return render_template("create.html")    

def get_nutrient_info(api_key, food_query):
    base_url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
    
    # Set up the parameters for the API request
    params = {
        'api_key': api_key, 
        'query': food_query,
    }

    # Make the request to the API
    response = requests.get(base_url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
        
        # Check if there are any foods in the response
        if 'foods' in data and len(data['foods']) > 0:
            # Extract nutrient information from the first food item
            nutrient_info = data['foods'][0]['foodNutrients']

            # Extract protein, carbohydrate, fat, and calories
            protein = next((nutrient['value'] for nutrient in nutrient_info if nutrient['nutrientName'] == 'Protein'), None)
            carbohydrate = next((nutrient['value'] for nutrient in nutrient_info if nutrient['nutrientName'] == 'Carbohydrate, by difference'), None)
            fat = next((nutrient['value'] for nutrient in nutrient_info if nutrient['nutrientName'] == 'Total lipid (fat)'), None)
            calories = next((nutrient['value'] for nutrient in nutrient_info if nutrient['nutrientName'] == 'Energy'), None)

            return {
                'food_query': food_query,
                'protein': protein,
                'carbohydrate': carbohydrate,
                'fat': fat,
                'calories': calories
            }
        else:
            return f"No data found for {food_query}"
    else:
        return f"Error: {response.status_code}"

# Replace 'YOUR_API_KEY' with your actual USDA API key
api_key = 'fGBKhhL1WHMqoMPHd6jfho7GPITT74w4ZO4gKdNM'

LIFESTYLES = ["Sedentary lifestyle","Mildly active","Fairly active", "Very active","Extremely active"]
tdeetimes = [1.2,1.375,1.55,1.725,1.9]
BMR = [5]
@app.route("/")
def index():
    if not session.get("name") and not session.get("pass"):
        return redirect("/login")
    return render_template("index.html")

@app.route("/login", methods = ["POST", "GET"])
def login():
    connection = sqlite3.connect("nutrient.db")
    cursor = connection.cursor()
    if request.method == "POST":
        session["name"] = request.form.get("name")
        session["password"] = request.form.get("pass")
        if session["name"] in [b[0] for b in cursor.execute("SELECT name FROM persons")]:
            if session["password"] in [a[0] for a in cursor.execute("SELECT password FROM persons WHERE name = ?", (session["name"],))]:
                if [c[0] for c in cursor.execute("SELECT numbers FROM persons WHERE name = ?", (session["name"],))][0]:
                    return redirect("/tracking")
                return redirect("/")
    connection.commit()
    return render_template("login.html")

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")
@app.route("/create")
def create():
    return render_template("create.html")
@app.route("/bmr")
def bmr():
    connection = sqlite3.connect("nutrient.db")
    cursor = connection.cursor()
    weight = int(request.args.get("weight"))
    height = int(request.args.get("height"))
    age = int(request.args.get("age"))
    gender = request.args.get("gender")
    if gender == "male":
        BMR[0] = 66 + (6.23 * weight * 2.20462) + (12.7 * height *0.393701) - (6.8 * age)
    else:
        BMR[0] = 655 + (4.3 * weight * 2.20462) + (4.7 * height *0.393701) - (4.7 * age)
    cursor.execute("UPDATE persons SET numbers = ? WHERE name = ?", (BMR[0],session["name"],))
    connection.commit()

    return render_template("bmr.html", weight = weight, height = height, age = age, gender = gender, BMR = BMR, LIFESTYLES = LIFESTYLES)

@app.route("/tdee", methods = ["POST"])
def tdee():
    lifestyle = request.form.get("lifestyle")
    if lifestyle not in LIFESTYLES:
        return redirect("/fault")
    else:
        for i in range (len(LIFESTYLES)):
            if lifestyle == LIFESTYLES[i]:
                tdee = tdeetimes[i] * BMR[0]
    return render_template("tdee.html", tdee = tdee)


@app.route("/fault")
def fault():
    return render_template("fault.html")

@app.route("/tracking")
def tracking():
    connection = sqlite3.connect("nutrient.db")
    cursor = connection.cursor()
    rows = cursor.execute("SELECT * FROM macro WHERE name = ?", (session["name"],))
    return render_template("tracking.html", rows = rows)

@app.route("/delete")
def delete():
    global count
    connection = sqlite3.connect("nutrient.db")
    id = request.args.get("id")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM macro WHERE id = ?", (id,))
    connection.commit()
    return redirect("/tracking")


@app.route("/add")
def add():
    global count
    food = request.args.get("food")
    FoodDict = get_nutrient_info(api_key, food)
    connection = sqlite3.connect("nutrient.db")
    cursor = connection.cursor()
    ids = cursor.execute("SELECT * FROM macro WHERE id=(SELECT max(id) FROM macro)")
    for id in ids:
        count = id[5] + 1
    cursor.execute("INSERT INTO macro (Food, Calories, Protein, Carb, Fat, id, name) VALUES (?,?,?,?,?,?,?)", (FoodDict['food_query'],FoodDict['calories'],FoodDict['protein'],FoodDict['carbohydrate'],FoodDict['fat'],count, session["name"]))
    connection.commit()
    return redirect("/tracking")

connection.close()

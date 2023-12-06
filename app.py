from flask import Flask, render_template, request, session, redirect,flash
from flask_session import Session
from flask_mysqldb import MySQLdb,MySQL
import MySQLdb.cursors
import pickle
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
import sklearn
from flask import jsonify
from datetime import date
import warnings

warnings.filterwarnings('ignore')

housedata = pd.read_csv('./REPO\Multi-Category-Prediction-Website\gold\Datasets\house_loc_dataframe.csv')

goldmodel = pickle.load(open('./REPO\Multi-Category-Prediction-Website\gold\GoldPriceDecisionTree.pkl', 'rb'))
loanmodel = pickle.load(open('./REPO\Multi-Category-Prediction-Website\gold\Loan_Status_RandomForest.pkl', 'rb'))
# carmodel = pickle.load(open('F:\REPO\Multi-Category-Prediction-Website\gold\Car_price_randomforest_regression.pkl', 'rb'))
# laptopmodel = pickle.load(open('F:\REPO\Multi-Category-Prediction-Website\gold\Laptop_RandomForest_Regressor.pkl', 'rb'))
# housemodel = pickle.load(open('F:\REPO\Multi-Category-Prediction-Website\gold\Banglore_house_LinearRegression.pkl', 'rb'))
# caloriesmodel = pickle.load(open('F:\REPO\Multi-Category-Prediction-Website\gold\Calories_burn_DecisionTree.pkl', 'rb'))


app = Flask(__name__)
app.secret_key = 'xyz123abc'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='root123$'
app.config['MYSQL_DB']='gold'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
mysql= MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/gold_price")
def gold_price():
    return render_template('gold-price.html')

@app.route("/loan_status")
def loan_status():
    return render_template('loan-status.html')

@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method=="POST" and request.form['username'] and request.form['email'] and request.form['password']:
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("insert into signup(username,email,password) values('{}','{}',{})".format(username,email,password))
        mysql.connection.commit()
        user=cursor.fetchone()
        if user:
            return redirect('/signin')
    return render_template('signup.html')


@app.route("/signin", methods=['GET','POST'])
def signin():
    message=''
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("select * from signup where username='{}' AND password='{}'".format(username,password))
        mysql.connection.commit()
        user=cursor.fetchone()
        if user:
            session["username"] = request.form.get("username")
            flash('Logged in successfully')
            return redirect("/")
        else:
            message='Enter proper credentials'   
    return render_template('signin.html',message=message)

@app.route("/logout")
def logout():
    session["username"] = None
    return redirect("/")


@app.route('/predict_gold', methods=['POST'])
def predict_gold_price():
    SPX = float(request.form.get('SPX'))
    USO = float(request.form.get('USO'))
    SLV = float(request.form.get('SLV'))
    EUR_USD = float(request.form.get('EUR_USD'))

    #gold price prediction
    goldresult = goldmodel.predict(np.array([SPX, USO, SLV, EUR_USD]).reshape(1,4))
    goldoutput = np.round(goldresult, 2)
    return render_template('gold-price.html', goldresult="Predicted Gold Price For Given Value:  {}/- ".format(goldoutput))

@app.route('/sanction', methods=['POST','GET'])
def sanction():
    if request.method=="POST":
        first_name= request.form.get('firstname')
        last_name=request.form.get('lastname')
        phone=request.form.get('phno')
        file1=request.form.get('filename')
        otype=request.form.get('otype')
        gprice=request.form.get('gprice')
        purity=request.form.get('purity')
        gamount=request.form.get('gamount')
        tstamp=request.form.get('tsamp')
        bid=request.form.get('bid')
        file2=request.form.get('filename1')
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO SANCTION(first_name,last_name,phone,file,ornament_tp,gross_wt,purity,gross_amt,time_of_trans,bill_id,imgfile)VALUES('{}','{}','{}','{}','{}','{}','{}',{},'{}',{},'{}')".format(first_name,last_name,phone,file1,otype,gprice,purity,gamount,tstamp,bid,file2)) 
        mysql.connection.commit()
        

    return render_template('loan-status.html') 
 



if __name__ == '__main__':
    app.run(debug=True)
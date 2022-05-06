from colorama import Cursor
import numpy as np
import pickle
from flask import Flask,render_template,redirect,request,flash,url_for,session
import pandas as pd
import os
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from keras.models import load_model





app = Flask('__main__')

app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''


app.secret_key = os.urandom(24)

mysql = MySQL(app)


    
app.config["FILE_UPLOADS"] = "E:\projects\ML\creditcard_fraud_detection\creditcard_fraud detection\static\saved"
app.config["ALLOWED_FILE_EXTENSIONS"] = ["CSV"]

logistic_regression = pickle.load(open('model1.pkl','rb'))
kmeans = pickle.load(open('model2.pkl','rb'))
isof = pickle.load(open('model4.pkl','rb'))
lof = pickle.load(open('model3.pkl','rb'))
#neural network
model =load_model("prediction_model.h5")



@app.route('/')
def home():
    if 'user_id' in session:
        return render_template("index.html")

    else:
     return render_template("login.html")    


@app.route('/signup', methods = ['GET','POST'])
def signup():

    if (request.method =="POST"):

        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        Cursor = mysql.connection.cursor()
        Cursor.execute("INSERT INTO users(first_name, last_name, email, password) VALUES(%s, %s, %s, %s)",(firstname, lastname, email, password))
        mysql.connection.commit()
        Cursor.close()
        return redirect(url_for('login'))

    return render_template("signup.html")


@app.route('/login', methods = ['GET','POST'])
def login():

    if (request.method=="POST"):

        upassword = request.form.get('lpassword')
        uemail = request.form.get('lemail')

        
        Cursor = mysql.connection.cursor()
        Cursor.execute(" SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}' ".format(uemail,upassword))
        u1=Cursor.fetchall()
        print(u1)        

        if len(u1)>0:
            session['user_id'] = u1[0][0]
            return redirect(url_for('home'))

        else:
            return "invalid"  

    return render_template("login.html")    

 
@app.route('/documentation')
def documentation():

    return render_template("documentation.html")   

@app.route('/models')
def models():

    return render_template("models.html")   
      
@app.route('/contact', methods = ['GET', 'POST'])
def contact():

    if(request.method=='POST'):

        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
       # entry = Contact(name=name, message = message, date= datetime.now(), email = email )
       # db.session.add(entry)
       # db.session.commit()

    return render_template("contact.html")  






     #upload of file
    
def allowed_files(filename):

    # We only want files with a . in the filename
    if not "." in filename:
        return False

    # Split the extension from the filename
    ext = filename.rsplit(".", 1)[1]

    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if ext.upper() in app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True
    else:
        return False


@app.route('/', methods = ["GET","POST"])
def file_upload():

    if request.method=="POST":
        
        if request.files:

            file = request.files['file']
            if file.filename == "":
             print("No filename")
             return redirect(request.url)
            

            if allowed_files(file.filename):

               

                file1 = file
                

                df = pd.read_csv(file1)

                
                   #logestic regression
                   
                final_data = df
                prediction = logistic_regression.predict(final_data)
                output = round(prediction[0], 2)  

                if output == 1:
                    transaction = 'fraud' 
                else:
                    transaction = 'valid'  

                    #kmeans

                final_data = df
                prediction2 = kmeans.predict(final_data)
                output2 = round(prediction2[0], 2)  

                if output2 == 1:
                    transaction2 = 'fraud' 
                else:
                    transaction2 = 'valid'    

                    #isof

                final_data = df
                prediction3 = isof.predict(final_data)
                output3 = round(prediction3[0], 2)  

                if output3 == 1:
                    transaction3 = 'fraud' 
                else:
                    transaction3 = 'valid'   

                    #lof

                final_data = df
                prediction4 = lof.predict(final_data)
                output4 = round(prediction4[0], 2)  

                if output4 == 1:
                    transaction4 = 'fraud' 
                else:
                    transaction4 = 'valid' 

                    # neural network  

                finaldata = np.array(df)
                prediction5 = model.predict(finaldata)
                output5 =prediction5.round()

                if output5 == 1:
                    transaction5 = 'fraud' 
                else:
                    transaction5 = 'valid'  


                return render_template("index.html", prediction_text1 = "Logestic regression:"+ transaction,
                 prediction_text2 ="Kmeans clustering:"+ transaction2, prediction_text3 ="Isolation forest:"+ transaction3
                 , prediction_text4 ="Local outlier factor:"+ transaction4, prediction_text5 ="Neural network:"+transaction5)

            else:
                print("That file extension is not allowed")
                return redirect(request.url)

    return render_template("index.html")
        
        
@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect(url_for("login"))

        

if __name__=='__main__':
    app.run(debug=True)


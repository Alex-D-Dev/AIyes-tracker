from flask import Flask, render_template, request,session,Response
import time
import mysql.connector
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import matplotlib
matplotlib.use('Agg')
from scipy.ndimage.filters import gaussian_filter
import ast
import cv2
from camera import VideoCamera
from datetime import datetime


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
)
print(mydb) 

cursor = mydb.cursor()
cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
cursor.close()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = 'SECRET KEY'


def gen(camera,capture_heatmap=False):
    list_heatmap = []
    while True:
        frame,list_heatmap = camera.get_frame(capture_heatmap)
        file = open('./static/list_heatmap.txt','w') 
        file.write(str(list_heatmap))
        file.close()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def myplot(x, y, s, bins=1000):
                heatmap, xedges, yedges = np.histogram2d(x, y, bins=bins)
                heatmap = gaussian_filter(heatmap, sigma=s)

                extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
                return heatmap.T, extent

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    print(session['user'])
    print(session['theme'])
    return render_template('connexion.html')

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    print(session['user'])
    print(session['theme'])
    mycursor = mydb.cursor()
    abonnement = []
    theme = []
    mycursor.execute("SELECT abonnementID,abonnementName FROM eye_tracker.abonnement")
    for x in mycursor:
        abonnement.append(x)
    mycursor.execute("SELECT ThemeID,Name FROM eye_tracker.theme")
    for x in mycursor:
        theme.append(x)
    mycursor.close()
    return render_template('inscription.html', post=[abonnement,theme])

@app.route('/video_feed')
def video_feed():
    video_stream = VideoCamera()
    capture = request.args.get("capture",False)
    frame = gen(video_stream, capture)
    return Response(frame,
                mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/aiyestracker', methods=['GET', 'POST'])
def aiyestracker():
    print(session['user'])
    print(session['theme'])
    start_time = str(datetime.now())
    return render_template('aiyestracker.html',post=[start_time])

@app.route('/resultats', methods=['GET', 'POST'])
def resultats():

    opt_param = request.form.get('resultats')
    print (opt_param)
    toPlot = None
    tofind = None

    if opt_param is not None:
        tofind = int(opt_param.split('£')[0])
        opt_param = opt_param.split('£')[1]
        print(str(tofind)+"ee")

    print(session['user'])
    print(session['theme'])
    email = session['user']
    y = []
    w= []
    if email != None :
        mycursor = mydb.cursor()
        query = ("SELECT utilisateurid FROM eye_tracker.utilisateur where email = %s")
        mycursor.execute(query, (email,))
        for x in mycursor:
            y.append(str(x)[1:-2])
        query = ("SELECT * FROM eye_tracker.tracking where utilisateurid = %s")
        mycursor.execute(query, (y[0],))
        for x in mycursor:
            w.append(x)

        for i in range(0,len(w)):
            if w[i][0] == tofind :
                toPlot = w[i][2]

        if toPlot !=None:

            z =  ast.literal_eval(toPlot)
            print(len(z))
            a = []
            b = []
            for i in range(0,len(z)):
                a.append(z[i][0])
                b.append(1080 - z[i][1])
                

            img, extent = myplot(a, b, 32)
            plt.imshow(img, extent=extent, origin='lower', cmap=cm.jet)
            plt.savefig('./static/a.png',dpi=100)
            plt.clf()

            sns.jointplot(x=a, y=b, kind='hex')
            plt.savefig("./static/b.png",dpi=100)
            plt.clf()

            sns.jointplot(x=a, y=b, kind='kde', cmap=cm.jet)
            plt.savefig("./static/c.png",dpi=100)
            plt.clf()

            plt.plot(a, b, 'k.', markersize=5)
            plt.savefig('./static/d.png',dpi=100)
            plt.clf()

        
    return render_template('resultats.html',post=[w,opt_param])

@app.route('/confirmation_inscription', methods=['GET', 'POST'])
def confirmation_inscription():
    print(session['user'])
    print(session['theme'])
    name = request.form['name']
    email = request.form['email']
    mdp = request.form['mdp'] 
    theme = request.form['theme']
    abonnement = request.form['abonnement']
    print(name,email,mdp,theme,abonnement)
    mycursor = mydb.cursor()

    query = ("INSERT INTO eye_tracker.Utilisateur (Name, Email, MotDePasse, ThemeID, AbonnementID) VALUES(%s, %s, %s, %s, %s)")

    mycursor.execute(query, (name, email, mdp, theme, abonnement))
    mydb.commit()
    mycursor.close()  

    message='Votre inscription a bien été enregistrée'
    return render_template('confirmation.html',post=[message])

@app.route('/confirmation_connexion', methods=['GET', 'POST'])
def confirmation_connexion():

    mycursor = mydb.cursor()
    email = request.form['email']
    mdp = request.form['mdp']    
    query = ("SELECT email FROM eye_tracker.utilisateur where email = %s and motdepasse= %s")
    mycursor.execute(query, (email,mdp))
    for z in mycursor:
        print(z)
    result = mycursor.rowcount
    message=''
    print(str(result))
    mycursor.close()

    mycursor = mydb.cursor()
    query = ("SELECT ThemeID FROM eye_tracker.utilisateur where email = %s ")
    mycursor.execute(query, (email,))
    theme = []
    for z in mycursor:
        theme.append(z)
    theme = int(str(theme[0])[1:-2])
    print(theme)
    mycursor.close()

    if result == 0 or result == -1:
        message = "Erreur  de  connexion"
    else:
        message = "Vous avez bien été connecté"
        session['user'] = email
        session['theme'] = theme

    return render_template('confirmation.html',post=[message])

@app.route('/confirmation_enregistrement_resultats', methods=['GET','POST'])
def confirmation_enregistrement_resultats():
    end = str(datetime.now())
    start = request.form['start']
    Des = request.form['nom']
    file = open('./static/list_heatmap.txt', "r")
    coordinate = file.read()

    email = session['user']
    mycursor = mydb.cursor()
    query = ("SELECT UtilisateurID FROM eye_tracker.utilisateur where email = %s ")
    mycursor.execute(query, (email,))
    email=[]
    for z in mycursor:
        email.append(z)
    UtiD = int(str(email[0])[1:-2])
    mycursor.close()

    mycursor = mydb.cursor()
    query = ("INSERT INTO eye_tracker.Tracking (UtilisateurID, Coordinates, Description, Debut, Fin) VALUES(%s, %s, %s, %s, %s)")
    mycursor.execute(query, (UtiD, coordinate, Des, start, end))
    mydb.commit()
    mycursor.close() 

    message = "Votre tracking a bien été enregistré"
    return render_template('confirmation.html',post=[message])

@app.route('/deconnecter', methods=['GET', 'POST'])
def deconnecter():
    session['user'] = None
    session['theme'] = None
    message = "Vous avez bien été déconnecté"
    print(session['user'])
    print(session['theme'])
    return render_template('confirmation.html',post=[message])

if __name__ == "__main__":
    app.run()
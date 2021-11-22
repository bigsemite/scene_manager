from flask import Flask, redirect, request, render_template, Response
import cv2
from threading import Thread
import datetime
import numpy as np
import os
import time

app = Flask(__name__)

frm = []
status = False
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/connect', methods=['POST', 'GET'])
def conn():
    pp = request.form['cam']
    print(pp)
    
    return Response(loadCam(pp), mimetype='multipart/x-mixed-replace; boundary=frame')


def loadCam(cam):
    global frm
    if cam == '0': cam = 0
    cap=cv2.VideoCapture(cam)
    while True:
        st, frm = cap.read()
        web_frm = cv2.imencode('.jpg',frm)[1].tobytes()
        if status:
        # do comparison
            tr = Thread(target= comp, args=(frm,))
            tr.start()
        if cv2.waitKey(2) == 27 : break
        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + web_frm +b'\r\n')

@app.route('/cap')
def snap():
    #print(frm)
    #if len(frm) >0:
    cv2.imwrite('static/snap.jpg', frm)
    return Response('New snap taken at: '+ str(datetime.datetime.now()))

@app.route('/start')
def st():
    global status
    status = True
    return Response('Started Monitoring at: ' + str(datetime.datetime.now()))

@app.route('/stop')
def stp():
    global status
    status = False
    return Response('Stopped Monitoring at: ' + str(datetime.datetime.now()))


def comp(img):
    try:
        img_org = cv2.imread('static/snap.jpg')
        # mse = summation(img_org - img)/(img_org.shape[0] * img_org.shape[1])
        mse =  np.sum((img_org.astype("float") - img.astype('float')) ** 2)
        mse /= (img_org.shape[0] * img_org.shape[1])
        if int(mse) > 300:
            cv2.imwrite('static/' + str(time.time()) +'.jpg', img)
        print (mse)
        
        
    except Exception as r:
        print('e', r)

@app.route('/shows')
def carry():
    fs = os.listdir('static/')
    fls = [f for f in fs if f !='snap.jpg' and f !='.DS_Store']
    return render_template('views.html', pics=fls)

@app.route('/delete')
def rmv():
    fs = os.listdir('static/')
    for f in fs:
        if f != 'snap.jpg':
            os.remove('static/'+ f)
    return redirect('/shows')

if __name__=='__main__':
    app.run()
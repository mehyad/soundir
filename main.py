import numpy as np
from flask import Flask, redirect, render_template, request, url_for
from werkzeug.datastructures import ImmutableMultiDict

import makeGif
import model.gcc.tdoa
from model.gcc import methods, utils

app = Flask(__name__)
class Data:
    def __init__(self):
        pass
memory = Data()
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data=ImmutableMultiDict.to_dict(request.form)
        memory.distance = int(data['distance'])
        memory.method = data['method']
        print(memory.distance, memory.method)
        return redirect(url_for('setup'))
    return render_template("main.html")
    


@app.route("/record", methods=["GET","POST"])
def setup():
    if request.method == "POST":
        print("FORM DATA RECEIVED")
        f = request.files["audio_data"]
        with open("audio.wav", "wb") as audio:
            f.save(audio)
    return render_template("recordv2.html")

@app.route("/direction", methods=["GET","POST"])
async def result():
    print("RESULT")
    # print(memory.distance, memory.method)
    # angle=40
    angle,msg=model.gcc.tdoa.tdoa("audio.wav", memory.distance, memory.method)
    makeGif.makeGif(angle)
    return render_template("direction.html",angle=angle,msg=msg)
    # print(memory.distance, memory.method)
   

if __name__ == "__main__":
    app.run(debug=True, threaded=True)

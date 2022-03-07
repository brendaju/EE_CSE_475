from flask import Flask, render_template, request, jsonify, json, copy_current_request_context, redirect, url_for, abort
import json
import requests
from threading import Lock
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect

import os
from werkzeug.utils import secure_filename
import matplotlib.image as mpimg
import numpy as np
from json import JSONEncoder

async_mode = None

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

app.config['UPLOAD_EXTENSIONS'] = ['.jpg']

color_array1 = []

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


@socketio.event
def buttonPressed(message):
	print(message)
	socketio.emit('my_response', {'data':message})

@app.route('/array',methods=['POST'])
def load_array():
	id = request.args['id']
	array_json = json.loads(request.get_json())
	#print(array_json)	
	#color_array1 = array_json
	socketio.emit('update_led',
		{'data':array_json['array'],
		 'userId':id})
	print(array_json)
	return array_json

@app.route('/upload', methods = ['POST'])
def upload():
	uploaded_file = request.files['image']
	filename = secure_filename(uploaded_file.filename)
	id = request.form.get("id")
	if filename != '':
		file_ext = os.path.splitext(filename)[1]
		if file_ext not in app.config['UPLOAD_EXTENSIONS']:
			abort(400)
		file = np.array(mpimg.imread(uploaded_file))
		image_data = {"array": file}
		image = json.dumps(image_data, cls = NumpyArrayEncoder)
		socketio.emit('sendimg', {'file':image})
	return redirect(url_for('imageshow', id=id))

@app.route('/')
def index():
	return render_template('welcome.html')

@app.route('/painting')
def painting():
	id = request.args['id']
	return render_template('painting.html', deviceID = id, idasync_mode=socketio.async_mode)
	
@app.route('/menu')
def menu():
	id = request.args['id']
	return render_template('menu.html', deviceID = id)

@app.route('/art')
def art():
	id = request.args['id']
	return render_template('art.html', deviceID = id)

@app.route('/chess')
def chess():
	id = request.args['id']
	return render_template('chess.html', deviceID = id)

@app.route('/tictactoe')
def tictactoe():
	id = request.args['id']
	return render_template('tictactoe.html', deviceID = id)

@app.route('/animation')
def animation():
	id = request.args['id']
	return render_template('animation.html', deviceID = id)

@app.route('/brickshooter')
def brickshooter():
	id = request.args['id']
	return render_template('brickshooter.html', deviceID = id)

@app.route('/tugofwar')
def tugofwar():
	id = request.args['id']
	return render_template('tugofwar.html', deviceID = id)

@app.route('/stacker')
def stacker():
	id = request.args['id']
	return render_template('stacker.html', deviceID = id)

@app.route('/simonsays')
def simonsays():
	id = request.args['id']
	return render_template('simonsays.html', deviceID = id)

@app.route('/pong')
def pong():
	id = request.args['id']
	return render_template('pong.html', deviceID = id)

@app.route('/imageshow')
def imageshow():
	id = request.args['id']
	return render_template('imageshow.html', deviceID = id)


deviceID = 0
@socketio.event
def connect():
	global deviceID
	print('User Connected')
	emit('connected', {'data': 'Connected', 'deviceID': deviceID})
	deviceID = deviceID + 1

@socketio.event
def changeApp(appName):
	print(appName)
	socketio.emit('appChange', {'data':appName})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
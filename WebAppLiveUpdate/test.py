from flask import Flask, render_template, request, jsonify, json, copy_current_request_context
import json
import requests
from threading import Lock
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect

async_mode = None

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


color_array1 = []

@socketio.event
def buttonPressed(message):
	print(message)
	socketio.emit('my_response', {'data':message})

#@socketio.event
#def changeApp(appName):
#	print(appName)
#	socketio.emit('my_response', {'data':appName})

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

deviceID = 0
@socketio.event
def connect():
	global deviceID
	print('User Connected')
	emit('connected', {'data': 'Connected', 'deviceID': deviceID})
	deviceID = deviceID + 1
    #emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.event
def changeApp(appName):
	print(appName)
	socketio.emit('appChange', {'data':appName})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
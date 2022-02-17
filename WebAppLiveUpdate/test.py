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

@app.route('/array',methods=['POST'])
def load_array():
	array_json = json.loads(request.get_json())
	#print(array_json)	
	#color_array1 = array_json
	socketio.emit('update_led',
		{'data':array_json['array']})
	print(array_json)
	return array_json

@app.route('/')
def index():
	return render_template('welcome.html')

@app.route('/painting')
def painting():
	return render_template('painting.html', async_mode=socketio.async_mode)
	
@app.route('/menu')
def menu():
	return render_template('menu.html')

@app.route('/art')
def art():
	return render_template('art.html')

@socketio.event
def connect():
	print('User Connected')
    #emit('my_response', {'data': 'Connected', 'count': 0})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
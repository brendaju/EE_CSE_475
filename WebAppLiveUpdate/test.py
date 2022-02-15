from flask import Flask, render_template, request, jsonify, json, copy_current_request_context
import json
import requests
from threading import Lock
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


color_array1 = []



@app.route('/array',methods=['POST'])
def load_array():
	array_json = json.loads(request.get_json())
	#print(array_json)	
	#color_array1 = array_json
	socketio.emit('my_response',
		{'data':array_json['array']})
	print(array_json)
	return array_json

@app.route('/')
def index():
	return render_template('index.html', async_mode=socketio.async_mode)




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
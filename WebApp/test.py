from flask import Flask, render_template, request, jsonify, json
import json
import requests



app = Flask(__name__)

color_array1 = []

@app.route('/array',methods=['POST'])
def load_array():
	array_json = json.loads(request.get_json())
	print(array_json)	
	color_array1 = array_json
	return array_json

@app.route('/')
def index():
   return render_template('index.html', color_array=color_array1)





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
from flask import Flask, render_template, request, jsonify, json
import json
import requests



app = Flask(__name__)

color_array1 = []



@app.route('/array',methods=['POST'])
def load_array():
	array_json = json.loads(request.get_json())
	print(array_json)	
	#color_array1 = array_json
	with open("test.txt", "w") as fo:
		fo.write(json.dumps(array_json))
	return array_json

@app.route('/')
def index():
   with open("test.txt", "r") as fo:
      color_array1 = json.loads(fo.read())

   print(color_array1["array"][0])
   return render_template('index.html', color_array=color_array1["array"])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
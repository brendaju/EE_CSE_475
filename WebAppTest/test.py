from flask import Flask, render_template, request, jsonify, json, redirect, url_for
import json
import requests



app = Flask(__name__, static_url_path='/static')

color_array1 = []



@app.route('/array',methods=['POST'])
def load_array():
	array_json = json.loads(request.get_json())
	#print(array_json)	
	color_array1 = array_json
	with open("test.txt", "w") as fo:
		fo.write(json.dumps(array_json))
	return redirect(request.url)


@app.route('/')
def index():
   with open("test.txt", "r") as fo:
      color_array1 = json.loads(fo.read())

   #print(color_array1["array"][0])
   return render_template('welcome.html')

@app.route('/painting')
def painting():

   with open("test.txt", "r") as fo:
      color_array1 = json.loads(fo.read())
   return render_template('painting.html', color_array=color_array1["array"])

@app.route('/menu')
def menu():
   return render_template('menu.html');

@app.route('/art')
def art():
   return render_template('art.html');

@app.route('/test.txt')
def textpage():
   with open("test.txt", "r") as fo:
      color_array1 = json.loads(fo.read())
   return color_array1

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
import shapefile
from pygeocoder import Geocoder
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, mpld3
from mpld3 import fig_to_html
import shapely.geometry
from patch import PolygonPatch
from flask import Flask
from flask import render_template
from flask import request
from flask import Markup
from flask import send_file
import StringIO

app = Flask(__name__)

@app.route('/')
def form():
    return render_template("form.html")

@app.route("/", methods=['POST'])
def image():
    addr1 = request.form['Addr1']
    addr2 = request.form['Addr2']
    return render_template("plot.html", addr1=addr1, addr2=addr2)

@app.route("/plot/<addr1>/<addr2>")
def plot(addr1, addr2):
    img = getInBetweenZipCodes(addr1, addr2)
    return send_file(img, mimetype='image/png')

def getInBetweenZipCodes(addr1, addr2):
	coord1 = Geocoder.geocode(addr1)[0].coordinates
	coord2 = Geocoder.geocode(addr2)[0].coordinates
        line = shapely.geometry.LineString([coord1[::-1], coord2[::-1]])
	sf = shapefile.Reader("cb_2013_us_zcta510_500k/cb_2013_us_zcta510_500k")
	zipcodeAreas = []
	for shape in sf.iterShapes():
		zipcodeArea = shapely.geometry.Polygon(shape.points)
		color = "red" if line.intersects(zipcodeArea) else "green"
		zipcodeAreas.append((zipcodeArea, color))
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.plot(*np.array(line).T, color='blue', linewidth=1, solid_capstyle='round')
	for (zipcodeArea, color) in zipcodeAreas:
		if (color == "red"):
			ax.add_patch(PolygonPatch(zipcodeArea, fc=color, ec=color, alpha=0.5))
	ax.axis([-200, -50, 0, 100])
	img = StringIO.StringIO()
	fig.savefig(img)
	img.seek(0)
	return img

if __name__ == "__main__":
    app.run()

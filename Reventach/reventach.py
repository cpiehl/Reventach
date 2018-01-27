##############################################################
# Lambo Reventon Tachometer
# THESE ARE NOT THE GAUGES OF A BILLIONAIRE, RICHARD
#
# Changelog:
#
# V1.0  - Initial version
#
#############################################################

import ac
import acsys
import json
import os

appHeight = 200
appWidth = 200
lineSlope = 3
fontSize = 0
gearSpacing = 0

appWindow = 0
doRender = True
Labels = {}
CarData = {
	"maxRPM": 10000,
	"totalGears": 6
}
gears = ["N", "R"]
maxRPM = 0
maxGear = 0

# This function gets called by AC when the Plugin is initialised
# The function has to return a string with the plugin name
def acMain(ac_version):
	global appWindow, Labels, gearSpacing, fontSize, gears
	appWindow = ac.newApp("Reventach")
	ac.setSize(appWindow, appWidth, appHeight)
	ac.drawBorder(appWindow, 0)
	ac.setBackgroundOpacity(appWindow, 0)
	ac.setIconPosition(appWindow, 0, -10000)
	ac.setTitle(appWindow, "")

	# Only enable rendering if app is activated
	ac.addOnAppActivatedListener(appWindow, onAppActivated)
	ac.addOnAppDismissedListener(appWindow, onAppDismissed)

	loadCarData()

	for n in range(CarData["totalGears"]):
		gears.insert(0, str(n + 1))

	gearSpacing = appHeight / (CarData["totalGears"] + 2)
	fontSize = gearSpacing * 0.8

	for n,c in enumerate(gears):
		Labels["gear" + c] = ac.addLabel(appWindow, c)
		ac.setPosition(Labels["gear" + c], 100, (n * gearSpacing))
		ac.setFontSize(Labels["gear" + c], fontSize)
		ac.setFontAlignment(Labels["gear" + c], "center")

	ac.addRenderCallback(appWindow, onFormRender)
	return "Reventach"


def onFormRender(deltaT):
	global doRender, maxRPM, maxGear

	if not doRender:
		return

	gear = ac.getCarState(0, acsys.CS.Gear)
	rpm = ac.getCarState(0, acsys.CS.RPM)

	gearY = appHeight - (gear * gearSpacing)
	rpmY = appHeight * (rpm / CarData["maxRPM"])
	rpmX = rpmY / lineSlope
	rpmXL = (appWidth * 0.02) + rpmX
	rpmXR = (appWidth * 0.98) - rpmX
	rpmY = appHeight - rpmY

	hBarWidth = appWidth * 0.04

	centerX = appWidth / 2
	centerY = gearY - fontSize / 2
	l = centerX - fontSize / 2
	r = centerX + fontSize / 2
	t = gearY - fontSize

	ac.glBegin(acsys.GL.Lines)

	ac.glColor4f(0.9, 0.9, 0.9, 0.9)

	# white selected gear box
	ac.glVertex2f(l, gearY)
	ac.glVertex2f(r, gearY)
	ac.glVertex2f(r, gearY)
	ac.glVertex2f(r, t)
	ac.glVertex2f(r, t)
	ac.glVertex2f(l, t)
	ac.glVertex2f(l, t)
	ac.glVertex2f(l, gearY)

	# white diagonals
	ac.glVertex2f(0, appHeight)
	ac.glVertex2f(appHeight/lineSlope, 0)
	ac.glVertex2f(appWidth, appHeight)
	ac.glVertex2f(appWidth - (appHeight/lineSlope), 0)

	ac.glColor4f(0.0, 0.9, 0.0, 0.9)

	# green diagonals
	ac.glVertex2f(appWidth * 0.02, appHeight)
	ac.glVertex2f(rpmXL, rpmY)
	ac.glVertex2f(appWidth * 0.98, appHeight)
	ac.glVertex2f(rpmXR, rpmY)

	# green horizontal rpms
	ac.glVertex2f(rpmXL, rpmY)
	ac.glVertex2f(rpmXL + hBarWidth, rpmY)
	ac.glVertex2f(rpmXR, rpmY)
	ac.glVertex2f(rpmXR - hBarWidth, rpmY)

	# green horizontal selected gear
	ac.glVertex2f(l, centerY)
	ac.glVertex2f(l - hBarWidth, centerY)
	ac.glVertex2f(r, centerY)
	ac.glVertex2f(r + hBarWidth, centerY)

	# green back to selected gear
	ac.glVertex2f(rpmXL + hBarWidth, rpmY)
	ac.glVertex2f(l - hBarWidth, centerY)
	ac.glVertex2f(rpmXR - hBarWidth, rpmY)
	ac.glVertex2f(r + hBarWidth, centerY)

	ac.glEnd()


def loadCarData():
	global CarData
	carName = ac.getCarName(0)

	try:
		carsFile = os.path.join(os.path.dirname(__file__), "cardata.json")
		with open(carsFile, "r") as f:
			jsonData = json.load(f)

	except OSError:
		ac.log("Reventach ERROR: loadCarData cardata.json not found")

	else:
		try:
			CarData["totalGears"] = jsonData[carName]["gears"]
			CarData["maxRPM"] = jsonData[carName]["maxRPM"]
			ac.console("Car data found for " + carName)

		except KeyError: # Doesn't exist in official, look for custom data
			try:
				carsFile = os.path.join(os.path.dirname(__file__), "cardata-custom.json")
				with open(carsFile, "r") as f:
					jsonData = json.load(f)
					CarData["totalGears"] = jsonData[carName]["gears"]
					CarData["maxRPM"] = jsonData[carName]["maxRPM"]

			except (OSError, KeyError) as e:
				ac.log("Reventach ERROR: loadCarData: No custom car data found for this car")
				CarData["totalGears"] = 6
				CarData["maxRPM"] = 10000

			else:
				ac.console("Custom car data found for " + carName)


def onAppActivated():
	global doRender
	doRender = True


def onAppDismissed():
	global doRender
	doRender = False

##############################################################
# Lambo Reventon Tachometer
# THESE ARE NOT THE GAUGES OF A BILLIONAIRE, RICHARD
#
# Changelog:
#
# V1.0  - Initial version
#
# V1.1	- Looks more like the real one.
#       - Colored bars, dashed RPM, redline
#
#############################################################

import ac
import acsys
import json
import os

appHeight = 200
appWidth = 250
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
PxPer1000RPM = 1
RPMdivs = 1

# This function gets called by AC when the Plugin is initialised
# The function has to return a string with the plugin name
def acMain(ac_version):
	global appWindow, Labels, gearSpacing, fontSize, gears, PxPer1000RPM, RPMdivs
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
	PxPer1000RPM = 1000 * appHeight / CarData["maxRPM"]
	RPMdivs = CarData["maxRPM"] // 10000 + 1
	#~ fontSize = PxPer1000RPM * 0.5 * RPMdivs
	fontSize = appHeight / 15

	y = appHeight - PxPer1000RPM * RPMdivs
	count = RPMdivs
	while y > -1:
		dx = (appHeight - y) / lineSlope
		Labels["rpmL" + str(count)] = ac.addLabel(appWindow, str(count))
		ac.setPosition(Labels["rpmL" + str(count)], dx - fontSize, y - fontSize/2)
		ac.setFontSize(Labels["rpmL" + str(count)], fontSize)
		ac.setFontAlignment(Labels["rpmL" + str(count)], "center")
		Labels["rpmR" + str(count)] = ac.addLabel(appWindow, str(count))
		ac.setPosition(Labels["rpmR" + str(count)], appWidth - dx + fontSize, y - fontSize/2)
		ac.setFontSize(Labels["rpmR" + str(count)], fontSize)
		ac.setFontAlignment(Labels["rpmR" + str(count)], "center")

		if y < PxPer1000RPM * RPMdivs - 1:
			ac.setFontColor(Labels["rpmL" + str(count)], 0.7, 0.0, 0.0, 0.9)
			ac.setFontColor(Labels["rpmR" + str(count)], 0.7, 0.0, 0.0, 0.9)

		y -= (PxPer1000RPM * RPMdivs)
		count += RPMdivs

	for n in range(CarData["totalGears"]):
		gears.insert(0, str(n + 1))

	gearSpacing = appHeight / (CarData["totalGears"] + 2)
	fontSize = gearSpacing * 0.8

	for n,c in enumerate(gears):
		Labels["gear" + c] = ac.addLabel(appWindow, c)
		ac.setPosition(Labels["gear" + c], appWidth/2, (n * gearSpacing))
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

	hBarWidth = appWidth * 0.04
	lineWidth = appWidth * 0.01
	doubleWidth = lineWidth * 2
	halfWidth = lineWidth / 2

	gearY = appHeight - (gear * gearSpacing)
	rpmY = appHeight * (rpm / CarData["maxRPM"])
	rpmX = rpmY / lineSlope
	rpmXL = doubleWidth + rpmX
	rpmXR = (appWidth - doubleWidth) - rpmX
	rpmY = appHeight - rpmY

	centerX = appWidth / 2
	centerY = gearY - fontSize / 2
	l = centerX - fontSize / 2
	r = centerX + fontSize / 2
	t = gearY - fontSize

	ac.glColor4f(0.7, 0.0, 0.0, 0.9)
	ac.glBegin(acsys.GL.Quads)

	# red diagonals
	ac.glVertex2f(0, appHeight)
	ac.glVertex2f(lineWidth, appHeight)
	ac.glVertex2f(appHeight/lineSlope + lineWidth, 0)
	ac.glVertex2f(appHeight/lineSlope, 0)

	ac.glVertex2f(appWidth - lineWidth, appHeight)
	ac.glVertex2f(appWidth, appHeight)
	ac.glVertex2f(appWidth - (appHeight/lineSlope), 0)
	ac.glVertex2f(appWidth - lineWidth - (appHeight/lineSlope), 0)

	ac.glEnd()

	# red RPM x1000 ticks
	y = appHeight
	while y > -1:
		dx = (appHeight - y) / lineSlope
		ac.glQuad(dx, y, hBarWidth, lineWidth)
		ac.glQuad(appWidth - dx - hBarWidth, y, hBarWidth, lineWidth)
		y -= (PxPer1000RPM * RPMdivs)

	# red/green diagonal quads
	ac.glColor4f(0.0, 0.9, 0.0, 0.9)
	topY = appHeight - (PxPer1000RPM * RPMdivs) + doubleWidth
	botY = appHeight - lineWidth
	while botY > 0:
		if topY < (PxPer1000RPM * RPMdivs):
			ac.glColor4f(0.7, 0.0, 0.0, 0.9)
			y = max(0, topY) # redline bars
		elif topY < rpmY:
			y = rpmY # current rpm bar
		else:
			y = topY # rest of the lower rpm bars
		dxt = (appHeight - y + doubleWidth) / lineSlope + doubleWidth
		dxb = (appHeight - botY + doubleWidth) / lineSlope + doubleWidth

		ac.glBegin(acsys.GL.Quads)
		ac.glVertex2f(dxb, botY)
		ac.glVertex2f(dxb + lineWidth * 3, botY)
		ac.glVertex2f(dxt + lineWidth * 3, y)
		ac.glVertex2f(dxt, y)

		ac.glVertex2f(appWidth - dxb - lineWidth * 3, botY)
		ac.glVertex2f(appWidth - dxb, botY)
		ac.glVertex2f(appWidth - dxt, y)
		ac.glVertex2f(appWidth - dxt - lineWidth * 3, y)

		ac.glEnd()

		botY = topY - lineWidth * 3
		topY -= (PxPer1000RPM * RPMdivs)


	# white boxes around gears
	for g in range(CarData["totalGears"] + 2):
		if g == gear:
			ac.glColor4f(0.0, 0.9, 0.0, 0.9)
			lw = lineWidth
		else:
			ac.glColor4f(0.9, 0.9, 0.9, 0.9)
			lw = halfWidth
		gy = appHeight - (g * gearSpacing)
		gt = gy - fontSize
		ac.glQuad(l - lw, gy, fontSize + (lw * 2), lw) # bot
		ac.glQuad(r, gt, lw, fontSize) # right
		ac.glQuad(l - lw, gt - lw, fontSize + (lw * 2), lw) # top
		ac.glQuad(l - lw, gt, lw, fontSize) # left

	ac.glColor4f(0.9, 0.9, 0.9, 0.9)
	ac.glBegin(acsys.GL.Lines)

	# white diagonal back to selected gear
	ac.glVertex2f(rpmXL + hBarWidth + lineWidth, rpmY)
	ac.glVertex2f(l - hBarWidth - lineWidth, centerY)
	ac.glVertex2f(rpmXR - hBarWidth - lineWidth, rpmY)
	ac.glVertex2f(r + hBarWidth + lineWidth, centerY)

	ac.glEnd()

	ac.glColor4f(0.9, 0.9, 0.9, 0.9)
	# white horizontal rpms
	ac.glQuad(rpmXL + lineWidth, rpmY - halfWidth, hBarWidth, lineWidth)
	ac.glQuad(rpmXR - hBarWidth - lineWidth, rpmY - halfWidth, hBarWidth, lineWidth)

	# white horizontal selected gear
	ac.glQuad(l - hBarWidth - lineWidth, centerY - halfWidth, hBarWidth, lineWidth)
	ac.glQuad(r + lineWidth, centerY - halfWidth, hBarWidth, lineWidth)


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

			else:
				ac.console("Custom car data found for " + carName)


def onAppActivated():
	global doRender
	doRender = True


def onAppDismissed():
	global doRender
	doRender = False

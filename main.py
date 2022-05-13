from distutils.log import error
import tkinter as tk
import time
import random
import json
from math import acos, degrees, pi, sqrt, atan, asin, floor, log, ceil
from turtle import color
import matplotlib.pyplot as plt
import numpy as np
import sys

from pygame import QUIT

with open('settings.json') as f:
    jsonFile=json.loads(f.read())
    f.close()
class Circle:
	def __init__(self, x, y, vx, vy, r):
		self.x = x
		self.y = y
		self.vx = vx
		self.vy = vy
		self.r = r
		self.m = r**2 * pi



pauseOnColision = False
jsonFile["air_resistance"] = 1
shapeLines = []

colided = []
energy = 0
events = []
lifetime = 0
maxHeight = 0
obj_mem = [[],[]]

energyGraphLine = [[0],[0]]
ballsGraphLine = [[0],[0]]

window = tk.Tk()       # creating the window object
window.title('Sim')
window.resizable(False, False)


objects = []

c = tk.Canvas(window,width=600, height=600, bg="black")

energy_string_var = tk.StringVar(value=f"energy : {energy if jsonFile['displayTotalEnergy'] else 'disabled'}")


def newSphere(r, x, y, vx = 0, vy = 0):
    global objects
    objects.append({
		"vx": vx, # velocity
		"vy": vy, # velocity
		"r": r,
		"m": pi*(r**2), # mass
		"o": c.create_oval(x-r, y-r, x+r, y+r, outline="white"),
		"vector": c.create_line(x, y, x+vx, y+vy, fill="orange", arrow=tk.LAST, width=1),
	})


def dump():
	with open('settings.json', 'w') as outfile:
		json.dump(jsonFile, outfile, sort_keys=True, indent=4)



def sync_windows():
	for widget in window.winfo_children(): # Loop through each widget in main window
		if '!toplevel' in str(widget):
			offset=json.loads(widget.title)
			print(widget.title)
			x = window.winfo_x() + window.winfo_width() + offset[0]
			y = window.winfo_y() + offset[1]
			widget.geometry("+%d+%d" % (x,y))
window.bind("<Configure>", lambda event: sync_windows())

def openGraph():
	global lifetime, energyGraphLine, maxHeight, ballsGraphLine, objects, obj_mem
	ballsGraphLine[0].append(lifetime)
	ballsGraphLine[1].append(len(objects))

	fig, host = plt.subplots()
	fig.subplots_adjust(right=0.75)

	par1 = host.twinx()
	par2 = host.twinx()

	# move the spine of the second axes outwards
	par2.spines["right"].set_position(("axes", 1.2))

	velocity = [[0],[0]]

	for i in range(len(obj_mem[0])):
		for j in range(len(obj_mem[1][i])):
			velocity[0].append(obj_mem[0][i])
			velocity[1].append(sqrt(abs(abs(obj_mem[1][i][j]["vx"])**2 + abs(obj_mem[1][i][j]["vy"])**2)))




	p1, = host.plot(energyGraphLine[0], energyGraphLine[1], 'r-', label="Sum Kenetic Energy")
	p2, = par1.plot(ballsGraphLine[0], ballsGraphLine[1], 'g-', label="Number of balls")
	p3, = par1.plot(velocity[0], velocity[1], 'o', label="Number of balls", color="grey", alpha=0.1, linewidth=1)

	host.set_xlim(0, lifetime)
	host.set_ylim(0, max(energyGraphLine[1])+(max(energyGraphLine[1])/10))
	par1.set_ylim(0, max(ballsGraphLine[1])*2+(max(ballsGraphLine[1])/20))
	par2.set_ylim(0, max(velocity[1]))

	host.set_xlabel("Time")
	host.set_ylabel("Sum Energy")
	par1.set_ylabel("Number of balls")
	par2.set_ylabel("Velocity")

	lines = [p1, p2, p3]
	host.legend(lines, [l.get_label() for l in lines])

	for ax in [par1, par2]:
		ax.set_frame_on(True)
		ax.patch.set_visible(False)

		plt.setp(ax.spines.values(), visible=False)
		ax.spines["right"].set_visible(True)

	host.yaxis.label.set_color(p1.get_color())
	par1.yaxis.label.set_color(p2.get_color())
	par2.yaxis.label.set_color(p3.get_color())

	par1.spines["right"].set_edgecolor(p2.get_color())
	par2.spines["right"].set_edgecolor(p3.get_color())

	host.tick_params(axis='y', colors=p1.get_color())
	par1.tick_params(axis='y', colors=p2.get_color())
	par2.tick_params(axis='y', colors=p3.get_color())

	plt.show()



def toolbarWindow():
	global jsonFile, energy_string_var
	options= tk.Toplevel(window, bg="black")
	options.title = "[15,0]"
	options.geometry("300x500"+f"+{window.winfo_x()+625}+{window.winfo_y()}")
	options.overrideredirect(True)

	close_button = tk.Button(options, text="close", bg="white", fg="red", command=options.destroy)
	close_button.pack(anchor=tk.NE, fill='none', padx=0, pady=0)
	dragable = tk.Button(options, text="Options", bg="white", fg="black", width=36)
	dragable.place(x=0,y=0)



	def drag(x,y):
		offset=json.loads(options.title)
		options.title=f"[{x+offset[0]},{y+offset[1]}]"
		sync_windows()

	dragable.bind("<Button1-Motion>", lambda event: drag(event.x,event.y))



	levelName = tk.StringVar(options)
	levelName.set("one") # default value
	levelOptions = ",".join((jsonFile["scenes"]).keys())
	print(levelOptions)
	dropdown = tk.OptionMenu(options, levelName, *levelOptions)
	dropdown.pack(anchor=tk.NW, fill=tk.NONE, padx=10, pady=10)

	air_label = tk.Label(options, text="Air Vecosity", bg="black", fg="white")
	air_label.pack(anchor=tk.NW, fill=tk.NONE, padx=10, pady=10)
	air_density_input = tk.Entry(options, name="air_density", bg="black", fg="white", insertbackground="#3C3F41")
	air_density_input.insert(tk.END, str(jsonFile["air_resistance"]))
	def set_air_density(event):
		global jsonFile

		try:
			jsonFile["air_resistance"] = float(air_density_input.get())
			if float(air_density_input.get()) > 500 or float(air_density_input.get()) < -100:
				jsonFile["air_resistance"] = 1
				air_density_input.delete(0, tk.END)
				air_density_input.insert(0, "1")
				return
		except :
			jsonFile["air_resistance"] = 1
			insert = air_density_input.index("insert")-1
			air_density_input.delete(insert)
		dump()
	air_density_input.bind("<KeyRelease>", lambda event:set_air_density(event))
	air_density_input.pack(anchor=tk.NW, padx=10, pady=2)


	frame_label = tk.Label(options, text="Game Speed", bg="black", fg="white")
	frame_label.pack(anchor=tk.NW, fill=tk.NONE, padx=10, pady=10)
	framerate_input = tk.Entry(options, name="gameSpeed", bg="black", fg="white", insertbackground="#3C3F41")
	framerate_input.insert(tk.END, str(jsonFile['frameRate']))
	def set_frame_rate(event):
		global jsonFile
		try:
			jsonFile['frameRate'] = float(framerate_input.get())
			if float(framerate_input.get()) > 500 or float(framerate_input.get()) < -100:
				jsonFile['frameRate'] = 1
				framerate_input.delete(0, tk.END)
				framerate_input.insert(0, "1")
				return
		except :
			jsonFile['frameRate'] = 1
			insert = framerate_input.index("insert")-1
			framerate_input.delete(insert)
		dump()
	framerate_input.bind("<KeyRelease>", lambda event:set_frame_rate(event))
	framerate_input.pack(anchor=tk.NW, padx=10, pady=2)



	

	def toggle_lines():
		global jsonFile
		jsonFile['lines'] = not jsonFile['lines']
		lines_button.config(text="Lines: "+("On" if jsonFile['lines'] else "Off"))
		dump()

	lines_button = tk.Button(options, text="Lines: "+("On" if jsonFile['lines'] else "Off"), bg="black", fg="white", command=lambda:toggle_lines())
	lines_button.pack(anchor=tk.NW, padx=10, pady=10)

	def toggle_vectors():
		global jsonFile
		jsonFile["vectors"] = not jsonFile["vectors"]
		vector_button.config(text="Vectors: "+("On" if jsonFile['vectors'] else "Off"))
		dump()

	vector_button = tk.Button(options,
    text="Vectors: "+("On" if jsonFile['vectors'] else "Off"),
    bg="black", fg="white", command=lambda:toggle_vectors())
	vector_button.pack(anchor=tk.NW, padx=10, pady=10)


	def toggle_energy():
		global jsonFile
		jsonFile["displayTotalEnergy"] = not jsonFile["displayTotalEnergy"]
		energy_string_var.set(f"energy : {energy if jsonFile['displayTotalEnergy'] else 'disabled'}")
		dump()

	energy_button = tk.Button(options, textvariable=energy_string_var, bg="black", fg="white", command=lambda:toggle_energy())
	energy_button.pack(anchor=tk.NW, padx=10, pady=10)


	test_button = tk.Button(options, text="test", bg="black", fg="white", command=lambda:test())
	test_button.pack(anchor=tk.NW, padx=10, pady=10)

	def toggle_vectors_graph():
		global jsonFile
		jsonFile["plot_velocity"] = not jsonFile["plot_velocity"]
		vector_button.config(text="plot velocity: "+("On" if jsonFile['plot_velocity'] else "Off"))
		dump()

	vector_button = tk.Button(options,
    text="Plot velocity: "+("On" if jsonFile['plot_velocity'] else "Off"),
    bg="black", fg="white", command=lambda:toggle_vectors_graph())
	vector_button.pack(anchor=tk.NW, padx=10, pady=10)





	lines_button = tk.Button(options, text="Graph", bg="black", fg="white", command=lambda:openGraph())
	lines_button.pack(anchor=tk.NW, padx=10, pady=10)

tools = tk.Button(text="Settings", command=lambda: toolbarWindow(), bg="black" , fg="white", borderwidth=0)
tools.place(x=10, y=10)



# newSphere(30, 80, 100)
# newSphere(30, 100, 200)
# newSphere(20, 500, 100, -10, 0)

newSphere(30, 100, 400, 20, -20)
newSphere(25, 500, 450, -20, -23)

# newSphere(30, 300, 300)
# newSphere(30, 300, 450)
# newSphere(30, 300, 450, 0, -100)

# newSphere(30, 100, 500, 5)
# newSphere(15, 500, 500, -10)

# newSphere(30, 300, 100, 0)
# newSphere(30, 320, 500, 0, -30)

# newSphere(20, 220, -5000, 0, 0)
# newSphere(40, 420, -5000, 0, 0)

def in_circle(center_x, center_y, radius, x, y):
    dist = sqrt((center_x - x) ** 2 + (center_y - y) ** 2)
    return dist <= radius


def click(event):
	global objects, lifetime

	clicked_circle = False
	for i in range(0, len(objects)):
		bx = c.bbox(objects[i]["o"])
		if (objects[i]["r"] >= sqrt((bx[2]-objects[i]["r"] - event.x) ** 2 + (bx[3]-objects[i]["r"] - event.y) ** 2)):
			c.delete((objects[i]["o"]))
			c.delete((objects[i]["vector"]))
			objects.pop(i)
			clicked_circle = True


	if not clicked_circle:
		newSphere(random.randint(20,50), event.x, event.y)
	ballsGraphLine[0].append(lifetime)
	ballsGraphLine[1].append(len(objects))

c.bind("<Button-1>", lambda event:events.append(click(event)))

c.pack()
run = True

def detect_floor(obj):
	if c.bbox(obj["o"])[3] >= 600:
		c.move(obj["o"], 0, -c.bbox(obj["o"])[3] + 600)
		return 0
	return obj["vy"]

def detect_walls(obj):
	if c.bbox(obj["o"])[0] <= 0:
		c.move(obj["o"], -c.bbox(obj["o"])[0]+0,0)
		return obj["vx"]*-.5
	elif c.bbox(obj["o"])[0] >= 600-2*obj["r"]:
		c.move(obj["o"], -c.bbox(obj["o"])[2]+(600),0)
		return obj["vx"]*-.5
	return obj["vx"]

def sortList(item_list):
	if len(item_list)-1 == 0: return item_list
	for i in range(0, len(item_list)-1):
		if item_list[i]["vy"]**2+item_list[i]["vx"]**2 < item_list[i+1]["vx"]**2+item_list[i+1]["vy"]**2:
			item_list[i+1], item_list[i] = item_list[i], item_list[i+1]
			i = 0
	return item_list


def colisions(list, object):
	global run, colided
	if len(list) <= 1: return
	obx = c.bbox(object["o"])
	for i in range(0, len(list)):
		try:
			if list[i] == object: break
		except:
			return list, object
		bx = c.bbox(list[i]["o"])
		if (list[i]["r"]+object["r"] >= sqrt((bx[2]-list[i]["r"] - (obx[2]-object["r"])) ** 2 + (bx[3]-list[i]["r"] - (obx[3]-object["r"])) ** 2)):
			if [list[i],object] in colided or [object,list[i]] in colided:
				break
			else:
				colided.append([list[i], object])

			# setting variables for the colision

			obj1 = Circle(obx[0]+object["r"], obx[1]+object["r"], object["vx"], object["vy"], object["r"])
			obj2 = Circle(bx[0]+list[i]["r"], bx[1]+list[i]["r"], list[i]["vx"], list[i]["vy"], list[i]["r"])




			c.itemconfig(list[i]["o"], outline="green")
			c.itemconfig(object["o"], outline="green")
			A = (obj1.x)-(obj2.x)
			B = (obj1.y)-(obj2.y)
			C = sqrt(A**2+B**2)




			if A==0:
				angle = 0
			elif B==0:
				angle = 90
			else:
				angle =  degrees(asin(abs(B) / abs(C)))+90


			E = (C/list[i]["r"])*A
			D = (C/list[i]["r"])*B


			overlap = sqrt((bx[2]-list[i]["r"] - (obx[2]-object["r"])) ** 2 + (bx[3]-list[i]["r"] - (obx[3]-object["r"])) ** 2)


			if jsonFile['lines']:
				shapeLines.append(c.create_line(obj1.x, obj1.y, obj2.x, obj2.y, fill="grey"))
				shapeLines.append(c.create_line(obj1.x, obj2.y, obj2.x, obj2.y, fill="grey"))
				shapeLines.append(c.create_line(obj2.x, obj1.y, obj2.x, obj2.y, fill="grey"))
				shapeLines.append(c.create_line(obj2.x, obj2.y, obj1.x, obj2.y, fill="grey"))
				shapeLines.append(c.create_text(obj1.x, obj1.y, text=str(angle), fill="grey"))





			if abs(abs(obj1.y) - abs(obj2.y)) > abs(abs(obj1.x) - abs(obj2.x)):
				diff = abs(abs(obj1.x) - abs(obj2.x))/abs(abs(obj1.y) - abs(obj2.y))
			else: 
				diff = abs(abs(obj1.y) - abs(obj2.y))/abs(abs(obj1.x) - abs(obj2.x))


			print(diff, 1-diff, )
			object["vx"] = (obj1.m / obj2.m) * ((obj2.vx * diff) + (obj2.vy * diff))
			object["vy"] = (obj1.m / obj2.m) * ((obj2.vy * (1-diff)) + (obj2.vy *(1- diff)))
			list[i]["vx"] = (obj2.m / obj1.m) * ((obj1.vx * diff) + (obj1.vy * diff))
			list[i]["vy"] = (obj2.m / obj1.m) * ((obj1.vy * (1-diff)) + (obj1.vy *(1- diff)))



			# if ((list[i]["r"]+object["r"])*0.8 >= sqrt((bx[2]-list[i]["r"] - (obx[2]-object["r"])) ** 2 + (bx[3]-list[i]["r"] - (obx[3]-object["r"])) ** 2)):
			# 	c.itemconfig(list[i]["o"], outline="red")
			# 	c.itemconfig(object["o"], outline="red")
			# 	object["vx"] += 10*(ceil((obj1.x - obj2.x)/(abs(obj1.x - obj2.x)+1)*10)-0.5) *(1-diff)
			# 	object["vy"] += 10*(ceil((obj1.y - obj2.y)/(abs(obj1.y - obj2.y)+1)*10)-0.5) *(diff)
			# 	list[i]["vx"] -= 10*(ceil((obj1.x - obj2.x)/(abs(obj1.x - obj2.x)+1)*10)-0.5) *(1-diff)
			# 	list[i]["vy"] -= 10*(ceil((obj1.y - obj2.y)/(abs(obj1.y - obj2.y)+1)*10)-0.5) *(diff)

		else:
			c.itemconfig(list[i]["o"], outline="white")
			c.itemconfig(object["o"], outline="white")


	return (object, list)

stop = False

def render():
	global run, objects, colided, jsonFile, events, energy, lifetime, maxHeight, ballsGraphLine, obj_mem, stop
	loopNum = 0
	ballsGraphLine[0].append(0)
	ballsGraphLine[1].append(len(objects))
	while True:
		try: int(jsonFile['frameRate']); 1/jsonFile['frameRate']
		except: jsonFile['frameRate'] = 1
		for i in range(ceil(jsonFile['frameRate'])):
			time.sleep(0.01616/100)
			window.update()
		if not run: break
		lifetime+=1

		if jsonFile["plot_velocity"]:
			obj_mem[0].append(lifetime)
			obj_mem[1].append(objects)
		if len(obj_mem[0]) > 10000:
			for i in range(len(obj_mem[0])):
				obj_mem[0].pop(0)
				obj_mem[1].pop(0)
				i += 4

		for i in range(len(events)): # this way the events don't occur during the loop and mess with variables im useing
			print(str(events[i]))
			events[i]
		events=[]

		loopNum += 1

		if len(shapeLines) > 0:
		
			if loopNum % 20 == 0:
				loopNum = 0
				c.after_idle(lambda: c.delete(shapeLines.pop(0)))
			if len(shapeLines) > 10:
				c.delete(shapeLines.pop(0))
				c.delete(shapeLines.pop(0))
		objects = sortList(objects)
		colided = []
		energy = 0
		for i in range(len(objects)):
			obj = objects[i]

			energy += abs(obj["vx"]*obj["m"]) + abs(obj["vy"]*obj["m"])


			if str(type(objects[i])) != "<class 'dict'>":print(str(type(objects[i]))); break; 
			obj["vy"] += 2

			# Stokes’ Law: F=6πaηv. (air friction)
			obj["vy"] -= ((6*pi*sqrt(obj["r"])*obj["vy"])/(6*pi*30*40))*jsonFile["air_resistance"] 
			obj["vx"] -= ((6*pi*sqrt(obj["r"])*obj["vx"])/(6*pi*30*40))*jsonFile["air_resistance"]
			obj["vx"] = floor(obj["vx"]*10000)/10000

			obj["vy"] = detect_floor(obj)
			obj["vx"] = detect_walls(obj)

			if len(objects) > 1:
				
				col = colisions(objects, obj)
				objects[i], objects = col[0], col[1]
		if jsonFile["displayTotalEnergy"]:
			energy_string_var.set(f"energy : {floor(energy*10)/10 if jsonFile['displayTotalEnergy'] else 'disabled'}")
			energyGraphLine[0].append(lifetime)
			energyGraphLine[1].append(energy)


		for i in range(len(objects)):
			obj = objects[i]
			c.move(obj["o"], obj["vx"], obj["vy"])
			obx = c.bbox(obj["o"])
			if jsonFile['vectors']:
				c.coords(obj["vector"], obx[0]+obj["r"], obx[1]+obj["r"], obx[0]+obj["vx"]+obj["r"], obx[1]+obj["vy"]+obj["r"])


			else:
				c.coords(obj["vector"], 0, 0, 0, 0)
		if stop: return


# def quitProgram(): # WHY WON'T IT DIE????
# 	window.quit()
# 	raise SystemExit
# 	quit()
# 	exit()
# 	sys.exit()


# window.protocol("WM_DELETE_WINDOW",  lambda: quitProgram())


# |------------------------------------------------------------- unit testing -------------------------------------| 

def test():
	global stop, objects
	stop = True

	testResault = tk.Toplevel(window)
	testResault.title("test results")
	testResault.minsize(300, 300)

	logText= tk.Text(testResault, width = 100)
	logText.pack()
	logText.insert(tk.END, "test results:")


	def log(text="undefined", condition="null", title=""):
		if title != "":
			logText.insert(tk.END,"\n\n"+title)
			return

		textLength = len(text)
		if condition == "passed":
			condition = "   | ✓"
		elif condition == "failed":
			condition = "✗ |   "
		if textLength >= 70:
			testLength = 60
		logText.insert(tk.END,str("\n	"+text+" "*(70-textLength)+condition))


	# test 1
	objects = []
	c.delete("all")
	preTestSpeed = jsonFile['frameRate']
	jsonFile['frameRate'] = 0
	log(title="Object collision along ground with objects of different radi")
	newSphere(30, 300, 600, 0, 0)
	newSphere(10, 350, 600, -30, 0)
	START_VELOCITY = 10
	for i in range(3): render()
	if objects[0]["r"] == 30:
		log("list ordering", "passed")
		BIG = 0
		SMALL = 1
	else:
		log("list ordering", "failed")
		BIG = 1
		SMALL = 0

	if objects[SMALL]["vx"]+objects[SMALL]["vy"] == 0:
		log("smaller obj loseing all velocity", "passed")
	else:
		log(" smaller obj losing all velocity", "failed")

	if objects[BIG]["vy"]+objects[BIG]["vy"] >= 0:
		log("bigger obj getting juggled into air", "failed")
	else:
		log("bigger obj getting juggled into air", "passed")

	if sum([ objects[BIG]["vy"],objects[BIG]["vy"], objects[SMALL]["vy"],objects[SMALL]["vy"]] )> START_VELOCITY:
		log("energy was lost to air friction", "failed")
	else:
		log("energy was lost to air friction", "passed")

	objects = []
	c.delete("all")


	# test 2

	log(title="newtons cradle")
	newSphere(20.0001, 300, 600, 0, 0)
	newSphere(20.0002, 341, 600, 0, 0)
	newSphere(20.0003, 382, 600, 0, 0)
	newSphere(20.0004, 423, 600, 0, 0)
	newSphere(20.0005, 500, 600, -10, 0)

	for i in range(10): render()

	if objects[0]["r"] == 20.0001:
		log("list ordering 0", "passed")
	else:
		log("list ordering 0", "failed")

	objects = []
	c.delete("all")




	jsonFile['frameRate'] = preTestSpeed
	stop = False
	# test 2

while True:
	render()




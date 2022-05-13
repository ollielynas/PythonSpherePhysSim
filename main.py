import tkinter as tk
import time
import random
import json
from math import acos, degrees, pi, sqrt, atan, asin, floor, log, ceil
import matplotlib.pyplot as plt



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

	host.set_xlim(0, lifetime)
	host.set_ylim(0, max(energyGraphLine[1])+(max(energyGraphLine[1])/10))
	par1.set_ylim(0, max(ballsGraphLine[1])*2+(max(ballsGraphLine[1])/20))

	host.set_xlabel("Time")
	host.set_ylabel("Sum Energy")
	par1.set_ylabel("Number of balls")


	lines = [p1, p2]
	host.legend(lines, [l.get_label() for l in lines])

	for ax in [par1, par2]:
		ax.set_frame_on(True)
		ax.patch.set_visible(False)

		plt.setp(ax.spines.values(), visible=False)
		ax.spines["right"].set_visible(True)

	host.yaxis.label.set_color(p1.get_color())
	par1.yaxis.label.set_color(p2.get_color())

	par1.spines["right"].set_edgecolor(p2.get_color())

	host.tick_params(axis='y', colors=p1.get_color())
	par1.tick_params(axis='y', colors=p2.get_color())

	plt.show()

def clear():
    global objects
    objects = []
    c.delete("all")

def openPresetWindow(options):
	global jsonFile, objects # perset window
	presetW= tk.Toplevel(window, bg="black")
	presetW.title = "[15,0]"
	presetW.geometry("300x500"+f"+{options.winfo_x()+325}+{options.winfo_y()}")
	presetW.overrideredirect(True)

	close_button = tk.Button(presetW, text="close", bg="white", fg="red", command=presetW.destroy)
	close_button.pack(anchor=tk.NE, fill='none', padx=0, pady=0)
	dragable = tk.Button(presetW, text="Presets", bg="white", fg="black", width=36)
	dragable.place(x=0,y=0)



	optionList = []
	keys = list(jsonFile["scenes"].keys())



	for i in range(len(keys)):
		command = "clear()"
		for j in range(len(jsonFile["scenes"][keys[i]])):
			scene=jsonFile["scenes"][keys[i]][j]
			scene=[str(x) for x in scene]
			command += f"\nnewSphere({','.join(scene)})"+"#"*i
		optionList.append(tk.Button(presetW, text=keys[i], bg="black", fg="white", command=lambda i=command: exec(i)))
		print(command)
		optionList[i].pack(anchor=tk.W, fill='none', padx=0, pady=0)



	def drag(x,y):
		offset=json.loads(presetW.title)
		presetW.title=f"[{x+offset[0]},{y+offset[1]}]"
		sync_windows()

	dragable.bind("<Button1-Motion>", lambda event: drag(event.x,event.y))




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
	dropdown = tk.OptionMenu(options, levelName, *levelOptions)
	dropdown.pack(anchor=tk.NW, fill=tk.NONE, padx=10, pady=10)

	air_label = tk.Label(options, text="Air Density", bg="black", fg="white")
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

	# def toggle_vectors_graph():
	# 	global jsonFile
	# 	jsonFile["plot_velocity"] = not jsonFile["plot_velocity"]
	# 	vector_button.config(text="plot velocity: "+("On" if jsonFile['plot_velocity'] else "Off"))
	# 	dump()

	# vector_button = tk.Button(options,
    # text="Plot velocity: "+("On" if jsonFile['plot_velocity'] else "Off"),
    # bg="black", fg="white", command=lambda:toggle_vectors_graph())
	# vector_button.pack(anchor=tk.NW, padx=10, pady=10)


	preset_button = tk.Button(options, text="Presets", bg="black", fg="white", command=lambda:openPresetWindow(options))
	preset_button.pack(anchor=tk.NW, padx=10, pady=10)


	graph_button = tk.Button(options, text="Graph", bg="black", fg="white", command=lambda:openGraph())
	graph_button.pack(anchor=tk.NW, padx=10, pady=10)

tools = tk.Button(text="Settings", command=lambda: toolbarWindow(), bg="black" , fg="white", borderwidth=0)
tools.place(x=10, y=10)



# newSphere(30, 80, 100)
# newSphere(30, 100, 200)
# newSphere(20, 500, 100, -10, 0)

# newSphere(30, 100, 400, 20, -20)
# newSphere(25, 500, 450, -20, -23)

newSphere(30, 260, 300, 40, 0)
newSphere(25, 460, 330, -30, 0)

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

			ratio = {
				"x":abs(abs(obj1.x) - abs(obj2.x)),
				"y":abs(abs(obj1.y) - abs(obj2.y))
			}
			total = ratio["x"]+ratio["y"]
			
			if total == 0: return (object, list)

			ratio["x"] /= total
			ratio["y"] /= total

			totalvx = abs(obj1.vx)+abs(obj2.vx)
			totalvy = abs(obj1.vy)+abs(obj2.vy)

			totalE1 = (abs(obj1.vx)+abs(obj1.vy))*(obj1.m / obj2.m)
			totalE2 =  (abs(obj2.vx)+abs(obj2.vy))*(obj2.m / obj1.m)

			object["vx"] = totalE2*ratio["x"]
			object["vy"] = totalE2*ratio["y"]
			list[i]["vx"] = totalE1*ratio["x"]
			list[i]["vy"] = totalE1*ratio["y"]

			if obj1.x < obj2.x:
				object["vx"] *= -1
			else:
				list[i]["vx"] *= -1
    
			if obj1.y < obj2.y:
				object["vy"] *= -1
			else:
				list[i]["vy"] *= -1



			# object["vx"] = (obj2.vx*total)/ratio["x"] + (obj2.vy*total)/ratio["y"]

			# object["vx"] = (obj1.m / obj2.m) * ((obj2.vx * (diff)) + (obj2.vy * (diff)))
			# object["vy"] = (obj1.m / obj2.m) * ((obj2.vy * (diff)) + (obj2.vy *(diff)))
			# list[i]["vx"] = (obj2.m / obj1.m) * ((obj1.vx * (diff)) + (obj1.vy * (diff)))
			# list[i]["vy"] = (obj2.m / obj1.m) * ((obj1.vy * (1-diff)) + (obj1.vy *(1-diff)))





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

			# Stokes’ Law: F=6πaηv. (air friction) to adapt this for one less dimention i square rooted raidus
			obj["vy"] -= 2*((6*pi*obj["r"]*obj["vy"])/(6*pi*20*40))*jsonFile["air_resistance"]
			obj["vx"] -= 2*((6*pi*obj["r"]*obj["vx"])/(6*pi*20*40))*jsonFile["air_resistance"]
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
	testResault.minsize(500, 300)

	logText= tk.Text(testResault, width = 100, height= 50)
	logText.pack()
	logText.insert(tk.END, "test results:")


	def log(text="undefined", condition="null", title=""):
		if title != "":
			logText.insert(tk.END,"\n\n "+title)
			return

		textLength = len(text)
		if condition == "passed":
			condition = "   | ✓"
		elif condition == "failed":
			condition = "✗ |   "
		if textLength >= 70:
			textLength = 60
		logText.insert(tk.END,str("\n	"+text+" "*(70-textLength)+condition))


	# test 1
	objects = []
	c.delete("all")
	preTestSpeed = jsonFile['frameRate']
	preTestFriction = jsonFile['air_resistance']
	jsonFile['air_resistance'] = 1

	jsonFile['frameRate'] = 0
	log(title="unevan collision")
	newSphere(30, 300, 600, 0, 0)
	newSphere(10, 350, 600, -30, 0)
	START_VELOCITY = 10
	for i in range(3): render()
	if objects[0]["r"] == 30:
		log("list ordering", "passed")
		BIG = 0
		SMALL = 1
	else:
		log("correct list ordering", "failed")
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

	for i in range(len(objects)):
		if objects[i]["r"] == 20.0001:
			if objects[i]["vx"] != 0:
				log(text="ball 1 is moveing", condition="passed")
			else:
				log(text="ball 1 is moveing", condition="failed")
		elif objects[i]["r"] == 20.0002:
			if objects[i]["vx"] == 0:
				log(text="ball 2 is not moveing", condition="passed")
			else:
				log(text="ball 2 is not moveing", condition="failed")
		elif objects[i]["r"] == 20.0003:
			if objects[i]["vx"] == 0:
				log(text="ball 3 is not moveing", condition="passed")
			else:
				log(text="ball 3 is not moveing", condition="failed")
		elif objects[i]["r"] == 20.0004:
			if objects[i]["vx"] == 0:
				log(text="ball 4 is not moveing", condition="passed")
			else:
				log(text="ball 4 is not moveing", condition="failed")
		elif objects[i]["r"] == 20.0005:
			if objects[i]["vx"] == 0:
				log(text="ball 5 is not moveing", condition="passed")
			else:
				log(text="ball 5 is not moveing", condition="failed")

	objects = []
	c.delete("all")


	# test 2

	log(title="stack of balls (2)")

	objects = []
	c.delete("all")

	newSphere(30, 300, 500, 0, 0)
	newSphere(20, 300, 200, 0, 0)

	for i in range(50): render()

	if objects[0]["vx"] == 0 and objects[1]["vx"] == 0:
		log(text="balls are balancd", condition="passed")
	else:
		log(text="balls are balancd", condition="failed")

	if objects[0]["vy"] == 0 and objects[1]["vy"] == 0:
		log(text="neither are falling", condition="passed")
	else:
		log(text="neither are falling", condition="failed")

	if c.bbox(objects[0]["o"])[3]-2 > c.bbox(objects[0]["o"])[1]:
		log(text="overlap", condition="failed")
	else:
		log(text="overlap", condition="passed")


	log(title="unbalalanced stack (Left)")

	objects = []
	c.delete("all")

	newSphere(30, 320, 500, 0, 0)
	newSphere(20, 300, 200, 0, 0)

	for i in range(30): render()

	if objects[0]["vx"] == 0 and objects[1]["vx"] == 0:
		log(text="balls are not balancd", condition="failed")
	else:
		log(text="balls are not balancd", condition="passed")

	if objects[0]["vy"] == 0 and objects[1]["vy"] == 0:
		log(text="neither are falling", condition="passed")
	else:
		log(text="neither are falling", condition="failed")

	if (objects[0]["vx"] < 0 and objects[1]["vx"] > 0) or (objects[0]["vx"] > 0 and objects[1]["vx"] < 0):
		log(text="ball move different directions", condition="passed")
	else:
		log(text="ball move different directions", condition="failed")

	log(title="unbalalanced stack (Right)")

	objects = []
	c.delete("all")

	newSphere(30, 300, 500, 0, 0)
	newSphere(20, 320, 200, 0, 0)

	for i in range(30): render()

	if objects[0]["vx"] == 0 and objects[1]["vx"] == 0:
		log(text="balls are not balancd", condition="failed")
	else:
		log(text="balls are not balancd", condition="passed")

	if objects[0]["vy"] == 0 and objects[1]["vy"] == 0:
		log(text="neither are falling", condition="passed")
	else:
		log(text="neither are falling", condition="failed")

	if (objects[0]["vx"] < 0 and objects[1]["vx"] > 0) or (objects[0]["vx"] > 0 and objects[1]["vx"] < 0):
		log(text="ball move different directions", condition="passed")
	else:
		log(text="ball move different directions", condition="failed")

	log(title="air friction")

	objects = []
	c.delete("all")

	newSphere(20, 300, -1500, 0, 0)


	for i in range(60): render()
	if objects[0]["vy"] <= 20:
		log(text="termanal velocity for 20r sphere is 20px/s", condition="passed")
	else:
		log(text="termanal velocity for 20r sphere is 20px/s", condition="failed")

	objects = []
	c.delete("all")

	newSphere(20, 100, -1500, 0, 0)
	newSphere(30, 500, -1500, 0, 0)

	for i in range(60): render()
	if objects[0]["r"] == 20:
		log(text="smaller objects fall faster (not sure if that is good or not)", condition="passed")
	else:
		log(text="smaller objects fall faster (not sure if that is good or not)", condition="failed")

	objects = []
	c.delete("all")
	newSphere(20, 100, -1500, 0, 0)
	for i in range(30): render()
	fallDist1 = c.bbox(objects[0]["o"])[1]
	objects = []
	c.delete("all")
	newSphere(20, 100, -1500, 0, 0)
	jsonFile['air_resistance'] = 10
	for i in range(30): render()
	fallDist2 = c.bbox(objects[0]["o"])[1]

	if fallDist2 < fallDist1:
		log(text="higher air densitys cause objects to fall slower", condition="passed")
	else:
		log(text="higher air densitys cause objects to fall slower", condition="failed")

	jsonFile['air_resistance'] = 1

	log(title="density")
	
	objects = []
	c.delete("all")

	newSphere(20, 300, 300, 5, 0)
	newSphere(30, 370, 300, -5, 0)
	
	for i in range(30): render()


	# |------------------------------------ Keep tests above here ------------------------------------------------|	
	log(title="\n		Test finished")


	objects = []
	c.delete("all")

	testResault["state"] = tk.DISABLED
	jsonFile['frameRate'] = preTestSpeed
	jsonFile['air_resistance'] = preTestFriction
	stop = False



while True:
	render()




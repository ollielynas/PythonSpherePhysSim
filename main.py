import tkinter as tk
import time
import random
import json
from math import acos, degrees, pi, sqrt, atan, asin, floor, log

class Circle:
	def __init__(self, x, y, vx, vy, r):
		self.x = x
		self.y = y
		self.vx = vx
		self.vy = vy
		self.r = r


jsonFile={}

draw_line = False
draw_vector = False
pauseOnColision = False
air_vecosity = 1
shapeLines = []

colided = []

with open('settings.json') as f:
    jsonFile=json.loads(f.read())
    f.close()

window = tk.Tk()       # creating the window object
window.title('Sim')
window.resizable(False, False)


objects = []

c = tk.Canvas(window,width=600, height=600, bg="black")



def newSphere(r, x, y, vx = 0, vy = 0):
    global objects
    objects.append({
		"vx": vx, # velocity
		"vy": vy, # velocity
		"r": r,
		"m": pi*(r**2), # mass
		"o": c.create_oval(x-r, y-r, x+r, y+r, outline="white"),
		"equvector": c.create_line(x, y, x+vx, y+vy, fill="grey", arrow=tk.LAST, width=1),
		"vector": c.create_line(x, y, x+vx, y+vy, fill="orange", arrow=tk.LAST, width=1),
	})


def sync_windows():
	for widget in window.winfo_children(): # Loop through each widget in main window
		if '!toplevel' in str(widget):
			offset=json.loads(widget.title)
			print(widget.title)
			x = window.winfo_x() + window.winfo_width() + offset[0]
			y = window.winfo_y() + offset[1]
			widget.geometry("+%d+%d" % (x,y))
window.bind("<Configure>", lambda event: sync_windows())

def toolbarWindow():
	global air_vecosity, draw_line, draw_vector
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
	air_density_input.insert(tk.END, str(air_vecosity))
	def set_air_density(event):
		global air_vecosity
		try:
			air_vecosity = float(air_density_input.get())
			if float(air_density_input.get()) > 500 or float(air_density_input.get()) < -100:
				air_vecosity = 1
				air_density_input.delete(0, tk.END)
				air_density_input.insert(0, "1")
				return
		except :
			air_vecosity = 1
			insert = air_density_input.index("insert")-1
			air_density_input.delete(insert)
	air_density_input.bind("<KeyRelease>", lambda event:set_air_density(event))
	air_density_input.pack(anchor=tk.NW, padx=10, pady=2)
    
	def toggle_lines():
		global draw_line
		draw_line = not draw_line
		lines_button.config(text="Lines: "+("On" if draw_line else "Off"))

	lines_button = tk.Button(options, text="Lines: "+("On" if draw_line else "Off"), bg="black", fg="white", command=lambda:toggle_lines())
	lines_button.pack(anchor=tk.NW, padx=10, pady=10)

	def toggle_vectors():
		global draw_vector
		draw_vector = not draw_vector
		vector_button.config(text="Vectors: "+("On" if draw_vector else "Off"))

	vector_button = tk.Button(options, text="Vectors: "+("On" if draw_vector else "Off"), bg="black", fg="white", command=lambda:toggle_vectors())
	vector_button.pack(anchor=tk.NW, padx=10, pady=10)




tools = tk.Button(text="Settings", command=lambda: toolbarWindow(), bg="black" , fg="white", borderwidth=0)
tools.place(x=10, y=10)



newSphere(30, 80, 100)
newSphere(30, 100, 200)
newSphere(20, 500, 100, -10, 0)

# newSphere(30, 100, 400, 20, -20)
# newSphere(25, 500, 450, -20, -23)

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
	global objects
	clicked_circle = False
	for i in range(0, len(objects)):
		bx = c.bbox(objects[i]["o"])
		if (objects[i]["r"] >= sqrt((bx[2]-objects[i]["r"] - event.x) ** 2 + (bx[3]-objects[i]["r"] - event.y) ** 2)):
			c.delete((objects[i]["o"]))
			c.delete((objects[i]["vector"]))
			c.delete((objects[i]["equvector"]))
			objects.pop(i)
			clicked_circle = True

	if not clicked_circle:
		newSphere(random.randint(20,50), event.x, event.y)

c.bind("<Button-1>", lambda event:click(event))

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
				print(abs(B) ,"/", abs(C))
				angle =  degrees(asin(abs(B) / abs(C)))+90



			E = (C/list[i]["r"])*A
			D = (C/list[i]["r"])*B


			overlap = sqrt((bx[2]-list[i]["r"] - (obx[2]-object["r"])) ** 2 + (bx[3]-list[i]["r"] - (obx[3]-object["r"])) ** 2)


			if draw_line:
				shapeLines.append(c.create_line(obj1.x, obj1.y, obj2.x, obj2.y, fill="grey"))
				shapeLines.append(c.create_line(obj1.x, obj2.y, obj2.x, obj2.y, fill="grey"))
				shapeLines.append(c.create_line(obj2.x, obj1.y, obj2.x, obj2.y, fill="grey"))
				shapeLines.append(c.create_line(obj2.x, obj2.y, obj1.x, obj2.y, fill="grey"))
				shapeLines.append(c.create_text(obj1.x, obj1.y, text=str(angle), fill="grey"))
			if pauseOnColision:
				window.update()
				time.sleep(5)

			temp = [object["vx"],object["vy"]] 

			if B > 0: xscale = -1 
			else: xscale = 1
			if A > 0: yscale = -1
			else: yscale = 1

			xRatio1 = angle/90 + (angle+90)/90
			xRatio2 = 1-xRatio1

			object["vx"] =	((angle)/90) *list[i]["vx"]* list[i]["m"]/object["m"] + (list[i]["vy"] * list[i]["m"]/object["m"] -  ((angle+90)/90) * list[i]["vy"] * list[i]["m"]/object["m"])
			object["vy"] = ((angle)/90) * list[i]["vy"] * list[i]["m"]/object["m"] + (list[i]["vy"] * list[i]["m"]/object["m"] - ((angle)/90) *list[i]["vx"]* list[i]["m"]/object["m"]) * yscale
			list[i]["vx"] = ((angle)/90) * (temp[0] * object["m"] / list[i]["m"]) + ((temp[1] * object["m"] / list[i]["m"])-((angle+90)/90) * (temp[1] * object["m"] / list[i]["m"]))	* xscale
			list[i]["vy"] = ((angle)/90) * (temp[1] * object["m"] / list[i]["m"]) + ((temp[1] * object["m"] / list[i]["m"])-((angle+90)/90) * (temp[1] * object["m"] / list[i]["m"])) * yscale


		else:
			c.itemconfig(list[i]["o"], outline="white")
			c.itemconfig(object["o"], outline="white")


	return (object, list)

def render():
	global run, objects, colided, air_vecosity
	loopNum = 0
	while True:
		time.sleep(0.01616)
		window.update()
		if not run: break
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
		for i in range(len(objects)):
			obj = objects[i]
			obj["vy"] += 2

			# Stokes’ Law: F=6πaηv. (air friction)
			obj["vy"] -= ((6*pi*sqrt(obj["r"])*obj["vy"])/(6*pi*30*40))*air_vecosity 
			obj["vx"] -= ((6*pi*sqrt(obj["r"])*obj["vx"])/(6*pi*30*40))*air_vecosity
			obj["vx"] = floor(obj["vx"]*10000)/10000

			obj["vy"] = detect_floor(obj)
			obj["vx"] = detect_walls(obj)
			if len(objects) > 1:
				
				col = colisions(objects, obj)
				objects[i], objects = col[0], col[1]
		
		for i in range(len(objects)):
			obj = objects[i]
			c.move(obj["o"], obj["vx"], obj["vy"])
			obx = c.bbox(obj["o"])
			if draw_vector:
				c.coords(obj["vector"], obx[0]+obj["r"], obx[1]+obj["r"], obx[0]+obj["vx"]+obj["r"], obx[1]+obj["vy"]+obj["r"])


				if (abs(obj["vx"]) < 10 and abs(obj["vy"] < 10)):
					ex = log(abs(obj["vx"]))
					c.coords(obj["equvector"], obx[0]+obj["r"], obx[1]+obj["r"], obx[0]+obj["vx"]*ex+obj["r"], obx[1]+obj["vy"]+obj["r"])
				else: c.coords(obj["equvector"], 0, 0, 0, 0)
			else:
				c.coords(obj["equvector"], 0, 0, 0, 0)
				c.coords(obj["vector"], 0, 0, 0, 0)


render()


window.protocol("WM_DELETE_WINDOW",  lambda: quit())
window.mainloop()

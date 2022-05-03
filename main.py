import tkinter as tk
import time
import math
import random


window = tk.Tk()       # creating the window object
window.title('Sim')
# write your code here

objects = []

c = tk.Canvas(window,width=600, height=600, bg="black")



def newSphere(r, x, y):
    global objects
    objects.append({
		"vx": 0, # velocity
		"vy": 0, # velocity
		"r": r,
		"m": 3.14159265*(r**2), # mass
		"o": c.create_oval(x-r, y-r, x+r, y+r, outline="white"),
	})


newSphere(30, 120, 100)
newSphere(30, 100, 200)


def in_circle(center_x, center_y, radius, x, y):
    dist = math.sqrt((center_x - x) ** 2 + (center_y - y) ** 2)
    return dist <= radius
	

def click(event):
	global objects
	clicked_circle = False
	for i in range(0, len(objects)):
		bx = c.bbox(objects[i]["o"])
		if (objects[i]["r"] >= math.sqrt((bx[2]-objects[i]["r"] - event.x) ** 2 + (bx[3]-objects[i]["r"] - event.y) ** 2)):
			c.delete((objects[i]["o"]))
			objects.pop(i)
			clicked_circle = True

	if not clicked_circle:
		newSphere(random.randint(20,50), event.x, event.y)

c.bind("<Button-1>", lambda event:click(event))

c.pack()
run = True

def detect_floor(obj):
	if c.bbox(obj["o"])[3] > 600:
		c.move(obj["o"], 0, -c.bbox(obj["o"])[3] + 600)
		return 0
	return obj["vy"]

def sortList(item_list):
	if len(item_list)-1 == 0: return item_list
	for i in range(0, len(item_list)-1):
		if item_list[i]["vy"]**2+item_list[i]["vx"]**1 < item_list[i+1]["vx"]**2+item_list[i+1]["vy"]**2:
			item_list[i+1], item_list[i] = item_list[i], item_list[i+1]
			i = 0
	return item_list

def colisions(list, object):
	if len(list) <= 1: return
	obx = c.bbox(object["o"])
	for i in range(0, len(list)):
		if list[i] == object: break
		bx = c.bbox(list[i]["o"])
		if (list[i]["r"]+object["r"] >= math.sqrt((bx[2]-list[i]["r"] - (obx[2]-object["r"])) ** 2 + (bx[3]-list[i]["r"] - (obx[3]-object["r"])) ** 2)):
			c.itemconfig(list[i]["o"], outline="green")
			c.itemconfig(object["o"], outline="green")

			temp = [object["vx"],object["vy"]]
			object["vx"] = list[i]["vx"]
			object["vy"] = list[i]["vy"]
			list[i]["vx"] = temp[0]
			list[i]["vy"] = temp[1]

		else:
			c.itemconfig(list[i]["o"], outline="white")
			c.itemconfig(object["o"], outline="white")


	return (object, list)


def render():
	global run, objects
	while True:
		time.sleep(0.01616)
		window.update()
		if not run: break
		objects = sortList(objects)
		for i in range(len(objects)):
			obj = objects[i]
			if obj["vy"] < 20:
				obj["vy"] += 2
			obj["vy"] = detect_floor(obj)
			if len(objects) > 1:
				col = colisions(objects, obj)
				objects[i], objects = col[0], col[1]
		
		for i in range(len(objects)):
			obj = objects[i]
			c.move(obj["o"], obj["vx"], obj["vy"])

render()

window.protocol("WM_DELETE_WINDOW",  lambda: quit())
window.mainloop()

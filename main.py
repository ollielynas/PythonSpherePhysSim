import tkinter as tk
import time
import random
from math import acos, degrees, pi, sqrt, atan, asin, floor


window = tk.Tk()       # creating the window object
window.title('Sim')
# write your code here



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
	})




# newSphere(30, 80, 100)
# newSphere(30, 100, 200)
# newSphere(20, 500, 100, -10, 0)

# newSphere(30, 100, 400, 20, -20)
# newSphere(25, 500, 450, -20, -23)

# newSphere(30, 300, 300)
# newSphere(30, 300, 450)
# newSphere(30, 300, 450, 0, -100)

# newSphere(30, 100, 500, 5)
# newSphere(15, 500, 500, -10)

newSphere(30, 300, 100, 0)
newSphere(30, 320, 500, 0, -30)

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

def sortList(item_list):
	if len(item_list)-1 == 0: return item_list
	for i in range(0, len(item_list)-1):
		if item_list[i]["vy"]**2+item_list[i]["vx"]**1 < item_list[i+1]["vx"]**2+item_list[i+1]["vy"]**2:
			item_list[i+1], item_list[i] = item_list[i], item_list[i+1]
			i = 0
	return item_list

draw_line = True
pauseOnColision = True

shapeLines = []

colided = []

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
			c.itemconfig(list[i]["o"], outline="green")
			c.itemconfig(object["o"], outline="green")
			A = (obx[0]-object["r"])-(bx[0]-list[i]["r"])
			B = (obx[1]-object["r"])-(bx[1]-list[i]["r"])
			C = sqrt(A**2+B**2)


			if A==0:
				angle = 0
			elif B==0:
				angle = 90
			else:
				angle =  degrees(asin(A / C))

			E = (C/list[i]["r"])*A
			D = (C/list[i]["r"])*B

			if (B > 0):
				angle = -angle
    
			if (C < 0):
				angle = -angle
			overlap = sqrt((bx[2]-list[i]["r"] - (obx[2]-object["r"])) ** 2 + (bx[3]-list[i]["r"] - (obx[3]-object["r"])) ** 2)

			if draw_line:
				shapeLines.append(c.create_line(obx[2]-object["r"], obx[3]-object["r"], bx[2]-list[i]["r"], bx[3]-list[i]["r"], fill="grey"))

				shapeLines.append(c.create_line(bx[2]-list[i]["r"], bx[3]-list[i]["r"], bx[2]-list[i]["r"]+D, bx[3]-list[i]["r"], fill="blue"))
				shapeLines.append(c.create_line(bx[2]-list[i]["r"], bx[3]-list[i]["r"], bx[2]-list[i]["r"]-(D-B), bx[3]-list[i]["r"], fill="grey", width="3"))
    
				shapeLines.append(c.create_line(bx[2]-list[i]["r"], bx[3]-list[i]["r"]-5, bx[2]-list[i]["r"]+overlap, bx[3]-list[i]["r"]-5, fill="red", width="3"))
    
				shapeLines.append(c.create_line(bx[2]-list[i]["r"], bx[3]-list[i]["r"], bx[2]-list[i]["r"], bx[3]-list[i]["r"]+E, fill="blue"))
    
				shapeLines.append(c.create_line(bx[2]-list[i]["r"]+D, bx[3]-list[i]["r"], bx[2]-list[i]["r"], bx[3]-list[i]["r"]+E, fill="red"))
				


				shapeLines.append(c.create_text(obx[2]-object["r"], obx[3]-object["r"], text=str(floor(angle*10)/10), fill="grey"))
				
				if pauseOnColision:
					window.update()
			c.move(object["o"], -object["vx"], -object["vy"])
			temp = [object["vx"],object["vy"]] 
			sqrt((bx[2]-list[i]["r"] - (obx[2]-object["r"])) ** 2)*-1
			#c.moveto(object["o"], (obx[2]-object["r"], bx[3]-list[i]["r"] - (obx[3]-object["r"]))*-1)

			object["vx"] = ((angle)/90) *list[i]["vx"]* list[i]["m"]/object["m"] + (list[i]["vy"] * list[i]["m"]/object["m"] -  ((angle+90)/90) * list[i]["vy"] * list[i]["m"]/object["m"])
			object["vy"] = ((angle+90)/90) * list[i]["vy"] * list[i]["m"]/object["m"] + (list[i]["vy"] * list[i]["m"]/object["m"] - ((angle)/90) *list[i]["vx"]* list[i]["m"]/object["m"])
			list[i]["vx"] = ((angle)/90) * (temp[0] * object["m"] / list[i]["m"]) + ((temp[1] * object["m"] / list[i]["m"])-((angle+90)/90) * (temp[1] * object["m"] / list[i]["m"]))
			list[i]["vy"] = ((angle+90)/90) * (temp[1] * object["m"] / list[i]["m"]) + ((temp[1] * object["m"] / list[i]["m"])-((angle+90)/90) * (temp[1] * object["m"] / list[i]["m"]))

		else:
			c.itemconfig(list[i]["o"], outline="white")
			c.itemconfig(object["o"], outline="white")


	return (object, list)

def render():
	global run, objects, colided
	loopNum = 0
	while True:
		time.sleep(0.01616)
		window.update()
		if not run: break
		loopNum += 1

		if len(shapeLines) > 0:
			if loopNum % 10 == 0:
				loopNum = 0
				c.after_idle(lambda: c.delete(shapeLines.pop(0)))
			if len(shapeLines) > 10:
				c.after_idle(lambda: c.delete(shapeLines.pop(0)))
				c.after_idle(lambda: c.delete(shapeLines.pop(0)))
		objects = sortList(objects)
		colided = []
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

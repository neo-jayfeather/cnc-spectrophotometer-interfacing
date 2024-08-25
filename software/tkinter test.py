import tkinter as tk    # tkinter for gui elements
import serial           # serial for comms with CNC
import time             # timing delays
import numpy as np      # array mgmt
import threading        # background processing

s = serial.Serial(port = 'COM8', baudrate = 115200, timeout = 0)   # establish serial connection with COM8 @ 115200 baud rate
currentPos = np.array([float(0),float(0),float(0)]) # i don't remember what this is for
pts = np.array([[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]) #saved 4 point grid
measurePts = [] # i should use this instead of pts since it's the same
inc = 1 # movement increments (in mm)
increments = [0.1, 1, 5, 10, 100] #movement map list

def placeGroup(group): # for when you have a list of tkinter objects to place (the list should be 2d, i.e., x = [[tk.Button(---), x, y]])
    for x in range(len(group)):
        group[x][0].place(x = group[x][1], y = group[x][2])
def set(command): # sets position (absoloute)
    s.write((command + "\r\n").encode())# send bytes, append 13-10 or \r\n (same thing)
    '''while s.in_waiting != 0:
        grbl_out = s.readline()         # read byes for as long as there are bytes in the buffer
        if(grbl_out[len(grbl_out)-2] == 13 and grbl_out[len(grbl_out)-1] == 10 and grbl_out.decode()[:2] == "ok"): #if = ok, print ok
            print(grbl_out.decode().strip())'''
def updatePos(xyz): # update relative position, xyz is a 1d array with 3 items [x,y,z]
    global currentPos
    currentPos = np.round(np.add(currentPos, xyz),4)
    set(f"X{currentPos[0]} Y{currentPos[1]} Z{currentPos[2]}")
def updateInc(): # updates increments for the increment button
    global inc
    for x in range(len(increments)):
        if(inc == increments[x]):
            inc = increments[(x + 1)%len(increments)]
            break
    btn_text.set(f"Increment : {inc}")
def setPos(p):
    global currentPos
    global pts
    pts[p] = currentPos
    ptsText[p].set(f"P{p+1}\n({pts[p][0]},{pts[p][1]},{pts[p][2]})")
def getCurrPos():
    global currPosStr
    while True:
        s.write(b"?")
        while s.in_waiting != 0: # this may cause an infinite loop in a scenario I haven't covered
            time.sleep(0.05)
            grbl_out = s.readline()
            if(grbl_out.decode().strip().split("|")[0] == "<Run" or grbl_out.decode().strip().split("|")[0] == "<Idle"):
                currPosStr.set(grbl_out.decode().strip().split(":")[1].split("|")[0])
getPos = threading.Thread(target=getCurrPos)
def calculateMatrix():
    global pts
    pts[4][0] = inputs[1][0].get("1.0","end-1c") # Y - split
    pts[4][1] = inputs[0][0].get("1.0","end-1c") # X - split
    measurePts = [[0.0,0.0,0.0]*(pts[4][0]+1)*(pts[4][1]+1)] #create array for all future points
    measurePts = np.reshape(np.array(measurePts),(pts[4][0]+1,pts[4][1]+1,3)) # convert to 3D numpy array (x split by y split by 3 coordinates)
    measurePts[0][0] = pts[0] #set corners 1-4
    measurePts[pts[4][0]][0] = pts[1]
    measurePts[0][pts[4][1]] = pts[2]
    measurePts[pts[4][0]][pts[4][1]] = pts[3]
    dist = np.subtract(measurePts[0][pts[4][1]], measurePts[0][0]) #3 number array for distance in cartesian 
    for x in range(pts[4][0]+1):
        measurePts[0][x] = np.add(measurePts[0][0], np.multiply(np.divide(dist,pts[4][0]),x)) # left side
    dist = np.subtract(measurePts[pts[4][0]][pts[4][1]], measurePts[pts[4][0]][0])
    for x in range(pts[4][0]+1):
        measurePts[pts[4][0]][x] = np.add(measurePts[pts[4][0]][0], np.multiply(np.divide(dist,pts[4][0]),x)) # right side
    for y in range(pts[4][0]+1): # fill in middle points
        dist = np.subtract(measurePts[pts[4][0]][y], measurePts[0][y])
        for x in range(pts[4][1]+1):
            measurePts[x][y] = np.add(measurePts[0][y], np.multiply(np.divide(dist,pts[4][1]),x))
    print(measurePts)
    moveToPoints(measurePts)
def moveToPoints(points):
    for y in range(len(points[0])):
        for x in range(len(points)):
            set(f"Z{currentPos[2]+2}")
            set(f"X{points[x][y][0]} Y{points[x][y][1]}")
            set(f"Z{currentPos[2]-2}")
    set(f"Z{currentPos[2]+2}")
    set("X0 Y0")
gui = tk.Tk()
gui.title("CNC GUI Controller")
btn_text = tk.StringVar()
currPosStr = tk.StringVar()
currPosStr.set("0.000, 0.000, 0.000")
gui.geometry("450x350")
ptsText = [tk.StringVar(),tk.StringVar(),tk.StringVar(),tk.StringVar(), tk.StringVar()]
for x in range(len(ptsText)):
    ptsText[x].set(f"P{x+1}")
buttons = [
    [tk.Button(gui, text = "left" , command = lambda : updatePos([-inc, 0, 0]), height = 2, width = 5) , 25, 75], #6 movement buttons
    [tk.Button(gui, text = "up"   , command = lambda : updatePos([0, inc, 0]), height = 2, width = 5)   , 75, 25],
    [tk.Button(gui, text = "right", command = lambda : updatePos([inc, 0, 0]), height = 2, width = 5), 125,75],
    [tk.Button(gui, text = "down" , command = lambda : updatePos([0, -inc, 0]), height = 2, width = 5) , 75, 125],
    [tk.Button(gui, text = "z down" , command = lambda : updatePos([0, 0, -inc]), height = 2, width = 5) , 200, 125],
    [tk.Button(gui, text = "z up" , command = lambda : updatePos([0, 0, inc]), height = 2, width = 5) , 200, 25],
    [tk.Button(gui, textvariable = btn_text, command = lambda : updateInc(), height = 2, width = 12), 200, 75], #Increments button
    [tk.Button(gui, textvariable = ptsText[0], command = lambda : setPos(0), height = 2, width = 10), 25, 175], #p1 - p4 buttons
    [tk.Button(gui, textvariable = ptsText[1], command = lambda : setPos(1), height = 2, width = 10), 125, 175],
    [tk.Button(gui, textvariable = ptsText[2], command = lambda : setPos(2), height = 2, width = 10), 25, 225],
    [tk.Button(gui, textvariable = ptsText[3], command = lambda : setPos(3), height = 2, width = 10), 125, 225],
    [tk.Button(gui, text = "P1", command = lambda : updatePos(np.subtract(np.array(pts[0]),np.array(currentPos))), height = 1, width = 4), 25, 300], # move to p1-p4 buttons
    [tk.Button(gui, text = "P2", command = lambda : updatePos(np.subtract(np.array(pts[1]),np.array(currentPos))), height = 1, width = 4), 72, 300],
    [tk.Button(gui, text = "P3", command = lambda : updatePos(np.subtract(np.array(pts[2]),np.array(currentPos))), height = 1, width = 4), 119, 300],
    [tk.Button(gui, text = "P4", command = lambda : updatePos(np.subtract(np.array(pts[3]),np.array(currentPos))), height = 1, width = 4), 166, 300],
    [tk.Button(gui, textvariable = currPosStr, command = lambda : getCurrPos(), height = 2, width = 15), 300, 75], #get current position
    [tk.Button(gui, text = "CALC", command = lambda : calculateMatrix()), 300, 200] #calculate matrix
]
inputs = [
    [tk.Text(gui, height = 1, width = 10),300,25], #text entries (rows)
    [tk.Text(gui, height = 1, width = 10),300,50]  #cols
]
labels = [
    [tk.Label(gui,text =  "Rows :"), 250, 25], #just plaintext :)
    [tk.Label(gui,text = "Cols :"), 250, 50],
    [tk.Label(gui,text = "Go to :"), 25, 275]
    
]
btn_text.set(f"Increment : {inc}") #update increment button
placeGroup(buttons) #create buttons, inputs and labels
placeGroup(inputs)
placeGroup(labels)
getPos.start()
gui.mainloop()
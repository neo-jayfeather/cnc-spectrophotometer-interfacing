import tkinter as tk #default libs
import serial
import time
import numpy as np
s = serial.Serial('COM8', 115200) #establish serial connection with COM8 @ 115200 baud rate
getPos = np.array([0,0,0]) # these three are for positioning data, will maybe consolidate into a single one later
currentPos = np.array([0,0,0])
pts = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
inc = 1 #increments
increments = [0.1, 1, 5, 10, 100]
lastxyz = [0,0,0]

def get():
    time.sleep(0.25)
    grbl_out = ''
    stop = False
    while (grbl_out != "Grbl 1.1f ['$' for help]" and stop == False):
        s.write("?".encode())
        stop = False
        grbl_out = s.readline()  # Read the available data
        try :
            print(grbl_out.strip().decode().split('|')[1])
            stop = True
        except :
            return(grbl_out.strip().decode().split(":")[0])
def set(command):
    global getPos
    command = command + "\r\n"
    s.write(command.encode()) #send bytes
    while s.in_waiting != 0:
        grbl_out = s.readline() #read bytes
        if(grbl_out[len(grbl_out)-2] == 13 and grbl_out[len(grbl_out)-1] == 10 and grbl_out.decode()[:2] == "ok"):
            print(grbl_out.decode().strip())
        '''if(grbl_out[len(grbl_out)-2] == 13 and grbl_out[len(grbl_out)-1] == 10 and grbl_out.decode()[0] == "<"):
            tempPos = grbl_out.decode().strip().split(":")[1].split("|")[0].split(",")
            tempPos = [float(tempPos[0]),float(tempPos[1]),float(tempPos[2])]
            getPos = np.array(tempPos)'''
    getCurrPos()
            
def updatePos(xyz):
    global lastxyz
    if 'currentPos' not in globals():
        global currentPos
        currentPos = [float(0),float(0),float(0)]
    xyz = np.array(xyz)
    currentPos = np.add(currentPos, xyz)
    set(f"X{currentPos[0]} Y{currentPos[1]} Z{currentPos[2]}")
    if ((np.add(np.add(getPos, xyz), lastxyz) != currentPos).all()): #due to a 2 command input lag
        print("ERROR") # if reported position != software (python) determined position, error
    lastxyz = xyz
def updateInc():
    global inc
    for x in range(len(increments)):
        if(inc == increments[x]):
            inc = increments[(x + 1)%len(increments)]
            break
    '''if(x == 1):
        x = 5
    elif(x == 5):
        x = 10
    elif(x == 10):
        x = 100
    elif(x == 100):
        x = 0.1
    else:
        x = 1'''
    btn_text.set(f"Increment : {inc}")
def setPos(p):
    global currentPos
    global pts
    pts[p] = currentPos
    ptsText[p].set(f"P{p+1}\n({pts[p][0]},{pts[p][1]},{pts[p][2]})")
def getCurrPos():
    global currPosStr
    s.write(b"?")
    time.sleep(0.1)
    flag = False
    while s.in_waiting != 0 and flag == False: # this may cause an infinite loop in a scenario I haven't covered
        grbl_out = s.readline()
        if(grbl_out.decode().strip().split("|")[0] == "<Idle"):
            flag = True
        else:
            s.write(b"?")
        try:
            currPosStr.set(grbl_out.decode().strip().split(":")[1].split("|")[0])
        except:
            flag = True
            currPosStr.set(f"{currentPos[0]}, {currentPos[1]}, {currentPos[2]}")

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
    [tk.Button(gui, text = "left" , command = lambda : updatePos([-inc, 0, 0]), height = 2, width = 5) , 25, 75],
    [tk.Button(gui, text = "up"   , command = lambda : updatePos([0, inc, 0]), height = 2, width = 5)   , 75, 25],
    [tk.Button(gui, text = "right", command = lambda : updatePos([inc, 0, 0]), height = 2, width = 5), 125,75],
    [tk.Button(gui, text = "down" , command = lambda : updatePos([0, -inc, 0]), height = 2, width = 5) , 75, 125],
    [tk.Button(gui, text = "z down" , command = lambda : updatePos([0, 0, -inc]), height = 2, width = 5) , 200, 125],
    [tk.Button(gui, text = "z up" , command = lambda : updatePos([0, 0, inc]), height = 2, width = 5) , 200, 25],
    [tk.Button(gui, textvariable = btn_text, command = lambda : updateInc(), height = 2, width = 12), 200, 75], #Increments button
    [tk.Button(gui, textvariable = ptsText[0], command = lambda : setPos(0), height = 2, width = 10), 25, 175],
    [tk.Button(gui, textvariable = ptsText[1], command = lambda : setPos(1), height = 2, width = 10), 125, 175],
    [tk.Button(gui, textvariable = ptsText[2], command = lambda : setPos(2), height = 2, width = 10), 25, 225],
    [tk.Button(gui, textvariable = ptsText[3], command = lambda : setPos(3), height = 2, width = 10), 125, 225],
    [tk.Button(gui, text = "P1", command = lambda : updatePos(np.subtract(np.array(pts[0]),np.array(currentPos))), height = 1, width = 4), 25, 300],
    [tk.Button(gui, text = "P2", command = lambda : updatePos(np.subtract(np.array(currentPos),np.array(pts[1]))), height = 1, width = 4), 72, 300],
    [tk.Button(gui, text = "P3", command = lambda : updatePos(np.subtract(np.array(currentPos),np.array(pts[2]))), height = 1, width = 4), 119, 300],
    [tk.Button(gui, text = "P4", command = lambda : updatePos(np.subtract(np.array(currentPos),np.array(pts[3]))), height = 1, width = 4), 166, 300],
    [tk.Button(gui, textvariable = currPosStr, command = lambda : getCurrPos()), 300, 75]
]

inputs = [
    [tk.Text(gui, height = 1, width = 15),300,25],
    [tk.Text(gui, height = 1, width = 15),300,50]
]
labels = [
    [tk.Label(gui,text =  "Rows :"), 250, 25],
    [tk.Label(gui,text = "Cols :"), 250, 50],
    [tk.Label(gui,text = "Go to :"), 25, 275]
    
]
btn_text.set(f"Increment : {x}")
for x in range(len(buttons)):
    buttons[x][0].place(x = buttons[x][1], y = buttons[x][2])
for x in range(len(inputs)):
    inputs[x][0].place(x = inputs[x][1], y = inputs[x][2])
for x in range(len(labels)):
    labels[x][0].place(x = labels[x][1], y = labels[x][2])
gui.mainloop()



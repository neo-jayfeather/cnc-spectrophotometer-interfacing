import tkinter as tk
import serial
import time
import numpy as np
s = serial.Serial('COM8', 115200)
pos = np.array([0,0,0])
x = 1
global lastLine
lastLine = None

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
            print(grbl_out.strip().decode())
def set(command):
    command = command + "\r\n"
    s.write(command.encode()) #send bytes
    while s.in_waiting != 0:
        global lastLine
        global counter
        grbl_out = s.readline() #read bytes
        if(lastLine == grbl_out):
            print(grbl_out.strip().decode() + f"({int(counter/2)})", end = "\r")
            counter += 1
        else:
            print("\n" + grbl_out.strip().decode())
            counter =  0
        lastLine = grbl_out      
def updatePos(xyz):
    if 'currentPos' not in globals():
        global currentPos
        currentPos = [0,0,0]
    xyz = np.array(xyz)
    currentPos = np.add(currentPos, xyz)
    set(f"X{currentPos[0]} Y{currentPos[1]} Z{currentPos[2]}")
def updateInc():
    global x
    y = x
    if(y == 1):
        y = 5
    elif(y == 5):
        y = 10
    elif(y == 10):
        y = 100
    else:
        y = 1
    x = y
    a = buttons[6]
    a["text"] = f"Increments : {x}"

    #buttons[6]["text"] = f"Increments : {x}"
gui = tk.Tk()
gui.title("CNC GUI Controller")
gui.geometry("450x350")
buttons = [
    [tk.Button(gui, text = "left" , command = lambda : updatePos([-x, 0, 0])) , 25, 100],
    [tk.Button(gui, text = "up"   , command = lambda : updatePos([0, x, 0]))   , 100, 25],
    [tk.Button(gui, text = "right", command = lambda : updatePos([x, 0, 0])), 175,100],
    [tk.Button(gui, text = "down" , command = lambda : updatePos([0, -x, 0])) , 100, 175],
    [tk.Button(gui, text = "z down" , command = lambda : updatePos([0, 0, -x])) , 300, 175],
    [tk.Button(gui, text = "z up" , command = lambda : updatePos([0, 0, x])) , 300, 25],
    [tk.Button(gui, text = f"Increments : {x}", command = lambda : updateInc()), 300, 100]
]
btn_text = f"Increments: {x}"
for x in range(len(buttons)):
    buttons[x][0].place(x = buttons[x][1], y = buttons[x][2])
gui.mainloop()



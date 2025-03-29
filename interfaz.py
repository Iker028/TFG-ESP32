import tkinter as tk
from tkinter import messagebox
from tkinter import Toplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import time
import threading
import matplotlib.pyplot as plt

arduino=serial.Serial(port='COM6',baudrate=9600,timeout=1)
root=tk.Tk()
root.title("Medición")
root.geometry("400x200")
def TEMP():
    arduino.write(bytes('temperatura','utf-8'))
    time.sleep(1)
    
    temp=arduino.readline()
    temp=temp.decode('utf8')
    temp=temp[:-2]
    result_label.config(text=f"Temperatura={temp} ºC")
def LUM():
    arduino.write(bytes('luminosidad','utf-8'))
    time.sleep(1)
    luz=arduino.readline()
    luz=luz.decode('utf8')
    luz=luz[:-2]
    result_label.config(text=f"Luminosidad={luz} lux")

def MEDIR():
    x=[]
    y=[]
    arduino.write(bytes('medir','utf-8'))
    time.sleep(5)
    stringcsv = arduino.readall().decode('utf-8')
    linea=stringcsv.splitlines()
    for i in range(1,len(linea)):
        x.append(float(linea[i].split(',')[0]))
        y.append(float(linea[i].split(',')[1]))
    
     # Create a new window (frame)
    new_window = Toplevel(root)
    new_window.title("Medicion")
    
    # Create a plot
    fig, ax = plt.subplots(dpi=150)
    ax.plot(x,y)
    ax.set_title("Medición del sensor")
    ax.set_xlabel(r"Voltaje $(V)$")
    ax.set_ylabel(r"Intensidad $(A)$")
    
    # Embed the plot in the new window
    canvas = FigureCanvasTkAgg(fig, master=new_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

def on_enter(e):
    medir_button.config(bg='lightblue')

def on_leave(e):
    medir_button.config(bg='skyblue')
    


temperatura=tk.Button(root,text='Temperatura',command=TEMP,font=('Arial',12))
temperatura.pack(pady=10)



luminosidad=tk.Button(root,text='Luminosidad',command=LUM,font=('Arial',12))
luminosidad.pack(pady=10)

medir_button = tk.Button(root, text="Medir", command=MEDIR,font=('Arial',12))
medir_button.pack(pady=10)

medir_button.bind("<Enter>", on_enter)
medir_button.bind("<Leave>", on_leave)

result_label = tk.Label(root, text="",width=40, anchor="w",font=('Arial',12))
#root.resizable(False, False)
result_label.pack(pady=10)

root.mainloop()



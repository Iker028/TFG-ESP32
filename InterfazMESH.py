import tkinter as tk
from tkinter import ttk  #version mas nueva
from ctypes import windll
from PIL import Image, ImageTk
from serial import SerialException
import matplotlib.colors as mcolors

try:
    import clasestringsMESH as cs
except(SerialException):
    windll.shcore.SetProcessDpiAwareness(1) 
    rootretry=tk.Tk()
    rootretry.title('Error')
    rootretry.geometry('600x150+150+150')
    labelretry=tk.Label(rootretry,text='No se ha encontrado el puerto serie. \n Conecte el dispositivo y vuelva a intentarlo.')
    labelretry.pack(pady=10)
    botonretry=ttk.Button(rootretry,text='OK',command=lambda:rootretry.quit())
    botonretry.pack(pady=10)
    rootretry.mainloop()
    exit()
    



windll.shcore.SetProcessDpiAwareness(1) #para que la letra se vea mejor (sin estar borrosa)

root=tk.Tk()
root.title('Menu')
root.geometry('600x280+150+150')
root.columnconfigure(2,weight=10)
root.rowconfigure(5,weight=10)
root.resizable(False,False)




label1=tk.Label(text='Celdas por módulo: ')
label1.grid(column=0,row=0,padx=5,pady=10,sticky='e')

varceldas=tk.StringVar()
textbox1=ttk.Entry(root,textvariable=varceldas)
textbox1.grid(column=1,row=0,pady=10)

label2=tk.Label(text='Módulos en una string: ')
label2.grid(column=0,row=1,pady=10,padx=5,sticky='e')

varmoduls=tk.StringVar()
textbox2=ttk.Entry(root,textvariable=varmoduls)
textbox2.grid(column=1,row=1,pady=10)

label3=tk.Label(text='Strings totales: ')
label3.grid(column=0,row=2,pady=10,padx=5,sticky='e')

varstrings=tk.StringVar()
textbox3=ttk.Entry(root,textvariable=varstrings)
textbox3.grid(column=1,row=2,pady=10)

def ejecutar(celdastr,modulostr,stringstr):
    celdas=int(celdastr)
    modulos=int(modulostr)
    strings=int(stringstr)
    root.destroy()
    gui=cs.GUI(celdas,modulos,strings).mainloop()
        

        
        

estilobot=ttk.Style()
estilobot.configure("Estilok.TButton",font=('Arial',10,'bold'))
botonok=ttk.Button(root,text='OK',command=lambda:ejecutar(varceldas.get(),varmoduls.get(),varstrings.get()),style="Estilok.TButton")

botonok.grid(column=0,row=3,pady=30)
def return_pressed(event):
    ejecutar(varceldas.get(),varmoduls.get(),varstrings.get())
botonok.bind('<Return>',return_pressed)
textbox3.bind('<Return>',return_pressed)
botoncancel=ttk.Button(root,text='CANCELAR',command=lambda:root.quit(),style='Estilok.TButton')
botoncancel.grid(column=1,row=3,pady=30,padx=10)






root.mainloop()



        
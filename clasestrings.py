import tkinter as tk
from tkinter import ttk  #version mas nueva
from ctypes import windll
from PIL import Image, ImageTk
import serial
import time
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)


class GUI(tk.Tk):
    
    def __init__(self,celdas,modulos,strings):
        super().__init__()
        self.title('PARQUE SOLAR')
        windll.shcore.SetProcessDpiAwareness(1) #para que la letra se vea mejor (sin estar borrosa)
        ylong=self.winfo_screenheight()
        xlong=self.winfo_screenwidth()

        height=int(ylong-50)
        width=int(xlong-50)
        centerx=int(xlong/2-width/2)
        centery=int(ylong/2-height/2)
        self.geometry(f'{width}x{height}+{centerx}+{centery}')

        #para añadir scrollbars
        canvas = tk.Canvas(self)
        scroll_y = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_x = tk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        frame = tk.Frame(canvas)

        # Configurar el canvas y las barras de desplazamiento
        canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        scroll_y.bind('<MouseWheel>',)

        # Actualizar el tamaño del frame para que se ajuste al contenido
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<Up>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Down>", lambda event: canvas.yview_scroll(1, "units"))
        canvas.bind_all("<Left>", lambda event: canvas.xview_scroll(-1, "units"))
        canvas.bind_all("<Right>", lambda event: canvas.xview_scroll(1, "units"))

        # Configurar el grid
        frame.columnconfigure(strings + 1, weight=1)
        frame.rowconfigure(modulos + 1, weight=1)

        #vamos a hacer un grid cuyo numero de columnas sea el numero de strings 
        #y el mumero de filas sea el numero de modulos
        self.columnconfigure(strings+1,weight=1)
        self.rowconfigure(modulos+1,weight=1)

        image = Image.open("modulo.jpg") #al ser JPG hay que hacer esto sino simplemente
        #download_icon= tk.PhotoImage("./download.png")

        image = image.resize((int(width/strings)-23, int(height/modulos)-12), Image.LANCZOS)
        self.modulo_icon = ImageTk.PhotoImage(image)

        for i in range(strings):
            for j in range(modulos):
                Boton(frame,i,j,self.modulo_icon)
        for i in range(strings):
            label=tk.Label(frame,text=f'S{i+1}',font=('Arial',11))
            label.grid(column=i+1,row=0,pady=5)
        for j in range(modulos):
            label=tk.Label(frame,text=f'M{j+1}',font=('Arial',11))
            label.grid(column=0,row=j+1,padx=5,sticky='nsew')


   

class Boton():
    arduino=serial.Serial(port='COM6',baudrate=9600,timeout=1)
    def __init__(self,root,i,j,imagen):
        self.root=root
        self.i=i
        self.j=j
        self.imagen=imagen
        boton=ttk.Button(self.root,image=self.imagen,command=lambda:self.botonfunc(self.i,self.j))
        boton.grid(column=self.i+1,row=self.j+1,padx=5,sticky='nsew')
    
    def botonfunc(self,i,j):
        root2=tk.Tk()
        root2.title('String '+str(i+1)+' Modulo '+str(j+1))
        root2.geometry('500x400+150+150')
        label=tk.Label(root2,text=f'String: {i+1}    Modulo: {j+1}',font=('Arial',15,'bold'))
        label.pack(side=tk.TOP)
        botonIV=ttk.Button(root2,text='Grafico I-V',command=self.graphIV)
        botonIV.pack(anchor='center')

    def graphIV(self):
        root3=tk.Tk()
        root3.title(f'Grafico I-V: S{self.j+1} M{self.i+1}')
        x=[]
        y=[]
        self.arduino.write(bytes('medir','utf-8'))
        time.sleep(5)
        stringcsv = self.arduino.readall().decode('utf-8')
        linea=stringcsv.splitlines()
        for i in range(1,len(linea)):
            x.append(float(linea[i].split(',')[0]))
            y.append(float(linea[i].split(',')[1]))
        fig, ax = plt.subplots(dpi=150)
        ax.plot(x,y)
        ax.set_title(f'I-V sensor S{self.j+1} M{self.i+1}')
        ax.set_xlabel(r"Voltaje $(V)$")
        ax.set_ylabel(r"Intensidad $(A)$")
        figure_canvas = FigureCanvasTkAgg(fig, root3)
        NavigationToolbar2Tk(figure_canvas, root3)
        figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
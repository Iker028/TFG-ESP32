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
    arduino=serial.Serial(port='COM6',baudrate=9600,timeout=1)
    sensores=[]
    modulo_icon=None
    modulo_iconroja=None
    frame=None
    
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
        self.frame = tk.Frame(canvas)

        # Configurar el canvas y las barras de desplazamiento
        canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=self.frame, anchor="nw")

        scroll_y.bind('<MouseWheel>',)

        # Actualizar el tamaño del frame para que se ajuste al contenido
        self.frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<Up>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Down>", lambda event: canvas.yview_scroll(1, "units"))
        canvas.bind_all("<Left>", lambda event: canvas.xview_scroll(-1, "units"))
        canvas.bind_all("<Right>", lambda event: canvas.xview_scroll(1, "units"))

        # Configurar el grid
        self.frame.columnconfigure(strings + 1, weight=1)
        self.frame.rowconfigure(modulos + 1, weight=1)

        #imagenes
        image = Image.open("modulo.jpg")
        image = image.resize((int(width/strings)-23, int(height/modulos)-12), Image.LANCZOS)
        self.modulo_icon = ImageTk.PhotoImage(image)
        imageroja= Image.open("modulorojo.jpg")
        imageroja= imageroja.resize((int(width/strings)-23, int(height/modulos)-12), Image.LANCZOS)
        self.modulo_iconroja= ImageTk.PhotoImage(imageroja)


        #vamos a hacer un grid cuyo numero de columnas sea el numero de strings 
        #y el mumero de filas sea el numero de modulos
        self.columnconfigure(strings+1,weight=1)
        self.rowconfigure(modulos+1,weight=1)
        self.suscribirasensores()
        for i in range(strings):
            label=tk.Label(self.frame,text=f'S{i+1}',font=('Arial',11))
            label.grid(column=i+1,row=0,pady=5)
        for j in range(modulos):
            label=tk.Label(self.frame,text=f'M{j+1}',font=('Arial',11))
            label.grid(column=0,row=j+1,padx=5,sticky='nsew')
    def suscribirasensores(self):
        self.arduino.write(bytes('macs','utf-8'))
        time.sleep(2)
        texto = self.arduino.readall().decode('utf-8')
        macs=texto.splitlines()
        for mac in macs:
            self.arduino.write(bytes(mac+'/getij','utf-8'))
            time.sleep(1)
            ij = self.arduino.readall().decode('utf-8')  
            j=int(ij.split(',')[0])
            i=int(ij.split(',')[1])
            bot=Boton(self.frame,i-1,j-1,self.modulo_icon,self.modulo_iconroja,mac)
            self.sensores.append(bot)
            
            


        
        


    


            
class Boton(GUI):
    def __init__(self,root,i,j,imagen,imagenroja,mac):
        self.root=root
        self.i=i
        self.j=j
        self.imagen=imagen
        self.imagenroja=imagenroja
        self.mac=mac
        self.boton=ttk.Button(self.root,image=self.imagen,command=lambda:self.botonfunc(self.i,self.j))
        self.boton.grid(column=self.i+1,row=self.j+1,padx=5,sticky='nsew')
        
    
    def botonfunc(self,i,j):
        root2=tk.Tk()
        root2.title('String '+str(i+1)+' Modulo '+str(j+1))
        root2.geometry('500x400+150+150')
        label=tk.Label(root2,text=f'String: {i+1}    Modulo: {j+1}',font=('Arial',15,'bold'))
        label.pack(side=tk.TOP)
        labelmac=tk.Label(root2,text=f'Mac: {self.mac}',font=('Arial',12,'bold'))
        labelmac.pack(side=tk.TOP)
        labeltemp=tk.Label(root2,text=f'Temperatura: {self.temp()}',font=('Arial',12,'bold'))
        labeltemp.pack(side=tk.TOP)
        labellum=tk.Label(root2,text=f'Luminosidad: {self.lum()}',font=('Arial',12,'bold'))
        labellum.pack(side=tk.TOP)
        botonIV=ttk.Button(root2,text='Grafico I-V',command=self.graphIV)
        botonIV.pack(anchor='center')
        


    def graphIV(self):
        root3=tk.Tk()
        root3.title(f'Grafico I-V: S{self.j+1} M{self.i+1}')
        x=[]
        y=[]
        GUI.arduino.write(bytes(self.mac+'/IV','utf-8'))
        time.sleep(1)
        stringcsv = GUI.arduino.readall().decode('utf-8')
        linea=stringcsv.splitlines()
        for i in range(1,len(linea)):
            try:
                x.append(float(linea[i].split(',')[0]))
                y.append(float(linea[i].split(',')[1]))
            except(ValueError):
                print(f"dato{i} no representable")
        fig, ax = plt.subplots(dpi=150)
        ax.scatter(x,y)
        ax.grid(True)
        ax.set_title(f'I-V sensor S{self.j+1} M{self.i+1}')
        ax.set_xlabel(r"Voltaje $(V)$")
        ax.set_ylabel(r"Intensidad $(A)$")
        figure_canvas = FigureCanvasTkAgg(fig, root3)
        NavigationToolbar2Tk(figure_canvas, root3)
        figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def temp(self):
        GUI.arduino.write(bytes(self.mac+'/temperatura','utf-8'))
        time.sleep(1)
        temperatura=GUI.arduino.readline()
        temperatura=temperatura.decode('utf-8')
        return float(temperatura)
    
    def lum(self):
        GUI.arduino.write(bytes(self.mac+'/luminosidad','utf-8'))
        time.sleep(1)
        luminosidad=GUI.arduino.readline()
        luminosidad=luminosidad.decode('utf-8')
        if (float(luminosidad)==0.0):
            self.change_image(self.imagenroja)
        else:
            self.change_image(self.imagen)
        return float(luminosidad)
    
    def change_image(self, new_image):
        self.boton.config(image=new_image)
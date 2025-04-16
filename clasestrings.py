import tkinter as tk
from tkinter import ttk  #version mas nueva
from ctypes import windll
from PIL import Image, ImageTk
import scipy as sp
import numpy as np
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
    formula=None
    def __init__(self,root,i,j,imagen,imagenroja,mac):
        self.root=root
        self.i=i
        self.j=j
        self.imagen=imagen
        self.imagenroja=imagenroja
        self.mac=mac
        self.boton=ttk.Button(self.root,image=self.imagen,command=lambda:self.botonfunc(self.i,self.j))
        self.boton.grid(column=self.i+1,row=self.j+1,padx=5,sticky='nsew')
        self.opV=0
        self.opI=0
    
    def botonfunc(self,i,j):
        root2=tk.Tk()
        root2.title('String '+str(i+1)+' Modulo '+str(j+1))
        root2.geometry('500x400+150+150')
        GUI.arduino.write(bytes(self.mac+'/OP','utf-8'))
        time.sleep(1)
        stringcsv = GUI.arduino.readall().decode('utf-8')
        linea=stringcsv.strip().splitlines()
        print(linea)
        self.opV=float(linea[0].split(',')[0])
        self.opI=float(linea[0].split(',')[1])
        label=tk.Label(root2,text=f'String: {i+1}    Modulo: {j+1}',font=('Arial',15,'bold'))
        label.pack(side=tk.TOP)
        labelmac=tk.Label(root2,text=f'Mac: {self.mac}',font=('Arial',12,'bold'))
        labelmac.pack(side=tk.TOP)
        labeltemp=tk.Label(root2,text=f'Temperatura: {self.temp()}',font=('Arial',12,'bold'))
        labeltemp.pack(side=tk.TOP)
        labellum=tk.Label(root2,text=f'Luminosidad: {self.lum()}',font=('Arial',12,'bold'))
        labellum.pack(side=tk.TOP)
        labelop=tk.Label(root2,text=f'Operation point: Vop={self.opV}, Iop={self.opI}',font=('Arial',12,'bold'))
        botonIV=ttk.Button(root2,text='Grafico I-V',command=self.graphIV)
        botonIV.pack(anchor='center')
        botonIVhist=ttk.Button(root2,text='IVhist',command=self.graph_IVhist)
        botonIVhist.pack(anchor='center')


    def graphIV(self):
        root3=tk.Tk()
        root3.title(f'Grafico I-V: S{self.j+1} M{self.i+1}')
        x=[]
        y=[]
        GUI.arduino.write(bytes(self.mac+'/IV','utf-8'))
        time.sleep(1)
        stringcsv = GUI.arduino.readall().decode('utf-8')
        linea=stringcsv.strip().splitlines()
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
        botonajustar=ttk.Button(root3,text="Ajustar",command=lambda:self.curvefit(root3,figure_canvas,y,x))
        botonajustar.pack(side=tk.TOP)
        NavigationToolbar2Tk(figure_canvas, root3)
        figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def graph_IVhist(self):
        root4=tk.Tk()
        root4.title(f'Grafico I-V con histeresis: S{self.j+1} M{self.i+1}')
        xIV=[]
        yIV=[]
        GUI.arduino.write(bytes(self.mac+'/IV','utf-8'))
        time.sleep(1)
        stringcsv = GUI.arduino.readall().decode('utf-8')
        linea=stringcsv.strip().splitlines()
        for i in range(1,len(linea)):
            try:
                xIV.append(float(linea[i].split(',')[0]))
                yIV.append(float(linea[i].split(',')[1]))
            except(ValueError):
                print(f"dato{i} no representable")
        histx=[]
        histy=[]
        GUI.arduino.write(bytes(self.mac+'/histeresis','utf-8'))
        time.sleep(1)
        stringcsv = GUI.arduino.readall().decode('utf-8')
        linea=stringcsv.strip().splitlines()
        for i in range(1,len(linea)):
            try:
                histx.append(float(linea[i].split(',')[0]))
                histy.append(float(linea[i].split(',')[1]))
            except(ValueError):
                print(f"dato{i} no representable")
        fig, ax = plt.subplots(dpi=150)
        ax.scatter(xIV,yIV,label='IV')
        ax.scatter(histx,histy,label='IVhist')
        ax.grid(True)
        ax.set_title(f'I-V sensor S{self.j+1} M{self.i+1}')
        ax.set_xlabel(r"Voltaje $(V)$")
        ax.set_ylabel(r"Intensidad $(A)$")
        ax.legend()
        figure_canvas = FigureCanvasTkAgg(fig, root4)
        NavigationToolbar2Tk(figure_canvas, root4)
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
    
    def _function(I,a,b,c,Rs):
        arg = -b*I + c
        # Return a big penalty where log is invalid
        if np.any(arg <= 0):
            return np.full_like(I, 1e6)
        return a * np.log(arg)-I*Rs
    def _dfunction(I,a,b,c,Rs):
        return -((a*b)/(c-b*I)-Rs)
    def _power(I,a,b,c,Rs):
        return Boton._function(I,a,b,c,Rs)*I
    def _dpower(I,a,b,c,Rs):
        return a*np.log(c-b*I)-I*(2*Rs+(a*b)/(c-b*I))
    
    def _newton(a,b,c,Rs,op):
        max=sp.optimize.newton(func=lambda I:Boton._power(I,a,b,c,Rs),x0=op,fprime=lambda I:Boton._dpower(I,a,b,c,Rs),tol=1e-6,maxiter=10000)
        return max
    def _monte_carlo_newton_curvefit(popt, pcov, op, num_samples=10000):
        # Generar muestras aleatorias de los parámetros usando la matriz de covarianza completa
        samples = np.random.multivariate_normal(mean=popt, cov=pcov, size=num_samples)
        results = []
        for sample in samples:
            a_sample, b_sample, c_sample, Rs_sample = sample
            try:
                # Calcular el máximo usando el método de Newton
                max_value = Boton._newton(a_sample, b_sample, c_sample, Rs_sample, op)
                results.append(max_value)
            except RuntimeError:
            # Si el método de Newton falla, ignorar este caso
                continue
        # Calcular el promedio y la desviación estándar de los resultados
        mean_max = np.mean(results)
        std_max = np.std(results)
        return mean_max, std_max
    
    def curvefit(self,root,figure_canvas,I,V): 
        p0 = [1.0, 0.001, 0.026, 1.0]
        lower_bounds = [0.00000000001, 0.0000000001, 0.0000000001,0.001]  # a > 0, b > 0.01
        upper_bounds = [np.inf,np.inf, np.inf,np.inf]
        popt, pcov = sp.optimize.curve_fit(Boton._function,I, V,maxfev=10000,bounds=(lower_bounds, upper_bounds),p0=p0)
        a=popt[0]
        b=popt[1]
        c=popt[2]      
        Rs=popt[3]
        erra = np.sqrt(pcov[0, 0])
        errb = np.sqrt(pcov[1, 1])
        errc = np.sqrt(pcov[2, 2])
        errRs = np.sqrt(pcov[3, 3])
        Is=1/b
        errIs=(1/b**2)*errb
        Il=(c-1)*Is
        errIl=np.sqrt((Is*errc)**2+(c-1)*errIs**2)
        # Calcular el promedio y la desviación estándar de los resultados
        #mean_Imax, std_Imax = Boton._monte_carlo_newton_curvefit(popt, pcov, self.opI)
        mean_Imax=Boton._newton(a,b,c,Rs,Il)
        mean_Vmax=Boton._function(mean_Imax,*popt)
        #std_Vmax=np.abs(Boton._dfunction(mean_Imax,*popt))*std_Imax
        #MPP
        mpp=mean_Imax*mean_Vmax/(self.opI*self.opV)
        #errmpp=np.sqrt((mean_Imax*std_Vmax)**2+(mean_Vmax*std_Imax)**2)/self.opV*self.opI
        indexmin=np.argmax(I)
        indexmax=np.argmin(I)

        # Crear una nueva figura y eliminar la anterior
        figure_canvas.get_tk_widget().destroy() 
        newfig, newax = plt.subplots(dpi=150)
        newax.scatter(V,I,color='orange',label='Datos',alpha=0.7)
        newax.scatter(self.opV,self.opI,color='purple',label='Punto de operación')
        newax.scatter(mean_Vmax,mean_Imax,label='Punto optimo')
        newax.grid(True)
        newax.set_title(f'I-V sensor S{self.j+1} M{self.i+1}')
        newax.set_xlabel(r"Voltaje $(V)$")
        newax.set_ylabel(r"Intensidad $(A)$")
        if(I[indexmin]<=mean_Imax):
            intinicial=mean_Imax+mean_Imax*0.2
        else:
            intinicial=I[indexmax]
        if(I[indexmax]<=mean_Imax):
            intfinal=I[indexmax]
        else:
            intfinal=mean_Imax-mean_Imax*0.2
        intensity=np.linspace(0,Il,2000)
        voltagefit=Boton._function(intensity,*popt)
        newax.plot(voltagefit,intensity,label=r"$V(I)=nV_t\cdot\ln\left(\frac{I_L-I}{I_s}+1\right)-IR_s$",color='blue')
        newax.legend()
        figure_canvas = FigureCanvasTkAgg(newfig, root)
        NavigationToolbar2Tk(figure_canvas, root)
        figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        rootajuste=tk.Tk()
        rootajuste.title(f"Ajuste S{self.j+1} M{self.i+1}")
        rootajuste.geometry('900x600+150+150')
        rootajuste.resizable(False,False)
        labelIs=tk.Label(rootajuste,text=f"Is: {Is} +/- {errIs}",font=('Arial',12,'bold')).pack(side=tk.TOP)
        labelIl=tk.Label(rootajuste,text=f"IL: {Il} +/- {errIl}",font=('Arial',12,'bold')).pack(side=tk.TOP)
        labelnVt=tk.Label(rootajuste,text=f"nVt: {a} +/- {erra}",font=('Arial',12,'bold')).pack(side=tk.TOP)
        labelRs=tk.Label(rootajuste,text=f"Rs: {Rs} +/- {errRs}",font=('Arial',12,'bold')).pack(side=tk.TOP)
        labeloptimo=tk.Label(rootajuste,text=f"V_optimo = {mean_Vmax}",font=('Arial',12,'bold')).pack(side=tk.TOP)
        labeloptimo=tk.Label(rootajuste,text=f"I_optimo = {mean_Imax}",font=('Arial',12,'bold')).pack(side=tk.TOP)
        labelmpp=tk.Label(rootajuste,text=f"MPP = {mpp}",font=('Arial',12,'bold')).pack(side=tk.TOP)

        

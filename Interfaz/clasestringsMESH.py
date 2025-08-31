import tkinter as tk
from tkinter import ttk  #version mas nueva
from ctypes import windll
from PIL import Image, ImageTk
import scipy as sp
import numpy as np
import serial
from matplotlib import cm
import time
import matplotlib
import matplotlib.pyplot as plt
import tkinter.font as tkFont

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
plt.rcParams.update(plt.rcParamsDefault)
#plt.rcParams['figure.dpi'] = 300
'''
plt.rcParams.update({  # Tamaño del gráfico
    'axes.titlesize': 20,      # Tamaño del título
    'axes.labelsize': 20,      # Tamaño de las etiquetas de los ejes
    'xtick.labelsize': 18,     # Tamaño de los números en el eje x
    'ytick.labelsize': 18,     # Tamaño de los números en el eje y
    'legend.fontsize': 18})
'''

class GUI(tk.Tk):
    nodeid=[]
    arduino= serial.Serial(port='COM9',baudrate=115200,timeout=1)
    sensores=[]
    modulo_icon=None
    modulo_iconroja=None
    frame=None
    dicmacs={}
    
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
        time.sleep(15)
        self.suscribirasensores()
        for i in range(strings):
            label=tk.Label(self.frame,text=f'S{i+1}',font=('Arial',11))
            label.grid(column=i+1,row=0,pady=5)
        for j in range(modulos):
            label=tk.Label(self.frame,text=f'M{j+1}',font=('Arial',11))
            label.grid(column=0,row=j+1,padx=5,sticky='nsew')
    def suscribirasensores(self):
        self.arduino.write(bytes('MACS','utf-8'))
        time.sleep(5)
        texto = self.arduino.readall().decode('utf-8')
        texto=texto.strip()
        macs=texto.splitlines()
        while len(macs)!=4:
            self.arduino.write(bytes('MACS','utf-8'))
            time.sleep(5)
            texto = self.arduino.readall().decode('utf-8')
            texto=texto.strip()
            macs=texto.splitlines()
        for linea in macs:
            if linea==''or linea=='\n':
                continue
            linea=linea.strip()
            linealist=linea.split(',')
            print(linealist)
            self.arduino.write(bytes(linealist[0]+'/getij','utf-8'))
            time.sleep(3)
            ij = self.arduino.readall().decode('utf-8')
            while ij=='' or ij==b'':
                self.arduino.write(bytes(linealist[0]+'/getij','utf-8'))
                time.sleep(3)
                ij = self.arduino.readall().decode('utf-8')
            print(ij.split(','))
            j=int(ij.split(',')[0])
            i=int(ij.split(',')[1])
            bot=Boton(self.frame,i-1,j-1,self.modulo_icon,self.modulo_iconroja,linealist[0])
            self.dicmacs[linealist[0]]=linealist[1]
            self.sensores.append(bot)
            
            


        
        


    


            
class Boton(GUI):
    formula=None
    def __init__(self,root,i,j,imagen,imagenroja,nodeid):
        self.root=root
        self.i=i
        self.j=j
        self.imagen=imagen
        self.imagenroja=imagenroja
        self.nodeid=nodeid
        self.boton=ttk.Button(self.root,image=self.imagen,command=lambda:self.botonfunc(self.i,self.j))
        self.boton.grid(column=self.i+1,row=self.j+1,padx=5,sticky='nsew')
        self.opV=0
        self.opI=0
        GUI.arduino.write(bytes(self.nodeid+'/OP','utf-8'))
        time.sleep(5)
        stringcsv = GUI.arduino.readall().decode('utf-8')
        while stringcsv=='':
            GUI.arduino.write(bytes(self.nodeid+'/OP','utf-8'))
            time.sleep(5)
            stringcsv = GUI.arduino.readall().decode('utf-8')
        linea=stringcsv.strip().splitlines()
        self.opV=float(linea[0].split(',')[0])
        self.opI=float(linea[0].split(',')[1])
        self.stringcsvIV=''
        GUI.arduino.write(bytes(self.nodeid+'/IV','utf-8'))
        time.sleep(5)
        self.stringcsvIV= GUI.arduino.readall().decode('utf-8')
        while self.stringcsvIV=='':
            GUI.arduino.write(bytes(self.nodeid+'/IV','utf-8'))
            time.sleep(5)
            self.stringcsvIV = GUI.arduino.readall().decode('utf-8')
        GUI.arduino.write(bytes(self.nodeid+'/histeresis','utf-8'))
        time.sleep(5)
        self.stringcsvhist = GUI.arduino.readall().decode('utf-8')
        while self.stringcsvhist=='':
            GUI.arduino.write(bytes(self.nodeid+'/histeresis','utf-8'))
            time.sleep(5)
            self.stringcsvhist = GUI.arduino.readall().decode('utf-8')
    
    def botonfunc(self,i,j):
        root2=tk.Tk()
        root2.title('String '+str(i+1)+' Modulo '+str(j+1))
        root2.geometry('500x400+150+150')
        label=tk.Label(root2,text=f'String: {i+1}    Modulo: {j+1}',font=('Arial',15,'bold'))
        label.pack(side=tk.TOP)
        labelmac=tk.Label(root2,text=f'Mac: {GUI.dicmacs[self.nodeid]}',font=('Arial',12,'bold'))
        labelmac.pack(side=tk.TOP)
        labeltemp=tk.Label(root2,text=f'Temperatura: {self.temp()} °C',font=('Arial',12,'bold'))
        labeltemp.pack(side=tk.TOP)
        labellum=tk.Label(root2,text=f'Luminosidad: {self.lum()} Lux',font=('Arial',12,'bold'))
        labellum.pack(side=tk.TOP)
        labelop=tk.Label(root2,text=f'Operation point: Vop={self.opV}, Iop={self.opI}',font=('Arial',12,'bold'))
       
        botonIVhist=ttk.Button(root2,text='Gráfico I-V',command=self.graph_IVhist)
        botonIVhist.pack(anchor='center')


    def graphIV(self):
        root3=tk.Tk()
        root3.title(f'Grafico I-V: S{self.j+1} M{self.i+1}')
        x=[]
        y=[]
        linea=self.stringcsvIV.strip().splitlines()
        for i in range(1,len(linea)):
            try:
                x.append(float(linea[i].split(',')[0]))
                y.append(float(linea[i].split(',')[1]))
            except(ValueError):
                print(f"dato{i} no representable")
        fig, ax = plt.subplots(dpi=150)
        ax.scatter(x,y,label='datos corregidos',color='tab:green',s=200,marker='*')
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
        linea=self.stringcsvIV.strip().splitlines()
        for i in range(1,len(linea)):
            try:
                xIV.append(float(linea[i].split(',')[0]))
                yIV.append(float(linea[i].split(',')[1]))
            except(ValueError):
                print(f"dato{i} no representable")
        # Save xIV and yIV to IV.txt
        with open("IV.txt", "w") as iv_file:
            for x, y in zip(xIV, yIV):
                iv_file.write(f"{x},{y}\n")
        histx=[]
        histy=[]
        linea=self.stringcsvhist.strip().splitlines()
        for i in range(1,len(linea)):
            try:
                histx.append(float(linea[i].split(',')[0]))
                histy.append(float(linea[i].split(',')[1]))
            except(ValueError):
                print(f"dato{i} no representable")
        # Save histx and histy to hist.txt
        with open("hist.txt", "w") as hist_file:
            for x, y in zip(histx, histy):
                hist_file.write(f"{x},{y}\n")
        
        Vmin=min(histx)
        min_index=histx.index(Vmin)

        histirev=histy[0:min_index-1]
        histvrev=histx[0:min_index-1]

        histifw=histy[min_index:]
        histvfw=histx[min_index:]
        
        fig, ax = plt.subplots(dpi=150)
        #ax.scatter(histx,histy,label='Medidas sin corregir')
        ax.plot(histvrev,histirev,linewidth='2',alpha=0.5,label='reversa')
        ax.plot(histvfw,histifw,linewidth='2',alpha=0.5,label='directa')
        ax.scatter(xIV,yIV,label='datos corregidos',color='tab:green',s=200,marker='*')
        ax.scatter(histvrev,histirev,color='tab:blue',s=100,marker='s',label='reversa',alpha=0.2)
        ax.scatter(histvfw,histifw,color='tab:orange',s=100,marker='o',label='directa',alpha=0.2)
        
        #ax.scatter(xIV,yIV,label='Datos corregidos')
        ax.grid(True)
        ax.set_title(f'I-V sensor S{self.j+1} M{self.i+1}')
        ax.set_xlabel(r"Voltaje $(V)$")
        ax.set_ylabel(r"Intensidad $(A)$")
        ax.legend()
        figure_canvas = FigureCanvasTkAgg(fig, root4)
        NavigationToolbar2Tk(figure_canvas, root4)
        figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        #botonajustar=ttk.Button(root4,text="Ajustar",command=lambda:self.curvefit(root4,figure_canvas,yIV,xIV))
        #botonajustar.pack(side=tk.TOP)
        menu_font = tkFont.Font(family="Arial", size=20)
        menu_bar = tk.Menu(root4,font=menu_font)
        root4.config(menu=menu_bar)
        
        # Create a File menu and add items
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Ajuste", command=lambda:self.curvefit(root4,figure_canvas,yIV,xIV))
        menu_bar.add_cascade(
        label="Options",
        menu=file_menu,
        underline=0)
        #file_menu.add_command(label="Open", command=open_file)
    def temp(self):
        GUI.arduino.write(bytes(self.nodeid+'/temperatura','utf-8'))
        time.sleep(2)
        temperatura=GUI.arduino.readline()
        temperatura=temperatura.strip()
        print(temperatura)
        while temperatura=='' or temperatura==b'':
            temperatura=GUI.arduino.readline()
            print(temperatura)
        temperatura=temperatura.decode('utf-8')
        return float(temperatura)
    
    def lum(self):
        GUI.arduino.write(bytes(self.nodeid+'/luminosidad','utf-8'))
        time.sleep(2)
        luminosidad=GUI.arduino.readline()
        while luminosidad=='' or luminosidad==b'':
            luminosidad=GUI.arduino.readline()
        luminosidad=luminosidad.decode('utf-8')
        if (float(luminosidad)==0.0):
            self.change_image(self.imagenroja)
        else:
            self.change_image(self.imagen)
        return float(luminosidad)
    
    def change_image(self, new_image):
        self.boton.config(image=new_image)
    
    def _function(I,params):
        Il, I0, Rs, NVt = params
        arg = -I/I0 + 1+Il/I0
        return NVt*np.log(arg)-I*Rs
    
    def _dfunction(I,params):
        Il, I0, Rs, NVt = params
        arg = -I/I0 + 1+Il/I0
        return NVt*(-1/I0)/arg - Rs
    def _power(I,params):
        return I*Boton._functon(I,params)
    def _dpower(I,params):
        Il, I0, Rs, NVt = params
        b=1/I0
        c=Il/I0+1
        return NVt*np.log(c-b*I)-I*(2*Rs+(NVt*b)/(c-b*I))
    
    def _newton(params,op):
        Il, I0, Rs, NVt = params
        resultado=sp.optimize.root_scalar(f=lambda I:Boton._dpower(I,params),x0=op,xtol=1e-5,maxiter=1000,method='bisect',bracket=[0,Il])
        return resultado.root
    def _monte_carlo(popt, pcov, op, num_samples=1000):
        # Generar muestras aleatorias de los parámetros usando la matriz de covarianza completa
        samples = np.random.multivariate_normal(mean=popt, cov=pcov, size=num_samples)
        resultsI = []
        resultsV=[]
        for sample in samples:
            Il, I0, Rs, NVt = sample
            try:
                max_value = Boton._newton(sample, op)
                if (-max_value/I0 + 1+Il/I0)<0 or Rs<0:
                    continue
                else:
                    resultsI.append(max_value)
                    resultsV.append(Boton._function(max_value,sample))
            except RuntimeError:
                print('hola')
                continue
        # Calcular el promedio y la desviación estándar de los resultados
        mean_Imax = np.mean(resultsI)
        
        std_Imax = np.std(resultsI)
        mean_Vmax = np.mean(resultsV)
        std_Vmax = np.std(resultsV)
        return mean_Imax, std_Imax, mean_Vmax, std_Vmax
    
    def monte_carlo_graph(self,popt, pcov, num_samples):
        # Generar muestras aleatorias de los parámetros usando la matriz de covarianza completa
        samples = np.random.multivariate_normal(mean=popt, cov=pcov, size=num_samples)
        resultsI = []
        resultsV=[]
        for sample in samples:
            # Calcular la curva I-V para cada conjunto de parámetros muestreados
            Il, I0, Rs, NVt = sample
            if Rs>=0:
                I = np.linspace(0,sample[0], 1000)
                V = Boton._function(I,sample)
                resultsI.append(I)
                resultsV.append(V)
        np.array(resultsI)
        np.array(resultsV)
        
        fig,ax=plt.subplots(dpi=150)
        ax.set_title(f'Curvas I-V Monte Carlo: S{self.j+1} M{self.i+1}')
        for Ival, Vval in zip(resultsI, resultsV):
            ax.plot(Vval, Ival, alpha=0.3, color='tab:red')  # Plot each curve with transparency
        ax.set_xlabel("Voltaje (V)")
        ax.set_ylabel("Intensidad (A)")
        I = np.linspace(0,popt[0], 1000)
        V = Boton._function(I,popt)
        ax.plot(V,I,label='Curva optima',color='black',linewidth='5') 
        ax.grid(True)
        ax.legend(loc='lower left')
        rootmontecarlo=tk.Tk()  
        rootmontecarlo.title(f'Curvas I-V Monte Carlo: S{self.j+1} M{self.i+1}')
        figure_canvas = FigureCanvasTkAgg(fig, rootmontecarlo)
        NavigationToolbar2Tk(figure_canvas, rootmontecarlo)
        figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


    def _coste(params,I,V):
        Il, I0, Rs, NVt = params
        dif= I - (Il - I0*(np.exp((V+Rs*I)/NVt)-1))
        return dif 
    
    def curvefit(self,root,figure_canvas,I,V): 
       # p0 = [0.026, 0.001, 0.01, 1.0]
        
        lower_bounds = [0.0001, 1e-20, 0,0] 
        upper_bounds = [200,1e-1, 50, 20]
        initial_params = [7.0, 1e-10, 0.001, 1.0] 
        result= sp.optimize.least_squares(Boton._coste, initial_params, args=(np.array(I), np.array(V)),bounds=(lower_bounds, upper_bounds))
        print(result)
        Il = result.x[0]
        I0 = result.x[1]
        Rs = result.x[2]
        NVt = result.x[3]
        jacobian = result.jac
        residuals = result.fun
        n_params = len(result.x)
        n_data = len(I) 
       
        # Estimate the variance of the residuals
        residual_variance = np.sum(residuals**2) / (n_data - n_params)

        # Covariance matrix approximation
        cov_matrix = np.linalg.inv(jacobian.T @ jacobian) * residual_variance

        # Standard errors (square root of diagonal elements of covariance matrix)
        parameter_errors = np.sqrt(np.diag(cov_matrix))
        errIl = parameter_errors[0]
        errI0 = parameter_errors[1]
        errRs = parameter_errors[2]
        errNVt = parameter_errors[3]
        
        # Calcular el promedio y la desviación estándar de los resultados
        mean_Imax, std_Imax,mean_Vmax,std_Vmax = Boton._monte_carlo(result.x, cov_matrix, self.opI)
        #MPP
        mpp=1-(self.opI*self.opV)/(mean_Imax*mean_Vmax)
        errmpp=np.sqrt((std_Vmax/(mean_Imax*(mean_Vmax)**2))**2+(std_Imax/(mean_Vmax*(mean_Imax)**2))**2)*(self.opV*self.opI)
        indexmin=np.argmax(I)
        indexmax=np.argmin(I)
        Im=Boton._newton(result.x,self.opI) 
        Vm=Boton._function(Im,result.x)

        # Crear una nueva figura y eliminar la anterior
        figure_canvas.get_tk_widget().destroy() 
        newfig, newax = plt.subplots(dpi=150)
        newax.scatter(V,I,label='Datos corregidos',alpha=0.2,s=100,marker='*',color='tab:green')
        newax.scatter(self.opV,self.opI,label='OP',marker='o',color='tab:red',s=50)
        newax.scatter(mean_Vmax,mean_Imax,label='MPP',s=50)
        newax.errorbar(
        mean_Vmax, mean_Imax, 
        xerr=std_Vmax, yerr=std_Imax, 
        fmt='o', color='tab:blue', capsize=5 )

        newax.errorbar(
        self.opV, self.opI, 
        xerr=0.2, yerr=0.01, 
        fmt='o', color='tab:red', capsize=5 )
        #newax.scatter(Vm,Im,label='MPP',marker='o',color='tab:blue')
        newax.grid(True)
        newax.set_title(f'I-V sensor S{self.j+1} M{self.i+1}')
        newax.set_xlabel(r"Voltaje $(V)$")
        newax.set_ylabel(r"Intensidad $(A)$")

        intensity=np.linspace(0,Il,1000)
        voltagefit=Boton._function(intensity,result.x)
        if voltagefit[-1]==-np.inf:
            voltagefit[-1]=0
        newax.plot(voltagefit,intensity,label=r"$V(I)=nV_t\cdot\ln\left(\frac{I_L-I}{I_s}+1\right)-IR_s$",color='green',linestyle='--')
        newax.legend()
        figure_canvas = FigureCanvasTkAgg(newfig, root)
        NavigationToolbar2Tk(figure_canvas, root)
        figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        rootajuste=tk.Toplevel()
        rootajuste.title(f"Ajuste S{self.j+1} M{self.i+1}")
        rootajuste.geometry('900x600+150+150')

        labelajuste=tk.Label(rootajuste,text=f"Parámetros: ",font=('Arial',15,'bold')).pack(side=tk.TOP)
        labelIs=tk.Label(rootajuste,text=f"Is: {I0} +/- {errI0}",font=('Arial',12,'bold'),anchor=tk.W).pack(side=tk.TOP,anchor=tk.W)
        labelIl=tk.Label(rootajuste,text=f"IL: {Il} +/- {errIl}",font=('Arial',12,'bold'),anchor=tk.W).pack(side=tk.TOP,anchor=tk.W)
        labelnVt=tk.Label(rootajuste,text=f"NVt: {NVt} +/- {errNVt}",font=('Arial',12,'bold'),anchor=tk.W).pack(side=tk.TOP,anchor=tk.W)
        labelRs=tk.Label(rootajuste,text=f"Rs: {Rs} +/- {errRs}",font=('Arial',12,'bold'),anchor=tk.W).pack(side=tk.TOP,anchor=tk.W)

        textmontecarl=tk.StringVar()
        text=ttk.Entry(rootajuste,textvariable=textmontecarl)
        botonMonteCarlo=ttk.Button(rootajuste,text='Graficar',command=lambda:Boton.monte_carlo_graph(self,result.x, cov_matrix,int(textmontecarl.get())))
       
        botonMonteCarlo.pack(side=tk.BOTTOM)
        text.pack(side=tk.BOTTOM)
        labelajuste=tk.Label(rootajuste,text=f"Monte Carlo numero de muestras: ",font=('Arial',12,'bold')).pack(side=tk.BOTTOM)
        
        
    
        labelVoperacion=tk.Label(rootajuste,text=f"V_OP: {self.opV:.3f}",font=('Arial',12,'bold'),anchor=tk.W,fg='orange').pack(side=tk.BOTTOM,anchor=tk.W)
        labelIoperacion=tk.Label(rootajuste,text=f"I_OP: {self.opI:.3f}",font=('Arial',12,'bold'),anchor=tk.W,fg='orange').pack(side=tk.BOTTOM,anchor=tk.W) 
        labeloptimo=tk.Label(rootajuste,text=f"V_MPP = {mean_Vmax:.3f} +/- {std_Vmax:.3f}",font=('Arial',12,'bold'),anchor=tk.W,fg='green').pack(side=tk.BOTTOM,anchor=tk.W)
        labeloptimo=tk.Label(rootajuste,text=f"I_MPP = {mean_Imax:.3f} +/- {std_Imax:.3f}",font=('Arial',12,'bold'),anchor=tk.W,fg='green').pack(side=tk.BOTTOM,anchor=tk.W)
        labelmpp=tk.Label(rootajuste,text=f"Desajuste = {mpp:.3f} +/- {errmpp:.3f}",font=('Arial',12,'bold'),anchor=tk.W).pack(side=tk.BOTTOM,anchor=tk.W)
        labelajuste=tk.Label(rootajuste,text=f"Desajuste: ",font=('Arial',15,'bold')).pack(side=tk.BOTTOM)

        

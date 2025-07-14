import tkinter as tk
from tkinter import ttk  #version mas nueva
from ctypes import windll
import serial
import time

class node():
    def __init__(self, nodeId, parent=None,children=None):
        self.nodeId = nodeId
        self.parent = parent
        if parent=='0':
            self.root = True
        else:
            self.root = False
        self.children=children
        if children==['0']:
            self.leaf = True
        else:
            self.leaf = False
    def __eq__(self,other):
        if(self.nodeId == other.nodeId and
           self.parent == other.parent and
           set(self.children) == set(other.children)):
            return True
        else:
            return False

class Tree():
    dicNodes = dict()
    dicletra= dict()
    diccolor={"A": "red", "B": "orange","C": "blue", "D": "green", "E": "gray"}
    canvas = None
    arduino= None
    def __init__(self, rootk, arduino,width, height):
        Tree.arduino = arduino
        arduino.write(bytes('ARBOL','utf-8'))
        time.sleep(1)
        texto = arduino.readall().decode('utf-8')
        for line in texto.split('\n'):
            palabras = line.split(' ')
            if len(palabras) ==6:
                hijos=palabras[5].split(',')
                Tree.dicNodes[palabras[1]]=node(palabras[1],palabras[3],hijos)
        arduino.write(bytes('LETRA','utf-8'))
        time.sleep(1)
        texto=arduino.readall().decode('utf-8')
        for line in texto.split('\n'):
            palabras = line.split()
            if len(palabras)==2:
                Tree.dicletra[palabras[0]]=palabras[1]
        for node_id in Tree.dicNodes:
            if Tree.dicNodes[node_id].root:
                self.root = Tree.dicNodes[node_id]
            
        print(Tree.dicNodes)
        canvas=tk.Canvas(rootk, width=width, height=height, bg='white')
        Tree.canvas=canvas
        self.width = width
        self.height = height
        self.draw_tree(Tree.canvas,Tree.dicNodes, self.root)
    def redraw_tree(self):
        Tree.arduino.write(bytes('ARBOL','utf-8'))
        thisdicNodes=dict()
        time.sleep(1)
        texto = Tree.arduino.readall().decode('utf-8')
        for line in texto.split('\n'):
            palabras = line.split(' ')
            if len(palabras)==6:
                hijos=palabras[5].split(',')
                thisdicNodes[palabras[1]]=node(palabras[1],palabras[3],hijos)
        if thisdicNodes != Tree.dicNodes:
            Tree.dicNodes = thisdicNodes
            for node_id in Tree.dicNodes:
                if Tree.dicNodes[node_id].root:
                    self.root = Tree.dicNodes[node_id]
                break
            arduino.write(bytes('LETRA','utf-8'))
            time.sleep(1)
            texto=arduino.readall().decode('utf-8')
            Tree.dicletra.clear()
            for line in texto.split('\n'):
                palabras = line.split()
                if len(palabras)==2:
                    Tree.dicletra[palabras[0]]=palabras[1]
            Tree.canvas.delete("all")
            print(Tree.dicNodes)
            self.draw_tree(Tree.canvas,Tree.dicNodes, self.root)
    def _tree_depth(node):
        if node.leaf:
            return 1
        max_child_depth = 0
        for child_id in node.children:
            if child_id in Tree.dicNodes:
                child_node = Tree.dicNodes[child_id]
                depth = Tree._tree_depth(child_node, Tree.dicNodes)
            if depth > max_child_depth:
                max_child_depth = depth
        return 1 + max_child_depth
    # Cuenta el número de hojas bajo cada nodo (para espaciar horizontalmente)
    def _count_leaves(node):
        if node.leaf:
            return 1
        total = 0
        for child_id in node.children:
            if child_id == '0':
                continue
            if child_id in Tree.dicNodes:
                total += Tree._count_leaves(Tree.dicNodes[child_id])
        return total if total > 0 else 1
    def _draw_node(node, x, y, x_min, x_max, level_gap,canvas):
        r = 70
        # Dibuja el nodo
        Tree.canvas.create_oval(x - r, y - r, x + r, y + r, fill=Tree.diccolor[Tree.dicletra[node.nodeId]])
        Tree.canvas.create_text(x, y, text=Tree.dicletra[node.nodeId], font=('Arial', 28, 'bold'))
        # Dibuja los hijos
        if node.leaf:
            return
        num_leaves = sum(Tree._count_leaves(Tree.dicNodes[child_id]) for child_id in node.children if child_id != '0' and child_id in Tree.dicNodes)
        if num_leaves == 0:
            return
        leaf_count = 0
        for child_id in node.children:
            if child_id == '0':
                continue
            if child_id in Tree.dicNodes:
                child_leaves = Tree._count_leaves(Tree.dicNodes[child_id])
                # Calcula la posición horizontal del hijo
                child_x_min = x_min + (leaf_count / num_leaves) * (x_max - x_min)
                leaf_count += child_leaves
                child_x_max = x_min + (leaf_count / num_leaves) * (x_max - x_min)
                child_x = (child_x_min + child_x_max) / 2
                child_y = y + level_gap
                # Línea al hijo
                Tree.canvas.create_line(x, y + r, child_x, child_y - r)
                Tree._draw_node(Tree.dicNodes[child_id], child_x, child_y, child_x_min, child_x_max, level_gap,Tree.canvas)

    def draw_tree(self,canvas,dicNodes, root_node):
        width=self.width
        height=self.height
        level_gap = 200
        Tree.canvas.delete("all")
        Tree._draw_node(root_node, width // 2, 100, 50, width - 50, level_gap,Tree.canvas)
        Tree.canvas.pack()


arduino=serial.Serial(port='COM9',baudrate=115200,timeout=1)
time.sleep(10)          # Espera un poco para que el cambio surta efecto
arduino.flushInput()   # Limpia el buffer de entrada si es necesario
root = tk.Tk()
root.title('Arbol de nodos')
windll.shcore.SetProcessDpiAwareness(1) #para que la letra se vea mejor (sin estar borrosa)
ylong=root.winfo_screenheight()
xlong=root.winfo_screenwidth()
height=int(ylong)
width=int(xlong)
centerx=int(xlong/2-width/2)
centery=int(ylong/2-height/2)
root.geometry(f'{width+1000}x{height+700}+{centerx}+{centery}')
arbol=Tree(root,arduino,width+1000,height+700)

def check_serial():
    #if arduino.in_waiting > 0:
     #   print("¡Datos recibidos por el puerto serie!")
    arbol.redraw_tree()  # O cualquier acción que necesites
    root.after(500,check_serial)  # Inicia la comprobación del puerto serie
check_serial()  # Llama a la función para iniciar la comprobación
root.mainloop()



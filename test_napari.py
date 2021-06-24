#import sys
#from PyQt5.QtWidgets import *
from magicgui import magicgui
import napari
from dask_image.imread import imread
import math # used to ensure numbers remain ints
import numpy as np
from numpy.core.fromnumeric import shape
import pandas as pd
from napari_plugin_engine import napari_hook_implementation

def create_points(unit_w,unit_h):
    unit_w = 1906/12 #according to dimensions of closely cropped reference template: 96well.png
    unit_h = 1249/8
    avg_len = (unit_w + unit_h)/2
    unit_cen = math.ceil(avg_len/2) #coordinates of first point in points layer for A1 is (unit_cen, unit_cen)
    col_num = 12 #96 well plate is 8X12; can be adjusted for 384
    row_num = 8

    col = np.arange(1,(col_num*2)+1,2)
    row = np.arange(1,(row_num*2)+1,2)

    row_coord = unit_cen*row
    col_coord = unit_cen*col

    #creating grid for points layer
    xlist = []
    i = 0
    for i in range(len(row_coord)):
        for j in range(len(col_coord)):
            xlist.append([row_coord[i]+95,col_coord[j]+130]) ## is this avg_len? make this scaleable or fix image to be more consistent
        i = i+1
    #adding points    
    points = np.reshape(xlist,(96,2))
    return points

def wells2image(selection): #input is not perfect, selection is redundantly called shapes_layer.data
    #how we convert indices in points to well numbers, output well_dict
    #dragged = False
    #yield
    # on move
    #while event.type == 'mouse_move':
        #print('something') 
        #dragged = True
        #yield
    # on release
    #if dragged:
    
        index2alpha = {
       0: "a",
       1: "b",
       2: "c",
       3: "d",
       4: "e",
       5: "f",
       6: "g",
       7: "h"}
        list_of_wells=[]
        i = 0
        for i in range(0,95): #will scale to 384
            if i%12 == 0:
                where = i/12
        #list_of_wells = index2alpha[where]
        #for each letter make an array/list of letter_range(1,12) 
                j = 1
                for j in range(1,13):
                    list_of_wells.append(f"{index2alpha[where]}{j}")
            i = i + 1
        
        well_dict = dict(zip(list_of_wells,points)) 
    #calculate distance to nearest well, output: wells2image_list 
        from scipy.spatial.distance import cdist
        D = cdist(selection[0],points)
    
        i = 0
        min_index = []
        for i in range (0,4):
            min_index.append(np.where(D[i] == D[i].min()))
        
        well_range = []
        well_range.append(points[min(min_index)])
        well_range.append(points[max(min_index)])
    #there is a bug here
        wells2image_list = []
        for well, array in well_dict.items():
            if any(array[0] == well_range[0][0]) and any(array[1] == well_range[0][0]):
                wells2image_list.append(well)

        index2search = well_range[1][0][1]

        for well, array in well_dict.items():
            if any(array[0] == well_range[1][0]) and array[1] == index2search:
                wells2image_list.append(well)
            
        send2nautilus = list_of_wells[min_index[0][0][0]:min_index[2][0][0]+1] #min of min index and max of min index
    
        return send2nautilus

im_path = '/Users/lena.blackmon/napari-pysero/napari_pysero/96well_background_intermediaryfix.jpeg' # path to plate template
pl_temp = imread(im_path)
viewer = napari.view_image(pl_temp, rgb=True)

points = create_points(unit_w=1906/12,unit_h=1249/8)
points_layer = viewer.add_points(points, size=5) #editable = False ; setting ndim=3 effectively does this as well

shapes_layer = viewer.add_shapes(
        face_color='transparent',
        edge_color='green',
        name='bounding box',
        edge_width = 10,
        ndim=2
    )
shapes_layer.mode = 'add_rectangle'

def shapes():
    np.save('/Users/lena.blackmon/napari-pysero/napari_pysero/shapez',shapes_layer.data)

@napari_hook_implementation
def napari_write_shapes():
    return shapes()

#after selection is made, change mode to select
@shapes_layer.mouse_drag_callbacks.append
def click_drag(layer, event):
    print('begin')
    dragged = False
    yield
    # on move
    while event.type == 'mouse_move':
        print('something') 
        dragged = True
        yield
    # on release
    if dragged:
        selectionn = shapes_layer.data
        napari_write_shapes()       ####### THIS does not work
        print(selectionn) 
        
        #insert calculations
        #send2nautilus = wells2image(selectionn)
        #selection = shapes_layer.data
        #send2nautilus = wells2image(selection)
        shapes_layer.mode = 'select'
        #return send2nautilus
        
    #else:
        #print('clicked!')


from PyQt5.QtWidgets import *
import sys


class SelectionWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        ###### HOW TO IMPLEMENT WELLS2IMAGE
        # convert .txt to numpy array
        

        #label
        layout.addWidget(QLabel("Make selection?"))
        
        # #list
        # self.listwidget = QListWidget()
        # i = 0
        # for i in range(len(self.send2nautilus)): #check whether this accurately indexes
        #     self.listwidget.insertItem(i, self.send2nautilus[i])
        # self.listwidget.clicked.connect(self.clicked)
        # layout.addWidget(self.listwidget)
        #button
        
        
        self.yesb = QPushButton('yes')
        layout.addWidget(self.yesb)
        self.yesb.clicked.connect(self.on_click) ########
        
        
        self.no_button = QPushButton('no')
        layout.addWidget(self.no_button)
        self.no_button.clicked.connect(self.close_napari_pysero)
        
        #qbtn.clicked.connect()
        #integrate magicgui mouse callback?
        
    def on_click(self,qmodelindex):              ############## THIS HAS WORKED
        #if self.ok_button.isChecked():
        #item = self.ok_button.currentItem()    
        #print('text')
        # selection = np.load('shapez.npy')
        # self.send2nautilus = wells2image(selection)
        viewer.window.add_dock_widget(Window())
        
    
    def close_napari_pysero(self,qmodelindex):
        viewer.close()
    
        
    # def clicked(self, qmodelindex):
    #     item = self.listwidget.currentItem()
    #     print(item.text())


class MetadataWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        ###### HOW TO IMPLEMENT WELLS2IMAGE
        # convert .txt to numpy array
        

        #label
        layout.addWidget(QLabel("Make selection?"))
        
        # #list
        # self.listwidget = QListWidget()
        # i = 0
        # for i in range(len(self.send2nautilus)): #check whether this accurately indexes
        #     self.listwidget.insertItem(i, self.send2nautilus[i])
        # self.listwidget.clicked.connect(self.clicked)
        # layout.addWidget(self.listwidget)
        #button
        
        
        self.yesb = QPushButton('yes')
        layout.addWidget(self.yesb)
        self.yesb.clicked.connect(self.on_click) ########
        
        
        self.no_button = QPushButton('no')
        layout.addWidget(self.no_button)
        self.no_button.clicked.connect(self.close_napari_pysero)
        
        #qbtn.clicked.connect()
        #integrate magicgui mouse callback?
        
    def on_click(self,qmodelindex):              ############## THIS HAS WORKED
        #if self.ok_button.isChecked():
        #item = self.ok_button.currentItem()    
        #print('text')
        # selection = np.load('shapez.npy')
        # self.send2nautilus = wells2image(selection)
        viewer.window.add_dock_widget(Window())
        
    
    def close_napari_pysero(self,qmodelindex):
        viewer.close()
    
        
    # def clicked(self, qmodelindex):
    #     item = self.listwidget.currentItem()
    #     print(item.text())


class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)
        ###### HOW TO IMPLEMENT WELLS2IMAGE
        # convert .txt to numpy array
        selection = np.load('shapez.npy')
        self.send2nautilus = wells2image(selection)

        #label
        layout.addWidget(QLabel("Image these wells?"))
        
        #list
        self.listwidget = QListWidget()
        i = 0
        for i in range(len(self.send2nautilus)): #check whether this accurately indexes
            self.listwidget.insertItem(i, self.send2nautilus[i])
        self.listwidget.clicked.connect(self.clicked)
        layout.addWidget(self.listwidget)
        #button
        
        
        self.ok_button = QPushButton('ok')
        layout.addWidget(self.ok_button)
        self.ok_button.clicked.connect(self.on_click) ########
        
        
        self.reselect_button = QPushButton('reselect')
        layout.addWidget(self.reselect_button)
        self.reselect_button.clicked.connect(self.close_napari_pysero)
        
        #qbtn.clicked.connect()
        #integrate magicgui mouse callback?
        
    def on_click(self,qmodelindex):              ############## THIS HAS WORKED
        #if self.ok_button.isChecked():
        #item = self.ok_button.currentItem()    
        #print('text')

        with open('wells2image7.txt', 'w+') as f:
            # write elements of list
            for items in self.send2nautilus:
                f.write('%s\n' %items)
      
            print("File written successfully")
    
    def close_napari_pysero(self,qmodelindex):
        viewer.close()
    
        
    def clicked(self, qmodelindex):
        item = self.listwidget.currentItem()
        print(item.text())
        

viewer.window.add_dock_widget(SelectionWindow())

napari.run()

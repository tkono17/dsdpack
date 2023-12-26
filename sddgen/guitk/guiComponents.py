#------------------------------------------------------------------------
# sddgen.guitk: guiComponents.py
#------------------------------------------------------------------------
import time
import logging
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)

def addScrollBars(widget, parent, xscroll=False, yscroll=False, layout='grid'):
    if yscroll:
        yscrollbar = ttk.Scrollbar(parent, 
                                   orient=tk.VERTICAL,
                                   command=widget.yview)
        widget['yscrollcommand'] = yscrollbar.set
        if layout == 'grid':
            yscrollbar.grid(row=0, column=1, sticky=tk.NS)
        elif layout == 'pack':
            yscrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=True)
    if xscroll:
        xscrollbar = ttk.Scrollbar(parent, 
                                   orient=tk.HORIZONTAL, 
                                   command=widget.xview)
        widget['xscrollcommand'] = xscrollbar.set
        if layout == 'grid':
            xscrollbar.grid(row=1, column=0, sticky=tk.EW)
        elif layout == 'pack':
            xscrollbar.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
    return (xscrollbar, yscrollbar)

#------------------------------------------------------------------------
# FieldEntryPanel
#------------------------------------------------------------------------
class FieldEntryPanel(ttk.Frame):
    def __init__(self, parent, name, value):
        super().__init__(parent)
        self.name = name
        self.value = value
        self.build()
        
    def build(self):
        x1 = ttk.Label(self, text=self.name, width=15)
        x2 = ttk.Entry(self, text=self.value)
        x1.pack(side=tk.LEFT)
        x2.pack(side=tk.LEFT, fill=tk.X, expand=True)
    pass

class FieldEntry:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def createVar(self):
        x = tk.StringVar()
        if type(self.value) == type(''):
            x = tk.StringVar(value=self.value)
        elif type(self.value) == type(1):
            x = tk.IntVar(value=self.value)
        elif type(self.value) == type(1.0):
            x = tk.DoubleVar(value=self.value)
        return x
    
#------------------------------------------------------------------------
# EntryButtonPanel
#------------------------------------------------------------------------
class EntryButtonPanel(ttk.Frame):
    def __init__(self, parent, buttonText):
        super().__init__(parent)
        self.buttonText = buttonText
        self.build()
        
    def build(self):
        entry = ttk.Entry(self)
        button = ttk.Button(self, self.buttonText, width=20)
        entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        button.pack(side=tk.LEFT)
        pass
    pass

class ComboEntryPanel(ttk.Frame):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.build(text)
        
    def build(self, text):
        cbox = ttk.Combobox(self, width=20)
        entry = ttk.Entry(self, text)
        cbox.pack(side=tk.LEFT)
        entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.comboBox = cbox
        self.entry = entry
        pass
    pass

class ParameterGridFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style='panel.TFrame')
        self.fields = []
        self.fieldVars = {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
    def setFields(self, v):
        self.clear()
        self.fields = v
        self.build()

    def addField(self, field):
        self.fields.append(field)

    def build(self):
        n = len(self.fields)
        c1 = ttk.Label(self, text='Field')
        c2 = ttk.Label(self, text='Value')
        c3 = ttk.Label(self, text='Scale')
        c1.grid(row=0, column=0, sticky=tk.EW)
        c2.grid(row=0, column=1, sticky=tk.EW)
        c3.grid(row=0, column=2, sticky=tk.EW)
        for i, field in enumerate(self.fields):
            irow = i + 1
            valuestr = field.createVar()
            self.fieldVars[field.name] = valuestr
            label = ttk.Label(self, text=field.name)
            value = ttk.Entry(self, textvariable=valuestr)
            print(f'{field.name}, {field.value}')
            slider = ttk.Scale(self, from_=0, to=100, orient=tk.HORIZONTAL)
            label.grid(row=irow, column=0, sticky=tk.EW)
            value.grid(row=irow, column=1, sticky=tk.EW)
            slider.grid(row=irow, column=2, sticky=tk.EW)

    def clear(self):
        self.fields.clear()
        self.fieldVars.clear()
        for x in self.winfo_children():
            x.destroy()
        
#------------------------------------------------------------------------
# AnalysisPanel
#------------------------------------------------------------------------
class AnalysisPanel(ttk.LabelFrame):
    def __init__(self, parent, values, text='Analysis'):
        super().__init__(parent, text=text)
        cframe = ttk.Frame(self, height=600)
        cframe.pack(side=tk.TOP, fill=tk.X)

        cframe.grid_columnconfigure(0, weight=1)
        cframe.grid_columnconfigure(1, weight=5)
        cframe.grid_columnconfigure(2, weight=1)

        selectionLabel = ttk.Label(cframe, text='Type: ')
        selectionLabel.grid(row=0, column=0, sticky=tk.NSEW)
        self.selection = ttk.Combobox(cframe, values=values)
        self.selection.grid(row=0, column=1, sticky=tk.NSEW)
        self.runButton = ttk.Button(cframe, text='Run')
        self.runButton.grid(row=0, column=2, sticky=tk.NSEW)
        nameLabel = ttk.Label(cframe, text='Name: ')
        nameLabel.grid(row=1, column=0, sticky=tk.NSEW)
        self.nameEntry = ttk.Entry(cframe)
        self.nameEntry.grid(row=1, column=1, sticky=tk.NSEW)
        
        self.properties = ttk.LabelFrame(self, text='Properties')
        self.properties.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        columns = ('parameter', 'value')
        fields = [FieldEntry('p1', 0.0),
                  FieldEntry('p2', 'hello')]
        self.propertiesFrame = ParameterGridFrame(self.properties)
        self.propertiesFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        #addScrollBars(self.propertiesFrame, self.properties, True, True)
        self.propertiesFrame.setFields(fields)

#------------------------------------------------------------------------
# ImageControlPanel
#------------------------------------------------------------------------
class ImageControlPanel(ttk.Frame):
    def __init__(self, panel, analysis):
        super().__init__(panel, style='P1.TFrame')
        self.analysis = analysis
        self.comboEntries = []
        self.parameters = {}
        self.build()

    def build(self):
        n = self.analysis.nInputImages
        print('ImageControlPanel n = %d' % n)
        self.comboEntries.clear()
        self.parameters.clear()
        #
        if n >= 1 and n <= 10:
            for i in range(n):
                text = ''
                if len(self.analysis.inputImages)>i:
                    text = self.analysis.inputImages[i].name
                x = ComboEntryPanel(self, text)
                x.pack(anchor=tk.NW, fill=tk.X)#, expand=True)
                print('Add combobox')
                self.comboEntries.append(x)
        for k, v in self.analysis.parameters.items():
            x1 = FieldEntryPanel(self, k, str(v))
            x1.pack(side=tk.TOP, fill=tk.X)#, expand=True)
            print('Add parameter field')
            self.parameters[k] = v
        #
        run = ttk.Button(self, text='Run', width=10)
        run.pack(side=tk.LEFT, expand=True)

    pass

class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg='ivory', width=300, height=300)
        xbar, ybar = addScrollBars(self.canvas, self, True, True, layout='none')
        xbar.pack(side=tk.BOTTOM, fill=tk.X)
        ybar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        #
        self.frame = ttk.Frame(self.canvas, style='canvas.TFrame')
        self.canvas.create_window(0, 0, window=self.frame, anchor=tk.NW)
        self.frame.bind('<Configure>', self.onFrameConfigure)
        self.frame.bind('<Button-1>', self.onFrameClick)
        self.canvas.bind('<Button-1>', self.onFrameClick)
        #
        for i in range(20):
            title = f'Label{i}'
            #label = ttk.Label(self.frame, text=title)
            #label.pack(side=tk.TOP, fill=tk.X, expand=True)

    def onFrameConfigure(self, event=None):
        canvas1 = event.widget.master
        canvas1.configure(scrollregion=canvas1.bbox('all'))

    def onFrameClick(self, event=None):
        widget = event.widget
        cw = widget.winfo_width()
        ch = widget.winfo_height()
        logger.info(f'widget {widget} w/h = ({cw}, {ch})')
        
    def frame(self):
        return self.frame

    pass
        
class GalleryPanel(ScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)

    def addImageFrame(self, image, title=''):
        frame = ttk.Frame(self.frame)
        frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        label = ttk.Label(frame, text=title)
        label.pack(anchor=tk.NW, fill=tk.X, expand=True)
        label = ttk.Label(frame, image=image)
        label.pack(anchor=tk.NW, fill=tk.X, expand=True)
    
    def clear(self):
        for w in self.frame.winfo_children():
            w.destroy()
    pass
    

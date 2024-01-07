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
        self.propertiesFrame = PropertyGridFrame(self.properties)
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

    def clear(self):
        for x in self.frame.winfo_children():
            x.destroy()
            
    def frame(self):
        return self.frame

    pass
        
class GalleryPanel(ScrollableFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

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
    

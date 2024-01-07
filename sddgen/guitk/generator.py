#-----------------------------------------------------------------------
# sddgen: guitk.py
#-----------------------------------------------------------------------
import logging
from ..model import Key, Node, ModelFile
from .guiComponents import ScrollableFrame, addScrollBars

logger = logging.getLogger(__name__)

class GuiTkGenerator:
    def __init__(self, modelFile):
        self.modelFile = modelFile
        self.topComponentType = ''
        self.menuStack = []
        pass

    def writeWidget(self, fout, node, parentNode=None, prefix=''):
        parentName = None
        if parentNode: parentName = parentNode.name
        
        fout.write(f'{prefix}{node.name} = {node.tags}({parentName})\n')
        for key in node.keys():
            if key.startswith('_'): continue
            x = node.childNode(key)
            self.writeWidget(fout, x, node, prefix+'  ')
            
    def writeStyles(self, fout, style, prefix):
        pass

    def writePlacement(self, fout, component, style, prefix):
        if style == None: return
        keys = style.keys()
        if 'pack' in keys:
            pack = style.childNode('pack')
            if pack:
                pack = pack.data
                s = f'{component.name}.pack('
                if 'fill' in pack.keys(): s += f'fill={pack["fill"]},'
                if 'side' in pack.keys(): s += f'side={pack["side"]},'
                if 'anchor' in pack.keys(): s += f'anchor={pack["anchor"]},'
                if 'expand' in pack.keys(): s += f'expand={pack["expand"]},'
                if s[-1]==',': s = s[:-1]
                s += ')\n'
                fout.write(f'{prefix}{s}')
        elif 'grid' in keys:
            grid = style.childNode('grid')
            if grid:
                grid = grid.data
                s = f'{component.name}.grid('
                if 'row' in grid.keys(): s += f'row={grid["row"]},'
                if 'column' in grid.keys(): s += f'column={grid["column"]},'
                if 'weight' in grid.keys(): s += f'weight={grid["weight"]},'
                if 'sticky' in grid.keys(): s += f'sticky={grid["sticky"]},'
                if s[-1]==',': s = s[:-1]
                s += ')\n'
                fout.write(f'{prefix}{s}')
        pass

    def writeClassDefLine(self, fout, component, prefix):
        superClasses = ''
        if len(component.tags)>0:
            superClasses = f'({component.tags[0]}'
            for tag in component.tags[1:]:
                superClasses += f',{tag}'
            superClasses += ')'
        fout.write(f'{prefix}class {component.name}{superClasses}:\n')

    def valueCheckTk(self, value):
        x = value
        vtype = value.__class__.__name__
        if vtype == 'str' and \
           not (value.startswith('tk.') or value.startswith('ttk.') ):
            x = f'"{value}"'
        return x
    
    def buildInitArgs(self, component, style):
        args = ''
        clsname = component.tags[0]
        options = component.options
        if clsname == 'ttk.PanedWindow':
            logger.info(f'PanedWindow {component.options}')
            if 'orient' in component.options.keys():
                orient = component.options['orient']
                if not orient.startswith('tk.'): orient = f'"{orient}"'
                args += f', orient={orient}'
        argkeys1 = ('text', 'width', 'height')
        argkeys2 = ('text', 'width', 'height', 'style')
        for k, v in component.options.items():
            if k in argkeys1:
                args += f',{k}={self.valueCheckTk(v)}'
        if style and style.data:
            for k, v in style.data.items():
                if k in argkeys2:
                    args += f',{k}={self.valueCheckTk(v)}'
        return args
    
    def buildAddArgs(self, component, style):
        args = ''
        clsname = component.tags[0]
        options = component.options
        argkeys = ()
        if clsname == 'ttk.PanedWindow':
            argkeys = ('weight')
        #
        for k, v in component.options.items():
            if k in argkeys:
                args += f',{k}={self.valueCheckTk(v)}'
        if style and style.data:
            for k, v in style.data.items():
                if k in argkeys:
                    args += f',{k}={self.valueCheckTk(v)}'
        return args
    
    def writeInstanciate(self, fout, component, parentName, prefix):
        clsname = ''
        style = self.modelFile.styleOfComponent(component)
        if len(component.tags)>0:
            clsname = component.tags[0]
        args = self.buildInitArgs(component, style)
        logger.info(f'{component.name} to instanciate')
        fout.write(f'{prefix}{component.name} = {clsname}({parentName}{args})\n')
        fout.write(f'{prefix}self.{component.name} = {component.name}\n')

    def writeMenuBar(self, fout, menuBar, prefix):
        name = 'menuBar'
        clsname = menuBar.tags[0]
        logger.info(f'{name} N={len(self.menuStack)}')
        fout.write(f'{prefix}root = self.master.master\n')
        fout.write(f'{prefix}menuBar = self\n')
        fout.write(f'{prefix}root.config(menu=self)\n')
        fout.write(f'{prefix}self.menuBar = menuBar\n')

    def writeMenu(self, fout, menu, parentName, prefix):
        name = menu.name
        clsname = menu.tags[0]
        logger.info(f'{name} N={len(self.menuStack)}')
        if len(self.menuStack) == 0:
            fout.write(f'{prefix}self.{name} = {name}\n')
            pass
        elif len(self.menuStack) == 1:
            parentName = self.menuStack[-1]
            fout.write(f'{prefix}{name} = {clsname}({parentName}, tearoff=False)\n')
            fout.write(f'{prefix}{parentName}.add_cascade(label="{name}", menu={name})\n')
            fout.write(f'{prefix}self.{name} = {name}\n')
        else:
            parentName = self.menuStack[-1]
            fout.write(f'{prefix}{parentName}.add_command(label="{name}")\n')

    def checkScrollBars(self, fout, component, parentName, style, prefix):
        xscroll, yscroll = False, False
        if style and style.data:
            skeys = style.data.keys()
            if 'xyscroll' in skeys or 'xscroll' in skeys:
                xscroll = True
            if 'xyscroll' in skeys or 'yscroll' in skeys:
                yscroll = True
        skeys = component.options.keys()
        if 'xyscroll' in skeys or 'xscroll' in skeys:
            xscroll = True
        if 'xyscroll' in skeys or 'yscroll' in skeys:
            yscroll = True
        if xscroll or yscroll:
            fout.write(f'{prefix}{parentName}.rowconfigure(0, weight=1)\n')
            fout.write(f'{prefix}{parentName}.columnconfigure(0, weight=1)\n')
            fout.write(f'{prefix}sddgen.guitk.addScrollBars({component.name}, {parentName}, True, True)\n')
            
    def writeSubComponents(self, fout, component, parentName, prefix):
        ckeys = component.keys()
        # - Create subcomponents
        fout.write(f'{prefix}# create subcomponents of {component.name}\n')
        for k2 in ckeys:
            c2 = component.childNode(k2)
            if c2.tags[0] == 'tk.Menu':
                logger.info(f'Menu {component.name} n in stack {len(self.menuStack)}')
                self.writeMenu(fout, c2, parentName, prefix)
            else:
                self.writeInstanciate(fout, c2, parentName, prefix)
        # - Placement
        for k2 in ckeys:
            c2 = component.childNode(k2)
            style2 = self.modelFile.styleOfComponent(c2)
            self.checkScrollBars(fout, c2, parentName, style2, prefix)
            self.writePlacement(fout, c2, style2, prefix)
        # - add(...) for certain types of components
        if component.tags[0] == 'ttk.PanedWindow':
            logger.info(f'Add sub widget to PanedWindow')
            for k2 in ckeys:
                c2 = component.childNode(k2)
                style = self.modelFile.styleOfComponent(c2)
                args = self.buildAddArgs(c2, style)
                fout.write(f'{prefix}{component.name}.add({c2.name}{args})\n')

        # - Create sub-components recursively
        #fout.write('\n')
        for k2 in ckeys:
            c2 = component.childNode(k2)
            if c2.nChildren() > 0:
                fout.write('\n')
                if c2.tags[0] == 'tk.Menu':
                    logger.info(f'Add menu to stack N(before): {len(self.menuStack)}')
                    self.menuStack.append(c2.name)
                self.writeSubComponents(fout, c2, c2.name, prefix)
                if c2.tags[0] == 'tk.Menu':
                    logger.info(f'Add menu to stack N(after): {len(self.menuStack)}')
                    self.menuStack.pop()
        pass
    
    def writeClassDef(self, fout, component, prefix):
        style = self.modelFile.styleOfComponent(component)
        self.writeClassDefLine(fout, component, prefix)
        fout.write(f'{prefix}  def __init__(self, parent):\n')
        fout.write(f'{prefix}    super().__init__(parent)\n')
        if component.name == self.topNode.tags[0]:
            fout.write(f'{prefix}    self.root = parent\n')
        fout.write(f'{prefix}    self.buildGui()\n')
        if component.name == self.topNode.tags[0]:
            fout.write(f'{prefix}    self.pack(fill=tk.BOTH, expand=True)\n')
        fout.write(f'{prefix}    pass\n\n')
        
        # buildGui()
        fout.write(f'{prefix}  def buildGui(self):\n')
        if component.tags[0] == 'tk.Menu':
            self.writeMenuBar(fout, component, prefix+'    ')
            self.menuStack.append('menuBar')
            
        # - Create sub-components
        ckeys = component.keys()
        self.writeSubComponents(fout, component, 'self', prefix+'    ')
        #self.writeStyles(fout, style, prefix+'  ')
        fout.write(f'{prefix}    pass\n\n')

        if component.tags[0] == 'tk.Menu':
            self.menuStack.pop()

    def generateClassDefs(self, fout):
        logger.info('Generate class definitions')
        components = self.modelFile.componentsNode()
        keys = self.modelFile.componentKeysInOrder()
        for ckey in keys:
            key = Key(ckey)
            content = components.childNode(ckey)
            logger.info(f'{key.name} {key.tags}')
            self.writeClassDef(fout, content, '')

    def generate(self, outputFN):
        self.topNode = self.modelFile.documentNode()
        with open(outputFN, 'w') as fout:
            # Python imports
            fout.write('import tkinter as tk\n')
            fout.write('from tkinter import ttk\n')
            fout.write('import sddgen\n')
            fout.write('from .guiComponents import *\n')
            fout.write('\n')
            
            # Components
            logger.info('Generate class definitions')
            self.generateClassDefs(fout)
            
            # main section
            topComponent = self.modelFile.findComponent(self.topNode.tags[0])
            style = self.modelFile.styleOfComponent(topComponent)
            logger.info(f'Top node {self.topNode.name} tags: {self.topNode.tags}')
            fout.write('if __name__ == "__main__":\n')
            fout.write('  root = tk.Tk()\n')
            if style:
                if 'title' in style.data.keys():
                    fout.write(f'  root.title("{style.data["title"]}")\n')
                if 'geometry' in style.data.keys():
                    fout.write(f'  root.geometry("{style.data["geometry"]}")\n')
            fout.write(f'  style = ttk.Style()\n')
            fout.write(f'  style.configure("r.TFrame", background="red")\n')
            fout.write(f'  style.configure("g.TFrame", background="green")\n')
            fout.write(f'  style.configure("b.TFrame", background="blue")\n')
            fout.write(f'  {self.topNode.name} = {self.topNode.tags[0]}(root)\n')
            fout.write('  root.mainloop()\n')


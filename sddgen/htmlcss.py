#-----------------------------------------------------------------------
# sddgen: htmlcss.py
#-----------------------------------------------------------------------
import logging

from .model import Node, Model, Components, Styles
from .generator import Generator

logger = logging.getLogger(__name__)

class HtmlDocument(Node):
    def __init__(self, node):
        super().__init__(node.key, node.value)
        for key in self.keys():
            x = self.child(key)
            if x:
                self.value[key] = HtmlElement(x)
        pass

class HtmlElement(Node):
    html5Tags = ('body', 'h1', 'h2', 'h3', 'h4', 'h5',
                 'ul', 'li', 'ol',
                 'table', 'tr', 'th', 'td',
                 )
    
    def __init__(self, node):
        super().__init__(node.key, node.value)
        self.htmlTag = 'div'
        if self.typeName in HtmlElement.html5Tags:
            self.htmlTag = self.typeName
        for key in self.keys():
            x = self.child(key)
            if x:
                self.value[key] = HtmlElement(x)
        pass

class CssEntry(Node):
    def __init__(self, node):
        super().__init__(node.key, node.value)
        pass

class HtmlComponents(Components):
    def __init__(self, node):
        super().__init__(node)
        elements = {}
        for k, v in self.value.items():
            x = HtmlElement(v)
            x.isComponent = True
            elements[k] = x
        self.value = elements

    def find(self, name):
        x = None
        if name in self.value.keys():
            x = self.value[name]
        return x
    
    pass
    
class CssStyles(Styles):
    def __init__(self, node):
        super().__init__(node)
    pass
    
class HtmlGenerator(Generator):
    def __init__(self, model=None, output='sddout'):
        super().__init__(model=model, output=output)
        self.header = self.data.header
        self.document = HtmlDocument(self.data.document)
        self.components = HtmlComponents(self.data.components)
        self.styles = CssStyles(self.data.styles)

    def generate(self):
        out = self.outputName
        fn1 = f'{out}.html'
        fn2 = f'{out}.css'
        f1 = open(fn1, 'w')
        f2 = open(fn2, 'w')
        self.writeHtml(f1, fn2)
        self.writeCss(f2)
        f1.close()
        f2.close()

    def writeHtml(self, fout, cssfn, prefix=''):
        title='???'
        fout.write(f'<html>\n')
        fout.write(f'  <head>\n')
        fout.write(f'    <meta charset="utf-8" />\n')
        fout.write(f'    <title>{title}</title>\n')
        fout.write(f'    <link rel="stylesheet" href="{cssfn}" />\n')
        fout.write(f'  </head>\n')
        fout.write(f'  <body>\n')
        for key in self.document.keys():
            logger.debug(f'Write node {key}')
            node = self.document.child(key)
            self.writeElement(fout, node, prefix='    ')
        fout.write(f'  </body>\n')
        fout.write(f'</html>\n')
        pass

    def writeElement(self, fout, node, prefix=''):
        n = node.nChildren()
        htmlTag = node.htmlTag
        tags1 = node.tags
        component = None
        logger.debug(f'{prefix}Element: {htmlTag} n={n} -> {node.typeName}')
        if node.typeName != '':
            component = self.components.find(node.typeName)
            if component:
                logger.debug(f'{prefix}Use component {node.typeName}')
                return self.writeElement(fout, component, prefix)
        #
        if node.isComponent:
            tags1 = [node.name] + tags1
        classList = ' '.join(tags1)
        logger.debug(f'{prefix}classlist={classList}')
        if classList != '':
            fout.write(f'{prefix}<{htmlTag} class="{classList}">\n')
        else:
            fout.write(f'{prefix}<{htmlTag}>\n')
        #
        if n>0:
            keys = node.keys()
            for key in keys:
                node2 = node.child(key)
                if node2:
                    self.writeElement(fout, node2, prefix+'  ')
        #
        fout.write(f'{prefix}</{htmlTag}>\n')

    def writeCss(self, fout):
        for key in self.styles.keys():
            cssEntry = self.styles[key]
            self.writeCssEntry(fout, cssEntry, '')
        pass
    
    def writeCssEntry(self, fout, node, prefix=''):
        name = node.name
        etype = ''
        if not name in HtmlElement.html5Tags:
            etype = '.'
        fout.write(f'{prefix}{etype}{name}' + '{\n')
        for key in node.keys():
            value = node[key].value
            fout.write(f'{prefix}  {key}: {value};\n')
        fout.write(f'{prefix}' + '}\n')
        pass
    

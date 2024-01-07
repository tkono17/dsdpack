#------------------------------------------------------------------------
# sddgen: model.py
#------------------------------------------------------------------------
import os
import re
import yaml
import logging

logger = logging.getLogger(__name__)

# Custom key
class Key:
    def __init__(self, key):
        self.key = key
        self.name, self.options, self.tags = self.decode()

    def stringToValue(self, value):
        x = value
        success = False
        try:
            x = int(value)
            success = True
        except ValueError:
            pass
        if not success:
            try:
                x = float(value)
                success = True
            except ValueError:
                pass
        if not success:
            if value in ('true', 'True', 'TRUE'):
                x = True
            elif value in ('false', 'False', 'FALSE'):
                x = False
        return x

    def decodeOptions(self, kvs):
        options = {}
        re1 = re.compile('^(.+)=(.+)$')
        for kv in kvs:
            mg = re1.match(kv)
            if mg:
                key, value = mg.group(1), mg.group(2)
                options[key] = self.stringToValue(value)
        return options

    def decode(self):
        key = self.key
        #logger.info(f'Decode key: {key}')
        re0 = re.compile('^(.+)$')
        re1 = re.compile('^(.+)\[(.*)\]$')
        re2 = re.compile('^(.+)\{(.*)\}$')
        re12 = re.compile('^(.+)\[(.*)\]\{(.*)\}$')

        name = ''
        tags = []
        options = {}
        # a[]{}
        mg = re12.match(key)
        if mg:
            #logger.info(f'match 12: {mg.groups()}')
            name = mg.group(1)
            options = self.decodeOptions(mg.group(2).split(','))
            tags = mg.group(3).split(',')
            return (name, options, tags)
        # a[]
        mg = re1.match(key)
        if mg:
            #logger.info(f'match 1: {mg.groups()}')
            name = mg.group(1)
            options = self.decodeOptions(mg.group(2).split(','))
            return (name, options, tags)
        # a{}
        mg = re2.match(key)
        if mg:
            #logger.info(f'match 2: {mg.groups()}')
            name = mg.group(1)
            tags = mg.group(2).split(',')
            return (name, options, tags)
        # a
        mg = re0.match(key)
        if mg:
            #logger.info(f'match 0: {mg.groups()}')
            name = mg.group(1)
            return (name, options, tags)
        return (name, options, tags)

# Node with tags and options
class Node:
    def __init__(self, data, key=None):
        self.data = data
        self.key = key
        self.name = ''
        self.tags = ''
        #
        if key and key!='':
            key1 = Key(key)
            self.name, self.options, self.tags = key1.decode()
        self.checkContent()

    def checkContent(self):
        if self.isScalarType():
            if self.isStringType():
                self.typeName = self.data
                
    def allTags(self):
        tags = list(self.tags)
        keys = self.keys()
        for k in keys:
            c = self.childNode(k)
            if c:
                for tag in c.tags:
                    if tag not in tags:
                        tags.append(tag)
        return tags

    def optionKeys(self):
        return self.options.keys()
    
    def allOptionKeys(self):
        okeys = self.options.keys()
        keys = self.keys()
        for k in keys:
            c = self.childNode(k)
            if c:
                okeys2 = c.optionKeys()
                for k2 in okeys2:
                    if k2 not in okeys:
                        okeys.append(k2)
        return okeys

    def allOptionValuesOf(self, optionKey):
        values = []
        if optionKey in self.options.keys():
            values.append(self.options[optionKey])
        keys = self.keys()
        for k in keys:
            c = self.childNode(k)
            if c:
                values2 = c.allOptionValuesOf(optionKey)
                for v2 in values2:
                    if v2 not in values:
                        values.append(v2)
        return values

    def nChildren(self):
        n = 0
        if self.isContainerType():
            n = len(self.data)
        return n
    
    def keys(self):
        keys = []
        if self.isObjectType():
            tag1 = '_orderedKeys'
            keys0 = self.data.keys()
            if tag1 in keys0:
                keys1 = self.data[tag1]
                name2key = {}
                for k in keys0:
                    key1 = Key(k)
                    name, options, tags = key1.decode()
                    if name in keys1:
                        name2key[name] = k
                for k in keys1:
                    keys.append(name2key[k])
            else:
                keys = list(filter(lambda x: not x.startswith('_'), self.data.keys()) )
            print('KEYS=', keys)
        elif self.isArrayType():
            keys = list(range(self.nChildren()))
        return keys
    
    def setValue(self, value):
        if type(value).__name__ == 'str' and \
           self.typeName == '': # and len(self.tags) == 0:
            self.typeName = value
        self.data = value

    def dataType(self):
        return type(self.data).__name__
    
    def isScalarType(self):
        return self.dataType() in ('int', 'float', 'str', 'bool')
    
    def isIntegerType(self):
        return self.dataType() == 'int'
    
    def isFloatType(self):
        return self.dataType() == 'float'
    
    def isStringType(self):
        return self.dataType() == 'str'
    
    def isBoolType(self):
        return self.dataType() == 'bool'
    
    def isArrayType(self):
        return self.dataType() == 'list'
    
    def isObjectType(self):
        return self.dataType() == 'dict'

    def isContainerType(self):
        return self.isArrayType() or self.isObjectType()

    def childNode(self, key):
        return Node(self[key], key)

    def items(self):
        if self.isObjectType():
            return self.data.items()
        else:
            return []
        
    def __getitem__(self, key):
        if self.isArrayType() or self.isObjectType():
            if self.isObjectType() and key not in self.data.keys():
                logger.error(f'Key error {key}, available={self.data.keys()}')
            return self.data[key]
        else:
            return None
    pass

def createNode(m, key=''):
    '''Create a Node from a Python object'''
    vnode = Node(key)
    tm = type(m)
    if tm == type(0) or tm == type(1.0) or tm == type(''):
        vnode.setValue(m)
    elif tm == type([]):
        value = []
        for i, node in enumerate(m):
            x = createNode(node, i)
            value.append(x)
        vnode.setValue(value)
    elif tm == type({}):
        value = {}
        for k, v in m.items():
            x = createNode(v, k)
            value[x.name] = x
            vnode.setValue(value)
    return vnode

class Header(Node):
    def __init__(self, data):
        super().__init__(data)
        #
        self.name = ''
        self.version = ''
        self.modelType = ''
        self.author = ''
        self.date = None
        self.setHeader(data)
        
    def setHeader(self, headerData):
        keys = headerData.keys()
        if 'name' in keys:
            self.name = headerData['name']
        if 'version' in keys:
            self.version = headerData['version']
        if 'modelType' in keys:
            self.modelType = headerData['modelType']
        if 'author' in keys:
            self.author = headerData['author']
        if 'date' in keys:
            dtstring = headerData['date']
            try:
                self.date = datetime.datetime.fromisoformat(dtstring)
            except ValueError:
                logger.error(f'{dtstring} does not look like a datetime format')
        
    def documentKey(self):
        key = 'document'
        if 'documentKey' in self.data.keys():
            key = self.data['documentKey']
        return key
    
    def componentsKey(self):
        key = 'components'
        if 'componentsKey' in self.data.keys():
            key = self.data['componentsKey']
        return key
    
    def stylesKey(self):
        key = 'styles'
        if 'stylesKey' in self.data.keys():
            key = self.data['stylesKey']
        return key

class ModelFile:
    def __init__(self, fileName=''):
        self.filePath = fileName
        self.header = None
        self.document = None
        self.documentKey = ''
        self.components = None
        self.styles = None

    def load(self):
        self.data = None
        if os.path.exists(self.filePath):
            with open(self.filePath, 'r') as f:
                self.data = yaml.load(f, Loader=yaml.SafeLoader)
        if self.data == None:
            logger.error(f'Cannot load sdd model from {self.filePath}')
            return
        #
        if 'header' in self.data.keys():
            self.header = Header(self.data['header'])
        if self.header:
            self.readContents()

    def readContents(self):
        topKeys = self.data.keys()
        dkey = self.header.documentKey()
        for key in topKeys:
            node = Node(None)
            key1 = Key(key)
            name, options, tags = key1.decode()
            if name == dkey:
                self.document = self.data[key]
                self.documentKey = key
                break
        key = self.header.componentsKey()
        if key in topKeys:
            self.components = self.data[key]
        key = self.header.stylesKey()
        if key in topKeys:
            self.styles = self.data[key]

    def findComponent(self, name):
        x = None
        for k, c in self.components.items():
            ckey = Key(k)
            if ckey.name == name:
                x = Node(c, k)
                break
        return x
            
    def findStyle(self, name):
        x = None
        for k, s in self.styles.items():
            skey = Key(k)
            if skey.name == name:
                x = Node(s, k)
                break
        return x

    def styleOfComponent(self, component):
        style = self.findStyle(component.name)
        return style
    
    def documentNode(self):
        logger.info(f'documentkey: {self.documentKey}')
        return Node(self.document, self.documentKey)
    
    def componentsNode(self):
        logger.info(f'CKEY:{self.header.componentsKey()}')
        return Node(self.components, self.header.componentsKey())
        
    def stylesNode(self):
        return Node(self.styles, self.header.stylesKey)
    
    def componentKeysInOrder(self):
        v = self.componentsNode()
        v2 = []
        keys = v.keys()
        for k in keys:
            c = v.childNode(k)
            if c==None:
                v2.insert(0, k)
                continue
            tags = c.allTags()
            imatch = -1
            for tag in tags:
                for i2, cname2 in enumerate(v2):
                    if cname2 == tag and i2 > imatch:
                        imatch = i2
            if imatch >= 0:
                v2.insert(imatch+1, k)
            else:
                v2.insert(0, k)
        return v2

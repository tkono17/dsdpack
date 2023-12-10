#!/usr/bin/env python3

import os
import argparse
import logging
import dslot

logger = logging.getLogger(__name__)

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFile', dest='inputFile',
                        type=str, default='', 
                        help='Input configuration file name')
    return parser.parse_args()

def run(args):
    data = None
    if os.path.exists(args.inputFile):
        data = dslot.ModelFile(args.inputFile)
        data.load()
    gen = None
    if data:
        print(data.header)
        print(data.document)
        print(data.components)
        print(data.styles)
        #gen = HtmlGenerator(model=data)
    if gen:
        gen.generator()
    gen = dslot.GuiTk(data)
    gen.generate('a.py')
    pass

if __name__ == '__main__':
    args = parseArgs()
    logging.basicConfig(level=logging.INFO, format='%(levelname)8s  %(message)8s')
    run(args)
    

#!/usr/bin/env python3
#------------------------------------------------------------------------
# structdd: sddgen.py
#------------------------------------------------------------------------

import yaml
import json
import argparse
import logging
import structdd

logger = logging.getLogger(__name__)

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file', dest='inputFile',
                        type=str, default='', 
                        help='Input filename (.yaml)')
    parser.add_argument('-o', '--output-file', dest='outputFile',
                        type=str, default='', 
                        help='Output filename')
    parser.add_argument('-l', '--logLevel', dest='logLevel',
                        type=str, default='INFO', 
                        help='Log level (ERROR|WARNING|INFO|DEBUG)')
    return parser.parse_args()

def logLevel(slevel):
    level = 'INFO'
    if slevel == 'ERROR':
        level = logging.ERROR
    elif slevel == 'WARNING':
        level = logging.WARNING
    elif slevel == 'INFO':
        level = logging.INFO
    elif slevel == 'DEBUG':
        level = logging.DEBUG
    else:
        logger.warning('Given log level %s is not valid, using INFO' % slevel)
    return level

def run(args):
    gen = None
    dtype = 'NOT_SPECIFIED'
    with open(args.inputFile, 'r') as f:
        data = structdd.Model(args.inputFile)
        data.load()
        dtype = data.header.documentType
        logger.info(f'dtype = {dtype}')
        if dtype == 'HTML+CSS':
            logger.info('HTML+CSS generator')
            gen = structdd.HtmlGenerator(model=data)
        elif dtype == 'Tkinter':
            gen = structdd.TkGenerator(model=data)
    if gen:
        logger.info(f'Generate output dtype={dtype}')
        gen.filenameIn = args.inputFile
        gen.generate()
        #print(json.dumps(data, indent=2))
    else:
        logger.error(f'No generator found for data type {dtype}')
        
if __name__ == '__main__':
    args = parseArgs()

    level = logLevel(args.logLevel)
    logging.basicConfig(level=level,
                        format='%(name)-20s %(levelname)-8s %(message)s')
                        
    
    logger.info('Running sddgen.py')

    run(args)
    
    

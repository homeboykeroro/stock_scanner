
import os
from pathlib import Path
import configparser
import sys

if getattr(sys, 'frozen', False):
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    ROOT_DIR = Path(__file__).parent.parent.parent

filename = os.path.join(ROOT_DIR, 'config.ini')

configParser= configparser.ConfigParser()
configParser.read(filename)

def isint(val): 
    try: 
        parsed_val = int(val) 
        result = True
    except ValueError: 
        result = False 
    
    return result
 
def isfloat(val):  
    try: 
        parsed_val = float(val) 
        result = True
    except ValueError: 
        result = False
         
    return result

def is_bool(val):
    result = False
    is_str = isinstance(val, str)
    
    if is_str:
        if val == 'True' or val == 'False':
            result = True
            
    return result

#https://medium.com/nerd-for-tech/python-configparser-a-comprehensive-guide-%EF%B8%8F-36331be5244f
def get_config(section: str, key: str):
    try:
        result = configParser[section][key]
        
        if isint(result):
            result = int(result)
        elif isfloat(result):
            result = float(result)
        elif is_bool(result):
            if result == 'True':
                result = True
            elif result == 'False':
                result = False
    
    except Exception:
        result = None
        
    return result    
        
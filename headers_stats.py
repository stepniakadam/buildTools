from optparse import OptionParser
import json
from builtins import RuntimeError
import os

parser = OptionParser()
parser.add_option("-p", "--path", dest="path",
                  help="Path to compile_commands.json file", metavar="FILE")

(options, args) = parser.parse_args()

def get_args(entry):
    args = []
    if "command" in entry:
        args = entry["command"].split(' ')
    elif "arguments" in entry:
        args = entry["arguments"]
    else:
        raise RuntimeError("No command or argument found in compile_commands.json!")    
    
    return args

# Compiler specific!!!
def get_include_dirs(entry):    
    args = get_args(entry)
    
    include_paths = []
    for idx in range(len(args)):
        val = args[idx]
        
        if "-I" == val:
            include_paths.append(args[idx + 1])
        elif "-I" in val:
            include_paths.append(val[2:])
        else:
            pass
            
    return include_paths

def get_headers_names(cpp_path, include_dirs):
    headers_names = []

    with open(cpp_path, "r") as f:
        for l in f.readlines():
            if "#include" in l:
                n = l[len("#include"):]
                n = n.replace('"', '')
                n = n.replace('<', '')
                n = n.replace('>', '')
                n = n.strip()
                headers_names.append(n)
            else:
                pass
    
    return headers_names

def get_headers_paths(header_paths, cpp_path, include_dirs):    
    headers_names = get_headers_names(cpp_path, include_dirs)
    
    for h_name in headers_names:
        for i_dir in include_dirs:
            p = os.path.join(i_dir, h_name)
            if os.path.exists(p) and p not in header_paths:
                header_paths.add(p)                

with open(options.path, "r") as f_content:
    commands = json.load(f_content)
        
    res = {}
    val = {"headers" : []}
    header_paths = set()
    
    for entry in commands:
        cpp = entry["file"]
        if cpp not in res:
            d = get_include_dirs(entry)
            get_headers_paths(header_paths, cpp, d)
    
    print(header_paths)         
    
    
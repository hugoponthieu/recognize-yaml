#!/bin/python3
import re

def is_yaml_line(line):
    # Basic check for YAML elements like key-value pairs or sequences
    key_value_pattern = re.compile(r'^\s*\w+:\s*.*$')  # Matches key-value
    sequence_pattern = re.compile(r'^\s*-\s+.*$')      # Matches sequences
    
    return key_value_pattern.match(line) or sequence_pattern.match(line)

def recognize_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if not is_yaml_line(line.strip()):
                    return False
        return True
    except IOError:
        print("File could not be read.")
        return False

# Usage
file_path = 'deployment.yaml'
if recognize_yaml(file_path):
    print("The file is a YAML.")
else:
    print("The file is not a valid YAML.")

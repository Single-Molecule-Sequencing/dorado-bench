#!/usr/bin/env python3
# Generate pod5.yml from subdirectories in input directory

import argparse
import os
import yaml


parser = argparse.ArgumentParser(description="Generate pod5.yml from subdirectories in input directory")
parser.add_argument("-i", "--input_dir", default="./Input", 
	help="Input directory [%(default)s]")
parser.add_argument("-o", "--output_file", default="pod5.yml", 
	help="Output YAML file [%(default)s]")
args = parser.parse_args()

input_dir   = args.input_dir
output_file = args.output_file

# Get all subdirectories in input_dir
pod5_dirs = [
	os.path.join(input_dir, d)
	for d in os.listdir(input_dir)
	if os.path.isdir(os.path.join(input_dir, d))
]

# Create YAML structure
config = {"pod5_dirs": pod5_dirs}

# Write to pod5.yml
with open(output_file, "w") as f:
	yaml.dump(config, f, default_flow_style=False)

print(f"Generated {output_file} with {len(pod5_dirs)} entries.")

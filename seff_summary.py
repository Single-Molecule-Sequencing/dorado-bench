# !/usr/bin/env python3

import argparse
import subprocess

def read_job_ids(psv_path) -> list[str]:
	job_ids = set()
	with open(psv_path, 'r') as fp:
		for line in fp:
			job_id = line.strip().split('|')[0]
			job_ids.add(job_id)
	return sorted(job_ids)

def parse_seff_output(output) -> dict:
	result = {}
	for line in output.strip().split('\n'):
		key, value = line.split(':', 1)
		result[key.strip()] = value.strip()
	return result

def write_tsv(data_list: list[dict], output_path: str):
	if not data_list:
		return
	keys = list(data_list[0].keys())
	with open(output_path, 'w') as fp:
		fp.write('\t'.join(keys) + '\n')
		for entry in data_list:
			row = [entry.get(k, '') for k in keys]
			fp.write('\t'.join(row) + '\n')

parser = argparse.ArgumentParser(description='Generate seff summaries from sacct job list.')
parser.add_argument('-i', '--input', 
	help='Path to sacct-generated PSV file')
parser.add_argument('-o', '--output', 
	help='Path to output TSV file')
args = parser.parse_args()

job_ids = read_job_ids(args.input)
seff_data = []

for job_id in job_ids:
	try:
		output = subprocess.check_output(['seff', job_id], text=True)
		parsed = parse_seff_output(output)
		seff_data.append(parsed)
	except subprocess.CalledProcessError:
		continue

write_tsv(seff_data, args.output)

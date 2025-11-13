#!/usr/bin/env python3

import argparse
import os
from pathlib import Path
import subprocess
import sys


TYPE_DIR_NAMES = {
	"variant": "Var",
	"correction": "Cor",
	"simplex": "Simplex",
	"polish": "Polish",
	"modification": "Mod",
	"stereo": "Stereo",
}


def parse_models(list_text: str) -> dict[str, dict[str, list[str]]]:
	models_by_type = {}
	current_type = None

	for raw in list_text.splitlines():
		line = raw.strip()
		if not line:
			continue

		if " > " in line and "models" in line:
			after = line.split(">", 1)[1].strip()
			type_word = after.split(" ", 1)[0].strip().lower()
			if type_word in TYPE_DIR_NAMES:
				current_type = type_word
				if current_type not in models_by_type:
					models_by_type[current_type] = {}
				continue
			else:
				print("[Model Downloader] Error: unrecognized model type:", type_word, file=sys.stderr)
				sys.exit(1)

		if current_type and " - " in line:
			parts = line.split(" - ", 1)
			if len(parts) < 2:
				continue
			model_name = parts[1].strip()

			if not model_name.startswith("dna"):
				continue

			version = model_name.split("@v", 1)[1][:5]

			if version not in models_by_type[current_type]:
				models_by_type[current_type][version] = []
			models_by_type[current_type][version].append(model_name)

	return models_by_type


def download_models(dorado_exe: Path, base_dir: Path, model_type: str, versions: list[str], models_by_type: dict[str, dict[str, list[str]]], dry_run: bool) -> None:
	type_dict = models_by_type[model_type]
	dir_name = TYPE_DIR_NAMES[model_type]
	type_dir = (base_dir / dir_name).resolve()

	for version in versions:
		if version not in type_dict:
			sys.exit(f"[Model Downloader] Error: no models found for type {model_type} with version {version}")

		models = type_dict[version]

		for model_name in models:
			target_dir = (type_dir / model_name).resolve()

			if target_dir.exists():
				print(f"[Model Downloader] Skipping downloaded model {model_name}")
				continue

			cmd = [
				dorado_exe,
				"download",
				"--model",
				model_name,
				"--models-directory",
				target_dir,
			]

			if dry_run:
				print(f"[DRY-RUN] Version {version} - model: {model_name}")
				print(f"[DRY-RUN] Would create directory: {target_dir}")
				print(f"[DRY-RUN] Would run: {' '.join(cmd)}")
				continue

			os.makedirs(target_dir, exist_ok=False)

			print(f"[Model Downloader] Running (version {version}): {' '.join(cmd)}")
			try:
				subprocess.run(cmd, check=True)
			except subprocess.CalledProcessError as exc:
				sys.exit(f"[Model Downloader] Error: Download failed for model {model_name} with exit code {exc.returncode}")

	return None


parser = argparse.ArgumentParser(description="Download DNA Dorado models by type and version")
parser.add_argument(
	"-d",
	"--dorado",
	default="dorado",
	help='Path to dorado executable [%(default)s]',
)
parser.add_argument(
	"-t",
	"--type",
	required=True,
	choices=TYPE_DIR_NAMES.keys(),
	help="Model type to download: variant, correction, simplex, polish, modification, stereo",
)
parser.add_argument(
	"-v",
	"--version",
	dest="versions",
	nargs="+",
	required=True,
	help="One or more model versions (e.g. 5.0.0 5.2.0).",
)
parser.add_argument(
	"-o",
	"--models-dir",
	default="Models",
	help='Base directory to store models [%(default)s]',
)
parser.add_argument(
	"--dry-run",
	action="store_true",
	help="Print what would be downloaded without running Dorado",
)
args = parser.parse_args()


dorado_exe_path = Path(args.dorado).resolve()
if not dorado_exe_path.exists():
	sys.exit(f"[Model Downloader] Error: dorado executable not found at path: {args.dorado}")

if args.type not in TYPE_DIR_NAMES.keys():
	sys.exit(f"[Model Downloader] Error: invalid model type: {args.type}")

for v in args.versions:
	if not v.count(".") == 2:
		sys.exit(f"[Model Downloader] Error: invalid version format: {v} (expected format: X.Y.Z)")

try:
	result = subprocess.run([dorado_exe_path, "download", "--list"], capture_output=True, text=True, check=True)
except subprocess.CalledProcessError as exc:
	sys.exit(f"[Model Downloader] Error: command failed: {' '.join(exc.cmd)}\n[Model Downloader] Exit code: ,{exc.returncode}")

list_output = result.stdout
print(list_output)
sys.exit(3)
models_by_type = parse_models(list_output)


base_dir = Path(args.models_dir).resolve()

download_models(
	dorado_exe_path,
	base_dir,
	args.type,
	args.versions,
	models_by_type,
	args.dry_run,
)

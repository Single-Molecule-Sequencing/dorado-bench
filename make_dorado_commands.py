#!/usr/bin/env python3

from itertools import product
from pathlib import Path
import yaml


#########
# funcs #
#########

def load_config(config: str = "config.yml") -> dict:
	with open(config, "r", encoding="utf-8") as fp:
		cfg = yaml.safe_load(fp) or {}
	return cfg


def validate_cfg(cfg: dict):
	if not isinstance(cfg.get("pod5_dirs"), list) or not cfg["pod5_dirs"]:
		raise ValueError("config.yml: 'pod5_dirs' must be a non-empty list of directories.")
	if not isinstance(cfg.get("model_versions"), list) or not cfg["model_versions"]:
		raise ValueError("config.yml: 'model_versions' must be a non-empty list.")
	if not isinstance(cfg.get("model_types"), list) or not cfg["model_types"]:
		raise ValueError("config.yml: 'model_types' must be a non-empty list.")

	trim = str(cfg.get("trim", "both")).lower()
	if trim not in {"both", "yes", "no"}:
		raise ValueError("config.yml: 'trim' must be one of 'both', 'yes', or 'no'.")


def build_commands(cfg: dict) -> list[str]:
	pod5_dirs      = cfg["pod5_dirs"]
	model_versions = cfg["model_versions"]
	model_types    = cfg["model_types"]
	model_mods     = cfg.get("model_mods", [])  # empty for now
	trim_mode      = str(cfg.get("trim", "both")).lower()
	gpu            = str(cfg.get("gpu", "auto"))
	models_dir     = cfg.get("models_directory", "")
	dorado_exe     = cfg.get("dorado_exe", "dorado")
	model_prefix   = cfg.get("model_prefix", "dna_r10.4.1_e8.2_400bps_")

	# trim states to test
	if trim_mode == "both":
		# True => trim1 (default trimming), False => trim0 (--no-trim)
		trims = [True, False]
	elif trim_mode == "yes":
		trims = [True]
	else:
		trims = [False]

	mods_list = model_mods if model_mods else [None]

	commands = []
	for pod_dir, version, mtype, mod, trimmed in product(pod5_dirs, model_versions, model_types, mods_list, trims):
		sample = Path(pod_dir).name or str(Path(pod_dir))
		base_model = f"{model_prefix}{mtype}@v{version}"
		model_and_mod = base_model if not mod else f"{base_model},{mod}"

		trim_tag = f"trim{1 if trimmed else 0}"
		bam_name = f"{sample}_{mtype}_v{version}_{trim_tag}"
		
		if mod:
			bam_name += f"_{mod}"
		bam_name += ".bam"

		parts = [
			dorado_exe,
			"basecaller",
			model_and_mod,
			"-x", gpu,
		]
		if models_dir:
			parts += ["--models-directory", models_dir]
		if not trimmed:
			parts.append("--no-trim")

		parts += [pod_dir, ">", bam_name]
		commands.append(" ".join(parts))

	return commands


def write_commands_file(commands: list[str], out_path: str = "dorado_basecaller_commands.txt"):
	with open(out_path, "w", encoding="utf-8") as fp:
		for c in commands:
			fp.write(c + "\n")


########
# main #
########

cfg = load_config("config.yml")
validate_cfg(cfg)
cmds = build_commands(cfg)
write_commands_file(cmds)
print(f"Wrote {len(cmds)} commands to dorado_basecaller_commands.txt")

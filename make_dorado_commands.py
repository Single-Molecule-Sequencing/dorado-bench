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


def build_commands_by_tier(cfg: dict) -> dict[str, list[str]]:
	pod5_dirs      = cfg["pod5_dirs"]
	model_versions = cfg["model_versions"]
	model_types    = cfg["model_types"]
	model_mods     = cfg.get("model_mods", [])  # empty for now
	trim_mode      = str(cfg.get("trim", "both")).lower()
	gpu            = str(cfg.get("gpu", "auto"))
	models_dir     = cfg.get("models_directory", "")
	dorado_exe     = cfg.get("dorado_exe", "dorado")
	output_dir     = cfg.get("output_directory", "./Output")
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

	buckets = {t: [] for t in model_types}

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
			Path(dorado_exe).resolve(),
			"basecaller",
			model_and_mod,
			"-x", gpu,
		]

		if models_dir:
			parts += ["--models-directory", Path(models_dir).resolve()]
		if not trimmed:
			parts.append("--no-trim")

		output_path = Path(output_dir).resolve() / bam_name
		parts += [Path(pod_dir).resolve(), ">", output_path]

		cmd = " ".join(parts)
		buckets[mtype].append(cmd)

	return buckets


def write_commands_file(commands: list[str], out_path: str = "dorado_basecaller_commands.txt"):
	with open(out_path, "w", encoding="utf-8") as fp:
		for c in commands:
			fp.write(c + "\n")


def write_files(buckets: dict) -> dict[str, tuple[str, int]]:
	name_map = {
		"fast": "dorado_basecaller_fast_cmd.txt",
		"hac":  "dorado_basecaller_hac_cmd.txt",
		"sup":  "dorado_basecaller_sup_cmd.txt",
	}
	written = {}
	for tier, cmds in buckets.items():
		outfile = name_map.get(tier, f"dorado_basecaller_{tier}_cmd.txt")
		with open(outfile, "w", encoding="utf-8") as f:
			for c in cmds:
				f.write(c + "\n")
		written[tier] = (outfile, len(cmds))
	return written


########
# main #
########

cfg = load_config("config.yml")
validate_cfg(cfg)
buckets = build_commands_by_tier(cfg)
written = write_files(buckets)

msg = "Created: " + ", ".join(f"{tier}-{path} ({n} cmds)" for tier, (path, n) in written.items())
print(msg)

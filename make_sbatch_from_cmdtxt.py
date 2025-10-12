#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys


#########
# funcs #
#########

def read_commands(path: Path) -> list[str]:
	if not path.exists():
		sys.exit(f"Input file not found: {path}")
	cmds = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()]
	return cmds


def derive_job_name(cmd: str, job_prefix: str, fallback_idx: int) -> str:
	"""
	X.bam -> X
	"""
	base = cmd.rsplit("/", 1)[-1].rsplit(".", 1)[0]
	if base:
		return f"{job_prefix}_{base}"
	return f"{job_prefix}_{fallback_idx:04d}"


def build_header(partition: str, job_name: str, account: str, gres: str, cpus: int, mem: str, walltime: str, email: str, logs_dir: str, module: str) -> str:
	lines = [
		"#!/bin/bash",
		f"#SBATCH --partition={partition}",
		f"#SBATCH --account={account}",
		f"#SBATCH --job-name={job_name}",
		f"#SBATCH --gres={gres}",
		f"#SBATCH --nodes=1",
		f"#SBATCH --ntasks=1",
		f"#SBATCH --cpus-per-task={cpus}",
		f"#SBATCH --mem={mem}",
		f"#SBATCH --time={walltime}",
		f"#SBATCH --mail-user={email}" if email else "",
		f"#SBATCH --mail-type=BEGIN,END,FAIL" if email else "",
		f"#SBATCH --output={logs_dir}/%x_%j.out",
		f"#SBATCH --error={logs_dir}/%x_%j.err",
		"",
		"set -euo pipefail",
		'echo "[$(date)] Node: $(hostname)"',
		'echo "[$(date)] CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"',
	]
	if module:
		lines += ["", f"module load {module}"]
	lines += ["", "# run command"]
	return "\n".join(lines)


############
# argparse #
############

p = argparse.ArgumentParser(description="Generate per-command Slurm .sbatch files from a text file of Dorado commands.")
p.add_argument("-i", "--input", required=True,
	help="Path to commands file")
p.add_argument("-o", "--outdir", default=".",
	help="Directory to write .sbatch files into [%(default)s]")
p.add_argument("--partition", default="gpu_mig40",
	help="Slurm partition [%(default)s]")
p.add_argument("--account", required=True,
	help="Slurm account")
p.add_argument("--gres", default="gpu:nvidia_a100_80gb_pcie_3g.40gb:1",
	help="Slurm GRES string [%(default)s]")
p.add_argument("--cpus", type=int, default=8,
	help="CPUs per task [%(default)i]")
p.add_argument("--mem", default="32G",
	help="Memory per task [%(default)s]")
p.add_argument("--time", default="06:00:00",
	help="Walltime (HH:MM:SS) [%(default)s]")
p.add_argument("--email", type=str,
	help="Email for Slurm notifications")
p.add_argument("--job-prefix", default="dorado",
	help="Prefix to prepend to job names [%(default)s]")
p.add_argument("--module", default="",
	help="Optional module to load at job start [%(default)s]")
args = p.parse_args()


########
# main #
########

inpath = Path(args.input)
outdir = Path(args.outdir)

outdir.mkdir(parents=True, exist_ok=True)

logs_dir = Path(outdir / "Logs").resolve()
logs_dir.mkdir(parents=True, exist_ok=True)

cmds = read_commands(inpath)
if not cmds:
	sys.exit("No commands found in input.")

written = 0
for idx, cmd in enumerate(cmds, start=1):
	job_name = derive_job_name(cmd, args.job_prefix, idx)
	header = build_header(
		partition = args.partition,
		account   = args.account,
		job_name  = job_name,
		gres      = args.gres,
		cpus      = args.cpus,
		mem       = args.mem,
		walltime  = args.time,
		email     = args.email,
		logs_dir  = logs_dir,
		module    = args.module.strip()
	)
	script = f"{header}\n{cmd}\n"

	outpath = outdir / f"{job_name}.sbatch"
	if outpath.exists():
		outpath = outdir / f"{job_name}_{idx:03d}.sbatch"
	outpath.write_text(script, encoding="utf-8")
	written += 1

print(f"Wrote {written} .sbatch files to {outdir}/")
print(f"Logs will go to {logs_dir}/ via #SBATCH --output/--error")

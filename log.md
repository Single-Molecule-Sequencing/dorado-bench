# Command Logs

A file that logs commands used for later reference.

## Setup

### Download Dorado Software

```bash
curl "https://cdn.oxfordnanoportal.com/software/analysis/dorado-1.1.1-linux-x64.tar.gz" -o dorado-1.1.1-linux-x64.tar.gz
```

### Inflating Tar Ball

```bash
tar -xzf dorado-1.1.1-linux-x64.tar.gz
```

### Removing Tar Ball

```bash
rm dorado-1.1.1-linux-x64.tar.gz
```

### Download Dorado Models

```bash
bash download_dorado_models.sh
```

Only DNA models are downloaded

As of Oct. 08, 2025, the most recent DNA dorado models listed on [Models List - Dorado Documentation](https://software-docs.nanoporetech.com/dorado/latest/models/list/) are following the "dna_r10.4.1_e8.2_400bps_{TYPES}@{VERSIONS}" naming conventions

The following 12 models are downloaded

```
dna_r10.4.1_e8.2_400bps_fast@v4.2.0
dna_r10.4.1_e8.2_400bps_hac@v4.2.0
dna_r10.4.1_e8.2_400bps_sup@v4.2.0
dna_r10.4.1_e8.2_400bps_fast@v4.3.0
dna_r10.4.1_e8.2_400bps_hac@v4.3.0
dna_r10.4.1_e8.2_400bps_sup@v4.3.0
dna_r10.4.1_e8.2_400bps_fast@v5.0.0
dna_r10.4.1_e8.2_400bps_hac@v5.0.0
dna_r10.4.1_e8.2_400bps_sup@v5.0.0
dna_r10.4.1_e8.2_400bps_fast@v5.2.0
dna_r10.4.1_e8.2_400bps_hac@v5.2.0
dna_r10.4.1_e8.2_400bps_sup@v5.2.0
```

We will only test the most recent 3, v5.2.0, v5.0.0, and v4.3.0.

### Experimental Design

- 4 DNA-seq experiment data to basecall
- 3 tiers of models
- 3 versions of models
- 2 trimming options (trim or no trim)

72 total basecalls

### Make dorado Commands by Tiers

`make_dorado_commands.py`

- relies on **env.yml** conda environment (pyyaml)
- pieces managed by **config.yml**
- `dorado basecaller` commands are written into tiered txt files

### Build Sbatch Job Files

`make_sbatch_from_cmdtxt.py`

- takes in txt files containing the commands
- one tiered txt file at a time
- options handled by **argparse**
- provide account, outdir, time allocation, email (optional)

### Submit Sbatch Files

`sbatch_all.sh`

- change sbdir to the directory containing the tiered directory of the sbatch files
- change sleep length when necessary

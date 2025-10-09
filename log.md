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

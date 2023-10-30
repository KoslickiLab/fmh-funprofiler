# Metagenomic functional profiler

A pipeline based on [sourmash](https://sourmash.readthedocs.io/en/latest/) and [KEGG database](https://www.genome.jp/kegg/) to perform functional profiles for metagenomic sequences.

#### Input:

1. pre-built reference data from KEGG
2. metagenomic sequences (fasta or fastq file)

#### Output:

1. List of KEGG Orthology (KOs) with abundance
2. Standard `sourmash gather` output with more KO-based statistics (including median weight, containment, ANI etc.)

</br>

## Installation

To install, do the following after cloning this repository:

```
conda create -n funcprofiler
conda activate funcprofiler
conda install -c bioconda -c conda-forge sourmash pandas
```

</br>

### Quick start

---

```
cd demo 

# Obtain reference data (pre-built sketches for the KEGG database)
wget https://zenodo.org/records/10045253/files/KOs_sketched_scaled_1000.sig.zip

# profile the example fastq file
python ../funcprofiler.py metagenome_example.fastq KOs_sketched_scaled_1000.sig.zip  7 1000 ko_profiles
```

#### Output:

1. `ko_profiles`: a csv file with abundance for all identified KOs in the sample
2. `__gather_out`: the full `sourmash gather` output containing more KO-based statistics, check [here](https://sourmash.readthedocs.io/en/latest/classifying-signatures.html) for more details



</br>

### Usage

---

The followings are detailed procedures for this pipeline.

## Prepare reference data: k-mer sketches for KEGG KO data

#### Pre-built reference sketches: obtain the pre-built KO sketches here

```
https://zenodo.org/records/10045253
```

1. The sbt's are sequence-bloom-trees. They make the pipeline run faster. We have
   made three sbt's available to use: scaled=1000 and k=7, 11, and 15.
2. We also have made two sig.zip files available: one with scaled=500, and another
   with scaled=1000. Each of these files have three k values: 7, 11, and 15.

</br>

#### Start from scratch

You may use your own reference data instead of KEGG, here is how to build your own reference data

```
# if you have a list of files, each file represents 1 gene (or gene cluster)
find <path of foler containg FASTA/FASTQ files> > dataset.csv
sourmash sketch fromfile -p protein,k=7,k=11,k=15,abund,scaled=1000 -o ref_sketch.sig.zip dataset.csv

# if you have a single file will all genes stored together and each record represents 1 gene (cluster)
sourmash sketch -p protein,k=7,k=11,k=15,abund,scaled=1000 --singleton -o ref_sketch.sig.zip ${input_file}
```



</br>

## Pipe usage

```
python funcprofiler.py -h
```

A metagenome example fastq file is available with this repository. Obtain the KO sketches from the link given above. Then, run the following command:

```
cd demo
python ../funcprofiler.py metagenome_example.fastq KOs_sbt_scaled_1000_k_15.sbt.zip 15 1000 ko_profiles
```

The output is a csv file named `ko_profiles`, which lists the KOs that are present in the sample, and the second column gives their relative abundances. And there is also an original `sourmash gather` output files recording more k-mer statistics.

#### Parameters:

| Name            | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| mg_filename     | Path to the input metagenomic sequences (fasta or fastq)     |
| ko_sketch       | Path to the reference sketch                                 |
| ksize           | Protein kmer size (7, 11, or 15) to use, corresponding to (21,33,45) for DNA |
| scaled          | The scale factor in the FracMinHash technique, 1000 is suitable for KEGG KO. |
| output          | Output filename                                              |
| -t THRESHOLD_BP | Least bp of overlap for a reference gene (cluster) to be present, default 1000 |
| -g GATHER_FILE  | Output filename for the sourmash gather output               |



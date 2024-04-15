# Metagenomic functional profiler

A pipeline based on [sourmash](https://sourmash.readthedocs.io/en/latest/) and [KEGG database](https://www.genome.jp/kegg/) to obtain functional profiles for metagenomic sequences.

#### Input:

1. pre-built reference data from KEGG
2. metagenomic sequences (fasta or fastq file)

#### Output:

1. List of KEGG Orthology (KOs) with abundance
2. Standard `sourmash prefetch` output with more KO-based statistics (including containment, ANI etc.)

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
git clone https://github.com/KoslickiLab/funprofiler.git
cd funprofiler/demo 

# Obtain reference data (pre-built sketches for the KEGG database)
wget https://zenodo.org/records/10045253/files/KOs_sketched_scaled_1000.sig.zip

# profile the example fastq file
python ../funcprofiler.py metagenome_example.fastq KOs_sketched_scaled_1000.sig.zip 11 1000 ko_profiles -p prefetch_out
```

#### Output:

1. `ko_profiles`: a csv file with abundance for all identified KOs in the sample
2. `prefetch_out`: the full `sourmash prefetch` output containing more KO-based statistics, check [here](https://sourmash.readthedocs.io/en/latest/command-line.html#sourmash-prefetch-select-subsets-of-very-large-databases-for-more-processing) for more details



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

As the reference database, one can use either the sig.zip files, or the sbt's. The results will be the same.

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
python ../funcprofiler.py metagenome_example.fastq KOs_sbt_scaled_1000_k_11.sbt.zip 11 1000 ko_profiles
```

The output is a csv file named `ko_profiles`, which lists the KOs that are present in the sample, and the second column gives their relative abundances.

#### Parameters:

| Name            | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| mg_filename     | Path to the input metagenomic sequences (fasta or fastq)     |
| ko_sketch       | Path to the reference sketch                                 |
| ksize           | Protein kmer size (7, 11, or 15) to use, corresponding to (21,33,45) for DNA |
| scaled          | The scale factor in the FracMinHash technique, 1000 is suitable for KEGG KO. |
| output          | Output filename                                              |
| -t THRESHOLD_BP | Least bp of overlap for a reference gene (cluster) to be present, default 1000 |
| -p PREFETCH_FILE  | Output filename for the sourmash prefetch output               |


# Running many instances together

One can run many instances of `funcprofiler.py` simultaneously in parallel for many metagenomes. The script is `funcprofiler_many.py`. This script takes a file_list as input, which should contain a list of all input metagenome files, and their target output files.

### Usage

```
python funcprofiler_many.py <KO_REF_DB> <KSIZE> <SCALED> <FILE_LIST> <THRESHOLD_BP>
```

#### Parameters
1. KO_REF_DB: the KO reference db (gig.zip or sbt, detailed above)
1. KSIZE: proper protein k-mer size
1. SCALED: proper scaled value (our pre-built ref dbs support 1000 or 500)
1. FILE_LIST: a text csv file, containing no headers, two columns, first column being the metagenome files, and the second column being the corresponding target ko profile output files
1. THRESHOLD_BP: the threshold bp to use in sourmash. 50/100/500 etc. are typical values. Larger value is faster with reduced sensitivity.

#### Example usage
```
cd demo
python ../funcprofiler_many.py KOs_sbt_scaled_1000_k_11.sbt.zip 11 1000 list_of_files 100
```
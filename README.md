# funprofiler
A functional profiler for metagenome samples.

## Inputs
1. Metagenome sample (sequencing reads)
1. FracMinHash sketch of KOs. The sketches need to be computed using `sourmash`

## Output
1. List of KOs that are present in the sample

## Installation
To install, do the following after cloning this repository:
```
conda create -n funcprofiler
conda activate funprofiler
conda install sourmash
```
You can use other python package managers to do the same thing.

## Obtaining KO sketches
Obtain the pre-built KO sketches from here:
```
https://zenodo.org/records/10045253
```
The sbt's are sequence-bloom-trees. They make the pipeline run faster. We have
made three sbt's available to use: scaled=1000 and k=7, 11, and 15.

We also have made two sig.zip files available: one with scaled=500, and another
with scaled=1000. Each of these files have three k values: 7, 11, and 15.

## Usage
```
python funcprofiler.py -h
```

## Example
A metagenome example fastq file is available with this repository. Obtain the KO sketches from the link given above. Then, run the following command:
```
python funcprofiler.py metagenome_example.fastq KOs_sbt_scaled_1000_k_15.sbt.zip 15 1000 1000 ko_profiles
```
The output is a csv file named `ko_profiles`, which lists the KOs that are present in the sample, and the second column gives their relative abundances.

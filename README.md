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
cobda create -n funcprofiler
conda activate funprofiler
conda install sourmash
```
You can use other python package managers to do the same thing.

## Obtaining KO sketches
Obtain the pre-built KO sketches from here:
```
https://zenodo.org/records/10045253
```

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

# GENIE-FMI-converter
This is the converter for foundation medicine provided by DUKE for GENIE

## Pugh Lab Fork: Dockerized GENIE-FMI-converter


### Setting up the Docker container
NOTE: if you already have the fastas downloaded, comment (#) the lines in the Dockerfile and use the docker run command with volumes mounted replace with your source directory (-v) 

```sh
$ git clone https://github.com/pughlab/GENIE-FMI-converter.git 
$ cd GENIE-FMI-converter
$ docker build -t genie_fmi --rm . 
$ docker run -it -v path/to/source/directory:/GENIE-FMI-converter/fasta genie_fmi 
$ docker run -it genie_fmi 
```

### Running the converter
Inside the docker container, run the GENIE python tool 
```sh
$ cd GENIE-FMI-converter
$ python3 xml_annotator -g fasta/ucsc.hg19.fasta -i DUKE input_xml_file_list.txt ResultsReport.2.1.xsd 
```







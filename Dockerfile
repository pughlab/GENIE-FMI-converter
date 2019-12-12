FROM ubuntu:19.04

RUN apt-get update && \
    apt-get install -y \
            gcc \
            wget \
            git \
            libxml2-dev \ 
            libxslt-dev \ 
            python-dev \ 
            python3 \ 
            python3-pip \
            vim 

# python packages required by GENIE-FMI-converter            
RUN pip3 install pyfaidx 
RUN pip3 install lxml 
RUN pip3 install requests 

# clone repo 
RUN git clone https://github.com/Sage-Bionetworks/GENIE-FMI-converter.git 

# comment out these build fastas if mounting volume
RUN cd GENIE-FMI-converter && \
    bash build_fasta.sh

# repo with example xmls to test 
RUN git clone https://github.com/AlexHelloWorld/parseTCGAClinicalXML.git 
RUN cd parseTCGAClinicalXML/sample && \
    cp nationwidechildrens*.xml /GENIE-FMI-converter/ && \
    cp input_xml_file_list.txt /GENIE-FMI-converter/ 



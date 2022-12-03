FROM centos:7

MAINTAINER OPI-API-Raleigh_DL@ds.org.com

#Build time ARG for password and storage account key and ENV for password
ARG PASSWORD
ENV FLASK_PASSWORD=$PASSWORD
ARG STORAGE_KEY

#Install rpm, python 2.7, gcc, gcc-c++, python-devel
RUN yum update -y \
&&  yum install -y \
    rpm \
    python27 \
    gcc gcc-c++ \
    python-devel

#Install EPEL to install pip
RUN yum -y --enablerepo=extras install epel-release

#Install pip and upgrade pip
RUN yum install -y python-pip \
&&  pip install --upgrade pip

#Install pip modules
RUN pip install flask \
&&  pip install pandas \
&&  pip install nltk \
&&  pip install num2words \
&&  pip install azure-storage-blob \
&&  pip install xlrd \
&&  pip install openpyxl \
&&  pip install pycrypto \
&&  pip install python-magic \
&&  pip install Flask-Cors \
&&  pip install unittest2


#Make directory for mapping/validation files
RUN mkdir map_validation_files

#Add Flask app and Storage Key Encryption
ADD FlaskProvider.py ./map_validation_files
ADD FlaskProviderTest.py ./map_validation_files
ADD EncryptStorageKey.py ./map_validation_files

#Run Storage Key Encryption
RUN python ./map_validation_files/EncryptStorageKey.py $STORAGE_KEY $PASSWORD

#Run Tests
#CMD python ./map_validation_files/FlaskProviderTest.py

#Start Flask app
CMD python ./map_validation_files/FlaskProvider.py $FLASK_PASSWORD

#Expose port 5000
EXPOSE 5000

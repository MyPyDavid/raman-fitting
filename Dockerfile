# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY . .

# copy setup.cfg to work dir
# COPY setup.cfg .
# COPY setup.py .
# install package test, maybe not possible because only src
# RUN pip install -e ./


# install dependencies
RUN pip install -r requirements.txt

RUN pip install --upgrade build
RUN build ./
RUN pip install -e  ./

# copy the content of the local src directory to the working directory
#COPY src/ .

# command to run on container start
CMD [ "python", "./raman_fitting/docker/run_make_examples.py" ]

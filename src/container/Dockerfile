# recommend not to use the alpine one, it lacks lots of dependencies
# the slim one ocuppies about 2x space compared to alpine one
# FROM python:3.7-alpine
FROM python:3.7-slim

COPY pip.conf /etc/pip.conf

# fulfill the structure requirement of proxy
RUN mkdir /proxy
# RUN mkdir /stress-ng

# copy libs
COPY proxy.py /proxy/proxy.py
COPY main.py /proxy/main.py
COPY Store.py /proxy/Store.py
COPY container_config.py /proxy/container_config.py
# COPY stress-ng /stress-ng/
COPY compute_pi.cpp /proxy/compute_pi.cpp

WORKDIR /proxy

# proxy server runs under port 5000
EXPOSE 5000

# for alpine base only
# RUN apk update && \
#     apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev make && \
#     pip install --no-cache-dir gevent flask && \
#     apk del .build-deps

# WORKDIR /stress-ng
# RUN apt-get clean && apt-get update && apt-get install g++ git make -y && pip3 install --no-cache-dir gevent flask couchdb redis pybind11 && make clean && make install

# WORKDIR /proxy

RUN apt-get clean
RUN apt-get update
# ***
RUN apt-get install g++ -y
# ***
RUN pip3 install --no-cache-dir gevent flask couchdb redis pybind11

# ***
RUN g++ -O3 -Wall -shared -std=c++11 -fPIC \
$(echo $(python3 -m pybind11 --includes)) compute_pi.cpp -o compute_pi\
$(echo $(python3-config --extension-suffix))

CMD [ "python3", "/proxy/proxy.py" ]

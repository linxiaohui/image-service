FROM ubuntu:18.04
LABEL maintainer="llinxiaohui@126.com"
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list \
 && apt update \
 && DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends libaio1 python3 python3-pip tzdata libglib2.0-0\
 && apt clean  && rm -rf /var/lib/apt/lists/*
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple pip -U
RUN pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple
RUN pip3 install --no-cache-dir setuptools wheel
RUN pip3 install --no-cache-dir numpy==1.15.2 h5py==2.10.0 zerorpc==0.6.3 tornado==6.1 requests==2.24.0 
RUN pip3 install --no-cache-dir scipy==1.1.0 opencv-python-headless==4.2.0.32
RUN pip3 install --no-cache-dir tensorflow==1.4
RUN pip3 install --no-cache-dir pillow
COPY align /align
COPY 20180408-102900 /models/20180408-102900
ENV IMAGESERVICE_ROOT /
COPY templates /templates
COPY facenet.py /facenet.py
COPY detect_server.py /detect_server.py
COPY calc_face_features.py /calc_face_features.py
CMD (nohup python3 -u calc_face_features.py &) && python3 -u detect_server.py



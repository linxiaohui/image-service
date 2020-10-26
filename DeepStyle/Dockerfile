FROM ubuntu:18.04
LABEL maintainer="llinxiaohui@126.com"
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list \
 && apt update \
 && DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends libaio1 python3 python3-pip tzdata libgl1-mesa-glx libglib2.0-0\
 && apt clean  && rm -rf /var/lib/apt/lists/*
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install --no-cache-dir setuptools h5py
RUN pip3 install --no-cache-dir opencv-python
RUN pip3 install --no-cache-dir zerorpc
RUN pip3 install --no-cache-dir tornado
RUN pip3 install --no-cache-dir torch-u2net==1.0.0
RUN pip3 install --no-cache-dir pillow
RUN pip3 install --no-cache-dir --no-deps torchvision==0.2.1
COPY cores /cores
COPY models /models
COPY pretrained_models /pretrained_models
COPY util /util
COPY *.py /
ENV IMAGESERVICE_ROOT /

FROM ubuntu:18.04
LABEL maintainer="llinxiaohui@126.com"
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list \
 && apt update \
 && DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends libaio1 python3 python3-pip tzdata \
 && apt clean &&  rm -rf /var/lib/apt/lists/*
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install --no-cache-dir setuptools h5py
RUN pip3 install --no-cache-dir zerorpc
RUN pip3 install --no-cache-dir tensorflow==1.14 
RUN pip3 install --no-cache-dir opencv-python
RUN pip3 install --no-cache-dir scikit-image==0.14.5
RUN pip3 install --no-cache-dir pillow
RUN apt update && apt install -y --no-install-recommends  libgl1-mesa-glx libglib2.0-0\
 && apt clean  && rm -rf /var/lib/apt/lists/*
COPY *.py /
COPY ./model /model
COPY ./test_images/ /test_images

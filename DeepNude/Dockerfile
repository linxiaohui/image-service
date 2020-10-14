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
RUN pip3 install --no-cache-dir setuptools
RUN pip3 install --no-cache-dir numpy==1.15.2
RUN pip3 install --no-cache-dir zerorpc
RUN pip3 install --no-cache-dir scikit-image==0.14.0
RUN pip3 install --no-cache-dir torch-u2net==1.0.0
RUN pip3 install --no-cache-dir --no-deps torchvision==0.2.1
RUN pip3 install --no-cache-dir pillow 
COPY ./opencv_transform /opencv_transform
COPY ./checkpoints /checkpoints
COPY *.py /
COPY *.png /
#ADD FaceSketchData.zip /FaceSketchData
ENV IMAGESERVICE_ROOT /
CMD python3 /main.py

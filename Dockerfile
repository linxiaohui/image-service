FROM ubuntu:18.04
LABEL maintainer="llinxiaohui@126.com"
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list \
 && apt update \
 && DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends libaio1 python3 python3-pip tzdata libgl1-mesa-glx libglib2.0-0\
 && apt clean  && rm -rf /var/lib/apt/lists/*
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple pip -U
RUN pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple
RUN pip3 install --no-cache-dir setuptools h5py wheel
RUN pip3 install --no-cache-dir numpy==1.15.2
RUN pip3 install --no-cache-dir opencv-python
RUN pip3 install --no-cache-dir zerorpc
RUN pip3 install --no-cache-dir tornado
RUN pip3 install torch==1.6.0+cpu torchvision==0.7.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip3 install --no-cache-dir dlib-binary
RUN pip3 install --no-cache-dir keras==2.2.4
RUN pip3 install --no-cache-dir tensorflow==1.14
RUN pip3 install --no-cache-dir requests scikit-image==0.14.0
COPY U-2-Net/model /model
COPY U-2-Net/u2net_rpc.py /u2net_rpc.py
COPY U-2-Net/data_loader.py /data_loader.py
COPY StyleTransfer/models /models
COPY StyleTransfer/style_transfer.py /style_transfer.py
COPY StyleTransfer/templates /templates
COPY StyleTransfer/style_transfer_server.py /style_transfer_server.py
ENV IMAGESERVICE_ROOT /
CMD python3 style_transfer_server.py

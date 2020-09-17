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
RUN pip3 install --no-cache-dir dlib-binary
RUN pip3 install --no-cache-dir zerorpc
RUN pip3 install --no-cache-dir tensorflow==1.4 
RUN pip3 install --no-cache-dir keras==2.0.5
COPY models /models
COPY resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5 /root/.keras/models/resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5
COPY beauty_predict.py /beauty_predict.py
COPY beauty_rpc.py /beauty_rpc.py
ENV IMAGESERVICE_ROOT /
CMD python3 /beauty_rpc.py


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
COPY ROI-Mark/models /models
COPY ROI-Mark/pretrained_models /pretrained_models
COPY ROI-Mark/roi_marker.py /roi_marker.py
COPY NSFW-Mask/bbox_blur.py /bbox_blur.py
COPY NSFW-Mask/mosaic_nsfw.py /mosaic_nsfw.py
COPY NSFW-Mask/model /model
COPY Mosaic/mosaic_utils.py /mosaic_utils.py
COPY BeautyPredict/beauty_predict.py /beauty_predict.py
COPY BeautyPredict/models /models
COPY BeautyPredict/resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5 /root/.keras/models/resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5
COPY Cartoonization/model /model
COPY Cartoonization/network.py /network.py
COPY Cartoonization/guided_filter.py /guided_filter.py
COPY Cartoonization/cartoonize.py /cartoonize.py
COPY CertPhoto/chg_bg.py /chg_bg.py
COPY FaceSketch/sketch.pth /sketch.pth
COPY FaceSketch/face_sketch.py /face_sketch.py
COPY FaceRank/dlib_landmarks.py /dlib_landmarks.py
COPY FaceRank/face_rank.py /face_rank.py
COPY FaceRank/shape_predictor_68_face_landmarks.dat /shape_predictor_68_face_landmarks.dat
COPY FaceDetect/face_decet_rpc.py /face_decet_rpc.py
COPY FaceCartoonization/inference.py /inference.py
COPY FaceCartoonization/weight.pth /weight.pth
COPY FaceCartoonization/templates /templates
COPY FaceCartoonization/cartoon_server.py /cartoon_server.py

ENV IMAGESERVICE_ROOT /
CMD python3 cartoon_server.py


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
RUN pip3 install --no-cache-dir setuptools wheel
RUN pip3 install --no-cache-dir numpy==1.15.2 h5py==2.10.0 zerorpc==0.6.3 tornado==6.1 requests==2.24.0 
RUN pip3 install --no-cache-dir scipy==1.5.4 opencv-python==4.4.0.46
RUN pip3 install torch==1.6.0+cpu torchvision==0.7.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip3 install --no-cache-dir dlib-binary
RUN pip3 install --no-cache-dir keras==2.2.4 tensorflow==1.14
RUN pip3 install --no-cache-dir scikit-image==0.14.0
COPY U-2-Net/model /model
COPY U-2-Net/u2net_rpc.py /u2net_rpc.py
COPY U-2-Net/data_loader.py /data_loader.py
COPY StyleTransfer/style_transfer.py /style_transfer.py
COPY ROI-Mark/dm_models /dm_models
COPY ROI-Mark/roi_marker.py /roi_marker.py
COPY NSFW-Mask/bbox_blur.py /bbox_blur.py
COPY NSFW-Mask/mosaic_nsfw.py /mosaic_nsfw.py
COPY Mosaic/mosaic_utils.py /mosaic_utils.py
COPY BeautyPredict/beauty_predict.py /beauty_predict.py
COPY BeautyPredict/resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5 /root/.keras/models/resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5
COPY Cartoonization/network.py /network.py
COPY Cartoonization/guided_filter.py /guided_filter.py
COPY Cartoonization/cartoonize.py /cartoonize.py
COPY CertPhoto/chg_bg.py /chg_bg.py
COPY FaceSketch/face_sketch.py /face_sketch.py
COPY FaceRank/dlib_landmarks.py /dlib_landmarks.py
COPY FaceRank/face_rank.py /face_rank.py
COPY FaceDetect/face_decet_rpc.py /face_decet_rpc.py
COPY FaceCartoonization/inference.py /inference.py
COPY DeepMosaic/deep_mosaic.py /deep_mosaic.py
COPY DeepMosaic/util /util
COPY DeepStyle/util/__init__.py /util/__init__.py
COPY DeepStyle/dm_models /dm_models
COPY DeepStyle/deep_style.py /deep_style.py
COPY NSFW/nsfw_predict.py /nsfw_predict.py
COPY imgsvr_templates /imgsvr_templates
COPY imgsvr_static /imgsvr_static
COPY image_service.py image_service.py
ENV IMAGESERVICE_ROOT /
CMD python3 -u image_service.py
 

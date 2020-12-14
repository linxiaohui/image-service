export IMAGESERVICE_ROOT=$(pwd)/run
rm -rf $IMAGESERVICE_ROOT
mkdir -p $IMAGESERVICE_ROOT
ln -s $(pwd)/models $IMAGESERVICE_ROOT/models
cp -r U-2-Net/model $IMAGESERVICE_ROOT/model
cp -r U-2-Net/u2net_op.py $IMAGESERVICE_ROOT/u2net_op.py
cp -r U-2-Net/data_loader.py $IMAGESERVICE_ROOT/data_loader.py
cp -r StyleTransfer/style_transfer.py $IMAGESERVICE_ROOT/style_transfer.py
cp -r ROI-Mark/dm_models $IMAGESERVICE_ROOT/dm_models
cp -r ROI-Mark/face_marker_op.py $IMAGESERVICE_ROOT/face_marker_op.py
cp -r Mosaic/mosaic_utils.py $IMAGESERVICE_ROOT/mosaic_utils.py
cp -r BeautyPredict/beauty_predict_op.py $IMAGESERVICE_ROOT/beauty_predict_op.py
cp -r Cartoonization/network.py $IMAGESERVICE_ROOT/network.py
cp -r Cartoonization/guided_filter.py $IMAGESERVICE_ROOT/guided_filter.py
cp -r Cartoonization/cartoonize.py $IMAGESERVICE_ROOT/cartoonize.py
cp -r CertPhoto/chg_bg.py $IMAGESERVICE_ROOT/chg_bg.py
cp -r FaceSketch/sketch_op.py $IMAGESERVICE_ROOT/sketch_op.py
cp -r FaceRank/dlib_landmarks.py $IMAGESERVICE_ROOT/dlib_landmarks.py
cp -r FaceRank/facerank_op.py $IMAGESERVICE_ROOT/facerank_op.py
cp -r FaceDetect/face_detect_rpc.py $IMAGESERVICE_ROOT/face_detect_rpc.py
cp -r DeepMosaic/deep_mosaic.py $IMAGESERVICE_ROOT/deep_mosaic.py
cp -r DeepMosaic/util $IMAGESERVICE_ROOT/util
cp -r DeepStyle/util/__init__.py $IMAGESERVICE_ROOT/util/__init__.py
cp -r DeepStyle/dm_models/* $IMAGESERVICE_ROOT/dm_models
cp -r DeepStyle/deep_style.py $IMAGESERVICE_ROOT/deep_style.py
cp -r NSFW/nsfw_predict.py $IMAGESERVICE_ROOT/nsfw_predict.py
cp -r FaceNet/align $IMAGESERVICE_ROOT/align
cp -r FaceNet/facenet.py $IMAGESERVICE_ROOT/facenet.py
cp -r FaceNet/facenet_op.py $IMAGESERVICE_ROOT/facenet_op.py
cp -r image_utils.py $IMAGESERVICE_ROOT/image_utils.py
cp -r imgsvr_lite_templates $IMAGESERVICE_ROOT/imgsvr_lite_templates
cp -r imgsvr_static $IMAGESERVICE_ROOT/imgsvr_static
cp -r image_lite_service.py $IMAGESERVICE_ROOT/image_lite_service.py
cd $IMAGESERVICE_ROOT
python3 -u $IMAGESERVICE_ROOT/image_lite_service.py

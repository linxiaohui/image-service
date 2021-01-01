export IMAGESERVICE_ROOT=$(pwd)/run
rm -rf $IMAGESERVICE_ROOT
mkdir -p $IMAGESERVICE_ROOT
ln -s $(pwd)/models $IMAGESERVICE_ROOT/models
cp -r U-2-Net/u2net_cv2.py $IMAGESERVICE_ROOT/u2net_cv2.py
cp -r StyleTransfer/style_transfer.py $IMAGESERVICE_ROOT/style_transfer.py
cp -r ROI-Mark/face_marker_cv2.py $IMAGESERVICE_ROOT/face_marker_cv2.py
cp -r Mosaic/mosaic_utils.py $IMAGESERVICE_ROOT/mosaic_utils.py
cp -r BeautyPredict/beauty_predict_cv2.py $IMAGESERVICE_ROOT/beauty_predict_cv2.py
cp -r Cartoonization/cartoon_onnx.py $IMAGESERVICE_ROOT/cartoon_onnx.py
cp -r CertPhoto/chg_bg.py $IMAGESERVICE_ROOT/chg_bg.py
cp -r FaceSketch/face_sketch_cv2.py $IMAGESERVICE_ROOT/face_sketch_cv2.py
cp -r FaceRank/dlib_landmarks.py $IMAGESERVICE_ROOT/dlib_landmarks.py
cp -r FaceRank/facerank_op.py $IMAGESERVICE_ROOT/facerank_op.py
cp -r FaceDetect/face_detect_rpc.py $IMAGESERVICE_ROOT/face_detect_rpc.py
cp -r NSFW/nsfw_cv2.py $IMAGESERVICE_ROOT/nsfw_cv2.py
cp -r FaceNet/mtcnn_cv2.py $IMAGESERVICE_ROOT/mtcnn_cv2.py
cp -r image_utils.py $IMAGESERVICE_ROOT/image_utils.py
cp -r imgsvr_lite_templates $IMAGESERVICE_ROOT/imgsvr_lite_templates
cp -r imgsvr_static $IMAGESERVICE_ROOT/imgsvr_static
cp -r image_lite_service.py $IMAGESERVICE_ROOT/image_lite_service.py
cd $IMAGESERVICE_ROOT
python3 -u $IMAGESERVICE_ROOT/image_lite_service.py

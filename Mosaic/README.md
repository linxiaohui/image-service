Mosaic
======
对图片的选定区域进行马赛克处理


# 构建与运行
## 构建
   * `docker build -t image-mosaic-webapp:1.0 .`

## 从DockerHub下载镜像并运行
   `docker run -d -p 65535:80 linxiaohui/image-mosaic-webapp:1.0`
   * 其中 `80`为容器中Web服务界面的监听端口；`65535`端口为映射到的本机端口.

# 使用方式
   * 浏览器打开，地址为宿主机地址+Web界面服务映射到的本机端口；
   * 上传图片或输入图片的URL， 点击提交后，图片将显示在页面当中；
   * 鼠标选择需要“打码”的区域，页面将显示“打码”后的图片


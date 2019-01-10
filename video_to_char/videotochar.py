import os
import cv2
from PIL import Image, ImageFont, ImageDraw


class VideoToChar:
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.ob_path, self.file_name = os.path.split(self.video_path)
        self.ob_path += '\\'
        self.cap = cv2.VideoCapture(self.video_path)
        self.frame_count = int(self.cap.get(7))
        self.video_width, self.video_height = int(self.cap.get(3)), int(self.cap.get(4))

    def video_to_frame(self):
        print('帧序列转换中....')
        for i in range(self.frame_count):
            ret, frame = self.cap.read()  # 读取帧
            cv2.imwrite(self.ob_path + f"frame_{i}.png", frame)  # 彩色
        self.flame_to_text()

    @staticmethod
    def __pixel_to_char():
        char_list = list(r"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")
        unit = int(255 / len(char_list)) + 1

        def _get_char(r, g, b, *args):
            gray = int(r * 30 + g * 59 + b * 11) / 100  # 转灰度经验公式
            return char_list[int(gray / unit)]

        return _get_char

    def flame_to_text(self):
        str_width_count, str_height_count = int(self.video_width / 3), int(self.video_height / 3)
        pixel_to_char = self.__pixel_to_char()

        def __flame_to_text(num):
            nonlocal str_width_count, str_height_count, pixel_to_char
            colors, content = [], ''  # 字符和颜色
            file_name = f"{self.ob_path}frame_{num}.png"
            image_read = Image.open(file_name).convert('RGB')
            image_read = image_read.resize((str_width_count, str_height_count), Image.NEAREST)  # 改大小

            for x in range(str_height_count):
                for y in range(str_width_count):
                    pixel = image_read.getpixel((y, x))  # 读取像素的rgb,返回一个四元组(r,g,b,a)
                    colors.append(pixel)  # 字符颜色记录到colors中,alpha通道不要
                    content += pixel_to_char(*pixel)  # 像素转字符
                content += '\n'  # 换行
                colors.append((255, 255, 255))

            char_img = Image.new("RGB", (self.video_width * 2, self.video_height * 2), (255, 255, 255))  # 新建图片
            image_write = ImageDraw.Draw(char_img)  # 准备图片写入
            font = ImageFont.load_default()  # 读取字体
            x, y = 0, 0  # 字符坐标
            font_pixel = 6  # 一个字符6*6像素
            for i in range(len(content)):
                if content[i] == '\n':
                    x += font_pixel
                    y = 0
                image_write.text((y, x), content[i], font=font, fill=colors[i])  # 生成当前ascii图片
                y += font_pixel
            char_img.save(file_name)  # 覆盖帧序列
            print(f'转换 {file_name} {num}/{self.frame_count} {num / self.frame_count * 100:.2f}%')

        for num in range(self.frame_count):  # 遍历所有图片
            __flame_to_text(num)
        self.text_to_video()

    def text_to_video(self):
        fps = int(self.cap.get(5))
        output_video = cv2.VideoWriter(f'{self.ob_path}{self.file_name.split(".")[0]}_char.avi',
                                       cv2.VideoWriter_fourcc("I", "4", "2", "0"),
                                       fps,
                                       (self.video_width * 2, self.video_height * 2))

        for num in range(self.frame_count):
            output_video.write(cv2.imread(self.ob_path + f'frame_{num}.png'))
            print(f'视频生成 {self.ob_path}frame_{num}.png {num}/{self.frame_count} {num / self.frame_count * 100:.2f}%')
        output_video.release()

    def clean(self):
        print('清理图片...')
        for num in range(self.frame_count):
            file_name = self.ob_path + f'frame_{num}.png'
            try:
                os.remove(file_name)
            except Exception:
                pass

    def convert(self):
        self.video_to_frame()
        self.clean()
        print('完成')


if __name__ == '__main__':
    VideoToChar(r"E:\test\t2.mp4").convert()

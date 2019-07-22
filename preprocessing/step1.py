import warnings
import config_submit
import os
import pydicom
import numpy as np

class PreProcessing(object):

    def __init__(self, INPUT_FOLDER):
        # 输入的文件地址 str
        self.INPUT_FOLDER = INPUT_FOLDER
        # 病人列表 list
        self.patients = []
        # 某个样例病人的文件路径 这里病人为self.patients[25] str
        self.case_path = ""
        # 这个样例病人的所有信息 list
        self.case = []
        # 记录每层的厚度信息 float
        self.slice_thickness = 0

    def init(self):
        """
        利用给到的文件夹初始化
        :return:
        """
        self.patients = os.listdir(self.INPUT_FOLDER)
        self.patients.sort()

    def load_scan(self):
        """
        读取扫描文件
        :return:
        """
        # 读入该样例病人的所有片子
        slices = [pydicom.read_file(self.case_path + '/' + s) for s in os.listdir(self.case_path)]
        # 从下到上排一下片子顺序
        slices.sort(key = lambda x: float(x.ImagePositionPatient[2]))
        # 原本做了一个不知道干啥的操作，这里先附上，回头看看有什么问题
        if slices[0].ImagePositionPatient[2] == slices[1].ImagePositionPatient[2]:
            print("""
            sec_num = 2;
            while slices[0].ImagePositionPatient[2] == slices[sec_num].ImagePositionPatient[2]:
                sec_num = sec_num+1;
            slice_num = int(len(slices) / sec_num)
            slices.sort(key = lambda x:float(x.InstanceNumber))
            slices = slices[0:slice_num]
            slices.sort(key = lambda x:float(x.ImagePositionPatient[2]))""")
        # 这个也不知道在干啥 好像在做一些防错措施 先注释掉 回头出现问题再搞回来
        try:
            slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
        except:
            self.slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)

        # 给每张都增加一个SliceThickness的特征，原来这里会报错，可能是因为没有这个属性的原因，
        # 在最前面的时候加上warnings就可以了
        for s in slices:
            s.SliceThickness = self.slice_thickness

        self.case = slices
        return slices

    def get_pixels_hu(self):
        """
        获得每个像素的HU值
        :return: 第一个记录图片的像素信息 第二个值记录图片的z x y轴每个像素之间间隔代表的实际长度
        """
        image = np.stack([s.pixel_array for s in self.case])
        # Convert to int16 (from sometimes int16),
        # should be possible as values should always be low enough (<32k)
        image = image.astype(np.int16)

        # 转换到Hounsfield Units(HU)
        for case_index, case in enumerate(self.case):
            intercept = case.RescaleIntercept
            slope = case.RescaleSlope

            if slope != 1:
                image[case_index] = slope * image[case_index].astype(np.float64)
                image[case_index] = image[case_index].astype(np.int16)

            image[case_index] += np.int16(intercept)
        # 转换为类中属性
        self.image = np.array(image, dtype=np.int16)
        self.spacing = np.array([self.case[0].SliceThickness] + self.case[0].PixelSpacing, dtype=np.float32)
        return self.image, self.spacing

    def do(self):
        """
        该类主体函数
        :return:
        """
        # 列出case路径
        self.case_path = os.path.join(self.INPUT_FOLDER,self.patients[25])
        # 读取case文件
        self.load_scan()
        # 获得每个像素的HU值
        self.get_pixels_hu()
        # 二值化
        self.binarize_per_slice()
        # print(self.case_path)
        pass

    def show(self):
        pass





if __name__ == "__main__":
    # 防止第三方库产生警告
    warnings.filterwarnings("ignore")
    INPUT_FOLDER = config_submit.config["datapath"]
    pre = PreProcessing(INPUT_FOLDER)
    pre.init()
    pre.do()
    pre.show()

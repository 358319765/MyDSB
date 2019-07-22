import warnings
import config_submit
import os


class PreProcessing(object):

    def __init__(self, INPUT_FOLDER):
        # 输入的文件地址
        self.INPUT_FOLDER = INPUT_FOLDER
        # 病人列表
        self.patients = []


    def init(self):
        """
        利用给到的文件夹初始化
        :return:
        """
        self.patients = os.listdir(self.INPUT_FOLDER)
        self.patients.sort()

    def do(self):
        """
        该类主体函数
        :return:
        """
        self.case_path = os.path.join(self.INPUT_FOLDER,self.patients[25])
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

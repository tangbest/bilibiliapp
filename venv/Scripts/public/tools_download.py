# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal
import threading
import contextlib
import requests
import os

# 线程下载基类
class CDownloaderBase(QThread):
    """download class"""
    oSignalDownload = pyqtSignal(QThread, int) # 下载量信号 list: value flag
    oSignalFinish = pyqtSignal(QThread, int) # 下载结束信号
    def __init__(self, sSavePath, sUrl):
        super(CDownloaderBase, self).__init__()
        self.m_sSavePath = sSavePath
        self.m_sUrl = sUrl
        self.m_oEventPause = threading.Event()     # pause flag
        self.m_oEventPause.set()       # True
        self.m_oEventRunning = threading.Event()      # stop flag
        self.m_oEventRunning.set()      # True
        self.m_dctHeader = {}

    def setHeader(self, dctHeader):
        self.m_dctHeader = {}

    def getHeader(self):
        dctHeaders = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            # 'Origin':'https://www.bilibili.com',
            'Pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36',
            'Referer': "",
        }
        return self.m_dctHeader.update(dctHeaders)

    def run(self):
        dctHeaders = self.getHeader()
        print("下载线程开启...")
        while self.m_oEventRunning.isSet(): # 如果被设置为了true就继续，false就终止了
            print("开始下载...", self.m_sSavePath, self.m_sUrl)
            with contextlib.closing(requests.get(self.m_sUrl, headers = dctHeaders, timeout = 5, stream=True)) as oRequest:
                print("状态码: ", oRequest.status_code)
                if oRequest.status_code != 200:
                    print("状态码有误,下载失败")
                    return
                iContentSize = int(oRequest.headers['content-length']) # 内容体总大小
                iChunkSize = int(iContentSize/100) # 单次请求最大值
                print('文件总大小: %.3f M, 单次请求最大值: %s' % (iContentSize / 1024 / 1024, iChunkSize))
                count = 0
                try:
                    self.createFile(self.m_sSavePath)
                    with open(self.m_sSavePath, "wb") as oFile:
                        #当流下载时，用Response.iter_content或许更方便些
                        #requests.get(url)默认是下载在内存中的 下载完成才存到硬盘上
                        # 可以用Response.iter_content　来边下载边存硬盘
                        for data in oRequest.iter_content(chunk_size=iChunkSize):
                            if not self.m_oEventRunning.isSet():
                                self.finishToEmit(-2)
                                return
                            self.m_oEventPause.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
                            oFile.write(data)
                            count += len(data)
                            #print("已下载大小: %s, 进度: %d%%" % (count, count / iContentSize * 100))
                            self.progressToEmit(int(count / iContentSize * 100))
                except Exception as e:
                    self.finishToEmit(-1)
                    print("错误:", e)
                    return
            break
        print("下载完成! ", self.m_sSavePath)
        self.finishToEmit(1)

    def pause(self):
        self.m_oEventPause.clear()

    def resume(self):
        self.m_oEventPause.set()

    def stop(self):
        self.m_oEventRunning.clear()
        self.exit()

    def progressToEmit(self, iProgress):
        self.oSignalDownload.emit(self, iProgress)

    def finishToEmit(self, iFlag):
        self.oSignalFinish.emit(self, iFlag)


    def createFile(self, sPath):
        import os
        sPath = sPath.replace("\\", "/")
        sDir = sPath[0:sPath.rfind("/")]
        if not os.path.isdir(sDir):  # 无文件夹时创建
            os.makedirs(sDir)
        if not os.path.isfile(sPath):  # 无文件时创建
            with open(sPath, mode="w", encoding="utf-8"):
                pass
        else:
            pass


# 不使用线程下载
def downloadByUrl(url, sPath, headers = None, dctConfig = None):
    import contextlib
    import requests
    if not dctConfig:
        dctConfig = {}
    if not headers:
        headers = {}
    header_base = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36',
        #'Referer': "",
        #'Origin': 'https://www.bilibili.com',
    }
    header_base.update(headers)
    createFile(sPath)
    with contextlib.closing(requests.get(url, headers=header_base, stream=True)) as oResponse: # stream属性必须带上
        chunk_size = dctConfig.get("ChunkSize", 1024)  # 每次下载的数据大小
        content_size = int(oResponse.headers['content-length'])  # 总大小
        if oResponse.status_code == 200:
            print('[文件大小]:%0.2f MB' % (content_size / 1024 / 1024))  # 换算单位
            with open(sPath, 'wb') as file:
                for data in oResponse.iter_content(chunk_size=chunk_size):
                    file.write(data)
    print("下载成功", url, sPath)

def createFile(sPath):
    import os
    sPath = sPath.replace("\\", "/")
    sDir = sPath[0:sPath.rfind("/")]
    if not os.path.isdir(sDir):  # 无文件夹时创建
        os.makedirs(sDir)
    if not os.path.isfile(sPath):  # 无文件时创建
        with open(sPath, mode="w", encoding="utf-8"):
            pass
    else:
        pass
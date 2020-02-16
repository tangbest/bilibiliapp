# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import  *

from widgets import ui_main
from public import dlgbase

import re
import json
import pprint
import threading
import contextlib
import requests
import os

class CMainDlg(dlgbase.CDlgBase, QMainWindow, ui_main.Ui_MainWindow):
    def __init__(self):
        super(CMainDlg, self).__init__()
        self.setupUi(self)
        self.Center()
        self.initData()
        self.initLayer()
        self.initEvent()
        self.show()

    def initData(self):
        import requests
        self.m_oRequest =requests.session()
        self.m_iAvID = None  # 视频id
        self.m_dctLinks = []  # 视频下载地址
        self.m_dctThread2Download = {}  # 下载的线程

    def onBtnMsg(self, *args):
        pSender = self.sender()
        if pSender == self.pushButtonSearch:
            self.clickSearch()
        elif pSender == self.pushButtonDownload:
            self.clickDownload()
        elif pSender == self.pushButtonAllStart:
            self.startAllDownload()
        elif pSender == self.pushButtonAllPause:
            self.pauseAllDownload()
        elif pSender == self.pushButtonClearAll:
            self.clearAllDownload()
        elif pSender == self.pushButtonOpenDir:
            self.openDownloadDir()
        elif pSender == self.pushButtonDownloadPic:
            self.downloadPicture()

    def downloadPicture(self):

        sUrl = self.lineEditCover.text()
        if not sUrl:
            return
        sFileName, sFileType = QFileDialog.getSaveFileName(self, "Save File", ".",
                                                           "Png(*.png);;Jpg(*.jpg);;All files(*.*)")
        #from public import tools_url
        #tools_url.downloadByUrl(sUrl, sFileName)
        from public import tools_download
        self.m_oThreadPic = tools_download.CDownloaderBase(sFileName, sUrl)
        self.m_oThreadPic.run()

    def openDownloadDir(self):
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.getcwd()+'/videos'))
        except:
            pass

    def clearAllDownload(self):
        for iID, oThread in self.m_dctThread2Download.items():
            oThread.stop()
        self.tableWidgetDownload.clearContents()
        self.tableWidgetDownload.setRowCount(0)
        self.m_dctThread2Download.clear()

    def pauseAllDownload(self):
        for iID, oThread in self.m_dctThread2Download.items():
            oThread.pause()

    def startAllDownload(self):
        for iID, oThread in self.m_dctThread2Download.items():
            oThread.resume()


    def clickSearch(self):
        print("点击了搜索")
        sUrl = self.lineEditInput.text()
        if not sUrl:
            return
        try:
            iAvNum = re.findall(r'(av\d+)', sUrl)[0]
        except:
            return
        print("AvNum: {avNum}, Url: {url}".format(avNum=iAvNum, url=sUrl))
        base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Connection': 'keep-alive',
            'Host': 'www.bilibili.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36',
        }
        oResult = self.m_oRequest.get(sUrl, headers=base_headers, timeout=3)
       # print("Text: \n", oResult.text)
       # print("Cookies: \n", oResult.cookies)
        iStatusCode = oResult.status_code
        print("StatusCode: ", iStatusCode)
        if iStatusCode != 200:
            print("访问失败...")
            return
        data = re.findall(r'<script>window\.__INITIAL_STATE__=(.*?);\(function', oResult.text)[0]
        dctBiliData = json.loads(data)
        #print("有效数据: ")
        #pprint.pprint(dctData)
        aid = dctBiliData['aid']
        title = dctBiliData.get("videoData", {}).get("title", "")
        pubtime = dctBiliData.get("videoData", {}).get("pubdate", "")
        up = dctBiliData.get("upData", {}).get("name", "")
        vtype = dctBiliData.get("videoData", {}).get("tname", "")
        cover = dctBiliData.get("videoData", {}).get("pic", "")
        desc = dctBiliData.get("videoData", {}).get("desc", "")
        self.lineEditAv.setText(str(aid))
        self.lineEditTitle.setText(str(title))
        self.lineEditTime.setText(str(pubtime))
        self.lineEditAuthor.setText(str(up))
        self.lineEditType.setText(str(vtype))
        self.lineEditCover.setText(str(cover))
        self.lineEditDesc.setText(str(desc))

        self.m_iAvID = aid
        self.m_sTitle = title
        self.m_dctLinks = self.getVideoLinks(oResult.text)

    def getVideoLinks(self, sText):
        # get video download links
        from public import tools
        dctDownloadLink = {}
        try:
            data = re.findall(r'<script>window\.__playinfo__=(.*?)</script>', sText)[0]
            dctBiliData = json.loads(data)
            #pprint.pprint(dctBiliData)
            lstLinkData = dctBiliData['data']['dash']['video']
            sAudioUrl = dctBiliData['data']['dash']['audio'][0]["base_url"].replace("http", "https")
            sVideoUrl = dctBiliData['data']['dash']['video'][0]["base_url"].replace("http", "https")
            dctDownloadLink["AudioUrl"] = sAudioUrl
            dctDownloadLink["VideoUrl"] = sVideoUrl
        except:
            print("解析地址失败...")
        print("下载链接 ", dctDownloadLink)
        return dctDownloadLink

    def clickDownload(self):
        print("点击了下载")
        if not self.m_dctLinks:
            return
        iRow = self.tableWidgetDownload.rowCount()
        oThreadDownload = CDownloader(self.m_iAvID, self.m_dctLinks)
        self.m_dctThread2Download[iRow] = oThreadDownload
        oThreadDownload.start()

        self.tableWidgetDownload.setRowCount(iRow + 1)
        sID = "%s" % self.m_iAvID
        print("ID and Rown", sID, iRow)
        pItem = QTableWidgetItem(sID)
        self.tableWidgetDownload.setItem(iRow, 0, pItem)
        pItem = QTableWidgetItem(self.m_sTitle)
        self.tableWidgetDownload.setItem(iRow, 1, pItem)
        pItem = QProgressBar()
        pItem.setValue(0)
        self.tableWidgetDownload.setCellWidget(iRow, 2, pItem)
        oThreadDownload.oSignalDownload.connect(self.onUpdateProgress)

    # 进度更新
    def onUpdateProgress(self, oThread, iProgress):
        for iRow, oThreadDownload in self.m_dctThread2Download.items():
            if oThread == oThreadDownload:
                self.tableWidgetDownload.cellWidget(iRow, 2).setValue(iProgress)

    def initLayer(self):
        #self.initStyle()
        pass

    def initEvent(self):
        self.pushButtonSearch.clicked.connect(self.onBtnMsg)
        self.pushButtonDownload.clicked.connect(self.onBtnMsg)
        self.pushButtonAllStart.clicked.connect(self.onBtnMsg)
        self.pushButtonAllPause.clicked.connect(self.onBtnMsg)
        self.pushButtonClearAll.clicked.connect(self.onBtnMsg)
        self.pushButtonOpenDir.clicked.connect(self.onBtnMsg)
        self.pushButtonDownloadPic.clicked.connect(self.onBtnMsg)

    def initStyle(self):
        qss_file = QFile(":res/style.qss")
        qss_file.open(QFile.ReadOnly)
        qss = str(qss_file.readAll(), encoding='utf-8')
        qss_file.close()
        self.setStyleSheet(qss)
        return
        try:
            with open(sStylePath) as f:
                style = f.read()  # 读取样式表
                self.setStyleSheet("../Res/style.qss")
        except:
            print("open stylesheet error")


class CDownloader(QThread):
    """download class"""
    oSignalDownload = pyqtSignal(QThread, int) # 下载量信号 list: value flag
    oSignalFinish = pyqtSignal(QThread, int) # 下载结束信号
    def __init__(self, iAvID, dctLinks):
        super(CDownloader, self).__init__()
        self.m_iAvID = iAvID
        self.m_dctLinks = dctLinks
        self.m_oEventPause = threading.Event()     # pause flag
        self.m_oEventPause.set()       # True
        self.m_oEventRunning = threading.Event()      # stop flag
        self.m_oEventRunning.set()      # True
        sScrPath = os.getcwd()
        self.m_sDir = os.path.join(sScrPath, "./videos")
        if not os.path.exists(self.m_sDir):
            os.mkdir(self.m_sDir)

    def run(self):
        """download a video
        may contain muti-slices videos
        """
        headers = {
            'Accept':'*/*',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
            'Cache-Control':'no-cache',
            'Connection':'keep-alive',
            'Origin':'https://www.bilibili.com',
            'Pragma':'no-cache',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36',
        }
        headers['Referer'] = 'https://www.bilibili.com/video/av%s' % self.m_iAvID
        print("下载线程开启...")
        sAudioPath = self.m_sDir + os.sep + str(self.m_iAvID) + ".mp3"
        sVideoPath = self.m_sDir + os.sep + str(self.m_iAvID) + ".mp4"
        sOutputPath = self.m_sDir + os.sep + "av" + str(self.m_iAvID) + ".mp4"
        for sType, sUrl in self.m_dctLinks.items():
            if sType == "AudioUrl":
                sFileName = sAudioPath
            else:
                sFileName = sVideoPath
            while self.m_oEventRunning.isSet(): # 如果被设置为了true就继续，false就终止了
                print("开始下载...", sFileName)
                with contextlib.closing(requests.get(sUrl, headers = headers, timeout = 3, stream=True)) as oRequest:
                    print("状态码: ", oRequest.status_code)
                    iContentSize = int(oRequest.headers['content-length']) # 内容体总大小
                    iChunkSize = int(iContentSize/100) # 单次请求最大值
                    print('文件总大小: %02sM, 单次请求最大值: %s' % (iContentSize / 1024 / 1024, iChunkSize))
                    count = 0
                    try:
                        with open(sFileName, "wb") as file:
                            #当流下载时，用Response.iter_content或许更方便些
                            #requests.get(url)默认是下载在内存中的 下载完成才存到硬盘上
                            # 可以用Response.iter_content　来边下载边存硬盘
                            for data in oRequest.iter_content(chunk_size=iChunkSize):
                                if not self.m_oEventRunning.isSet():
                                    self.finishToEmit(-2)
                                    return
                                self.m_oEventPause.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
                                file.write(data)
                                count += len(data)
                                #print("已下载大小: %s, 进度: %d%%" % (count, count / iContentSize * 100))
                                self.progressToEmit(int(count / iContentSize * 100))
                    except Exception as e:
                        self.finishToEmit(-1)
                        print("错误:", e)
                        return
                print("下载完成! ", sFileName)
                break
        try:
            self.combineVideo(sAudioPath, sVideoPath, sOutputPath)
            self.delSourceFile(sAudioPath, sVideoPath)
        except Exception as e:
            print("错误,请检查是否安装了ffmpeg", e)
        self.finishToEmit(1)

    # 合成音频和视频
    def combineVideo(self, sAudioPath, sVideoPath, sOutputPath):
        import subprocess
        import ffmpeg
        print("开始合成音频和视频...", sAudioPath, sVideoPath, sOutputPath)
        sCmd = 'ffmpeg -i ' + sAudioPath + ' -i ' + sVideoPath + ' -vcodec copy -acodec copy -y ' + sOutputPath
        subprocess.run(sCmd, shell=True)
        print("合成完成...")
        self.combineFinish()

    # 删除源文件
    def delSourceFile(self, sAudioPath, sVideoPath):
        print("删除源文件: ", sAudioPath, sVideoPath)
        os.remove(sAudioPath)
        os.remove(sVideoPath)

    def combineFinish(self):
        print("合成成功!")

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


def openMainDlg():
    import sys
    app = QApplication(sys.argv)
    w = CMainDlg()
    sys.exit(app.exec_())
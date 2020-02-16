# -*- coding: utf-8 -*-


def openUrl(self, sUrl):
    from PyQt5.QtGui import QDesktopServices
    QDesktopServices.openUrl(
        QUrl(sUrl)
    )


def saveToFile(sText, sPath):
    createFile(sPath)
    with open(sPath, 'w', encoding='utf-8') as oFile:
        oFile.write(sText)

def createFile(sPath):
    import os
    sPath = sPath.replace("\\", "/")
    path = filename[0:filename.rfind("/")]
    if not os.path.isdir(path):  # 无文件夹时创建
        os.makedirs(path)
    if not os.path.isfile(sPath):  # 无文件时创建
        with open(sPath, mode="w", encoding="utf-8"):
            pass
    else:
        pass
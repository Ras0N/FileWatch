# -*- coding:GBK -*-
import sys
import time 
import logging 
import os
import ctypes
from FileChain import FileTree
from CompressThread import CompressThread
from ctypes import Structure
from ctypes import wintypes
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.utils import dirsnapshot
import logging
e_dirs_created = 0b00000001
e_dirs_deleted = 0b00000010
e_dirs_modified = 0b00000100
e_dirs_moved = 0b00001000

e_files_created = 0b00010000
e_files_deleted = 0b00100000
e_files_modified = 0b01000000
e_files_moved = 0b10000000    

class browseinfo(Structure):
    _fields_=[('hwndOwner',ctypes.wintypes.HWND),
              ('pidRoot',ctypes.c_void_p),
              ('pszDisplayName',ctypes.wintypes.LPCSTR),
              ('lpszTitle',ctypes.c_wchar_p),
              ('ulFlags',ctypes.c_uint),
              ('lpFn',ctypes.c_void_p),
              ('lParam',ctypes.c_void_p),
              ('iImage',ctypes.c_int)]
class tagINITCOMMONCONTROLSEX(Structure):
    _fields_=[('dwSize',ctypes.wintypes.DWORD),('dwICC',ctypes.wintypes.DWORD)]
class FileState(dirsnapshot.DirectorySnapshotDiff):
    def __init__(self,ref,NewSnap):
        super(FileState,self).__init__(ref,NewSnap)

    def GetState(self):
        # 获取对比后的状态
        state = 0        
        if self._dirs_created:
            state |= e_dirs_created
        if self._dirs_deleted:
            state |= e_dirs_deleted
        if self._dirs_modified:
            state |= e_dirs_modified
        if self._dirs_moved:
            state |= e_dirs_moved
        if self._files_created:
            state |= e_files_created
        if self._files_deleted:
            state |= e_files_deleted
        if self._files_modified:
            state |= e_files_modified
        if self._files_moved:
            state |= e_files_moved
        return state
    
    
class MyFileHandler(FileSystemEventHandler):
    __FileOldSnap = ''
    __FileNewSnap = ''
    __DirPath = ''
    __FileCount = 0
    __ComThread = None
    def __init__(self,path):
        #FileSystemEventHandler.__init__(self)
        super(MyFileHandler,self).__init__()
        self.__DirPath = path
        self.__FileOldSnap = dirsnapshot.DirectorySnapshot(self.__DirPath)
        self.__FileCount = 0
        
    def on_any_event(self,event):
        logging.info('[*] Event catched!')
        self.__FileNewSnap = dirsnapshot.DirectorySnapshot(self.__DirPath)
        FileCmp =FileState(self.__FileOldSnap,self.__FileNewSnap)
        CmpState = 0
        CmpState = FileCmp.GetState()
        if CmpState & e_dirs_created :# 检测文件夹创建
            DirArray = FileCmp.dirs_created
            for element in DirArray:
                print '[*] Directory Created! ',element
        if CmpState & e_dirs_moved :# 检测文件夹重命名
            DirMovedArray = FileCmp.dirs_moved
            for element in DirMovedArray:
                print '[*] Directory :',element[0],'renamed as :',element[1]            
        if CmpState & e_files_created :# 检测文件的创建
            FileArray = FileCmp.files_created
            for element in FileArray:
                print '[*] File Created! ',element
                log = '[*] File Created! '+element
                logging.info(log)
                self.__FileCount += 1
        if CmpState & e_files_modified:# 检测文件是否进行了更改
            FileArray = FileCmp.files_modified
            for element in FileArray:
                print '[*] File modified! ',element
        if CmpState & e_files_moved:# 检测文件重命名事件
            FileMovedArray = FileCmp.files_moved
            for element in FileMovedArray:
                print '[*] File :',element[0],'renamed as :',element[1]

        self.__FileOldSnap = self.__FileNewSnap # 更新列表
        if self.__FileCount > 16:
            self.__FileCount = 0
            FileList = FileTree(self.__DirPath)
            FileList.SetNode()
            fFile = FileList.CheckFileExt('.txt')
            if self.__ComThread == None or self.__ComThread.IsRunning() == False:
                self.__ComThread = CompressThread(fFile)
                if not self.__ComThread.IsRunning():
                    self.__ComThread.start()
                    
    def StopThread(self):
        if self.__ComThread.IsRunning:
            self.__ComThread.SetStop()
            self.__ComThread.join()
            
def main():
    Shell32=ctypes.windll.LoadLibrary('Shell32.dll')
    Comctl32=ctypes.windll.LoadLibrary('Comctl32.dll')
    MAX_PATH = 255
    szReturnPath = (ctypes.wintypes.WCHAR * MAX_PATH)()
    bInfo = browseinfo()
    bInfo.hwndOwner = None
    bInfo.iImage = 0
    bInfo.lParam = None
    bInfo.lpfn = None
    bInfo.lpszTitle = "选择要监视的文件夹"
    bInfo.pszDisplayname = ctypes.byref(szReturnPath)
    bInfo.ulFlags = 0x80 | 0x10
    InitCtrls = tagINITCOMMONCONTROLSEX(0,0)
    Comctl32.InitCommonControlsEx(ctypes.byref(InitCtrls))
    pil = Shell32.SHBrowseForFolderW(ctypes.byref(bInfo))
    if pil != 0:
        Shell32.SHGetPathFromIDListW(pil,szReturnPath)
        print 'Path Found!'
        print szReturnPath.value
        logging.info('Path Found!')
        logging.info(szReturnPath.value)
        path = szReturnPath.value
        event_handler = MyFileHandler(path)
        observer = Observer()
        observer.schedule(event_handler,path,recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            event_handler.StopThread()
            observer.stop()
        observer.join()


if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO,
                        format = '%(asctime)s %(filename)s[Line:%(lineno)d] %(levelname)s %(message)s',
                        filename = 'runtime.log',
                        filemode = 'a+')    
    main()

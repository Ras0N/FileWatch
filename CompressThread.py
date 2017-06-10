# -*- coding:GBK -*- 

import threading
import os
import errno
import logging

class CompressThread(threading.Thread):
    __FileList = []
    __bIsRun = False
    __SetStop = False
    def __init__(self,FileList):
        super(CompressThread,self).__init__()
        self.__FileList = FileList
        self.__bIsRun = False
        self.__SetStop = False
        
    def ComPressFiles(self):
        self.__bIsRun = True
        for elements in self.__FileList:
            if not self.__SetStop:
                j = len(elements) - 1
                for i in range(j):
                    if not self.__SetStop:
                        nName,nExt = os.path.splitext(elements[i])
                        compName = nName + '.7z'
                        cmd = '7za.exe a -t7z "'+compName+'" "'+elements[i]+'" -mx5 -ms -mmt'
                        print '[*] Compressing ...'
                        print cmd
                        logging.info('[*] Compressing ...')
                        logging.info(cmd)
                        t = os.system(cmd.encode('GBK'))
                        if t == 0:#执行成功，返回0值
                            logging.info('[*] Success!')
                            try:
                                #os.remove(elements[i])
								logging.info('[*] File removed')
                            except WindowsError,e:
                                logging.error('[*] Delete File Err!')
                                logging.info(e)
                        else:#失败，删除程序创建的空7z文件
                            logging.warning('[*] Compress failed!')
                            try:
                                os.remove(compName)
                            except WindowsError,e:
                                logging.error('[*] Delete File Err!')
                                logging.info(e)                            
                    else:
                        print '[*] Thread has been Closed by User!'
                        logging.warning('[*] Thread has been Closed by User!')
                        break
            else:
                break
        self.__bIsRun = False
        
    def IsRunning(self):
        return self.__bIsRun
    
    def run(self):
        if self.__bIsRun:
            print '[*] Thread is Running!'
            logging.warning('[*] Thread is Running!')
        else :
            self.__SetStop = False
            if self.__FileList == [] :
                print '[*] Empty List'
                logging.warning('[*] Empty List')
            else:
                self.ComPressFiles()
    
    def SetStop(self):
        self.__SetStop = True

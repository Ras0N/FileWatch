# -*- coding:GBK -*-

import os 
import sys
from CompressThread import CompressThread
import time
import logging
'''
    实现最基本的文件链表结构
    表结构：数据块+指针块
    指针快包括四项，分别是：上一个节点的指针，下一个节点的指针，父节点指针，子节点指针
    上一个节点的指针，当为链表头时指向自己。下一个节点的指针，当为链表尾的时候指向自己。
    父节点指针无新的父节点时，指向自己，子节点当无新的子节点时指向自己
'''

class FileNode(object):
    __Content = ''
    __pBefore = None
    __pNext = None
    __pParent = None
    __pChild = None
    def __init__(self,parent = 0):
        print '[*] node created!'
        logging.info('[*] node created!')
        if not parent:
            parent = self
        self.__pBefore = self
        self.__pNext = self
        self.__pParent = parent
        self.__pChild = self
    
    def SetContent(self,context):
        self.__Content = context 

        
    def GetContent(self):
        return self.__Content
    
    def SetpBefore(self,pBefore):
        self.__pBefore = pBefore
        
    def GetpBefore(self):
        return self.__pBefore
    
    def SetpNext(self,pNext):
        self.__pNext = pNext
        
    def GetpNext(self):
        return self.__pNext
    
    def SetParent(self,parent):
        self.__pParent = parent
        
    def GetParent(self):
        return self.__pParent
    
    def SetChild(self,child):
        self.__pChild = child
        
    def GetChild(self):
        return self.__pChild
    
    def isHead(self):
        if self.GetpBefore() == self:
            return True
        else:
            return False
        
    def isTail(self):
        if self.GetpNext() == self:
            return True
        else:
            return False
    
    def HasChild(self):
        if self.GetChild() == self:
            return False
        else:
            return True
        
    def HasParent(self):
        if self.GetParent() == self:
            return False
        else:
            return True
class FileTree(object):
    __FileTree = None
    __Path = ''
    __FileList = []
    def __init__(self,path):
        self.__FileTree = FileNode() # 新建父节点
        self.__Path = path
        
        
    def SetNode(self,path = 0,currentTree = 0):
        if path == 0:
            path = self.__Path
        if currentTree == 0:
            currentTree = self.__FileTree
        pList = os.listdir(path)
        pLen = len(pList)-1
        for i,elements in enumerate(pList):
            if os.path.isdir(os.path.join(path,elements)):# 为文件夹
                ChildNode= FileNode(currentTree) # 以当前节点作为下一级节点的父节点
                currentTree.SetContent(elements) # 填充当前节点的目录信息
                currentTree.SetChild(ChildNode)# 将新节点填入当前节点的子节点当中
                self.SetNode(os.path.join(path,elements),ChildNode)#补全子节点
            else :# 为文件
                currentTree.SetContent(elements)# 填充文件信息
            if not i == pLen: #不为末节点
                    NextNode = FileNode()# 新建下一个节点
                    currentTree.SetpNext(NextNode)# 将下一个节点信息填充进当前节点
                    if currentTree.HasParent():# 若当前节点为父节点
                        NextNode.SetParent(currentTree.GetParent())# 复制当前节点父节点信息
                    NextNode.SetpBefore(currentTree)
                    currentTree = NextNode# 修改当前节点为下一个节点
                    
    def DeleteNode(self,node):
        LastNode = node.GetpBefore()
        NextNode = node.GetpNext()
        LastNode.SetpNext(NextNode)
        NextNode.SetpBefore(LastNode)
        del node # 释放变量
        # gc.collect() 
        
    def InsertNode(self,node,lastnode):
        node.SetpNext(lastnode.GetpNext)
        node.SetpBefore(lastnode)
        lastnode.SetpNext(node)
        
    def CheckFileExt(self,ext,Node = 0):
        if Node == 0:
            Node = self.__FileTree
        bQuit = False # 遍历到最后
        LastChecked = False
        FileList = []
        FileCount = 0
        while not bQuit:
            if Node.GetContent() == None:
                FName = ''
                FExt = ''
            else:
                FName,FExt = os.path.splitext(Node.GetContent())
            if FName == '':
                bQuit = True
                break
            if FExt == '':
                cDirFileList =self.CheckFileExt(ext,Node.GetChild())
                # 文件夹不一定最后遍历，可以在任何地方
                if not cDirFileList == []:
                    if FileList == []:
                        FileList = cDirFileList
                    else:
                        FileList.extend(cDirFileList)
            if cmp(FExt.upper(),ext.upper()) == 0:
                FileName = Node.GetContent()
                NodeParent = Node
                while NodeParent.HasParent():
                    NodeParent = NodeParent.GetParent()
                    FileName = os.path.join(NodeParent.GetContent(),FileName)
                FileName = os.path.join(self.__Path,FileName)
                if FileList == []:
                    FileList.append(FileName)
                    FileList = [FileList]
                    FileCount += 1
                elif type(FileList[0]) is list :# 已经存在列表
                    if FileCount == 0: # 添加第一个文件，需要新建列表
                        FileList.insert(0,[])# 创建新列表
                        FileList[0].append(FileName)
                        FileCount += 1
                    else:
                        FileList[0].append(FileName)
                        FileCount += 1
                else :#不存在列表
                    FileList = [FileList]
                    FileList[0].append(FileName)
                    FileCount += 1
            Node = Node.GetpNext()
            if Node.isTail():#到末尾
                if Node.isHead(): #仅存在此文件夹
                    bQuit = True#已经遍历，退出
                elif LastChecked == False:
                    LastChecked = True
                else:
                    bQuit = True
        while True:
            try:
                FileList.remove([])
            except ValueError:
                break
        return FileList
#def main():
    #path = 'F:\\123'
    #a = FileTree(path)
    #a.SetNode()
    #fList = a.CheckFileExt('.txt')
    #for elements in fList:
        #for subelements in elements:
            #print subelements
    #ComThread = CompressThread(fList)
    #ComThread.start()
    #try:
        #while True:
            #time.sleep(1)
            #if ComThread.IsRunning() == False:
                #break
    #except KeyboardInterrupt:
        #ComThread.SetStop()
    #ComThread.join()
    #print ''
    #print 'Finished!'
    
#if __name__ == "__main__":
    #main()
                

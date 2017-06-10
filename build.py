#-*- coding:GBK -*-
from distutils.core import setup
import py2exe
import sys
sys.argv.append('py2exe')
includes = []
py2exe_options = {"py2exe":{
           "compressed":1,
           "optimize":2,
           #"bundle_files":1,
           "includes":includes,
           "dll_excludes":["MSVCP90.dll"],
           }}
setup(
    name = 'Compressor',
    version = '0.0.2',
    console = [{"script":"FileWatcher.py","icon_resources":[(1,"Compress.ico")]}],
    zipfile = None,
    description = u'文件监视压缩程序',
    options = py2exe_options,
)

from bypy import ByPy
import os
bp = ByPy()
bp.mkdir('债权债务/2013-2016/')
for file in os.listdir('债权债务'):
    if file.endswith(".xls"):
        print("债权债务/"+file)
        bp.upload(localpath="债权债务/"+file,remotepath='债权债务/2013-2016/',ondup='newcopy')


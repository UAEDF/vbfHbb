#!/bin/sh

#./printSingleChoice.py 6 12 "drawopts:colz" "title x:leading b-jet CSV" "title y:m_{q#bar{q}} (GeV)" "savename:signQCDA.pdf" "colour:625" "text:Set A,QCD" "val:2" "norm:1" #419
#./printSingleChoice.py 8 10 "drawopts:colz" "title x:m_{q#bar{q}} (GeV)" "title y:|#Delta#eta_{q#bar{q}}|" "savename:signQCDB.pdf"  "colour:602" "text:Set B,QCD" "val:1" "norm:1" 
#./printSingleChoice.py 6 36 "drawopts:colz" "title x:leading b-jet CSV" "title y:m_{q#bar{q}} (GeV)" "savename:sign125A.pdf" "colour:625" "text:Set A,VBF signal" "val:2" "norm:1" #419
#./printSingleChoice.py 8 30 "drawopts:colz" "title x:m_{q#bar{q}} (GeV)" "title y:|#Delta#eta_{q#bar{q}}|" "savename:sign125B.pdf"  "colour:602" "text:Set B,VBF signal" "val:1" "norm:1"
#./printSingleChoice.py 2 1 "drawopts:colz,text" "title x:leading b-jet CSV" "title y:m_{q#bar{q}} (GeV)" "savename:mapA.pdf" "colour:625" "text:Set A" "val:2" #419
#./printSingleChoice.py 3 1 "drawopts:colz,text" "title x:m_{q#bar{q}} (GeV)" "title y:|#Delta#eta_{q#bar{q}}|" "savename:mapB.pdf"  "colour:602" "text:Set B" "val:1"
#
#./printSingleChoice.py 6 12 "drawopts:colz" "title x:leading b-jet CSV" "title y:m_{q#bar{q}} (GeV)" "savename:signQCDA.pdf" "colour:1" "text:Set A,QCD" "val:2" "norm:1" #419
#./printSingleChoice.py 8 10 "drawopts:colz" "title x:m_{q#bar{q}} (GeV)" "title y:|#Delta#eta_{q#bar{q}}|" "savename:signQCDB.pdf"  "colour:1" "text:Set B,QCD" "val:1" "norm:1" 
#./printSingleChoice.py 6 35 "drawopts:colz" "title x:leading b-jet CSV" "title y:m_{q#bar{q}} (GeV)" "savename:sign125A.pdf" "colour:1" "text:Set A,VBF signal" "val:2" "norm:1" #419
#./printSingleChoice.py 8 29 "drawopts:colz" "title x:m_{q#bar{q}} (GeV)" "title y:|#Delta#eta_{q#bar{q}}|" "savename:sign125B.pdf"  "colour:1" "text:Set B,VBF signal" "val:1" "norm:1"
#./printSingleChoice.py 2 1 "drawopts:colz,text" "title x:leading b-jet CSV" "title y:m_{q#bar{q}} (GeV)" "savename:mapA.pdf" "colour:1" "text:Set A" "val:2" #419
#./printSingleChoice.py 3 1 "drawopts:colz,text" "title x:m_{q#bar{q}} (GeV)" "title y:|#Delta#eta_{q#bar{q}}|" "savename:mapB.pdf"  "colour:1" "text:Set B" "val:1"
./printSingleChoice.py 19 179 "drawopts:hist" "title x:" "title y:Trigger Scale Factor" "savename:scaleB.pdf"  "colour:1" "text:Set B" "val:1"

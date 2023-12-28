# coetool
coetool is a cli or gui program to convert from .coe files (memory map for a ROM in an FPGA) to image files and the other way around, load an image and generate .coe file. Original author: http://jqm.io/files/coetool/

# Usage:
convert from .coe file (VGA mem) to image file and vice versa(Support RGB888, RGB565 and RGB332)

No gui:  `python coetool.py -c RGB565 Lenna.png Lenna565.coe`

gui: `python coetool.py` or `python coetoolgui.py`

# denpendencies: 
python3 + PyQt5 + PIL

# License:
GPL

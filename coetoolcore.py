# -*- coding: utf-8 -*-

"""
Doc...

"""

from PyQt5 import QtCore, QtGui
from PIL import Image
import tempfile

from PyQt5.QtGui import qRgb


class CoeConverter:
    
    def __init__(self, in_file, rgb_format="RGB565"):
        
        self.in_file = in_file
        self.in_file_ext = in_file.rsplit('.',maxsplit=1)[1].lower()

        # RGB888, RGB565, RGB332
        self.rgb_format = rgb_format


        #RGB palette generation: Red(3bits) Green(3bits) Blue(2bits)/1pixel = 256 colors (as used in .coe VGA mem files). NECESSARY
        # self.Qtrgb332_palette=[] 
        
        #for i in range(256):
            # & 224 means a bit mask for the MSB and >> 5 is a bitwise to strip LSB bits
            #self.Qtrgb332_palette.append(QtGui.qRgb( int(((i & 224) >> 5)*(255/7)), int(((i & 28) >> 2)*(255/7)), int((i & 3)*(255/3)))) 
        
        self.dataInit()
        
        
    def dataInit(self):
        
        if self.in_file_ext == 'coe':
            img_content = self.coe_parse('memory_initialization_vector=', ';', '=').replace('\n','').split(',')
            # self.imgbytes = bytes.fromhex(img_content)
            self.height=int(self.coe_parse('Height:',',',' '))
            self.width=int(self.coe_parse('Width:','\n',' ')) #end char = new line!
            self.img = QtGui.QImage(self.width, self.height, QtGui.QImage.Format_RGB32)
            length = len(img_content[0])
            # 16进制长度为2说明是rgb332
            if length == 2:
                for h in range(self.height):
                    for w in range(self.width):
                        rgb332 = int(img_content[self.width * h + w], 16)
                        value = qRgb((rgb332 >> 5) & 0x07, (rgb332 >> 2) & 0x7, rgb332 & 0x3)
                        self.img.setPixel(w, h, value)
            elif length == 4:
                # rgb565
                for h in range(self.height):
                    for w in range(self.width):
                        rgb565 = int(img_content[self.width * h + w], 16)
                        value = qRgb((rgb565 >> 11) & 0x1F, (rgb565 >> 5) & 0x3F, rgb565 & 0x1F)
                        self.img.setPixel(w, h, value)
            elif length == 6:
                # rgb888
                for h in range(self.height):
                    for w in range(self.width):
                        rgb565 = int(img_content[self.width * h + w], 16)
                        value = qRgb((rgb565 >> 16) & 0xFF, (rgb565 >> 8) & 0xFF, rgb565 & 0xFF)
                        self.img.setPixel(w, h, value)
            
        else:
            img = QtGui.QImage(self.in_file)
            self.height = str(img.height())
            self.width = str(img.width())
            #img2 = img.convertToFormat(QtGui.QImage.Format_Indexed8, self.Qtrgb332_palette) #create 8 bits img with QImage Qtrgb332_palette necessary.
            img2 = img.convertToFormat(QtGui.QImage.Format_RGB888) #create 24 bits img with QImage Qtrgb888
            tmpfileimg2 = tempfile.NamedTemporaryFile(suffix='.bmp', delete=False)
            tmpfileimg2.close()
            img2.save(tmpfileimg2.name,'BMP',-1) #save 8 bits img with QImage  try via buffer TO-DO create _tmp_ file
            img3 = Image.open(tmpfileimg2.name) #open image with PIL
            #self.imgbytes =[format(i, '02x').upper() for i in list(img3.getdata())] #extract data with PIL
            self.imgbytes =tuple(list(img3.getdata())) #extract data with PIL
            
               
    def coe_parse(self, key_name, key_end_char, separator):
        with open(self.in_file, encoding='utf-8', mode='r') as coefile:
            coefile_data = coefile.read()   
            key=key_name
            key_offset=coefile_data.find(key)
            key_end=coefile_data.find(key_end_char,key_offset) 
            key_value=coefile_data[key_offset:key_end].split(separator)[1] 

            return key_value


    def createCoe(self, out_file):
        with open(out_file, encoding='utf-8', mode='wt') as out_coe_file:
            out_coe_file.write('; VGA Memory Map\n; .COE file with HEX coefficients\n; Height: '+self.height+', Width: '+self.width+'\n\nmemory_initialization_radix=16;\n')
            out_coe_file.write('memory_initialization_vector=\n')
           
            for i, b in enumerate(self.imgbytes):
                if i > 0 and i % 16 == 0:           #TO-DO check if necessary, check in FPGA
                    out_coe_file.write('\n')

                # 不同rgb format的输出生成
                if self.rgb_format == "RGB565":
                    out = (((b[0] & 0xf8) >> 3) << 11) | (((b[1] & 0xfc) >> 2) << 5) | ((b[2] & 0xf8) >> 3)
                    # out_coe_file.write("%x" % out)
                elif self.rgb_format == "RGB888":
                    out = (b[0] << 16) | (b[1] << 8) | b[2]
                elif self.rgb_format == "RGB332":
                    out = (b[0] & 0xe0) | (b[1] & 0x1c) | (b[2] & 0x03)
                else:
                    print("ERROR: Unknown rgb format.")
                    exit(-1)

                out_coe_file.write("%x" % out)

                if i == len(self.imgbytes) - 1:
                    out_coe_file.write(';')
                else:
                    out_coe_file.write(',')
            
            
    def exportImg(self, out_file, imgformat):
        self.img.save(out_file, imgformat, -1)
        print('file ' + out_file + ' written to disk')
    

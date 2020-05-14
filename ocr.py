import os
from PIL import Image
import pytesseract
import datetime

def normalize(im):
    newimdata = []
    orange = (231, 148, 119)
    black = (0,0,0)
    white = (255,255,255)
    for color in im.getdata():
        if color == orange:
            newimdata.append( white )
        elif color == white:
        	newimdata.append( black )
        else:
            newimdata.append( white )
    newim = Image.new(im.mode,im.size)
    newim.putdata(newimdata)
    return newim

def recognize(im):
	norm = normalize(im)
	digits = pytesseract.image_to_string(norm, config='--psm 7')
	digits = digits.replace(' ','').replace('O','0').replace('I','1').replace('l','1').replace('B','8').replace('S','5').replace('A','4').replace('Z','2').replace('g','8')
	try:
		strength = int(digits)
	except ValueError as e:
		im.save(f'screenshots/unrecognized_strength_{datetime.datetime.now():%Y%m%d_%H%M%S}.png')
		print('Failed to OCR digits!')
		strength = 200000		
	return strength

if __name__ == '__main__':
	for filename in os.listdir('ocrtest'):
		if filename.endswith('.png') and filename.startswith('test'):
			pic = Image.open(f'ocrtest/{filename}')
			norm = normalize(pic)
			norm.save(f'ocrtest/n{filename}')
			scan = pytesseract.image_to_string(norm, config='--psm 7').replace(' ','')
			print(filename, scan)

	print('Done!')
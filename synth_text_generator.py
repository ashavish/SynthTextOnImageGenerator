# Synthetic Text Superimposition on images


import random,string
from PIL import Image, ImageDraw,ImageFont,ImageOps
import numpy as np
import glob
import os
import yaml

with open("config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile,Loader=yaml.FullLoader)


def random_number_generation(length=10):
	x = random.sample(range(0,10), length)
	x = list(map(str,x))
	return "".join(x)

def random_alphanumeric_generator(length=10):
	special_chars = ["@","_","-",":"," "]
	no_digits = random.choice(range(0,length))
	no_alphabets = length - no_digits
	x = random.sample(range(0,10), no_digits)
	x = list(map(str,x))
	y = random.sample(list(string.ascii_uppercase) + list(string.ascii_lowercase) + special_chars, no_alphabets)
	y = list(map(str,y))
	z = x + y
	random.shuffle(z)	
	return "".join(z)

def random_alphabet_generator(length=10):
	special_chars = ["@","_","-",":"," "]
	y = random.sample(list(string.ascii_uppercase) + list(string.ascii_lowercase) + special_chars, length)
	y = list(map(str,y))
	random.shuffle(y)	
	return "".join(y)

def random_orientation():
	orientation = random.choice(range(0,360))
	return orientation

def random_font(fontList,target_img):	
	font= fontList[random.choice(range(0,len(fontList)))]
	ht,wd =target_img.size
	x = (ht+wd)/2
	min_val = int(max(x/20.0,30))
	max_val = int(min(x/5.0,100))
	font_size = random.choice(range(min_val,max_val))
	return font,font_size
	
def random_color(target_img):
	rgb_im = target_img.convert('RGB')
	r, g, b = rgb_im.getpixel((1, 1))
	dist = 0
	while dist < 150:
		R = random.choice(range(0,255))
		G = random.choice(range(0,255))
		B = random.choice(range(0,255))
		A = random.choice(range(0,255))
		dist = np.sqrt(np.square(R-r) + np.square(G-g) + np.square(B-b))
		#print(dist)
	return (R,G,B,A)



def load_fonts(cfg=cfg):
	fonts = []
	for fname in glob.glob(cfg['font_loc']+"*"):
		font_name = fname.split("/")[-1]
		fonts.append(font_name)

	if cfg['light_fonts'] == True:
		return fonts

	light_fonts = ['Raleway-ThinItalic.ttf','OpenSans-LightItalic.ttf','Lato-HairlineItalic.ttf','Roboto-Thin.ttf',
	'Walkway_Oblique_Bold.ttf','CaviarDreams_Italic.ttf','Raleway-ExtraLight.ttf','Roboto-ThinItalic.ttf'
	'Raleway-ThinItalic.ttf', 'Lato-Thin.ttf', 'Raleway-Thin.ttf', 'Roboto-Thin.ttf', 'Lato-ThinItalic.ttf', 
	'Roboto-ThinItalic.ttf','Lato-Light.ttf', 'RobotoCondensed-Light.ttf', 'Raleway-Light.ttf', 'OpenSans-Light.ttf', 
	'Roboto-Light.ttf', 'Raleway-ExtraLight.ttf', 'Sansation-LightItalic.ttf', 'OpenSans-LightItalic.ttf', 'Raleway-LightItalic.ttf', 'Roboto-LightItalic.ttf', 'RobotoCondensed-LightItalic.ttf', 
	'Raleway-ExtraLightItalic.ttf', 'Lato-LightItalic.ttf', 'Sansation-Light.ttf','Lato-Hairline.ttf','AmaticSC-Regular.ttf']

	fonts = list(set(fonts) - set(light_fonts))
	return fonts


fonts = load_fonts()


def randomize_text_pil(orientation,fname,random_skew=0,options=None,fonts=fonts,cfg=cfg):
	if options is None:
		choice =random.choice(range(0,2))
		if choice==0:
			text = random_number_generation()
		elif choice==1:		
			text = random_alphabet_generator()
		else:
			text = random_alphanumeric_generator()
	else:
		text = options['text']		
	background = Image.open(fname)
	wd,ht = background.size
	print(fname)
	if options is None:
		text_color = random_color(background)
		fill_color=random.randint(1, 80) if len(text_color) == 0 else text_color
		font,font_size = random_font(fonts,background)
	else:
		text_color = options['text_color']
		fill_color = options['fill_color']
		font = options['font']
		font_size = options['font_size']
	img_font = ImageFont.truetype(cfg['font_loc']+font, size=font_size)	
	x1 = y1 =  int(font_size*len(text)/2)
	if x1 > min(ht,wd):
		x1 = int(0.3*min(ht,wd))
	if y1 > min(ht,wd):
		y1 = int(0.3*min(ht,wd))
	img_mask = Image.new('L', (x1,y1))
	draw_img_mask = ImageDraw.Draw(img_mask)
	draw_img_mask.text((0, 0), text,fill=255 ,font=img_font)
	X = np.where(np.array(img_mask)!=0)
	y1 = min(X[0])
	y2 = max(X[0])
	x1 = min(X[1])
	x2 = max(X[1])
	img_mask = np.array(img_mask)[y1:y2,x1:x2]
	img_mask = Image.fromarray(img_mask)
	if random_skew and options is None:
		orientation = random_orientation()	
		rotated_img_mask = img_mask.rotate(orientation,expand=1)
	elif options is not None:
		orientation = options['orientation']
		rotated_img_mask = img_mask.rotate(orientation,expand=1)
	else:
		rotated_img_mask = img_mask.rotate(orientation,expand=1)
	#rotated_img_mask.save("/home/kicompute/Downloads/test.jpeg")
	x_max = rotated_img_mask.size[0]
	y_max = rotated_img_mask.size[1]
	ht = y2-y1
	from math import cos, radians,sin
	if orientation <= 90 and orientation >=0:
		y_delta = int(ht*cos(radians(orientation)))
		x_delta = int(ht*sin(radians(orientation)))
		new_coords = [(0,y_max-y_delta),(x_delta,y_max),(x_max,y_delta),(x_max-x_delta,0)]
	if orientation > 90 and orientation <= 180:
		orientation_ = 180 - orientation 	
		y_delta = int(ht*cos(radians(orientation_)))
		x_delta = int(ht*sin(radians(orientation_)))
		new_coords = [(x_delta,0),(0,y_delta),(x_max-x_delta,y_max),(x_max,y_max-y_delta)]		
	if orientation <= 270 and orientation > 180:
		orientation_ = orientation - 180
		y_delta = int(ht*cos(radians(orientation_)))
		x_delta = int(ht*sin(radians(orientation_)))
		new_coords = [(0,y_max-y_delta),(x_delta,y_max),(x_max,y_delta),(x_max-x_delta,0)]
	if orientation <= 360 and orientation > 270:
		orientation_ = 360 - orientation
		y_delta = int(ht*cos(radians(orientation_)))
		x_delta = int(ht*sin(radians(orientation_)))
		new_coords = [(x_delta,0),(0,y_delta),(x_max-x_delta,y_max),(x_max,y_max-y_delta)]		
	x1,y1 = rotated_img_mask.size
	print("rotated mask size",rotated_img_mask.size)
	print("background size",background.size)
	if options is None:
		x_offset = random.choice(range(0,background.size[0]-max(x1,y1)))
		y_offset = random.choice(range(0,background.size[1]-max(x1,y1)))
	else:
		x_offset = options['x_offset']
		y_offset = options['y_offset']
	options = {'font':font,'font_size':font_size,'text':text,'text_color':text_color,'fill_color':fill_color,'text':text,'orientation':orientation,'x_offset':x_offset,'y_offset':y_offset}
	print(options)
	background.paste(ImageOps.colorize(rotated_img_mask, (0,0,0), fill_color), (x_offset,y_offset),  rotated_img_mask)
	#background.save(target_path+"/" + fname.split("/")[-1].split(".")[0] + "_rotated." + fname.split("/")[-1].split(".")[1])
	background.save(cfg['target_path']+"/" + fname.split("/")[-1])
	print("Saved")
	draw_img_mask = ImageDraw.Draw(background)
	new_coords = [(new_coords[0][0] + x_offset,new_coords[0][1] + y_offset),(new_coords[1][0] + x_offset,new_coords[1][1] + y_offset),(new_coords[2][0] + x_offset,new_coords[2][1] + y_offset),(new_coords[3][0] + x_offset,new_coords[3][1] + y_offset)]
	# Save coords
	#x = draw_img_mask.polygon(new_coords,outline=255)
	#background.save(target_path+"/" + fname.split("/")[-1].split(".")[0] + "_coords." + fname.split("/")[-1].split(".")[1])
	return new_coords,text


# options = None
# randomize_text_pil(1,fname,random_skew=1,options=options)

all_files=[]
for fname in glob.glob(cfg['image_path']+"/*"):
	all_files.append(fname)

n_horizontal = int(len(all_files)*cfg['horizontal']/100.0)
n_vertical = int(len(all_files)*cfg['vertical']/100.0)

all_files_horizontal = all_files[:n_horizontal]
all_files_vertical = all_files[n_horizontal:n_horizontal+n_vertical]
all_files_random = all_files[n_horizontal+n_vertical:]

all_coords = []
all_files = []
all_text = []

for fname in glob.glob(cfg['image_path']+"/*"):
	try:
		if fname in all_files_horizontal:
			coords,text = randomize_text_pil(0,fname,0)
		if fname in all_files_vertical:
			coords,text = randomize_text_pil(90,fname,0)		
		if fname in all_files_random:
			coords,text = randomize_text_pil(0,fname,1)
		all_files.append(fname.split("/")[-1])
		all_coords.append(coords)
		all_text.append(text)
	except Exception as e:
		print(e)
		continue

all_files = np.array(all_files)
all_coords = np.array(all_coords)
all_text = np.array(all_text)




# Annotation files for east
for i,each in enumerate(all_files):
	label_fname = each.split("/")[-1].split(".")[0] + ".txt"
	f = open(os.path.join(cfg['target_path'],label_fname),"w")
	x = []
	for y in all_coords[i]:
		x.append(str(y[0]))
		x.append(str(y[1]))
	x.append(all_text[i])
	print(x)
	x = ",".join(x)
	print(x)
	f.write(x)
	f.close()


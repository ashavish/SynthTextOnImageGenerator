# Visualize annotations

import cv2
import yaml
import glob
from PIL import Image, ImageDraw,ImageFont,ImageOps
import argparse


with open("config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile,Loader=yaml.FullLoader)

parser = argparse.ArgumentParser()
parser.add_argument('-image', action="store",dest='image_val',default=False)
args = parser.parse_args()


def visualize_annot(fname):	
	background = Image.open(fname)
	annot_fname = ".".join(fname.split(".")[:-1]) + ".txt"
	annot = open(annot_fname,"r")
	coords = annot.readlines()[0]
	x1,y1,x2,y2,x3,y3,x4,y4,text = list(map(int,coords.split(",")))
	new_coords = [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]
	draw_img_mask = ImageDraw.Draw(background)
	draw_img_mask.polygon(new_coords,outline="red")
	background.show()



visualize_annot(cfg['target_path']+"/" +args.image_val)
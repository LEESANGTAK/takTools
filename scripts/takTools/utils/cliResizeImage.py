"""
Author: Sang-tak Lee
Contact: chst27@gmail.com
Created: 02/03/2016
Updated: 09/26/2017

Description:
You can resize images in directory
"""

import os
import re
import argparse
import logging
from PIL import Image

logging.basicConfig()
logger = logging.getLogger('resizeImage')
logger.setLevel(logging.DEBUG)


def main():
	""" Add arguments and parsing """
	parser = argparse.ArgumentParser(description='Resize images in given folder', usage='tak_resizeImg.py "Directory Path" 0.25')

	parser.add_argument('directory', help='Directory path that have images')
	parser.add_argument('scale', help='0.1 ~ 1.0')

	parser.add_argument('-s', '--search', default='', help='Search string for replace')
	parser.add_argument('-r', '--replace', default='', help='Replace string with search string')
	parser.add_argument('-f', '--suffix', default='', help='Suffix string')

	args = parser.parse_args()

	resizeImage(directory=args.directory, scale=args.scale, search=args.search, replace=args.replace, suffix=args.suffix)


IMAGE_EXTENSIONS = ['.jpg', '.JPG', '.png', '.PNG', '.tif', '.TIF', '.tga', '.TGA', '.exr', '.EXR', '.bmp', '.BMP']


def resizeImage(directory, scale, search, replace, suffix):
	"""
	Resizing images
	Args:
		directory : Directory path that have images
		scale : This value multiplied to original image size. 0.5 will create half size image
		search : Search string for replace
		replace : Replace string with search string
		suffix : Suffix string

	Returns:
		None
	"""
	if not os.path.exists(directory):
		logger.error('There is no such directory')

	imageFiles = [f for f in os.listdir(directory) if os.path.splitext(f)[-1] in IMAGE_EXTENSIONS]
	if not imageFiles:
		logger.warning('There is no image in directory')
		return

	for f in imageFiles:
		baseName, ext = os.path.splitext(f)
		newName = re.sub(search, replace, baseName) + suffix
		newFullPath = '%s%s' % (os.path.join(directory, newName), ext)

		img = Image.open(os.path.join(directory, f))
		size = int(round(img.size[0] * float(scale))), int(round(img.size[1] * float(scale)))
		img = img.resize(size, Image.ANTIALIAS)

		img.save(newFullPath)


if __name__ == '__main__':
	main()

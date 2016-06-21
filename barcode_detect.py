import os, sys
import Image
import ImageDraw
import itertools
from itertools import groupby
from operator import itemgetter


def average_continuous_coordinate(broken_pos_y):
	"""Find the continuous y coordinate and calculate the average of them"""
   	
	mean = [] 
	for k, g in groupby(enumerate(broken_pos_y), lambda (i,x): i-x):
		lists = map(itemgetter(1), g)
		mean.append(sum(lists)/len(lists))

	return mean

#NOTE: must operate on rgb image, because red color cannot displayed on gray image 
def draw_red_rect(image, point, size=10):
	"""Drawing rectangle around bugy regions"""

	if (point[0] - size >= 0 and point[1] - size >= 0 and point[0]+size < image.size[0] and point[1]+size < image.size[1]):
		region = (point[0] - size, point[1] - size, point[0]+size,  point[1]+size)
		draw = ImageDraw.Draw(image)
		draw.rectangle(region, outline='red')


def binarify_gray_image(im_g, threshold=128, reverse=False):
	if reverse:
		return im_g.point(lambda i : i < threshold and 255)
	else:
		return im_g.point(lambda i : i > threshold and 255)


def scale_image(im_g, large_size=256):
	"""Scale image to certain size(defaultly, scale long side to 256)"""
	
	factor = max(im_g.size) / large_size 
	return im_g.resize(tuple([x / factor for x in im_g.size]))


def sum_pixel(im_g, dim=0, pos=0, inner_padding=0):
	"""Sum up the pixel value of a row or a col"""	

	pix = im_g.load()
	x_size, y_size = im_g.size
	sum = 0
	if dim == 0:		
		for y in range(y_size - inner_padding):
			sum = sum + pix[pos, y]		
		return sum

	elif dim == 1:
		for x in range(x_size - inner_padding):
			sum = sum + pix[x, pos]
		return sum
	else:
		print('ERROR: dim must be 0(indicates x) or 1(indicates y)')
		return 

def scan_line(im_g, x):
	"""Scan the pixel value of certain x and find the y coordinate of broken points"""

	pix = im_g.load()
	broken_points = []
	for i in range(im_g.size[1]):
		if pix[x, i] < 128:
			broken_points.append(i)	
	
	return broken_points	

def find_begin_end_x(im_g, threshold=10000, num=30):
	"""Find the begin postion and end position of barcode on x coordinate"""
	
	begin_pos = 0
	end_pos = 0
	for i in range(im_g.size[0]):
		if sum_pixel(im_g, 0, i) > threshold:
			begin_pos = i
			break
	
	for i in range(begin_pos, im_g.size[0] - 20):
		if sum_pixel(im_g, 0, i) < threshold:
			is_continous = True
			for j in range(num):
				is_continous = True if sum_pixel(im_g, 0, i + j) < threshold else False
				if is_continous==False:
					break
			if is_continous:
				end_pos = i
				break
	
	return begin_pos, end_pos


def find_begin_end_y(im_g, begin_threshold=100000, end_threshold=50000):
	"""Find the begin postion and end position of barcode on y coordinate"""
	
	#get the position of first barcode
	begin_pos1 = 0
	end_pos1 = 0
	for i in range(im_g.size[1]):
		if sum_pixel(im_g, 1, i) > begin_threshold:
			begin_pos1 = i
			break
	for i in range(begin_pos1, im_g.size[1]):
		if sum_pixel(im_g, 1, i) < end_threshold:
			end_pos1 = i
			break	

	#get the position of the second barcode
	begin_pos2 = 0 
	end_pos2 = 0
	for i in range(end_pos1, im_g.size[1]):
		if sum_pixel(im_g, 1, i) > begin_threshold:
			begin_pos2 = i
			break
	for i in range(begin_pos2, im_g.size[1]):
		if sum_pixel(im_g, 1, i) < end_threshold:
			end_pos2 = i
			break	
	
	return begin_pos1, end_pos1, begin_pos2, end_pos2	
	
def crop_barcode(im_g, padding=8):
	"""Crop the two barcode region from the original image"""

	begin_x, end_x = find_begin_end_x(im_g)
	begin_y_1, end_y_1, begin_y_2, end_y_2 = find_begin_end_y(im_g)
	barcode1 = im_g.crop((begin_x - padding, begin_y_1 - padding, end_x + padding, end_y_1 + padding)) 
	barcode2 = im_g.crop((begin_x - padding, begin_y_2 - padding, end_x + padding, end_y_2 + padding)) 

	return barcode1, barcode2, (begin_x - padding, begin_y_1 - padding), (begin_x - padding, begin_y_2 - padding)

def calc_vertical_average_pixel(im_g, inner_padding=5):
	"""Calculate the average pixel value of each line"""

	coordinate_pixel = [] 
	for i in range(im_g.size[0]):
		sum = sum_pixel(im_g, 0, i, inner_padding)
		sum = sum / im_g.size[1]
		coordinate_pixel.append((i, sum))	
	
	return coordinate_pixel
	
def split_barcode(im_g):
	"""Split the whole barcode into a pieces of single lines"""

	lines = []
	coordinate_pixel = calc_vertical_average_pixel(im_g)

	#group the tuples by zero separated group
	lines = [list(pixel) for pos, pixel in groupby(coordinate_pixel, lambda (pos,pixel): pixel==0)]
	
	#delete the zero value of group
	lines = filter(lambda x: x[0][1] != 0, lines)
	
	#delete the first two and last two elements in each line group
	lines = [line[2:-2] for line in lines]

	#delete empty elements
	lines = [l for l in lines if l]	

	return lines

def get_broken_points(im_g, pixel_threshold=240):
	"""Get the coordinate of the broken position of each line"""
	
	lines = split_barcode(im_g)
	center_x= []
	broken_points = []
	for line_list in lines:
		broken_x= filter(lambda ll: ll[1] < pixel_threshold, line_list)
		broken_pos = [bp[0] for bp in broken_x]
		if broken_pos != []:
			center_x.append(sum(broken_pos)/len(broken_pos))	
	
	broken_pos_y = [scan_line(im_g, x) for x in center_x]
	for i in range(len(broken_pos_y)):
		center_y = average_continuous_coordinate(broken_pos_y[i])		

		#remove number that too small or too large
		center_y = filter(lambda y: y > 10, center_y)
		center_y = filter(lambda y: y < im_g.size[1]- 10, center_y)
		
		#remove lines that have more than 3 broken points(it's obviously a error.)
		if len(center_y) >= 4:
			continue	
		broken_x_y = [(center_x[i], y) for y in center_y]
		broken_points.append(broken_x_y)	
		
	#flatten the list of list to list
	broken_points = list(itertools.chain(*broken_points))	
	return broken_points
				

def main():
	if len(sys.argv) < 2:
		print('USAGE: barcode_detect.py <path to barcode image>')
		return 

	im_path = sys.argv[1]  
	try:
		im = Image.open(im_path)
	except IOError:
		print('File open error!')
		return 
	
	#convert RGB image to gray scale
	im_g = im.convert('L')

	#binarify the gray image
	im_g = binarify_gray_image(im_g, reverse=True)

	#get the barcode regions and the begin points of region,since we 
	#have to draw rectange on original image, we need the points to 
	#calculate the absolute positions of broken points
	b1,b2,begin_point1,begin_point2 = crop_barcode(im_g, padding=0)
	

	#process the first barcode
	broken_points1 = get_broken_points(b1, pixel_threshold=240)
	
	#change from coordinate of barcode to original image
	broken_points1 = [(x[0]+begin_point1[0], x[1]+ begin_point1[1]) for x in broken_points1]

	for bp in broken_points1:
		draw_red_rect(im, bp)
	
	#process the first barcode
	broken_points2 = get_broken_points(b2, pixel_threshold=240)
	broken_points2 = [(x[0]+begin_point2[0], x[1]+ begin_point2[1]) for x in broken_points2]

	for bp in broken_points2:
		draw_red_rect(im, bp)

	
	#show the marked image
	im.show()	
	

if __name__ == '__main__':
	main()
	

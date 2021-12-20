import json
import codecs
import boto3
import csv
import numpy
import matplotlib
from matplotlib import pyplot, image
import copy
import itertools
from PIL import Image

COLS = {	"butter": [	'#fce94f',
					'#edd400',
					'#c4a000'],
		"orange": [	'#fcaf3e',
					'#f57900',
					'#ce5c00'],
		"chocolate": [	'#e9b96e',
					'#c17d11',
					'#8f5902'],
		"chameleon": [	'#8ae234',
					'#73d216',
					'#4e9a06'],
		"skyblue": [	'#729fcf',
					'#3465a4',
					'#204a87'],
		"plum": 	[	'#ad7fa8',
					'#75507b',
					'#5c3566'],
		"scarletred":[	'#ef2929',
					'#cc0000',
					'#a40000'],
		"aluminium": [	'#eeeeec',
					'#d3d7cf',
					'#babdb6',
					'#888a85',
					'#555753',
					'#2e3436'],
		}
# FONT
FONT = {	'family': 'Ubuntu',
		'size': 12}
matplotlib.rc('font', **FONT)

def parse_fixations(fixations):
	fix = {
		'x':numpy.zeros(len(fixations)),
		'y':numpy.zeros(len(fixations)),
		'dur':numpy.zeros(len(fixations))
	}
	ex = []
	ey = []
	dur = []
	
	for fixnr in range(len(fixations)):
		ex.append(fixations[fixnr]['x'])
		ey.append(fixations[fixnr]['y'])
		dur.append(fixations[fixnr]['events']['Efix'])
		
	fix['x'] = numpy.array(list(itertools.chain.from_iterable(ex)))
	fix['y'] = numpy.array(list(itertools.chain.from_iterable(ey)))
	fix['dur'] = numpy.array(list(itertools.chain.from_iterable(dur)))
	
	return fix
	
def draw_display(exp_name, dispsize, imagefile=None):
	s3 = boto3.client('s3')
	bucket = 'ed1-eye-tracker'
	path = 'Experiences/'+ exp_name + '/'
	
	data_type = 'float32' # note: image must be png
	# data_type = 'uint8'
	screen = numpy.zeros((dispsize[1],dispsize[0],3), dtype=data_type)
	# screen = numpy.zeros((dispsize[1],dispsize[1],3), dtype=data_type)
	if imagefile != None:
		local = '/tmp/temp.png'
		s3.download_file(bucket,imagefile, local)
		# s3.download_file(bucket,img_key, local)
		img = image.imread(local)
		# img = numpy.flipud(img)
		screen += img
		
	dpi = 100.0
	figsize = (dispsize[0]/dpi, dispsize[1]/dpi)
	# figsize = (dispsize[1]/dpi, dispsize[1]/dpi)
	fig = pyplot.figure(figsize=figsize, dpi=dpi, frameon=False)
	ax = pyplot.Axes(fig, [0,0,1,1])
	ax.set_axis_off()
	fig.add_axes(ax)
	# ax.imshow(screen, extent=(-dispsize[0]/2,dispsize[0]/2,-dispsize[1]/2,dispsize[1]/2))
	# ax.imshow(screen, extent=(-dispsize[1]/2,dispsize[1]/2,-dispsize[1]/2,dispsize[1]/2))	
	
	return fig,ax

def draw_fixations(exp_name, exp_type, fixations, dispsize, imagefile=None, durationsize=True, durationcolour=True, alpha=0.5, savefilename=None):
	s3 = boto3.client('s3')
	bucket = 'ed1-eye-tracker'
	path = 'Experiences/'+ exp_name + '/'	
	fix = parse_fixations(fixations)
	fig, ax = draw_display(exp_name, dispsize, imagefile=imagefile)
	
	dur = fix['dur']
	if durationsize:
		siz = dur
	else:
		siz = numpy.median(dur)
	col = COLS['chameleon'][2]
	x = fix['x']
	y = fix['y']
	
	# rem = (dispsize[0]-dispsize[1])/2
	# x_neg = -(dispsize[0]/2) + rem
	# x_pos = (dispsize[0]/2) - rem
	
	# x_scale = numpy.interp(x, (x.min(),x.max()), (-dispsize[0]/2,dispsize[0]/2))
	# x_scale = numpy.interp(x, (x.min(),x.max()), (x_neg,x_pos))
	# y_scale = numpy.interp(y, (y.min(),y.max()), (-dispsize[1]/2,dispsize[1]/2))	
	
	x_scale = numpy.interp(x, (-0.4,0.4), (-dispsize[0]/2,dispsize[0]/2))
	y_scale = numpy.interp(y, (-0.4,0.4), (-dispsize[1]/2,dispsize[1]/2))
	
	ax.scatter(x_scale,y_scale, s=siz, c=col, marker='o', cmap='jet', alpha=alpha, edgecolors='none')
	ax.invert_yaxis()
	if savefilename != None:
		local = '/tmp/fixmap.png'
		fig.savefig(local)
		img_data = open(local, "rb")
		figure_key = path + 'Fixation Maps/' + exp_type + '_' + exp_name.replace(" ","_") + '_Fixation_Map.png'
		s3.put_object(Bucket=bucket, Key=figure_key, Body=img_data, ContentType="image/png", ACL="public-read")
	return fig
	
def lambda_handler(event, context):
    exp_name = event['exp_name']
    exp_type = event['exp_type']
    s3 = boto3.client('s3')
    bucket = 'ed1-eye-tracker'
    path = 'Experiences/'+ exp_name + '/' 
    
    img_key = path + exp_type + '_' + exp_name.replace(" ","_") + '.png'
    # img_key = path + exp_name.replace(" ","_") + '.png'
    local = '/tmp/temp1.png'
    s3.download_file(bucket,img_key, local)
    img = Image.open(local)
    width, height = img.size
    img.close()
    
    file_key = path + exp_type +'_Fixations_' + exp_name.replace(" ","_") + '.csv'
    csvfile = s3.get_object(Bucket=bucket, Key=file_key)
    reader = csv.DictReader(codecs.getreader("utf-8")(csvfile["Body"]))
    
    data = []
    x = []
    y = []
    trial = {}
    events = {'Efix':[]}

    for item in reader:
        x.append(float(item.get("Fix Avg X")))
        y.append(float(item.get("Fix Avg Y")))
        events['Efix'].append(float(item.get("Duration")))
        
    trial['x'] = numpy.array(x)
    trial['y'] = numpy.array(y)
    trial['events'] = copy.deepcopy(events)
    data.append(trial)
    
    # draw_fixations(exp_name,exp_type,data,[new_width,new_height],img_key,durationsize=True,durationcolour=True,alpha=0.5,savefilename='test.png')
    draw_fixations(exp_name,exp_type,data,[width,height],img_key,durationsize=True,durationcolour=True,alpha=0.5,savefilename='test.png')
    
    # https://ed1-eye-tracker.s3.amazonaws.com/Experiences/Dining+Room/Fixation+Maps/2D_Dining_Room_Fixation_Map.png
    src_2d = "<img src='https://" + bucket + ".s3.amazonaws.com/" + path.replace(" ","+") + "Fixation+Maps/2D_" + exp_name.replace(' ','_') + "_Fixation_Map.png' alt='2D Fixation Map Not Available'>"
    src_ar = "<img src='https://" + bucket + ".s3.amazonaws.com/" + path.replace(" ","+") + "Fixation+Maps/AR_" + exp_name.replace(' ','_') + "_Fixation_Map.png' alt='AR Fixation Map Not Available'>"
    src_rl = "<img src='https://" + bucket + ".s3.amazonaws.com/" + path.replace(" ","+") + "Fixation+Maps/RL_" + exp_name.replace(' ','_') + "_Fixation_Map.png' alt='RL Fixation Map Not Available'>"
    
    return src_2d, src_ar, src_rl

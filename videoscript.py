import subprocess
import shlex
import os.path
import csv

csvfilename = "TPES Virtual Variety Show 2020 - Videos Upload - 2020-04-18.csv"

#
# time savers! to help you quickly text between different settings, you can skip some of 
# the steps of this script. NOTICE: You need run all the steps at least once, and you have to keep
# the files generated at these steps (filename_scaled.mp4, filename_text.mp4) to be able to skip that step
#
skip_scaling         = True
skip_scalingAndText  = True

# set it to 2 if you want to test changes without encoding
# the entire spreadsheet
# set it to 0 if you don't want any limits
limitfiles = 3

# final video resolution
output_width = 1280
output_height = 720
output_filename = "output.mp4"

# text related
fontname = "MyHandwritingSucks.ttf"
fontcolor= "white"
fontbordercolor = "black"
fontborderwidth = "3"
fonthasabox = "1" # use 0 for no box
fontboxcolor = "black@0.5"  # black with 50% transparency
fontboxborderwidth = "8"
fontsize = "64"
text_duration = "5"

# transition
transition_name = "fade"
transition_timems = 750

print("Expecting files to be at: %s" %  os.path.abspath(__file__))


# we use python's string formatting to change the content of these commands.
# for example:
# string = "Hello %s! This is %s"
# the string above has a placeholder for two strings (%s - string; %d - decimal; %f - float; etc...)
# thus, if you want to fill in the placeholders, use the % operator
# print(string % ("world","Danilo")) 
# the command above outputs: "Hello world! This is Danilo"

# commands used to invoke ffmpeg
scale_command = 'ffmpeg -y -i "%s" -vf "scale=%s:%s:force_original_aspect_ratio=decrease,pad=%s:%s:(ow-iw)/2:(oh-ih)/2" -codec:a copy \'%s\'' 
scale_add_text_command = 'ffmpeg -y -i "%s" -vf drawtext="fontfile=\'%s\': text=\'%s\': fontcolor=%s: fontsize=%s: bordercolor=%s: borderw=%s: box=%s: boxcolor=%s: boxborderw=%s: x=(w-text_w)/2: y=h-text_h*1.2: enable=lt(t\,%s)" -codec:a copy "%s"'


#
# Reads csv file and look for files
#

input_list = []
input_text = []

if (limitfiles > 0):
    print("Warning! Only the first %d files of the csv file will be read!" % limitfiles)

with open(csvfilename, "r",encoding='utf-8') as csvfile:
    csvrows = csv.reader(csvfile, delimiter=',', quotechar='"')
    counter = 0
    header = True
    
    for row in csvrows:
        # skips header
        if header:
            header = False
            continue
            
        # appends to the list of filenames and text
        input_list.append(row[5])
        input_text.append("%s - %s" % (row[4], row[3]))
        
        # generates the videos
        counter += 1
        if limitfiles > 0 and counter > limitfiles:
            break


#
# This is where the magic happens
#

counter = 0

#
# Create individual files with the correct resolution and with text
#

final_list = []
for filename,text in zip(input_list, input_text):
    counter += 1
    input_file=filename
    input_file_name = os.path.splitext(input_file)[0]

    # scale video 
    if not skip_scaling and not skip_scalingAndText:
      subprocess.check_call(shlex.split(scale_command % (input_file, output_width, output_height, output_width, output_height, "%s_scaled.mp4" % input_file_name)))

    # add text
    if not skip_scalingAndText:
      subprocess.check_call(shlex.split(scale_add_text_command % ("%s_scaled.mp4" % input_file_name, fontname, ".%s%s%s."%(" "*50,text," "*50), fontcolor, fontsize, fontbordercolor, fontborderwidth, fonthasabox, fontboxcolor, fontboxborderwidth, text_duration, "%s_text.mp4" % input_file_name)))

    final_list.append("%s.mp4" % counter)
    final_list.append("black.mp4")
    
final_list.pop()

# create the ffmpeg command to crossfade videos (as many as there are in the list)
subprocess.check_call(shlex.split("ffmpeg -y %s -filter_complex \"%s concat=n=%d:v=1:a=1 [v] [a]\" -map [v] -map [a] %s" % (" ".join("-i \"%s\""%filename for filename in final_list), " ".join(["[%d:v] [%d:a]"%(i,i) for i in range(len(final_list))]), len(final_list), output_filename)))



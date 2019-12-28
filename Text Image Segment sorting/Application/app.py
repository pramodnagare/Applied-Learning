import os
import time
import shutil
import glob
import json
import csv
import cv2
import pytesseract
import pandas as pd
import concurrent.futures
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

pytesseract.pytesseract.tesseract_cmd = r'../Tesseract-OCR-Installables/tesseract.exe'

class TextImageSorting:

    def __init__(self, conf_file):
        self.load_configuration(conf_file)

    def load_configuration(self, conf_file):
        try:
            conf = open(conf_file).read()
            conf = json.loads(conf)
            if None in list(conf.values()):
                print("Please mention all the field values in the configuration")
            else:
                self.input_dir = conf['input_dir']
                self.output_dir = conf['output_dir']
                self.class_file = json.loads(open(conf['class_file']).read())
                self.image_file_type = conf['image_file_type']
                self.segment_text_file_name = conf['segment_text_file_name']
                self.back_list_characters = conf['back_list_characters']

                print("Configuration file loaded successfully!")
        except:
            print("Error while loading configuration file")

    def formatText(self, text):
        text = str(text).replace("\n", "")
        return text

    def getText(self, image_path):
        try:
            image = cv2.imread(image_path)
            text = str(pytesseract.image_to_string(image, config='--psm 6'))
            text = self.formatText(text)
            return text
        except:
            print("Error while get Text for {}".format(image_path))
            return None

    def extract_text_images(self):

        try:
            start = time.time()
            images = glob.glob(os.path.join(self.input_dir, "*" + self.image_file_type))
            print("Number of images to process: ", len(images))
            NUM_WORKERS = int(os.environ['NUMBER_OF_PROCESSORS'])
            print("There are {} number of processors".format(NUM_WORKERS))

            result = {}
            i = 0
            with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
                for image,text in zip(images,executor.map(self.getText,images)):
                    path, image = os.path.split(image)
                    result[str(i)] = {}
                    result[str(i)]['path'] = path
                    result[str(i)]['image'] = image
                    result[str(i)]['text'] = text
                    i += 1
            
            with open(os.path.join(self.output_dir, self.segment_text_file_name), mode='w', encoding='utf-8') as TextExt:
                json.dump(result, TextExt, indent=2)

            end = time.time()
            print("Time for extracting {} images is {}".format(len(images), end-start))

        except:
            print("Error while extracting an image in parallel")

    def extract_text_images_seq(self):

        try:
            start = time.time()
            images = glob.glob(os.path.join(self.input_dir, "*" + self.image_file_type))
            result = {}
            i = 0
            for image in images:
                text = self.getText(image)
                path, image = os.path.split(image)
                result[str(i)] = {}
                result[str(i)]['path'] = path
                result[str(i)]['image'] = image
                result[str(i)]['text'] = text
                i += 1
            with open(os.path.join(self.output_dir, self.segment_text_file_name), mode='w', encoding='utf-8') as TextExt:
                json.dump(result, TextExt, indent=2)

            end = time.time()
            print("Time for extracting {} images is {}".format(len(images), end-start))
        except:
            print("Errored while extracting an image in sequence")

    def setupOutputDir(self):
        for key in self.class_file.keys():
            os.makedirs(os.path.join(self.output_dir, str('%03d' %int(key))), exist_ok=True)
    
    def blackListText(self, text):
        text = text.translate(str.maketrans('', '', "".join(self.back_list_characters)))
        return text.lower()
    
    def sortImages(self):
        try:
            start = time.time()
            segment_text = open(os.path.join(self.output_dir, self.segment_text_file_name)).read()
            segment_text = json.loads(segment_text)
            
            temp_class_file = {}
            for key in self.class_file.keys():
                temp_class_file[key] = str(self.blackListText(self.class_file[key]['Keyword']))

            images_processed = 0
            for item in segment_text.keys():
                text = self.blackListText(segment_text[item]['text'])
                key = process.extractBests(text, temp_class_file, scorer=fuzz.token_sort_ratio, limit=1)
                if key:
                    keyword, score, index = key[0]
                    if score > 85:
                        source = os.path.join(segment_text[item]['path'], segment_text[item]['image'])
                        destination = os.path.join(self.output_dir, str('%03d' %int(index)))
                        shutil.copy(source, destination)
                        images_processed += 1
            end = time.time()
            print("Time for sorting {} images is {}".format(images_processed, end-start))
        except:
            print("Error while sorting images")
from skimage import measure, exposure
from skimage.measure import regionprops
from skimage.io import imread
from skimage.filters import roberts, threshold_otsu
from scipy import ndimage
import random
import datetime
import imutils
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2
from exceptions import *

class CarInput:
    # how many frames to skip
    FRM = 3
    # total images to take from video
    TOT_IMG = 20
    
    def __init__(self, uri, is_url=False, is_image=False, display=True):
        self.uri = uri
        self.is_url = is_url
        if not is_image:
            self.image = self.load_image_from_video()
        else:
            self.image = self.load_image() 
        self.image_for_plate_detection = self.image

    def set_image_for_plate_detection(self, image):
        # convert image to binary before storing
        image = image > threshold_otsu(image)
        self.image_for_plate_detection = image

    def get_image_for_plate_detection(self):
        return self.image_for_plate_detection

    def get_image(self):
        return self.image

    def show_image(self):
        plt.figure(figsize=(12,8))
        ax = plt.subplot()
        ax.imshow(self.get_image(), cmap="gray")

    def load_image(self):
        if self.is_url:
            raise NotImplementedError('URL not supported yet')

        return imread(self.uri, as_gray=True)

    def load_image_from_video(self):
        if self.is_url:
            raise NotImplementedError('URL not supported yet')
        
        random.seed(datetime.datetime.now())

        cap = cv2.VideoCapture(self.uri)
        images = []

        # display video and choose one image
        while cap.isOpened() and len(images) < TOT_IMG:
            count = 0
            ret, frame = cap.read()
            if ret == True:
                frame = imutils.rotate(frame, 270)
                if self.display:
                    cv2.imshow('camera-feed', cv2.resize(frame, (960, 540)))

                if count % FRM == 0:
                    images.append(frame)

                count += 1

                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            else:
                # cv2.imwrite(filename[:filename.rfind('.')] + '.jpg', chosen_image)
                cap.release()

        if images:
            return cv2.cvtColor(random.choice(images), cv2.COLOR_BGR2GRAY)
        else:
            raise InvalidSourceError()


    

class DetectPlate:
    SMALL = 2500 / (720*1280)
    BIG = 100000 / (720*1280)
    
    def __init__(self, car_input: CarInput, display=True):
        self.CarInput = car_input
        self.image = car_input.get_image()
        self.display = display

    def set_display(self, display):
        self.display = display

    def areas_of_interest(self):
        aoi = []

        image = self.image

        # contrast stretching
        p2, p98 = np.percentile(image, (2, 98))
        image = exposure.rescale_intensity(image, in_range=(p2, p98))

        self.CarInput.set_image_for_plate_detection(image)

        # sharpen image

        # blurred_img = ndimage.gaussian_filter(image, 3)
        # filter_blurred_img = ndimage.gaussian_filter(blurred_img, 1)
        # alpha = 40
        # image = blurred_img + alpha * (blurred_img - filter_blurred_img)
        
        # detect edges and invert just to get outlines
        fil_img = roberts(image)
        bin_img = fil_img > threshold_otsu(fil_img)
        bin_img = np.invert(bin_img)

        processed_image = bin_img
        
        label_image = measure.label(processed_image)
        
        plt.figure(figsize=(12,8))
        
        if self.display:
            fig, ax = plt.subplots(1)
            ax.imshow(processed_image, cmap='gray')
        

        fig, ax1 = plt.subplots(1)
        ax1.imshow(self.image, cmap='gray')
        
        
        for region in regionprops(label_image):
            
            rel_sz = region.area/processed_image.size

            # process only if it lies in a range
            if not(rel_sz < DetectPlate.SMALL or rel_sz > DetectPlate.BIG):
                aoi.append(region)
                
                if self.display:
                    min_row, min_col, max_row, max_col = region.bbox
                    rectBorder = patches.Rectangle(
                            (min_col, min_row), max_col - min_col, max_row - min_row, edgecolor="red", linewidth=2, fill=False)
                    ax1.add_patch(rectBorder)

        self.aoi = aoi
        self.processed_image = processed_image

        return bool(self.aoi)
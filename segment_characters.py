import numpy as np
from skimage import measure
from skimage.transform import resize
from skimage.measure import regionprops
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from shared import *
from exceptions import *


class Plate_Character:
    def __init__(self, image, roi):
        self.roi = roi
        self.image = image
        self.top_left_pixel = (roi.bbox[1], roi.bbox[0])

    def get_processed_image(self):
        '''Returns image to be used as input for ML model'''
        # return resize(self.image, (20, 20), mode='constant', cval=0.)
        return np.invert(self.image) * 255


class SegmentCharacters:
    def __init__(self, full_image, display=True):
        '''Takes a uncropped binary image as argument from which we crop out aoi as required'''
        self.image = self.process_image(full_image)
        self.display = display

    def process_image(self, full_image):
        return np.invert(full_image)

    def increase_smaller_widths(chars: list, avg_width: int):
        '''Increases widths of those characters which are smaller than avg_width'''
        for char in chars:
            y0, x0, y1, x1 = char.roi.bbox
            region_height = y1 - y0
            region_width = x1 - x0

            if region_width < avg_width:
                # make image of avg_width
                new_img = np.zeros((region_height, avg_width), dtype='int')
                offset = (avg_width-region_width+1) // 2
                # set old image in centre of new image
                new_img[:, offset:offset+region_width] = char.image
                #binarise image
                new_img = new_img == 1
                # replace old image
                char.image = new_img

    def get_cc_from_aoi(self, aoi):
        '''
            Finds connected components with the area of interest
        '''
        min_row, min_col, max_row, max_col = aoi.bbox

        cropped_image = self.image[min_row:max_row, min_col:max_col]

        labelled_plate = measure.label(cropped_image)

        if self.display:
            fig, ax1 = plt.subplots(1)
            ax1.imshow(cropped_image, cmap="gray")

        # a character should be between 5% and 15% of the license plate,
        # and height should be between 35% and 60%
        character_dimensions = (
            0.35*cropped_image.shape[0],
            0.70*cropped_image.shape[0],
            0.03*cropped_image.shape[1],
            0.15*cropped_image.shape[1]
        )

        min_height, max_height, min_width, max_width = character_dimensions

        characters = []
        widths = []
        counter = 0

        for region in regionprops(labelled_plate):
            # regionprops returns connected components
            y0, x0, y1, x1 = region.bbox
            region_height = y1 - y0
            region_width = x1 - x0

            if (region_height > min_height and region_height < max_height and
                    region_width > min_width and region_width < max_width):
                
                char_image = cropped_image[y0:y1, x0:x1]

                if self.display:
                    # draw a red bordered rectangle over the character.
                    rect_border = patches.Rectangle((x0, y0), x1 - x0, y1 - y0, edgecolor="red",
                                                    linewidth=2, fill=False)
                    ax1.add_patch(rect_border)

                # create object of Plate_Character and save in array
                characters.append(Plate_Character(char_image, region))

                # make widths the same
                widths.append(region_width)

        # print(characters)
        if characters:
            avg_width = sum(widths)//len(widths)

            SegmentCharacters.increase_smaller_widths(characters, avg_width)

        if self.display:
            plt.show(block=False)
            plt.pause(DL)
            plt.close()

        return characters

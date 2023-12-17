import cv2
import numpy as np

# def remove_text_inpainting(input_image_path, output_image_path):
#     # Read the image
#     image = cv2.imread(input_image_path)

#     # Define the region to be inpainted (adjust as needed)
#     mask_position = (0, image.shape[0] - 20, image.shape[1], image.shape[0])

#     # Create a mask
#     mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
#     mask[mask_position[1]:mask_position[3], mask_position[0]:mask_position[2]] = 255

#     # Perform inpainting
#     result = cv2.inpaint(image, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)

#     # Save the result
#     cv2.imwrite(output_image_path, result)

# def remove_text_inpainting(input_image_path, output_image_path):
#     # Read the image
#     image = cv2.imread(input_image_path)

#     # Define the region to be inpainted (adjust as needed)
#     mask_position = (0, image.shape[0] - 20, image.shape[1], image.shape[0])

#     # Create a mask
#     mask = cv2.cvtColor(np.zeros(image.shape[:2], dtype=np.uint8), cv2.COLOR_GRAY2BGR)
#     mask[mask_position[1]:mask_position[3], mask_position[0]:mask_position[2]] = [255, 255, 255]

#     # Perform inpainting
#     result = cv2.inpaint(image, mask[:, :, 0], inpaintRadius=5, flags=cv2.INPAINT_TELEA)

#     # Save the result
#     cv2.imwrite(output_image_path, result)


def opencv_infill_white_pixels_bottom_row(image, rows=20):
    # Read the image
    mask = image.copy()
    # Clear unimportant bits
    mask[:-rows, :, :] = 0  # Set to black (0, 0, 0)
    # Define the white color range in RGB
    lower_white = np.array([230, 230, 230], dtype=np.uint8)
    upper_white = np.array([255, 255, 255], dtype=np.uint8)
    # Create a mask for white pixels
    white_mask = cv2.inRange(mask, lower_white, upper_white)
    # Extract white pixels using the mask
    white_pixels = cv2.bitwise_and(image, image, mask=white_mask)
    inpaintmask = cv2.cvtColor(white_pixels, cv2.COLOR_BGR2GRAY)
    return cv2.inpaint(image, inpaintmask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)

def opencv_remove_timestamp(input_image_path, output_image_path):
    input = cv2.imread(input_image_path)
    output = opencv_infill_white_pixels_bottom_row(input)
    cv2.imwrite(output_image_path, output)


# import required module
import os
# assign directory
directory = 'data'
 
# iterate over files in
# that directory
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        print(f)
        opencv_remove_timestamp(f,f)


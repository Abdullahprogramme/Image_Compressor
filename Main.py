import numpy as np 
from PIL import Image, ImageDraw
import io

def Weighted_Average(histogram):
    total = sum(histogram)
    error = value = 0

    if total > 0:
        value = sum(i * x for i, x in enumerate(histogram)) / total
        error = sum(x * (value - i) ** 2 for i, x in enumerate(histogram)) / total
        error = error ** 0.5

    return error

def Get_Detail(histogram):
    '''
    Description: 
        This function calculates the detail intensity of the image by taking the weighted average of the histogram of the image.
    
    Args:
        histogram: list of pixel values.
    
    Returns:
        detail_intensity: float value of the detail intensity.
    '''
    red_detail = Weighted_Average(histogram[:256]) # taking values from 0 to 255 for red colour channel
    green_detail = Weighted_Average(histogram[256:512]) # taking values from 256 to 511 for green colour channel
    blue_detail = Weighted_Average(histogram[512:768]) # taking values from 512 to 767 for blue colour channel

    detail_intensity = red_detail * 0.2989 + green_detail * 0.5870 + blue_detail * 0.1140  # weighted average of the three colour channels for eye sensitivity

    return detail_intensity

def Average_Colour(image):
    """
    Description:
        Calculates the average color of an image represented in PIL format.

    Args:
        We are giving an image.

    Returns:
        A tuple of three integers representing the average red, green, and blue values for the entire image.
    """


    image_arr = np.asarray(image) # convert image to np array
    # get average of whole image
    avg_color_per_row = np.average(image_arr, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0) 

    return (int(avg_color[0]), int(avg_color[1]), int(avg_color[2]))

def Quadrant(image, bbox, depth):
    quadrant = {} # dictionary to store the details of the quadrant
    quadrant['bbox'] = bbox # bounding box of the quadrant
    quadrant['depth'] = depth # depth of the quadrant in the tree
    quadrant['children'] = None # children of the quadrant
    quadrant['leaf'] = False # flag to check if the quadrant is a leaf node

    # crop image to quadrant size
    image = image.crop(bbox) # cropping the image to the size of the quadrant using the bounding box
    hist = image.histogram() # getting the histogram of the image which contains the pixel values 

    quadrant['detail'] = Get_Detail(hist) # calculating the detail intensity of the quadrant
    quadrant['colour'] = Average_Colour(image) # calculating the average colour of the quadrant
    return quadrant

def Split_Quadrant(quadrant, image):
    '''
    description:
        This function splits the input quadrant into 4 new quadrants.
    Args:
        quadrant: dictionary to store the details of the quadrant
        image: input image
    '''
    left, top, right, bottom = quadrant['bbox'] # getting the bounding box of the quadrant
    middle_x = left + (right - left) / 2 # getting the middle x coordinate of the quadrant
    middle_y = top + (bottom - top) / 2 # getting the middle y coordinate of the quadrant

    # split root quadrant into 4 new quadrants
    upper_left = Quadrant(image, (left, top, middle_x, middle_y), quadrant['depth']+1) # creating the upper left quadrant
    upper_right = Quadrant(image, (middle_x, top, right, middle_y), quadrant['depth']+1) # creating the upper right quadrant
    lower_left = Quadrant(image, (left, middle_y, middle_x, bottom), quadrant['depth']+1) # creating the lower left quadrant
    lower_right = Quadrant(image, (middle_x, middle_y, right, bottom), quadrant['depth']+1) # creating the lower right quadrant

    quadrant['children'] = [upper_left, upper_right, lower_left, lower_right] # storing the children of the quadrant in the quadrant dictionary

def Start_QuadTree(image, MAX_DEPTH, DETAIL_THRESHOLD):
    '''
    description:
        This function starts the compression of the image by creating a quad tree of the image.
    Args:
        image: input image
    '''
    root = Quadrant(image, image.getbbox(), 0) # creating the root quadrant of the image
    max_depth = Build(root, image, 0, MAX_DEPTH, DETAIL_THRESHOLD) # building the quad tree of the image
    return root, max_depth

def Build(root, image, max_depth, MAX_DEPTH, DETAIL_THRESHOLD):
    '''
    description:
        This function builds the quad tree of the input image.
    Args:
        quad_tree: dictionary to store the details of the quad tree
        root: dictionary to store the details of the root quadrant
        image: input image
    '''
    if root['depth'] > MAX_DEPTH or root['detail'] < DETAIL_THRESHOLD: # checking if the depth of the quadrant is greater than the maximum depth or the detail intensity of the quadrant is less than the detail threshold
        if root['depth'] > max_depth: 
            max_depth = root['depth']

        root['leaf'] = True # assigning the quadrant to a leaf node and stopping the recursion
        return max_depth
    
    Split_Quadrant(root, image) # splitting the quadrant into 4 new quadrants

    for child in root['children']: # iterating through the children of the quadrant
        max_depth = Build(child, image, max_depth, MAX_DEPTH, DETAIL_THRESHOLD) # building the quad tree of the child
    return max_depth

def Create_Image(root, max_depth, user_depth, show_lines=False):
    """
    Description:
        Create an image representation of the quadtree with a specified depth.

    Args:
        root: Dictionary representing the root quadrant.
        max_depth: Maximum depth of the quadtree.
        depth: Depth of the image to be created.
        show_lines: Flag to indicate whether to draw lines around quadrants.

    Returns:
        An Image object representing the quadtree visualization.
    """
    # Get the width and height of the image
    width, height = root['bbox'][2], root['bbox'][3]

    # Create a blank image canvas
    image = Image.new('RGB', (int(width), int(height)))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), (0, 0, 0))

    # Get leaf quadrants for the specified depth
    leaf_quadrants = Get_Leaf_Quadrants(root, max_depth, user_depth)

    # Draw rectangle size of quadrant for each leaf quadrant
    for quadrant in leaf_quadrants:
        bbox = quadrant['bbox']
        color = quadrant['colour']
        if show_lines:
            draw.rectangle(bbox, color, outline=(0, 0, 0))
        else:
            draw.rectangle(bbox, color)

    return image

def Get_Leaf_Quadrants(root, max_depth, user_depth):
    '''
    description:
        This function gets the leaf quadrants of the quad tree.
    Args:
        root: dictionary to store the details of the root quadrant
        max_depth: maximum depth of the quad tree
        depth: depth of the quad tree
    Returns:
        quadrants: list of leaf quadrants
    '''

    if user_depth > max_depth:
        raise ValueError('A depth larger than the trees depth was given')

    quandrants = []
    Recursive_Search(root, user_depth, quandrants.append)
    return quandrants

def Recursive_Search(quadrant, max_depth, append_leaf):
    '''
    description:
        This function recursively searches the quad tree.
    Args:
        quadrant: dictionary to store the details of the quadrant
        max_depth: maximum depth of the quad tree
        append_leaf: flag to append the leaf quadrant
    '''

    if quadrant['leaf'] == True or quadrant['depth'] == max_depth:
        append_leaf(quadrant)
    elif quadrant['children'] != None:
        for child in quadrant['children']:
            Recursive_Search(child, max_depth, append_leaf)

def Create_Gif(root, max_depth, gif_depth, duration=1000, loop=0, show_lines=False):
    '''
    description:
        This function creates a gif of the quad tree.
    Args:
        root: dictionary to store the details of the root quadrant
        max_depth: maximum depth of the quad tree
        file_name: name of the gif file
        duration: duration of the gif
        loop: flag to loop the gif
        show_lines: flag to show the lines in the gif
    '''

    gif = []
    end_product_image = Create_Image(root, max_depth, gif_depth, show_lines=show_lines)

    for i in range(gif_depth):
        image = Create_Image(root, max_depth, i, show_lines=show_lines)
        gif.append(image)
    for _ in range(4):
        gif.append(end_product_image)

    gif_bytes = io.BytesIO()
    gif[0].save(
        gif_bytes,
        format='GIF',
        save_all=True,
        append_images=gif[1:],
        duration=duration, loop=loop)
    gif_bytes.seek(0)

    return gif_bytes

def main(image_path, option, need_gif=False):
    SIZE_MULTIPLIER = 1
    if option == 'slightly less better':
        DETAIL_THRESHOLD = 10
        MAX_DEPTH = user_depth = 6
    elif option == 'slightly better':
        DETAIL_THRESHOLD = 3
        MAX_DEPTH = user_depth = 9
        

    # image_path = 'BMI.jpg'
    image = Image.open(image_path) # opening the image
    image = image.resize((image.size[0] * SIZE_MULTIPLIER, image.size[1] * SIZE_MULTIPLIER)) # resizing the image

    root, max_depth = Start_QuadTree(image, MAX_DEPTH, DETAIL_THRESHOLD) # starting the quad tree of the image
    user_depth = 7
    image = Create_Image(root, max_depth, user_depth, show_lines=False)
    
    if need_gif == True:
        gif = Create_Gif(root, max_depth, user_depth, duration=1000, loop=0, show_lines=True)
        return image, gif
    return image

# High quality image:
# user_depth = 8, MAX_DEPTH = 8, DETAIL_THRESHOLD = 5, SIZE_MULTIPLIER = 1

# Low quality image:
# user_depth = 6, MAX_DEPTH = 8, DETAIL_THRESHOLD = 10, SIZE_MULTIPLIER = 1

# Medium quality image:
# user_depth = 7, MAX_DEPTH = 8, DETAIL_THRESHOLD = 8, SIZE_MULTIPLIER = 1

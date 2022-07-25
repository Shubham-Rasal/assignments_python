#Import required library
from PIL import Image,ImageFilter

#Open Image
fileName="sugarcane.jpg"
im = Image.open(fileName).show()

#Image rotate & show
# im.rotate(45).show()

grayImage=im.convert('L')

# # grayImage.show()

edges_image = im.filter(ImageFilter.FIND_EDGES).show()
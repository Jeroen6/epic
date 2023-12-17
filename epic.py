import pygame
import glob
import os.path
from datetime import datetime, timedelta
import io
from urllib.request import urlopen
from aia import AIA

# Settings!
# AIA Channel The SDO channel identifier. 
# Possible values are '0094', '0131', '0171', '0193', '0211', '0304', '0335', '1600', '1700', 'HMIB', 'HMII', 'HMID', 'HMIBC', 'HMIIF', 'HMIIC'.
aia_channel = '0193'

# AIA Resolution
# The resolution of the image. Possible values are '4096', '2048', '1024', '512'.
aia_resolution = '512'

# This is how many images to keep cached
imageCount = 200

# This sets an age threshold for deletetion (curernt not used)
ageThreshold = timedelta(hours=48)

# This is the delay between api calls
check_delay = timedelta(minutes=9)

# This is the delay rotating the slowhow
rotateTime = timedelta(seconds=0.6)

# This is how fast the loop runs 
# and thus how much cpu is used
# fadeTime in seconds
frameRate = 15
fadeTime = 0.5
fadingSetting = True

# Crop the image?
# There some space around the earth, crop this? (pun intended)
# Apparently the sattelite moves a bit 
# It calculates the crop factor based on the sattelite coordinates in the metadata
# crop_extra_edge provides an amount of pixels extra room
cropping = True
crop_extra_edge = 3
# Constants for autocrop
planet_diameter_km = 12742
camera_fov_deg = 0.62

# Exit on mouse hold (seconds)
mouse_exit_delay = 5

# Constants, don't change these
scanpath = r'data/*.jpg'
if not os.path.exists('./data'):
    os.makedirs('./data')
if not os.path.exists('./originals'):
    os.makedirs('./originals')

# Setup PyGame, if a file "debug" exists run it windowed
os.environ["DISPLAY"] = ":0"
pygame.init()
if(os.path.isfile("debug")):
    window = pygame.display.set_mode((480, 480))
else:
    window = pygame.display.set_mode((480, 480), pygame.FULLSCREEN)
clock = pygame.time.Clock()
pygame.mouse.set_visible(0)

# Load background surface
background = pygame.Surface(window.get_size())
background = pygame.image.load("loading.jpg").convert()

# Load foreground surface
image = pygame.Surface(window.get_size(), pygame.SRCALPHA)
image = pygame.image.load("loading.jpg").convert()
image.set_alpha(0)

window.blit(background, (0, 0))
pygame.display.flip()

# Functions
def blitFadeIn(target, image, pos, step=2):
    """Fade in function"""
    # borrowed from here https://stackoverflow.com/a/75003503/1850429
    alpha = image.get_alpha()
    alpha = min(255, alpha + step)
    image.set_alpha(alpha)
    target.blit(image, pos)
    return alpha == 255

def blitFadeOut(target, image, pos, step=2):
    """Fade out function"""
    # borrowed from here https://stackoverflow.com/a/75003503/1850429
    alpha = image.get_alpha()
    alpha = max(0, alpha - step)
    image.set_alpha(alpha)
    target.blit(image, pos)
    return alpha == 0

def find_and_download_new_images():
    """Check data directory, check api, download and crop new images we don't have, and delete old ones"""
    # Find images   
    # absolute path to search all text files inside a specific folder
    files = glob.glob(scanpath)
    basefilenames = []
    for f in files:
        basefilenames.append(os.path.basename(f))
    print(files)

    # Check for new images
    try:
        latest = AIA.download_latest_time(aia_channel)
        print(latest)
        timecompare = timedelta(minutes=15)
        if latest < datetime.now()-timecompare:
            print("downloading new image")
            AIA.download_latest_image(aia_channel, aia_resolution, "./data/")
    except Exception as e:
        print("There was a problem downloading and saving the images, no internet? Details below:")
        print(e)

    # Update scan list
    files = glob.glob(scanpath)

def delete_old_images():
    """Find and delete the oldest images"""
    files = sorted(glob.glob(scanpath))
    count = len(files)
    if(count > imageCount):
        print("More than {} images, cleaning the oldest".format(imageCount))
        for file in files:
            # 20231217_170741_512_0193.jpg
            f = os.path.splitext(os.path.basename(file))[0]
            split = f.split('_')
            stamp = split[0]+split[1]
            # 20231217153753
            date = datetime.strptime(stamp, '%Y%m%d%H%M%S')
            if date < datetime.now()-ageThreshold:
                print("{} old: {}".format(date,f))
            else:
                print("{} not: {}".format(date,f))
            # Remove by count, not time
            os.remove(file)
            print("Delete: {}".format(file))
            count = count - 1
            if(count <= imageCount):
                print("Deleted enough")
                break
    else:
        print("Less then {} images, skipping deletions".format(imageCount))

def selectNewImage(currentIndex):
    """Iterate the index through the data directory"""
    files = sorted(glob.glob(scanpath))
    currentIndex = currentIndex + 1
    if(currentIndex > len(files)-1):
        currentIndex = 0        
    if(len(files) == 0):               
        return "no-internet.jpg",currentIndex
    return files[currentIndex],currentIndex

# Startup code
AIA.download_range(datetime.now()-timedelta(days=1), datetime.now(), aia_channel, aia_resolution, "./data/", True)
delete_old_images()

# Read the last image count and the last time we checked api from file
try:
    with open("lastCheck","r") as file: 
        last_check = datetime.strptime(file.read(), "%d-%b-%Y (%H:%M:%S.%f)")
    print("last check from file {}".format(last_check))
except:
    last_check = datetime.now()-check_delay

# Loop
fadeStep = 255/frameRate/fadeTime
showImage = False
imageShown = False
lastRotation = datetime.now() - rotateTime
manual = False
currentIndex = 0
run = True
holdcounter = 0
done = True
fading = fadingSetting
while run:
    clock.tick(frameRate)
    # Handle exit events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False 
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            manual = len(glob.glob(scanpath))
            currentIndex = 0
            print(f"manual {manual}")
            fading = False
    # Also exit when mousebutton was held for mouse_exit_delay
    if pygame.mouse.get_pressed()[0]: 
        holdcounter = holdcounter + 1
        if(holdcounter > mouse_exit_delay * frameRate):
            run = False
    else:
        holdcounter = 0        

    # Fading
    if(fading):
        window.blit(background, (0, 0))
        if showImage:
            done = blitFadeIn(window, image, (0, 0), fadeStep)
            if done:
                imageShown = True
        if not showImage:
            done = blitFadeOut(window, image, (0, 0), fadeStep)
            if done:
                imageShown = False
    pygame.display.flip()
    
    # Scan new images
    timecompare = check_delay
    # Check more often if there are no files yet because we have no internet
    if(len(glob.glob(scanpath)) == 0):
        timecompare = datetime.timedelta(minutes=5)
    if last_check < datetime.now()-timecompare:
        print("Checking for new images {}".format(str(datetime.now())))
        last_check = datetime.now()
        with open("lastCheck","w") as file: 
            file.write(datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))

        find_and_download_new_images()
        delete_old_images()

    # Rotate images
    if(lastRotation < datetime.now()-rotateTime or manual > 0):
        if(manual > 0):
            manual -= 1
            if(manual == 0):
                # End the video with the most recent
                currentIndex = len(glob.glob(scanpath))-2
                fading = fadingSetting
        lastRotation = datetime.now()
        fileName,currentIndex = selectNewImage(currentIndex)
        if(not fading):
            print(f"update {fileName} {manual} {currentIndex}")
            image = pygame.image.load(fileName).convert() 
            image = pygame.transform.scale(image, (480,480))
            image.set_alpha(0xFF)
            window.blit(image, (0, 0))
        else:
            if(done and imageShown):
                # Replace background
                background = pygame.image.load(fileName).convert()
                background = pygame.transform.scale(background, (480,480))
            if(done and not imageShown):
                # Replace image 
                image = pygame.image.load(fileName).convert() 
                image = pygame.transform.scale(image, (480,480))
                image.set_alpha(0)
            if showImage:
                showImage = False
            else:
                showImage = True

pygame.quit()
exit()
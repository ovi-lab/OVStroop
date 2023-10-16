# Script to generate stimuli for the Stroop Task

import os

from PIL import Image, ImageDraw, ImageFont

def main() -> None:
    # Specify the colors used in the task. The stimuli images will consist of text
    # of a certain color written on a black background. The text and the color of
    # the text are both selected from the below list, and one stimulus is created
    # for every possible combination.
    colors = ['red', 'green', 'yellow', 'blue']

    # Image parameters common to every stimulus
    imgSize = (512,512)
    font = ImageFont.truetype("arial.ttf", size=40)

    for message in colors:
        for textColor in colors:
            # Create the image
            img = Image.new('RGB', imgSize, color='black')
            imgDraw = ImageDraw.Draw(img)
            
            # Get the location of the text in the image
            _, _, w, h = imgDraw.textbbox((0, 0), message, font=font)
            textSize = (w,h)
            xy = tuple((imgSize[k] - textSize[k]) / 2 for k in range(len(imgSize)))
            
            # Write the text on the image
            imgDraw.text(xy, message, font=font, fill=textColor)
            
            # Save the image
            start = os.path.dirname(__file__)
            fileDir = os.path.abspath(os.path.join(start, "..", "assets"))
            filename = f"stroop_stim_text_{message}_color_{textColor}.png"
            img.save(os.path.join(fileDir, filename))
        
if __name__ == "__main__":
    main()
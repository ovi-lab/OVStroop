# Script to generate stimuli for the Stroop Task

import os

from PIL import Image, ImageDraw, ImageFont

def makeStimuli() -> None:
    # Specify the colors used in the task. The stimuli images will consist of text
    # of a certain color written on a black background. The text and the color of
    # the text are both selected from the below list, and one stimulus is created
    # for every possible combination.
    colors = ['red', 'green', 'yellow', 'blue']

    # Image parameters common to every stimulus
    imgSize = __getImageSize()
    font = __getFont()

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

    
def makeInstructions() -> None:
    imgSize = __getImageSize()
    font = __getFont()
    
    # Specify what to write
    pages = [
        {
            'title' : "start",
            'content' : [
                {
                    'msg' : "Start of the experiment",
                    'color' : "white"
                },
                {
                    'msg' : "\n",
                    'color' : "white"
                },
                {
                    'msg' : "Press SPACE to continue",
                    'color' : "grey"
                }
            ]
        },
        {
            'title' : "start_block",
            'content' : [
                {
                    'msg' : "Start of the Block",
                    'color' : "white"
                },
                {
                    'msg' : "\n",
                    'color' : "white"
                },
                {
                    'msg' : "Press SPACE to continue",
                    'color' : "grey"
                }
            ]
        },
        {
            'title' : "ins1",
            'content' : [
                {
                    'msg' : "Thank you for participating in our study",
                    'color' : "white"
                },
                {
                    'msg' : "",
                    'color' : "white"
                },
                {
                    'msg' : "Here you are asked to identify the color of " +
                        "the word",
                    'color' : "white"
                },
                {
                    'msg' : "If you see this, for example",
                    'color' : "white"
                },
                {
                    'msg' : "GREEN",
                    'color' : "red"
                },
                {
                    'msg' : "\n",
                    'color' : "white"
                },
                {
                    'msg' : "Press SPACE to continue",
                    'color' : "grey"
                }
            ]
        },
        {
            'title' : "ins2",
            'content' : [
                {
                    'msg' : "Press the Red sticker for Red",
                    'color' : "red"
                },
                {
                    'msg' : "Press the Green sticker for Green",
                    'color' : "green"
                },
                {
                    'msg' : "Press the Blue sticker for Blue",
                    'color' : "blue"
                },
                {
                    'msg' : "Press the Yellow sticker for Yellow",
                    'color' : "yellow"
                },
                {
                    'msg' : "\n",
                    'color' : "white"
                },
                {
                    'msg' : "Press SPACE to continue",
                    'color' : "grey"
                }
            ]
        },
        {
            'title' : "ins3",
            'content' : [
                {
                    'msg' : "It is important that you press the button as " +
                        "fast as possible.",
                    'color' : "white"
                },
                {
                    'msg' : "",
                    'color' : "white"
                },
                {
                    'msg' : "When press the SPACEBAR you will see a " +
                        "fixation point (+) on the",
                    'color' : "white"
                },
                {
                    'msg' : "monitor for 1.5 seconds. Please stare at the " +
                        "fixation point as a",
                    'color' : "white"
                },
                {
                    'msg' : "stimulus will be presented there.",
                    'color' : "white"
                },
                {
                    'msg' : "",
                    'color' : "white"
                },
                {
                    'msg' : "Please ask any questions if you have any.",
                    'color' : "white"
                },
                {
                    'msg' : "\n",
                    'color' : "white"
                },
                {
                    'msg' : "Press SPACE to continue",
                    'color' : "grey"
                }
            ]
        },
        {
            'title' : "end",
            'content' : [
                {
                    'msg' : "End of the Experiment",
                    'color' : "white"
                }
            ]
        },
        {
            'title' : "end_block",
            'content' : [
                {
                    'msg' : "End of the Block",
                    'color' : "white"
                },
            ]
        },
        {
            'title' : "practice_red",
            'content' : [
                {
                    'msg' : "XXXX",
                    'color' : "red"
                },
            ]
        },
        {
            'title' : "practice_green",
            'content' : [
                {
                    'msg' : "XXXX",
                    'color' : "green"
                },
            ]
        },
        {
            'title' : "practice_blue",
            'content' : [
                {
                    'msg' : "XXXX",
                    'color' : "blue"
                },
            ]
        },
        {
            'title' : "practice_yellow",
            'content' : [
                {
                    'msg' : "XXXX",
                    'color' : "yellow"
                },
            ]
        },
        {
            'title' : "practice_start_block",
            'content' : [
                {
                    'msg' : "Start of the Practice Block",
                    'color' : "white"
                },
                {
                    'msg' : "\n",
                    'color' : "white"
                },
                {
                    'msg' : "Press SPACE to continue",
                    'color' : "grey"
                }
            ]
        },
        {
            'title' : "practice_end_block",
            'content' : [
                {
                    'msg' : "End of the Practice Block",
                    'color' : "white"
                },
            ]
        },
    ]
    
    for page in pages:
        # Create the image
        img = Image.new('RGB', imgSize, color='black')
        imgDraw = ImageDraw.Draw(img)
        
        # Get the location of all text in the image
        xy = []
        # Find the width and height of each line, and the total height
        totalHeight = 0
        for text in page['content']:
            _, _, w, h = imgDraw.multiline_textbbox(
                (0, 0), 
                text['msg'], 
                font=font
            )
            xy.append([w, h])
            totalHeight += h
        # Center each line horizontally and the overall text vertically
        for k in range(len(xy)):
            xy[k][0] = (imgSize[0] - xy[k][0]) / 2
            
            y0 = xy[k - 1][1] if k > 0 else (imgSize[1] - totalHeight) / 2
            xy[k][1] = y0 + xy[k][1]
            
        # Write the text on the image
        for k, text in enumerate(page['content']):
            imgDraw.multiline_text(
                xy[k], 
                text['msg'], 
                font=font, 
                fill=text['color']
            )
            
        # Save the image
            start = os.path.dirname(__file__)
            fileDir = os.path.abspath(os.path.join(start, "..", "assets"))
            filename = f"{page['title']}.png"
            img.save(os.path.join(fileDir, filename))
            
def __getImageSize():
    return (3840,2160)

def __getFont():
    return ImageFont.truetype("arial.ttf", size=40)
        
if __name__ == "__main__":
    makeStimuli()
    makeInstructions()
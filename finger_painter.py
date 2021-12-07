import numpy as np
import cv2
from collections import deque


# Import images and resize them to display
logo = cv2.imread('logo.png')
logo = cv2.resize(logo, (100,100))


# Some colors for you to use
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (122, 122, 122)

colors = [BLUE, GREEN, RED, YELLOW]


def draw_layout(frame):
    """
    Function takes a default frame of the live camera and:
        - Flips the frame (to make writing easier)
        - Converts the frame to HSV scale
        - Draws the layout components (button rectangles and text)
        - Includes images into the frame (logos)
    
    Returns the modified frame and its HSV equivalent
    """
    # Flip the frame (1 stands for y-axis, i.e. mirror the image)
    frame = cv2.flip(frame, 1)
    
    # Convert the given frame to HSV scale and save it
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    frame = cv2.rectangle(frame, (40, 1), (140, 65), (122, 122, 122), -1)
    frame = cv2.rectangle(frame, (160, 1), (255, 65), colors[0], -1)
    frame = cv2.rectangle(frame, (275, 1), (370, 65), colors[1], -1)
    frame = cv2.rectangle(frame, (390, 1), (485, 65), colors[2], -1)
    #     frame = cv2.rectangle(frame, (505, 1), (600, 65),
    #                         colors[3], -1)
        
        
    cv2.putText(frame, "CLEAR ALL", (49, 33),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 255), 2, cv2.LINE_AA)
    
    cv2.putText(frame, "BLUE", (185, 33),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 255), 2, cv2.LINE_AA)
    
    cv2.putText(frame, "GREEN", (298, 33),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 255), 2, cv2.LINE_AA)
    
    cv2.putText(frame, "RED", (420, 33),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 255), 2, cv2.LINE_AA)
    
    # We are displaying the logo instead of the yellow button
    # cv2.putText(frame, "YELLOW", (520, 33),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.5,
    #             (150, 150, 150), 2, cv2.LINE_AA)
    
    # Draw the logo on the frame
    frame[1:101, 510:610] = logo
    
    # Return the frame and the HSV version
    return frame, hsv


def create_mask(hsv):
    """
    Given an HSV version of the frame, create a mask performing one or more of the
    following operations (morphological transformations):
        - Segment out a region of the image within the lower-upper range of HSV
        - "Erosion"
        - "Opening"
        - "Dilation"
    """

    # The "pointer" you will use to draw must have a color between
    # the lower and upper HSV range to be recognized
    lower_hsv = np.array([64, 72, 49])
    upper_hsv = np.array([153, 255, 255])
    
    # The kernel to be used for transformation purposes
    kernel = np.ones((5, 5), np.uint8)

    # Apply the morphological transformations
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    mask = cv2.erode(mask, kernel, iterations = 1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.dilate(mask, kernel, iterations = 1)

    return mask


def main():
    # Loading the default webcam of PC.
    camera = cv2.VideoCapture(0)
    
    # Initializing lists to hold all points drawn
    bpoints = [deque(maxlen = 1024)]
    gpoints = [deque(maxlen = 1024)]
    rpoints = [deque(maxlen = 1024)]
    ypoints = [deque(maxlen = 1024)]

    # Indices to keep track of the position
    blue_index = 0
    green_index = 0
    red_index = 0
    yellow_index = 0
    
    colorIndex = 0
    
    # Keep looping
    while True:
        
        # Reading the frame from the camera
        ret, frame = camera.read()
        
        # Draw the layout on the frame and convert to HSV
        frame, hsv = draw_layout(frame)
        
        # Create the mask using the HSV frame
        mask = create_mask(hsv)
        
        # Find contours for the pointer after
        # idetifying it
        cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
        # Ifthe contours are formed
        if len(cnts) > 0:
            # sorting the contours to find biggest
            cnt = max(cnts, key = cv2.contourArea)
            
            if cv2.contourArea(cnt) > 1000:
                # Get the radius of the enclosing circle
                # around the found contour
                (x, y), radius = cv2.minEnclosingCircle(cnt)        
                
                # Draw the circle around the contour
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                
                # Calculating the center of the detected contour
                center = (int(x), int(y))
        
                # Now checking if the user wants to click on
                # any button above the screen
                if center[1] <= 65:
                    
                    # Clear Button
                    if 40 <= center[0] <= 140:
                        bpoints = [deque(maxlen = 512)]
                        gpoints = [deque(maxlen = 512)]
                        rpoints = [deque(maxlen = 512)]
                        ypoints = [deque(maxlen = 512)]
        
                        blue_index = 0
                        green_index = 0
                        red_index = 0
                        yellow_index = 0
        
                    elif 160 <= center[0] <= 255:
                            colorIndex = 0 # Blue
                    elif 275 <= center[0] <= 370:
                            colorIndex = 1 # Green
                    elif 390 <= center[0] <= 485:
                            colorIndex = 2 # Red
                    elif 505 <= center[0] <= 600:
                            colorIndex = 3 # Yellow
                else :
                    if colorIndex == 0:
                        bpoints[blue_index].appendleft(center)
                    elif colorIndex == 1:
                        gpoints[green_index].appendleft(center)
                    elif colorIndex == 2:
                        rpoints[red_index].appendleft(center)
                    elif colorIndex == 3:
                        ypoints[yellow_index].appendleft(center)
                    
        # Append the next deques when nothing is
        # detected to avois messing up
        else:
            bpoints.append(deque(maxlen = 512))
            blue_index += 1
            gpoints.append(deque(maxlen = 512))
            green_index += 1
            rpoints.append(deque(maxlen = 512))
            red_index += 1
            ypoints.append(deque(maxlen = 512))
            yellow_index += 1
    
        # Draw lines of all the colors on the
        # canvas and frame
        points = [bpoints, gpoints, rpoints, ypoints]
        for i in range(len(points)):
            
            for j in range(len(points[i])):
                
                for k in range(1, len(points[i][j])):
                    
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                        
                    cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2)
    
        # Show all the windows
        frame[1:101, 510:610] = logo
        cv2.imshow("Tracking", frame)
        cv2.imshow("mask", mask)
    
        # If the 'q' key is pressed then stop the application
        if cv2.waitKey(1) == ord("q"):
            break
    
    # Release the camera and all resources
    camera.release()
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    main()

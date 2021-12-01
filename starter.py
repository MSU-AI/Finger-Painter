import numpy as np
import cv2


# Import images and resize them to display
logo = cv2.imread('images/logo.png')
logo = cv2.resize(logo, (100,100))


# Some colors for you to use
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PINK = (255, 0, 255)
GRAY = (122, 122, 122)



def draw_layout(frame):
    """
    SECTION #3
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
    
    # Draw the "CLEAR ALL" rectangle on the frame
    frame = cv2.rectangle(frame, (40, 1), (140, 65), GRAY, -1)
    cv2.putText(frame, "CLEAR ALL", (49, 33),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 255), 2, cv2.LINE_AA)
    
    # Draw the "BLUE" rectangle on the frame
    frame = cv2.rectangle(frame, (160, 1), (255, 65), BLUE, -1)
    cv2.putText(frame, "BLUE", (185, 33),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 255, 255), 2, cv2.LINE_AA)
    
    # Draw the logo on the frame
    frame[1:101, 510:610] = logo
    
    # Return the frame and the HSV version
    return frame, hsv


def create_mask(hsv):
    """
    SECTION #4
    Given an HSV version of the frame, create a mask performing one or more of the
    following operations (morphological transformations):
        - Segment out a region of the image within the lower-upper range of HSV
        - "Erosion"
        - "Opening"
        - "Dilation"
    """

    # The "pointer" you will use to draw must have a color between
    # the lower and upper HSV range to be recognized
    lower_hsv = (128, 28, 19)
    upper_hsv = (306, 100, 100)
    
    # Scale the values to the way OpenCV likes it
    lower_hsv = np.array([lower_hsv[0] / 2, lower_hsv[1] * 2.55, lower_hsv[2] * 2.55])
    upper_hsv = np.array([upper_hsv[0] / 2, upper_hsv[1] * 2.55, upper_hsv[2] * 2.55])
    
    # Build the mask with the object of color in the range provided
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    
    # The kernel to be used for transformation purposes
    # kernel = np.ones(( XXX , XXX ), np.uint8)
    
    # Apply the morphological transformations
    # mask = cv2.dilate(mask, kernel, iterations = YYY)
    # mask = cv2.erode(mask, kernel, iterations = ZZZ)
    # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    return mask


def main():
    """
    SECTION #1
    """
    # List to store all the blue points drawn
    blue_points = []
    
    # Loading the default webcam of PC.
    camera = cv2.VideoCapture(0)
    
    # Keep reading the camera until the user quits
    while True:
        """
        SECTION #2
        """
        # Reading the frame from the camera
        ret, frame = camera.read()
        
        # Draw the layout on the frame and convert to HSV
        frame, hsv = draw_layout(frame)
            
        # Create the mask using the HSV frame
        mask = create_mask(hsv)
        
        """
        SECTION #5
        """
        # Find contours for the pointer after identifying it
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # If any contour is found
        if contours:
            """
            SECTION #6
            """
            # Find the largest contour in the contours
            largest_contour = max(contours, key = cv2.contourArea)
            
            # This is the area of the contour, how can you use it to ignore
            # small objects?
            area = cv2.contourArea(largest_contour)
        
            # Get the center position and radius of the contour's enclosing circle
            (x, y), radius = cv2.minEnclosingCircle(largest_contour)        
            center = (int(x), int(y))
            radius = int(radius)
            
            # Draw the circle around the contour
            cv2.circle(frame, center, radius, YELLOW, 2)
    
            # If the pointer is on the top margin (the button area)
            if center[1] <= 65:
                
                # If it's within the "CLEAR ALL" area, empty the list of points drawn
                if 40 <= center[0] <= 140:
                    blue_points = []
            
            # Else -we are below the top margin- keep drawing
            else:
                blue_points.append(center)
            
            
    
        """
        SECTION #7
        """
        # Draw the lines using the points in the list
        for i in range(1, len(blue_points)):
            # Skip "None" points
            if blue_points[i - 1] is None or blue_points[i] is None:
                continue
            
            # Connect the points with lines
            cv2.line(frame, blue_points[i - 1], blue_points[i], BLUE, 2)
    
        
        """
        SECTION #8
        """
        # Show all the windows
        cv2.imshow("Tracking", frame)
        cv2.imshow("mask", mask)
    
        # If the key 'q' is pressed then stop the application
        if cv2.waitKey(1) == ord("q"):
            break
    
    # Release the camera and all resources
    camera.release()
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    main()


import numpy as np
import cv2

def train_bg_subtractor(inst, cap, num=500):
    '''
        BG substractor need process some amount of frames to start giving result
    '''
    print ('Training BG Subtractor...')
    i = 0
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        inst.apply(frame, None, 0.001)
        i += 1
        if i >= num or not ret:
            return cap

def get_centroid(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)

    cx = x + x1
    cy = y + y1

    return (cx, cy)

def detect_vehicles(fg_mask, min_contour_width=35, min_contour_height=35, max_contour_width=300, max_contour_height=200):

    matches = []

    # finding external contours
    contours, hierarchy = cv2.findContours(
        fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

    # filtering by with, height
    for (i, contour) in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        contour_valid = (w >= min_contour_width) and (w < max_contour_width) and (
            h >= min_contour_height) and (h < max_contour_height)

        if not contour_valid:
            continue
        
        # getting center of the bounding box
        centroid = get_centroid(x, y, w, h)

        matches.append(((x, y, w, h), centroid))

    return matches, contours

def main():
    cap = cv2.VideoCapture("./img/vid3.mp4")
    #cap = cv2.VideoCapture(1)

    # bg_subtractor = cv2.createBackgroundSubtractorMOG2(
    #     history=2000, detectShadows=True)

    # train_bg_subtractor(bg_subtractor, cap, num=100)

    ret, first = cap.read()

    print(first.shape[:2])

    # Save the first image as reference
    first_gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)


    cv2.VideoCapture.set(cap, cv2.CAP_PROP_POS_MSEC, 0)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            break

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Display the resulting frame
        #cv2.imshow('frame',gray)

        # bg_subtractor.apply(frame, None, 0.001)

        # frame = bg_subtractor.apply(frame, None, 0.001)

        frame = cv2.absdiff(gray, first_gray)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))

        frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)

        frame = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)

        frame = cv2.erode(frame,kernel,iterations = 5)

        frame = cv2.dilate(frame, kernel, iterations=2)

        ret, frame = cv2.threshold(frame,50,255,cv2.THRESH_BINARY)

        matches, contours = detect_vehicles(frame)

        cv2.drawContours(frame, contours, -1, (0,255,0), 3)

        print(len(matches))

        cv2.imshow('frame',frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
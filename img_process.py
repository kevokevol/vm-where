import numpy as np
import cv2
import sys

def train_bg(bg, cap, num=500):
    '''
        BG substractor need process some amount of frames to start giving result
    '''
    print ('Training BG Subtractor...')
    i = 0
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        bg = cv2.addWeighted(bg,0.5,frame,0.5,0)
        i += 1
        if i >= num or not ret:
            return bg

def get_centroid(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)

    cx = x + x1
    cy = y + y1

    return (cx, cy)

def detect_vehicles(fg_mask, min_contour_width=35, min_contour_height=35, max_contour_width=400, max_contour_height=400):

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
    if sys.argv[1].isnumeric():
        vid = int(sys.argv[1])
    else:
        vid = sys.argv[1]
    cap = cv2.VideoCapture(vid)

    ret, bg = cap.read()
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
    bg = train_bg(bg, cap, num=100)

    print(bg.shape[:2])

    cv2.VideoCapture.set(cap, cv2.CAP_PROP_POS_MSEC, 0)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            break

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        frame = cv2.absdiff(gray, bg)

        ret, frame= cv2.threshold(frame,20,255,cv2.THRESH_TOZERO)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

        frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)

        frame = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel, iterations = 2)

        frame = cv2.erode(frame,kernel,iterations = 2)

        frame = cv2.dilate(frame, kernel, iterations = 2)

        ret, frame = cv2.threshold(frame,100,255,cv2.THRESH_BINARY)

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
import sys
import cv2

if __name__ == '__main__':
    # Get user supplied values
    image_path = sys.argv[1]
    casc_path = sys.argv[2]

    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier(casc_path)

    # Read the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    if len(faces) > 0:
        print(f'faces detected in {image_path}.\nfaces locations:\n{faces}')
    else:
        print(f'faces not detected in {image_path}')

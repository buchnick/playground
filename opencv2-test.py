import sys
import cv2

CASC_PATH = 'cascades/haarcascade_frontalface_alt2.xml'


def get_faces_locations(_image_path: str) -> list[str]:
    # Create the haar cascade
    face_cascade = cv2.CascadeClassifier(CASC_PATH)

    # Read the image
    image = cv2.imread(_image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    pedestrians = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=2,
        minSize=(5, 5),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    print("Found {0} ppl!".format(len(pedestrians)))

    # Draw a rectangle around the detected objects
    for (x, y, w, h) in pedestrians:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imwrite("output.jpg", image)
    cv2.imshow("Ppl found", image)
    cv2.waitKey(0)

    return pedestrians


def is_face_exists(_image_path: str) -> bool:
    return len(get_faces_locations(_image_path)) > 0


if __name__ == '__main__':
    # Get user supplied values
    image_path = sys.argv[1]

    faces = get_faces_locations(image_path)
    if len(faces) > 0:
        print(f'{len(faces)} faces detected in {image_path}.\nfaces locations:\n{faces}')
    else:
        print(f'faces not detected in {image_path}')

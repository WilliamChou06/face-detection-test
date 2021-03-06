try:
    import os
    os.add_dll_directory(os.path.join(os.environ['CUDA_PATH_V10_1'], 'bin'))
except Exception:
    pass

import face_recognition
import cv2
import numpy as np
import dlib

from PIL import ImageGrab

def get_image_encoding(file_pathname):
    image = face_recognition.load_image_file(file_pathname)
    image_encoding = face_recognition.face_encodings(image)[0]

    return image_encoding

# Create arrays of known face encodings and their names
# known_face_encodings = [
#     inbar_lavi_encoding,
#     tom_ellis_encoding
# ]
# known_face_names = [
#     'Inbar Lavi',
#     'Tom Ellis'
# ]

known_face_encodings = []
known_face_names = []

for file in os.listdir('photos'):
    file_pathname = f'photos/{str(file)}'
    print(file_pathname)
    image_encoding = get_image_encoding(file_pathname)
    known_face_encodings.append(image_encoding)
    known_face_names.append(str(file).replace('.jpg', '').replace('_', ' '))

# inbar_lavi = face_recognition.load_image_file("inbar_lavi.jpg")
# inbar_lavi_encoding = face_recognition.face_encodings(inbar_lavi)[0]

# tom_ellis = face_recognition.load_image_file("tom_ellis.jpg")
# tom_ellis_encoding = face_recognition.face_encodings(tom_ellis)[0]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    # Grab a single frame of video
    # ret, frame = video_capture.read()
    capture = ImageGrab.grab()
    frame = np.array(capture)

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.50, fy=0.50)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame, model='cnn')
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Face Detection Video', cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
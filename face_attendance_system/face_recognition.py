import os
import cv2
import pickle
import numpy as np

# Paths
HAARCASCADE_PATH = "models/haarcascade_frontalface_default.xml"
TRAINED_MODEL_PATH = "models/trained_model.yml"
LABEL_NAMES_PATH = "models/label_names.pkl"

class FaceRecognition:
    def __init__(self):
        try:
            # Load face cascade
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + HAARCASCADE_PATH)
            if self.face_cascade.empty():
                raise FileNotFoundError("Haarcascade file not found or corrupted.")

            # Load face recognizer
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            self.label_names = {}
            self.load_model()
        except Exception as e:
            print(f"Error initializing FaceRecognition: {e}")

    def load_model(self):
        try:
            if not os.path.exists(TRAINED_MODEL_PATH):
                raise FileNotFoundError(f"Trained model file '{TRAINED_MODEL_PATH}' not found.")

            self.recognizer.read(TRAINED_MODEL_PATH)

            if not os.path.exists(LABEL_NAMES_PATH):
                raise FileNotFoundError(f"Label names file '{LABEL_NAMES_PATH}' not found.")

            with open(LABEL_NAMES_PATH, "rb") as f:
                self.label_names = pickle.load(f)

            if not self.label_names:
                raise ValueError("Label names file is empty or corrupted.")
        except Exception as e:
            print(f"Error loading model: {e}")

    def detect_faces(self, frame):
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            return gray, faces
        except cv2.error as e:
            print(f"OpenCV error in detect_faces: {e}")
            return frame, []

    def recognize_faces(self, gray, faces):
        recognized_faces = []
        try:
            for (x, y, w, h) in faces:
                face = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face, (200, 200))

                label_id, confidence = self.recognizer.predict(face_resized)
                person_name = self.label_names.get(label_id, "Unknown")
                recognized_faces.append((x, y, w, h, person_name, confidence))
        except Exception as e:
            print(f"Error in recognize_faces: {e}")
        return recognized_faces

    def update_frame(self, frame):
        gray, faces = self.detect_faces(frame)
        recognized_faces = self.recognize_faces(gray, faces)

        for (x, y, w, h, person_name, confidence) in recognized_faces:
            color = (0, 255, 0) if person_name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, f"{person_name} ({confidence:.2f})", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        return frame

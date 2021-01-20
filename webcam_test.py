import cv2
import numpy as np
import torch

from blazeface import BlazeFace
from performance_profile import TimeMeasure

net = BlazeFace()
net.load_weights("blazeface.pth")
net.load_anchors("anchors.npy")
anchors = np.load("anchors.npy")
anchors.astype(np.float32).tofile("anchors_blazeface_pytorch_5af71b66.bin")

# Optionally change the thresholds:
net.min_score_thresh = 0.75
net.min_suppression_threshold = 0.3

capture = cv2.VideoCapture(0)
while True:
    ret, img = capture.read()
    if not ret:
        break
    windowsize = (128, 128)
    # rimg = cv2.resize(img, windowsize)
    rimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    for i in range(10):
        with TimeMeasure("predict"):
            detections = net.predict_on_image(rimg)

    TimeMeasure.print_all_avg()

    if isinstance(detections, torch.Tensor):
        detections = detections.cpu().numpy()

    if detections.ndim == 1:
        detections = np.expand_dims(detections, axis=0)

    for i in range(detections.shape[0]):
        ymin = int(detections[i, 0] * img.shape[0])
        xmin = int(detections[i, 1] * img.shape[1])
        ymax = int(detections[i, 2] * img.shape[0])
        xmax = int(detections[i, 3] * img.shape[1])

        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 0))
        for k in range(6):
            kp_x = detections[i, 4 + k * 2] * img.shape[1]
            kp_y = detections[i, 4 + k * 2 + 1] * img.shape[0]
            cv2.circle(img, (int(kp_x), int(kp_y)), 2, (0, 255, 0))
    cv2.imshow('result', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

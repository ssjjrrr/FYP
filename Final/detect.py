#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import cv2
import onnxruntime
import argparse
import random
import time
import pyttsx3
import numpy as np

from utils import letterbox, scale_coords


class Detector():

    def __init__(self, opt):
        super(Detector, self).__init__()
        self.img_size = opt.img_size
        self.threshold = opt.conf_thres
        self.iou_thres = opt.iou_thres
        self.stride = 1
        self.weights = opt.weights
        self.init_model()
        self.names = ['crossing', 'green','red', 'stairs']

    def init_model(self):
        
        sess = onnxruntime.InferenceSession(self.weights)  # 加载模型权重
        self.input_name = sess.get_inputs()[0].name  # 获得输入节点
        output_names = []
        for i in range(len(sess.get_outputs())):
            print("output node:", sess.get_outputs()[i].name)
            output_names.append(sess.get_outputs()[i].name)  # 所有的输出节点
        print(output_names)
        self.output_name = sess.get_outputs()[0].name  # 获得输出节点的名称
        print(f"input name {self.input_name}-----output_name{self.output_name}")
        input_shape = sess.get_inputs()[0].shape  # 输入节点形状
        print("input_shape:", input_shape)
        self.m = sess

    def preprocess(self, img):
        
        img0 = img.copy()
        img = letterbox(img, new_shape=self.img_size)[0]  # 图片预处理
        img = img[:, :, ::-1].transpose(2, 0, 1)
        img = np.ascontiguousarray(img).astype(np.float32)
        img /= 255.0
        img = np.expand_dims(img, axis=0)
        assert len(img.shape) == 4
        return img0, img

    def detect(self, im):
        
        img0, img = self.preprocess(im)
        pred = self.m.run(None, {self.input_name: img})[0]  # 执行推理
        pred = pred.astype(np.float32)
        pred = np.squeeze(pred, axis=0)
        boxes = []
        classIds = []
        confidences = []
        for detection in pred:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID] * detection[4]  # 置信度为类别的概率和目标框概率值得乘积

            if confidence > self.threshold:
                box = detection[0:4]
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                boxes.append([x, y, int(width), int(height)])
                classIds.append(classID)
                confidences.append(float(confidence))
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.threshold, self.iou_thres)  # 执行nms算法
        pred_boxes = []
        pred_confes = []
        pred_classes = []
        if len(idxs) > 0:
            for i in idxs.flatten():
                confidence = confidences[i]
                if confidence >= self.threshold:
                    pred_boxes.append(boxes[i])
                    pred_confes.append(confidence)
                    pred_classes.append(classIds[i])
        return im, pred_boxes, pred_confes, pred_classes


def plot_one_box(x, img, color=None, label=None, line_thickness=None):
    tl = (
        line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1
    )  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(
            img,
            label,
            (c1[0], c1[1] - 2),
            0,
            tl / 3,
            [225, 255, 255],
            thickness=tf,
            lineType=cv2.LINE_AA,
        )

def main(opt):
    engine = pyttsx3.init()
    # engine.say("Welcome to the yolov5_ort demo")
    # engine.runAndWait()

    det = Detector(opt)
    video = 0
    cap = cv2.VideoCapture(video)
    dic_labels= {0:'crossing',
            1:'green',
            2:'red',
            }
    original_fps = cap.get(cv2.CAP_PROP_FPS)  # 原始视频的帧率
    frame_time = 1 / original_fps  # 每帧的时间间隔

    total_frames_processed = 0
    total_time_spent = 0
    speak_time = time.time()

    while True:
        start_time = time.time()
        success, image = cap.read()

        shape = (det.img_size, det.img_size)
        if success:
            img, pred_boxes, pred_confes, pred_classes = det.detect(image)
            detected = []
            for box,score,id in zip(pred_boxes, pred_confes, pred_classes):
                detected.append([id])
                left, top, width, height = box[0], box[1], box[2], box[3]
                box = (left, top, left + width, top + height)
                box = np.squeeze(
                scale_coords(shape, np.expand_dims(box, axis=0).astype("float"), img.shape[:2]).round(), axis=0).astype(
                "int")
                label = '%s:%.2f'%(dic_labels[id],score)
                plot_one_box(box, img, color=(255,0,0), label=label, line_thickness=None)
                cv2.imshow("video",img)
            if time.time() - speak_time > 2 and len(set(detected)) > 0:
                for class_id in set(detected):
                    engine.say(dic_labels[class_id])
                    engine.runAndWait()
                speak_time = time.time()
        end_time = time.time()
        processing_time = end_time - start_time
        total_frames_processed += 1
        total_time_spent += processing_time

        if processing_time > frame_time:
            skip_count = int(processing_time // frame_time)
            for _ in range(skip_count):
                cap.read()

        key=cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    cap.release()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='best.onnx', help='onnx path(s)')
    parser.add_argument('--img', type=str, default='../models/nan.jpg', help='source')  # file/folder, 0 for webcam
    parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='IOU threshold for NMS')
    parser.add_argument('--line-thickness', default=1, type=int, help='bounding box thickness (pixels)')
    parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
    parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
    opt = parser.parse_args()
    main(opt)

"""滑块验证码处理"""

import random
import time
from typing import Dict, List, Tuple

import cv2
import numpy as np


def find_slider_gap(bg_image: bytes, slider_image: bytes) -> Tuple[int, float]:
    """使用 OpenCV 模板匹配找到滑块缺口位置"""
    bg = cv2.imdecode(np.frombuffer(bg_image, np.uint8), cv2.IMREAD_COLOR)
    slider = cv2.imdecode(np.frombuffer(slider_image, np.uint8), cv2.IMREAD_UNCHANGED)

    if bg is None or slider is None:
        raise ValueError("无法解码验证码图片")

    bgr = slider[:, :, :3]
    alpha = slider[:, :, 3]

    ys, _ = np.where(alpha > 0)
    y_min, y_max = ys.min(), ys.max()
    cropped = bgr[y_min:y_max + 1, :]
    alpha_cropped = alpha[y_min:y_max + 1, :]

    result = cv2.matchTemplate(bg, cropped, cv2.TM_CCOEFF_NORMED, mask=alpha_cropped)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    return max_loc[0], max_val


def generate_slide_track(start_x: int, start_y: int, distance: int, duration_ms: int = 800) -> List[Dict]:
    """
    生成模拟的滑块拖动轨迹
    注意: 正方系统使用的是 clientX/clientY (绝对坐标)，不是相对位移！
    """
    track = []
    start_time = int(time.time() * 1000)
    track.append({"x": start_x, "y": start_y, "t": start_time})

    end_x = start_x + distance
    steps = random.randint(15, 25)
    for i in range(1, steps):
        progress = i / (steps - 1)
        eased = 1 - (1 - progress) ** 2
        x = int(start_x + (end_x - start_x) * eased)
        y = start_y + random.randint(-2, 2)
        t = start_time + int(duration_ms * progress) + random.randint(0, 15)
        track.append({"x": x, "y": y, "t": t})

    track.append({"x": end_x, "y": start_y, "t": start_time + duration_ms + random.randint(10, 50)})
    return track

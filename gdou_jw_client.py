#!/usr/bin/env python3
"""
广东海洋大学教务系统客户端
正方教务系统 V9.0 逆向实现

职责：登录教务系统并查询课表、考试、成绩信息

使用方法:
    uv run python gdou_jw_client.py

配置:
    在项目目录创建 .env 文件:
    GDOU_USERNAME=你的学号
    GDOU_PASSWORD=你的密码

作者: AI Assistant
日期: 2026-06-11
"""

import os
import re
import json
import base64
import time
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import cv2
import numpy as np


# ============== 配置 ==============

BASE_URL = "https://jw.gdou.edu.cn"
TIMEOUT = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


# ============== 工具函数 ==============

def ef(text: str) -> str:
    """滑块验证码轨迹加密函数 - Base64(UTF-8)"""
    return base64.b64encode(text.encode("utf-8")).decode("utf-8")


def rsa_encrypt(password: str, modulus_b64: str, exponent_b64: str) -> str:
    """使用 RSA 公钥加密密码"""
    modulus_hex = base64.b64decode(modulus_b64).hex()
    exponent_hex = base64.b64decode(exponent_b64).hex()
    n = int(modulus_hex, 16)
    e = int(exponent_hex, 16)
    key = RSA.construct((n, e))
    cipher = PKCS1_v1_5.new(key)
    encrypted = cipher.encrypt(password.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


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


# ============== 教务系统客户端 ==============

class GdouJwClient:
    """广东海洋大学教务系统客户端"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.base_url = BASE_URL
        self.logged_in = False
        self.instance_id = "zfcaptchaLogin"
        self._rtk: Optional[str] = None

    def _url(self, path: str) -> str:
        return urljoin(self.base_url, path)

    def _get_rtk(self) -> str:
        """从验证码 JS 中获取 RTK (每次刷新页面都会变化)"""
        if self._rtk:
            return self._rtk

        resp = self.session.get(
            self._url("/zfcaptchaLogin"),
            params={"type": "resource", "instanceId": self.instance_id, "name": "zfdun_captcha.js"},
            timeout=TIMEOUT
        )
        resp.raise_for_status()

        rtk_match = re.search(r"rtk:'([^']+)'", resp.text)
        if not rtk_match:
            raise RuntimeError("无法获取验证码 RTK")

        self._rtk = rtk_match.group(1)
        return self._rtk

    def _get_login_page(self) -> Dict[str, str]:
        """获取登录页面，提取 CSRF Token 和隐藏字段"""
        resp = self.session.get(self._url("/xtgl/login_slogin.html"), timeout=TIMEOUT)
        resp.raise_for_status()
        html = resp.text

        csrf_match = re.search(r'id="csrftoken"[^>]*value="([^"]+)"', html)
        result = {"csrftoken": csrf_match.group(1) if csrf_match else ""}

        for field in ["mmsfjm", "mmsrddcshkzfs", "dlsbsdsj", "xxdm", "language"]:
            match = re.search(rf'id="{field}"[^>]*value="([^"]*)"', html)
            if match:
                result[field] = match.group(1)

        return result

    def _get_public_key(self) -> Tuple[str, str]:
        """获取 RSA 公钥"""
        timestamp = int(time.time() * 1000)
        resp = self.session.get(self._url(f"/xtgl/login_getPublicKey.html?time={timestamp}"), timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data["modulus"], data["exponent"]

    def _refresh_captcha(self) -> Dict[str, str]:
        """刷新验证码图片"""
        rtk = self._get_rtk()
        timestamp = int(time.time() * 1000)
        resp = self.session.get(
            self._url("/zfcaptchaLogin"),
            params={"type": "refresh", "rtk": rtk, "time": timestamp, "instanceId": self.instance_id},
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        return resp.json()

    def _get_captcha_images(self, captcha_data: Dict) -> Tuple[bytes, bytes]:
        """下载验证码图片"""
        bg_resp = self.session.get(
            self._url("/zfcaptchaLogin"),
            params={"type": "image", "id": captcha_data["si"], "imtk": captcha_data["imtk"],
                    "t": captcha_data["t"], "instanceId": self.instance_id},
            timeout=TIMEOUT
        )
        bg_resp.raise_for_status()

        slider_resp = self.session.get(
            self._url("/zfcaptchaLogin"),
            params={"type": "image", "id": captcha_data["mi"], "imtk": captcha_data["imtk"],
                    "t": captcha_data["t"], "instanceId": self.instance_id},
            timeout=TIMEOUT
        )
        slider_resp.raise_for_status()

        return bg_resp.content, slider_resp.content

    def _verify_captcha(self, move_track: List[Dict]) -> bool:
        """提交滑块验证码验证"""
        rtk = self._get_rtk()
        track_json = json.dumps(move_track)
        encrypted_track = ef(track_json)
        timestamp = int(time.time() * 1000)

        navigator_info = {
            "appName": "Netscape",
            "userAgent": HEADERS["User-Agent"],
            "appVersion": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        extend = ef(json.dumps(navigator_info))

        resp = self.session.post(
            self._url("/zfcaptchaLogin"),
            data={"type": "verify", "rtk": rtk, "time": timestamp, "mt": encrypted_track,
                  "instanceId": self.instance_id, "extend": extend},
            timeout=TIMEOUT
        )
        resp.raise_for_status()

        try:
            result = resp.json()
            return result.get("status") == "success"
        except:
            return False

    def _solve_captcha(self) -> bool:
        """自动解决滑块验证码"""
        captcha_data = self._refresh_captcha()
        bg_image, slider_image = self._get_captcha_images(captcha_data)

        try:
            gap_x, _ = find_slider_gap(bg_image, slider_image)
        except Exception as e:
            print(f"缺口识别失败: {e}")
            return False

        start_client_x = random.randint(500, 600)
        start_client_y = random.randint(380, 420)
        track = generate_slide_track(start_client_x, start_client_y, gap_x)

        return self._verify_captcha(track)

    def login(self, username: str, password: str) -> bool:
        """登录教务系统"""
        print(f"开始登录: {username}")

        print("1. 获取登录页面...")
        page_data = self._get_login_page()

        print("2. 获取 RSA 公钥...")
        modulus, exponent = self._get_public_key()

        print("3. 加密密码...")
        encrypted_password = rsa_encrypt(password, modulus, exponent)

        print("4. 解决滑块验证码...")
        captcha_success = self._solve_captcha()
        if not captcha_success:
            print("验证码验证失败，尝试重试...")
            for i in range(2):
                print(f"   第 {i+2} 次尝试...")
                if self._solve_captcha():
                    break
            else:
                print("验证码多次失败，登录中止")
                return False

        print("5. 提交登录...")
        timestamp = int(time.time() * 1000)
        login_data = {
            "csrftoken": page_data.get("csrftoken", ""),
            "language": "zh_CN",
            "yhm": username,
            "mm": encrypted_password,
        }

        resp = self.session.post(
            self._url(f"/xtgl/login_slogin.html?time={timestamp}"),
            data=login_data,
            timeout=TIMEOUT,
            allow_redirects=False
        )

        if resp.status_code == 302:
            location = resp.headers.get("Location", "")
            print(f"   登录成功!")
            self.logged_in = True
            self.session.get(self._url(location), timeout=TIMEOUT)
            return True
        else:
            print(f"   登录响应状态: {resp.status_code}")
            if "密码" in resp.text or "错误" in resp.text:
                print("   可能是密码错误")
            return False

    def get_schedule(self, year: str, term: int) -> List[Dict]:
        """
        查询课表

        Args:
            year: 学年，如 "2024"
            term: 学期 (1 或 2)

        Returns:
            课程列表
        """
        if not self.logged_in:
            raise RuntimeError("请先登录")

        term_code = "3" if term == 1 else "12"

        resp = self.session.post(
            self._url("/kbcx/xskbcx_cxXsgrkb.html"),
            data={"xnm": year, "xqm": term_code, "kzlx": "ck"},
            timeout=TIMEOUT
        )
        resp.raise_for_status()

        data = resp.json()
        return data.get("kbList", [])

    def get_exams(self, year: str, term: int) -> List[Dict]:
        """
        查询考试安排

        Args:
            year: 学年
            term: 学期 (1 或 2)

        Returns:
            考试列表
        """
        if not self.logged_in:
            raise RuntimeError("请先登录")

        term_code = "3" if term == 1 else "12"

        resp = self.session.post(
            self._url("/kwgl/kscx_cxXsksxxIndex.html?doType=query"),
            data={"xnm": year, "xqm": term_code, "queryModel.showCount": 100},
            timeout=TIMEOUT
        )
        resp.raise_for_status()

        data = resp.json()
        return data.get("items", [])

    def get_grades(self, year: str, term: int) -> List[Dict]:
        """
        查询成绩

        Args:
            year: 学年
            term: 学期 (1 或 2)

        Returns:
            成绩列表
        """
        if not self.logged_in:
            raise RuntimeError("请先登录")

        term_code = "3" if term == 1 else "12"

        resp = self.session.post(
            self._url("/cjcx/cjcx_cxDgXscj.html?doType=query"),
            data={"xnm": year, "xqm": term_code, "queryModel.showCount": 100},
            timeout=TIMEOUT
        )
        resp.raise_for_status()

        data = resp.json()
        return data.get("items", [])


# ============== 主程序 ==============

def main():
    load_dotenv()

    username = os.environ.get("GDOU_USERNAME", "").strip()
    password = os.environ.get("GDOU_PASSWORD", "").strip()

    if not username or not password:
        print("错误: 请在 .env 文件中设置 GDOU_USERNAME 和 GDOU_PASSWORD")
        return

    client = GdouJwClient()

    if not client.login(username, password):
        print("登录失败")
        return

    print("\n=== 课表查询 ===")
    courses = client.get_schedule("2024", 2)
    print(f"共 {len(courses)} 门课程")
    for c in courses[:5]:
        print(f"  {c.get('kcmc', '未知')} | {c.get('xqjmc', '')} {c.get('jc', '')} | {c.get('cdmc', '')} | {c.get('zcd', '')}")

    print("\n=== 考试查询 ===")
    exams = client.get_exams("2024", 2)
    print(f"共 {len(exams)} 门考试")
    for e in exams[:5]:
        print(f"  {e.get('kcmc', '未知')} | {e.get('kssj', '')} | {e.get('cdmc', '')}")

    print("\n=== 成绩查询 ===")
    grades = client.get_grades("2024", 2)
    print(f"共 {len(grades)} 条成绩")
    for g in grades[:5]:
        print(f"  {g.get('kcmc', '未知')} | 成绩: {g.get('cj', '')} | 绩点: {g.get('jd', '')} | 学分: {g.get('xf', '')}")


if __name__ == "__main__":
    main()

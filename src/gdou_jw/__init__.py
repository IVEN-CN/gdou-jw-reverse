"""广东海洋大学教务系统客户端"""

import os
import re
import json
import time
import random
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv

from .crypto import rsa_encrypt, ef
from .captcha import find_slider_gap, generate_slide_track


BASE_URL = "https://jw.gdou.edu.cn"
TIMEOUT = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


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

    def _get_public_key(self):
        """获取 RSA 公钥"""
        timestamp = int(time.time() * 1000)
        resp = self.session.get(self._url(f"/xtgl/login_getPublicKey.html?time={timestamp}"), timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data["modulus"], data["exponent"]

    def _refresh_captcha(self):
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

    def _get_captcha_images(self, captcha_data: Dict):
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
            print("   登录成功!")
            self.logged_in = True
            self.session.get(self._url(resp.headers.get("Location", "")), timeout=TIMEOUT)
            return True
        else:
            print(f"   登录响应状态: {resp.status_code}")
            return False

    def get_schedule(self, year: str, term: int) -> List[Dict]:
        """查询课表"""
        if not self.logged_in:
            raise RuntimeError("请先登录")

        term_code = "3" if term == 1 else "12"
        resp = self.session.post(
            self._url("/kbcx/xskbcx_cxXsgrkb.html"),
            data={"xnm": year, "xqm": term_code, "kzlx": "ck"},
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        return resp.json().get("kbList", [])

    def get_exams(self, year: str, term: int) -> List[Dict]:
        """查询考试安排"""
        if not self.logged_in:
            raise RuntimeError("请先登录")

        term_code = "3" if term == 1 else "12"
        resp = self.session.post(
            self._url("/kwgl/kscx_cxXsksxxIndex.html?doType=query"),
            data={"xnm": year, "xqm": term_code, "queryModel.showCount": 100},
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        return resp.json().get("items", [])

    def get_grades(self, year: str, term: int) -> List[Dict]:
        """查询成绩"""
        if not self.logged_in:
            raise RuntimeError("请先登录")

        term_code = "3" if term == 1 else "12"
        resp = self.session.post(
            self._url("/cjcx/cjcx_cxDgXscj.html?doType=query"),
            data={"xnm": year, "xqm": term_code, "queryModel.showCount": 100},
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        return resp.json().get("items", [])

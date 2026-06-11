"""命令行入口"""

import os
from dotenv import load_dotenv

from . import GdouJwClient


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

"""命令行入口 - 使用 Click"""

import os
from typing import Optional

import click
from dotenv import load_dotenv

from . import GdouJwClient


def _get_client():
    """获取已登录的客户端"""
    load_dotenv()
    username = os.environ.get("GDOU_USERNAME", "").strip()
    password = os.environ.get("GDOU_PASSWORD", "").strip()

    if not username or not password:
        click.echo("错误: 请在 .env 文件中设置 GDOU_USERNAME 和 GDOU_PASSWORD", err=True)
        raise click.Abort()

    client = GdouJwClient()
    if not client.login(username, password):
        click.echo("登录失败", err=True)
        raise click.Abort()

    return client


@click.group()
def cli():
    """广东海洋大学教务系统查询工具"""
    pass


@cli.command()
@click.option("--year", "-y", default="2025", help="学年，如 2025")
@click.option("--term", "-t", default=1, type=int, help="学期: 1 或 2")
def courses(year: str, term: int):
    """查询课表"""
    client = _get_client()
    items = client.get_schedule(year, term)

    click.echo(f"\n=== {year}-{int(year)+1}学年 第{term}学期课表 ({len(items)}门) ===\n")
    for c in items:
        click.echo(
            f"{c.get('xqjmc', '')} {c.get('jc', '')} | "
            f"{c.get('kcmc', '未知')} | "
            f"{c.get('cdmc', '')} | "
            f"{c.get('zcd', '')}"
        )


@cli.command()
@click.option("--year", "-y", default="2025", help="学年，如 2025")
@click.option("--term", "-t", default=1, type=int, help="学期: 1 或 2")
def exams(year: str, term: int):
    """查询考试安排"""
    client = _get_client()
    items = client.get_exams(year, term)

    click.echo(f"\n=== {year}-{int(year)+1}学年 第{term}学期考试 ({len(items)}门) ===\n")
    for e in items:
        click.echo(
            f"{e.get('kcmc', '未知')} | "
            f"{e.get('kssj', '')} | "
            f"{e.get('cdmc', '')}"
        )


@cli.command()
@click.option("--year", "-y", default="2025", help="学年，如 2025")
@click.option("--term", "-t", default=1, type=int, help="学期: 1 或 2")
def grades(year: str, term: int):
    """查询成绩"""
    client = _get_client()
    items = client.get_grades(year, term)

    click.echo(f"\n=== {year}-{int(year)+1}学年 第{term}学期成绩 ({len(items)}条) ===\n")
    for g in items:
        click.echo(
            f"{g.get('kcmc', '未知')} | "
            f"成绩: {g.get('cj', '')} | "
            f"绩点: {g.get('jd', '')} | "
            f"学分: {g.get('xf', '')}"
        )


def main():
    cli()

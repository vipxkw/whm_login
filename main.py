import os
import asyncio
import requests
from pyppeteer import launch
from datetime import datetime, timezone, timedelta

async def login(url: str, email: str, password:str) -> bool:
    page = None
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    try:
        page = await browser.newPage()
        await page.goto(url)
        original_url = page.url
        await page.type('#inputEmail', email)
        await page.type('#inputPassword', password)

        login_button = await page.querySelector('#login')
        if login_button:
            await login_button.click()
        else:
            raise Exception('无法找到登陆按钮')
        await page.waitForNavigation(timeout=5000)
        current_url = page.url

        if current_url != original_url:
            return True
        else:
            return False
    except Exception as e:
        print(f'账号登录时出现错误: {e}')
        return False
    finally:
        if page is not None:
            await page.close()
        if browser is not None:
            await browser.close()

async def send_notification(token: str, message: str) -> None:
    url = 'https://push.chinasclm.com/push/vipiu'
    data = {
        "token": token,
        "channel": "wechat",
        "title": "📡 WebHostMost 虚拟主机签到",
        "description": "GitHub 自动签到推送",
        "content": message
    }

    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f'发送消息失败: {response.text}')
    except Exception as e:
        print(f'发送消息时出错: {e}')

async def main() -> None:
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    url = 'https://client.webhostmost.com/login'
    token = os.getenv('TOKEN')
    now = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
    
    is_logged_in = await login(url, email, password)
    
    if is_logged_in:
        message = f"""
🎉 **签到成功**

📧 **账号**: {email}
⏰ **时间**: {now}
🌏 **时区**: 北京时间 (UTC+8)
✅ **状态**: 登录成功

---
*WebHostMost 虚拟主机自动签到完成*
        """.strip()
        print(f"账号于北京时间{now}登录成功！")
    else:
        message = f"""
❌ **签到失败**

📧 **账号**: {email}
⏰ **时间**: {now}
🌏 **时区**: 北京时间 (UTC+8)
⚠️ **状态**: 登录失败

💡 **建议**: 请检查账号和密码是否正确

---
*WebHostMost 虚拟主机自动签到失败*
        """.strip()
        print(f"账号登录失败，请检查账号和密码是否正确。")

    await send_notification(token, message)

if __name__ == "__main__":
    asyncio.run(main())

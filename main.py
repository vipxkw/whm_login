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

async def send_telegram_message(message: str, telegram_bot_token: str, telegram_chat_id: str) -> None:
     msg = f"""
🎯 webhostmost自动化保号脚本运行报告

🕰 *北京时间*: {datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}

⏰ *UTC时间*: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}

📝 *任务报告*:

{message}

     """
     url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'
     payload = {
         'chat_id': telegram_chat_id,
         'text': msg,
         'parse_mode': 'Markdown',
     }
     headers = {'Content-Type': 'application/json'}

     try:
         response = requests.post(url, json=payload, headers=headers)
         if response.status_code != 200:
             print(f'发送消息到Telegram失败: {response.text}')
     except Exception as e:
         print(f'发送消息到Telegram时出错: {e}')

async def main() -> None:
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    url = 'https://client.webhostmost.com/login'
    message = ''
    telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    now = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
    is_logged_in = await login(url, email, password)
    if is_logged_in:
        message += f'✅账号 *{email}* 于北京时间{now}登录成功！\n\n'
        print(f"账号于北京时间{now}登录成功！")
    else:
        message += f'❌账号 *{email}* 于北京时间{now}登录失败！\n\n'
        print(f"账号登录失败，请检查账号和密码是否正确。")

    await send_telegram_message(message, telegram_bot_token, telegram_chat_id)


if __name__ == "__main__":
    asyncio.run(main())

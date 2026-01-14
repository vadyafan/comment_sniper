import os.path
import base64
import re
from loguru import logger
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

# Права: только чтение почты (безопасно)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json' # Тут сохраним сессию, чтобы не логиниться каждый раз

class GmailService:
    def __init__(self):
        self.creds = self._authenticate()
        self.service = build('gmail', 'v1', credentials=self.creds)

    def _authenticate(self):
        """Проходит OAuth аутентификацию и сохраняет токен."""
        creds = None
        # 1. Если уже есть сохраненный токен — грузим его
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        # 2. Если токена нет или он протух — обновляем
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    # Если рефреш не сработал, удаляем и заново
                    if os.path.exists(TOKEN_FILE): os.remove(TOKEN_FILE)
                    return self._authenticate()
            else:
                # 3. Первый запуск: открываем браузер пользователю
                if not os.path.exists(CREDENTIALS_FILE):
                    logger.error(f"❌ File {CREDENTIALS_FILE} not found! Download it from Google Cloud.")
                    raise FileNotFoundError(f"Missing {CREDENTIALS_FILE}")
                
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Сохраняем токен для будущих запусков
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        return creds

    def check_for_linkedin_emails(self, lookback_hours=24):
        """
        Ищет письма от LinkedIn за последние X часов.
        Возвращает список найденных URL постов.
        """
        logger.info("📧 Checking Gmail for new alerts...")
        
        # Фильтр поиска: от LinkedIn, непрочитанные (можно убрать 'is:unread', если тестируешь на старых)
        # q = f'from:linkedin.com subject:"posted" newer_than:{lookback_hours}h'
        # Для тестов давай искать вообще всё от LinkedIn со словом post
        q = 'from:linkedin.com "posted" newer_than:1d' 

        try:
            results = self.service.users().messages().list(userId='me', q=q).execute()
            messages = results.get('messages', [])
            
            found_urls = []
            
            if not messages:
                logger.info("📭 No new LinkedIn emails found.")
                return []

            logger.info(f"📨 Found {len(messages)} emails. Parsing...")

            for msg in messages:
                # Получаем детали письма
                msg_data = self.service.users().messages().get(userId='me', id=msg['id']).execute()
                payload = msg_data['payload']
                snippet = msg_data.get('snippet', '')
                
                # Ищем тело письма (HTML)
                body_data = ""
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/html':
                            body_data = part['body']['data']
                            break
                elif payload.get('body', {}).get('data'): # Если письмо без частей
                    body_data = payload['body']['data']

                if not body_data:
                    continue

                # Декодируем base64
                html_content = base64.urlsafe_b64decode(body_data).decode('utf-8')
                
                # Парсим ссылку на пост
                link = self._extract_post_link(html_content)
                if link:
                    # Чистим ссылку от трекинга
                    clean_link = link.split('?')[0]
                    found_urls.append(clean_link)
                    logger.success(f"🔗 Found Post Link: {clean_link}")
                else:
                    logger.warning(f"⚠️ Could not extract link from email: {snippet[:50]}...")

            return list(set(found_urls)) # Убираем дубликаты

        except Exception as e:
            logger.error(f"❌ Gmail Error: {e}")
            return []

    def _extract_post_link(self, html):
        """Парсит HTML письма и ищет кнопку 'View post' или ссылку на activity."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # LinkedIn ссылки в письмах обычно длинные и страшные, но ведут на linkedin.com/comm/
        # Ищем все ссылки
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Фильтруем именно ссылки на посты/активность
            if "linkedin.com/comm/feed/update" in href or "linkedin.com/posts" in href:
                return href
            # Иногда ссылка спрятана в трекере
            if "linkedin.com/comm/linkedin/feed" in href:
                return href
                
        return None

# Singleton
gmail_service = GmailService()
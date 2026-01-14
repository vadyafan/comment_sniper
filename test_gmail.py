from app.services.gmail import gmail_service

def test():
    print("🚀 Starting Gmail Test...")
    # Первый запуск откроет браузер для логина
    urls = gmail_service.check_for_linkedin_emails()
    
    print(f"\n✅ Total URLs found: {len(urls)}")
    for url in urls:
        print(f" - {url}")

if __name__ == "__main__":
    test()
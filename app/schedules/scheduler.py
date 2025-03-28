# app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.crawl_data_products_service import crawl_data_product_from_tiki  # Đảm bảo đường dẫn này đúng

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(crawl_data_product_from_tiki, 'cron', hour=0, minute=1)
    scheduler.start()
    print("Senior Dev Log: APScheduler đã được khởi động.")

def stop_scheduler():
    scheduler.shutdown()
    print("Senior Dev Log: APScheduler đã dừng.")
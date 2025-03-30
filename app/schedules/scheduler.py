from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.crawl_data_products_service import crawl_data_product_from_tiki
from app.utils.database import get_database  # Import get_database

scheduler = AsyncIOScheduler()

async def run_crawl_job():
    db = await get_database()
    await crawl_data_product_from_tiki(db)

def start_scheduler():
    scheduler.add_job(run_crawl_job, 'cron', hour=0, minute=1)
    scheduler.start()
    print("Senior Dev Log: AsyncIOScheduler đã được khởi động.")

def stop_scheduler():
    scheduler.shutdown()
    print("Senior Dev Log: AsyncIOScheduler đã dừng.")
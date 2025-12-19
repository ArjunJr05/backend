import asyncio
from app.core.queue_manager import process_queue
from app.config import QUEUE_CHECK_INTERVAL

worker_task = None

async def start_worker():
    global worker_task
    worker_task = asyncio.create_task(run_worker())
    return worker_task

async def run_worker():
    while True:
        try:
            await process_queue()
        except Exception as e:
            print(f"Error in background worker: {e}")
        
        await asyncio.sleep(QUEUE_CHECK_INTERVAL)

async def stop_worker():
    global worker_task
    if worker_task:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

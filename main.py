from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_client import disable_created_metrics, make_asgi_app


from app.jobs import file_cleanup
from app.jobs import camera_sync
from app.utils import constants

app = FastAPI()

# Prometheus metrics
disable_created_metrics()
metrics_app = make_asgi_app()

app.mount("/metrics", metrics_app)

# Scheduler
scheduler = BackgroundScheduler()

# Start background jobs using APScheduler
scheduler.add_job(camera_sync.run, 'interval', seconds=constants.SYNC_INTERVAL_SECONDS)  # Sync every 30 seconds
scheduler.add_job(file_cleanup.run, 'cron', hour=constants.DATA_CLEANUP_HOUR)  # Cleanup every 30 minutes
scheduler.start()

# Ensure scheduler stops on shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    scheduler.shutdown()

if __name__ == "__main__":
    import uvicorn
    import uvicorn.config

    uvicorn.config.LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    uvicorn.config.LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
    uvicorn.config.LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    uvicorn.config.LOGGING_CONFIG["loggers"]["app"] = {
        'handlers': ['default'],
        'level': 'DEBUG',
        'propagate': False
    }

    uvicorn.run(app, host=constants.LISTEN_ADDRESS, port=constants.LISTEN_PORT)

import asyncio
import logging
import sys
import os

# Set logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(os.getcwd())

async def main():
    try:
        from src.data.storage import DataStorage, get_storage
        from src.agents.event_calendar import EventCalendar

        logger.info("1. Initializing Storage...")
        storage = get_storage("./debug_data.db") # Use separate DB for debug
        await storage.initialize()
        logger.info("Storage initialized.")

        try:
            # Check if EconomicEvent exists
            from src.data.storage import EconomicEvent
            logger.info("EconomicEvent model confirmed.")
        except ImportError:
            logger.error("EconomicEvent model NOT found in storage.py")
            return

        logger.info("2. Initializing EventCalendar...")
        calendar = EventCalendar()
        
        logger.info("3. Testing get_calendar_v2...")
        try:
            res = await calendar.get_calendar_v2(
                start_date="2024-01-01", 
                end_date="2024-01-31", 
                storage=storage
            )
            logger.info(f"get_calendar_v2 Success! Events count: {res['total_events']}")
            logger.info(f"Sample Event: {res['events'][0] if res['events'] else 'None'}")
        except AttributeError:
             logger.error("EventCalendar has no attribute 'get_calendar_v2'")
        except Exception as e:
            logger.error(f"get_calendar_v2 Failed: {e}", exc_info=True)

    except ImportError as e:
        logger.error(f"Import Error: {e}")
    except Exception as e:
        logger.error(f"General Error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())

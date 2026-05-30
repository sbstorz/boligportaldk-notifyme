import time
from datetime import datetime

from notifier import TelegramNotifier
from scraper import BoligScraper


def main():
    scraper = BoligScraper('config/config.yaml')
    notifier = TelegramNotifier()

    # test
    print(f"Starting monitoring of {scraper.config['search_url']}")
    print(f"Will check every {scraper.config['check_interval']} seconds")

    try:
        while True:
            print(f"\n{'=' * 50}")
            print(f"Checking for new listings at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'=' * 50}")

            new_listings = scraper.get_new_listings()

            if new_listings:
                print(f"\nFound {len(new_listings)} new listings!")
                for listing in new_listings:
                    print("\nNew listing found:")
                    print(f"Rooms: {listing['rooms']} ({listing['size']} m²)")
                    print(f"Location: {listing['city']}, {listing['street']}")
                    print(f"Price: {listing['price']}")
                    print(f"Listed: {listing['listing_age']}")
                    print(f"URL: {listing['url']}")

                    # Send Telegram notification
                    if notifier.send_notification(listing):
                        print("✅ Telegram notification sent")
                    else:
                        print("❌ Failed to send Telegram notification")

                    print("-" * 50)
            else:
                print("\nNo new listings found in this check")

            print(f"\nWaiting {scraper.config['check_interval']} seconds before next check...")
            time.sleep(scraper.config['check_interval'])

    except KeyboardInterrupt:
        print("\nStopping the monitor...")
    except Exception as e:
        print(f"\nError in main loop: {str(e)}")


if __name__ == "__main__":
    main()
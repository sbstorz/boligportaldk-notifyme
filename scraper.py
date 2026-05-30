import yaml
from datetime import datetime
from typing import List, Dict

import requests
from bs4 import BeautifulSoup


class BoligScraper:
    def __init__(self, config_path: str):
        self.listings_cache_file = "seen_listings.txt"
        self.config = self._load_config(config_path)
        self.seen_listings = self._load_seen_listings()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def _load_config(self, config_path: str) -> Dict:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _load_seen_listings(self) -> set:
        try:
            with open(self.listings_cache_file, 'r') as f:
                return set(line.strip() for line in f)
        except FileNotFoundError:
            return set()

    def _save_seen_listings(self):
        with open(self.listings_cache_file, 'w') as f:
            for listing_id in self.seen_listings:
                f.write(f"{listing_id}\n")

    def _extract_listing_id(self, url: str) -> str:
        """Extract the listing ID from the URL."""
        if 'id-' in url:
            return url.split('id-')[-1].split('/')[0]
        return url  # fallback to full URL if ID not found

    def _extract_address(self, address_elem) -> tuple:
        """Extract city and street from address element."""
        if not address_elem:
            return None, None

        text = address_elem.get_text(strip=True)
        parts = text.split(',', 1)
        city = parts[0].strip() if parts else None
        street = parts[1].strip() if len(parts) > 1 else None
        return city, street

    def _extract_size_and_rooms(self, title_elem) -> tuple:
        """Extract size and number of rooms from title element."""
        if not title_elem:
            return None, None

        text = title_elem.get_text(strip=True)
        try:
            rooms = text.split('rm.')[0].strip()
            size = text.split('of')[1].split('m²')[0].strip()
            return rooms, size
        except:
            return None, None

    def get_new_listings(self) -> List[Dict]:
        try:
            print(f"\nFetching listings from: {self.config['search_url']}")
            response = requests.get(self.config['search_url'], headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            new_listings = []

            # Find all listing cards using the specific class
            listing_cards = soup.find_all("a", class_="AdCardSrp__Link")

            for card in listing_cards:
                try:
                    # Get the listing URL
                    listing_url = card.get('href')
                    if not listing_url:
                        continue

                    if not listing_url.startswith('http'):
                        listing_url = f"https://www.boligportal.dk{listing_url}"

                    listing_id = self._extract_listing_id(listing_url)

                    if listing_id not in self.seen_listings:
                        # Extract title information
                        title_elem = card.select_one("span.css-a76tvl")
                        rooms, size = self._extract_size_and_rooms(title_elem)

                        # Extract address
                        address_elem = card.select_one("span.css-avmlqd")
                        city, street = self._extract_address(address_elem)

                        # Extract price
                        price_elem = card.select_one("span.css-dlcfcd")
                        price = price_elem.get_text(strip=True) if price_elem else "Price not found"

                        # Extract image URL
                        img_elem = card.select_one("img.css-1yrtl0o")
                        image_url = img_elem.get('src') if img_elem else None

                        # Extract listing age
                        age_elem = card.select_one("span.css-14yggbm")
                        listing_age = age_elem.get_text(strip=True) if age_elem else None

                        details = {
                            'url': listing_url,
                            'id': listing_id,
                            'rooms': rooms,
                            'size': size,
                            'city': city,
                            'street': street,
                            'price': price,
                            'image_url': image_url,
                            'listing_age': listing_age,
                            'found_at': datetime.now().isoformat()
                        }


                        # Only include listings that are 0 to 5 minutes old
                        if listing_age and "minute" in listing_age:
                            try:
                                minutes = int(listing_age.split()[0])
                                if 0 <= minutes <= 5:
                                    new_listings.append(details)
                                    self.seen_listings.add(listing_id)
                            except ValueError:
                                pass  # skip if parsing fails

                except Exception as e:
                    print(f"Error processing card: {str(e)}")
                    continue

            if new_listings:
                self._save_seen_listings()
                print(f"Found {len(new_listings)} new listings")
            else:
                print("No new listings found")

            return new_listings

        except Exception as e:
            print(f"Error fetching listings: {str(e)}")
            return []

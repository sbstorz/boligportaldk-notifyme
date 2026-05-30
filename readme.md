**FORK**

Please find the original README [here](https://github.com/francescaboe/boligportaldk-notifyme)

# Boligportal Notifier Bot

An automated scraper that monitors boligportal.dk for new rental listings and sends notifications via Telegram.

## Features

- Monitors moligportal.dk search results in real-time
- Detects new listings automatically
- Sends instant Telegram notifications with listing details
- Maintains history of seen listings to avoid duplicates
- Configurable search parameters and check intervals

## Project Structure
```
boligportaldk-notifyme/
    ├── config/         
    │   └── config.json     # configuration file
    ├── Dockerfile          # Docker image for cloud deployment
    ├── main.py             # Main script that runs the monitoring loop
    ├── notifier.py         # Telegram notifier
    ├── requirements.txt    # python dependencies
    └── scraper.py          # Handles the scraping of Boligportal listings
```

## Setup


1. Obtain the Telegram bot API token and Chat ID for instant notifications.
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

- Text the @BotFather to set up a new bot
- Start a conversation with the bot in a private message
- With the new API token, access the `https://api.telegram.org/bot<token>/getUpdates` URL in a web browser and find the *result[0].message.chat.id* 

2. Configure `config/config.yaml` to your liking:
- `search_url`: The Boligportal.dk search URL to monitor.
    For optimal results, apply filters from the website and then copy the resulting URL.
    For location filters, go to the map view, zoom in to the area of your liking, copy the resulting URL and remove the `&view=map` parameter.
    > [!IMPORTANT]
    > The scraper works ONLY with results! 
    > Ensure that the URL looks like this: `https://www.boligportal.dk/en/...`
- `check_interval`: Time between checks in seconds

## Installation and Usage with Docker
1. Clone the repository:
```bash
git clone https://github.com/yourusername/boligportaldk-notifyme.git
```

and `cd` into it.

2. Build the Docker image:
```bash
docker build -t "boligportal-scraper" .
```

**OPTION 1** Plain Docker

3. Run the container:
```bash
docker run -e TELEGRAM_BOT_TOKEN=<token> -e TELEGRAM_CHAT_ID=<chat_id> boligportal-scraper:latest
```

**OPTION 2** Docker Compose

3. In a directory of your choice, create a compose file:
```yaml
services:
  boligportal-notifier:
    restart: unless-stopped
    image: boligportal-notifyme:latest
    volumes:
      - ./data:/app/config
    tty: true
    environment:
      - TELEGRAM_BOT_TOKEN=<token>
      - TELEGRAM_CHAT_ID=<chat_id>
networks: {}
```

4. Create the *./data* directory and copy the *config/config.yaml* file there
5. Bring the stack up with 
```bash
docker compose up
```

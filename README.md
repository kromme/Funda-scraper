# Scraping Funda
**This script is already a few years old, dependencies (like XPATHs) might have changed**

Some years ago I was looking to buy my first house. It was not an easy task to find a house in Utrecht,
housing prices are going through the roof and quite some houses are already sold before the're
added on Funda. Key is being early!  

That is why I wrote this script, so I could call the real estate agent first! And with success.
Using this script I found and bought my first house.  

## Installation
This script is a stand alone script, aside from the dependencies there is no need to install the scraper.  
Dependencies:  
* selenium (3.4.0)  
* Firefox (59.02)  
* geckodriver (0.20)  
* pandas  
* telegram  

## Usage
The usage of this script is quite straightforward, but you'll need to setup Telegram first. Take a look at: https://core.telegram.org/bots/. Note the `telegram_token` and the `telegram_chat_id`.   

Next step is deciding what and which kind of house you're looking for. Go to Funda, set the location, define the filters and copy the into the `funda_url`-parameter. 

```
sf = FundaScraper(funda_url = '',
                telegram_token = '',
                telegram_chat_id = '',
)

sf.run()
```

## Counter bot-blocks
Sometimes Funda (or other site you want to scrape) find out you're using a bot and they'll block you. Here we're using two things to counter their blocks.  

### User Agent
First we're changing the user agent of your browser.
The user agent says to the site which browser and OS you're using, but we can change this. 
When getting blocked, we're changing it to another heavy used agent.  

### Proxies
The next thing we're doing is changing the actual url we're accessing the site from. https://www.sslproxies.org/ has a list of proxies, we're simply looping through the list until we've found a proxy which is accepted by Funda.

*Note: that this script and the scraped data are not used commercially.*
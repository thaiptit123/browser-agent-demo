from browser_use import Agent, ChatOllama
from browser_use.browser.browser import Browser, BrowserConfig

browser = Browser(config=BrowserConfig(allowed_domains=["quotes.toscrape.com"]))
print("BrowserConfig allowed_domains is valid!")

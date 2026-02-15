"""
Skill 1: 社媒B端客户智能挖掘

功能：
- 调用第三方数据服务API获取B端客户信息
- 支持关键词/类目/话题定向
- 自动去重和过滤
"""
import asyncio
from typing import Dict, Any, List, Optional
import httpx
from datetime import datetime

from app.core.skill_base import BaseSkill, SkillStatus, register_skill
from app.core.context import ExecutionContext
from app.config import settings


@register_skill
class SocialScraperSkill(BaseSkill):
    """
    社媒数据挖掘Skill

    从第三方数据服务获取社媒用户信息
    """
    name = "social_scraper"
    display_name = "Social Media Scraper"
    description = "挖掘社媒B端客户信息，支持TikTok、Instagram等平台"
    category = "data"
    version = "1.0.0"

    config_schema = {
        "type": "object",
        "properties": {
            "data_provider": {
                "type": "string",
                "enum": ["apify", "bright_data", "zyte", "mock"],
                "description": "数据服务提供商"
            },
            "max_retries": {
                "type": "integer",
                "default": 3,
                "description": "最大重试次数"
            },
            "request_delay": {
                "type": "number",
                "default": 1.0,
                "description": "请求延迟（秒）"
            }
        }
    }

    default_config = {
        "data_provider": "mock",  # 默认使用mock，生产环境需配置真实API
        "max_retries": 3,
        "request_delay": 1.0
    }

    input_schema = {
        "type": "object",
        "required": [],
        "properties": {
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "搜索关键词"
            },
            "platforms": {
                "type": "array",
                "items": {"type": "string"},
                "enum": ["tiktok", "instagram", "youtube", "facebook"],
                "description": "目标平台"
            },
            "countries": {
                "type": "array",
                "items": {"type": "string"},
                "description": "目标国家（ISO代码）"
            },
            "min_followers": {
                "type": "integer",
                "default": 10000,
                "description": "最小粉丝数"
            },
            "limit": {
                "type": "integer",
                "default": 100,
                "description": "返回数量上限"
            },
            "account_types": {
                "type": "array",
                "items": {"type": "string"},
                "enum": ["creator", "brand", "mcn", "retailer"],
                "description": "账号类型筛选"
            }
        }
    }

    output_schema = {
        "type": "object",
        "required": ["customers", "total"],
        "properties": {
            "customers": {
                "type": "array",
                "description": "客户列表"
            },
            "total": {
                "type": "integer",
                "description": "总数"
            },
            "duplicates_removed": {
                "type": "integer",
                "description": "去重数量"
            },
            "filtered": {
                "type": "integer",
                "description": "被过滤的数量"
            }
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def _close_client(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute the social scraping skill

        Args:
            context: Execution context with input data

        Returns:
            Dict containing scraped customer data
        """
        input_data = context.input_data

        # Extract parameters
        keywords = input_data.get("keywords", [])
        platforms = input_data.get("platforms", ["tiktok", "instagram"])
        countries = input_data.get("countries", [])
        min_followers = input_data.get("min_followers", 10000)
        limit = input_data.get("limit", 100)
        account_types = input_data.get("account_types", [])

        provider = self.config.get("data_provider", "mock")
        max_retries = self.config.get("max_retries", 3)
        request_delay = self.config.get("request_delay", 1.0)

        # Track metrics
        context.increment_metric("requests_sent")
        context.set_state("scrape_params", {
            "keywords": keywords,
            "platforms": platforms,
            "countries": countries,
            "min_followers": min_followers,
            "limit": limit
        })

        # Fetch data from provider
        all_customers = []
        duplicates_count = 0
        filtered_count = 0

        # Process each keyword and platform combination
        for platform in platforms:
            for keyword in keywords:
                try:
                    if provider == "apify":
                        customers = await self._fetch_from_apify(
                            platform, keyword, countries, min_followers, limit
                        )
                    elif provider == "bright_data":
                        customers = await self._fetch_from_bright_data(
                            platform, keyword, countries, min_followers, limit
                        )
                    else:
                        # Mock data for testing
                        customers = await self._fetch_mock(
                            platform, keyword, countries, min_followers, limit
                        )

                    # Apply filters
                    filtered_customers = self._apply_filters(
                        customers, account_types, min_followers, countries
                    )
                    filtered_count += len(customers) - len(filtered_customers)

                    # Deduplicate
                    new_customers, duplicates = self._deduplicate(
                        all_customers, filtered_customers
                    )
                    all_customers.extend(new_customers)
                    duplicates_count += duplicates

                    # Request delay
                    await asyncio.sleep(request_delay)

                except Exception as e:
                    context.increment_metric("errors")
                    if settings.DEBUG:
                        raise
                    continue

        await self._close_client()

        # Limit results
        if len(all_customers) > limit:
            all_customers = all_customers[:limit]

        # Update metrics
        context.set_output("customers_count", len(all_customers))
        context.set_output("duplicates_removed", duplicates_count)
        context.set_output("filtered_count", filtered_count)

        context.increment_metric("customers_found", len(all_customers))

        return {
            "customers": all_customers,
            "total": len(all_customers),
            "duplicates_removed": duplicates_count,
            "filtered": filtered_count
        }

    async def _fetch_from_apify(
        self,
        platform: str,
        keyword: str,
        countries: List[str],
        min_followers: int,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """
        Fetch data from Apify

        Args:
            platform: Target platform
            keyword: Search keyword
            countries: Target countries
            min_followers: Minimum follower count
            limit: Result limit

        Returns:
            List of customer data
        """
        api_key = settings.APIFY_API_KEY
        if not api_key:
            raise ValueError("APIFY_API_KEY not configured")

        # Apify Actor IDs for different platforms
        actor_ids = {
            "tiktok": "clockworks/free-tiktok-scraper",
            "instagram": "apify/instagram-scraper",
            "youtube": "apify/youtube-scraper"
        }

        actor_id = actor_ids.get(platform)
        if not actor_id:
            return []

        client = await self._get_client()

        # Build input for the actor
        actor_input = {
            "usernames": [],
            "hashtags": [f"#{keyword}"],
            "maxItems": limit,
            "resultsPerPage": min(limit, 50)
        }

        # Run the actor
        response = await client.post(
            f"https://api.apify.com/v2/acts/{actor_id}/runs",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"input": actor_input}
        )
        response.raise_for_status()

        run_id = response.json()["data"]["id"]

        # Wait for completion
        while True:
            response = await client.get(
                f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            run_data = response.json()["data"]
            status = run_data.get("status")

            if status in ["SUCCEEDED", "FAILED", "ABORTED"]:
                break
            await asyncio.sleep(2)

        # Get results
        if status != "SUCCEEDED":
            return []

        response = await client.get(
            f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}/dataset/items",
            headers={"Authorization": f"Bearer {api_key}"}
        )

        items = response.json()
        return self._normalize_apify_data(items, platform)

    def _normalize_apify_data(self, items: List[Dict], platform: str) -> List[Dict[str, Any]]:
        """Normalize Apify data to standard format"""
        normalized = []

        for item in items:
            try:
                if platform == "tiktok":
                    normalized.append({
                        "username": item.get("username"),
                        "platform": "tiktok",
                        "follower_count": item.get("stats", {}).get("followerCount", 0),
                        "verified": item.get("verified", False),
                        "bio": item.get("bio"),
                        "country": self._extract_country(item.get("bio", "")),
                        "profile_url": item.get("webVideoUrl"),
                        "avatar": item.get("avatarThumb"),
                        "account_type": self._guess_account_type(item),
                        "raw_data": item
                    })
                elif platform == "instagram":
                    normalized.append({
                        "username": item.get("username"),
                        "platform": "instagram",
                        "follower_count": item.get("followersCount", 0),
                        "verified": item.get("isVerified", False),
                        "bio": item.get("biography"),
                        "country": self._extract_country(item.get("biography", "")),
                        "profile_url": f"https://instagram.com/{item.get('username')}",
                        "avatar": item.get("profilePicUrl"),
                        "account_type": self._guess_account_type(item),
                        "raw_data": item
                    })
            except Exception:
                continue

        return normalized

    async def _fetch_from_bright_data(
        self,
        platform: str,
        keyword: str,
        countries: List[str],
        min_followers: int,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Fetch data from Bright Data (placeholder)"""
        # Implement Bright Data API integration
        return []

    async def _fetch_mock(
        self,
        platform: str,
        keyword: str,
        countries: List[str],
        min_followers: int,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Fetch mock data for testing"""
        mock_data = []

        # Generate some mock data
        for i in range(min(limit, 10)):
            mock_data.append({
                "username": f"@{keyword}_user_{i}",
                "platform": platform,
                "follower_count": min_followers + (i * 5000),
                "verified": i % 3 == 0,
                "bio": f"Passionate about {keyword}. Based in {countries[0] if countries else 'US'}.",
                "country": countries[0] if countries else "US",
                "profile_url": f"https://{platform}.com/{keyword}_user_{i}",
                "avatar": f"https://example.com/avatar_{i}.jpg",
                "account_type": ["creator", "brand", "mcn", "retailer"][i % 4],
                "email": f"contact@{keyword}_user_{i}.com",
                "whatsapp": f"+1{2000000000 + i}",
                "raw_data": {}
            })

        return mock_data

    def _apply_filters(
        self,
        customers: List[Dict[str, Any]],
        account_types: List[str],
        min_followers: int,
        countries: List[str],
    ) -> List[Dict[str, Any]]:
        """Apply filters to customer list"""
        filtered = []

        for customer in customers:
            # Filter by account type
            if account_types and customer.get("account_type") not in account_types:
                continue

            # Filter by follower count
            if customer.get("follower_count", 0) < min_followers:
                continue

            # Filter by country
            if countries and customer.get("country") not in countries:
                continue

            filtered.append(customer)

        return filtered

    def _deduplicate(
        self,
        existing: List[Dict[str, Any]],
        new: List[Dict[str, Any]],
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Deduplicate customer lists

        Returns:
            Tuple of (new_unique_customers, duplicate_count)
        """
        existing_keys = {
            (c.get("username"), c.get("platform")) for c in existing
        }

        new_unique = []
        duplicate_count = 0

        for customer in new:
            key = (customer.get("username"), customer.get("platform"))
            if key not in existing_keys:
                new_unique.append(customer)
                existing_keys.add(key)
            else:
                duplicate_count += 1

        return new_unique, duplicate_count

    def _extract_country(self, text: str) -> Optional[str]:
        """Extract country from bio/text"""
        # Simple country extraction - can be enhanced with NLP
        country_map = {
            "us": "US",
            "usa": "US",
            "uk": "UK",
            "gb": "UK",
            "germany": "DE",
            "france": "FR",
            "italy": "IT",
            "spain": "ES",
            "canada": "CA",
            "australia": "AU",
            "japan": "JP",
            "korea": "KR",
            "india": "IN",
            "brazil": "BR",
            "mexico": "MX",
            "uae": "AE",
            "china": "CN",
            "russia": "RU"
        }

        text_lower = text.lower()
        for country, code in country_map.items():
            if country in text_lower:
                return code

        return None

    def _guess_account_type(self, data: Dict[str, Any]) -> str:
        """Guess account type from profile data"""
        bio = data.get("bio", "").lower()
        username = data.get("username", "").lower()

        # Keywords for different account types
        brand_keywords = ["official", "brand", "store", "shop", "boutique"]
        mcn_keywords = ["media", "network", "management", "agency"]
        retailer_keywords = ["retail", "reseller", "wholesale", "distributor"]

        if any(k in bio or k in username for k in brand_keywords):
            return "brand"
        elif any(k in bio or k in username for k in mcn_keywords):
            return "mcn"
        elif any(k in bio or k in username for k in retailer_keywords):
            return "retailer"
        else:
            return "creator"

"""
Skill 2: 数据自动清洗与结构化

功能：
- 去重、格式统一、空值处理
- 自动打标签（客户类型、意向等级等）
- 输出标准化Excel
"""
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import re

from app.core.skill_base import BaseSkill, register_skill
from app.core.context import ExecutionContext
from app.config import settings


@register_skill
class DataCleanerSkill(BaseSkill):
    """
    数据清洗Skill

    清洗和标准化社媒客户数据
    """
    name = "data_cleaner"
    display_name = "Data Cleaner"
    description = "清洗和标准化社媒客户数据，自动打标签"
    category = "data"
    version = "1.0.0"

    config_schema = {
        "type": "object",
        "properties": {
            "output_format": {
                "type": "string",
                "enum": ["excel", "csv", "json"],
                "default": "excel"
            },
            "output_path": {
                "type": "string",
                "description": "输出文件路径"
            },
            "enable_deduplication": {
                "type": "boolean",
                "default": True
            },
            "enable_standardization": {
                "type": "boolean",
                "default": True
            },
            "enable_tagging": {
                "type": "boolean",
                "default": True
            }
        }
    }

    default_config = {
        "output_format": "excel",
        "output_path": None,  # Will use default if None
        "enable_deduplication": True,
        "enable_standardization": True,
        "enable_tagging": True
    }

    input_schema = {
        "type": "object",
        "required": ["customers"],
        "properties": {
            "customers": {
                "type": "array",
                "description": "原始客户数据"
            },
            "existing_customers": {
                "type": "array",
                "description": "已有客户数据（用于去重）"
            },
            "tagging_rules": {
                "type": "object",
                "description": "自定义打标签规则"
            }
        }
    }

    output_schema = {
        "type": "object",
        "required": ["cleaned_customers", "stats"],
        "properties": {
            "cleaned_customers": {
                "type": "array",
                "description": "清洗后的客户数据"
            },
            "stats": {
                "type": "object",
                "properties": {
                    "total": {"type": "integer"},
                    "duplicates_removed": {"type": "integer"},
                    "invalid_removed": {"type": "integer"},
                    "valid": {"type": "integer"},
                    "with_contact": {"type": "integer"}
                }
            },
            "output_file": {
                "type": "string",
                "description": "输出文件路径"
            }
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    def _get_output_path(self) -> str:
        """Get output file path"""
        if self.config.get("output_path"):
            return self.config["output_path"]

        # Use default export directory
        export_dir = settings.EXPORT_DIR
        os.makedirs(export_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(export_dir, f"customers_cleaned_{timestamp}.xlsx")

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute data cleaning

        Args:
            context: Execution context

        Returns:
            Dict containing cleaned data and statistics
        """
        input_data = context.input_data
        customers = input_data.get("customers", [])
        existing_customers = input_data.get("existing_customers", [])
        tagging_rules = input_data.get("tagging_rules", {})

        enable_deduplication = self.config.get("enable_deduplication", True)
        enable_standardization = self.config.get("enable_standardization", True)
        enable_tagging = self.config.get("enable_tagging", True)

        # Initial stats
        original_count = len(customers)
        duplicates_removed = 0
        invalid_removed = 0

        # Step 1: Remove invalid entries
        customers = self._remove_invalid(customers)
        invalid_removed = original_count - len(customers)

        # Step 2: Deduplicate
        if enable_deduplication:
            customers, duplicates_removed = self._deduplicate(
                customers, existing_customers
            )

        # Step 3: Standardize data
        if enable_standardization:
            customers = self._standardize(customers)

        # Step 4: Add tags
        if enable_tagging:
            customers = self._add_tags(customers, tagging_rules)

        # Step 5: Add metadata
        customers = self._add_metadata(customers)

        # Calculate stats
        valid_count = len(customers)
        with_contact = sum(1 for c in customers if c.get("email") or c.get("whatsapp"))

        stats = {
            "total": original_count,
            "duplicates_removed": duplicates_removed,
            "invalid_removed": invalid_removed,
            "valid": valid_count,
            "with_contact": with_contact,
            "without_contact": valid_count - with_contact
        }

        # Step 6: Export to file
        output_file = await self._export(customers)

        # Update context
        context.set_state("cleaning_stats", stats)
        context.increment_metric("customers_cleaned", valid_count)

        return {
            "cleaned_customers": customers,
            "stats": stats,
            "output_file": output_file
        }

    def _remove_invalid(self, customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove invalid customer entries"""
        valid = []

        for customer in customers:
            # Must have at least username or platform
            if not customer.get("username") and not customer.get("platform"):
                continue

            # Username should not be empty
            username = customer.get("username", "")
            if not username or len(username) < 2:
                continue

            valid.append(customer)

        return valid

    def _deduplicate(
        self,
        customers: List[Dict[str, Any]],
        existing_customers: List[Dict[str, Any]],
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Deduplicate customer list

        Returns:
            Tuple of (unique_customers, duplicate_count)
        """
        # Build key sets for existing customers
        existing_keys = {
            self._make_key(c) for c in existing_customers
        }

        unique = []
        duplicates = 0
        seen_keys = set()

        for customer in customers:
            key = self._make_key(customer)

            # Check if already in existing
            if key in existing_keys:
                duplicates += 1
                continue

            # Check if already seen in current batch
            if key in seen_keys:
                duplicates += 1
                continue

            unique.append(customer)
            seen_keys.add(key)

        return unique, duplicates

    def _make_key(self, customer: Dict[str, Any]) -> tuple:
        """Create a unique key for a customer"""
        username = customer.get("username", "").lower().strip("@")
        platform = customer.get("platform", "").lower()
        email = customer.get("email", "").lower()
        whatsapp = customer.get("whatsapp", "")

        # Priority: email > (username + platform) > whatsapp
        if email:
            return ("email", email)
        elif username and platform:
            return ("user_platform", username, platform)
        elif whatsapp:
            return ("whatsapp", whatsapp)

        return ("other", str(hash(str(customer))))

    def _standardize(self, customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Standardize customer data"""
        for customer in customers:
            # Standardize username (remove @, lowercase)
            username = customer.get("username", "")
            if username:
                customer["username"] = username.strip().lstrip("@").strip()

            # Standardize platform
            platform = customer.get("platform", "")
            if platform:
                customer["platform"] = platform.lower().strip()

            # Standardize country
            country = customer.get("country", "")
            if country:
                customer["country"] = self._standardize_country(country)

            # Standardize email
            email = customer.get("email", "")
            if email:
                customer["email"] = email.strip().lower()

            # Standardize WhatsApp
            whatsapp = customer.get("whatsapp", "")
            if whatsapp:
                customer["whatsapp"] = self._standardize_phone(whatsapp)

            # Standardize phone
            phone = customer.get("phone", "")
            if phone:
                customer["phone"] = self._standardize_phone(phone)

            # Standardize account type
            account_type = customer.get("account_type", "")
            if account_type:
                customer["account_type"] = account_type.lower().strip()

            # Ensure follower count is integer
            if "follower_count" in customer:
                try:
                    customer["follower_count"] = int(customer["follower_count"])
                except (ValueError, TypeError):
                    customer["follower_count"] = 0

            # Ensure verified is boolean
            if "verified" in customer:
                customer["verified"] = bool(customer["verified"])

        return customers

    def _standardize_country(self, country: str) -> Optional[str]:
        """Standardize country code"""
        if not country:
            return None

        country = country.upper().strip()

        # Direct mapping for common codes
        if len(country) == 2:
            return country

        # Map country names to codes
        country_map = {
            "UNITED STATES": "US",
            "USA": "US",
            "AMERICA": "US",
            "UNITED KINGDOM": "UK",
            "UK": "UK",
            "GREAT BRITAIN": "UK",
            "ENGLAND": "UK",
            "GERMANY": "DE",
            "FRANCE": "FR",
            "ITALY": "IT",
            "SPAIN": "ES",
            "CANADA": "CA",
            "AUSTRALIA": "AU",
            "JAPAN": "JP",
            "KOREA": "KR",
            "SOUTH KOREA": "KR",
            "INDIA": "IN",
            "BRAZIL": "BR",
            "MEXICO": "MX",
            "UNITED ARAB EMIRATES": "AE",
            "UAE": "AE",
            "CHINA": "CN",
            "RUSSIA": "RU",
            "NETHERLANDS": "NL",
            "BELGIUM": "BE",
            "SWITZERLAND": "CH",
            "SWEDEN": "SE",
            "NORWAY": "NO",
            "DENMARK": "DK",
            "POLAND": "PL",
            "CZECH": "CZ",
            "TURKEY": "TR",
            "ISRAEL": "IL",
            "SOUTH AFRICA": "ZA",
            "INDONESIA": "ID",
            "THAILAND": "TH",
            "VIETNAM": "VN",
            "PHILIPPINES": "PH",
            "MALAYSIA": "MY",
            "SINGAPORE": "SG",
            "HONG KONG": "HK",
            "TAIWAN": "TW",
            "NEW ZEALAND": "NZ",
            "ARGENTINA": "AR",
            "COLOMBIA": "CO",
            "CHILE": "CL",
            "PERU": "PE",
            "EGYPT": "EG",
            "NIGERIA": "NG",
            "KENYA": "KE"
        }

        return country_map.get(country, country)

    def _standardize_phone(self, phone: str) -> Optional[str]:
        """Standardize phone number"""
        if not phone:
            return None

        # Remove all non-digit characters
        digits = re.sub(r"[^\d+]", "", phone)

        # Add + if missing
        if not digits.startswith("+"):
            if digits.startswith("0"):
                # Remove leading 0 for international format
                digits = digits[1:]

        if len(digits) < 5:
            return None

        return digits

    def _add_tags(
        self,
        customers: List[Dict[str, Any]],
        custom_rules: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Add tags to customers based on rules"""
        for customer in customers:
            tags = []

            # Tag by follower count tier
            follower_count = customer.get("follower_count", 0)
            if follower_count >= 1000000:
                tags.append("mega_influencer")
            elif follower_count >= 100000:
                tags.append("macro_influencer")
            elif follower_count >= 10000:
                tags.append("micro_influencer")
            elif follower_count >= 1000:
                tags.append("nano_influencer")

            # Tag by account type
            account_type = customer.get("account_type", "")
            if account_type:
                tags.append(f"type_{account_type}")

            # Tag by verification status
            if customer.get("verified", False):
                tags.append("verified")

            # Tag by contact info availability
            if customer.get("email"):
                tags.append("has_email")
            if customer.get("whatsapp"):
                tags.append("has_whatsapp")

            # Tag by platform
            platform = customer.get("platform", "")
            if platform:
                tags.append(f"platform_{platform}")

            # Apply custom rules
            tags.extend(self._apply_custom_rules(customer, custom_rules))

            customer["tags"] = list(set(tags))  # Remove duplicates

        return customers

    def _apply_custom_rules(
        self,
        customer: Dict[str, Any],
        rules: Dict[str, Any],
    ) -> List[str]:
        """Apply custom tagging rules"""
        tags = []

        for rule_name, rule_config in rules.items():
            # Check condition
            condition = rule_config.get("condition", {})
            if self._evaluate_condition(customer, condition):
                tags.append(rule_config.get("tag", rule_name))

        return tags

    def _evaluate_condition(
        self,
        customer: Dict[str, Any],
        condition: Dict[str, Any],
    ) -> bool:
        """Evaluate a tagging condition"""
        field = condition.get("field")
        operator = condition.get("operator", "equals")
        value = condition.get("value")

        if not field:
            return False

        customer_value = customer.get(field)

        try:
            if operator == "equals":
                return str(customer_value).lower() == str(value).lower()
            elif operator == "not_equals":
                return str(customer_value).lower() != str(value).lower()
            elif operator == "contains":
                return value.lower() in str(customer_value).lower()
            elif operator == "not_contains":
                return value.lower() not in str(customer_value).lower()
            elif operator == "greater_than":
                return float(customer_value) > float(value)
            elif operator == "less_than":
                return float(customer_value) < float(value)
            elif operator == "in":
                return str(customer_value).lower() in [str(v).lower() for v in value]
            elif operator == "not_in":
                return str(customer_value).lower() not in [str(v).lower() for v in value]
        except (ValueError, TypeError):
            return False

        return False

    def _add_metadata(self, customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add metadata to customers"""
        timestamp = datetime.now().isoformat()

        for customer in customers:
            customer["imported_at"] = timestamp
            customer["import_source"] = "ai_agent"

            # Add initial intent level
            follower_count = customer.get("follower_count", 0)
            if follower_count >= 50000:
                customer["intent_level"] = "medium"
            else:
                customer["intent_level"] = "low"

        return customers

    async def _export(self, customers: List[Dict[str, Any]]) -> str:
        """Export customers to file"""
        output_format = self.config.get("output_format", "excel")
        output_path = self._get_output_path()

        # Standardized column mapping
        column_mapping = {
            "username": "Username",
            "platform": "Platform",
            "email": "Email",
            "whatsapp": "WhatsApp",
            "phone": "Phone",
            "country": "Country",
            "category": "Category",
            "subcategory": "Subcategory",
            "follower_count": "Follower Count",
            "account_type": "Account Type",
            "verified": "Verified",
            "website": "Website",
            "company_name": "Company",
            "job_title": "Job Title",
            "bio": "Bio",
            "tags": "Tags",
            "intent_level": "Intent Level",
            "imported_at": "Import Date"
        }

        # Create DataFrame
        df = pd.DataFrame(customers)

        # Rename columns
        df_renamed = df.rename(columns=column_mapping)

        # Select and order columns
        ordered_columns = [col for col in column_mapping.values() if col in df_renamed.columns]
        df_ordered = df_renamed[ordered_columns]

        # Export
        if output_format == "excel":
            df_ordered.to_excel(output_path, index=False, engine="openpyxl")
        elif output_format == "csv":
            output_path = output_path.replace(".xlsx", ".csv")
            df_ordered.to_csv(output_path, index=False)
        elif output_format == "json":
            output_path = output_path.replace(".xlsx", ".json")
            df_ordered.to_json(output_path, orient="records", indent=2)

        return output_file

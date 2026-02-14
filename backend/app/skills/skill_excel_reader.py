"""
Skill 3: Excel/在线表格读取

功能：
- 读取本地Excel或在线表格
- 自动识别表头
- 条件筛选
"""
import pandas as pd
import openpyxl
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import os
import re

from app.core.skill_base import BaseSkill, register_skill
from app.core.context import ExecutionContext
from app.config import settings


@register_skill
class ExcelReaderSkill(BaseSkill):
    """
    Excel读取Skill

    读取本地Excel或在线表格
    """
    name = "excel_reader"
    display_name = "Excel Reader"
    description = "读取Excel文件或在线表格，支持条件筛选"
    category = "data"
    version = "1.0.0"

    config_schema = {
        "type": "object",
        "properties": {
            "skip_empty_rows": {
                "type": "boolean",
                "default": True
            },
            "skip_empty_columns": {
                "type": "boolean",
                "default": True
            },
            "header_row": {
                "type": "integer",
                "default": 0,
                "description": "表头行号（从0开始）"
            }
        }
    }

    default_config = {
        "skip_empty_rows": True,
        "skip_empty_columns": True,
        "header_row": 0
    }

    input_schema = {
        "type": "object",
        "required": ["source"],
        "properties": {
            "source": {
                "type": "string",
                "enum": ["local", "google_sheets", "feishu", "dingtalk"],
                "description": "数据源类型"
            },
            "file_path": {
                "type": "string",
                "description": "本地文件路径"
            },
            "sheet_name": {
                "type": "string",
                "description": "工作表名称"
            },
            "sheet_index": {
                "type": "integer",
                "description": "工作表索引"
            },
            "range": {
                "type": "string",
                "description": "读取范围（如 A1:Z100）"
            },
            "url": {
                "type": "string",
                "description": "在线表格URL"
            },
            "spreadsheet_id": {
                "type": "string",
                "description": "Google Sheets ID"
            },
            "filters": {
                "type": "object",
                "description": "筛选条件"
            },
            "columns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "需要读取的列"
            }
        }
    }

    output_schema = {
        "type": "object",
        "required": ["customers", "count"],
        "properties": {
            "customers": {
                "type": "array",
                "description": "读取的客户数据"
            },
            "count": {
                "type": "integer",
                "description": "数据条数"
            },
            "columns": {
                "type": "array",
                "description": "读取的列"
            }
        }
    }

    # Column name mapping for different naming conventions
    COLUMN_ALIASES = {
        "username": ["username", "user", "name", "contact", "联系人", "姓名", "用户名", "账号"],
        "platform": ["platform", "社交平台", "平台"],
        "email": ["email", "mail", "邮箱", "电子邮箱"],
        "whatsapp": ["whatsapp", "wa", "whatapp", "what's app"],
        "phone": ["phone", "tel", "telephone", "mobile", "电话", "手机"],
        "country": ["country", "国家"],
        "category": ["category", "class", "class_name", "行业", "类目"],
        "subcategory": ["subcategory", "sub_category", "子类目"],
        "follower_count": ["follower_count", "followers", "粉丝数", "粉丝"],
        "account_type": ["account_type", "account", "账号类型", "类型"],
        "website": ["website", "site", "web", "url", "官网", "网站"],
        "company": ["company", "company_name", "firm", "公司", "公司名称"],
        "job_title": ["job_title", "title", "position", "职位", "头衔"],
        "bio": ["bio", "biography", "description", "简介", "描述"],
        "notes": ["notes", "note", "remark", "备注", "说明"]
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute Excel reading

        Args:
            context: Execution context

        Returns:
            Dict containing customer data
        """
        input_data = context.input_data
        source = input_data.get("source", "local")
        filters = input_data.get("filters", {})

        # Read data based on source
        if source == "local":
            df = await self._read_local(input_data)
        elif source == "google_sheets":
            df = await self._read_google_sheets(input_data)
        elif source == "feishu":
            df = await self._read_feishu(input_data)
        elif source == "dingtalk":
            df = await self._read_dingtalk(input_data)
        else:
            raise ValueError(f"Unsupported source: {source}")

        if df is None or df.empty:
            return {
                "customers": [],
                "count": 0,
                "columns": []
            }

        # Normalize column names
        df = self._normalize_columns(df)

        # Apply filters
        if filters:
            df = self._apply_filters(df, filters)

        # Select specific columns if requested
        columns_requested = input_data.get("columns")
        if columns_requested:
            # Map requested columns to normalized names
            mapped_columns = self._map_columns(df.columns, columns_requested)
            df = df[[col for col in mapped_columns if col in df.columns]]

        # Convert to list of dicts
        customers = df.to_dict("records")

        # Track metrics
        context.increment_metric("customers_read", len(customers))
        context.set_state("source_file", input_data.get("file_path") or input_data.get("url"))

        return {
            "customers": customers,
            "count": len(customers),
            "columns": list(df.columns)
        }

    async def _read_local(self, input_data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Read local Excel file"""
        file_path = input_data.get("file_path")
        if not file_path:
            raise ValueError("file_path is required for local source")

        # Handle relative paths
        if not os.path.isabs(file_path):
            upload_dir = settings.UPLOAD_DIR
            file_path = os.path.join(upload_dir, file_path)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        sheet_name = input_data.get("sheet_name")
        sheet_index = input_data.get("sheet_index")
        header_row = self.config.get("header_row", 0)

        try:
            if sheet_name:
                df = pd.read_excel(
                    file_path,
                    sheet_name=sheet_name,
                    header=header_row,
                    engine="openpyxl"
                )
            elif sheet_index is not None:
                df = pd.read_excel(
                    file_path,
                    sheet_name=sheet_index,
                    header=header_row,
                    engine="openpyxl"
                )
            else:
                # Read first sheet
                df = pd.read_excel(
                    file_path,
                    header=header_row,
                    engine="openpyxl"
                )

            return self._clean_dataframe(df)
        except Exception as e:
            raise RuntimeError(f"Failed to read Excel file: {str(e)}")

    async def _read_google_sheets(self, input_data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Read Google Sheets"""
        spreadsheet_id = input_data.get("spreadsheet_id")
        url = input_data.get("url")
        sheet_name = input_data.get("sheet_name")
        range_str = input_data.get("range")

        # Extract spreadsheet ID from URL if not provided
        if not spreadsheet_id and url:
            spreadsheet_id = self._extract_spreadsheet_id(url)

        if not spreadsheet_id:
            raise ValueError("Either spreadsheet_id or url is required for Google Sheets")

        try:
            # Import Google Sheets API
            from googleapiclient.discovery import build
            from google.oauth2 import service_account

            # Get credentials
            credentials_json = settings.GOOGLE_SHEETS_CREDENTIALS
            if not credentials_json:
                raise ValueError("GOOGLE_SHEETS_CREDENTIALS not configured")

            credentials = service_account.Credentials.from_service_account_file(
                credentials_json,
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
            )

            service = build("sheets", "v4", credentials=credentials)

            # Build range
            sheet_range = f"'{sheet_name}'!{range_str}" if range_str else sheet_name

            # Get values
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=sheet_range
            ).execute()

            values = result.get("values", [])
            if not values:
                return None

            # Convert to DataFrame
            header_row = self.config.get("header_row", 0)
            df = pd.DataFrame(values[header_row + 1:], columns=values[header_row])

            return self._clean_dataframe(df)

        except ImportError:
            # Fallback to CSV export URL
            if url:
                return await self._read_google_sheets_csv(url)
            raise RuntimeError("google-api-python-client not installed")

    async def _read_google_sheets_csv(self, url: str) -> Optional[pd.DataFrame]:
        """Read Google Sheets via CSV export"""
        csv_url = url.replace("/edit", "/export?format=csv")
        df = pd.read_csv(csv_url)
        return self._clean_dataframe(df)

    def _extract_spreadsheet_id(self, url: str) -> Optional[str]:
        """Extract spreadsheet ID from Google Sheets URL"""
        # Pattern: https://docs.google.com/spreadsheets/d/{id}/edit...
        pattern = r"/d/([a-zA-Z0-9-_]+)"
        match = re.search(pattern, url)
        return match.group(1) if match else None

    async def _read_feishu(self, input_data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Read Feishu (Lark) spreadsheet"""
        # Feishu API integration would go here
        # For now, return empty DataFrame
        return pd.DataFrame()

    async def _read_dingtalk(self, input_data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Read DingTalk spreadsheet"""
        # DingTalk API integration would go here
        # For now, return empty DataFrame
        return pd.DataFrame()

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame"""
        # Drop empty rows
        if self.config.get("skip_empty_rows", True):
            df = df.dropna(how="all")

        # Drop empty columns
        if self.config.get("skip_empty_columns", True):
            df = df.dropna(axis=1, how="all")

        # Reset index
        df = df.reset_index(drop=True)

        # Fill NaN with empty string
        df = df.fillna("")

        return df

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to standard names"""
        # Create mapping from actual column names to standard names
        column_mapping = {}

        for col in df.columns:
            col_lower = str(col).lower().strip()
            standard_name = self._map_column_name(col_lower)
            if standard_name:
                column_mapping[col] = standard_name

        # Rename columns
        if column_mapping:
            df = df.rename(columns=column_mapping)

        return df

    def _map_column_name(self, column: str) -> Optional[str]:
        """Map column name to standard name"""
        for standard_name, aliases in self.COLUMN_ALIASES.items():
            for alias in aliases:
                if alias.lower() in column:
                    return standard_name
        return None

    def _map_columns(self, existing_columns: List[str], requested: List[str]) -> List[str]:
        """Map requested columns to existing columns"""
        mapped = []
        for req in requested:
            for col in existing_columns:
                if req.lower() in col.lower():
                    mapped.append(col)
                    break
        return mapped

    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to DataFrame"""
        for field, condition in filters.items():
            if field not in df.columns:
                continue

            # Exact match
            if isinstance(condition, (str, int, float, bool)):
                df = df[df[field] == condition]

            # List of values (in)
            elif isinstance(condition, list):
                df = df[df[field].isin(condition)]

            # Dict with operator
            elif isinstance(condition, dict):
                operator = condition.get("operator", "equals")
                value = condition.get("value")

                if operator == "equals":
                    df = df[df[field] == value]
                elif operator == "not_equals":
                    df = df[df[field] != value]
                elif operator == "contains":
                    df = df[df[field].astype(str).str.contains(str(value), case=False, na=False)]
                elif operator == "not_contains":
                    df = df[~df[field].astype(str).str.contains(str(value), case=False, na=False)]
                elif operator == "greater_than":
                    df = df[pd.to_numeric(df[field], errors="coerce") > value]
                elif operator == "less_than":
                    df = df[pd.to_numeric(df[field], errors="coerce") < value]
                elif operator == "is_not_null":
                    df = df[df[field].notna() & (df[field] != "")]

        return df.reset_index(drop=True)

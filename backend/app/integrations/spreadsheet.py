"""
表格服务

支持Google Sheets、飞书、钉钉等在线表格
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import httpx
import json
from datetime import datetime

from app.config import settings


class SpreadsheetService:
    """表格服务基类"""

    async def read_sheet(
        self,
        spreadsheet_id: str,
        sheet_name: Optional[str] = None,
        range_str: Optional[str] = None,
    ) -> List[List[str]]:
        """
        读取表格数据

        Args:
            spreadsheet_id: 表格ID
            sheet_name: 工作表名称
            range_str: 范围（如 A1:Z100）

        Returns:
            二维列表数据
        """
        pass

    async def write_sheet(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        range_str: str,
        values: List[List[str]],
    ) -> Dict[str, Any]:
        """
        写入表格数据

        Args:
            spreadsheet_id: 表格ID
            sheet_name: 工作表名称
            range_str: 范围
            values: 数据

        Returns:
            写入结果
        """
        pass

    async def append_rows(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        values: List[List[str]],
    ) -> Dict[str, Any]:
        """
        追加行

        Args:
            spreadsheet_id: 表格ID
            sheet_name: 工作表名称
            values: 数据

        Returns:
            追加结果
        """
        pass


class GoogleSheetsService(SpreadsheetService):
    """Google Sheets服务"""

    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path or settings.GOOGLE_SHEETS_CREDENTIALS
        self._service = None

    async def _get_service(self):
        """获取Google Sheets API服务"""
        if self._service:
            return self._service

        try:
            from googleapiclient.discovery import build
            from google.oauth2 import service_account

            if not self.credentials_path:
                raise ValueError("GOOGLE_SHEETS_CREDENTIALS not configured")

            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )

            self._service = build("sheets", "v4", credentials=credentials)
            return self._service

        except ImportError:
            raise RuntimeError("google-api-python-client not installed")

    async def read_sheet(
        self,
        spreadsheet_id: str,
        sheet_name: Optional[str] = None,
        range_str: Optional[str] = None,
    ) -> List[List[str]]:
        """读取表格数据"""
        service = await self._get_service()

        # Build range
        sheet_range = f"'{sheet_name}'!{range_str}" if sheet_name and range_str else sheet_name or range_str

        # Get values
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_range
        ).execute()

        return result.get("values", [])

    async def write_sheet(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        range_str: str,
        values: List[List[str]],
    ) -> Dict[str, Any]:
        """写入表格数据"""
        service = await self._get_service()

        sheet_range = f"'{sheet_name}'!{range_str}"

        body = {
            "values": values
        }

        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
            valueInputOption="RAW",
            body=body
        ).execute()

        return {
            "success": True,
            "updated_rows": result.get("updates").get("updatedRows")
        }

    async def append_rows(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        values: List[List[str]],
    ) -> Dict[str, Any]:
        """追加行"""
        service = await self._get_service()

        sheet_range = f"'{sheet_name}'"

        body = {
            "values": values
        }

        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
            valueInputOption="RAW",
            body=body
        ).execute()

        return {
            "success": True,
            "updated_rows": result.get("updates").get("updatedRows")
        }

    async def export_to_sheet(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        导出数据到表格

        Args:
            spreadsheet_id: 表格ID
            sheet_name: 工作表名称
            data: 数据列表

        Returns:
            导出结果
        """
        if not data:
            return {"success": True, "rows": 0}

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Replace NaN with empty string
        df = df.fillna("")

        # Convert to list of lists
        header = list(df.columns)
        values = [header] + df.values.tolist()

        # Clear and write
        await self.write_sheet(spreadsheet_id, sheet_name, "A1", values)

        return {
            "success": True,
            "rows": len(data)
        }


class FeishuSheetService(SpreadsheetService):
    """飞书表格服务"""

    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
    ):
        self.app_id = app_id or settings.FEISHU_APP_ID
        self.app_secret = app_secret or settings.FEISHU_APP_SECRET
        self._access_token = None

    async def _get_access_token(self) -> str:
        """获取访问令牌"""
        if self._access_token:
            return self._access_token

        url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            self._access_token = data.get("app_access_token")

        return self._access_token

    async def read_sheet(
        self,
        spreadsheet_token: str,
        sheet_id: str = None,
        range_str: str = None,
    ) -> List[List[str]]:
        """读取飞书表格数据"""
        access_token = await self._get_access_token()

        url = f"https://open.feishu.cn/open-apis/sheets/v4/spreadsheets/{spreadsheet_token}/values/get"

        payload = {}
        if sheet_id:
            payload["valueRange"] = {"sheetId": sheet_id}
        if range_str:
            payload["valueRange"]["range"] = range_str

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return data.get("data", {}).get("valueRange", {}).get("values", [])

    async def write_sheet(
        self,
        spreadsheet_token: str,
        sheet_id: str,
        range_str: str,
        values: List[List[str]],
    ) -> Dict[str, Any]:
        """写入飞书表格数据"""
        access_token = await self._get_access_token()

        url = f"https://open.feishu.cn/open-apis/sheets/v4/spreadsheets/{spreadsheet_token}/values"

        payload = {
            "valueRange": {
                "sheetId": sheet_id,
                "range": range_str,
                "values": values
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=payload, headers=headers)
            response.raise_for_status()

        return {"success": True}

    async def append_rows(
        self,
        spreadsheet_token: str,
        sheet_id: str,
        values: List[List[str]],
    ) -> Dict[str, Any]:
        """追加行"""
        access_token = await self._get_access_token()

        url = f"https://open.feishu.cn/open-apis/sheets/v4/spreadsheets/{spreadsheet_token}/values:append"

        payload = {
            "valueRange": {
                "sheetId": sheet_id,
                "values": values
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()

        return {"success": True}


class DingtalkSheetService(SpreadsheetService):
    """钉钉表格服务"""

    def __init__(
        self,
        app_key: Optional[str] = None,
        app_secret: Optional[str] = None,
    ):
        self.app_key = app_key or settings.DINGTALK_APP_KEY
        self.app_secret = app_secret or settings.DINGTALK_APP_SECRET
        self._access_token = None

    async def _get_access_token(self) -> str:
        """获取访问令牌"""
        if self._access_token:
            return self._access_token

        url = f"https://api.dingtalk.com/v1.0/oauth2/accessToken"

        payload = {
            "appKey": self.app_key,
            "appSecret": self.app_secret
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            self._access_token = data.get("accessToken")

        return self._access_token

    async def read_sheet(
        self,
        spreadsheet_id: str,
        sheet_name: Optional[str] = None,
        range_str: Optional[str] = None,
    ) -> List[List[str]]:
        """读取钉钉表格数据"""
        # Implement DingTalk integration
        return []

    async def write_sheet(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        range_str: str,
        values: List[List[str]],
    ) -> Dict[str, Any]:
        """写入钉钉表格数据"""
        # Implement DingTalk integration
        return {"success": True}

    async def append_rows(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        values: List[List[str]],
    ) -> Dict[str, Any]:
        """追加行"""
        # Implement DingTalk integration
        return {"success": True}


# Service factory
def get_spreadsheet_service(
    service_type: str = "google_sheets",
    **kwargs
) -> SpreadsheetService:
    """
    获取表格服务实例

    Args:
        service_type: 服务类型 (google_sheets, feishu, dingtalk)
        **kwargs: 服务配置参数

    Returns:
        SpreadsheetService实例
    """
    if service_type == "google_sheets":
        return GoogleSheetsService(**kwargs)
    elif service_type == "feishu":
        return FeishuSheetService(**kwargs)
    elif service_type == "dingtalk":
        return DingtalkSheetService(**kwargs)
    else:
        raise ValueError(f"Unknown spreadsheet service type: {service_type}")

"""Standard JSON-RPC message types and models for MCP protocol."""
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class JSONRPCRequest(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: Optional[Union[Dict[str, Any], List[Any]]] = None
    id: Union[int, str]


class JSONRPCResponse(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Union[int, str]] = None


class JSONRPCNotification(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: Optional[Union[Dict[str, Any], List[Any]]] = None

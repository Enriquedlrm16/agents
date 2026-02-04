"""
MCP Client for DateTime Server
Provides functions to connect to the datetime MCP server and use its tools.
"""

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import List
from agents import FunctionTool
import json


async def list_datetime_tools():
    """
    Connect to the datetime MCP server and list available tools.
    
    Returns:
        List of Tool objects from the MCP server
    """
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "datetime_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            return tools.tools


async def get_datetime_tools_openai() -> List[FunctionTool]:
    """
    Get datetime tools in OpenAI Agents SDK format.
    
    Returns:
        List of FunctionTool objects compatible with OpenAI Agents
    """
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "datetime_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools from server
            response = await session.list_tools()
            tools = response.tools
            
            # Convert to OpenAI format
            openai_tools = []
            
            for tool in tools:
                # Create a wrapper function for each tool
                async def call_tool(session=session, tool_name=tool.name, **kwargs):
                    """Wrapper to call the MCP tool"""
                    result = await session.call_tool(tool_name, arguments=kwargs)
                    # Extract content from result
                    if hasattr(result, 'content') and len(result.content) > 0:
                        return result.content[0].text
                    return str(result)
                
                # Create FunctionTool
                function_tool = FunctionTool(
                    name=tool.name,
                    description=tool.description,
                    params_json_schema=tool.inputSchema,
                    on_invoke_tool=lambda **kwargs, tn=tool.name: call_tool(tool_name=tn, **kwargs),
                    strict_json_schema=True
                )
                
                openai_tools.append(function_tool)
            
            return openai_tools


async def call_datetime_tool(tool_name: str, arguments: dict = None):
    """
    Call a specific datetime tool directly.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Dictionary of arguments for the tool
    
    Returns:
        Result from the tool
    """
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "datetime_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            args = arguments or {}
            result = await session.call_tool(tool_name, arguments=args)
            
            # Extract text content
            if hasattr(result, 'content') and len(result.content) > 0:
                return result.content[0].text
            return str(result)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("🔧 Testing DateTime MCP Client\n")
        
        # List available tools
        print("📋 Available tools:")
        tools = await list_datetime_tools()
        for tool in tools:
            print(f"  • {tool.name}: {tool.description}")
        
        print("\n" + "="*60 + "\n")
        
        # Test each tool
        print("🧪 Testing tools:\n")
        
        date = await call_datetime_tool("get_current_date")
        print(f"📅 Current Date: {date}")
        
        time = await call_datetime_tool("get_current_time")
        print(f"⏰ Current Time: {time}")
        
        datetime_str = await call_datetime_tool("get_current_datetime")
        print(f"📆 Current DateTime: {datetime_str}")
        
        day = await call_datetime_tool("get_day_of_week")
        print(f"📌 Day of Week: {day}")
        
        timestamp = await call_datetime_tool("get_timestamp")
        print(f"⏱️  Unix Timestamp: {timestamp}")
        
        iso = await call_datetime_tool("get_iso_datetime")
        print(f"🔤 ISO DateTime: {iso}")
        
        ny_time = await call_datetime_tool(
            "get_datetime_in_timezone", 
            {"timezone": "America/New_York"}
        )
        print(f"🗽 New York Time: {ny_time}")
        
        tokyo_time = await call_datetime_tool(
            "get_datetime_in_timezone",
            {"timezone": "Asia/Tokyo"}
        )
        print(f"🗼 Tokyo Time: {tokyo_time}")
    
    asyncio.run(main())

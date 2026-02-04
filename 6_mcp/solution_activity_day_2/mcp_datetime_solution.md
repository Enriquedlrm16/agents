# 📅 Solución Completa: MCP Server para Fecha Actual

## 🎯 Ejercicio Propuesto

**Objetivo:** Crear un MCP Server que exponga una función para obtener la fecha actual, y que un agente pueda usar esta herramienta.

**Ejercicio Extra (Difícil):** Crear un MCP Client y usar una llamada nativa de OpenAI (sin Agents SDK) para usar la herramienta.

---

## 📋 Estructura de Archivos

```
week6/
├── datetime_server.py          # MCP Server
├── datetime_client.py          # MCP Client
├── test_datetime_agent.ipynb   # Tests con Agent SDK
└── test_datetime_native.ipynb  # Tests con OpenAI nativo
```

---

## 🔧 Parte 1: MCP Server - `datetime_server.py`

Este archivo define el servidor MCP que expone herramientas relacionadas con fecha y hora.

```python
"""
MCP Server for Date and Time Tools
Provides utilities for getting current date, time, and timezone information.
"""

from datetime import datetime
import pytz
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Create MCP server instance
mcp = FastMCP("datetime-server")


@mcp.tool()
def get_current_date() -> str:
    """
    Get the current date in YYYY-MM-DD format.
    
    Returns:
        Current date as a string (e.g., '2026-02-04')
    """
    return datetime.now().strftime("%Y-%m-%d")


@mcp.tool()
def get_current_time() -> str:
    """
    Get the current time in HH:MM:SS format.
    
    Returns:
        Current time as a string (e.g., '14:30:45')
    """
    return datetime.now().strftime("%H:%M:%S")


@mcp.tool()
def get_current_datetime() -> str:
    """
    Get the current date and time in a human-readable format.
    
    Returns:
        Current datetime as a string (e.g., 'Tuesday, February 04, 2026 at 14:30:45')
    """
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y at %H:%M:%S")


@mcp.tool()
def get_timestamp() -> str:
    """
    Get the current Unix timestamp.
    
    Returns:
        Unix timestamp as a string (seconds since epoch)
    """
    return str(int(datetime.now().timestamp()))


@mcp.tool()
def get_datetime_in_timezone(timezone: str) -> str:
    """
    Get the current date and time in a specific timezone.
    
    Args:
        timezone: Timezone name (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo')
    
    Returns:
        Current datetime in the specified timezone
    
    Examples:
        get_datetime_in_timezone('America/New_York') -> '2026-02-04 09:30:45 EST'
        get_datetime_in_timezone('Europe/London') -> '2026-02-04 14:30:45 GMT'
    """
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as e:
        return f"Error: Invalid timezone '{timezone}'. Use format like 'America/New_York'"


@mcp.tool()
def get_day_of_week() -> str:
    """
    Get the current day of the week.
    
    Returns:
        Day name (e.g., 'Monday', 'Tuesday', etc.)
    """
    return datetime.now().strftime("%A")


@mcp.tool()
def get_iso_datetime() -> str:
    """
    Get the current datetime in ISO 8601 format.
    
    Returns:
        ISO formatted datetime (e.g., '2026-02-04T14:30:45.123456')
    """
    return datetime.now().isoformat()


# Resource to get timezone list (optional advanced feature)
@mcp.resource("timezones://list")
def get_timezone_list() -> str:
    """
    Get a list of all available timezone names.
    
    Returns:
        JSON list of timezone names
    """
    import json
    common_timezones = [
        "America/New_York",
        "America/Los_Angeles",
        "America/Chicago",
        "Europe/London",
        "Europe/Paris",
        "Asia/Tokyo",
        "Asia/Shanghai",
        "Australia/Sydney",
        "UTC"
    ]
    return json.dumps(common_timezones, indent=2)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
```

---

## 🔌 Parte 2: MCP Client - `datetime_client.py`

Este archivo crea un cliente para conectarse al MCP Server.

```python
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
```

---

## 📓 Parte 3: Test con Agents SDK - `test_datetime_agent.ipynb`

Notebook para probar con el framework de Agents.

```python
# Cell 1: Imports
from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio
from IPython.display import display, Markdown

load_dotenv(override=True)

# Cell 2: Setup MCP Server
# Configure the datetime server
params = {"command": "uv", "args": ["run", "datetime_server.py"]}

# List available tools
async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as server:
    mcp_tools = await server.list_tools()

print("📋 Available DateTime Tools:")
for tool in mcp_tools:
    print(f"\n  🔧 {tool.name}")
    print(f"     {tool.description}")

# Cell 3: Create Agent with DateTime Tools
instructions = """
You are a helpful assistant with access to date and time tools.

You can:
- Tell users the current date and time
- Provide time in different timezones
- Get day of week, timestamps, etc.

Be friendly and format your responses nicely.
"""

request = "What's today's date and what day of the week is it?"
model = "gpt-4o-mini"

async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as mcp_server:
    agent = Agent(
        name="datetime_assistant",
        instructions=instructions,
        model=model,
        mcp_servers=[mcp_server]
    )
    
    with trace("datetime_query"):
        result = await Runner.run(agent, request)
    
    display(Markdown(result.final_output))

# Cell 4: Test Multiple Queries
test_queries = [
    "What time is it right now?",
    "Tell me the current date in ISO format",
    "What time is it in Tokyo right now?",
    "Give me the Unix timestamp for right now",
    "What's the current date and time in New York?"
]

async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as mcp_server:
    agent = Agent(
        name="datetime_assistant",
        instructions=instructions,
        model=model,
        mcp_servers=[mcp_server]
    )
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"❓ Query: {query}")
        print(f"{'='*60}\n")
        
        with trace(f"query_{test_queries.index(query)}"):
            result = await Runner.run(agent, query)
        
        display(Markdown(f"**Answer:** {result.final_output}"))

# Cell 5: Advanced - Multi-timezone comparison
complex_request = """
I need to schedule a meeting for tomorrow at 2 PM my time (current timezone).
Can you tell me:
1. What the exact date and time will be
2. What time that will be in Tokyo
3. What time that will be in London
4. What day of the week it will be
"""

async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as mcp_server:
    agent = Agent(
        name="datetime_assistant",
        instructions=instructions,
        model=model,
        mcp_servers=[mcp_server]
    )
    
    with trace("complex_datetime_query"):
        result = await Runner.run(agent, complex_request)
    
    display(Markdown(result.final_output))
```

---

## 🔥 Parte 4: Test con OpenAI Nativo - `test_datetime_native.ipynb`

**EJERCICIO DIFÍCIL:** Usar la API de OpenAI directamente sin Agents SDK.

```python
# Cell 1: Imports
from dotenv import load_dotenv
from datetime_client import list_datetime_tools, call_datetime_tool
from openai import OpenAI
import json

load_dotenv(override=True)

client = OpenAI()

# Cell 2: Get MCP Tools
# List available MCP tools
mcp_tools = await list_datetime_tools()

print("📋 Available MCP Tools:")
for tool in mcp_tools:
    print(f"\n🔧 {tool.name}")
    print(f"   Description: {tool.description}")
    print(f"   Input Schema: {json.dumps(tool.inputSchema, indent=2)}")

# Cell 3: Convert MCP Tools to OpenAI Format
def mcp_tool_to_openai_format(mcp_tool):
    """Convert MCP tool to OpenAI function calling format"""
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description,
            "parameters": mcp_tool.inputSchema
        }
    }

openai_tools = [mcp_tool_to_openai_format(tool) for tool in mcp_tools]

print("\n✅ Converted to OpenAI format:")
print(json.dumps(openai_tools[0], indent=2))

# Cell 4: Manual Agent Loop with Native OpenAI
messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant with access to date and time tools. Use them to answer user questions."
    },
    {
        "role": "user",
        "content": "What's today's date and what day of the week is it?"
    }
]

print("🤖 Starting agent loop with native OpenAI...\n")

max_iterations = 5
iteration = 0

while iteration < max_iterations:
    iteration += 1
    print(f"{'='*60}")
    print(f"🔄 Iteration {iteration}")
    print(f"{'='*60}\n")
    
    # Call OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=openai_tools,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    finish_reason = response.choices[0].finish_reason
    
    print(f"📊 Finish Reason: {finish_reason}\n")
    
    # Add assistant message to history
    messages.append(message.model_dump())
    
    if finish_reason == "tool_calls":
        # Handle tool calls
        tool_calls = message.tool_calls
        
        print(f"🛠️  Tool Calls: {len(tool_calls)}\n")
        
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            print(f"   Calling: {tool_name}")
            print(f"   Arguments: {arguments}")
            
            # Call the MCP tool
            result = await call_datetime_tool(tool_name, arguments)
            
            print(f"   Result: {result}\n")
            
            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
    
    elif finish_reason == "stop":
        # Agent finished
        print("✅ Agent completed!\n")
        print(f"💬 Final Answer:\n{message.content}\n")
        break
    
    else:
        print(f"⚠️  Unexpected finish reason: {finish_reason}")
        break

print(f"\n{'='*60}")
print("🎉 Agent loop completed!")
print(f"{'='*60}")

# Cell 5: Test Multiple Queries with Native OpenAI
def run_native_agent(user_query: str):
    """
    Run a complete agent loop with native OpenAI API.
    
    Args:
        user_query: User's question
    
    Returns:
        Final response from the agent
    """
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant with access to date and time tools."
        },
        {
            "role": "user",
            "content": user_query
        }
    ]
    
    max_iterations = 10
    
    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=openai_tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason
        
        messages.append(message.model_dump())
        
        if finish_reason == "tool_calls":
            # Execute tool calls
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                # Call MCP tool (using async wrapper)
                import asyncio
                result = asyncio.run(call_datetime_tool(tool_name, arguments))
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        
        elif finish_reason == "stop":
            return message.content
        
        else:
            return f"Error: Unexpected finish reason: {finish_reason}"
    
    return "Error: Max iterations reached"


# Test queries
test_queries = [
    "What's the current time?",
    "Tell me today's date in ISO format",
    "What time is it in London right now?",
    "Give me the Unix timestamp"
]

print("\n🧪 Testing Multiple Queries:\n")

for query in test_queries:
    print(f"{'='*60}")
    print(f"❓ {query}")
    print(f"{'='*60}")
    
    answer = run_native_agent(query)
    print(f"💬 {answer}\n")

# Cell 6: Compare Performance - Agent SDK vs Native
import time

query = "What's today's date and what day of the week is it?"

# Test with Agent SDK
print("⏱️  Testing with Agent SDK...")
start_time = time.time()

async with MCPServerStdio(
    params={"command": "uv", "args": ["run", "datetime_server.py"]},
    client_session_timeout_seconds=30
) as mcp_server:
    agent = Agent(
        name="datetime_assistant",
        instructions="You are a helpful date/time assistant.",
        model="gpt-4o-mini",
        mcp_servers=[mcp_server]
    )
    result = await Runner.run(agent, query)
    sdk_answer = result.final_output

sdk_time = time.time() - start_time

print(f"✅ Agent SDK: {sdk_time:.2f}s")
print(f"   Answer: {sdk_answer}\n")

# Test with Native OpenAI
print("⏱️  Testing with Native OpenAI...")
start_time = time.time()

native_answer = run_native_agent(query)
native_time = time.time() - start_time

print(f"✅ Native OpenAI: {native_time:.2f}s")
print(f"   Answer: {native_answer}\n")

# Comparison
print(f"{'='*60}")
print("📊 Performance Comparison:")
print(f"{'='*60}")
print(f"Agent SDK:     {sdk_time:.2f}s")
print(f"Native OpenAI: {native_time:.2f}s")
print(f"Difference:    {abs(sdk_time - native_time):.2f}s")
```

---

## 📝 Resumen de la Solución

### ✅ Parte 1 (Básica): MCP Server + Agent SDK

**Archivos:**
- `datetime_server.py`: Define 7 herramientas de fecha/hora
- `test_datetime_agent.ipynb`: Usa Agent SDK para interactuar

**Herramientas implementadas:**
1. `get_current_date()` - Fecha actual
2. `get_current_time()` - Hora actual
3. `get_current_datetime()` - Fecha y hora completa
4. `get_timestamp()` - Unix timestamp
5. `get_datetime_in_timezone()` - Hora en timezone específico
6. `get_day_of_week()` - Día de la semana
7. `get_iso_datetime()` - Formato ISO 8601

### ✅ Parte 2 (Difícil): MCP Client + OpenAI Nativo

**Archivos:**
- `datetime_client.py`: Cliente MCP reutilizable
- `test_datetime_native.ipynb`: Implementación sin Agent SDK

**Características avanzadas:**
- Conversión de herramientas MCP → OpenAI format
- Agent loop manual implementado
- Comparación de performance
- Manejo de tool calls sin abstracción

---

## 🎯 Conceptos Clave Demostrados

1. **MCP Server**: Protocolo estándar para exponer herramientas
2. **MCP Client**: Conexión y consumo de herramientas MCP
3. **Agent SDK**: Abstracción de alto nivel (fácil)
4. **Native OpenAI**: Control completo de bajo nivel (difícil)
5. **Tool Calling**: Patrón de función-llamada-resultado
6. **Async/Await**: Operaciones asíncronas con MCP

---

## 🚀 Cómo Ejecutar

```bash
# 1. Instalar dependencias
pip install mcp fastmcp pytz openai python-dotenv agents

# 2. Probar el servidor directamente
python datetime_server.py

# 3. Probar el cliente
python datetime_client.py

# 4. Ejecutar notebooks
jupyter notebook test_datetime_agent.ipynb
jupyter notebook test_datetime_native.ipynb
```

---

¡Solución completa implementada! 🎉

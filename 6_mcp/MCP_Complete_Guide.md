# 🚀 Guía Completa de MCP (Model Context Protocol)

## 📖 Índice

1. [¿Qué es MCP?](#qué-es-mcp)
2. [¿Por qué existe MCP?](#por-qué-existe-mcp)
3. [Conceptos Fundamentales](#conceptos-fundamentales)
4. [MCP Server - Tutorial Paso a Paso](#mcp-server---tutorial-paso-a-paso)
5. [MCP Client - Tutorial Paso a Paso](#mcp-client---tutorial-paso-a-paso)
6. [Casos de Uso Reales](#casos-de-uso-reales)
7. [Ejemplos Completos](#ejemplos-completos)

---

## ¿Qué es MCP?

**MCP (Model Context Protocol)** es un protocolo estándar para que los **modelos de IA (LLMs)** puedan **usar herramientas externas** de forma consistente.

### 🎯 Analogía Simple

Imagina que MCP es como un **adaptador universal para enchufes**:

```
Sin MCP:
┌─────────────┐
│   ChatGPT   │ → Necesita código específico para cada herramienta
│             │ → get_weather() ✗
│             │ → send_email() ✗
│             │ → read_database() ✗
└─────────────┘

Con MCP:
┌─────────────┐
│   ChatGPT   │ → MCP Server (Weather) ✓
│             │ → MCP Server (Email) ✓
│             │ → MCP Server (Database) ✓
└─────────────┘
```

**Antes de MCP:** Cada empresa creaba sus propias herramientas de forma incompatible.

**Con MCP:** Todos usan el mismo "lenguaje" para exponer herramientas.

---

## ¿Por qué existe MCP?

### 🔴 Problema Original

```python
# Problema: Cada LLM tiene su propio formato de herramientas

# OpenAI format
openai_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "parameters": {...}
    }
}

# Anthropic format (diferente!)
anthropic_tool = {
    "name": "get_weather",
    "description": "...",
    "input_schema": {...}
}

# Google format (también diferente!)
google_tool = {
    "function_declarations": [{
        "name": "get_weather",
        ...
    }]
}
```

**Resultado:** Si creas una herramienta para OpenAI, NO funciona en Anthropic.

### ✅ Solución: MCP

```python
# UN SOLO servidor MCP funciona con TODOS los LLMs

@mcp.tool()
def get_weather(city: str) -> str:
    """Get weather for a city"""
    return f"Weather in {city}: Sunny, 22°C"

# Este mismo código funciona con:
# ✓ OpenAI (GPT-4, GPT-3.5)
# ✓ Anthropic (Claude)
# ✓ Google (Gemini)
# ✓ Cualquier LLM que soporte MCP
```

---

## Conceptos Fundamentales

### 🏗️ Arquitectura MCP

```
┌─────────────────────────────────────────────────────────┐
│                      TU APLICACIÓN                       │
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │  LLM (GPT)   │ ←──────→│  MCP Client  │             │
│  │              │         │              │             │
│  └──────────────┘         └──────┬───────┘             │
│                                   │                      │
└───────────────────────────────────┼──────────────────────┘
                                    │
                                    │ MCP Protocol (JSON-RPC)
                                    │
┌───────────────────────────────────┼──────────────────────┐
│                                   ▼                      │
│                          ┌──────────────┐                │
│                          │  MCP Server  │                │
│                          │              │                │
│                          │  Tools:      │                │
│                          │  • Tool 1    │                │
│                          │  • Tool 2    │                │
│                          │  • Tool 3    │                │
│                          └──────────────┘                │
│                                                          │
│                       SERVIDOR REMOTO                    │
└─────────────────────────────────────────────────────────┘
```

### 🎭 Los 3 Actores Principales

#### 1️⃣ **MCP Server (Proveedor)**
- **Qué es:** Un programa que expone herramientas
- **Qué hace:** Espera peticiones y ejecuta funciones
- **Ejemplo:** Un servidor que puede consultar bases de datos

#### 2️⃣ **MCP Client (Consumidor)**
- **Qué es:** Un programa que conecta al servidor
- **Qué hace:** Descubre herramientas disponibles y las llama
- **Ejemplo:** Tu aplicación que quiere usar las herramientas

#### 3️⃣ **MCP Protocol (Comunicación)**
- **Qué es:** El "lenguaje" que usan para hablar
- **Cómo funciona:** JSON-RPC sobre STDIO o HTTP
- **Ejemplo:** `{"method": "tools/call", "params": {...}}`

---

## MCP Server - Tutorial Paso a Paso

### 📝 Ejemplo 1: El Servidor Más Simple Posible

```python
"""
Archivo: simple_server.py
El servidor MCP más básico que existe
"""

from mcp.server.fastmcp import FastMCP

# Paso 1: Crear el servidor
mcp = FastMCP("my-first-server")

# Paso 2: Definir una herramienta
@mcp.tool()
def say_hello(name: str) -> str:
    """Say hello to someone"""
    return f"Hello, {name}!"

# Paso 3: Ejecutar el servidor
if __name__ == "__main__":
    mcp.run()
```

**¿Qué hace cada parte?**

```python
mcp = FastMCP("my-first-server")
#              ^^^^^^^^^^^^^^^^
#              Nombre del servidor (puede ser cualquier cosa)
```

```python
@mcp.tool()
# ^^^^
# Este decorador dice: "Esta función es una herramienta MCP"
```

```python
def say_hello(name: str) -> str:
    """Say hello to someone"""
    #   ^^^^^^^^^^^^^^^^^^^^
    #   Esta descripción es IMPORTANTE - el LLM la lee para saber qué hace la herramienta
    
    return f"Hello, {name}!"
```

### 🏃 Ejecutar el Servidor

```bash
# Método 1: Directamente
python simple_server.py

# Método 2: Con uv (recomendado)
uv run simple_server.py
```

**Salida esperada:**
```
MCP Server listening on stdio://
```

El servidor está corriendo y esperando peticiones.

---

### 📝 Ejemplo 2: Servidor con Múltiples Herramientas

```python
"""
Archivo: calculator_server.py
Servidor MCP que funciona como calculadora
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calculator")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together"""
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a"""
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> str:
    """Divide a by b"""
    if b == 0:
        return "Error: Cannot divide by zero"
    return str(a / b)


@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent"""
    return base ** exponent


if __name__ == "__main__":
    mcp.run()
```

**Características importantes:**

1. **Type hints son obligatorios:**
```python
def add(a: float, b: float) -> float:
#          ^^^^^    ^^^^^      ^^^^^
#          MCP necesita saber los tipos para generar el esquema
```

2. **Docstrings son la descripción que ve el LLM:**
```python
"""Add two numbers together"""
# El LLM lee esto para decidir si usar esta herramienta
```

3. **Manejo de errores:**
```python
if b == 0:
    return "Error: Cannot divide by zero"
# Siempre retorna strings con errores descriptivos
```

---

### 📝 Ejemplo 3: Servidor con Herramientas Complejas

```python
"""
Archivo: file_server.py
Servidor MCP para operaciones con archivos
"""

from mcp.server.fastmcp import FastMCP
import os
from typing import List

mcp = FastMCP("file-operations")


@mcp.tool()
def list_files(directory: str = ".") -> str:
    """
    List all files in a directory.
    
    Args:
        directory: Path to the directory (default: current directory)
    
    Returns:
        Formatted list of files
    """
    try:
        files = os.listdir(directory)
        if not files:
            return f"Directory '{directory}' is empty"
        
        result = f"Files in '{directory}':\n"
        for i, file in enumerate(files, 1):
            result += f"{i}. {file}\n"
        
        return result
    except FileNotFoundError:
        return f"Error: Directory '{directory}' not found"
    except PermissionError:
        return f"Error: Permission denied for '{directory}'"


@mcp.tool()
def read_file(filepath: str) -> str:
    """
    Read the contents of a text file.
    
    Args:
        filepath: Path to the file to read
    
    Returns:
        File contents or error message
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: File '{filepath}' not found"
    except PermissionError:
        return f"Error: Permission denied for '{filepath}'"
    except UnicodeDecodeError:
        return f"Error: '{filepath}' is not a text file"


@mcp.tool()
def write_file(filepath: str, content: str) -> str:
    """
    Write content to a file.
    
    Args:
        filepath: Path where to write the file
        content: Content to write
    
    Returns:
        Success message or error
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to '{filepath}'"
    except PermissionError:
        return f"Error: Permission denied for '{filepath}'"
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def file_exists(filepath: str) -> str:
    """
    Check if a file exists.
    
    Args:
        filepath: Path to check
    
    Returns:
        "exists" or "not found"
    """
    if os.path.exists(filepath):
        return f"'{filepath}' exists"
    return f"'{filepath}' not found"


if __name__ == "__main__":
    mcp.run()
```

**Lecciones importantes:**

1. **Siempre maneja excepciones:**
```python
try:
    # código que puede fallar
except FileNotFoundError:
    return "Error: ..."  # Mensaje descriptivo
```

2. **Usa valores por defecto:**
```python
def list_files(directory: str = ".") -> str:
#                              ^^^^
#                              El LLM puede omitir este parámetro
```

3. **Documenta los Args:**
```python
"""
Args:
    directory: Path to the directory (default: current directory)
    
Returns:
    Formatted list of files
"""
# El LLM lee esta información para saber cómo usar la herramienta
```

---

### 📝 Ejemplo 4: Servidor con Resources (Avanzado)

**Resources** son datos que el LLM puede leer (pero no modificar).

```python
"""
Archivo: config_server.py
Servidor con herramientas Y resources
"""

from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("config-manager")

# Configuración simulada
config = {
    "app_name": "MyApp",
    "version": "1.0.0",
    "settings": {
        "theme": "dark",
        "language": "en"
    }
}


# RESOURCE: El LLM puede LEER esto
@mcp.resource("config://settings")
def get_config() -> str:
    """Get current application configuration"""
    return json.dumps(config, indent=2)


# TOOL: El LLM puede EJECUTAR esto
@mcp.tool()
def update_setting(key: str, value: str) -> str:
    """
    Update a configuration setting.
    
    Args:
        key: Setting key (e.g., 'theme', 'language')
        value: New value
    """
    if key in config["settings"]:
        old_value = config["settings"][key]
        config["settings"][key] = value
        return f"Updated '{key}' from '{old_value}' to '{value}'"
    return f"Error: Setting '{key}' not found"


@mcp.tool()
def get_setting(key: str) -> str:
    """Get the value of a specific setting"""
    if key in config["settings"]:
        return f"{key}: {config['settings'][key]}"
    return f"Error: Setting '{key}' not found"


if __name__ == "__main__":
    mcp.run()
```

**Diferencia Tools vs Resources:**

| Aspecto | Tools | Resources |
|---------|-------|-----------|
| **Propósito** | Ejecutar acciones | Leer información |
| **Efecto** | Puede modificar estado | Solo lectura |
| **Ejemplo** | `send_email()` | `get_user_profile()` |
| **Cuándo usar** | Cambios, cálculos | Datos estáticos, configs |

---

## MCP Client - Tutorial Paso a Paso

### 🔌 ¿Qué es un MCP Client?

Es el código que **se conecta** a un MCP Server para **usar sus herramientas**.

### 📝 Ejemplo 1: Cliente Más Simple

```python
"""
Archivo: simple_client.py
Cliente MCP básico
"""

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio


async def main():
    # Paso 1: Configurar conexión al servidor
    server_params = StdioServerParameters(
        command="uv",                      # Comando para ejecutar
        args=["run", "simple_server.py"]   # Argumentos
    )
    
    # Paso 2: Conectar al servidor
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # Paso 3: Inicializar la sesión
            await session.initialize()
            
            # Paso 4: Listar herramientas disponibles
            tools_response = await session.list_tools()
            print("📋 Available tools:")
            for tool in tools_response.tools:
                print(f"  • {tool.name}: {tool.description}")
            
            # Paso 5: Llamar una herramienta
            result = await session.call_tool(
                "say_hello",
                arguments={"name": "Alice"}
            )
            
            # Paso 6: Mostrar resultado
            print(f"\n💬 Result: {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
```

**Ejecutar:**
```bash
python simple_client.py
```

**Salida esperada:**
```
📋 Available tools:
  • say_hello: Say hello to someone

💬 Result: Hello, Alice!
```

---

### 📝 Ejemplo 2: Cliente con Múltiples Llamadas

```python
"""
Archivo: calculator_client.py
Cliente que usa el servidor de calculadora
"""

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio


async def call_tool(session, tool_name: str, arguments: dict):
    """Helper para llamar herramientas y extraer resultado"""
    result = await session.call_tool(tool_name, arguments=arguments)
    return result.content[0].text


async def main():
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "calculator_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("🧮 Calculator Client\n")
            
            # Operaciones
            operations = [
                ("add", {"a": 10, "b": 5}),
                ("subtract", {"a": 10, "b": 5}),
                ("multiply", {"a": 10, "b": 5}),
                ("divide", {"a": 10, "b": 5}),
                ("power", {"base": 2, "exponent": 8}),
                ("divide", {"a": 10, "b": 0})  # Error case
            ]
            
            for tool_name, args in operations:
                result = await call_tool(session, tool_name, args)
                
                # Formatear para display
                if tool_name == "add":
                    expr = f"{args['a']} + {args['b']}"
                elif tool_name == "subtract":
                    expr = f"{args['a']} - {args['b']}"
                elif tool_name == "multiply":
                    expr = f"{args['a']} × {args['b']}"
                elif tool_name == "divide":
                    expr = f"{args['a']} ÷ {args['b']}"
                elif tool_name == "power":
                    expr = f"{args['base']} ^ {args['exponent']}"
                
                print(f"{expr} = {result}")


if __name__ == "__main__":
    asyncio.run(main())
```

**Salida esperada:**
```
🧮 Calculator Client

10 + 5 = 15.0
10 - 5 = 5.0
10 × 5 = 50.0
10 ÷ 5 = 2.0
2 ^ 8 = 256.0
10 ÷ 0 = Error: Cannot divide by zero
```

---

### 📝 Ejemplo 3: Cliente Integrado con LLM

Este es el caso de uso **MÁS COMÚN**: Un LLM usando herramientas MCP.

```python
"""
Archivo: llm_client.py
Cliente que conecta un LLM con herramientas MCP
"""

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
import asyncio
import json

client = OpenAI()


def mcp_tool_to_openai(mcp_tool):
    """Convertir herramienta MCP a formato OpenAI"""
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description,
            "parameters": mcp_tool.inputSchema
        }
    }


async def run_agent_with_mcp():
    """Ejecutar un agente que usa herramientas MCP"""
    
    # Conectar al servidor MCP
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "calculator_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Obtener herramientas del servidor MCP
            tools_response = await session.list_tools()
            mcp_tools = tools_response.tools
            
            # Convertir a formato OpenAI
            openai_tools = [mcp_tool_to_openai(tool) for tool in mcp_tools]
            
            # Configurar conversación
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful math assistant with access to calculator tools."
                },
                {
                    "role": "user",
                    "content": "What's 15 multiplied by 8, then add 100 to the result?"
                }
            ]
            
            print("🤖 Agent Loop Starting...\n")
            
            # Agent loop
            max_iterations = 10
            for iteration in range(max_iterations):
                print(f"{'='*60}")
                print(f"Iteration {iteration + 1}")
                print(f"{'='*60}\n")
                
                # Llamar al LLM
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=openai_tools
                )
                
                message = response.choices[0].message
                finish_reason = response.choices[0].finish_reason
                
                messages.append(message.model_dump())
                
                if finish_reason == "tool_calls":
                    print(f"🛠️  LLM wants to use tools:\n")
                    
                    # Ejecutar cada tool call
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        
                        print(f"   Calling: {tool_name}")
                        print(f"   Arguments: {arguments}")
                        
                        # Llamar herramienta MCP
                        result = await session.call_tool(
                            tool_name,
                            arguments=arguments
                        )
                        
                        tool_result = result.content[0].text
                        print(f"   Result: {tool_result}\n")
                        
                        # Añadir resultado a mensajes
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result
                        })
                
                elif finish_reason == "stop":
                    print("✅ Agent finished!\n")
                    print(f"💬 Final Answer:\n{message.content}\n")
                    break
                
                else:
                    print(f"⚠️  Unexpected finish: {finish_reason}")
                    break


if __name__ == "__main__":
    asyncio.run(run_agent_with_mcp())
```

**Salida esperada:**
```
🤖 Agent Loop Starting...

============================================================
Iteration 1
============================================================

🛠️  LLM wants to use tools:

   Calling: multiply
   Arguments: {'a': 15, 'b': 8}
   Result: 120.0

============================================================
Iteration 2
============================================================

🛠️  LLM wants to use tools:

   Calling: add
   Arguments: {'a': 120, 'b': 100}
   Result: 220.0

============================================================
Iteration 3
============================================================

✅ Agent finished!

💬 Final Answer:
The result of 15 multiplied by 8 is 120, and adding 100 to that gives us 220.
```

---

## Casos de Uso Reales

### 🎯 Caso de Uso 1: Sistema de Soporte al Cliente

```python
"""
customer_support_server.py
MCP Server para automatizar soporte al cliente
"""

from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("customer-support")

# Base de datos simulada
tickets = {}
knowledge_base = {
    "reset_password": "Go to Settings > Account > Reset Password",
    "billing": "Contact billing@company.com or call 1-800-BILLING",
    "technical": "Check status.company.com for system status"
}


@mcp.tool()
def create_ticket(customer_name: str, issue: str, priority: str = "normal") -> str:
    """
    Create a new support ticket.
    
    Args:
        customer_name: Name of the customer
        issue: Description of the issue
        priority: Ticket priority (low, normal, high, urgent)
    """
    ticket_id = f"TICK-{len(tickets) + 1:04d}"
    tickets[ticket_id] = {
        "customer": customer_name,
        "issue": issue,
        "priority": priority,
        "status": "open"
    }
    return f"Created ticket {ticket_id} for {customer_name}"


@mcp.tool()
def search_knowledge_base(keyword: str) -> str:
    """Search the knowledge base for solutions"""
    keyword = keyword.lower()
    results = []
    
    for topic, solution in knowledge_base.items():
        if keyword in topic.lower() or keyword in solution.lower():
            results.append(f"**{topic}**: {solution}")
    
    if results:
        return "\n".join(results)
    return "No solutions found. Please create a support ticket."


@mcp.tool()
def get_ticket_status(ticket_id: str) -> str:
    """Get the status of a support ticket"""
    if ticket_id in tickets:
        ticket = tickets[ticket_id]
        return json.dumps(ticket, indent=2)
    return f"Ticket {ticket_id} not found"


@mcp.tool()
def escalate_ticket(ticket_id: str, reason: str) -> str:
    """Escalate a ticket to senior support"""
    if ticket_id in tickets:
        tickets[ticket_id]["priority"] = "urgent"
        tickets[ticket_id]["escalated"] = reason
        return f"Ticket {ticket_id} escalated to senior support"
    return f"Ticket {ticket_id} not found"


if __name__ == "__main__":
    mcp.run()
```

**Uso con un agente:**
```python
# El agente puede:
# 1. Buscar en knowledge base primero
# 2. Si no hay solución, crear ticket
# 3. Si el cliente está frustrado, escalar
```

---

### 🎯 Caso de Uso 2: Análisis de Datos

```python
"""
data_analysis_server.py
MCP Server para análisis de datos
"""

from mcp.server.fastmcp import FastMCP
import pandas as pd
import json

mcp = FastMCP("data-analyst")

# Datos de ejemplo
data = pd.DataFrame({
    'product': ['A', 'B', 'C', 'A', 'B', 'C'],
    'sales': [100, 150, 200, 120, 180, 220],
    'region': ['North', 'North', 'North', 'South', 'South', 'South']
})


@mcp.tool()
def get_total_sales(region: str = None) -> str:
    """Get total sales, optionally filtered by region"""
    if region:
        filtered = data[data['region'] == region]
        total = filtered['sales'].sum()
        return f"Total sales in {region}: ${total}"
    
    total = data['sales'].sum()
    return f"Total sales: ${total}"


@mcp.tool()
def get_top_products(n: int = 3) -> str:
    """Get top N products by sales"""
    top = data.groupby('product')['sales'].sum().sort_values(ascending=False).head(n)
    
    result = f"Top {n} products:\n"
    for i, (product, sales) in enumerate(top.items(), 1):
        result += f"{i}. Product {product}: ${sales}\n"
    
    return result


@mcp.tool()
def compare_regions() -> str:
    """Compare sales performance across regions"""
    by_region = data.groupby('region')['sales'].sum()
    
    result = "Sales by Region:\n"
    for region, sales in by_region.items():
        result += f"  {region}: ${sales}\n"
    
    return result


@mcp.tool()
def get_product_details(product: str) -> str:
    """Get detailed sales information for a specific product"""
    product_data = data[data['product'] == product]
    
    if product_data.empty:
        return f"Product {product} not found"
    
    total = product_data['sales'].sum()
    by_region = product_data.groupby('region')['sales'].sum()
    
    result = f"Product {product} Details:\n"
    result += f"Total Sales: ${total}\n"
    result += "By Region:\n"
    for region, sales in by_region.items():
        result += f"  {region}: ${sales}\n"
    
    return result


if __name__ == "__main__":
    mcp.run()
```

**Interacción natural:**
```
Usuario: "¿Cuál es nuestro producto más vendido?"
LLM: [usa get_top_products(n=1)]
LLM: "El producto C es el más vendido con $420 en ventas totales."

Usuario: "¿Cómo se desempeña en cada región?"
LLM: [usa get_product_details(product="C")]
LLM: "El Producto C vendió $200 en North y $220 en South."
```

---

### 🎯 Caso de Uso 3: Automatización de Email

```python
"""
email_server.py
MCP Server para gestión de emails
"""

from mcp.server.fastmcp import FastMCP
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

mcp = FastMCP("email-manager")

# Plantillas
templates = {
    "welcome": """
    Hi {name},
    
    Welcome to our platform! We're excited to have you.
    
    Best regards,
    The Team
    """,
    
    "reminder": """
    Hi {name},
    
    This is a friendly reminder about {topic}.
    
    Thanks,
    The Team
    """
}


@mcp.tool()
def list_templates() -> str:
    """List all available email templates"""
    result = "Available templates:\n"
    for name, content in templates.items():
        result += f"\n**{name}**:\n{content}\n"
    return result


@mcp.tool()
def preview_email(template: str, name: str, topic: str = "") -> str:
    """
    Preview an email before sending.
    
    Args:
        template: Template name (welcome, reminder)
        name: Recipient name
        topic: Topic for reminder emails
    """
    if template not in templates:
        return f"Template '{template}' not found"
    
    content = templates[template].format(name=name, topic=topic)
    return f"Preview:\n{content}"


@mcp.tool()
def send_email(to: str, template: str, name: str, topic: str = "") -> str:
    """
    Send an email using a template.
    
    Args:
        to: Recipient email address
        template: Template name
        name: Recipient name
        topic: Topic for reminder emails
    """
    if template not in templates:
        return f"Error: Template '{template}' not found"
    
    content = templates[template].format(name=name, topic=topic)
    
    # En producción, aquí iría el código real de SMTP
    # Por ahora, simulamos el envío
    return f"✓ Email sent to {to} using '{template}' template"


@mcp.tool()
def create_template(name: str, content: str) -> str:
    """
    Create a new email template.
    
    Args:
        name: Template name
        content: Template content (use {name} and {topic} as placeholders)
    """
    templates[name] = content
    return f"Created template '{name}'"


if __name__ == "__main__":
    mcp.run()
```

---

## 💡 Mejores Prácticas

### ✅ DO - Hacer

```python
# 1. Siempre usa type hints
@mcp.tool()
def good_tool(name: str, age: int) -> str:  # ✓ Tipos claros
    return f"{name} is {age} years old"

# 2. Escribe docstrings descriptivos
@mcp.tool()
def search_products(query: str, max_results: int = 10) -> str:
    """
    Search for products in the catalog.
    
    Args:
        query: Search term (e.g., 'laptop', 'phone')
        max_results: Maximum number of results to return (default: 10)
    
    Returns:
        Formatted list of matching products
    """
    pass

# 3. Maneja errores gracefully
@mcp.tool()
def divide(a: float, b: float) -> str:
    if b == 0:
        return "Error: Division by zero"
    return str(a / b)

# 4. Retorna strings formateados
@mcp.tool()
def get_user_info(user_id: str) -> str:
    user = database.get(user_id)
    return f"""
    User Information:
    - Name: {user.name}
    - Email: {user.email}
    - Status: {user.status}
    """
```

### ❌ DON'T - No Hacer

```python
# 1. Sin type hints
@mcp.tool()
def bad_tool(name, age):  # ✗ MCP no puede generar esquema
    return f"{name} is {age}"

# 2. Docstrings vagos
@mcp.tool()
def search(query: str) -> str:
    """Search stuff"""  # ✗ El LLM no sabe qué busca
    pass

# 3. Dejar que las excepciones exploten
@mcp.tool()
def divide(a: float, b: float) -> float:
    return a / b  # ✗ Crash si b == 0

# 4. Retornar objetos complejos
@mcp.tool()
def get_users() -> list:  # ✗ MCP espera strings
    return [user1, user2]
```

---

## 🎓 Conceptos Avanzados

### 🔄 Progreso y Notificaciones

```python
@mcp.tool()
async def long_running_task(duration: int) -> str:
    """Execute a long-running task with progress updates"""
    import asyncio
    
    for i in range(duration):
        # Simular trabajo
        await asyncio.sleep(1)
        
        # En una implementación real, podrías enviar notificaciones
        progress = (i + 1) / duration * 100
        print(f"Progress: {progress:.1f}%")
    
    return "Task completed!"
```

### 🎨 Prompts Personalizados

```python
@mcp.prompt()
def create_analysis_prompt(data_type: str) -> str:
    """Generate a prompt for data analysis"""
    return f"""
    You are a data analyst specializing in {data_type}.
    
    Your task is to:
    1. Analyze the data thoroughly
    2. Identify key trends
    3. Provide actionable insights
    4. Create visualizations when helpful
    
    Be concise but comprehensive.
    """
```

### 🔐 Autenticación y Seguridad

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("secure-server")

# Configurar autenticación
@mcp.tool()
def sensitive_operation(api_key: str, action: str) -> str:
    """Perform a sensitive operation (requires API key)"""
    
    # Validar API key
    if not validate_api_key(api_key):
        return "Error: Invalid API key"
    
    # Verificar permisos
    if not has_permission(api_key, action):
        return "Error: Insufficient permissions"
    
    # Ejecutar operación
    return perform_action(action)
```

---

## 📊 Comparación: MCP vs Alternativas

| Aspecto | MCP | Function Calling Nativo | LangChain Tools |
|---------|-----|-------------------------|-----------------|
| **Estándar** | ✅ Universal | ❌ Específico por LLM | ⚠️ Framework-specific |
| **Portabilidad** | ✅ Alta | ❌ Baja | ⚠️ Media |
| **Complejidad** | ⚠️ Media | ✅ Baja | ❌ Alta |
| **Reutilización** | ✅ Excelente | ❌ Pobre | ⚠️ Buena |
| **Comunidad** | 🆕 Creciendo | ✅ Establecida | ✅ Establecida |

---

## 🎯 Resumen Final

### ¿Cuándo usar MCP?

✅ **Úsalo cuando:**
- Quieras herramientas reutilizables entre LLMs
- Necesites separar lógica de negocio de la IA
- Quieras compartir herramientas con otros
- Construyas infraestructura a largo plazo

❌ **No lo uses cuando:**
- Necesitas algo rápido y simple
- Solo usarás un LLM específico
- El proyecto es experimental/temporal

### Checklist de Aprendizaje

- [ ] Entiendo qué es MCP y por qué existe
- [ ] Puedo crear un servidor MCP básico
- [ ] Puedo crear un cliente MCP básico
- [ ] Sé convertir herramientas MCP a formato OpenAI
- [ ] Entiendo la diferencia entre Tools y Resources
- [ ] Puedo manejar errores apropiadamente
- [ ] Conozco casos de uso reales

---

## 🚀 Próximos Pasos

1. **Crea tu primer servidor MCP**
2. **Pruébalo con un cliente simple**
3. **Intégralo con un LLM**
4. **Publica tu servidor** (GitHub, npm, etc.)
5. **Explora servidores MCP públicos**

---

¡Felicidades! Ahora tienes una comprensión completa de MCP. 🎉

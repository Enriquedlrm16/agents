# 📧 Análisis Completo: 2_lab2.ipynb - Sistema Agéntico de Emails de Ventas

## 🎯 Objetivo del Laboratorio

Construir un **sistema multi-agente** para generar y enviar emails de ventas en frío (cold emails) que demuestra:
1. **Agent workflow**: Flujo de trabajo coordinado entre agentes
2. **Tools**: Uso de herramientas para ejecutar funciones
3. **Agent collaboration**: Colaboración mediante Tools y Handoffs

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     SALES MANAGER                            │
│            (Agente de planificación central)                 │
│                                                              │
│  Tools disponibles:                                          │
│  • sales_agent1 (Professional)                               │
│  • sales_agent2 (Engaging/Humorous)                          │
│  • sales_agent3 (Concise)                                    │
│  • send_email                                                │
│                                                              │
│  Handoffs disponibles:                                       │
│  • Email Manager                                             │
└─────────────────────────────────────────────────────────────┘
                    │
                    ├──→ Genera 3 borradores de emails
                    │
                    ├──→ Evalúa y selecciona el mejor
                    │
                    └──→ Handoff a Email Manager
                            │
                            ├──→ subject_writer (tool)
                            ├──→ html_converter (tool)
                            └──→ send_html_email (tool)
```

---

## 📚 Componentes del Sistema

### **1. Sales Agents (3 agentes especialistas)**

#### **Sales Agent 1: Professional**
```python
instructions1 = "You are a sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write professional, serious cold emails."
```

**Características:**
- Tono: Formal y profesional
- Estilo: Corporativo, serio
- Público objetivo: Ejecutivos senior, C-level

**Ejemplo de output:**
```
Subject: Simplify SOC2 Compliance with AI-Powered Solutions

Dear [Recipient's Name],

I hope this message finds you well.

Navigating the complexities of SOC2 compliance can be challenging...
```

---

#### **Sales Agent 2: Engaging**
```python
instructions2 = "You are a humorous, engaging sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write witty, engaging cold emails that are likely to get a response."
```

**Características:**
- Tono: Casual, divertido
- Estilo: Usa emojis, metáforas creativas
- Público objetivo: Startups, equipos jóvenes

**Ejemplo de output:**
```
Subject: Ready to Tame Your Compliance Chaos? 🦁

Hey [Recipient's Name],

Ever feel like navigating SOC2 compliance is like trying to assemble 
IKEA furniture without the instructions? 😅
```

---

#### **Sales Agent 3: Concise**
```python
instructions3 = "You are a busy sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write concise, to the point cold emails."
```

**Características:**
- Tono: Directo, eficiente
- Estilo: Breve, al grano
- Público objetivo: Ejecutivos ocupados

**Ejemplo de output:**
```
Subject: Simplify Your SOC 2 Compliance Process

Hi [Recipient's Name],

I know how challenging SOC 2 compliance can be. ComplAI streamlines 
the process with AI-powered automation.

Quick call next week?
```

---

### **2. Herramientas (Tools)**

#### **Conceptos clave sobre Tools:**

**Antes (sin OpenAI Agents SDK):**
```python
# Definición JSON manual
tool_json = {
    "name": "send_email",
    "description": "Send an email",
    "parameters": {
        "type": "object",
        "properties": {
            "body": {"type": "string"}
        },
        "required": ["body"]
    }
}

# Handler manual
def handle_tool_calls(tool_calls):
    for tool_call in tool_calls:
        if tool_call.name == "send_email":
            # lógica manual...
```

**Ahora (con OpenAI Agents SDK):**
```python
@function_tool
def send_email(body: str):
    """ Send out an email with the given body to all sales prospects """
    # implementation...
```

**¡Magia!** El decorador `@function_tool` automáticamente:
- Crea el esquema JSON
- Maneja la invocación
- Gestiona tipos y validación

---

#### **Tool 1: send_email**

```python
@function_tool
def send_email(body: str):
    """ Send out an email with the given body to all sales prospects """
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("your@email.com")
    to_email = To("recipient@email.com")
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, "Sales email", content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}
```

**Características:**
- **Input**: `body` (string) - El cuerpo del email
- **Output**: Diccionario con status
- **Integración**: SendGrid API
- **Formato**: Texto plano

---

#### **Tools 2-4: Agents como Tools**

```python
tool1 = sales_agent1.as_tool(
    tool_name="sales_agent1", 
    tool_description="Write a cold sales email"
)
tool2 = sales_agent2.as_tool(
    tool_name="sales_agent2", 
    tool_description="Write a cold sales email"
)
tool3 = sales_agent3.as_tool(
    tool_name="sales_agent3", 
    tool_description="Write a cold sales email"
)
```

**¿Qué significa `.as_tool()`?**

Convierte un agente en una herramienta que otro agente puede llamar:

```
Sales Manager (agente)
    │
    └──→ Llama tool: sales_agent1
         │
         └──→ Ejecuta Sales Agent 1 (agente)
              └──→ Retorna email generado
```

**Ventaja**: Permite composición y reutilización de agentes.

---

### **3. Sales Manager (Agente Coordinador)**

```python
sales_manager_instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
 
Follow these steps carefully:
1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. 
   Do not proceed until all three drafts are ready.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment 
   of which one is most effective. You can use the tools multiple times if you're not satisfied 
   with the results from the first try.
 
3. Handoff for Sending: Pass ONLY the winning email draft to the 'Email Manager' agent. 
   The Email Manager will take care of formatting and sending.
 
Crucial Rules:
- You must use the sales agent tools to generate the drafts — do not write them yourself.
- You must hand off exactly ONE email to the Email Manager — never more than one.
"""

sales_manager = Agent(
    name="Sales Manager",
    instructions=sales_manager_instructions,
    tools=tools,
    handoffs=handoffs,
    model="gpt-4o-mini"
)
```

**Responsabilidades:**
1. ✅ Usar los 3 agentes de ventas como herramientas
2. ✅ Evaluar y seleccionar el mejor email
3. ✅ Hacer handoff al Email Manager

**Características importantes:**
- **No genera emails**: Delega la generación a los agentes especializados
- **Toma decisiones**: Evalúa cuál email es mejor
- **Orquesta el flujo**: Coordina todo el proceso

---

### **4. Email Manager (Agente de Formato y Envío)**

```python
instructions = """
You are an email formatter and sender. You receive the body of an email to be sent. 
You first use the subject_writer tool to write a subject for the email, 
then use the html_converter tool to convert the body to HTML. 
Finally, you use the send_html_email tool to send the email with the subject and HTML body.
"""

emailer_agent = Agent(
    name="Email Manager",
    instructions=instructions,
    tools=[subject_tool, html_tool, send_html_email],
    model="gpt-4o-mini",
    handoff_description="Convert an email to HTML and send it"
)
```

**Tools del Email Manager:**

1. **subject_writer** (Agent as Tool):
```python
subject_writer = Agent(
    name="Email subject writer", 
    instructions=subject_instructions, 
    model="gpt-4o-mini"
)
subject_tool = subject_writer.as_tool(
    tool_name="subject_writer",
    tool_description="Write a subject for a cold sales email"
)
```

2. **html_converter** (Agent as Tool):
```python
html_converter = Agent(
    name="HTML email body converter", 
    instructions=html_instructions, 
    model="gpt-4o-mini"
)
html_tool = html_converter.as_tool(
    tool_name="html_converter",
    tool_description="Convert a text email body to an HTML email body"
)
```

3. **send_html_email** (Function Tool):
```python
@function_tool
def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
    """ Send out an email with the given subject and HTML body to all sales prospects """
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("your@email.com")
    to_email = To("recipient@email.com")
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}
```

---

## 🔄 Flujo de Ejecución Completo

### **Paso a paso:**

```python
message = "Send out a cold sales email addressed to Dear CEO from Alice"

with trace("Automated SDR"):
    result = await Runner.run(sales_manager, message)
```

### **Iteración 1: Sales Manager planifica**

**LLM piensa:**
```
Necesito usar las 3 herramientas de sales agents para generar borradores.
```

**LLM ejecuta:**
```python
tool_calls = [
    {"function": "sales_agent1", "arguments": {"input": "Write a cold sales email addressed to Dear CEO from Alice"}},
    {"function": "sales_agent2", "arguments": {"input": "Write a cold sales email addressed to Dear CEO from Alice"}},
    {"function": "sales_agent3", "arguments": {"input": "Write a cold sales email addressed to Dear CEO from Alice"}}
]
```

### **Iteración 2: Los sales agents responden**

Cada agente genera su email:
- **Agent 1**: Email profesional y formal
- **Agent 2**: Email divertido con emojis
- **Agent 3**: Email conciso

### **Iteración 3: Sales Manager evalúa**

**LLM piensa:**
```
He recibido 3 emails. El email del Agent 2 (engaging) es el más 
probable de obtener respuesta porque usa humor y es memorable.
```

**LLM decide:**
```
Voy a hacer handoff al Email Manager con el email ganador.
```

### **Iteración 4: Handoff a Email Manager**

```python
# El control pasa completamente al Email Manager
# Sales Manager ya no participa más
```

### **Iteración 5: Email Manager formatea**

**Email Manager ejecuta:**
```python
tool_calls = [
    {"function": "subject_writer", "arguments": {"input": "Ready to Tame Your Compliance Chaos? 🦁..."}},
]
```

Recibe: `"Subject: Transform SOC2 Compliance into Your Competitive Advantage"`

### **Iteración 6: Email Manager convierte a HTML**

```python
tool_calls = [
    {"function": "html_converter", "arguments": {"input": "Hey [Name],\n\nEver feel like..."}},
]
```

Recibe:
```html
<html>
  <body>
    <p>Hey <strong>[Name]</strong>,</p>
    <p>Ever feel like navigating SOC2 compliance is like trying to assemble 
    IKEA furniture without the instructions? 😅</p>
    ...
  </body>
</html>
```

### **Iteración 7: Email Manager envía**

```python
tool_calls = [
    {"function": "send_html_email", "arguments": {
        "subject": "Transform SOC2 Compliance...",
        "html_body": "<html>...</html>"
    }},
]
```

**Resultado**: Email enviado ✅

---

## 🎓 Patrones de Diseño Agéntico Identificados

### **1. Planning Pattern (Patrón de Planificación)**

**¿Qué es?**
Un agente central coordina el trabajo de múltiples agentes especializados.

**Implementación:**
```python
sales_manager = Agent(
    name="Sales Manager",
    instructions="Generate 3 drafts, evaluate, and select the best",
    tools=[sales_agent1, sales_agent2, sales_agent3],
    ...
)
```

**Ventajas:**
- Separación de responsabilidades
- Reutilización de componentes
- Fácil de extender

---

### **2. Tool Use Pattern (Patrón de Uso de Herramientas)**

**¿Qué es?**
Agentes que pueden llamar funciones externas para realizar acciones.

**Implementación:**
```python
@function_tool
def send_email(body: str):
    # Integración con API externa (SendGrid)
    ...
```

**Ventajas:**
- Conexión con sistemas reales
- Acciones verificables
- Extensibilidad

---

### **3. Handoff Pattern (Patrón de Traspaso)**

**¿Qué es?**
Un agente transfiere el control completo a otro agente.

**Implementación:**
```python
sales_manager = Agent(
    ...,
    handoffs=[emailer_agent]
)
```

**Diferencia Tools vs Handoffs:**

**Tools (control regresa):**
```
Manager → call tool1 → result → Manager (continúa)
```

**Handoffs (control no regresa):**
```
Manager → handoff → Email Manager → Email Manager continúa
```

---

### **4. Agent-as-Tool Pattern (Patrón de Agente como Herramienta)**

**¿Qué es?**
Convertir un agente completo en una herramienta que otros agentes pueden usar.

**Implementación:**
```python
tool1 = sales_agent1.as_tool(
    tool_name="sales_agent1",
    tool_description="Write a cold sales email"
)
```

**Ventaja:**
- Composición modular
- Reutilización máxima
- Flexibilidad arquitectónica

---

## 🔍 Respuesta al Ejercicio: "¿Qué línea convierte esto de workflow a agent?"

### **La respuesta está aquí:**

```python
sales_manager = Agent(
    name="Sales Manager",
    instructions=sales_manager_instructions,
    tools=tools,                    # ← Esta línea
    handoffs=handoffs,              # ← Y esta línea
    model="gpt-4o-mini"
)
```

### **¿Por qué?**

**Definición de Anthropic:**
> "Un agente es un sistema en el que un LLM controla el flujo de trabajo"

**Workflow vs Agent:**

**Workflow (hardcoded):**
```python
# Flujo predeterminado, sin decisiones
result1 = sales_agent1.run(message)
result2 = sales_agent2.run(message)
result3 = sales_agent3.run(message)
best = pick_best([result1, result2, result3])
send_email(best)
```

**Agent (LLM controla el flujo):**
```python
# El LLM DECIDE qué herramientas usar y cuándo
sales_manager = Agent(
    tools=[tool1, tool2, tool3, send_email],  # ← LLM decide
    handoffs=[emailer_agent]                   # ← LLM decide
)
```

**La línea clave:**
```python
tools=tools
```

**¿Por qué?**
- Dar `tools` a un agente significa: "Tú decides cuándo y cómo usarlas"
- El LLM analiza el contexto y elige la estrategia
- No hay flujo pre-programado; el agente adapta su comportamiento

**Comparación:**

| Aspecto | Workflow | Agent |
|---------|----------|-------|
| Control | Código Python | LLM |
| Decisiones | Predeterminadas | Dinámicas |
| Adaptabilidad | Baja | Alta |
| Complejidad | Simple | Compleja |

---

## 💡 Soluciones Propuestas para los Ejercicios

### **Ejercicio 1: Añadir más tools y agents**

Vamos a añadir:
1. **Mail merge**: Enviar a múltiples destinatarios
2. **Follow-up agent**: Generar emails de seguimiento
3. **A/B testing**: Comparar efectividad de emails

---

### **Ejercicio 2: HARD CHALLENGE - Webhook para respuestas**

Implementar un sistema que:
1. Recibe webhooks de SendGrid cuando hay respuesta
2. Clasifica la respuesta (interesado/no interesado)
3. SDR responde automáticamente

---


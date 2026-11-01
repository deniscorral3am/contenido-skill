# Setter IA en vivo: contesta los DMs de tus reels en segundos, 24/7

Piezas: **ManyChat** (recibe el comentario o el DM) → **n8n** (el setter piensa la respuesta con Claude y tu voz) →
**ManyChat** (la envía).

## 1 · Genera tu setter (1 minuto)
```bash
python3 ~/.claude/skills/contenido/motor/setter_prompt.py --probar --palabra CONTENIDO
```
Crea `~/Contenido/dms/setter/prompt.txt`, `setter-n8n.json` (el flujo con tu prompt dentro) y `prueba.md` con 3 leads
simulados. Si algo no suena a ti, cambia tu cerebro (`~/Contenido/cerebro/voz.md`) y repite.

## 2 · Impórtalo en n8n (3 minutos)
1. n8n → **Create workflow** → menú ⋯ → **Import from file** → `~/Contenido/dms/setter/setter-n8n.json`.
2. Nodo **Claude** → credencial de Anthropic (console.anthropic.com → API Keys). ¿Prefieres OpenRouter? Cambia el nodo
   por «OpenRouter Chat Model» con un modelo de Claude.
3. **Activa** el flujo y copia la **Production URL** del nodo «Mensaje del lead» (acaba en `/webhook/setter`).

Pruébalo (cambia la URL):
```bash
curl -s -X POST https://TU-N8N/webhook/setter -H 'content-type: application/json' \
  -d '{"id":"prueba-1","nombre":"Laura","canal":"instagram","palabra":"CONTENIDO","mensaje":"CONTENIDO"}'
```
Responde `{"respuesta":"…","humano":false,"caliente":false}`.

## 3 · Conéctalo a ManyChat (5 minutos)
1. ManyChat → **Settings → Fields** → crea el campo de usuario `setter_respuesta` (texto).
2. En la automatización de tu palabra clave, después del DM con el recurso, cuando el lead responde:
   - Acción **External Request** → POST a tu URL → Body JSON:
     `{"id":"{{user_id}}","nombre":"{{first_name}}","canal":"instagram","palabra":"CONTENIDO","mensaje":"{{last_input_text}}"}`
     → Response mapping: `$.respuesta` → `setter_respuesta`.
   - Mensaje con el texto `{{setter_respuesta}}`.
   - Condición: si `$.humano` es true → etiqueta «HUMANO», notificación y pausa la automatización.
   - Si `$.caliente` es true → etiqueta «CALIENTE» (son los que reciben tu enlace de agenda).
3. Ponlo también como **Default Reply** para los DMs que no vienen de un comentario.
4. Prueba desde otra cuenta: comenta la palabra y contesta al DM.

## Bueno saber
- La memoria de la conversación va por `id` (el usuario de ManyChat). La «Simple Memory» de n8n se borra si reinicias
  n8n; para producción usa «Postgres Chat Memory» con la misma clave de sesión.
- Instagram solo deja responder en las 24 h siguientes al último mensaje del lead (norma de Meta). Los seguimientos
  posteriores te los prepara el agente setter cada noche para que los mandes tú.
- Si algo falla: n8n → Executions te dice en qué nodo.

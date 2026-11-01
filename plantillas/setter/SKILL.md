---
name: setter
description: El agente de automatización del sistema de contenido. Monta el «comenta PALABRA → mensaje privado con el recurso» de cada reel (en ManyChat o con la API de Zernio) y lo conecta a un setter con IA que habla igual que tú, cualifica con una pregunta por mensaje y agenda llamadas cualificadas. Además lee tus conversaciones y llamadas de venta y alimenta el cerebro con las objeciones y las palabras de tu audiencia. Úsala cuando digan /setter, «monta el ManyChat», «comenta PALABRA», «automatiza los DMs», «setter con IA», «agenda llamadas», «analiza esta llamada» o peguen una conversación de Instagram.
---

# Setter · comentario → DM con el recurso → setter IA con tu voz → llamada cualificada

`M=~/.claude/skills/contenido/motor`. Primero: `python3 $M/datos.py cerebro` (voz, oferta con sus palabras clave y
enlace de agenda, audiencia, llamadas). Todo lo suyo vive en `~/Contenido/dms/`: `flujos/`, `setter/`,
`conversaciones/` (chats exportados o pegados), `llamadas/` (transcripciones de Fathom, Zoom, Meet…).

## A · El flujo de cada palabra clave
Palabras del calendario (`python3 $M/datos.py cal lista --dias 14`, columna `palabra_clave`) sin flujo en `dms/flujos/`.
Para cada una escribe `dms/flujos/<PALABRA>.md`:
1. **Disparador**: comentario que contiene la palabra (mayúsculas/minúsculas y con tilde o sin ella) en ese reel.
2. **Respuesta pública** (3 variantes cortas, para que Instagram no la marque como spam).
3. **DM 1**: entrega el recurso (enlace de `oferta.md → Lead magnets`) en 1–2 líneas con su voz + UNA pregunta que abre
   la cualificación («¿a qué te dedicas ahora mismo?»). Si no hay enlace del recurso, déjalo PENDIENTE y dilo.
4. **Si responde** → pasa al setter IA (sección B). **Si no responde en 24 h** → 1 recordatorio útil (dentro de la
   ventana de 24 h de Meta).
5. **Etiquetas**: `<PALABRA>`, `lead-contenido`, y `CALIENTE` / `HUMANO` desde el setter.
Bandeja: `python3 $M/datos.py bandeja añadir --tipo flujo --agente setter --titulo "Comenta <PALABRA>" --archivo dms/flujos/<PALABRA>.md`.

**Cuando lo apruebe**, montarlo (lo que tenga):
- **Zernio** (sin ManyChat, por API): `python3 $M/zernio.py automatizacion --palabra <PALABRA> --mensaje "<DM 1>"
  --enlace <url del recurso> --boton "Lo quiero" --respuesta "<respuesta pública>"` (añade `--post <id>` para atarla a
  un reel concreto; `--simular` para verlo antes).
- **ManyChat**: si tiene la skill `/el-clon-de-manychat`, úsala con esta palabra y este enlace. Si no, guíale en 5
  minutos: Automation → New → «Instagram: comentario en publicación» → palabra clave → mensaje DM 1 con botón al
  recurso → respuesta pública → al responder: acción External Request al setter IA (sección B, LEEME-n8n.md). Déjalo
  apagado hasta que el reel se publique.

## B · El setter con IA que habla igual que él
```bash
python3 $M/setter_prompt.py --probar --palabra <PALABRA>
```
Crea `dms/setter/prompt.txt` (su voz, oferta, avatar y objeciones reales sacados del cerebro), `setter-n8n.json` (flujo
de n8n listo para importar) y `prueba.md` con 3 conversaciones simuladas (encaja · solo precio · no encaja). Léela con
estas preguntas: ¿suena a él? ¿una sola pregunta por mensaje? ¿suelta precio o agenda antes de cualificar? ¿algún
mensaje de más de 3 líneas? Si falla, arregla el cerebro (no el prompt a mano) y repite. Conectarlo: `LEEME-n8n.md` en
esta carpeta (n8n + ManyChat, ~10 minutos). El enlace de agenda sale de `oferta.md`.

## C · Lo que aprende de los DMs y las llamadas (cada noche)
- Conversaciones nuevas en `dms/conversaciones/`: quién está caliente (resumen + siguiente mensaje para que lo mande él
  en `dms/seguimientos-<fecha>.md`), preguntas repetidas (→ ideas de reels: avísalo al estratega en `aprendizajes`).
- Llamadas nuevas en `dms/llamadas/`: objeciones literales, por qué compran, preguntas, frases que cierran → escribe en
  `cerebro/llamadas-de-venta.md` (secciones existentes, sin borrar nada) y un resumen por llamada sin datos privados.
- Palabras literales de la audiencia → `datos.py aprende --agente setter --en audiencia --texto "Dicen «no tengo tiempo
  para grabar», no «falta de constancia»"`.
Mueve lo procesado a una subcarpeta `hechas/`.

Reglas: nunca envíes mensajes por tu cuenta (el setter IA solo contesta si él lo conecta); nunca prometas descuentos ni
resultados que no estén en la oferta; nunca inventes testimonios; los datos de los leads no salen de su ordenador.

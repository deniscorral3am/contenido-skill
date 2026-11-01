---
name: contenido
description: Monta el sistema entero de contenido con 7 agentes de Claude y un solo cerebro - el jefe de gabinete (el único con el que hablas, te trae los briefs y lo que necesita tu visto bueno), el analista (lo que revienta en tu nicho y lo que funciona en tu cuenta), el estratega (lo que grabas después), el copywriter (hooks y guiones con tu forma de hablar, adaptados a tu oferta y tu avatar), el editor (corta, anima y subtitula tu vídeo en bruto), el publicador (reels y trial reels en tu Instagram con Zernio) y el setter (ManyChat + setter IA con tu voz que agenda llamadas cualificadas). Hace 5 preguntas, crea el cerebro de marca que todos leen y donde todos aprenden, instala cada agente como skill, los prueba y deja el turno de noche y el panel. Úsala cuando digan /contenido, «comenta CONTENIDO», «los 7 agentes de contenido», «móntame el sistema de contenido», «un solo cerebro», «agentes para mi contenido» o «que Claude lleve mi contenido».
---

# /contenido · 7 agentes, un solo cerebro, todos trabajando para tu contenido

Idea: el dueño graba y aprueba; el resto lo hacen ellos. Cada agente tiene **un** trabajo de principio a fin, se pasan
el trabajo por archivos y **todos leen y escriben en el mismo cerebro** (`~/Contenido/cerebro/`): tu audiencia, tu nicho,
tu forma de comunicar, tu oferta, tus llamadas de venta y tus métricas. Cada cosa que uno aprende la saben los siete.

| # | Agente | Skill | Trabajo | Deja |
|---|---|---|---|---|
| 1 | Jefe de gabinete | `/jefe` | el único con el que hablas: reparte, te trae los briefs y la bandeja de aprobación | `bandeja/`, `PANEL.html` |
| 2 | Analista | `/analista` | lo que revienta en tu nicho (múltiplo sobre la media de cada cuenta) y lo que funciona en tu cuenta | `ideas.csv`, `referencias/` |
| 3 | Estratega | `/estratega` | convierte todo eso en lo que grabas después: 7 días, embudo, trial reels | `calendario.csv` |
| 4 | Copywriter | `/copywriter` | hooks y guiones con tu forma de hablar, adaptados a tu oferta y tu avatar | `guiones/` |
| 5 | Editor | `/edicion` (motor `/editor`) | crudo → cortes, animaciones, subtítulos y música con tu estilo | `editados/` |
| 6 | Publicador | `/publicador` | publica y programa reels y trial reels en tu Instagram con Zernio; trae las métricas | `metricas.csv` |
| 7 | Setter | `/setter` | comenta PALABRA → DM (ManyChat o Zernio) → setter IA con tu voz → llamada cualificada | `dms/` |

Si el usuario ya tenía una skill con alguno de esos nombres, el instalador no la pisa: ese agente queda como
`/contenido-<nombre>` (mira `~/Contenido/.sistema/equipo.json`). `M=~/.claude/skills/contenido/motor`.

## 01 · Las 5 preguntas (minuto 0–5)
Si `~/Contenido/cerebro/` ya existe y está relleno, enseña un resumen de 3 líneas (`python3 $M/datos.py cerebro`) y
pregunta solo si quiere cambiar algo; luego salta al paso 04.
Si no, AskUserQuestion en una tanda de 4 (opciones sacadas de lo que ya haya contado; siempre cabe «Otro») y la 5.ª en
texto libre:
1. **Tu nicho**: a qué te dedicas y de qué hablas en tus vídeos (3–5 temas).
2. **Tu oferta y su precio**: qué vendes, cuánto cuesta, enlace de agenda si lo tienes, y qué recurso regalas con
   «comenta PALABRA» (si regalas alguno).
3. **Tu avatar**: a quién quieres atraer (situación, qué quiere, qué le frena) y para quién NO es.
4. **Tu Instagram** (@) y 3 cuentas de tu nicho que te gustaría superar; cuántos reels quieres a la semana
   (recomendado 5 + 3 trial).
5. **Cómo hablas**: «Pega 3 guiones o transcripciones de reels tuyos tal cual, o pásame 3 enlaces de tus reels y los
   transcribo yo». Con enlaces: `python3 $M/reels.py url <enlaces>` y `python3 $M/reels.py transcribir ~/Contenido/referencias/sueltos`.
Después, opcional y en una línea: transcripciones de llamadas de venta, casos reales con números, y si tiene Zernio,
ManyChat, n8n o Apify. Si dice «tú decides», elige lo prudente y apúntalo.

## 02 · Instalar y crear el cerebro (minuto 5–8)
```bash
python3 ~/.claude/skills/contenido/motor/instalar.py
python3 $M/datos.py ajustes nombre="<su nombre>" marca="<su marca>" instagram=@<cuenta> reels_por_semana=5 trials_por_semana=3 palabra_clave=<PALABRA>
```
Crea `~/Contenido/` (cerebro, CSV, carpetas, `.env` vacío), instala los 7 agentes y descarga el motor `/editor` si falta.
Rellena el cerebro **con sus palabras literales**, editando las líneas de cada archivo:
`oferta.md` (oferta, precio, agenda, lead magnets, prueba) · `audiencia.md` (avatar, dolor, deseo, creencias, palabras
literales) · `nicho.md` (nicho, pilares, cuenta, cuentas que mira el analista) · `voz.md` (cómo habla, frases, palabras
que no usa, CTA y los 3 guiones pegados en «Ejemplos reales»; de esos guiones saca tú el tuteo, el ritmo y las
expresiones) · `llamadas-de-venta.md` (si dio transcripciones). Lo que no dio queda `PENDIENTE`.
**Nunca inventes** casos, cifras, testimonios ni enlaces.

## 03 · Primera prueba de cada agente (minuto 8–20)
Que vea al equipo trabajar con SUS datos antes de cerrar la terminal. Sigue la skill de cada agente y cuéntale en una
línea lo que hace cada uno mientras trabaja:
1. **Analista**: su cuenta (Zernio → Apify → lo que pegue) + 1–3 cuentas de su nicho (Apify, o 3 enlaces con
   `reels.py url`) → al menos 5 ideas en `ideas.csv` con múltiplo, gancho y por qué funciona.
2. **Estratega**: la semana en `calendario.csv`.
3. **Copywriter**: el guion completo de la primera pieza → bandeja. Pregúntale si suena a él; si no, corrige `voz.md`
   y reescríbelo (esta es la prueba que más importa).
4. **Editor**: `python3 ~/.claude/skills/editor/scripts/entorno.py` (y `--instalar` si falta algo). Si tiene un crudo a
   mano, edítalo ya; si no, dile que grabe el guion aprobado y lo deje en `~/Contenido/crudos/`.
5. **Publicador**: con `ZERNIO_API_KEY` en `~/Contenido/.env` → `zernio.py estado` y `zernio.py metricas`. Sin clave →
   `zernio.py --simular publicar …` para enseñarle lo que hará, y cómo sacar la clave (3 minutos).
6. **Setter**: flujo de la primera palabra clave en `dms/flujos/` + `python3 $M/setter_prompt.py --probar` (3
   conversaciones simuladas con su voz). Revisa `prueba.md` con él.
7. **Jefe**: `python3 $M/panel.py --servir` → ve su panel («Buenas noches, <nombre>»), lo que hizo cada agente y
   aprueba o pide cambios desde los botones.
Para el panel con lo que hizo cada uno, escribe antes `~/Contenido/partes/<fecha>/turno.json` (formato en la skill del jefe).
Si algo sale flojo (genérico, sin su voz, sin datos), corrige el cerebro o la plantilla instalada y repite esa parte.

## 04 · Turno de noche y panel (minuto 20–22)
```bash
python3 $M/noche.py programar --hora 00:00 --abrir 08:00
```
Cada noche: publicador (métricas) → analista → estratega → copywriter → (editor si hay crudos) → setter → el jefe
deja la bandeja y el panel; a las 8 se abre el panel. El Mac tiene que estar encendido y enchufado (imprime el comando
`pmset` para que se despierte solo). En Windows/Linux: `noche.py orden` da la orden para cron. Nada se publica ni se
envía sin su visto bueno. Comprobarlo: `noche.py estado`.

## 05 · Entregar
Corto: la tabla de agentes con su comando, la ruta del panel, qué quedó `PENDIENTE` en el cerebro y el siguiente paso
(normalmente: «aprueba el guion de mañana en el panel y grábalo; deja el vídeo en ~/Contenido/crudos/ y el resto lo
hacen ellos»). Desde ahora solo tiene que hablar con **/jefe**.

## Reglas
- **Un solo cerebro**: todo agente lee `datos.py cerebro` antes de trabajar y apunta lo que aprende con `datos.py aprende`.
  Si cambia la oferta, se cambia `oferta.md` y los siete se enteran.
- **Nada sale sin su visto bueno**: guiones, vídeos, publicaciones y automatizaciones pasan por la bandeja.
- **Nunca inventar** cifras, visitas, casos, testimonios ni enlaces. Sin dato, se dice o queda `PENDIENTE`.
- **Sus claves son suyas**: viven en `~/Contenido/.env`; nunca se escriben en el chat, en memoria ni en otros archivos.
- En español de España, tuteando, sin jerga técnica.

Hecha por Denis Corral · [Sell Your AI](https://sellyourai.io).

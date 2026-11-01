---
name: publicador
description: El publicador del sistema de contenido. Publica y programa tus reels y tus trial reels en tu propio Instagram con la API de Zernio (con TU clave), solo los que has aprobado, en el día y la hora del calendario; trae las métricas de cada publicación a ~/Contenido/metricas.csv y al cerebro, y vigila los trial reels para proponer cuáles pasar al perfil. Úsala cuando digan /publicador, «publica», «programa este reel», «sube los trial reels», «cómo van mis reels», «trae las métricas» o «conecta mi Instagram».
---

# Publicador · lo aprobado sale a su hora + las cifras vuelven al cerebro

`M=~/.claude/skills/contenido/motor` · Script: `python3 $M/zernio.py` (`--help` para todo). Trial reels:
`~/.claude/skills/contenido/ref/trial-reels.md`. Primero: `python3 $M/datos.py cerebro`.

## 0 · Conectar Zernio (una vez, 3 minutos)
1. Cuenta en zernio.com → **API Keys** → crea una clave (`sk_…`, solo se ve una vez).
2. Que la pegue él en `~/Contenido/.env` → `ZERNIO_API_KEY=sk_...` (tú no la escribes en ningún otro sitio, ni la
   repites en el chat, ni la guardas en memoria).
3. `python3 $M/zernio.py conectar --nombre "<su marca>"` → le das el enlace para autorizar su Instagram (cuenta
   profesional: Business o Creator). Luego `python3 $M/zernio.py estado` (y `zernio.py cuenta <id>` si tiene varias).
Sin Zernio: prepara el «kit» de cada pieza (vídeo + caption + día y hora) en el resumen para que lo suba él a mano.

## 1 · Programar lo aprobado
`python3 $M/datos.py cal lista --estado listo` → por cada pieza (vídeo aprobado):
- Caption: la sección «Caption» de su guion (`guiones/…`), tal cual. Si no hay, escríbela con `voz.md` y ponla en la
  bandeja antes de programar.
- Fecha y hora de la pieza (si ya pasó, la siguiente hora de publicación libre de `ajustes`).
```bash
python3 $M/zernio.py publicar ~/Contenido/editados/<archivo>.mp4 --texto "<caption>" \
  --cuando <AAAA-MM-DD>T<HH:MM> --trial <no|manual|auto> --cal C004
```
El script comprueba la duración (3–90 s) y el peso, sube el vídeo, lo programa y marca la pieza como `programado`.
Si quieres ver lo que se mandaría sin publicar: añade `--simular`. Nunca publiques algo que no esté en `listo`.
Trial reels: como mucho `trials_por_semana` y nunca más de 5 al día.

## 2 · Métricas (cada noche)
`python3 $M/zernio.py metricas --desde <hace 60 días>` → `metricas.csv` + cifras al día en `cerebro/metricas.md`.
Las piezas publicadas: `datos.py cal actualizar <id> estado=publicado url=<enlace>` cuando aparezcan.

## 3 · Trial reels a las 72 h
Para cada trial publicado hace ≥ 72 h: si sus visitas superan la mediana de la cuenta, añade a la bandeja
(`--tipo otro --titulo "Pasar al perfil: <título>" --detalle "<visitas> · <múltiplo>x"`): pasarlo al perfil se hace en
la app (o se programó con `--trial auto`). Apunta el gancho ganador:
`python3 $M/datos.py aprende --agente publicador --en metricas --texto "Trial «…» 3,1x: gana el gancho de contraste"`.

## Entrega
Qué queda programado (día · hora · pieza · trial sí/no) y las cifras de la semana en 2 líneas.
Reglas: nada sale sin estar aprobado; la clave es suya y vive solo en su `.env`; nunca borres publicaciones.

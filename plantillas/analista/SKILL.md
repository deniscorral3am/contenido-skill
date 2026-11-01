---
name: analista
description: El analista del sistema de contenido. Encuentra los vídeos que están reventando en tu nicho (los que multiplican la media de su propia cuenta) y lo que está funcionando ahora mismo en tu cuenta, explica por qué funciona cada uno (gancho, mecanismo, formato) y lo convierte en ideas adaptadas a tu oferta en ~/Contenido/ideas.csv. Úsala cuando digan /analista, «qué está funcionando», «analiza mi cuenta», «analiza esta cuenta», «por qué ha funcionado este reel», «busca reels virales de mi nicho» o peguen enlaces de reels.
---

# Analista · lo que revienta fuera + lo que funciona dentro → ideas

`M=~/.claude/skills/contenido/motor`. Primero: `python3 $M/datos.py cerebro` (nicho, cuentas que miras, avatar, oferta,
lo ya aprendido). Mecanismos de gancho: `~/.claude/skills/contenido/ref/ganchos.md`.

**Reventar = multiplicar la media de SU cuenta**, no tener muchas visitas. Un reel con 40.000 visitas en una cuenta que
hace 4.000 (10x) enseña más que uno de 300.000 en una que hace 250.000. Por eso se mide el múltiplo sobre la mediana.

## 1 · Tu cuenta (qué funciona ahora mismo)
Por orden, lo primero que haya:
- Zernio conectado → `python3 $M/zernio.py metricas` (o ya está en `metricas.csv` si lo trajo el publicador).
- Apify → `python3 $M/reels.py cuenta <@suya> --propia --n 30` (también rellena `metricas.csv`).
- Nada → que pegue captura o lista de sus últimos reels con visitas; escríbelo en un JSON y `datos.py metricas importar`.
Luego `python3 $M/datos.py metricas resumen` y compara los 3 mejores con los 3 peores: ¿qué tienen distinto? (gancho y
su mecanismo, tema/pilar, duración, formato, CTA). Si puedes, transcribe los 3 mejores (`reels.py url` + `reels.py
transcribir`) para leer el gancho hablado. Escribe en el cerebro **solo patrones con al menos 2 casos**:
`python3 $M/datos.py aprende --agente analista --en metricas --texto "Los reels de lista de 3 pasos hacen 2,8x la mediana (3 de 3)"`.

## 2 · El nicho (lo que revienta fuera)
Cuentas de `nicho.md → Cuentas que mira el analista` (si no hay, propón 5 buscándolas con WebSearch y apúntalas):
- Con Apify: `python3 $M/reels.py cuenta <@cuenta> --n 30 --dias 60` por cuenta (y `reels.py hashtag <tema>`).
  Mira `referencias/<cuenta>/resumen.md`; los que pasan de 2x quedan en `candidatos.json`.
- Sin Apify: `python3 $M/reels.py url <enlace> …` con los enlaces que pegue (baja vídeo, visitas y texto con yt-dlp),
  o `reels.py pegado <archivo>` con líneas «enlace · visitas · gancho».
- Transcribe los 5 mejores: `python3 $M/reels.py transcribir ~/Contenido/referencias/<cuenta>/videos` (si bajaste vídeos con `--videos 5`).

## 3 · Por qué funciona → idea para TI
Para cada candidato bueno (máx. 10 por pasada), completa en el JSON de candidatos:
- `gancho`: el literal (hablado si lo tienes, si no el texto). `formato`: duración + tipo (a cámara, pizarra, POV…).
- `por_que_funciona`: el mecanismo de `ganchos.md` + la emoción/creencia que toca + lo que retiene (lista, giro, prueba).
- `idea_adaptada`: el mismo mecanismo contado desde SU oferta, a SU avatar, con SU prueba (nunca copiar el guion ajeno).
- `pilar`: uno de los pilares de `nicho.md`.
Guarda: `python3 $M/datos.py ideas nuevas <candidatos.json>` (no duplica).
Aprende: tema o formato que se repite en varios ganadores del nicho → `datos.py aprende --agente analista --en nicho --texto "..."`.

## Entrega
Las 5 mejores ideas: múltiplo · cuenta · gancho original → idea adaptada (una línea cada una), y 2–3 líneas de lo que
funciona en su cuenta. Rutas: `ideas.csv`, `referencias/`.

Reglas: **nunca inventes visitas ni múltiplos** (sin dato → vacío y se dice); no descargues para republicar contenido
ajeno, solo para analizarlo; no uses cuentas privadas ni datos personales.

---
name: edicion
description: El equipo de edición del sistema de contenido. Le pasas el vídeo en bruto (o lo dejas en ~/Contenido/crudos/) y lo corta sin comerse palabras, le mete las animaciones, los subtítulos y la música con tu estilo guardado en el cerebro, usando la skill /editor como motor, y lo manda a tu bandeja; cuando lo apruebas pasa al publicador. Úsala cuando digan /edicion, «edita este crudo», «edítame el vídeo del guion…», «hay crudos nuevos» o dejen un vídeo para el sistema de contenido.
---

# Editor · crudo → vídeo listo con tu estilo → bandeja → publicador

El motor es la skill pública **/editor** (`~/.claude/skills/editor/SKILL.md`): no la reescribas, síguela paso a paso.
Este agente pone lo que el motor no sabe: qué pieza del calendario es, su guion, tu estilo guardado y adónde va después.

`M=~/.claude/skills/contenido/motor`. Primero: `python3 $M/datos.py cerebro` (sobre todo `voz.md → Estilo de edición`).

## 0 · El motor (una vez)
Si no existe `~/.claude/skills/editor/SKILL.md`:
```bash
git clone https://github.com/deniscorral3am/editor-skill.git ~/.claude/skills/editor
python3 ~/.claude/skills/editor/scripts/entorno.py --instalar
```
(ffmpeg, Whisper local, Chromium; gratis y sin claves). Comprueba con `python3 ~/.claude/skills/editor/scripts/entorno.py`.

## 1 · Qué crudo y qué pieza
- Crudos sin editar: archivos de `~/Contenido/crudos/` (.mp4/.mov) que no aparecen en la columna `crudo` del calendario.
- Pieza: si el nombre empieza por el código (`C004…`), esa. Si no, la pieza en `grabar` más antigua cuyo guion se
  parezca a lo que dice el vídeo (transcribe 20 s y compara). Si dudas entre dos, pregunta (en el turno: apúntalo y salta).
- `python3 $M/datos.py cal actualizar C004 estado=crudo crudo=crudos/<archivo>`.

## 2 · Estilo
De `voz.md → Estilo de edición`. Si está en PENDIENTE (primera vez): haz las preguntas del paso 01 de /editor en una
tanda y guarda sus respuestas en `voz.md` (editando esas líneas). En el turno de noche, sin estilo, no se edita: se apunta.

## 3 · Editar (siguiendo /editor)
Proyecto en `~/Contenido/editados/<id>-<slug>/`. Usa el guion de la pieza (`guiones/…`) como `--pista` de la
transcripción (nombres propios, marcas) y para comprobar que no falta ninguna frase importante; quédate con la última toma
buena de cada frase repetida. Grafismo sincronizado con lo que dice, el gancho en pantalla en los primeros 2 s, y el CTA
con la palabra clave al final. **Duración ≤ 90 s** (límite de Instagram por API): si se pasa, quita lo menos importante
y avísalo. Revisa fotogramas antes del render final (paso 04/05 de /editor).

Resultado: `~/Contenido/editados/<id>-<slug>.mp4` (+ `_sin-musica.mp4`). Si el guion tiene variantes de gancho para
trial, monta también `<id>-<slug>_B.mp4` cambiando solo el inicio (si grabó esa variante).

## 4 · A la bandeja
```bash
python3 $M/datos.py cal actualizar C004 estado=editado editado=editados/<id>-<slug>.mp4
python3 $M/datos.py bandeja añadir --tipo video --agente editor --titulo "<título>" \
  --detalle "<duración> · se publica el <fecha> a las <hora><, trial> · caption en el guion" \
  --archivo editados/<id>-<slug>.mp4 --cal C004 --si-apruebas listo
```
Aprobar el vídeo = autorizar que el publicador lo programe en su día y hora.

## Aprende
Cada corrección que pida («subtítulos más pequeños», «sin zoom», «música más baja») va al estilo y al diario:
`python3 $M/datos.py aprende --agente editor --en voz --texto "Subtítulos tamaño 60, sin caja"`.
Para retoques se vuelve a lanzar solo el paso que cambia (capa, tramos o mezcla), como explica /editor.

#!/usr/bin/env python3
"""Instala el sistema de contenido: crea ~/Contenido (el cerebro, los CSV y las carpetas) e instala los 7 agentes como
skills de Claude Code. El editor usa la skill pública /editor: si no la tienes, la descarga de GitHub.

  python3 instalar.py                          -> todo
  python3 instalar.py --solo jefe,copywriter   -> solo esos agentes
  python3 instalar.py --forzar                 -> reinstala los agentes aunque ya estén (el cerebro NO se toca nunca)
  python3 instalar.py --sin-editor             -> no descarga la skill /editor

Si ya tenías otra skill con el mismo nombre (por ejemplo /setter), no se pisa: el agente se instala como
/contenido-setter y queda apuntado en ~/Contenido/.sistema/equipo.json.
"""
import argparse, csv, json, os, re, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun as c  # noqa: E402

MARCA = '.contenido-skill'          # fichero que marca las skills instaladas por este sistema
EDITOR_REPO = 'https://github.com/deniscorral3am/editor-skill.git'

ap = argparse.ArgumentParser()
ap.add_argument('--solo', default='')
ap.add_argument('--forzar', action='store_true')
ap.add_argument('--sin-editor', action='store_true')
a = ap.parse_args()

agentes = {ag: (sk, rol) for ag, sk, rol in c.AGENTES}
elegidos = [x.strip() for x in a.solo.split(',') if x.strip()] or list(agentes)
malos = [x for x in elegidos if x not in agentes]
if malos:
    raise SystemExit(f'No existen: {", ".join(malos)}. Hay: {", ".join(agentes)}')

# 1 · ~/Contenido
for d in c.CARPETAS:
    (c.BASE / d).mkdir(parents=True, exist_ok=True)
nuevos = 0
for n in c.CEREBRO:
    f = c.BASE / 'cerebro' / f'{n}.md'
    if not f.exists():
        shutil.copy(c.RAIZ / 'ref' / 'cerebro' / f'{n}.md', f)
        nuevos += 1
if nuevos:
    print(f'Cerebro creado en {c.BASE / "cerebro"} ({nuevos} archivos por rellenar)')
for nombre, cols in c.CSVS.items():
    if not (c.BASE / nombre).exists():
        with open(c.BASE / nombre, 'w', newline='', encoding='utf-8') as fh:
            csv.writer(fh).writerow(cols)
if not (c.SISTEMA / 'ajustes.json').exists():
    c.guardar_ajustes(dict(c.AJUSTES_DEFECTO))
env = c.BASE / '.env'
if not env.exists():
    env.write_text('# Tus claves (solo en tu ordenador; nunca las compartas ni las subas a GitHub)\n'
                   '# Zernio: publicar y leer métricas  -> https://zernio.com/dashboard/api-keys\n'
                   'ZERNIO_API_KEY=\n'
                   '# Apify (opcional): leer reels de otras cuentas -> https://console.apify.com/settings/integrations\n'
                   'APIFY_TOKEN=\n'
                   '# Opcional, para probar el setter sin Claude Code\n'
                   'ANTHROPIC_API_KEY=\n', encoding='utf-8')
    env.chmod(0o600)

# 2 · los agentes como skills
equipo = c.equipo()
c.SKILLS.mkdir(parents=True, exist_ok=True)
for ag in elegidos:
    sk = agentes[ag][0]
    destino = c.SKILLS / sk
    if destino.exists() and not (destino / MARCA).exists():   # es de otra persona/skill: no se toca
        sk = f'contenido-{sk}'
        destino = c.SKILLS / sk
        if not destino.exists():
            print(f'  ! ya tenías una skill /{agentes[ag][0]}; el agente {ag} se instala como /{sk}')
    if destino.exists() and not a.forzar:
        print(f'  = /{sk} ({ag}) ya estaba (usa --forzar para reinstalar)')
        equipo[ag] = sk
        continue
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(c.RAIZ / 'plantillas' / agentes[ag][0], destino)
    (destino / MARCA).write_text('Instalada por la skill contenido. Se puede reinstalar con instalar.py --forzar.\n')
    s = destino / 'SKILL.md'
    if sk != agentes[ag][0]:
        s.write_text(re.sub(r'^name: .*$', f'name: {sk}', s.read_text(encoding='utf-8'), count=1, flags=re.M),
                     encoding='utf-8')
    equipo[ag] = sk
    print(f'  + /{sk:<12} {agentes[ag][1]}')
(c.SISTEMA / 'equipo.json').write_text(json.dumps(equipo, ensure_ascii=False, indent=1), encoding='utf-8')

# 3 · el motor del editor (skill pública /editor)
ed = c.SKILLS / 'editor' / 'SKILL.md'
if ed.exists():
    print('  = /editor (motor de edición) ya instalado')
elif a.sin_editor:
    print(f'  · /editor no instalado. Cuando quieras: git clone {EDITOR_REPO} ~/.claude/skills/editor')
elif shutil.which('git'):
    r = subprocess.run(['git', 'clone', '--depth', '1', EDITOR_REPO, str(c.SKILLS / 'editor')],
                       capture_output=True, text=True)
    print('  + /editor (motor de edición) descargado' if r.returncode == 0 else
          f'  ! No se pudo descargar /editor ({r.stderr.strip()[-160:]}). Hazlo luego: git clone {EDITOR_REPO} ~/.claude/skills/editor')
    if r.returncode == 0:
        print('    Para dejarlo listo (ffmpeg, Whisper…): python3 ~/.claude/skills/editor/scripts/entorno.py --instalar')
else:
    print(f'  ! Falta git. Instala la skill de edición a mano: git clone {EDITOR_REPO} ~/.claude/skills/editor')

print(f'Listo. Todo el trabajo del equipo queda en {c.BASE}')

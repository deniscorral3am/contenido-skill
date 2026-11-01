#!/usr/bin/env python3
"""El turno de noche del equipo de contenido: mientras duermes, el publicador trae las métricas, el analista busca lo que
está reventando, el estratega rehace el plan, el copywriter escribe los guiones y el jefe te deja la bandeja y el panel.

  noche.py programar [--hora 00:00] [--abrir 08:00]   -> cada noche (macOS, launchd) y por la mañana abre el panel
  noche.py ahora                                      -> lanza el turno ya, para probarlo
  noche.py estado                                     -> si está programado y cómo fue la última noche
  noche.py quitar                                     -> lo desprograma
  noche.py orden                                      -> imprime la orden exacta (para cron o el Programador de tareas)

Es Claude Code sin ventana (claude -p) siguiendo la skill del jefe, con permiso solo para leer y escribir archivos,
buscar en la web y ejecutar los scripts del sistema. Nunca publica ni envía nada: lo deja en tu bandeja.
"""
import argparse, plistlib, shutil, subprocess, sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun as c  # noqa: E402

LOGS = c.SISTEMA / 'logs'
LA = Path.home() / 'Library' / 'LaunchAgents'
ID_TURNO, ID_ABRIR = 'io.sellyourai.contenido-turno', 'io.sellyourai.contenido-panel'
HERRAMIENTAS = ('Read Write Edit Glob Grep WebSearch WebFetch Skill Bash(python3:*) Bash(yt-dlp:*) Bash(ffprobe:*) '
                'Bash(ffmpeg:*) Bash(node:*) Bash(mkdir:*) Bash(ls:*) Bash(date:*)')


def prompt():
    jefe = c.equipo()['jefe']
    return (f'Usa la skill {jefe} y haz el TURNO DE NOCHE completo del sistema de contenido. Trabaja solo, sin preguntar '
            'nada: si falta un dato, apúntalo como pendiente en la bandeja y sigue. No publiques ni envíes nada.')


def guion():
    claude = shutil.which('claude') or str(Path.home() / '.local' / 'bin' / 'claude')
    LOGS.mkdir(parents=True, exist_ok=True)
    s = c.SISTEMA / 'noche.sh'
    s.write_text(f'''#!/bin/zsh -l
# Turno de noche del sistema de contenido. Lo lanza launchd ({ID_TURNO}). Log en {LOGS}/
cd "{c.BASE}" || exit 1
F=$(date +%Y-%m-%d)
echo "inicio $(date +%H:%M)" > "{LOGS}/$F.log"
caffeinate -i "{claude}" -p "{prompt()}" \\
  --permission-mode acceptEdits --allowedTools {' '.join(repr(h) for h in HERRAMIENTAS.split())} \\
  --add-dir "{c.RAIZ}" --add-dir "{c.SKILLS}" >> "{LOGS}/$F.log" 2>&1
echo "fin $(date +%H:%M) codigo $?" >> "{LOGS}/$F.log"
python3 "{c.RAIZ / 'motor' / 'panel.py'}" --no-abrir >> "{LOGS}/$F.log" 2>&1
''', encoding='utf-8')
    s.chmod(0o755)
    return s


def plist(ident, args, hora):
    h, m = (int(x) for x in hora.split(':'))
    LA.mkdir(parents=True, exist_ok=True)
    ruta = LA / f'{ident}.plist'
    subprocess.run(['launchctl', 'unload', str(ruta)], capture_output=True)
    ruta.write_bytes(plistlib.dumps({'Label': ident, 'ProgramArguments': args,
                                     'StartCalendarInterval': {'Hour': h, 'Minute': m},
                                     'StandardOutPath': str(LOGS / f'{ident}.out'),
                                     'StandardErrorPath': str(LOGS / f'{ident}.err')}))
    subprocess.run(['launchctl', 'load', str(ruta)], check=True)


def programar(hora, abrir):
    s = guion()
    plist(ID_TURNO, ['/bin/zsh', '-l', str(s)], hora)
    aj = c.ajustes(); aj['hora_turno'], aj['hora_panel'] = hora, abrir or ''; c.guardar_ajustes(aj)
    print(f'✓ Turno de noche programado a las {hora} (cada día).')
    if abrir:
        plist(ID_ABRIR, ['/usr/bin/open', str(c.BASE / 'PANEL.html')], abrir)
        print(f'✓ A las {abrir} se abre tu panel.')
    hh = int(hora[:2])
    print('Si el Mac está dormido a esa hora, el turno arranca en cuanto se despierta. Para que se despierte solo:\n'
          f'  sudo pmset repeat wakeorpoweron MTWRFSU {(hh - 1) % 24:02d}:58:00\n'
          'Déjalo enchufado y con la tapa abierta (o con monitor externo).')


def ahora():
    s = guion()
    log = LOGS / f'{date.today().isoformat()}.log'
    print(f'Lanzando el turno… (log en {log})')
    subprocess.run(['/bin/zsh', '-l', str(s)])
    print(log.read_text(encoding='utf-8')[-1500:] if log.exists() else '(sin log)')


def estado():
    for ident in (ID_TURNO, ID_ABRIR):
        ok = (LA / f'{ident}.plist').exists()
        print(f'{"✓" if ok else "·"} {ident}: {"programado" if ok else "no programado"}')
    logs = sorted(LOGS.glob('20*.log')) if LOGS.exists() else []
    if logs:
        print(f'\nÚltima noche ({logs[-1].stem}):')
        print(logs[-1].read_text(encoding='utf-8')[-800:])


def quitar():
    for ident in (ID_TURNO, ID_ABRIR):
        ruta = LA / f'{ident}.plist'
        if ruta.exists():
            subprocess.run(['launchctl', 'unload', str(ruta)], capture_output=True)
            ruta.unlink()
            print(f'✗ {ident} quitado')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('programar'); p.add_argument('--hora', default='00:00'); p.add_argument('--abrir', default='08:00')
    for n in ('ahora', 'estado', 'quitar', 'orden'):
        sub.add_parser(n)
    a = ap.parse_args()
    if a.cmd == 'orden':
        print(f'cd "{c.BASE}" && claude -p "{prompt()}" --permission-mode acceptEdits --allowedTools '
              + ' '.join(repr(h) for h in HERRAMIENTAS.split()))
        sys.exit()
    if sys.platform != 'darwin' and a.cmd in ('programar', 'ahora'):
        raise SystemExit('El programador automático es para macOS. En Windows/Linux usa cron o el Programador de tareas '
                         'con la orden de: python3 noche.py orden')
    {'programar': lambda: programar(a.hora, a.abrir), 'ahora': ahora, 'estado': estado, 'quitar': quitar}[a.cmd]()

#!/usr/bin/env python3
"""El panel: lo que han hecho tus 7 agentes, lo que espera tu visto bueno (con botón de aprobar), lo que toca grabar,
el calendario, las métricas y lo que ha aprendido el cerebro. En una página: ~/Contenido/PANEL.html

  panel.py                   -> genera ~/Contenido/PANEL.html (y lo abre en Mac)
  panel.py --no-abrir
  panel.py --servir [--puerto 8765]
                             -> lo abre en http://127.0.0.1:8765 y los botones Aprobar / Cambiar guardan solos
                                (sin servidor, el botón copia la orden para pegarla en la terminal o decírsela al jefe)
  panel.py --salida ruta.html  -> generarlo en otro sitio (lo usa el ejemplo)

Lee: partes/<fecha>/turno.json (lo que dejó el jefe al cerrar el turno), bandeja/, calendario.csv, ideas.csv,
metricas.csv y cerebro/aprendizajes.md. Las cifras salen de los CSV, nunca se escriben a mano.
"""
import argparse, json, subprocess, sys, threading, webbrowser
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun as c  # noqa: E402
import datos  # noqa: E402
from estilo import esc, pagina  # noqa: E402

DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre',
         'noviembre', 'diciembre']
TIPOS = {'guion': 'guion', 'video': 'vídeo', 'flujo': 'automatización', 'idea': 'idea', 'publicacion': 'publicación',
         'otro': 'otro'}
EXTRA_CSS = """
h1,h2{text-transform:lowercase}
.saludo{font-size:clamp(40px,7vw,68px)}
.ejemplo{display:inline-block;margin-bottom:22px;font-size:12px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;
color:#1A1406;background:linear-gradient(100deg,#C9A35A,#DDBE7C 70%,#F2DDA8);padding:6px 12px;border-radius:999px}
.aviso{font-size:13px;color:var(--tx3);margin-top:10px}
.aviso code,.mut3 code{background:var(--card2);border:1px solid var(--line);border-radius:6px;padding:1px 6px;color:var(--tx2)}
.acciones{display:flex;gap:10px;margin-top:14px;flex-wrap:wrap}
.b{font:600 14px Inter,system-ui,sans-serif;border-radius:999px;padding:10px 20px;cursor:pointer;border:1px solid var(--line2);
background:transparent;color:var(--tx)}
.b.si{background:linear-gradient(100deg,#C9A35A,#DDBE7C 70%,#F2DDA8);color:#1A1406;border:0}
.b:hover{filter:brightness(1.08)}
.hecho .acciones{display:none} .hecho{opacity:.55}
.estado{font-size:13px;margin-top:10px;color:var(--ac);display:none} .hecho .estado{display:block}
.prev{max-height:220px;overflow:auto}
video{width:100%;max-width:300px;border-radius:14px;margin-top:10px;background:#111}
.num{width:44px;height:44px;border-radius:50%;flex:none;display:grid;place-items:center;font-weight:700;font-size:17px;
color:#1A1406;background:linear-gradient(140deg,#C9A35A,#DDBE7C 60%,#F2DDA8)}
.num.off{background:var(--card2);color:var(--tx3);border:1px solid var(--line2)}
.barra{height:6px;border-radius:99px;background:linear-gradient(90deg,#C9A35A,#DDBE7C 70%,#F2DDA8);margin-top:6px}
.cerebro li{list-style:none;padding:9px 0;border-top:1px solid var(--line);color:var(--tx2);font-size:14.5px}
.cerebro li:first-child{border-top:0} .cerebro b{color:var(--ac);font-weight:600}
"""
JS = """
const SERVIDOR = location.protocol.startsWith('http');
function marcar(id, dec, cmd){
  const el = document.getElementById('b-' + id); if(!el) return;
  el.classList.add('hecho');
  el.querySelector('.estado').innerHTML = (dec === 'aprobado' ? '✓ Aprobado' : '↺ Devuelto al equipo con tu nota') +
    (cmd ? '<br><span class="mut3">Orden copiada. Pégala en la terminal o dile al jefe: «' + (dec === 'aprobado' ? 'apruebo ' : 'cambia ') + id + '»</span>' : '');
}
async function decidir(id, dec){
  let nota = '';
  if(dec === 'rechazado'){ nota = prompt('¿Qué cambiarías? El equipo aprende de esto.'); if(nota === null || !nota.trim()) return; }
  if(SERVIDOR){
    const r = await fetch('/api/decidir', {method:'POST', headers:{'content-type':'application/json'},
                                          body: JSON.stringify({id, decision: dec, nota})});
    if(!r.ok){ alert('No se ha podido guardar: ' + await r.text()); return; }
    marcar(id, dec);
  } else {
    const cmd = 'python3 ~/.claude/skills/contenido/motor/datos.py bandeja ' + (dec === 'aprobado' ? 'aprobar ' : 'rechazar ') + id +
                (nota ? ' --nota "' + nota.replace(/"/g, "'") + '"' : '');
    try { navigator.clipboard.writeText(cmd); } catch(e) {}
    try { localStorage.setItem('dec-' + id, dec); } catch(e) {}
    marcar(id, dec, cmd);
  }
}
if(!SERVIDOR){ document.querySelectorAll('[data-id]').forEach(el => {
  let d = null; try { d = localStorage.getItem('dec-' + el.dataset.id); } catch(e) {}
  if(d) marcar(el.dataset.id, d, true); }); }
else { const a = document.getElementById('aviso-servidor'); if(a) a.remove(); }
"""


def miles(n):
    return f'{int(c.num(n)):,}'.replace(',', '.')


def saludo(h):
    return 'buenos días' if 6 <= h < 14 else 'buenas tardes' if 14 <= h < 21 else 'buenas noches'


def ultimo_turno():
    ts = sorted(c.BASE.glob('partes/*/turno.json'))
    return json.loads(ts[-1].read_text(encoding='utf-8')) if ts else {}


def previa(archivo):
    if not archivo:
        return ''
    f = c.BASE / archivo
    if archivo.lower().endswith(('.mp4', '.mov')):
        if f.exists():
            return f'<video src="{esc(archivo)}" controls preload="metadata" playsinline></video>'
        return f'<p class="mut3">vídeo: {esc(archivo)}</p>'
    if f.exists() and f.suffix in ('.md', '.txt'):
        t = f.read_text(encoding='utf-8')
        return f'<div class="msg prev">{esc(t[:1400])}{"…" if len(t) > 1400 else ""}</div>'
    return f'<p class="mut3">{esc(archivo)}</p>'


def generar(salida=None, ahora=None):
    ahora = ahora or datetime.now()
    aj, r, t = c.ajustes(), datos.resumen(), ultimo_turno()
    nombre = (aj.get('nombre') or '').split(' ')[0]
    h = []
    if aj.get('ejemplo'):
        h.append('<div class="ejemplo">Ejemplo · datos ficticios</div>')
    h.append(f'<div class="eyebrow">Tu sistema de contenido · {DIAS[ahora.weekday()]} {ahora.day} de {MESES[ahora.month - 1]}</div>')
    h.append(f'<h1 class="saludo">{saludo(ahora.hour)}{", " + esc(nombre.lower()) if nombre else ""}.</h1>')
    sub = t.get('titular') or 'Tu equipo está listo. Esta noche empieza a trabajar.'
    turno = f' El turno empezó a las {esc(t["inicio"])} y terminó a las {esc(t.get("fin", "--:--"))}.' if t.get('inicio') else ''
    h.append(f'<p class="sub">{esc(sub)}{turno} No ha salido nada sin tu visto bueno.</p>')

    kpis = [(r['pendientes_aprobar'], 'esperan tu visto bueno'), (r['para_grabar'], 'guiones listos para grabar'),
            (r['calendario'].get('programado', 0), 'reels programados'), (r['ideas_nuevas'], 'ideas en la recámara'),
            (miles(r['visitas_7d']), 'visitas en 7 días'), (miles(r['mediana_visitas']), 'visitas medianas por reel')]
    h.append('<div class="grid">' + ''.join(f'<div class="kpi"><b>{esc(v)}</b><span>{esc(x)}</span></div>' for v, x in kpis) + '</div>')

    # --- bandeja
    items = c.bandeja()
    h.append('<div class="sec"><div class="eyebrow">Te lo trae el jefe de gabinete</div>')
    if items:
        h.append(f'<h2>{len(items)} {"cosa necesita" if len(items) == 1 else "cosas necesitan"} tu visto bueno.</h2>')
        h.append('<p class="aviso" id="aviso-servidor">Para que los botones guarden solos, abre el panel con '
                 '<code>python3 ~/.claude/skills/contenido/motor/panel.py --servir</code>. Desde aquí, el botón copia la orden.</p>')
        for it in items:
            h.append(f'<div class="card" id="b-{esc(it["id"])}" data-id="{esc(it["id"])}">'
                     f'<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">'
                     f'<span class="tag ac">{esc(TIPOS.get(it["tipo"], it["tipo"]))}</span>'
                     f'<span class="mut3">{esc(it["id"])} · de {esc(it["agente"])} · {esc(it["creado"])}</span></div>'
                     f'<h3 style="margin-top:10px">{esc(it["titulo"])}</h3>'
                     f'<p class="mut">{esc(it.get("detalle", ""))}</p>{previa(it.get("archivo", ""))}'
                     f'<div class="acciones"><button class="b si" onclick="decidir(\'{esc(it["id"])}\',\'aprobado\')">Aprobar</button>'
                     f'<button class="b" onclick="decidir(\'{esc(it["id"])}\',\'rechazado\')">Pedir cambios</button></div>'
                     f'<div class="estado"></div></div>')
    else:
        h.append('<h2>nada pendiente.</h2><p class="mut">Cuando el equipo prepare guiones, vídeos o automatizaciones, aparecerán aquí.</p>')
    h.append('</div>')

    # --- el equipo
    hecho = {a.get('agente'): a for a in t.get('agentes', [])}
    h.append('<div class="sec"><div class="eyebrow">Siete agentes, un solo cerebro</div><h2>lo que ha hecho tu equipo.</h2><div class="card">')
    for i, (ag, _, rol) in enumerate(c.AGENTES, 1):
        a = hecho.get(ag)
        h.append(f'<div class="row"><div class="num{"" if a else " off"}">{i}</div><div style="flex:1">'
                 f'<h3>{esc(rol)}</h3><p class="mut">{esc(a["hecho"]) if a else "Sin trabajo en este turno."}</p>')
        for x in (a or {}).get('items', [])[:4]:
            tag = f' <span class="tag {esc(x.get("tipo", ""))}">{esc(x["etiqueta"])}</span>' if x.get('etiqueta') else ''
            enl = f' · <a href="{esc(x["enlace"])}">abrir</a>' if x.get('enlace') else ''
            h.append(f'<p class="mut3" style="margin-top:6px"><span style="color:var(--tx)">{esc(x["titulo"])}</span>{tag}'
                     f'{" · " + esc(x["detalle"]) if x.get("detalle") else ""}{enl}</p>')
        h.append('</div></div>')
    h.append('</div></div>')

    # --- grabar
    cal = c.leer('calendario.csv')
    grabar = [x for x in cal if x['estado'] == 'grabar']
    if grabar:
        h.append(f'<div class="sec"><div class="eyebrow">Tú solo grabas</div><h2>{len(grabar)} {"guion listo" if len(grabar) == 1 else "guiones listos"} para grabar.</h2>'
                 '<p class="mut">Graba y deja el vídeo en <code>~/Contenido/crudos/</code> con el código delante (p. ej. '
                 '<code>C004.mov</code>). El editor hace el resto.</p><div class="card">')
        for x in grabar:
            enl = f' · <a href="{esc(x["guion"])}">guion</a>' if x.get('guion') else ''
            h.append(f'<div class="row"><span class="tag ac">{esc(x["id"])}</span><div style="flex:1"><h3>{esc(x["titulo"])}</h3>'
                     f'<p class="mut3">«{esc(x.get("gancho", ""))}» · para el {esc(x["fecha"])}{enl}</p></div></div>')
        h.append('</div></div>')

    # --- calendario
    hoy_, fin = date.today().isoformat(), (date.today() + timedelta(days=7)).isoformat()
    prox = [x for x in cal if hoy_ <= x['fecha'] <= fin and x['estado'] != 'descartado']
    h.append('<div class="sec"><div class="eyebrow">El plan del estratega</div><h2>los próximos 7 días.</h2>')
    if prox:
        h.append('<div class="card" style="overflow-x:auto"><table><tr><th>Día</th><th>Pieza</th><th>Embudo</th><th>Estado</th></tr>')
        for x in prox:
            d = datetime.strptime(x['fecha'], '%Y-%m-%d')
            trial = ' <span class="tag">trial</span>' if x.get('trial') == 'si' else ''
            h.append(f'<tr><td>{DIAS[d.weekday()][:3]} {d.day} · {esc(x.get("hora", ""))}</td><td>{esc(x["titulo"])}{trial}</td>'
                     f'<td>{esc(x.get("embudo", ""))}</td><td><span class="tag {"ok" if x["estado"] in ("programado", "publicado") else ""}">'
                     f'{esc(x["estado"])}</span></td></tr>')
        h.append('</table></div>')
    else:
        h.append('<p class="mut">Todavía no hay plan. Pídeselo al jefe: «/jefe planifica la semana».</p>')
    h.append('</div>')

    # --- métricas
    m = datos.resumen_metricas()
    h.append('<div class="sec"><div class="eyebrow">Lo que mide el publicador</div><h2>lo que está funcionando.</h2>')
    if m['mejores']:
        top = max(c.num(x['visitas']) for x in m['mejores']) or 1
        h.append('<div class="card">')
        for x in m['mejores']:
            v = c.num(x['visitas'])
            enl = f' · <a href="{esc(x["url"])}">ver</a>' if x.get('url') else ''
            h.append(f'<div class="row" style="display:block"><div style="display:flex;justify-content:space-between;gap:12px">'
                     f'<h3>{esc(x["titulo"])}</h3><span class="mut" style="white-space:nowrap">{miles(v)} · {x["multiplo"]}x</span></div>'
                     f'<div class="barra" style="width:{max(4, v / top * 100):.0f}%"></div>'
                     f'<p class="mut3">{esc(x.get("fecha", "")[:10])}{" · trial" if x.get("trial") == "si" else ""}{enl}</p></div>')
        h.append(f'</div><p class="aviso">Mediana de la cuenta: {miles(m["mediana_visitas"])} visitas. '
                 '«2x» = el doble de lo normal.</p>')
    else:
        h.append('<p class="mut">Sin métricas todavía. Con Zernio conectado llegan solas cada noche '
                 '(<code>zernio.py metricas</code>).</p>')
    h.append('</div>')

    # --- cerebro
    ap = c.ultimas_lineas('aprendizajes.md', 8)
    h.append('<div class="sec"><div class="eyebrow">El cerebro común</div><h2>lo que ha aprendido.</h2>')
    if ap:
        h.append('<div class="card"><ul class="cerebro">')
        for l in reversed(ap):
            fecha, resto = l.split(' · ', 1)
            quien, txt = resto.split(':', 1) if ':' in resto else ('', resto)
            h.append(f'<li><b>{esc(quien)}</b> · {esc(txt.strip())} <span class="mut3">· {esc(fecha)}</span></li>')
        h.append('</ul></div>')
    else:
        h.append('<p class="mut">Aún nada. Cada agente apunta aquí lo que descubre de tu audiencia, tu nicho y tu forma de hablar.</p>')
    pend = c.pendientes_cerebro()
    if pend:
        h.append(f'<p class="aviso">Faltan {len(pend)} datos en el cerebro (el equipo no se los inventa): '
                 f'{esc(", ".join(pend[:4]))}{"…" if len(pend) > 4 else ""}. Díselos al jefe cuando puedas.</p>')
    h.append('</div>')

    marca = aj.get('marca') or aj.get('nombre') or ''
    h.append(f'<p class="pie">{esc(marca) + " · " if marca else ""}7 agentes, un solo cerebro · hecho con Claude</p>')
    html = pagina(f'Panel · {ahora:%d/%m}', ''.join(h)).replace('</style>', EXTRA_CSS + '</style>', 1)
    js = JS.replace("location.protocol.startsWith('http')", 'false') if aj.get('ejemplo') else JS
    html = html.replace('</body>', f'<script>{js}</script></body>')
    out = Path(salida).expanduser() if salida else c.BASE / 'PANEL.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    return out


class Manejador(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def responder(self, codigo, cuerpo, tipo='text/plain; charset=utf-8'):
        b = cuerpo if isinstance(cuerpo, bytes) else cuerpo.encode()
        self.send_response(codigo)
        self.send_header('Content-Type', tipo)
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        ruta = unquote(urlparse(self.path).path).lstrip('/')
        if ruta in ('', 'PANEL.html'):
            return self.responder(200, generar().read_bytes(), 'text/html; charset=utf-8')
        f = (c.BASE / ruta).resolve()
        if c.BASE.resolve() not in f.parents or not f.is_file() or '.env' in f.name or '.sistema' in f.parts:
            return self.responder(404, 'no')
        tipo = {'.mp4': 'video/mp4', '.mov': 'video/quicktime', '.md': 'text/plain; charset=utf-8',
                '.txt': 'text/plain; charset=utf-8', '.csv': 'text/plain; charset=utf-8',
                '.html': 'text/html; charset=utf-8'}.get(f.suffix.lower(), 'application/octet-stream')
        self.responder(200, f.read_bytes(), tipo)

    def do_POST(self):
        if urlparse(self.path).path != '/api/decidir':
            return self.responder(404, 'no')
        try:
            d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
            if d.get('decision') not in ('aprobado', 'rechazado'):
                raise ValueError('decisión no válida')
            it = c.bandeja_decidir(str(d['id']), d['decision'], str(d.get('nota', ''))[:1000])
            self.responder(200, json.dumps(it, ensure_ascii=False), 'application/json')
        except (SystemExit, ValueError, KeyError) as e:
            self.responder(400, str(e))


def servir(puerto):
    for p in range(puerto, puerto + 20):      # si el puerto está ocupado, el siguiente libre
        try:
            srv = ThreadingHTTPServer(('127.0.0.1', p), Manejador)
            puerto = p
            break
        except OSError:
            continue
    else:
        raise SystemExit(f'No hay ningún puerto libre entre {puerto} y {puerto + 19}.')
    url = f'http://127.0.0.1:{puerto}/'
    print(f'Panel en {url}  (Ctrl+C para cerrarlo)', flush=True)
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-abrir', action='store_true')
    ap.add_argument('--servir', action='store_true')
    ap.add_argument('--puerto', type=int, default=8765)
    ap.add_argument('--salida', default='')
    a = ap.parse_args()
    if not (c.BASE / 'cerebro').exists():
        raise SystemExit(f'No existe {c.BASE}. Primero: python3 {c.RAIZ / "motor" / "instalar.py"}')
    if a.servir:
        servir(a.puerto)
    else:
        out = generar(a.salida or None)
        print(out)
        if not a.no_abrir and sys.platform == 'darwin':
            subprocess.run(['open', str(out)])

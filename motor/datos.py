#!/usr/bin/env python3
"""Los datos del sistema de contenido (todo en ~/Contenido). Lo usan los 7 agentes para no pisarse.

CEREBRO
  datos.py cerebro                              -> imprime el cerebro entero (lo leen todos antes de trabajar)
  datos.py aprende --agente analista --en nicho --texto "Los reels de 3 pasos doblan la media"
                                                -> lo apunta en aprendizajes.md y en nicho.md (en = audiencia|nicho|voz|
                                                   oferta|llamadas-de-venta|metricas|aprendizajes)
IDEAS (analista)
  datos.py ideas nuevas <archivo.json>          -> lista de {fuente, cuenta, url, visitas, mediana_cuenta, formato,
                                                   gancho, por_que_funciona, idea_adaptada, pilar}; no duplica
  datos.py ideas lista [--estado nueva] [--top 10]
  datos.py ideas marcar <id> estado=al_plan|descartada
CALENDARIO (estratega, copywriter, editor, publicador)
  datos.py cal nuevo <archivo.json>             -> lista de {fecha, hora, pilar, embudo, formato, titulo, idea_id, gancho,
                                                   palabra_clave, trial}
  datos.py cal lista [--estado guion] [--dias 7]
  datos.py cal actualizar <id> estado=grabar guion=guiones/x.md ...
MÉTRICAS (publicador)
  datos.py metricas importar <archivo.json>     -> lista de {post_id, fecha, titulo, url, trial, visitas, ...}; actualiza
  datos.py metricas resumen                     -> mediana, mejores y peores (JSON)
BANDEJA (lo que necesita tu visto bueno)
  datos.py bandeja añadir --tipo guion|video|flujo|idea|otro --agente copywriter --titulo "..." [--detalle "..."]
                          [--archivo guiones/x.md] [--cal C004] [--si-apruebas grabar]
  datos.py bandeja lista [--todas]
  datos.py bandeja aprobar <id> [--nota "..."]
  datos.py bandeja rechazar <id> --nota "por qué"
OTROS
  datos.py ajustes [clave=valor ...]            -> ver o cambiar ajustes (nombre, instagram, reels_por_semana…)
  datos.py resumen                              -> cifras para el panel y el jefe (JSON)
"""
import argparse, json, sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun as c  # noqa: E402


def cargar_json(ruta):
    d = json.loads(Path(ruta).expanduser().read_text(encoding='utf-8'))
    return d if isinstance(d, list) else d.get('items', [d])


def pares(lista):
    out = {}
    for x in lista:
        if '=' not in x:
            raise SystemExit(f'«{x}» no es campo=valor')
        k, v = x.split('=', 1)
        out[k.strip()] = v
    return out


# ---------- cerebro ----------
def cmd_cerebro(_):
    for n in c.CEREBRO:
        f = c.BASE / 'cerebro' / f'{n}.md'
        print(f'\n========== cerebro/{n}.md ==========')
        print(f.read_text(encoding='utf-8').strip() if f.exists() else '(no existe: ejecuta instalar.py)')
    p = c.pendientes_cerebro()
    if p:
        print('\n---------- SIN RELLENAR (no lo inventes: pregúntalo o déjalo como pendiente) ----------')
        print('\n'.join('· ' + x for x in p))


def cmd_aprende(a):
    if a.en not in c.CEREBRO:
        raise SystemExit(f'--en tiene que ser uno de: {", ".join(c.CEREBRO)}')
    print(c.aprender(a.agente, a.texto, a.en))


# ---------- ideas ----------
def cmd_ideas(a):
    filas = c.leer('ideas.csv')
    if a.accion == 'nuevas':
        vistas = {(r['url'] or r['gancho']).strip().lower() for r in filas}
        n = 0
        for x in cargar_json(a.args[0]):
            k = (x.get('url') or x.get('gancho') or '').strip().lower()
            if not k or k in vistas:
                continue
            vis, med = c.num(x.get('visitas')), c.num(x.get('mediana_cuenta'))
            x.setdefault('multiplo', round(vis / med, 1) if vis and med else '')
            x.update(id=c.siguiente_id(filas, 'I'), fecha=x.get('fecha') or c.hoy(), estado=x.get('estado') or 'nueva')
            filas.append(x)
            vistas.add(k)
            n += 1
        c.escribir('ideas.csv', filas)
        print(f'{n} ideas nuevas · {len(filas)} en total → {c.BASE / "ideas.csv"}')
    elif a.accion == 'lista':
        sel = [r for r in filas if not a.estado or r['estado'] == a.estado]
        sel.sort(key=lambda r: c.num(r.get('multiplo')), reverse=True)
        print(json.dumps(sel[:a.top] if a.top else sel, ensure_ascii=False, indent=1))
    elif a.accion == 'marcar':
        cambios = pares(a.args[1:])
        for r in filas:
            if r['id'] == a.args[0]:
                r.update(cambios)
        c.escribir('ideas.csv', filas)
        print('ok')


# ---------- calendario ----------
def cmd_cal(a):
    filas = c.leer('calendario.csv')
    if a.accion == 'nuevo':
        ya = {(r['fecha'], r['hora'], r['titulo']) for r in filas}
        n = 0
        for x in cargar_json(a.args[0]):
            if (x.get('fecha'), x.get('hora', ''), x.get('titulo')) in ya:
                continue
            x.update(id=c.siguiente_id(filas, 'C'), estado=x.get('estado') or 'idea')
            x['trial'] = 'si' if str(x.get('trial', '')).lower() in ('si', 'sí', 'true', '1') else 'no'
            filas.append(x)
            n += 1
        filas.sort(key=lambda r: (r['fecha'], r['hora']))
        c.escribir('calendario.csv', filas)
        print(f'{n} piezas nuevas en el calendario · {len(filas)} en total')
    elif a.accion == 'lista':
        hasta = (date.today() + timedelta(days=a.dias)).isoformat() if a.dias else '9999'
        sel = [r for r in filas if (not a.estado or r['estado'] == a.estado) and r['fecha'] <= hasta]
        print(json.dumps(sel, ensure_ascii=False, indent=1))
    elif a.accion == 'actualizar':
        cambios = pares(a.args[1:])
        if 'estado' in cambios and cambios['estado'] not in c.ESTADOS:
            raise SystemExit(f'estado tiene que ser uno de: {", ".join(c.ESTADOS)}')
        hecho = False
        for r in filas:
            if r['id'] == a.args[0]:
                r.update(cambios)
                hecho = True
        if not hecho:
            raise SystemExit(f'No existe {a.args[0]} en el calendario.')
        c.escribir('calendario.csv', filas)
        print('ok')


# ---------- métricas ----------
def importar_metricas(items):
    filas = {r['post_id']: r for r in c.leer('metricas.csv')}
    for x in items:
        pid = str(x.get('post_id') or x.get('url') or '')
        if not pid:
            continue
        r = filas.get(pid, {})
        r.update({k: v for k, v in x.items() if v not in (None, '')})
        r['post_id'], r['actualizado'] = pid, c.ahora()
        filas[pid] = r
    lista = sorted(filas.values(), key=lambda r: r.get('fecha', ''), reverse=True)
    c.escribir('metricas.csv', lista)
    return len(items)


def resumen_metricas():
    filas = [r for r in c.leer('metricas.csv') if c.num(r.get('visitas'))]
    med = c.mediana([c.num(r['visitas']) for r in filas if r.get('trial') != 'si'] or [c.num(r['visitas']) for r in filas])
    for r in filas:
        r['multiplo'] = round(c.num(r['visitas']) / med, 1) if med else 0
    orden = sorted(filas, key=lambda r: c.num(r['visitas']), reverse=True)
    corte = (date.today() - timedelta(days=7)).isoformat()
    return {'publicaciones': len(filas), 'mediana_visitas': med,
            'visitas_7d': int(sum(c.num(r['visitas']) for r in filas if r.get('fecha', '')[:10] >= corte)),
            'mejores': orden[:5], 'peores': orden[-3:][::-1] if len(orden) > 5 else []}


def cmd_metricas(a):
    if a.accion == 'importar':
        print(f'{importar_metricas(cargar_json(a.args[0]))} publicaciones actualizadas → {c.BASE / "metricas.csv"}')
    else:
        print(json.dumps(resumen_metricas(), ensure_ascii=False, indent=1))


# ---------- bandeja ----------
def cmd_bandeja(a):
    if a.accion == 'añadir' or a.accion == 'anadir':
        if not (a.tipo and a.agente and a.titulo):
            raise SystemExit('Hace falta --tipo, --agente y --titulo.')
        it = c.bandeja_añadir(a.tipo, a.agente, a.titulo, a.detalle, a.archivo, a.cal, a.si_apruebas)
        print(f'{it["id"]} en la bandeja: {it["titulo"]}')
    elif a.accion == 'lista':
        print(json.dumps(c.bandeja(a.todas), ensure_ascii=False, indent=1))
    elif a.accion in ('aprobar', 'rechazar'):
        if a.accion == 'rechazar' and not a.nota:
            raise SystemExit('Al rechazar, di por qué (--nota): es lo que hace aprender al equipo.')
        ids = a.args if a.args != ['todo'] else [x['id'] for x in c.bandeja()]
        for i in ids:
            it = c.bandeja_decidir(i, 'aprobado' if a.accion == 'aprobar' else 'rechazado', a.nota)
            print(f'{i} {it["estado"]}: {it["titulo"]}')


# ---------- ajustes / resumen ----------
def cmd_ajustes(a):
    d = c.ajustes()
    if a.args:
        for k, v in pares(a.args).items():
            d[k] = int(v) if v.isdigit() and isinstance(c.AJUSTES_DEFECTO.get(k), int) else v
        c.guardar_ajustes(d)
    print(json.dumps(d, ensure_ascii=False, indent=1))


def resumen():
    cal, ideas = c.leer('calendario.csv'), c.leer('ideas.csv')
    por = {e: sum(1 for r in cal if r['estado'] == e) for e in c.ESTADOS}
    m = resumen_metricas()
    hasta = (date.today() + timedelta(days=7)).isoformat()
    return {'fecha': c.hoy(), 'ideas_nuevas': sum(1 for r in ideas if r['estado'] == 'nueva'),
            'ideas_hoy': sum(1 for r in ideas if r['fecha'] == c.hoy()), 'calendario': por,
            'proximos_7d': sum(1 for r in cal if c.hoy() <= r['fecha'] <= hasta and r['estado'] != 'descartado'),
            'para_grabar': por['grabar'], 'pendientes_aprobar': len(c.bandeja()),
            'visitas_7d': m['visitas_7d'], 'mediana_visitas': m['mediana_visitas'],
            'flujos': len(list((c.BASE / 'dms' / 'flujos').glob('*.md'))) if (c.BASE / 'dms' / 'flujos').exists() else 0,
            'cerebro_pendiente': len(c.pendientes_cerebro())}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('cerebro')
    p = sub.add_parser('aprende'); p.add_argument('--agente', required=True); p.add_argument('--texto', required=True)
    p.add_argument('--en', default='aprendizajes')
    p = sub.add_parser('ideas'); p.add_argument('accion', choices=['nuevas', 'lista', 'marcar']); p.add_argument('args', nargs='*')
    p.add_argument('--estado', default=''); p.add_argument('--top', type=int, default=0)
    p = sub.add_parser('cal'); p.add_argument('accion', choices=['nuevo', 'lista', 'actualizar']); p.add_argument('args', nargs='*')
    p.add_argument('--estado', default=''); p.add_argument('--dias', type=int, default=0)
    p = sub.add_parser('metricas'); p.add_argument('accion', choices=['importar', 'resumen']); p.add_argument('args', nargs='*')
    p = sub.add_parser('bandeja'); p.add_argument('accion', choices=['añadir', 'anadir', 'lista', 'aprobar', 'rechazar'])
    p.add_argument('args', nargs='*')
    for o in ('tipo', 'agente', 'titulo', 'detalle', 'archivo', 'cal', 'si-apruebas', 'nota'):
        p.add_argument('--' + o, default='')
    p.add_argument('--todas', action='store_true')
    p = sub.add_parser('ajustes'); p.add_argument('args', nargs='*')
    sub.add_parser('resumen')
    a = ap.parse_args()
    if a.cmd != 'ajustes' and not (c.BASE / 'cerebro').exists():
        raise SystemExit(f'No existe {c.BASE}. Primero: python3 {c.RAIZ / "motor" / "instalar.py"}')
    {'cerebro': cmd_cerebro, 'aprende': cmd_aprende, 'ideas': cmd_ideas, 'cal': cmd_cal, 'metricas': cmd_metricas,
     'bandeja': cmd_bandeja, 'ajustes': cmd_ajustes,
     'resumen': lambda _: print(json.dumps(resumen(), ensure_ascii=False, indent=1))}[a.cmd](a)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Publica y programa tus reels y trial reels en TU Instagram con la API de Zernio, lee las métricas y crea la
automatización «comenta PALABRA → DM». Usa TU clave: ZERNIO_API_KEY en ~/Contenido/.env (o en el entorno).

  zernio.py estado                                  -> comprueba la clave y lista tus cuentas
  zernio.py conectar [--nombre "Mi marca"]          -> crea el perfil (si no hay) y te da el enlace para conectar Instagram
  zernio.py cuenta <accountId>                      -> elige la cuenta de Instagram por defecto
  zernio.py publicar <video.mp4> --texto "caption" --cuando 2026-11-03T19:30|ya [--trial no|manual|auto]
                     [--cal C004] [--portada-ms 1500] [--simular]
  zernio.py metricas [--desde 2026-10-01]           -> trae las estadísticas de tus publicaciones a metricas.csv
  zernio.py automatizacion --palabra CONTENIDO --mensaje "Aquí lo tienes: …" [--enlace URL --boton "Lo quiero"]
                     [--respuesta "Te lo he mandado por privado"] [--post <id de Zernio>] [--pausada] [--simular]
  zernio.py publicaciones                           -> lo programado y publicado

--simular enseña lo que se mandaría sin llamar a la API (sirve para probar sin clave).
Límites de Instagram por API: reels de 3 a 90 s, hasta 300 MB, 9:16; unos 5 trial reels al día.
"""
import argparse, json, os, shutil, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun as c  # noqa: E402

API = 'https://zernio.com/api/v1'
SIMULAR = False


def clave():
    k = c.env('ZERNIO_API_KEY')
    if not k and not SIMULAR:
        raise SystemExit('FALTA_CLAVE: crea tu clave en https://zernio.com/dashboard/api-keys y pégala en '
                         f'{c.BASE / ".env"} como ZERNIO_API_KEY=sk_...')
    return k


def pedir(metodo, ruta, cuerpo=None):
    if SIMULAR:
        print(f'[simulado] {metodo} {API}{ruta}')
        if cuerpo is not None:
            print(json.dumps(cuerpo, ensure_ascii=False, indent=1))
        return {}
    r = urllib.request.Request(API + ruta, method=metodo, data=json.dumps(cuerpo).encode() if cuerpo is not None else None,
                               headers={'Authorization': 'Bearer ' + clave(), 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(r, timeout=120) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        cuerpo_err = e.read().decode(errors='ignore')[:600]
        if e.code == 401:
            raise SystemExit('CLAVE_MAL: Zernio no acepta la clave. Créala otra vez en zernio.com/dashboard/api-keys.')
        if e.code == 429:
            raise SystemExit('Zernio dice que vas demasiado rápido (429). Espera un minuto y repite.')
        raise SystemExit(f'Zernio {metodo} {ruta} -> {e.code}: {cuerpo_err}')


def ident(x):
    return x.get('_id') or x.get('id') if isinstance(x, dict) else x


def cuentas():
    return [x for x in pedir('GET', '/accounts').get('accounts', []) if x.get('platform') == 'instagram']


def cuenta_defecto():
    aj = c.ajustes()
    if aj.get('zernio_cuenta'):
        return aj['zernio_cuenta'], aj.get('zernio_perfil', '')
    if SIMULAR:
        return '<accountId>', '<profileId>'
    cs = cuentas()
    if not cs:
        raise SystemExit('No hay ninguna cuenta de Instagram conectada. Ejecuta: zernio.py conectar')
    if len(cs) > 1:
        raise SystemExit('Tienes varias cuentas. Elige una con: zernio.py cuenta <accountId>\n' +
                         '\n'.join(f'  {ident(x)}  @{x.get("username", "?")}' for x in cs))
    aj['zernio_cuenta'], aj['zernio_perfil'] = ident(cs[0]), ident(cs[0].get('profileId')) or ''
    c.guardar_ajustes(aj)
    return aj['zernio_cuenta'], aj['zernio_perfil']


# ---------- comandos ----------
def estado(_):
    clave()
    cs = cuentas()
    print(f'✓ Clave correcta. Cuentas de Instagram conectadas: {len(cs)}')
    for x in cs:
        print(f'  {ident(x)}  @{x.get("username", "?")}  (perfil {ident(x.get("profileId"))})')
    if not cs:
        print('Conecta tu Instagram con: zernio.py conectar')


def conectar(a):
    perfiles = pedir('GET', '/profiles').get('profiles', [])
    pid = ident(perfiles[0]) if perfiles else ident(pedir('POST', '/profiles', {'name': a.nombre}).get('profile', {}))
    url = pedir('GET', f'/connect/instagram?profileId={pid}').get('authUrl', '')
    aj = c.ajustes(); aj['zernio_perfil'] = pid or aj.get('zernio_perfil', ''); c.guardar_ajustes(aj)
    print(f'Abre este enlace y autoriza tu Instagram (tiene que ser cuenta profesional: Business o Creator):\n{url}')
    print('Después: zernio.py estado')


def elegir_cuenta(a):
    cs = {ident(x): x for x in cuentas()}
    if a.id not in cs:
        raise SystemExit('Esa cuenta no está conectada. Mira las tuyas con: zernio.py estado')
    aj = c.ajustes(); aj['zernio_cuenta'] = a.id; aj['zernio_perfil'] = ident(cs[a.id].get('profileId')) or ''
    c.guardar_ajustes(aj)
    print(f'✓ Cuenta por defecto: @{cs[a.id].get("username")}')


def duracion(video):
    if not shutil.which('ffprobe'):
        return None
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def publicar(a):
    video = Path(a.video).expanduser()
    if not video.exists():
        raise SystemExit(f'No encuentro {video}')
    d = duracion(str(video))
    if d and not 3 <= d <= 90:
        raise SystemExit(f'El vídeo dura {d:.0f} s. Instagram por API solo acepta reels de 3 a 90 s: recórtalo antes.')
    tam = video.stat().st_size
    if tam > 300 * 1024 * 1024:
        raise SystemExit('El vídeo pesa más de 300 MB: expórtalo más ligero.')
    if len(a.texto) > 2200:
        raise SystemExit('El texto pasa de 2.200 caracteres (límite de Instagram).')
    cuenta, _ = cuenta_defecto()
    pre = pedir('POST', '/media/presign', {'filename': video.name, 'contentType': 'video/mp4', 'size': tam})
    if not SIMULAR:
        with open(video, 'rb') as f:   # la subida va sin la clave
            urllib.request.urlopen(urllib.request.Request(pre['uploadUrl'], data=f.read(), method='PUT',
                                                          headers={'Content-Type': 'video/mp4'}), timeout=600).read()
    psd = {'shareToFeed': True}
    if a.trial != 'no':
        psd['trialParams'] = {'graduationStrategy': 'SS_PERFORMANCE' if a.trial == 'auto' else 'MANUAL'}
    if a.portada_ms:
        psd['thumbOffset'] = a.portada_ms
    cuerpo = {'content': a.texto, 'mediaItems': [{'type': 'video', 'url': pre.get('publicUrl', '<publicUrl>')}],
              'platforms': [{'platform': 'instagram', 'accountId': cuenta, 'platformSpecificData': psd}]}
    if a.cuando == 'ya':
        cuerpo['publishNow'] = True
    else:
        cuerpo.update(scheduledFor=a.cuando, timezone=c.ajustes().get('zona_horaria', 'Europe/Madrid'))
    post = pedir('POST', '/posts', cuerpo).get('post', {})
    if SIMULAR:
        print('[simulado] no se ha publicado nada.')
        return
    pid = ident(post)
    with open(c.SISTEMA / 'publicaciones.jsonl', 'a', encoding='utf-8') as fh:
        fh.write(json.dumps({'post_id': pid, 'video': str(video), 'cuando': a.cuando, 'trial': a.trial,
                             'cal': a.cal, 'estado': post.get('status'), 'fecha': c.ahora()}, ensure_ascii=False) + '\n')
    if a.cal:
        filas = c.leer('calendario.csv')
        for r in filas:
            if r['id'] == a.cal:
                r.update(estado='publicado' if a.cuando == 'ya' else 'programado', post_id=pid)
        c.escribir('calendario.csv', filas)
    print(json.dumps({'post_id': pid, 'estado': post.get('status'), 'programado': post.get('scheduledFor'),
                      'trial': a.trial}, ensure_ascii=False))


def metricas(a):
    q = f'/analytics?platform=instagram&fromDate={a.desde}' if a.desde else '/analytics?platform=instagram'
    if c.ajustes().get('zernio_cuenta'):
        q += f'&accountId={c.ajustes()["zernio_cuenta"]}'
    items, pagina = [], 1
    while True:
        r = pedir('GET', q + f'&page={pagina}')
        posts = r.get('posts', [])
        for p in posts:
            an = p.get('analytics', {}) or {}
            psd = next((x.get('platformSpecificData', {}) for x in p.get('platforms', []) if isinstance(x, dict)), {}) or {}
            items.append({'post_id': ident(p), 'fecha': (p.get('publishedAt') or '')[:16].replace('T', ' '),
                          'titulo': (p.get('content') or '').split('\n')[0][:90], 'url': p.get('platformPostUrl', ''),
                          'trial': 'si' if (p.get('isTrialReel') or psd.get('trialParams')) else 'no',
                          'visitas': an.get('views') or an.get('plays') or 0, 'alcance': an.get('reach', ''),
                          'likes': an.get('likes', ''), 'comentarios': an.get('comments', ''),
                          'compartidos': an.get('shares', ''), 'guardados': an.get('saves', '')})
        pag = r.get('pagination') or {}
        if SIMULAR or not posts or not (pag.get('hasMore') or pag.get('page', pagina) < pag.get('pages', pag.get('totalPages', 0))):
            break
        pagina += 1
    if SIMULAR:
        return
    import datos
    datos.importar_metricas(items)
    # las cifras del día, escritas en el cerebro para que las lean todos
    m = datos.resumen_metricas()
    bloque = [f'- Actualizado: {c.ahora()} · {m["publicaciones"]} publicaciones · mediana {int(m["mediana_visitas"])} visitas'
              f' · {m["visitas_7d"]} visitas en 7 días']
    bloque += [f'- Top: «{x["titulo"]}» · {int(c.num(x["visitas"]))} visitas ({x["multiplo"]}x)' for x in m['mejores'][:3]]
    f = c.BASE / 'cerebro' / 'metricas.md'
    t = f.read_text(encoding='utf-8')
    ini, fin = '<!-- cifras:inicio -->', '<!-- cifras:fin -->'
    nuevo = f'{ini}\n' + '\n'.join(bloque) + f'\n{fin}'
    t = t.split(ini)[0] + nuevo + t.split(fin)[1] if ini in t and fin in t else t.rstrip() + '\n\n## Cifras (automático)\n' + nuevo + '\n'
    f.write_text(t, encoding='utf-8')
    print(f'✓ {len(items)} publicaciones con métricas → {c.BASE / "metricas.csv"}')
    print('\n'.join(bloque))


def automatizacion(a):
    cuenta, perfil = cuenta_defecto()
    cuerpo = {'profileId': perfil, 'accountId': cuenta, 'name': f'Comenta {a.palabra.upper()}',
              'keywords': [a.palabra.upper(), a.palabra.lower(), a.palabra.capitalize()], 'matchMode': 'word',
              'typoTolerance': True, 'dmMessage': a.mensaje, 'isActive': not a.pausada,
              'repeatPolicy': {'mode': 'once'}, 'actions': {'likeComment': True}}
    if a.respuesta:
        cuerpo['commentReply'] = a.respuesta
        cuerpo['commentReplyVariations'] = [a.respuesta, '¡Mira tus mensajes! 📩', 'Enviado 🙌 revisa el privado'][:3]
    if a.enlace:
        cuerpo['buttons'] = [{'type': 'url', 'title': (a.boton or 'Lo quiero')[:20], 'url': a.enlace}]
    if a.post:
        cuerpo['postId'] = a.post
    r = pedir('POST', '/comment-automations', cuerpo)
    if SIMULAR:
        return
    au = r.get('automation', {})
    print(f'✓ Automatización «{cuerpo["name"]}» creada ({"activa" if au.get("isActive") else "pausada"}) · id {au.get("id")}')


def publicaciones(_):
    for p in pedir('GET', '/posts').get('posts', [])[:30]:
        print(f'{ident(p)}  {p.get("status", ""):<10} {(p.get("scheduledFor") or p.get("publishedAt") or "")[:16]}  '
              f'{(p.get("content") or "").splitlines()[0][:60] if p.get("content") else ""}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--simular', action='store_true')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('estado')
    p = sub.add_parser('conectar'); p.add_argument('--nombre', default='Mi marca')
    p = sub.add_parser('cuenta'); p.add_argument('id')
    p = sub.add_parser('publicar'); p.add_argument('video'); p.add_argument('--texto', required=True)
    p.add_argument('--cuando', required=True); p.add_argument('--trial', choices=['no', 'manual', 'auto'], default='no')
    p.add_argument('--cal', default=''); p.add_argument('--portada-ms', type=int, default=0)
    p.add_argument('--simular', action='store_true', dest='simular_sub')
    p = sub.add_parser('metricas'); p.add_argument('--desde', default=''); p.add_argument('--simular', action='store_true', dest='simular_sub')
    p = sub.add_parser('automatizacion'); p.add_argument('--palabra', required=True); p.add_argument('--mensaje', required=True)
    p.add_argument('--enlace', default=''); p.add_argument('--boton', default=''); p.add_argument('--respuesta', default='')
    p.add_argument('--post', default=''); p.add_argument('--pausada', action='store_true')
    p.add_argument('--simular', action='store_true', dest='simular_sub')
    sub.add_parser('publicaciones')
    a = ap.parse_args()
    SIMULAR = a.simular or getattr(a, 'simular_sub', False)
    {'estado': estado, 'conectar': conectar, 'cuenta': elegir_cuenta, 'publicar': publicar, 'metricas': metricas,
     'automatizacion': automatizacion, 'publicaciones': publicaciones}[a.cmd](a)

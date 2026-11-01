#!/usr/bin/env python3
"""El analista baja reels y encuentra los que están reventando (los que multiplican la media de su propia cuenta).

  reels.py cuenta @usuario [--n 30] [--dias 90] [--propia] [--videos 3]
        -> con Apify (APIFY_TOKEN en ~/Contenido/.env): sus últimos reels, la mediana de la cuenta y el múltiplo de cada
           uno. Deja referencias/<usuario>/reels.json, resumen.md y candidatos.json (los que pasan de 2x, en el formato de
           ideas). --propia = tu cuenta: además, sus cifras van a metricas.csv. --videos N baja los N mejores en mp4.
  reels.py hashtag <palabra> [--n 30]
        -> con Apify: los reels con más visitas de un hashtag de tu nicho (candidatos.json en referencias/#palabra/)
  reels.py url <enlace> [<enlace> ...]
        -> sin claves (yt-dlp): baja el reel, sus visitas, autor y texto a referencias/sueltos/
  reels.py transcribir <video.mp4 | carpeta>
        -> lo que dice (Whisper en tu ordenador) en un .txt al lado, con el gancho hablado (primeros 4 s) aparte
  reels.py pegado <archivo.txt>
        -> sin claves ni descargas: líneas «enlace · visitas · gancho» que te pasen → candidatos.json

Después: datos.py ideas nuevas <candidatos.json> (el analista escribe antes por_que_funciona e idea_adaptada).
Nunca se inventan cifras: lo que no se puede leer queda vacío.
"""
import argparse, json, re, shutil, subprocess, sys, urllib.error, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun as c  # noqa: E402

APIFY = 'https://api.apify.com/v2/acts/{}/run-sync-get-dataset-items?timeout=290'
REF = c.BASE / 'referencias'


def usuario(t):
    m = re.search(r'instagram\.com/([A-Za-z0-9_.]+)', t)
    return (m.group(1) if m else t).strip().lstrip('@').rstrip('/').split('?')[0]


def apify(actor, entrada):
    tok = c.env('APIFY_TOKEN')
    if not tok:
        raise SystemExit('FALTA_APIFY: sin clave de Apify no puedo leer cuentas enteras. Opciones: pon APIFY_TOKEN en '
                         f'{c.BASE / ".env"} (tiene saldo gratis cada mes), usa «reels.py url <enlace>» con enlaces '
                         'concretos o «reels.py pegado» con lo que te pasen.')
    req = urllib.request.Request(APIFY.format(actor), data=json.dumps(entrada).encode(),
                                 headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=320) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode(errors='ignore')[:300]
        if e.code in (401, 403):
            raise SystemExit('CLAVE_MAL: Apify no acepta la clave (Settings → API & Integrations).')
        if e.code == 402 or 'limit' in cuerpo.lower():
            raise SystemExit('SIN_SALDO: la cuenta de Apify ha gastado el saldo de este mes.')
        raise SystemExit(f'Apify ha fallado ({e.code}): {cuerpo}')
    return [x for x in d if isinstance(x, dict) and not x.get('error')]


def visitas(r):
    return r.get('videoPlayCount') or r.get('videoViewCount') or r.get('playCount') or 0


def fecha(r):
    return (r.get('timestamp') or '')[:10]


def bajar(url, ruta):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=90) as r:
            Path(ruta).write_bytes(r.read())
        return True
    except Exception:
        return False


def candidatos(reels, cuenta, fuente, med, minimo=2.0):
    out = []
    for r in reels:
        v = visitas(r)
        mult = round(v / med, 1) if med else 0
        if mult >= minimo:
            cap = (r.get('caption') or '').strip()
            out.append({'fuente': fuente, 'cuenta': '@' + cuenta if cuenta and not cuenta.startswith('#') else cuenta,
                        'url': r.get('url') or f'https://www.instagram.com/reel/{r.get("shortCode")}/',
                        'visitas': v, 'mediana_cuenta': int(med), 'multiplo': mult,
                        'formato': f'{round(r.get("videoDuration") or 0)} s' if r.get('videoDuration') else '',
                        'gancho': cap.split('\n')[0][:160], 'por_que_funciona': '', 'idea_adaptada': '', 'pilar': '',
                        'fecha_reel': fecha(r)})
    return out


def resumen_md(destino, titulo, reels, med):
    L = [f'# {titulo}', '', f'- Reels leídos: {len(reels)} · mediana de visitas: {int(med)}', '',
         '| # | Visitas | Múltiplo | Fecha | Duración | Comentarios | Texto |', '|---|---|---|---|---|---|---|']
    for i, r in enumerate(reels, 1):
        v = visitas(r)
        L.append(f'| {i} | {v} | {round(v / med, 1) if med else "—"}x | {fecha(r)} | {round(r.get("videoDuration") or 0)} s | '
                 f'{r.get("commentsCount", "")} | {(r.get("caption") or "").replace(chr(10), " ").replace("|", "/")[:140]} |')
    (destino / 'resumen.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


def cmd_cuenta(a):
    u = usuario(a.usuario)
    d = REF / u
    d.mkdir(parents=True, exist_ok=True)
    print(f'Leyendo los últimos {a.n} reels de @{u}…')
    reels = apify('apify~instagram-reel-scraper', {'username': [u], 'resultsLimit': a.n})
    if a.dias:
        corte = (datetime.now(timezone.utc) - timedelta(days=a.dias)).date().isoformat()
        reels = [r for r in reels if not fecha(r) or fecha(r) >= corte]
    if not reels:
        raise SystemExit(f'No hay reels de @{u} (¿cuenta privada o mal escrita?).')
    reels.sort(key=visitas, reverse=True)
    med = c.mediana([visitas(r) for r in reels])
    (d / 'reels.json').write_text(json.dumps(reels, ensure_ascii=False, indent=1), encoding='utf-8')
    resumen_md(d, f'@{u}', reels, med)
    cand = candidatos(reels, u, 'propia' if a.propia else 'nicho', med)
    (d / 'candidatos.json').write_text(json.dumps(cand, ensure_ascii=False, indent=1), encoding='utf-8')
    if a.videos:
        (d / 'videos').mkdir(exist_ok=True)
        for i, r in enumerate(reels[:a.videos], 1):
            if r.get('videoUrl'):
                bajar(r['videoUrl'], d / 'videos' / f'{i:02d}_{r.get("shortCode")}.mp4')
    if a.propia:
        import datos
        datos.importar_metricas([{'post_id': r.get('shortCode') or r.get('id'), 'fecha': (r.get('timestamp') or '')[:16].replace('T', ' '),
                                  'titulo': (r.get('caption') or '').split('\n')[0][:90], 'url': r.get('url', ''),
                                  'visitas': visitas(r), 'likes': r.get('likesCount', ''),
                                  'comentarios': r.get('commentsCount', ''), 'trial': 'no'} for r in reels])
    print(f'Mediana de @{u}: {int(med)} visitas. {len(cand)} reels pasan de 2x:')
    for x in cand[:8]:
        print(f'  {x["multiplo"]}x · {x["visitas"]} · {x["gancho"][:90]}')
    print(f'→ {d / "resumen.md"}\n→ {d / "candidatos.json"}')


def cmd_hashtag(a):
    tag = a.palabra.lstrip('#').replace(' ', '')
    d = REF / f'#{tag}'
    d.mkdir(parents=True, exist_ok=True)
    reels = apify('apify~instagram-hashtag-scraper', {'hashtags': [tag], 'resultsType': 'reels', 'resultsLimit': a.n})
    reels = [r for r in reels if visitas(r)] or reels
    reels.sort(key=visitas, reverse=True)
    med = c.mediana([visitas(r) for r in reels])
    resumen_md(d, f'#{tag}', reels, med)
    cand = []
    for r in reels[:10]:  # en un hashtag no hay «media de la cuenta»: se quedan los de arriba
        x = candidatos([r], r.get('ownerUsername', ''), 'nicho', med, minimo=0)[0]
        x['cuenta'] = '@' + (r.get('ownerUsername') or '?')
        cand.append(x)
    (d / 'candidatos.json').write_text(json.dumps(cand, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{len(reels)} reels de #{tag}; los 10 con más visitas en {d / "candidatos.json"}')


def cmd_url(a):
    if not shutil.which('yt-dlp'):
        raise SystemExit('Falta yt-dlp: instálalo con  brew install yt-dlp  (Mac) o  pip install yt-dlp')
    d = REF / 'sueltos'
    d.mkdir(parents=True, exist_ok=True)
    cand = []
    for url in a.enlaces:
        base = ['yt-dlp', '--no-warnings', '--no-simulate', '--print', 'id', '-o', str(d / '%(id)s.%(ext)s'),
                '-f', 'mp4/best', '--write-info-json', url]
        r = subprocess.run(base, capture_output=True, text=True)
        if r.returncode != 0:  # Instagram a veces pide sesión: se reintenta con las cookies del navegador
            r = subprocess.run(base[:1] + ['--cookies-from-browser', 'chrome'] + base[1:], capture_output=True, text=True)
        vid = (r.stdout.strip().splitlines() or [''])[-1]
        info = d / f'{vid}.info.json'
        if r.returncode != 0 or not vid or not info.exists():
            print(f'  ✗ {url}: {(r.stderr.strip().splitlines() or ["no se pudo bajar"])[-1][:160]}')
            continue
        i = json.loads(info.read_text(encoding='utf-8'))
        v = i.get('view_count') or i.get('play_count') or ''
        cand.append({'fuente': 'enlace', 'cuenta': '@' + (i.get('uploader_id') or i.get('channel') or i.get('uploader') or '?'),
                     'url': url, 'visitas': v, 'mediana_cuenta': '', 'formato': f'{round(i.get("duration") or 0)} s',
                     'gancho': (i.get('description') or i.get('title') or '').split('\n')[0][:160],
                     'por_que_funciona': '', 'idea_adaptada': '', 'pilar': '', 'video': str(d / f'{i.get("id")}.mp4')})
        print(f'  ✓ {url} · {v or "visitas no visibles"} · {d / (str(i.get("id")) + ".mp4")}')
    f = d / 'candidatos.json'
    viejos = json.loads(f.read_text(encoding='utf-8')) if f.exists() else []
    f.write_text(json.dumps(viejos + cand, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'→ {f}  (transcríbelos con: reels.py transcribir {d})')


def cmd_transcribir(a):
    p = Path(a.ruta).expanduser()
    videos = sorted(p.glob('*.mp4')) if p.is_dir() else [p]
    videos = [v for v in videos if not v.with_suffix('.txt').exists()]
    if not videos:
        print('Nada nuevo que transcribir.')
        return
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise SystemExit('FALTA_WHISPER: pip install faster-whisper  (o, si tienes /editor instalado: '
                         'python3 ~/.claude/skills/editor/scripts/transcribir.py <video>)')
    m = WhisperModel(a.modelo, device='cpu', compute_type='int8')
    for v in videos:
        segs, _ = m.transcribe(str(v), language='es', vad_filter=True)
        segs = list(segs)
        texto = ' '.join(s.text.strip() for s in segs)
        gancho = ' '.join(s.text.strip() for s in segs if s.start < 4)
        v.with_suffix('.txt').write_text(f'GANCHO HABLADO (0-4 s): {gancho}\n\n{texto}\n', encoding='utf-8')
        print(f'  ✓ {v.name}: «{gancho[:90]}»')


def cmd_pegado(a):
    cand = []
    for l in Path(a.archivo).expanduser().read_text(encoding='utf-8').splitlines():
        if not l.strip():
            continue
        url = (re.search(r'https?://\S+', l) or [''])[0]
        resto = l.replace(url, ' ')
        m = re.search(r'(\d[\d.,]*\s*[kKmM]?)\s*(visitas|views|reproducciones)?', resto)
        v = c.num(m.group(1)) if m else ''
        gancho = re.sub(r'(\d[\d.,]*\s*[kKmM]?)\s*(visitas|views|reproducciones)', ' ', resto)
        gancho = re.sub(r'\s*[·|\-–]\s*', ' ', gancho).strip(' ·|-–')
        m_c = re.search(r'instagram\.com/([A-Za-z0-9_.]+)/', url)
        cuenta = '@' + m_c.group(1) if m_c and m_c.group(1) not in ('reel', 'reels', 'p', 'tv') else ''
        cand.append({'fuente': 'pegado', 'cuenta': cuenta,
                     'url': url, 'visitas': int(v) if v else '', 'mediana_cuenta': '', 'formato': '', 'gancho': gancho[:160],
                     'por_que_funciona': '', 'idea_adaptada': '', 'pilar': ''})
    d = REF / 'pegados'
    d.mkdir(parents=True, exist_ok=True)
    f = d / f'candidatos-{c.hoy()}.json'
    f.write_text(json.dumps(cand, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{len(cand)} candidatos → {f}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('cuenta'); p.add_argument('usuario'); p.add_argument('--n', type=int, default=30)
    p.add_argument('--dias', type=int, default=90); p.add_argument('--propia', action='store_true')
    p.add_argument('--videos', type=int, default=0)
    p = sub.add_parser('hashtag'); p.add_argument('palabra'); p.add_argument('--n', type=int, default=30)
    p = sub.add_parser('url'); p.add_argument('enlaces', nargs='+')
    p = sub.add_parser('transcribir'); p.add_argument('ruta'); p.add_argument('--modelo', default='small')
    p = sub.add_parser('pegado'); p.add_argument('archivo')
    a = ap.parse_args()
    {'cuenta': cmd_cuenta, 'hashtag': cmd_hashtag, 'url': cmd_url, 'transcribir': cmd_transcribir,
     'pegado': cmd_pegado}[a.cmd](a)

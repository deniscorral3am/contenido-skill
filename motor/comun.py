"""Lo que comparten todos los scripts del sistema de contenido: rutas, columnas de los CSV, ajustes, la bandeja de
aprobación y el cerebro. Solo librería estándar (Python 3.8+)."""
import csv, json, os, re
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent          # carpeta de la skill
BASE = Path(os.environ.get('CONTENIDO', Path.home() / 'Contenido')).expanduser()
SKILLS = Path.home() / '.claude' / 'skills'
SISTEMA = BASE / '.sistema'

CEREBRO = ['audiencia', 'nicho', 'voz', 'oferta', 'llamadas-de-venta', 'metricas', 'aprendizajes']
AGENTES = [  # (agente, skill por defecto, rol)
    ('jefe', 'jefe', 'Jefe de gabinete'),
    ('analista', 'analista', 'Analista'),
    ('estratega', 'estratega', 'Estratega'),
    ('copywriter', 'copywriter', 'Copywriter'),
    ('editor', 'edicion', 'Equipo de edición'),
    ('publicador', 'publicador', 'Publicador'),
    ('setter', 'setter', 'ManyChat + setter IA'),
]
CARPETAS = ['cerebro', 'guiones', 'crudos', 'editados', 'referencias', 'dms/flujos', 'dms/conversaciones',
            'dms/llamadas', 'dms/setter', 'bandeja', 'partes', '.sistema/logs']

C_IDEAS = ['id', 'fecha', 'fuente', 'cuenta', 'url', 'visitas', 'mediana_cuenta', 'multiplo', 'formato', 'gancho',
           'por_que_funciona', 'idea_adaptada', 'pilar', 'estado']
C_CALENDARIO = ['id', 'fecha', 'hora', 'pilar', 'embudo', 'formato', 'titulo', 'idea_id', 'gancho', 'palabra_clave',
                'trial', 'estado', 'guion', 'crudo', 'editado', 'post_id', 'url', 'notas']
C_METRICAS = ['post_id', 'fecha', 'titulo', 'url', 'trial', 'visitas', 'alcance', 'likes', 'comentarios',
              'compartidos', 'guardados', 'actualizado']
CSVS = {'ideas.csv': C_IDEAS, 'calendario.csv': C_CALENDARIO, 'metricas.csv': C_METRICAS}

# Estados de una pieza del calendario, en orden
ESTADOS = ['idea', 'guion', 'grabar', 'crudo', 'editado', 'listo', 'programado', 'publicado', 'descartado']

AJUSTES_DEFECTO = {
    'nombre': '', 'marca': '', 'instagram': '', 'zona_horaria': 'Europe/Madrid',
    'reels_por_semana': 5, 'trials_por_semana': 3, 'hora_publicacion': '19:30',
    'hora_turno': '00:00', 'hora_panel': '08:00', 'palabra_clave': '',
    'zernio_perfil': '', 'zernio_cuenta': '', 'ejemplo': False,
}


def hoy():
    return date.today().isoformat()


def ahora():
    return datetime.now().strftime('%Y-%m-%d %H:%M')


# ---------- ajustes y .env ----------
def ajustes():
    f = SISTEMA / 'ajustes.json'
    d = dict(AJUSTES_DEFECTO)
    if f.exists():
        d.update(json.loads(f.read_text(encoding='utf-8')))
    return d


def guardar_ajustes(d):
    SISTEMA.mkdir(parents=True, exist_ok=True)
    (SISTEMA / 'ajustes.json').write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')


def equipo():
    """{agente: nombre de la skill instalada} (normalmente el mismo; distinto si ya tenías otra skill con ese nombre)."""
    f = SISTEMA / 'equipo.json'
    d = {a: s for a, s, _ in AGENTES}
    if f.exists():
        d.update(json.loads(f.read_text(encoding='utf-8')))
    return d


def env(nombre):
    """Una clave del usuario: primero la variable de entorno, luego ~/Contenido/.env. Nunca se imprime."""
    if os.environ.get(nombre):
        return os.environ[nombre].strip()
    f = BASE / '.env'
    if f.exists():
        for l in f.read_text(encoding='utf-8').splitlines():
            l = l.strip()
            if l.startswith(nombre + '='):
                return l.split('=', 1)[1].strip().strip('"').strip("'")
    return ''


# ---------- CSV ----------
def leer(nombre):
    f = BASE / nombre
    if not f.exists():
        return []
    with open(f, newline='', encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def escribir(nombre, filas):
    cols = CSVS[nombre]
    with open(BASE / nombre, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for r in filas:
            w.writerow({c: r.get(c, '') for c in cols})


def siguiente_id(filas, prefijo):
    n = [int(re.sub(r'\D', '', r.get('id', '')) or 0) for r in filas]
    return f'{prefijo}{(max(n) if n else 0) + 1:03d}'


def num(x, defecto=0):
    """'12.400' · '12,4K' · '1.2M' · 3500 → número. Lo que no se entiende → defecto."""
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x or '').strip().upper().replace(' ', '')
    mult = 1
    if s[-1:] in ('K', 'M'):
        mult, s = (1000 if s[-1] == 'K' else 1000000), s[:-1]
        s = s.replace(',', '.')
    elif re.fullmatch(r'\d{1,3}(\.\d{3})+', s):      # 12.400 (miles a la española)
        s = s.replace('.', '')
    else:
        s = s.replace(',', '.')
    try:
        return float(s) * mult
    except ValueError:
        return defecto


def mediana(xs):
    xs = sorted(x for x in xs if x)
    if not xs:
        return 0
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2


# ---------- bandeja de aprobación ----------
def bandeja(todas=False):
    d = BASE / 'bandeja'
    items = []
    for f in sorted(d.glob('*.json')) if d.exists() else []:
        it = json.loads(f.read_text(encoding='utf-8'))
        if todas or it.get('estado') == 'pendiente':
            items.append(it)
    return items


def bandeja_añadir(tipo, agente, titulo, detalle='', archivo='', cal='', si_apruebas='', extra=None):
    d = BASE / 'bandeja'
    d.mkdir(parents=True, exist_ok=True)
    for it in bandeja():  # no duplicar lo mismo dos veces
        if it['titulo'] == titulo and it['tipo'] == tipo:
            return it
    n = len(list(d.glob('*.json'))) + 1
    it = {'id': f'B{n:03d}', 'tipo': tipo, 'agente': agente, 'titulo': titulo, 'detalle': detalle,
          'archivo': archivo, 'calendario_id': cal, 'si_apruebas': si_apruebas, 'creado': ahora(),
          'estado': 'pendiente', 'nota': '', 'decidido': ''}
    if extra:
        it.update(extra)
    (d / f'{it["id"]}.json').write_text(json.dumps(it, ensure_ascii=False, indent=1), encoding='utf-8')
    return it


def bandeja_decidir(ident, decision, nota=''):
    f = BASE / 'bandeja' / f'{ident}.json'
    if not f.exists():
        raise SystemExit(f'No existe {ident} en la bandeja.')
    it = json.loads(f.read_text(encoding='utf-8'))
    it.update(estado=decision, nota=nota, decidido=ahora())
    f.write_text(json.dumps(it, ensure_ascii=False, indent=1), encoding='utf-8')
    with open(BASE / 'bandeja' / 'decisiones.csv', 'a', newline='', encoding='utf-8') as fh:
        csv.writer(fh).writerow([it['decidido'], ident, it['tipo'], it['agente'], decision, it['titulo'], nota])
    # efecto en el calendario: al aprobar, la pieza avanza; al rechazar, vuelve atrás con la nota
    if it.get('calendario_id'):
        filas = leer('calendario.csv')
        for r in filas:
            if r['id'] == it['calendario_id']:
                if decision == 'aprobado' and it.get('si_apruebas'):
                    r['estado'] = it['si_apruebas']
                elif decision == 'rechazado':
                    r['notas'] = (r.get('notas', '') + f' | rechazado {hoy()}: {nota}').strip(' |')
        escribir('calendario.csv', filas)
    if decision == 'rechazado' and nota:  # lo que no le gusta es lo que más enseña
        aprender('jefe', f'Rechazó «{it["titulo"]}» ({it["tipo"]} de {it["agente"]}): {nota}', 'aprendizajes')
    return it


# ---------- cerebro ----------
def aprender(agente, texto, en='aprendizajes'):
    """Apunta algo aprendido. Siempre en aprendizajes.md (el diario común) y, si se indica, también en la sección
    «Lo que vamos aprendiendo» del archivo del cerebro que toque (voz, nicho, audiencia…)."""
    texto = ' '.join(str(texto).split())
    linea = f'- {hoy()} · {agente}: {texto}\n'
    diario = BASE / 'cerebro' / 'aprendizajes.md'
    with open(diario, 'a', encoding='utf-8') as fh:
        fh.write(linea if en == 'aprendizajes' else linea.replace(f'{agente}:', f'{agente} [{en}]:'))
    if en != 'aprendizajes':
        f = BASE / 'cerebro' / f'{en}.md'
        t = f.read_text(encoding='utf-8') if f.exists() else f'# {en}\n'
        if '## Lo que vamos aprendiendo' not in t:
            t = t.rstrip() + '\n\n## Lo que vamos aprendiendo\n'
        f.write_text(t.rstrip() + '\n' + linea, encoding='utf-8')
    return linea.strip()


def pendientes_cerebro():
    """Campos del cerebro que siguen en PENDIENTE (los agentes avisan en vez de inventar)."""
    out = []
    for n in CEREBRO:
        f = BASE / 'cerebro' / f'{n}.md'
        if f.exists():
            sec = ''
            for l in f.read_text(encoding='utf-8').splitlines():
                if l.startswith('## '):
                    sec = l[3:].strip()
                if 'PENDIENTE' in l and l.startswith('- '):
                    campo = l[2:].split(':')[0].strip() if ':' in l else sec
                    out.append(f'{n}.md → {campo}')
    return out


def ultimas_lineas(archivo, n=8):
    f = BASE / 'cerebro' / archivo
    if not f.exists():
        return []
    return [l[2:] for l in f.read_text(encoding='utf-8').splitlines() if re.match(r'- \d{4}-\d{2}-\d{2} · ', l)][-n:]

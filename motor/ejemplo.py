#!/usr/bin/env python3
"""Genera ejemplo/PANEL.html con un perfil FICTICIO (marcado como ejemplo), en una carpeta temporal: no toca tu
~/Contenido. Sirve para enseñar cómo queda el panel antes de instalar nada.

  python3 ejemplo.py        -> <skill>/ejemplo/PANEL.html
"""
import json, os, re, shutil, sys, tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix='contenido-ejemplo-'))
os.environ['CONTENIDO'] = str(TMP)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun as c  # noqa: E402
import panel  # noqa: E402

H = date.today()
d = lambda n: (H + timedelta(days=n)).isoformat()  # noqa: E731

for x in c.CARPETAS:
    (TMP / x).mkdir(parents=True, exist_ok=True)
for n in c.CEREBRO:
    shutil.copy(c.RAIZ / 'ref' / 'cerebro' / f'{n}.md', TMP / 'cerebro' / f'{n}.md')
rellenos = {
    'oferta': {'Nombre de la oferta': 'Agenda Llena (ficticia)', 'Precio (y forma de pago)': '1.500 € o 3 × 550 €',
               'Qué consigue el cliente (la promesa, en una frase)': 'Fotógrafos de boda con la temporada reservada sin depender de bodas.net'},
    'audiencia': {'Avatar en una frase': 'Fotógrafo de bodas de 28–40 años que vive del boca a boca y quiere dejar de depender de él'},
    'nicho': {'Nicho (en una frase)': 'Negocio para fotógrafos de bodas', 'Tu cuenta de Instagram': '@marta.ejemplo',
              'Pilares de contenido (3–5 temas de los que hablas siempre)': 'precios · captación · portfolio · ventas'},
    'voz': {'Tú / usted': 'tú', 'Tono (directo, cercano, serio, provocador, con humor…)': 'directo y con humor'},
}
for archivo, campos in rellenos.items():
    f = TMP / 'cerebro' / f'{archivo}.md'
    t = f.read_text(encoding='utf-8')
    for k, v in campos.items():
        t = re.sub(rf'^- {re.escape(k)}: PENDIENTE$', f'- {k}: {v}', t, flags=re.M)
    f.write_text(t, encoding='utf-8')

c.guardar_ajustes(dict(c.AJUSTES_DEFECTO, nombre='Marta Ejemplo', marca='Estudio Ejemplo (ficticio)',
                       instagram='@marta.ejemplo', palabra_clave='AGENDA', ejemplo=True))

c.escribir('ideas.csv', [
    {'id': 'I001', 'fecha': d(0), 'fuente': 'nicho', 'cuenta': '@cuenta.ejemplo1', 'visitas': 182000, 'mediana_cuenta': 21000,
     'multiplo': 8.7, 'formato': '38 s · a cámara', 'gancho': 'Subí mis precios un 40 % y tengo más bodas',
     'por_que_funciona': 'Contraste + resultado: rompe la creencia de que subir precios espanta clientes',
     'idea_adaptada': 'Por qué el fotógrafo más barato de tu ciudad es el que menos reserva', 'pilar': 'precios', 'estado': 'al_plan'},
    {'id': 'I002', 'fecha': d(0), 'fuente': 'nicho', 'cuenta': '@cuenta.ejemplo2', 'visitas': 64000, 'mediana_cuenta': 15000,
     'multiplo': 4.3, 'formato': '52 s · pantalla', 'gancho': '3 mensajes que mando a cada pareja que me escribe',
     'por_que_funciona': 'Lista + plantilla copiable: se guarda y se comparte', 'idea_adaptada': 'Los 3 mensajes que convierten una consulta en reserva',
     'pilar': 'ventas', 'estado': 'nueva'},
    {'id': 'I003', 'fecha': d(0), 'fuente': 'propia', 'cuenta': '@marta.ejemplo', 'visitas': 9800, 'mediana_cuenta': 3500,
     'multiplo': 2.8, 'formato': '41 s · a cámara', 'gancho': 'Nadie te cuenta esto de bodas.net', 'por_que_funciona': 'Curiosidad + enemigo común',
     'idea_adaptada': 'Segunda parte: qué hago en su lugar', 'pilar': 'captación', 'estado': 'nueva'},
])
c.escribir('calendario.csv', [
    {'id': 'C001', 'fecha': d(-2), 'hora': '19:30', 'pilar': 'captación', 'embudo': 'TOFU', 'formato': 'a cámara',
     'titulo': 'Nadie te cuenta esto de bodas.net', 'estado': 'publicado', 'trial': 'no'},
    {'id': 'C002', 'fecha': d(1), 'hora': '19:30', 'pilar': 'precios', 'embudo': 'TOFU', 'formato': 'a cámara',
     'titulo': 'El fotógrafo más barato es el que menos reserva', 'idea_id': 'I001',
     'gancho': 'El fotógrafo más barato de tu ciudad es el que menos bodas hace', 'estado': 'guion',
     'guion': 'guiones/ejemplo-precios.md', 'trial': 'no'},
    {'id': 'C003', 'fecha': d(2), 'hora': '19:30', 'pilar': 'ventas', 'embudo': 'MOFU', 'formato': 'pantalla',
     'titulo': '3 mensajes que convierten una consulta', 'gancho': '3 mensajes que mando a cada pareja', 'palabra_clave': 'AGENDA',
     'estado': 'grabar', 'trial': 'no'},
    {'id': 'C004', 'fecha': d(3), 'hora': '13:00', 'pilar': 'captación', 'embudo': 'TOFU', 'formato': 'a cámara',
     'titulo': 'bodas.net: gancho B', 'estado': 'editado', 'editado': 'editados/C004-bodasnet-B.mp4', 'trial': 'si'},
    {'id': 'C005', 'fecha': d(4), 'hora': '19:30', 'pilar': 'portfolio', 'embudo': 'TOFU', 'formato': 'POV',
     'titulo': 'POV: editas 2.000 fotos un domingo', 'estado': 'programado', 'trial': 'no'},
    {'id': 'C006', 'fecha': d(6), 'hora': '19:30', 'pilar': 'ventas', 'embudo': 'BOFU', 'formato': 'a cámara',
     'titulo': '«Es caro»: lo que respondo', 'palabra_clave': 'AGENDA', 'estado': 'idea', 'trial': 'no'},
])
c.escribir('metricas.csv', [
    {'post_id': f'p{i}', 'fecha': d(-k), 'titulo': t, 'visitas': v, 'trial': tr, 'likes': v // 30, 'comentarios': v // 400}
    for i, (k, t, v, tr) in enumerate([(2, 'Nadie te cuenta esto de bodas.net', 9800, 'no'), (5, 'Cuánto cobro por una boda', 7400, 'no'),
                                       (8, 'Mi primera boda: lo que haría distinto', 3900, 'no'), (10, 'El contrato que me salvó', 3500, 'no'),
                                       (12, 'Precios: gancho B', 5100, 'si'), (15, 'Edito así en 2 horas', 2600, 'no'),
                                       (18, 'Por qué no hago preboda gratis', 3100, 'no'), (21, 'Mi equipo en una boda', 1900, 'no')])])

(TMP / 'guiones' / 'ejemplo-precios.md').write_text(
    '# El fotógrafo más barato es el que menos reserva · C002 · TOFU · a cámara · 40 s\n'
    'Para: fotógrafo que compite por precio · Rompe: «si subo precios me quedo sin bodas» · Sale de: idea I001\n\n'
    '## Ganchos\n1. (dicho) El fotógrafo más barato de tu ciudad es el que menos bodas hace. · (pantalla) bajar precios ≠ más bodas · contraste\n'
    '2. (dicho) Subí mis precios y me escribieron más parejas. · (pantalla) ¿por qué? · curiosidad\n'
    '3. (dicho) Deja de bajar tus precios en enero. · (pantalla) error caro · enemigo común\n\n'
    '## Guion\nEl fotógrafo más barato de tu ciudad es el que menos bodas hace. Y no es casualidad.\n'
    'Una pareja que se gasta 20.000 euros en su boda no busca al más barato: busca al que le da confianza…\n', encoding='utf-8')
c.bandeja_añadir('guion', 'copywriter', 'El fotógrafo más barato es el que menos reserva', 'TOFU · para mañana a las 19:30',
                 'guiones/ejemplo-precios.md', 'C002', 'grabar')
c.bandeja_añadir('video', 'editor', 'bodas.net: gancho B (trial reel)', '0:41 · se publica en 3 días a las 13:00, trial',
                 'editados/C004-bodasnet-B.mp4', 'C004', 'listo')
c.bandeja_añadir('flujo', 'setter', 'Comenta AGENDA', 'Comentario → DM con la plantilla de mensajes → setter IA. Se monta con Zernio al aprobar.',
                 '', '', '')
for ag, txt, en in [('analista', 'Los reels de lista con plantilla copiable hacen 4x la mediana en el nicho (3 de 4 ganadores)', 'nicho'),
                    ('analista', 'En la cuenta, los ganchos de curiosidad doblan a los de pregunta (2,8x frente a 1,1x)', 'metricas'),
                    ('setter', 'Las parejas dicen «no sabemos si nos lo podemos permitir», no «es caro»', 'audiencia'),
                    ('copywriter', 'No dice «increíble»: dice «una pasada»', 'voz'),
                    ('estratega', 'El BOFU del domingo pasado trajo 6 conversaciones: repetir día', 'aprendizajes')]:
    c.aprender(ag, txt, en)
(TMP / 'partes' / d(0)).mkdir(parents=True, exist_ok=True)
(TMP / 'partes' / d(0) / 'turno.json').write_text(json.dumps({
    'fecha': d(0), 'inicio': '00:00', 'fin': '00:38',
    'titular': '3 ideas nuevas, 1 guion y 1 vídeo esperando tu visto bueno, y la semana planificada.',
    'agentes': [
        {'agente': 'jefe', 'hecho': 'Ha juntado 3 cosas para tu visto bueno y el brief de mañana.'},
        {'agente': 'analista', 'hecho': 'Ha leído 90 reels de 3 cuentas del nicho y tu cuenta: 3 ideas nuevas por encima de 2x.',
         'items': [{'titulo': 'Subí mis precios un 40 % y tengo más bodas', 'etiqueta': '8,7x', 'tipo': 'ac', 'detalle': '@cuenta.ejemplo1'},
                   {'titulo': '3 mensajes que mando a cada pareja', 'etiqueta': '4,3x', 'tipo': 'ac', 'detalle': '@cuenta.ejemplo2'}]},
        {'agente': 'estratega', 'hecho': 'Semana planificada: 4 reels y 1 trial (60 % alcance, 20 % método, 20 % venta).'},
        {'agente': 'copywriter', 'hecho': 'Guion de mañana con 3 ganchos y 2 variantes para trial.',
         'items': [{'titulo': 'El fotógrafo más barato es el que menos reserva', 'etiqueta': 'para aprobar', 'tipo': 'warn'}]},
        {'agente': 'editor', 'hecho': 'Ha editado el crudo de bodas.net con el gancho B (41 s, subtítulos y música).'},
        {'agente': 'publicador', 'hecho': 'Métricas al día (8 reels) y 1 reel programado para el jueves.'},
        {'agente': 'setter', 'hecho': 'Flujo «Comenta AGENDA» listo y 2 objeciones nuevas apuntadas en el cerebro.'},
    ]}, ensure_ascii=False, indent=1), encoding='utf-8')

out = panel.generar(c.RAIZ / 'ejemplo' / 'PANEL.html', ahora=datetime.combine(H, datetime.min.time()).replace(hour=23, minute=40))
shutil.rmtree(TMP, ignore_errors=True)
print(out)

#!/usr/bin/env python3
"""El setter con IA que habla igual que tú: genera su prompt con el cerebro (tu voz, tu oferta, tu avatar y las
objeciones de tus llamadas), el flujo de n8n listo para importar y lo prueba con 3 leads simulados.

  setter_prompt.py                      -> ~/Contenido/dms/setter/prompt.txt + setter-n8n.json
  setter_prompt.py --probar             -> además, 3 conversaciones simuladas en dms/setter/prueba.md
                                           (con tu Claude Code; o ANTHROPIC_API_KEY / OPENROUTER_API_KEY en ~/Contenido/.env)
  setter_prompt.py --palabra CONTENIDO  -> la palabra clave con la que llegan los leads de prueba
"""
import argparse, json, re, shutil, subprocess, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun as c  # noqa: E402

SALIDA = c.BASE / 'dms' / 'setter'


def seccion(nombre):
    """El archivo del cerebro sin comentarios ni campos PENDIENTE (lo que no se sabe no entra en el prompt)."""
    f = c.BASE / 'cerebro' / f'{nombre}.md'
    if not f.exists():
        return ''
    t = re.sub(r'<!--.*?-->', '', f.read_text(encoding='utf-8'), flags=re.S)
    out = []
    for bloque in re.split(r'^## ', t, flags=re.M)[1:]:        # una sección por bloque
        titulo, _, cuerpo = bloque.partition('\n')
        if titulo.strip() == 'Estilo de edición':               # eso es del editor, no del setter
            continue
        lineas = [l for l in cuerpo.splitlines() if l.strip() not in ('', '-') and 'PENDIENTE' not in l
                  and not re.match(r'- [^:]+:\s*$', l)]
        if lineas:
            out.append(f'{titulo.strip()}:\n' + '\n'.join(lineas))
    return '\n\n'.join(out)


def prompt(aj):
    quien = aj.get('nombre') or 'el creador'
    marca = aj.get('marca') or quien
    return f"""Eres el setter de {marca}. Escribes por mensaje privado de Instagram en nombre de {quien}, como si fueras su equipo, a personas que acaban de comentar una palabra clave en un reel o que han escrito por privado.
Tu único objetivo: que los que encajan con la oferta agenden una llamada cualificada. Los que no encajan se van bien tratados y con algo útil.

== CÓMO HABLA {quien.upper()} (cópialo: palabras, ritmo, tuteo, frases) ==
{seccion('voz') or 'Cercano, directo, frases cortas, tuteo.'}

== LA OFERTA ==
{seccion('oferta') or 'Sin datos de la oferta: no hables de precio ni de detalles, ofrece la llamada para verlo.'}

== A QUIÉN AYUDA (y a quién no) ==
{seccion('audiencia') or '—'}

== LO QUE SE OYE EN LAS LLAMADAS DE VENTA ==
{seccion('llamadas-de-venta') or '—'}

== CÓMO TRABAJAS ==
1. Primero da lo que pidió (si comentó una palabra, el recurso: su enlace está en el mensaje automático; tú confirmas y preguntas). Luego UNA pregunta.
2. Cualifica de una en una: a qué se dedica / situación actual → qué quiere conseguir → qué le frena hoy → para cuándo lo quiere → si está en posición de invertir en ayuda. Lo que ya te ha contado cuenta como respondido. Nunca repitas una pregunta.
3. Si encaja y tiene urgencia: explica en una línea para qué es la llamada (qué se lleva aunque no compre) y manda el enlace de agenda de la oferta. Añade [CALIENTE] al final.
4. Si no encaja: agradece, deja algo útil (un recurso, un consejo concreto) y cierra sin agenda.
5. Precio: no lo das hasta cualificar; si insiste, rango o «depende de tu caso» y sigues con la pregunta.
6. Objeción: reconócela, haz una pregunta que la desmonte (usa lo que se oye en las llamadas) y sigue.

Reglas: mensajes de 1 a 3 líneas, como una persona por WhatsApp. Una sola pregunta por mensaje. Sin listas, sin negritas, sin emojis si su voz no los usa.
Nunca inventes cifras, casos, testimonios, plazos ni descuentos: solo la prueba que aparece arriba.
Pasa a humano (escribe [HUMANO] al final) si: se enfada, pide hablar con una persona, ya es cliente, pregunta algo legal o médico, o no avanzáis en 3 mensajes.
Si te preguntan directamente si eres una IA, di la verdad."""


def clave():
    for k in ('ANTHROPIC_API_KEY', 'OPENROUTER_API_KEY'):
        if c.env(k):
            return k, c.env(k)
    if shutil.which('claude'):
        return 'CLAUDE_CODE', ''
    raise SystemExit('Para probar necesito Claude Code (comando claude) o ANTHROPIC_API_KEY / OPENROUTER_API_KEY en ~/Contenido/.env')


def llamar(k, v, sistema, hist):
    if k == 'CLAUDE_CODE':
        chat = '\n\n'.join(('LEAD' if m['role'] == 'user' else 'TÚ') + ':\n' + m['content'] for m in hist)
        r = subprocess.run(['claude', '-p', f'Conversación hasta ahora:\n\n{chat}\n\nEscribe SOLO tu siguiente mensaje al lead.',
                            '--system-prompt', sistema, '--model', 'sonnet', '--tools', ''],
                           capture_output=True, text=True, timeout=240)
        salida = r.stdout.strip()
        if r.returncode != 0 or not salida or 'Not logged in' in salida or 'Please run /login' in salida:
            raise SystemExit('Claude Code no ha contestado (¿sesión iniciada? abre «claude» y haz /login), o pon '
                             f'ANTHROPIC_API_KEY en {c.BASE / ".env"}. Detalle: {(salida or r.stderr.strip())[-200:]}')
        return salida
    if k == 'ANTHROPIC_API_KEY':
        req = urllib.request.Request('https://api.anthropic.com/v1/messages', json.dumps(
            {'model': 'claude-sonnet-5-5', 'max_tokens': 400, 'system': sistema, 'messages': hist}).encode(),
            {'x-api-key': v, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
        return json.load(urllib.request.urlopen(req, timeout=90))['content'][0]['text']
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', json.dumps(
        {'model': 'anthropic/claude-sonnet-5.5', 'max_tokens': 400,
         'messages': [{'role': 'system', 'content': sistema}] + hist}).encode(),
        {'Authorization': f'Bearer {v}', 'content-type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=90))['choices'][0]['message']['content']


def casos(palabra):
    return {
        'encaja y tiene prisa': [palabra, 'Gracias! Pues llevo un año con esto y no consigo que me entren clientes de forma constante',
                                 'Quiero llenar la agenda este trimestre, lo necesito ya', 'Sí, si veo que tiene sentido invierto'],
        'solo quiere el precio': ['cuánto cuesta?', 'ya pero dime más o menos', 'vale, ¿y qué incluye?'],
        'no encaja': [palabra, 'solo quería el recurso, todavía no tengo nada montado ni sé a qué dedicarme'],
    }


def probar(sistema, palabra):
    k, v = clave()
    out = []
    for caso, mensajes in casos(palabra).items():
        hist, tiempos = [], []
        out.append(f'\n## {caso}')
        for m in mensajes:
            hist.append({'role': 'user', 'content': f'Canal: instagram\nNombre del lead: Laura\nPalabra que comentó: {palabra}\nMensaje: {m}'})
            t0 = time.time()
            r = llamar(k, v, sistema, hist)
            tiempos.append(time.time() - t0)
            hist.append({'role': 'assistant', 'content': r})
            out.append(f'Lead: {m}\nSetter ({tiempos[-1]:.1f} s): {r}\n')
        out.append(f'Tiempo máximo de respuesta: {max(tiempos):.1f} s')
    texto = '\n'.join(out)
    (SALIDA / 'prueba.md').write_text(f'# Prueba del setter (vía {k})\n'
                                      'Revisa: ¿suena a ti? ¿una pregunta por mensaje? ¿no suelta precio ni agenda antes de tiempo?\n'
                                      f'{texto}\n', encoding='utf-8')
    print(texto)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--probar', action='store_true')
    ap.add_argument('--palabra', default='')
    a = ap.parse_args()
    SALIDA.mkdir(parents=True, exist_ok=True)
    aj = c.ajustes()
    s = prompt(aj)
    (SALIDA / 'prompt.txt').write_text(s, encoding='utf-8')
    flujo = json.loads((c.RAIZ / 'plantillas' / 'setter' / 'n8n-setter.json').read_text(encoding='utf-8'))
    for n in flujo['nodes']:
        if n['name'] == 'Setter IA':
            n['parameters']['options']['systemMessage'] = s
    (SALIDA / 'setter-n8n.json').write_text(json.dumps(flujo, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✓ {SALIDA / "prompt.txt"}\n✓ {SALIDA / "setter-n8n.json"}  (n8n → Import from file)')
    if a.probar:
        probar(s, (a.palabra or aj.get('palabra_clave') or 'CONTENIDO').upper())

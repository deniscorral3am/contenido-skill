# Contenido · 7 agentes, un solo cerebro

Siete agentes de Claude trabajando para tu contenido. Tú grabas y apruebas; el resto lo hacen ellos. Todos comparten el
mismo cerebro: aprenden de sí mismos, de tu audiencia, tu nicho, tu forma de comunicar, tus llamadas de venta y tus
métricas.

| # | Agente | Comando | Qué hace |
|---|---|---|---|
| 1 | Jefe de gabinete | `/jefe` | el único con el que hablas: reparte el trabajo, te trae los briefs y junta en una bandeja todo lo que necesita tu visto bueno |
| 2 | Analista | `/analista` | encuentra los reels que están reventando en tu nicho (los que multiplican la media de su cuenta) y lo que funciona en tu cuenta, y explica por qué |
| 3 | Estratega | `/estratega` | lo convierte en lo que tienes que grabar después: calendario de 7 días con embudo, formato, palabra clave y trial reels |
| 4 | Copywriter | `/copywriter` | escribe hooks y guiones con tu forma de hablar, adaptados a tu oferta y a tu avatar |
| 5 | Editor | `/edicion` | le pasas el vídeo en bruto: corta, mete animaciones, subtítulos y música con tu estilo (motor: [editor-skill](https://github.com/deniscorral3am/editor-skill)) |
| 6 | Publicador | `/publicador` | publica y programa tus reels y trial reels en tu Instagram con [Zernio](https://zernio.com) y trae las métricas |
| 7 | Setter | `/setter` | monta el «comenta PALABRA → DM» (ManyChat o Zernio) y un setter con IA que habla como tú y agenda llamadas cualificadas |

Si ya tenías otra skill con alguno de esos nombres (por ejemplo `/setter`), no se pisa: ese agente se instala como
`/contenido-<nombre>`.

**Nada sale sin tu visto bueno.** Los agentes preparan; tú apruebas desde el panel con un botón.

Hecha por [Denis Corral · Sell Your AI](https://sellyourai.io).

## Instalación

```bash
git clone https://github.com/deniscorral3am/contenido-skill ~/.claude/skills/contenido
```

Abre Claude Code y escribe `/contenido`. Te hace 5 preguntas (nicho, oferta y precio, avatar, tu Instagram y cómo
hablas), crea tu cerebro de marca, instala a los 7 agentes, los prueba con tus datos y deja programado el turno de noche.
Unos 20 minutos. Desde ese momento solo hablas con `/jefe`.

## Qué necesitas

- [Claude Code](https://claude.com/claude-code) (con tu suscripción de Claude basta) y Python 3 (solo librería estándar).
- Para el editor: lo instala él (ffmpeg, Whisper local y Chromium; gratis y sin claves). En Mac hace falta [Homebrew](https://brew.sh).
- macOS para el turno de noche automático (en Windows/Linux, `noche.py orden` te da la orden para cron).

Opcionales (todo funciona sin ellos, con menos automatización):

| Herramienta | Para qué | Sin ella |
|---|---|---|
| [Zernio](https://zernio.com) | publicar y programar reels y trial reels, leer métricas, comenta→DM por API | el publicador te deja el vídeo, el texto y la hora para subirlo tú |
| [ManyChat](https://manychat.com) + [n8n](https://n8n.io) | el setter IA contestando en vivo 24/7 | el setter te prepara los mensajes y los seguimientos |
| [Apify](https://apify.com) | leer cuentas enteras del nicho y tu cuenta (saldo gratis cada mes) | el analista trabaja con enlaces (yt-dlp) o con lo que le pegues |

Tus claves van en `~/Contenido/.env` (solo en tu ordenador).

## Cómo se usa

- **Por la mañana**: se abre `~/Contenido/PANEL.html`: lo que hizo cada agente esta noche, lo que espera tu visto bueno,
  lo que toca grabar, el calendario, tus métricas y lo que ha aprendido el cerebro. Con
  `python3 ~/.claude/skills/contenido/motor/panel.py --servir` los botones de aprobar guardan solos.
- **Durante el día**: «/jefe qué grabo hoy», «/jefe apruebo el B003», «/jefe analiza este reel: <enlace>», o deja el
  vídeo grabado en `~/Contenido/crudos/` y «/jefe edita lo que hay en crudos».
- **Por la noche**: nada. Publicador → analista → estratega → copywriter → editor → setter → el jefe te deja la bandeja.

Mira un panel de ejemplo (datos ficticios) en [`ejemplo/PANEL.html`](ejemplo/PANEL.html).

## Dónde queda todo

```
~/Contenido/
  cerebro/              el cerebro común (lo leen y escriben los 7)
    audiencia.md  nicho.md  voz.md  oferta.md  llamadas-de-venta.md  metricas.md  aprendizajes.md
  ideas.csv             lo que encuentra el analista (con múltiplo y por qué funciona)
  calendario.csv        el plan del estratega: idea → guion → grabar → crudo → editado → listo → programado → publicado
  guiones/              los guiones del copywriter
  crudos/               deja aquí tus vídeos en bruto
  editados/             los vídeos del editor
  metricas.csv          las cifras de cada publicación
  dms/                  flujos de palabras clave, setter IA, conversaciones y llamadas
  bandeja/              lo que espera tu visto bueno (y el historial de decisiones)
  PANEL.html            tu panel
  .env                  tus claves (Zernio, Apify…)
```

## Motor

| Script | Para qué |
|---|---|
| `motor/instalar.py` | crea `~/Contenido` y el cerebro, instala los 7 agentes como skills y descarga el editor |
| `motor/datos.py` | cerebro, ideas, calendario, métricas, bandeja de aprobación y ajustes (lo usan todos los agentes) |
| `motor/reels.py` | el analista: cuentas y hashtags con Apify, enlaces con yt-dlp, transcripción con Whisper, múltiplo sobre la mediana |
| `motor/zernio.py` | publicar / programar / trial reels, métricas y automatización comenta→DM con tu clave de Zernio |
| `motor/setter_prompt.py` | el prompt del setter IA desde tu cerebro + flujo de n8n + 3 conversaciones de prueba |
| `motor/panel.py` | el panel (`--servir` para aprobar con un clic) |
| `motor/noche.py` | programar / lanzar / quitar el turno de noche (launchd) |
| `motor/ejemplo.py` | regenera `ejemplo/PANEL.html` con un perfil ficticio |

Licencia MIT.

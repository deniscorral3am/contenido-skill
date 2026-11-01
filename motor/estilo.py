"""Estilo común de las páginas que genera el equipo (parte de la mañana y propuestas). Oscuro, Inter, un solo acento."""
import html

ACENTO = '#C9A35A'


def esc(s):
    return html.escape(str(s if s is not None else ''))


def eur(n):
    try:
        return f"{round(float(n)):,} €".replace(',', '.')
    except (TypeError, ValueError):
        return esc(n)


def css(acento=ACENTO):
    return f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root{{--bg:#000;--card:#111113;--card2:#18181b;--line:rgba(255,255,255,.08);--line2:rgba(255,255,255,.16);
--tx:#F5F5F7;--tx2:#A1A1A6;--tx3:#6E6E73;--ac:{acento};--ok:#30D158;--warn:#FF9F0A;--bad:#FF453A}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--tx);font:16px/1.5 Inter,system-ui,sans-serif;font-feature-settings:'cv11','ss01','ss03';
-webkit-font-smoothing:antialiased;padding:56px 20px 80px}}
.w{{max-width:880px;margin:0 auto}}
.eyebrow{{font-size:12px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--ac)}}
h1{{font-size:clamp(34px,6vw,56px);font-weight:700;letter-spacing:-.045em;line-height:1.05;margin:12px 0 14px}}
h2{{font-size:24px;font-weight:700;letter-spacing:-.03em;margin:0 0 6px}}
h3{{font-size:17px;font-weight:600;letter-spacing:-.015em}}
.sub{{color:var(--tx2);font-size:18px;max-width:640px}}
.oro{{background:linear-gradient(100deg,{acento},#DDBE7C 70%,#F2DDA8);-webkit-background-clip:text;background-clip:text;color:transparent}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:24px 26px;margin-top:16px}}
.card.dest{{border-color:color-mix(in srgb,var(--ac) 35%,transparent);
background:radial-gradient(120% 80% at 50% -20%,color-mix(in srgb,var(--ac) 16%,transparent),transparent 60%),var(--card)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-top:28px}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px 20px}}
.kpi b{{display:block;font-size:34px;font-weight:700;letter-spacing:-.04em;font-variant-numeric:tabular-nums}}
.kpi span{{color:var(--tx2);font-size:13px}}
.sec{{margin-top:48px}}
.row{{display:flex;gap:14px;align-items:flex-start;padding:14px 0;border-top:1px solid var(--line)}}
.row:first-of-type{{border-top:0}}
.tag{{font-size:11px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;padding:4px 9px;border-radius:999px;
border:1px solid var(--line2);color:var(--tx2);white-space:nowrap}}
.tag.ac{{color:var(--ac);border-color:color-mix(in srgb,var(--ac) 40%,transparent)}}
.tag.ok{{color:var(--ok);border-color:rgba(48,209,88,.35)}} .tag.bad{{color:var(--bad);border-color:rgba(255,69,58,.35)}}
.tag.warn{{color:var(--warn);border-color:rgba(255,159,10,.35)}}
.mut{{color:var(--tx2)}} .mut3{{color:var(--tx3);font-size:13px}}
.msg{{background:var(--card2);border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin-top:8px;
color:var(--tx);font-size:14.5px;white-space:pre-wrap}}
.av{{width:44px;height:44px;border-radius:50%;flex:none;display:grid;place-items:center;font-weight:700;font-size:15px;
background:var(--card2);border:1px solid var(--line2);color:var(--ac)}}
a{{color:var(--ac);text-decoration:none}} a:hover{{text-decoration:underline}}
.btn{{display:inline-block;background:linear-gradient(100deg,{acento},#DDBE7C 70%,#F2DDA8);color:#1A1406;font-weight:600;
padding:14px 26px;border-radius:999px;margin-top:18px}}
.btn:hover{{text-decoration:none;filter:brightness(1.05)}}
ol.todo{{list-style:none;counter-reset:t}} ol.todo li{{counter-increment:t;display:flex;gap:12px;padding:10px 0;
border-top:1px solid var(--line)}} ol.todo li:first-child{{border-top:0}}
ol.todo li:before{{content:counter(t);width:26px;height:26px;flex:none;border-radius:50%;display:grid;place-items:center;
font-size:13px;font-weight:700;color:#1A1406;background:var(--ac)}}
table{{width:100%;border-collapse:collapse;font-size:15px}} td,th{{text-align:left;padding:10px 8px;border-top:1px solid var(--line)}}
th{{color:var(--tx3);font-weight:500;font-size:13px;border-top:0}} td.n{{text-align:right;font-variant-numeric:tabular-nums}}
.pie{{margin-top:64px;color:var(--tx3);font-size:13px;text-align:center}}
@media (max-width:600px){{.card{{padding:20px}} .row{{flex-wrap:wrap}}}}
"""


def pagina(titulo, cuerpo, acento=ACENTO):
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(titulo)}</title>'
            f'<style>{css(acento)}</style></head><body><div class="w">{cuerpo}</div></body></html>')

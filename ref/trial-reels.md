# Trial reels (Instagram)

Un trial reel se enseña primero solo a gente que **no te sigue**. Si funciona, pasa a tu perfil; si no, no ensucia tu feed.

## Para qué los usa el sistema
1. **Probar ganchos**: mismo vídeo, otro gancho (variantes B y C del guion). El que más retiene se queda para el reel principal.
2. **Reciclar ganadores**: un reel tuyo que pasó de 2x tu mediana → vuelve como trial con otro inicio, otra música o
   1,1x de velocidad, 2–4 semanas después.
3. **Temas nuevos sin riesgo**: un pilar que no has tocado nunca.

## Cómo
- Publicar: `zernio.py publicar video.mp4 --texto "…" --cuando <fecha> --trial manual` (o `--trial auto` para que
  Instagram lo pase solo al perfil si funciona).
- Máximo ~5 trial reels al día (límite de Instagram); el sistema no programa más de los `trials_por_semana` de tus ajustes.
- A las 72 h el publicador mira las visitas: si supera tu mediana, propone en la bandeja pasarlo al perfil (manual) y el
  analista apunta qué gancho ganó en `cerebro/aprendizajes.md`.
- Necesita cuenta profesional (Business o Creator).

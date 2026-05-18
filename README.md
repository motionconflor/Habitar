# MOTioN — HABITAR

Plataforma digital de movimiento consciente.

**4 estados. 4 experiencias. Un camino hacia tu cuerpo.**

---

## El Programa

| Estado | Intención |
|--------|-----------|
| PAUSAR | Detenerse. Escuchar. |
| LIBERAR | Soltar tensión. Abrir espacio. |
| FLUIR | Moverse sin resistencia. |
| HABITAR | Estar presente en el cuerpo. |

---

## Estructura del proyecto

```
motion-habitar/
├── index.html              ← Landing page (GitHub Pages)
├── styles.css              ← Estilos (minimalismo cálido)
├── docs/                   ← Material de marketing
│   └── brochure.pdf
├── bot/
│   ├── main.py             ← Entry point del bot
│   ├── config.py           ← Token + configuración
│   ├── states.py           ← Estados FSM
│   ├── handlers/           ← Manejadores de comandos
│   ├── keyboards/          ← Teclados inline y reply
│   ├── services/           ← Lógica de usuarios y lecciones
│   └── data/
│       └── lessons.json    ← Contenido de los 4 estados
```

---

## Tecnología

- **Front:** HTML5 + CSS3 (GitHub Pages)
- **Bot:** Python 3.11+ + aiogram 3.x
- **Video:** Vimeo (embeds privados)
- **Pagos:** MercadoPago Checkout Pro (link)

---

## Inicio rápido

### Landing
```bash
# Abrir localmente
open index.html
# o desplegar en GitHub Pages desde Settings → Pages
```

### Bot
```bash
pip install -r requirements.txt
cd bot
# Crear .env con BOT_TOKEN=...
python main.py
```

---

## Licencia

AGPL-3.0 — ver [LICENSE](LICENSE)

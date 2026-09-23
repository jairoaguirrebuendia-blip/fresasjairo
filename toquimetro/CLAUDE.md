# CLAUDE.md — Toquímetro

## Descripción
Toquímetro es una app mobile-first para **registrar y analizar el consumo de cannabis**: mide el tiempo desde el último consumo, guarda sesiones (método, cantidad, efecto, estado de ánimo) y muestra estadísticas para fomentar la consciencia y el control.

## Stack
- HTML5 + CSS3 + JavaScript ES6+ vanilla, en un solo archivo: `www/index.html`
- Persistencia: `localStorage` (clave `"toquimetro"`)
- Empaquetado Android: Capacitor 7 (`android/`), plugins `@capacitor/app` y `@capacitor/status-bar`
- Sin backend, sin cuentas, sin anuncios

## Estructura
```
toquimetro/
├── www/                 # la app web (lo que ve el usuario)
│   ├── index.html
│   ├── manifest.webmanifest
│   └── icon-*.png
├── assets/              # fuentes de ícono y splash (icon.svg → PNG)
├── android/             # proyecto nativo generado por Capacitor
├── capacitor.config.json
└── package.json
```

## Flujo de trabajo
1. Edita `www/index.html`.
2. `npm install` y luego `npx cap sync android` para copiar la web al proyecto Android.
3. Compila: `cd android && ./gradlew assembleDebug` (requiere Android SDK + JDK 21),
   o deja que lo haga GitHub Actions (`.github/workflows/toquimetro-android.yml`).
4. Íconos: edita `assets/icon.svg`, regenera los PNG y ejecuta `npm run icons`.

## Convenciones
- Mantener todo en `www/index.html` sin frameworks ni bundler.
- Los plugins nativos se usan vía `window.Capacitor.Plugins` y solo si `Capacitor.isNativePlatform()`.
- No cambiar la clave de `localStorage` (perdería los datos de los usuarios).

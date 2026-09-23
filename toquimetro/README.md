# Toquímetro 🌿

App Android para registrar y analizar tu consumo: contador desde el último toque, historial y análisis. Todo se guarda solo en tu teléfono.

## Descargar el APK
Cada push que toque `toquimetro/` compila el APK en GitHub Actions
(workflow **Toquímetro · APK Android**):

- **Releases → "Toquímetro (última versión)"** → descarga `toquimetro.apk`, o
- **Actions → última ejecución → Artifacts → `toquimetro-apk`**.

En el teléfono, abre el APK y permite *instalar apps desconocidas* para tu navegador o gestor de archivos.

## Compilar en tu computadora
Requisitos: Node 22, JDK 21 y Android Studio (Android SDK).

```bash
cd toquimetro
npm install
npx cap sync android
npx cap open android      # abre Android Studio → Run ▶
# o por consola:
cd android && ./gradlew assembleDebug
```
El APK queda en `android/app/build/outputs/apk/debug/app-debug.apk`.

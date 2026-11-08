# Ciriaco AceStream - M3U automática

Componente independiente de [TitoFlorenn Server](https://github.com/titoflorenn/Titoflorenn-Server).
No es un complemento ni una copia de la configuración del servidor. Su función
es producir una M3U estable que Jellyfin consulta con su propio intervalo.

## Flujo actual

1. GitHub Actions ejecuta el extractor a las `00:17`, `03:17`, `06:17`, etc. UTC
   (`17 */3 * * *`); la ejecución puede retrasarse.
2. Playwright abre la web y obtiene los enlaces AceStream del DOM, incluidos
   paneles desplegables. Aunque la web pueda usar JSON internamente, el script
   actual **no descarga directamente un endpoint JSON**.
3. Normaliza nombres, elimina hashes idénticos y ordena los resultados.
4. Compara la M3U nueva con la versionada. Solo hace commit si hay cambios.
5. Jellyfin vuelve a descargar esa URL según el intervalo configurado por su
   administrador, independientemente del horario de GitHub Actions.

No se agrupan aquí canales con hashes distintos: esa identidad y sus fuentes
alternativas corresponden al catálogo de Canales-Acestream. Se conserva la lista
anterior si hay menos de 12 fuentes o cae más del 70 % del número previo.

## Uso

URL estable para Jellyfin:

https://raw.githubusercontent.com/titoflorenn/ciriaco-acestream/main/canales.m3u

GitHub Actions consulta `https://ciriaco.netlify.app/` cada 3 horas y modifica `canales.m3u` únicamente si detecta cambios.
Se ejecuta también manualmente desde **Actions > Actualizar Ciriaco M3U > Run workflow**.
Se utiliza Playwright porque los enlaces pueden generarse mediante JavaScript.
Se eliminan hashes repetidos; se preservan variantes diferentes del mismo canal.
Si falla la extracción o hay una caída anómala del número de enlaces, no se modifica la lista.

**Avisos:** GitHub puede retrasar ejecuciones programadas; el propietario de la web puede cambiar su HTML. GitHub deshabilita algunos workflows programados de repositorios públicos inactivos durante 60 días. Los enlaces provienen de terceros y no se comprueba su reproducción ni su autorización.

Los ajustes de actualización de canales dentro de Jellyfin son independientes del horario de GitHub Actions.

# Ciriaco AceStream - M3U automática

URL estable para Jellyfin:

https://raw.githubusercontent.com/titoflorenn/ciriaco-acestream/main/canales.m3u

GitHub Actions consulta `https://ciriaco.netlify.app/` cada 3 horas y modifica `canales.m3u` únicamente si detecta cambios.
Se ejecuta también manualmente desde **Actions > Actualizar Ciriaco M3U > Run workflow**.
Se utiliza Playwright porque los enlaces pueden generarse mediante JavaScript.
Se eliminan hashes repetidos; se preservan variantes diferentes del mismo canal.
Si falla la extracción o hay una caída anómala del número de enlaces, no se modifica la lista.

**Avisos:** GitHub puede retrasar ejecuciones programadas; el propietario de la web puede cambiar su HTML. GitHub deshabilita algunos workflows programados de repositorios públicos inactivos durante 60 días. Los enlaces provienen de terceros y no se comprueba su reproducción ni su autorización.

Los ajustes de actualización de canales dentro de Jellyfin son independientes del horario de GitHub Actions.

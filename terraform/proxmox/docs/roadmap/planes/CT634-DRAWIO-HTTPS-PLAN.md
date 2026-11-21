# CT634 — Draw.io HTTPS e integración nativa

21/11/2026 Europe/Madrid. Ronda `implementation`, base
`4bd13663353baab449a1ed92fa26fd2f4ca97d5e`, rama `ops/knowledge-drawio-https`,
worktree `../mailerblend-platform-infra-knowledge-drawio`. PR #90 fusionado.
El propietario publicó el registro. Servir Draw.io en CT109 con TLS
verificado en ambos saltos y acceso LAN. Conservar el HTTP loopback para
monitorización. Configurar por el mecanismo nativo de Outline y probar en
un documento de validación, sin cambiar otros vhosts ni contenido humano.

## Evidencia y resultado

Autoritativos Route 53 devolvieron la IP esperada. Tras propagación, DNS
normal en la LAN y HTTPS HTTP 200. Wildcard válido en CT109. Desde una IP
distinta de CT109 el salto interno devolvió 403. La integración nativa
`embed/diagrams` devuelve el origen esperado desde la API de Outline.
En Chromium, el comando nativo abrió únicamente la URL del editor
autoalojado. Se guardó un rectángulo editable. Se reabrió, se añadió una
elipse y se guardó el segundo adjunto. Tras reiniciar solo Draw.io, el
mismo documento volvió a abrir el rectángulo y la elipse. El SVG guardado
incluye XML editable. La sonda del CT siguió en verde después de estabilizar.
La receta amplió el respaldo cifrado a las carpetas edge de CT633/634.
SMTP sigue pendiente de un transporte TLS que valide el relay CT632.

[PR #91](https://github.com/eduardo152030/mailerblend-platform-infra/pull/91).

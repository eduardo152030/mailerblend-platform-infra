# Diagnóstico de eno1 — 2026-11-13

Fase 7. IaC Reliability, Security & Disaster Recovery. Tarea NET-ENO1:
diagnóstico DONE; resolución física TODO. Captura 2026-11-13 11:42:46 CET
(Europe/Madrid), SSH estricto como root. Producción solo lectura; sin instalaciones,
test de cable, reinicios, recargas ni cambios. Sin commit/push.

## Resultado

| Dato | Evidencia |
|---|---|
| NIC | Intel Ethernet Connection (5) I219-LM, PCI 8086:15e3 |
| Driver / firmware | e1000e, kernel 6.8.12-4-pve / 0.1-4 |
| Máximo soportado | 1000baseT/Full: 1 Gb/s; no anuncia modos superiores |
| Host anuncia | 10/100 Half/Full y 1000 Full; autonegociación sí |
| Otro extremo anuncia | 10/100 Half/Full; autonegociación sí; no anuncia 1000 |
| Negociado | 100 Mb/s Full Duplex; enlace activo; autonegociación on |
| Errores físicos | CRC, RX/TX errors, colisiones, carrier y demás contadores filtrados: 0 |
| Descartes | ip: RX dropped 2605 acumulados; TX dropped 0. No prueban cable defectuoso |
| Configuración | Sin velocidad/duplex/autoneg forzados en rutas examinadas; includes vacíos; hooks genéricos |
| Kernel | Enlace a 100 Full desde arranque; sin caídas posteriores en mensajes disponibles |
| iperf3 | No encontrado; no instalado |

## Interpretación

Culpable más probable **b: puerto del switch/router limitado a 100 Mb/s o
anuncio de ese puerto limitado por su configuración**. El dato probado es que
el vecino no anuncia gigabit; no demuestra si su hardware es Fast Ethernet o
si está configurado así. No se accedió al switch/router.
**a: cable/conector** sigue siendo alternativa: no se han comprobado pares ni
descartado reducción automática por problemas físicos. Cero CRC a 100 no valida
el cable para gigabit. **c: configuración del host** sin evidencia en las rutas
revisadas y contradicha por anuncio 1000/autoneg on. **d: driver/firmware** sin
indicios positivos en estas lecturas; no se ha realizado prueba exhaustiva.

La NIC actual puede llegar a 1 Gb/s, pero no a 2,5/5/10 Gb/s según sus modos.
vmbr0 utiliza eno1 y no impone aquí una velocidad física de 100 Mb/s.

## Pasos del propietario

1. Identificar modelo y puerto exactos del switch/router y confirmar capacidad
   gigabit y configuración auto con anuncio 1000.
2. En ventana con acceso local, probar cable Cat5e/Cat6 conocido y completo,
   preferiblemente directo sin rosetas/adaptadores intermedios.
3. Probar otro puerto gigabit conocido, cambiando una variable cada vez.
   Estas acciones físicas interrumpen temporalmente la gestión remota.
4. Después comprobar `ethtool eno1`: Speed 1000Mb/s, Duplex Full,
   Auto-negotiation on y anuncio 1000 del vecino. Comparar contadores con baseline.
   No forzar 1000 desde el host para intentar resolver la ausencia del anuncio vecino.

Test `ethtool --cable-test eno1` NO ejecutado: puede interrumpir el enlace;
soporte específico no demostrado (supports-test no acredita cable-test).
Requiere OK explícito y ventana segura.

Rendimiento opcional, NO ejecutado. iperf3 falta en PVE: instalación pendiente
de aprobación separada por fase solo lectura. Con herramienta disponible:
en otro equipo LAN `iperf3 -s`; en PVE `iperf3 -c <IP_LAN> -t 20` y después
`iperf3 -c <IP_LAN> -t 20 -R`. Mide TCP extremo a extremo y añade tráfico;
no demuestra por sí solo la capacidad máxima de la NIC.

## Fase 3 y límites

No procede proponer modificación exacta de interfaces ni rollback de una
modificación no justificada: no se identifica c como causa. No se aplicó nada.
Próximo paso: comprobación física/administrativa del puerto por el propietario.
Fase 7 global permanece IN PROGRESS; no se cierran pendientes heredados.

[Evidencia de comandos](evidence/2026-11-13-eno1-diagnostic.json).

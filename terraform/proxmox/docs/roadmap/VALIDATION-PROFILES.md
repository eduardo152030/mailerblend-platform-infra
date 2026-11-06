# Fase 4 — perfiles de validación D-038

## D-040 vigente — ventanas por servicio

|Servicio|Segundos|Muestras a30s|
|---|---:|---:|
|LXC convencionales|180|7|
|Grafana CT611|180|7|
|Blackbox CT616|180|7|
|CRM CT618 yEVA CT622|300|11|
|Prometheus/Alertmanager CT610|600|21|

Solo nuevas observaciones; lasiniciadas conservan su duración fijada al empezar.
El generador común usa `profile_for(ct)`; eldriver captura losvalores alentrar en
`observe`, incluido el camino deentregaTelegram porlote. ElperfilCRITICAL conserva
sus controles reforzados; las excepciones porCT cambian únicamente duración/muestras.
Las pruebas históricas y evidenciasD039 mantienen los600s realmente ejecutados.

Posterior: siguen scrape/reglasPrometheus yAlertmanager sin parar; sus anomalías
quedan enestado/historial de alertas ynotificaciones existentes. Losguards entreCT
comprueban cobertura yerroresTelegram. No se lanza retrospectivamentewatch900s ni
se repiteCPU/RAM deaceptados. Esta política no prueba por sí sola recepción humana
ni reglas con `for` aún no transcurrido. Todo fallo observado debe registrarse y
clasificarse; regresión/fallocompartido detiene avance yrequiere recuperación.
Sin modificación del contratoCPU/RAM, tolerancias,backup/rollback nialcance autorizado.
17pruebas dirigidasPASS; no suitecompleta ni intervenciones enproducción.

## Historial D038/D039 — duraciones anteriores, no vigente donde difiera

D039: driverCRITICAL adaptado y ejecutado para622/611/616/610;618revertido.
13DONE/4BLOCKED/0PENDING. [Resultado](CRITICAL-D039-EXECUTION.md).
Política cerrada; no nueva ejecución autorizada. El resto conserva el registro
de preparaciónD038, sustituido donde difiera porD039.

Política aprobada por el propietario; sustituye la obligación general dewatch900s,
rollback ensayado y entregaTelegram por cada CT. No modifica los criterios de
aceptaciones históricas ni relaja tolerancias/frescura deCPU/RAM.

|Control|STANDARD|CRITICAL|
|---|---|---|
|Observación|180s,7muestras cada30s|600s,21muestras cada30s|
|Vigilancia adicional obligatoria|No|Según riesgo específico; no900s automático|
|Rollback|Disponible; prueba anterior verificable del mismo procedimiento/dependencias o ensayo nuevo si cambió|Plan específico y continuidad/recuperación verificadas|
|Aplicación|Baseline verificado,sin regresión; unhealthy previo permitido con alertas conservadas|Igual, más dependencias y continuidad específicas|
|Telegram|AMready y errores sin aumento; entrega real porlote/cambio de configuración|Igual, continuidad del plano de alertas|
|Métricas|Node/cAdvisor,CPU/RAM,Docker,cgroups,identidad/timestamps válidos; sin ausentes convertidos en0|Igual|
|Seguridad|Preflight,backupverificado,Promrecogiendo,sinOOM/reinicios inesperados,idempotencia|Igual más recuperación específica|

Un fallo aislado exige estado seguro/cobertura conservada y dependencia independiente
antes de saltar; fallo compartido, backup fallido, regresión no contenida, datos en
riesgo o estado incierto detienen globalmente. Un error del lector no demuestra
un error del exporter. No reintentos indefinidos ni reparaciones de apps ajenas.

Implementación local:

- [Configuración](../../services/common/phase4-validation-profiles.yml).
- [Selección,plan y aceptación](../../scripts/phase4-validation-profiles.py).
- [Ventanas](../../scripts/rollout-observation-policy.py) acepta STANDARD/CRITICAL;
  conserva R1–R7 como reproducción histórica de procedimientos anteriores.
- [Clasificador](../../scripts/phase4-skip-policy.py) evalúa evidencias con
  `validation_profile` mediante el contrato nuevo, sin exigirwatch/healthy inicial.
- Reuso de pruebas/rollback exige resultadoPASS,evidencia verificada y huella exacta
  de todos los archivos relevantes y versiones de dependencias. No generar una
  prueba de reuso a partir de la mera existencia de un archivo antiguo.

Estos cambios son preparación local de política/aceptación, **no un despliegue ni
una certificación del ejecutor crítico**. El driver históricoD035/D037 conserva sus
pasos deejecución y no debe usarse como ejecutorSTANDARD sin adaptar su orquestación
al perfil en una intervención autorizada. Ningún targetSTANDARD pendiente requiere
esa adaptación en esta sesión. El próximo ejecutor crítico necesitará pasos de
continuidad/recuperación específicos y autorización; el perfil no la concede.

Estado verificado D038:9DONE,3BLOCKED617/615/614,5PENDING618/622/611/616/610;
**cero STANDARD pendientes autorizados**. No despliegues ni cambios de producción.
Orden propuesto:618CRM→622EVA, después611Grafana→616Blackbox→610Prometheus.
CRM/EVA son las aplicaciones pendientes; observabilidad al final mantiene el plano
actual durante sus cambios. No implica dependencia funcionalCRM→EVA demostrada;
revisarla en preflight. Mantener bloqueados para recuperaciónindividual al final.

Comando local de planificación (usar salida nueva):

```bash
python3 scripts/phase4-validation-profiles.py --output /tmp/phase4-next-plan.json
```

25pruebas pertinentes PASS (8perfiles,13clasificación,4ventanas), sin repetir80pruebas
comunes ni lecturas largas deCPU/RAM. Producción porlectura:9cadenas sanas,9runtimes
aceptados intactos,17Node/17cAdvisor/11BlackboxUP,Prom/AMready200,sin aumento de
fallosTelegram. No nuevo testdeentrega; los56fallos acumulados sonhistóricos y no
se interpretan como0. [Evidencia](evidence/2026-11-06-d038-production-check.json).

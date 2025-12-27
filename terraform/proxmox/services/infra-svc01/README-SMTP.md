Perfecto 👍
Aquí tienes un **README pequeño, claro y operativo** para dejar **registro exacto** de la configuración SMTP de NocoDB en tu infra.
Está pensado para que dentro de **6–12 meses** no tengas que volver a pensar nada.

Puedes copiarlo tal cual a un archivo, por ejemplo:

```
services/infra-svc01/README-SMTP.md
```

---

```md
# NocoDB – Configuración SMTP (OSS / Self-Hosted)

Este documento registra la configuración SMTP utilizada por NocoDB
en el servicio `infra-svc01` dentro del homelab Mailerblend / Núcleo Tecnológico.

⚠️ IMPORTANTE  
En **NocoDB OSS**, el SMTP **NO se configura desde la UI**.  
La UI muestra el formulario, pero **no persiste ni aplica cambios**.  
La **única forma válida** es mediante **variables de entorno**.

---

## 📍 Ubicación del servicio

- Servicio: `infra-svc01`
- IP local: `192.168.1.112`
- Puerto expuesto: `18080`
- URL local:  
```

[http://192.168.1.112:18080](http://192.168.1.112:18080)

```

---

## 📁 Archivos implicados

- Repo:
```

services/infra-svc01/compose/.env

```
- Contenedor (solo referencia, no editar manualmente):
```

/opt/infra-svc01/.env

````

---

## ✉️ Proveedor SMTP

- Proveedor: **Nominalia**
- Host: `authsmtp.securemail.pro`
- Puerto: `465`
- Seguridad: `SSL`
- Usuario SMTP: email completo del buzón

---

## 🔐 Variables SMTP configuradas

```env
NC_SMTP_HOST=authsmtp.securemail.pro
NC_SMTP_PORT=465
NC_SMTP_SECURE=true
NC_SMTP_USERNAME=team@nucleotecnologico.es
NC_SMTP_PASSWORD=********
NC_SMTP_FROM=team@nucleotecnologico.es
````

📌 Notas importantes:

* No usar comillas
* No usar `${VARIABLES}`
* Las passwords SMTP **sí pueden contener caracteres especiales**
* Nunca exportar estas variables en bash sin comillas (usar heredoc)

---

## 🚀 Aplicar cambios

Desde el host Proxmox (NO desde el contenedor):

```bash
cd ~/work/mailerblend-platform-infra/terraform/proxmox

./scripts/deploy-service.sh infra-svc01 192.168.1.112
ssh root@192.168.1.112 'docker restart infra-svc01-nocodb'
```

---

## ✅ Verificación

### 1️⃣ Confirmar variables dentro del contenedor

```bash
ssh root@192.168.1.112 \
'docker inspect -f "{{range .Config.Env}}{{println .}}{{end}}" infra-svc01-nocodb | egrep "^NC_SMTP_"'
```

### 2️⃣ Prueba funcional REAL

En la UI de NocoDB:

```
Settings → Users → Invite user
```

* Introducir un email válido
* Si el correo llega → **SMTP OK**

Resultado validado:
✔️ “Invitation sent successfully”
✔️ Email recibido correctamente

---

## 🧠 Lecciones aprendidas

* NocoDB OSS ignora configuración SMTP desde la UI
* `docker compose down -v` es obligatorio si se cambian credenciales DB
* El indicador real de éxito es **correo recibido**, no logs ni UI

---

## 📅 Estado

* SMTP: ✅ Operativo
* Fecha de validación: 2025-12-27
* Configuración aplicada y verificada end-to-end

```

---

Si quieres, en el siguiente paso puedo:
- Integrarlo en tu **runbook principal**
- Crear una versión **PDF**
- O hacer un **README estándar reutilizable** para otros servicios con SMTP

Tú mandas 🚀
```

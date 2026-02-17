Perfecto 👌
Te voy a crear una **documentación clara, ordenada y segura**, alineada con tu filosofía:

* ✅ Orden exacto
* ✅ Backup obligatorio antes de tocar nada
* ✅ Sin romper otros dominios
* ✅ Certificado primero
* ✅ Sin conflictos de `server_name`
* ✅ Compatible con tu edge-router LXC

Esto es producción-grade.

---

# 📘 Runbook — Agregar nuevo servicio en `root@edge-router`

## 🎯 Objetivo

Publicar un nuevo servicio interno (ej: `infra-pulpo`) detrás de:

```
https://infra-pulpo.mailerblend.com
```

Sin afectar otros dominios existentes.

---

# 🔒 REGLA CRÍTICA

ANTES de tocar cualquier archivo:

```bash
cp -a /etc/nginx /etc/nginx.backup.$(date +%F-%H%M%S)
```

Esto crea una copia completa y reversible.

---

# 🧭 ORDEN CORRECTO (NO cambiar el orden)

---

# 1️⃣ Verificar DNS (desde tu máquina local)

```bash
dig +short infra-pulpo.mailerblend.com
```

Debe devolver tu IP pública actual.

Si no → no continuar.

---

# 2️⃣ Verificar que el backend responde (desde edge-router)

```bash
curl -I http://192.168.1.119:15678
```

Debe responder `200` o `302`.

Si falla → arreglar backend primero.

---

# 3️⃣ Generar certificado (SIN tocar nginx manualmente)

```bash
certbot --nginx -d infra-pulpo.mailerblend.com
```

Esto:

* Genera el certificado
* Lo instala temporalmente en default
* Activa autorenovación automática

Verificar:

```bash
ls -l /etc/letsencrypt/live/infra-pulpo.mailerblend.com/
```

---

# 4️⃣ Limpiar el `default` (IMPORTANTE)

Buscar si certbot añadió bloques para el nuevo dominio:

```bash
grep -R "infra-pulpo.mailerblend.com" /etc/nginx/sites-available/default
```

Si aparece → editar:

```bash
nano /etc/nginx/sites-available/default
```

Eliminar SOLO los bloques correspondientes a ese dominio
(No tocar otros dominios)

Guardar.

---

# 5️⃣ Crear vhost dedicado (NUNCA usar default)

```bash
nano /etc/nginx/sites-available/infra-pulpo.conf
```

Contenido estándar seguro:

```nginx
server {
    listen 80;
    server_name infra-pulpo.mailerblend.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name infra-pulpo.mailerblend.com;

    ssl_certificate /etc/letsencrypt/live/infra-pulpo.mailerblend.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/infra-pulpo.mailerblend.com/privkey.pem;

    location / {
        proxy_pass http://192.168.1.119:15678;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

---

# 6️⃣ Activar el nuevo servicio

```bash
ln -sf /etc/nginx/sites-available/infra-pulpo.conf \
       /etc/nginx/sites-enabled/infra-pulpo.conf
```

---

# 7️⃣ Validar configuración (OBLIGATORIO)

```bash
nginx -t
```

Debe decir:

```
syntax is ok
test is successful
```

Si hay error → NO recargar.

---

# 8️⃣ Recargar nginx

```bash
systemctl reload nginx
```

---

# 9️⃣ Verificación final

Desde edge-router:

```bash
curl -I http://192.168.1.119:15678
```

Desde tu máquina local:

```bash
curl -I https://infra-pulpo.mailerblend.com
```

Debe devolver 200 o 302 (pero no la página default).

---

# 🔄 Autorrenovación (ya viene incluida)

Verificar timer:

```bash
systemctl list-timers | grep certbot
```

Test renovación:

```bash
certbot renew --dry-run
```

---

# ⚠️ Qué NO hacer nunca

❌ No usar `/etc/nginx/sites-enabled/default` para nuevos servicios
❌ No borrar default si otros dominios lo usan
❌ No crear vhost antes de tener certificado
❌ No hacer `systemctl restart nginx` sin `nginx -t` previo
❌ No mezclar dominios en un mismo archivo

---

# 🧠 Filosofía recomendada (tu modelo correcto)

Un dominio = un archivo:

```
/etc/nginx/sites-available/
    ├── default
    ├── mailerblend.conf
    ├── nucleo.conf
    ├── infra-pulpo.conf
```

Nunca compartir `server_name` entre archivos.

---

# 📌 Estado final correcto

* Certificado válido
* Autorrenovación activa
* Sin conflictos de server_name
* Sin afectar otros dominios
* Backend aislado
* Reverse proxy limpio

---

Si quieres, puedo generarte:

* 📄 Versión Markdown descargable
* 📦 Versión PDF para tu homelab docs
* 📘 Versión tipo Confluence
* 🧩 Versión integrada en tu repo `mailerblend-platform-infra/docs/`

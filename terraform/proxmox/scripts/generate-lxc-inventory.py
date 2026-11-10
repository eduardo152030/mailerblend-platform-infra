#!/usr/bin/env python3
"""Generate Notes input and Markdown from declared inventory plus dated observations.
No network access or production mutations. --check detects stale generated artifacts.
"""
import argparse, hashlib, ipaddress, json, re
from pathlib import Path
import yaml
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lxc_provisioning import validate as validate_new_service, pending_notes, inventory_document
ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {610,611,613,614,615,616,617,618,619,620,621,622,623,624,625,626,61211}
META_FIELDS = {'function','environment','category','project','lifecycle','code_repository',
               'application_repository','legacy_notes','applications','declared_dependencies','runbook','functional_status','pending'}
class UniqueLoader(yaml.SafeLoader):
    pass
def unique_mapping(loader, node, deep=False):
    result = {}
    for k, v in node.value:
        key = loader.construct_object(k, deep=deep)
        if key in result:
            raise ValueError('Duplicate YAML key')
        result[key] = loader.construct_object(v, deep=deep)
    return result
UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)
def read_yaml(path):
    return yaml.load(path.read_text(), Loader=UniqueLoader)
def assert_public(data):
    """Fail closed on secret assignments/URLs; no rejected values in error output."""
    text = json.dumps(data, ensure_ascii=False)
    patterns = [r'(?i)(?:password|passwd|token|secret|container_config|authorization|connection_string)\s*["\s]*[:=]\s*[^\s,}]+',
                r'https?://[^\s/]+:[^\s/]+@', r'-----BEGIN .*PRIVATE KEY-----', r'gh[pousr]_[A-Za-z0-9]{20,}']
    assert not any(re.search(p, text) for p in patterns), 'Potential secret detected (value withheld)'
def load(root=ROOT):
    declared = {p.stem:read_yaml(p) for p in sorted((root/'inventory/services').glob('*.yml'))}
    meta = read_yaml(root/'inventory/documentation.yml')
    observed = json.loads((root/'inventory/lxc-observed.json').read_text())
    routes = json.loads((root/'docs/inventory/routing-observed.json').read_text())
    assert meta['schema_version'] == 1
    assert set(meta['services']) <= set(declared), 'Missing legacy service records'
    for key in set(declared)-set(meta['services']):validate_new_service(declared[key])
    ids = [d['service']['vmid'] for d in declared.values()]
    assert len(set(ids)) == len(ids) and EXPECTED <= set(ids), 'Unexpected or duplicate CT ID'
    assert len(observed['lxcs']) == 17 and {r['ct'] for r in observed['lxcs']} == EXPECTED
    assert len({r['ct'] for r in observed['lxcs']}) == 17
    for key,m in meta['services'].items():
        assert set(m) == META_FIELDS, 'Metadata schema mismatch: '+key
        for field in META_FIELDS-{'applications','declared_dependencies','pending'}:
            assert isinstance(m[field],str) and m[field].strip(), 'Missing metadata: '+key+'/'+field
        assert isinstance(m['applications'],dict) and all(isinstance(k,str) and isinstance(v,str) for k,v in m['applications'].items())
        assert isinstance(m['declared_dependencies'],dict) and all(isinstance(v,list) and all(isinstance(x,str) for x in v) for v in m['declared_dependencies'].values())
        assert isinstance(m['pending'],list) and all(isinstance(x,str) for x in m['pending'])
        assert m['code_repository'].startswith('https://github.com/')
        assert (root/m['runbook']).is_file(), 'Missing runbook: '+key
        ipaddress.ip_interface(declared[key]['service']['ip'])
    assert_public([declared,meta,observed,routes])
    return declared,meta['services'],observed,routes,read_yaml(root/'inventory/defaults.yml')['lxc']
def domains_for(ip,routes):
    groups={g['name']:g['servers'] for g in routes.get('upstream_groups',[])}
    out=[]
    for r in routes['routes']:
        for upstream in r['proxy_upstreams']:
            host=upstream.split('://',1)[-1].split('/')[0]
            destinations=groups.get(host,[host])
            if any(x.split(':')[0] == ip for x in destinations):
                out.extend(r['server_names'])
    return sorted(set(out))
def build(root=ROOT):
    declared,meta,observed,routes,defaults=load(root)
    by_id={r['ct']:r for r in observed['lxcs']};notes={};summary=[];details=[]
    for key,d in sorted(declared.items(),key=lambda kv:kv[1]['service']['vmid']):
        s=d['service']
        if key not in meta:
            notes[key]=pending_notes(d,key)
            ct=s['vmid'];ip=s['ip'].split('/')[0]
            summary.append(f'| {ct} | {s["name"]} | {d["provisioning"]["purpose"]} | {ip} | PENDING VERIFICATION | PENDING VERIFICATION | Declarado, no desplegado | docs/inventory/{ct}-LXC-INVENTORY.md |')
            details.append(inventory_document(d,key))
            continue
        m=meta[key];r=by_id[s['vmid']];cfg=r['config'];ip=s['ip'].split('/')[0]
        observed_ip=re.search(r'(?:^|,)ip=([^,]+)',cfg['net0'])
        assert observed_ip and observed_ip.group(1) == s['ip'] and cfg['hostname']==s['name'], 'Identity mismatch: '+key
        domains=domains_for(ip,routes);dom=', '.join(domains) or 'Not verified'
        resources={k:d.get('resources',{}).get(k,defaults[k]) for k in ['cpu','memory','disk_gb']}
        sections=[f"**Función:** {m['function']}\n**Entorno:** {m['environment']} | **Categoría:** {m['category']}\n**Proyecto:** {m['project']} | **Ciclo de vida:** {m['lifecycle']}",
                  f"**Infraestructura declarada:** CT {s['vmid']} | IP {s['ip']} | CPU {resources['cpu']} | RAM {resources['memory']} MiB | disco {resources['disk_gb']} GiB\n**Observada ({observed['observed_at_utc']}):** nodo {r['node']} | {r['status']} | CPU {cfg['cores']} | RAM {cfg['memory']} MiB | rootfs {cfg['rootfs']} | SO {r['runtime']['os_release']}"]
        apps=[];held=[]
        for c in r['runtime']['containers']:
            if c['status']!='running':held.append(c['name']);continue
            if c['name'] in ['node_exporter','cadvisor']:continue
            role=m['applications'].get(c.get('compose_service'),m['applications'].get(c['name'],'Not verified: función pendiente'))
            ports=[f"{v.get('HostIp') or '*'}:{v['HostPort']}->{target}" for target,values in (c.get('ports') or {}).items() for v in (values or [])]
            apps.append(f"- {c['name']}: {role}; puertos {', '.join(ports) or 'sin publicación'}; Docker {c['health']}; imagen {c['image']}")
        sections.append('**Aplicaciones observadas (estado de proceso, no prueba funcional):**\n'+('\n'.join(apps) or '- No se observaron contenedores de aplicación activos.'))
        sections.append(f"**Dominios:** {dom} (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).\n**Dependencias declaradas en Compose:** "+('; '.join(k+' -> '+', '.join(v) for k,v in m['declared_dependencies'].items()) or 'Not verified / no depends_on declarado')+'\nDependencias externas y su disponibilidad: Not verified.')
        active_paths=sorted({c['compose_files'] for c in r['runtime']['containers'] if c['status']=='running' and c['compose_files']})
        health='; '.join(c['name']+': '+c['healthcheck_type'] for c in r['runtime']['containers'] if c['status']=='running' and c['name'] not in ['node_exporter','cadvisor']) or 'Aplicación: Not verified'
        sections.append('**Operación:**\n- Healthchecks: '+health+'\n- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.\n- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.\n- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.\n- Configuración activa observada: '+('; '.join(active_paths) or 'Not verified')+f'\n- IaC: inventory/services/{key}.yml; services/{key}/ (puede contener configuración histórica; contrastar con activa).\n- Runbook: '+m['runbook'])
        sections.append(f"**Repositorio IaC:** {m['code_repository']}\n**Repositorio de aplicación:** {m['application_repository']}\n**Funcionalidad confirmada:** {m['functional_status']}\n**Pendiente:** "+'; '.join(m['pending']))
        if held:sections.append('**Conservados detenidos (no reactivar automáticamente):** '+', '.join(held))
        if m.get('legacy_notes'):sections.append('**Nota previa conservada:** '+m['legacy_notes'])
        title=f"CT {s['vmid']} — {s['name']}"
        notes_title = title
        notes_file = d.get('documentation',{}).get('notes_file')
        if notes_file:
            source = (root/notes_file).resolve()
            assert source.is_relative_to(root.resolve()) and source.is_file(), 'Invalid Notes source'
            raw = source.read_text()
            assert raw.startswith('# ') and '\n\n' in raw, 'Notes must start with a Markdown title'
            header, body = raw.split('\n\n',1)
            notes_title = header[2:]
            sections = [body.rstrip()]
        notes[key]={'title':notes_title,'sections':sections}
        app_names=', '.join(c['name'] for c in r['runtime']['containers'] if c['status']=='running' and c['name'] not in ['node_exporter','cadvisor']) or 'Sin aplicación Docker activa'
        runbook_path = d.get('documentation',{}).get('inventory_file',m['runbook'])
        assert (root/runbook_path).is_file(), 'Missing individual inventory'
        summary.append(f"| {s['vmid']} | {s['name']} | {m['function']} | {ip} | {dom} | {app_names} | Parcial: observación verificada; funcionalidad pendiente | [{runbook_path.split('/')[-1]}](../../{runbook_path}) |")
        if d.get('documentation',{}).get('inventory_file'):
            details.append('## '+title+'\n\nFicha principal: ['+runbook_path.split('/')[-1]+'](../../'+runbook_path+'). No duplicar aquí su contenido.\n')
        else:
            details.append('## '+title+'\n\n'+'\n\n'.join(sections)+'\n')
    assert_public(notes)
    intro='''# Inventario funcional LXC — generado mediante IaC

No editar este archivo ni las notas generadas manualmente. Fuente: inventario de
recursos, `inventory/documentation.yml`, `inventory/lxc-observed.json` y rutas
Nginx filtradas. Regenerar: `python3 scripts/generate-lxc-inventory.py`.
La observación es una captura fechada; no constituye un monitor en tiempo real.
**Declarado**, **observado** y **funcionalidad confirmada** se muestran por separado.
No se atribuye un dominio por su nombre. Recursos distintos no se reconcilian aquí.

| CT | Servicio | Funcionalidad | IP | Dominio según proxy | Aplicaciones activas | Documentación | Runbook |
|---|---|---|---|---|---|---|---|
'''
    return notes,intro+'\n'.join(summary)+'\n\n'+'\n'.join(details)
def main():
    global ROOT
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');ap.add_argument('--root',type=Path,default=ROOT);args=ap.parse_args();ROOT=args.root.resolve()
    notes,markdown=build(ROOT);outputs={ROOT/'inventory/generated/lxc-notes.json':json.dumps(notes,ensure_ascii=False,indent=2)+'\n',ROOT/'docs/inventory/LXC-INVENTORY.md':markdown}
    sources = [ROOT/'inventory/documentation.yml', ROOT/'inventory/lxc-observed.json', ROOT/'docs/inventory/routing-observed.json', ROOT/'inventory/defaults.yml', ROOT/'scripts/generate-lxc-inventory.py', ROOT/'scripts/lxc_provisioning.py', ROOT/'templates/lxc-notes.tftpl'] + sorted((ROOT/'inventory/services').glob('*.yml'))
    sources += [ROOT/d['documentation']['notes_file'] for d in (read_yaml(p) for p in sorted((ROOT/'inventory/services').glob('*.yml'))) if d.get('documentation',{}).get('notes_file')]
    sources += [ROOT/d['documentation']['inventory_file'] for d in (read_yaml(p) for p in sorted((ROOT/'inventory/services').glob('*.yml'))) if d.get('documentation',{}).get('inventory_file')]
    manifest = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    outputs[ROOT/'inventory/generated/lxc-notes-manifest.json'] = json.dumps(manifest,indent=2)+'\n'
    for path,content in outputs.items():
        if args.check:assert path.is_file() and path.read_text()==content, 'Stale generated file: '+str(path.relative_to(ROOT))
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)
    print('PASS: schema, service identities, references, secret patterns and generated inventory'+(' freshness' if args.check else ''))
if __name__=='__main__':main()

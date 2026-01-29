import express from 'express';
import { PubSub } from '@google-cloud/pubsub';
import crypto from 'crypto';

const app = express();
app.use(express.json({ limit: '1mb' }));

const PROJECT_ID = process.env.GCP_PROJECT_ID || '';
const TOPIC = process.env.PUBSUB_TOPIC || '';
const INGEST_SECRET = process.env.INGEST_SECRET || '';
const COLLECTOR_VERSION = process.env.COLLECTOR_VERSION || 'v1';

let pubsub = null;
let topic = null;

if (PROJECT_ID && TOPIC) {
  pubsub = new PubSub({ projectId: PROJECT_ID });
  topic = pubsub.topic(TOPIC);
}

app.get('/healthz', (_, res) => res.status(200).send('ok'));

app.post('/ingest', async (req, res) => {
  try {
    const secret = req.header('X-Ingest-Secret') || '';
    if (!INGEST_SECRET || secret !== INGEST_SECRET) {
      return res.status(401).json({ ok: false, error: 'unauthorized' });
    }

    const e = req.body || {};

    // Normalización de payload para compatibilidad con BigQuery (tipo STRING)
    if (e.payload && typeof e.payload === 'object') {
      e.payload = JSON.stringify(e.payload);
    } else if (e.payload === undefined || e.payload === null) {
      e.payload = '{}';
    } else {
      e.payload = String(e.payload);
    }

    // Validación de campos obligatorios
    if (!e.event_name || !e.event_timestamp || !e.event_date) {
      return res.status(400).json({
        ok: false,
        error: 'missing_required_fields',
        required: ['event_name', 'event_timestamp', 'event_date']
      });
    }

    // Enriquecimiento básico
    if (!e.event_id) e.event_id = crypto.randomUUID();
    e.ingested_at = new Date().toISOString();
    e.collector_version = COLLECTOR_VERSION;

    // Si no hay Pub/Sub configurado, aceptamos el evento pero avisamos (modo bootstrap)
    if (!topic) {
      return res.status(202).json({ ok: true, mode: 'bootstrap_no_pubsub', event_id: e.event_id });
    }

    const attributes = {
      event_name: String(e.event_name || ''),
      lead_source: String(e.lead_source || ''),
      page_path: String(e.page_path || '')
    };

    // Publicación a Pub/Sub
    const messageId = await topic.publishMessage({
      data: Buffer.from(JSON.stringify(e)),
      attributes
    });

    return res.status(200).json({ ok: true, messageId, event_id: e.event_id });

  } catch (err) {
    console.error('publish_failed', err);
    return res.status(500).json({ ok: false, error: 'publish_failed' });
  }
});

const port = process.env.PORT || 8080;
app.listen(port, () => console.log(`Listening on port ${port}`));
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useLSSKnowledgeBase } from "@/hooks/use-api";
import { BookOpen, ChevronDown, ChevronUp } from "lucide-react";

const CATEGORY_LABELS: Record<string, string> = {
  SERVICES: "Servicios",
  ICP_DEFINITION: "ICP",
  PAIN_POINTS: "Pain Points",
  OBJECTIONS: "Objeciones",
  FAQ: "FAQ",
};

const PACK_BORDER: Record<string, string> = {
  GUARDIAN: "border-l-emerald-500",
  MOTOR: "border-l-blue-500",
  FORTALEZA: "border-l-purple-500",
};

function parseContent(raw: unknown): Record<string, unknown> {
  if (!raw) return {};
  if (typeof raw === "string") {
    try { return JSON.parse(raw); } catch { return {}; }
  }
  return raw as Record<string, unknown>;
}

function KnowledgeEntryCard({ entry }: { entry: Record<string, any> }) {
  const [expanded, setExpanded] = useState(false);
  const content = parseContent(entry.content);
  const borderClass = PACK_BORDER[entry.target_pack] || "border-l-muted";

  return (
    <Card className={`border-l-4 ${borderClass}`}>
      <CardHeader className="pb-2 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-sm font-medium">{entry.title}</CardTitle>
            <div className="flex gap-2">
              <Badge variant="outline" className="text-[10px]">{CATEGORY_LABELS[entry.category] || entry.category}</Badge>
              {entry.target_pack && <Badge variant="secondary" className="text-[10px]">{entry.target_pack}</Badge>}
              <span className="text-[10px] text-muted-foreground">Prioridad: {entry.priority}</span>
            </div>
          </div>
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </div>
      </CardHeader>
      {expanded && (
        <CardContent className="text-xs space-y-3 pt-0">
          {entry.category === "SERVICES" && (
            <>
              {content.tagline && <p className="italic text-muted-foreground">{String(content.tagline)}</p>}
              {content.pricing && (
                <p className="font-medium">💰 {typeof content.pricing === "object" ? (content.pricing as any)?.base_monthly || JSON.stringify(content.pricing) : String(content.pricing)}</p>
              )}
              {Array.isArray(content.what_includes) && (
                <div>
                  <p className="font-semibold text-foreground">✅ Incluye:</p>
                  <ul className="list-disc pl-4 space-y-0.5 text-muted-foreground">
                    {(content.what_includes as string[]).map((item, i) => <li key={i}>{item}</li>)}
                  </ul>
                </div>
              )}
              {Array.isArray(content.what_NOT_includes) && (
                <div>
                  <p className="font-semibold text-foreground">❌ NO incluye:</p>
                  <ul className="list-disc pl-4 space-y-0.5 text-muted-foreground">
                    {(content.what_NOT_includes as string[]).map((item, i) => <li key={i}>{item}</li>)}
                  </ul>
                </div>
              )}
            </>
          )}
          {entry.category === "ICP_DEFINITION" && (
            <>
              {content.company_profile && (
                <div className="space-y-1">
                  <p><strong>Tamaño:</strong> {(content.company_profile as any)?.size}</p>
                  <p><strong>Revenue:</strong> {(content.company_profile as any)?.revenue}</p>
                </div>
              )}
              {content.decision_maker && (
                <p><strong>Decisor:</strong> {Array.isArray((content.decision_maker as any)?.title) ? (content.decision_maker as any).title.join(", ") : String((content.decision_maker as any)?.title || "")}</p>
              )}
              {Array.isArray(content.trigger_symptoms) && (
                <div>
                  <p className="font-semibold">🚨 Síntomas clave:</p>
                  <ul className="list-disc pl-4 text-muted-foreground">
                    {(content.trigger_symptoms as string[]).slice(0, 5).map((s, i) => <li key={i}>"{s}"</li>)}
                  </ul>
                </div>
              )}
            </>
          )}
          {entry.category === "PAIN_POINTS" && (
            <pre className="whitespace-pre-wrap text-muted-foreground">{typeof content === "object" ? JSON.stringify(content, null, 2) : String(content)}</pre>
          )}
          {!["SERVICES", "ICP_DEFINITION", "PAIN_POINTS"].includes(entry.category) && (
            <pre className="whitespace-pre-wrap text-muted-foreground">{typeof content === "object" ? JSON.stringify(content, null, 2) : String(content)}</pre>
          )}
        </CardContent>
      )}
    </Card>
  );
}

export default function KnowledgeBaseSection() {
  const [category, setCategory] = useState<string>("ALL");
  const [pack, setPack] = useState<string>("ALL");

  const params: Record<string, any> = { limit: 50 };
  if (category !== "ALL") params.category = category;
  if (pack !== "ALL") params.target_pack = pack;

  const { data, isLoading , isError } = useLSSKnowledgeBase(params);
  const entries = (data as any)?.items ?? [];

  if (isError) return <p role="alert" className="text-destructive">No se pudo cargar esta configuración.</p>;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 flex-wrap">
        <BookOpen size={16} className="text-muted-foreground" />
        <Select value={category} onValueChange={setCategory}>
          <SelectTrigger className="w-[160px] h-8 text-xs"><SelectValue placeholder="Categoría" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">Todas las categorías</SelectItem>
            {Object.entries(CATEGORY_LABELS).map(([k, v]) => <SelectItem key={k} value={k}>{v}</SelectItem>)}
          </SelectContent>
        </Select>
        <Select value={pack} onValueChange={setPack}>
          <SelectTrigger className="w-[140px] h-8 text-xs"><SelectValue placeholder="Pack" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">Todos los packs</SelectItem>
            <SelectItem value="GUARDIAN">GUARDIAN</SelectItem>
            <SelectItem value="MOTOR">MOTOR</SelectItem>
            <SelectItem value="FORTALEZA">FORTALEZA</SelectItem>
          </SelectContent>
        </Select>
        <span className="text-xs text-muted-foreground ml-auto">{entries.length} entradas</span>
      </div>

      {isLoading ? (
        <div className="space-y-3">{Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-20 w-full" />)}</div>
      ) : entries.length === 0 ? (
        <p className="text-sm text-muted-foreground text-center py-8">No hay entradas para estos filtros.</p>
      ) : (
        <div className="space-y-3">
          {entries.map((entry: any) => <KnowledgeEntryCard key={entry.id} entry={entry} />)}
        </div>
      )}
    </div>
  );
}

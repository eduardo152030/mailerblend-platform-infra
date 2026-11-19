import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, Loader2 } from "lucide-react";

export interface Column<T = Record<string, unknown>> {
  key: string;
  label: string;
  render?: (value: unknown, row: T) => React.ReactNode;
  className?: string;
}

interface Props<T = Record<string, unknown>> {
  columns: Column<T>[];
  data: T[];
  total?: number;
  limit?: number;
  offset?: number;
  onPageChange?: (offset: number) => void;
  onRowClick?: (row: T) => void;
  loading?: boolean;
}

export function DataTable<T extends Record<string, unknown>>({
  columns, data, total = 0, limit = 50, offset = 0,
  onPageChange, onRowClick, loading,
}: Props<T>) {
  const page = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="rounded-lg border bg-card overflow-hidden">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/50">
              {columns.map((col) => (
                <TableHead key={col.key} className={col.className}>
                  {col.label}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-32 text-center">
                  <Loader2 className="mx-auto h-6 w-6 animate-spin text-muted-foreground" />
                </TableCell>
              </TableRow>
            ) : data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-32 text-center text-muted-foreground">
                  Sin resultados
                </TableCell>
              </TableRow>
            ) : (
              data.map((row, i) => (
                <TableRow
                  key={(row.id as string) || i}
                  className={onRowClick ? "cursor-pointer hover:bg-muted/50 transition-colors" : ""}
                  onClick={() => onRowClick?.(row)}
                >
                  {columns.map((col) => (
                    <TableCell key={col.key} className={col.className}>
                      {col.render ? col.render(row[col.key], row) : String(row[col.key] ?? "—")}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {total > limit && (
        <div className="flex items-center justify-between px-4 py-3 border-t bg-muted/30">
          <span className="text-sm text-muted-foreground">
            {offset + 1}–{Math.min(offset + limit, total)} de {total}
          </span>
          <div className="flex gap-1">
            <Button
              variant="ghost" size="sm"
              disabled={offset === 0}
              onClick={() => onPageChange?.(Math.max(0, offset - limit))}
            >
              <ChevronLeft size={16} />
            </Button>
            <Button
              variant="ghost" size="sm"
              disabled={offset + limit >= total}
              onClick={() => onPageChange?.(offset + limit)}
            >
              <ChevronRight size={16} />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

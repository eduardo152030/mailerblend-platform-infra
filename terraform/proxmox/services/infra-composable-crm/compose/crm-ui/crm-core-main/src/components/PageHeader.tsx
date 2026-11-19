import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";

interface Props {
  title: string;
  subtitle?: string;
  searchValue?: string;
  onSearch?: (q: string) => void;
  searchPlaceholder?: string;
  actions?: React.ReactNode;
}

export function PageHeader({ title, subtitle, searchValue, onSearch, searchPlaceholder, actions }: Props) {
  return (
    <div className="flex flex-col gap-3 mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="min-w-0">
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight truncate">{title}</h1>
          {subtitle && <p className="text-sm text-muted-foreground mt-0.5">{subtitle}</p>}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {actions}
        </div>
      </div>
      {onSearch && (
        <div className="relative w-full sm:max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            className="pl-9 w-full"
            placeholder={searchPlaceholder || "Buscar..."}
            value={searchValue}
            onChange={(e) => onSearch(e.target.value)}
          />
        </div>
      )}
    </div>
  );
}

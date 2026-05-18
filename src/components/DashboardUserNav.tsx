import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useDashboardSession } from "@/hooks/useDashboardSession";

type DashboardUserNavProps = {
  onProfileClick: () => void;
  /** Show name + role beside avatar on desktop (default true). */
  showDetails?: boolean;
};

export default function DashboardUserNav({
  onProfileClick,
  showDetails = true,
}: DashboardUserNavProps) {
  const { fullName, roleLabel, initials, isLoading } = useDashboardSession();

  return (
    <div
      className="flex items-center space-x-2 cursor-pointer"
      onClick={onProfileClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onProfileClick()}
    >
      <Avatar className="h-8 w-8">
        <AvatarFallback className="bg-primary text-white">
          {isLoading ? "…" : initials}
        </AvatarFallback>
      </Avatar>
      {showDetails && (
        <div className="hidden md:block text-left">
          <p className="text-sm font-medium leading-tight">
            {isLoading ? "Loading…" : fullName || "User"}
          </p>
          <p className="text-xs text-muted-foreground">{roleLabel}</p>
        </div>
      )}
    </div>
  );
}

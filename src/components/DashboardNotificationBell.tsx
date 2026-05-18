import { useQuery } from "@tanstack/react-query";
import { Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getUnreadNotificationCount } from "@/services/notificationService";

const DashboardNotificationBell = () => {
  const { data } = useQuery({
    queryKey: ["notifications-unread"],
    queryFn: getUnreadNotificationCount,
    refetchInterval: 30_000,
  });

  const count = data?.count ?? 0;

  return (
    <Button variant="ghost" size="icon" className="relative">
      <Bell className="h-5 w-5" />
      {count > 0 && (
        <span className="absolute -top-1 -right-1 bg-destructive text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
          {count > 9 ? "9+" : count}
        </span>
      )}
    </Button>
  );
};

export default DashboardNotificationBell;

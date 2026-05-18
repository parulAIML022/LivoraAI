import { LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLogout } from "@/hooks/useLogout";

type ProfileLogoutButtonProps = {
  className?: string;
  fullWidth?: boolean;
};

export default function ProfileLogoutButton({
  className = "",
  fullWidth = true,
}: ProfileLogoutButtonProps) {
  const handleLogout = useLogout();

  return (
    <Button
      type="button"
      className={`bg-blue-600 text-white hover:bg-blue-700 ${fullWidth ? "w-full" : ""} ${className}`}
      onClick={() => void handleLogout()}
    >
      <LogOut className="h-4 w-4 mr-2" />
      Log out
    </Button>
  );
}

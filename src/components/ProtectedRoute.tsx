import { Navigate, useLocation } from "react-router-dom";
import { useAuth, dashboardPathForRole } from "@/contexts/AuthContext";

type ProtectedRouteProps = {
  children: React.ReactNode;
  allowedRoles: string[];
};

export default function ProtectedRoute({
  children,
  allowedRoles,
}: ProtectedRouteProps) {
  const { session, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  if (!session) {
    return <Navigate to="/signin" state={{ from: location }} replace />;
  }

  const normalizedAllowed = allowedRoles.map((r) =>
    r === "coordinator" ? "admin" : r
  );

  if (!normalizedAllowed.includes(session.role)) {
    return <Navigate to={dashboardPathForRole(session.role)} replace />;
  }

  return <>{children}</>;
}

import { useEffect } from "react";

import { queryCurrentUser } from "./services/auth";
import { useAuthStore } from "./store/authStore";
import { AppRouter } from "./router";

export default function App() {
  const tokens = useAuthStore((state) => state.tokens);
  const currentUser = useAuthStore((state) => state.currentUser);
  const setCurrentUser = useAuthStore((state) => state.setCurrentUser);
  const logout = useAuthStore((state) => state.logout);

  useEffect(() => {
    if (!tokens?.accessToken || currentUser) return;
    queryCurrentUser()
      .then((res) => setCurrentUser(res))
      .catch(() => logout());
  }, [tokens?.accessToken, currentUser, setCurrentUser, logout]);

  return <AppRouter />;
}

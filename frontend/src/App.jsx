import { useState } from "react";
import Homepage from "./pages/Homepage";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const [page, setPage] = useState("home");

  if (page === "home")      return <Homepage onEnter={() => setPage("login")} />;
  if (page === "login")     return <Login    onLogin={() => setPage("dashboard")} />;
  if (page === "dashboard") return <Dashboard />;
}
import { FileSearchCorner, List, ScrollText, Upload } from "lucide-react";
import { Link, NavLink, Outlet } from "react-router-dom";

const NAV = [
  { to: "/upload", label: "Upload", icon: Upload },
  { to: "/documents", label: "Documents", icon: List },
  { to: "/audit", label: "Audit", icon: FileSearchCorner },
];

export default function Layout() {
  return (
    <div
      className="flex min-h-screen"
      style={{ backgroundColor: "var(--color-bg)" }}
    >
      <aside className="sidebar">
        <Link to="/documents">
          <div className="sidebar-logo flex gap-1 items-center justify-center">
            <ScrollText />
            <div className="font-bold text-ink">Document Registry</div>
          </div>
        </Link>

        <nav className="flex-1 px-3 py-4 flex flex-col gap-0.5">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                isActive ? "nav-link nav-link-active" : "nav-link"
              }
            >
              <Icon />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="flex-1 ml-56 min-h-screen">
        <Outlet />
      </main>
    </div>
  );
}

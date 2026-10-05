import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Documents from "./pages/Documents";
import Upload from "./pages/Upload";
import Audit from "./pages/Audit";

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/documents" replace />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/audit" element={<Audit />} />
      </Route>
    </Routes>
  );
}

export default App;

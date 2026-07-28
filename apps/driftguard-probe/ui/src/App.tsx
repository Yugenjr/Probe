import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { WorkspaceLayout } from "./layouts/SidebarLayout";
import { Investigations } from "./pages/Investigations";
import { InvestigationDetails } from "./pages/InvestigationDetails";
import { ConnectedPlatforms } from "./pages/ConnectedPlatforms";
import { Settings } from "./pages/Settings";
import { HistoryPage } from "./pages/History";
import { KnowledgePage } from "./pages/Knowledge";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<WorkspaceLayout />}>
          <Route index element={<Navigate to="/investigations" replace />} />
          <Route path="investigations" element={<Investigations />} />
          <Route path="investigations/:sessionId" element={<InvestigationDetails />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="knowledge" element={<KnowledgePage />} />
          <Route path="platforms" element={<ConnectedPlatforms />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/investigations" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

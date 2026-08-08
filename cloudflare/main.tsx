import React from "react";
import { createRoot } from "react-dom/client";
import RankingClient from "../app/ranking-client";
import rankingData from "../app/rankings.json";
import "../app/globals.css";

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RankingClient data={rankingData} />
  </React.StrictMode>,
);

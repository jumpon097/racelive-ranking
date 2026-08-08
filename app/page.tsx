import RankingClient from "./ranking-client";
import rankingData from "./rankings.json";

export default function Home() {
  return <RankingClient data={rankingData} />;
}

import MapClientWrapper from "./component/MapClientWrapper";

export default function Home() {
  return (
    // give the main element a viewport height so the MapContainer (height: 100%) is visible
    <main style={{ height: "100vh" }}>
      <MapClientWrapper />
    </main>
  );
}
"use client";

import dynamic from "next/dynamic";


const DynamicMap = dynamic(() => import("./Map"), {
  ssr: false,
  loading: () => <p style={{ padding: 20 }}>Loading map…</p>,
});

export default function MapClientWrapper({ GeoJsonLayerData }) {
  // console.log(GeoJsonLayerData)
  return <DynamicMap GeoJsonLayerData={GeoJsonLayerData}   />;
}
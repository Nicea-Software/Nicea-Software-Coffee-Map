"use client";

import dynamic from "next/dynamic";
import geoJsonFileMetaData from "../types/GeoJsonFileMetaData"

const DynamicMap = dynamic(() => import("./Map"), {
  ssr: false,
  loading: () => <p style={{ padding: 20 }}>Loading map…</p>,
});

export default function MapClientWrapper( GeoJsonLayerData :  geoJsonFileMetaData[] ) {
  return <DynamicMap GeoJsonLayerData={GeoJsonLayerData}   />;
}
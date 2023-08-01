import { useEffect, useMemo, useRef, useState } from "react";
import { LineChart } from "./LineChart.tsx";
import * as d3 from "d3";
const BUTTONS_HEIGHT = 50;

type LineChartDatasetTransitionProps = {
  data: object;
  width: number;
  height: number;
};

const buttonStyle = {
  border: "1px solid #9a6fb0",
  borderRadius: "3px",
  padding: "4px 8px",
  margin: "10px 2px",
  fontSize: 14,
  color: "#9a6fb0",
  opacity: 0.7,
};

export const LineChartTransition = ({
  data,
  width,
  height,
}: LineChartDatasetTransitionProps) => {
  const [selectedGroup, setSelectedGroup] = useState<"temperature" | "pressure" | "humidity" | "illumination" | "dust" | "oxidising" | "reducing" | "nh3">(
    "temperature"
  );
  const handleVariableSwitch = (event) => {
    setSelectedGroup(event.target.value);
  };
  return (
    <div>
      <div style={{ height: BUTTONS_HEIGHT }}>
        <select onChange={handleVariableSwitch}>
            <option value="temperature">Temperature</option>
            <option value="pressure">Pressure</option>
            <option value="humidity">Humidity</option>
            <option value="illumination">Illumination</option>
            <option value="dust">Dust</option>
            <option value="oxidising">Oxidising</option>
            <option value="reducing">Reducing</option>
            <option value="nh3">NH3</option>
        </select>
      </div>
      <LineChart
        width={width}
        height={height - BUTTONS_HEIGHT}
        data={data}
        selectedGroup={selectedGroup}
      />
    </div>
  );
};

import { useRef, useState } from "react";
import { LineChart } from "./LineChart.tsx";
import Select from 'react-select'

const BUTTONS_HEIGHT = 140;

type LineChartDatasetTransitionProps = {
  data: object;
  width: number;
  height: number;
};

export const LineChartTransition = ({
  currentScope,
  currentPointer,
  entries,
  data,
  width,
  height,
}: LineChartDatasetTransitionProps) => {
  const axesRef = useRef(null);
  const selectOptions = [
    { value: 'temperature', label: 'Temperature' },
    { value: 'pressure', label: 'Pressure' },
    { value: 'humidity', label: 'Humidity' },
    { value: 'illumination', label: 'Illumination' },
    { value: 'dust', label: 'Dust' },
    { value: 'oxidising', label: 'Oxidising' },
    { value: 'reducing', label: 'Reducing' },
    { value: 'nh3', label: 'NH3' },
  ];
  const [selectedGroup, setSelectedGroup] = useState<"temperature" | "pressure" | "humidity" | "illumination" | "dust" | "oxidising" | "reducing" | "nh3">(
    "temperature"
  );
  const handleVariableSwitch = (group) => {
    setSelectedGroup(group.value);
  };
  return (
    <div>
      {<LineChart
        currentScope={currentScope}
        currentPointer={currentPointer}
        axesRef={axesRef}
        entries={entries}
        width={width - 50}
        height={height - BUTTONS_HEIGHT}
        data={data}
        selectedGroup={selectedGroup}
      />}
      <div style={{
        marginTop: 25,
        marginLeft: 10,
        marginRight: 10,
      }}>
        <Select style={{
          height: BUTTONS_HEIGHT,
        }} menuPlacement="top" options={selectOptions} onChange={handleVariableSwitch} isSearchable={false}>
            <option value="temperature">Temperature</option>
            <option value="pressure">Pressure</option>
            <option value="humidity">Humidity</option>
            <option value="illumination">Illumination</option>
            <option value="dust">Dust</option>
            <option value="oxidising">Oxidising</option>
            <option value="reducing">Reducing</option>
            <option value="nh3">NH3</option>
        </Select>
      </div>
    </div>
  );
};

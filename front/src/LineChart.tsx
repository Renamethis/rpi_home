import { useEffect, useMemo, useState} from "react";
import { useNavigate } from 'react-router-dom';
//import { useSpring, animated } from "@react-spring/web";
import { motion, useAnimation } from "framer-motion"
import { colours } from "./Colorus.js"
import * as d3 from "d3";

export const MARGIN = { top: 30, right: 30, bottom: 30, left: 20 };

type EnvironmentPoint = { x : number; temperature : number; pressure: number;
                          humidity : number; illumination : number;
                          dust : number; oxidizing: number; reducing : number;
                          nh3 : number, datetime: string};

type LineChartProps = {
  width: number;
  height: number;
  data: EnvironmentPoint[];
  selectedGroup: "temperature" | "pressure" | "humidity" | "illumination" | "dust" | "oxidizing" | "reducing" | "nh3";
};

export const LineChart = ({
  currentPointer,
  currentScope,
  axesRef,
  entries,
  width,
  height,
  data,
  selectedGroup,
}: LineChartProps) => {
    const navigate = useNavigate();
    const boundsWidth = width - MARGIN.right - MARGIN.left;
    const boundsHeight = height - MARGIN.top - MARGIN.bottom;
    const values = Object.entries(data).map(([_, v]) => v[selectedGroup])
    const max = d3.max(values);
    const min = d3.min(values);
    const yScale = useMemo(() => {
        return d3.scaleLinear().domain([Math.round(min * 0.9), Math.round(max * 1.1)]).range([boundsHeight, 0])
    }, [data, max, min]);

    const xScale = useMemo(() => {
        return d3.scaleLinear().domain([entries + currentPointer, currentPointer - 1]).range([0, boundsWidth]);
    }, [data, currentPointer]);
    const [linePath, updateLinePath] = useState([]);

  useEffect(() => {

    const svgElement = d3.select(axesRef.current)
    svgElement.selectAll("g").remove();
    svgElement.selectAll("g").remove();
    const xAxisGenerator = d3.axisBottom(xScale);
    svgElement
      .append("g")
      .attr("class", "x axis")
      .attr("margin", "10px")
      .attr("transform", "translate(0," + boundsHeight + ")")
      .transition()
      .duration(750)
      .call(xAxisGenerator);

    const yAxisGenerator = d3.axisLeft(yScale);
    svgElement.append("g")
              .attr("margin", "10px")
              .attr("class", "y axis")
              .transition()
              .duration(750)
              .call(yAxisGenerator);

    svgElement.selectAll('circle')
              .data(data)
              .join("circle")
              .transition()
              .duration(630)
              .attr("class", "circle")
              .attr("cx", d => xScale(d.x))
              .attr("cy", d => yScale(d[selectedGroup]))
              .attr("r", 5)
              .attr("stroke", "#69b3a2")
              .attr("stroke-width", 3)
              .attr("fill", "white")
      svgElement.selectAll('circle')
                .on("click", function(event, a) {
                  event.preventDefault()
                  const time = event.target.__data__.datetime
                  navigate('weather', {state:{date:time}})
                })
      const lineBuilder = d3
      .line<EnvironmentPoint>()
      .x((d) => xScale(d.x))
      .y((d) => yScale(d[selectedGroup]));
      updateLinePath(lineBuilder(data));
  }, [currentPointer, xScale, yScale, boundsHeight]);

  return (
     <div>
      <svg className="svg_element" width={width} height={height} transform={`translate(${[MARGIN.left, MARGIN.top].join(",")})`}>
        <g width={boundsWidth} height={boundsHeight} transform={`translate(${[MARGIN.left, MARGIN.top].join(",")})`}>
          {/*linePath.map(line => (<LineItem path={line} color={colours[selectedGroup]} length={linePath.getTotalLength}/>))*/
          linePath && <LineItem path={linePath} color={colours[selectedGroup]} length={linePath.getTotalLength}/>}
        </g>
        <g
          width={boundsWidth}
          height={boundsHeight}
          ref={axesRef}
          transform={`translate(${[MARGIN.left, MARGIN.top].join(",")})`}
        />
      </svg>
    </div>
  );
};

type LineItemProps = {
  path: string;
  color: string;
};

const transition = { duration: 4, yoyo: Infinity, ease: "easeInOut",   damping: 10,
stiffness: 100}
function template({ rotate, x }) {
  return `rotate(${rotate}) translateX(${x})`
}
const LineItem = ({ path, color }: LineItemProps) => {
  const anim = useAnimation();
  useEffect(() => {
    anim.start();
  });
  const icon = {
    hidden: {
      pathLength: 0,
      x: 0,
      fill: "rgba(255, 255, 255, 0)",
    },
    visible: {
      pathLength: 1,
      fill: "rgba(255, 255, 255, 1)",
    }
  }
  return (
    <>
    <motion.path
      d={path}
      variants={icon}
      initial="hidden"
      animate="visible"
      fill={"none"}
      stroke={color}
      strokeWidth={2}
      transformTemplate={template}
      transition={transition}
    />
    </>
  );
};


